---
name: orca-setup-build
description: "Orca가 새 워크트리를 만들 때 실행할 setup 명령(orca.yaml의 scripts.setup)을 레포에 맞게 자동 작성하고 검증한다. 락파일·빌드시스템·모노레포를 프로파일링하고, git이 따라오지 않는 비추적 자산(.env·.claude/settings.local.json·.serena·대용량 참조 디렉토리)을 스캔해 '새 워크트리에서 바로 작업 가능한' 상태를 만드는 훅을 생성한다. Orca가 러너에 주입하는 set -e·120초 타임아웃·YAML 파싱 실패 시 훅 전체 무시 같은 실측 함정을 기본 회피하고, 임시 git worktree에서 ORCA_* 환경변수를 주입한 실드라이런으로 소요시간·실패 단계·멱등성을 증거로 남긴다. 사용자가 'Orca setup 스크립트 만들어줘', 'Add a setup command to run when Orca creates new worktrees', 'orca.yaml 만들어줘', '워크트리 훅 작성', 'Orca 워크트리 생성 시 실행할 명령 설정', 'setup 스크립트 추가', 'archive 훅 추가', '/orca-setup-build' 등을 요청할 때 자동 적용. 기존 orca.yaml 진단만 필요하면 orca-setup-review, Orca 쪽 레포/프로젝트 등록 설정은 orca-project-config 담당."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# orca-setup-build — Orca 워크트리 setup 훅 작성

Orca는 새 워크트리를 만들 때 레포 루트 `orca.yaml`의 `scripts.setup`을 실행한다. 이 스킬은 그 스크립트를 **레포를 실제로 분석해서** 쓰고, **실제로 돌려보고** 넘긴다.

## 무엇을 해결하는가

git 워크트리에는 **추적되는 파일만** 따라온다. `node_modules`, `.venv`, `.env`, `.claude/settings.local.json`, 빌드 캐시, 대용량 참조 자산은 전부 빠진 채 생성된다. setup 훅이 없으면 새 워크트리에서 첫 명령이 실패한다.

## 사용 시기

- "Add a setup command to run when Orca creates new worktrees" (Orca UI가 띄우는 안내)
- 새 워크트리를 만들 때마다 `pnpm install`·`cmake --preset`·설정 복사를 손으로 반복하고 있음
- 팀원이 워크트리를 만들면 환경이 달라 빌드가 깨짐 (로컬 훅은 공유되지 않는다 — `orca.yaml`은 커밋된다)
- 기존 `orca.yaml`에 단계를 추가/수정해야 함

**쓰지 않는 경우**: 이미 있는 훅의 진단만 필요하면 `/orca-setup-review`, Orca 앱 쪽 레포 등록·base ref·워크트리 경로 설정은 `/orca-project-config`.

## 반드시 지켜야 할 실행 조건 (실측)

| 조건 | 값 | 결과 |
|---|---|---|
| 러너 앞 `set -e` 주입 | Orca가 생성하는 `setup-runner.sh` 첫 줄 | 해제하지 않으면 **첫 실패에서 나머지 단계 전부 누락** |
| 타임아웃 | **120초** | 초과 시 중단 — 빌드·테스트는 넣지 않는다 |
| 실행 셸 | Linux/macOS `/bin/bash`, Windows `%ComSpec%`(cmd.exe) | bash 스크립트는 Windows 호스트에서 동작하지 않는다 |
| cwd | `$ORCA_WORKTREE_PATH` | 그래도 명시적으로 `cd` 해서 고정한다 |
| YAML 파싱 실패 | 훅을 **부분 적용하지 않고 통째로 무시** | 들여쓰기 오류 = 조용한 기능 상실 |
| 인식 키 | `scripts` · `issueCommand` · `defaultTabs` · `environmentRecipes` | 그 외 키는 조용히 무시된다 |

환경변수: `$ORCA_WORKTREE_PATH`(생성 중인 워크트리) · `$ORCA_ROOT_PATH`(메인 체크아웃) · `$ORCA_WORKSPACE_NAME`(보통 브랜치명).

세부는 `references/orca-yaml-schema.md`.

## 서브커맨드

| 호출 | 동작 |
|------|------|
| `/orca-setup-build` | 현재 레포 분석 → `orca.yaml` 생성/갱신 → 드라이런 검증 |
| `/orca-setup-build --repo <경로>` | 대상 레포 지정 |
| `/orca-setup-build --inline` | 별도 스크립트 없이 `orca.yaml` 안에만 작성 (짧은 훅) |
| `/orca-setup-build --script` | `tools/orca-setup.sh` 분리 + `orca.yaml`은 1줄 호출 (긴 훅) |
| `/orca-setup-build --archive` | archive 훅(아카이브 직전 정리)도 함께 작성 |
| `/orca-setup-build --dry-run-only` | 생성하지 않고 기존 훅만 드라이런 |
| `/orca-setup-build --no-dryrun` | 정적 검사까지만 (드라이런 생략 — 기본은 실행한다) |

## 워크플로 (8단계)

스크립트 두 개가 기계적 작업을 맡는다. **레포 특성 판단과 단계 선별은 네가 한다.**

```bash
C="${CLAUDE_SKILL_DIR}/assets/check_orca_yaml.py"   # 정적 검사 / 훅 본문 추출
D="${CLAUDE_SKILL_DIR}/assets/dryrun_setup.sh"      # 임시 워크트리 실드라이런
```

### 1. 사전 점검

```bash
git rev-parse --show-toplevel          # 레포 루트
git rev-parse HEAD                     # 커밋 존재 (드라이런 전제)
ls orca.yaml orca.yml 2>/dev/null      # 기존 설정
uname -s                               # 호스트 OS
```

- git 레포가 아니면 중단한다 (워크트리 훅은 git 워크트리 기능이다)
- `orca.yaml`이 이미 있으면 **덮어쓰지 않고 병합 모드**로 간다: 기존 본문을 읽고, 추가할 단계만 제안한 뒤 사용자 확인을 받는다
- 커밋이 없으면 드라이런이 불가능하다 — 정적 검사까지만 하고 그 사실을 보고한다

### 2. 레포 프로파일링

무엇을 탐지하고 각 생태계에서 어떤 단계가 적절한지는 `references/repo-profiling.md`에 표로 있다. 최소한 다음을 확인한다:

```bash
git ls-files | grep -E '(^|/)(pnpm-lock\.yaml|package-lock\.json|yarn\.lock|bun\.lockb|Cargo\.lock|go\.sum|uv\.lock|poetry\.lock|requirements.*\.txt|CMakePresets\.json|CMakeLists\.txt|.*\.sln|gradlew|Makefile)$'
```

모노레포면 **하위 패키지 경로까지** 잡는다(`wmx37/Frontend/pnpm-lock.yaml`처럼). 루트에만 있다고 가정하지 않는다.

도구가 PATH에 있는지도 확인한다 — 없는 도구를 호출하는 단계는 경고로 처리하도록 써야 한다.

### 3. 비추적 자산 스캔 (가장 중요한 단계)

새 워크트리에 **따라오지 않는데 필요한 것**을 찾는다.

```bash
git status --ignored --short | head -40           # 무시되는 항목
git ls-files --others --exclude-standard | head   # 미추적(무시도 아님)
du -sm .venv old node_modules 2>/dev/null         # 대용량 후보 크기
```

분류 기준:

| 분류 | 처리 | 예 |
|---|---|---|
| 재생성 가능 + 빠름 | setup에서 **재설치** | `node_modules`(lockfile 있음) |
| 재생성 가능 + 느림/무거움 | **링크** 또는 생략 | 빌드 캐시, `_deps` |
| 재생성 불가 + 작음 | 메인에서 **복사** | `.env`, `settings.local.json`, `.serena/` |
| 재생성 불가 + 큼(100MB+) | 메인으로 **심볼릭 링크** | 참조용 레거시 자산, `.venv` |
| 비밀정보 | 복사는 하되 **내용을 orca.yaml에 넣지 않는다** | `.env` |

**링크를 만들면 `info/exclude`에 등록한다.** `.gitignore`의 `dir/` 패턴은 심볼릭 링크에 매칭되지 않아(실측) 워크트리마다 `?? old` 같은 잡음이 `git status`를 가린다. `info/exclude`는 커밋되지 않는 로컬 파일이라 `.gitignore`를 건드리지 않는다.

### 4. 120초 예산 배분

각 후보 단계에 비용을 매기고 예산 안에 들어오는 것만 남긴다.

- **포함**: 의존성 설치(lockfile 기반), configure(`cmake --preset`), 설정 복사/링크, 가벼운 점검
- **제외**: 전체 빌드, 테스트 실행, `docker build`, `git clone`, LFS 대량 수신
- 애매하면 **넣지 말고** 리포트에 "수동 실행 필요"로 남긴다 — 타임아웃은 워크트리 생성 경험 전체를 망친다

메인 체크아웃에서 대표 명령의 실제 소요를 측정해 근거로 삼는다:
```bash
time (cd <pkg> && <install-cmd> --frozen-lockfile) 2>&1 | tail -3
```

### 5. 작성

- 단계가 **3개 이하이고 각 단계가 짧으면** `orca.yaml` 인라인 (`--inline`)
- 그 이상이면 `tools/orca-setup.sh`로 분리하고 `orca.yaml`은 두 줄로 유지 (`--script`) — 셸 로직을 YAML 블록 스칼라 안에서 디버깅하는 것은 고통스럽고, 분리하면 직접 실행해 볼 수 있다

```yaml
scripts:
  setup: |
    set -u
    bash tools/orca-setup.sh
```

템플릿: `assets/templates/orca.yaml`, `assets/templates/orca-setup.sh`. `{{PLACEHOLDER}}`를 채워 쓴다.

**분리 스크립트는 반드시 git에 추가한다** — 추적되지 않으면 새 워크트리에 그 파일이 없어서 훅이 매번 실패한다.

### 6. 필수 관용구 (누락 시 재작성)

`references/script-conventions.md`에 이유와 함께 정리돼 있다. 요약:

1. **`set +e`를 첫머리에** — Orca가 주입한 `set -e` 해제
2. **멱등** — 이미 있는 파일·링크·`info/exclude` 항목은 건드리지 않는다
3. **항상 `exit 0`** — 점검 실패로 워크트리 생성을 막지 않는다 (진짜 치명적일 때만 예외)
4. **경로는 변수로** — `$ORCA_ROOT_PATH`/`$ORCA_WORKTREE_PATH`만 쓰고 `/home/<user>/...`를 쓰지 않는다
5. **링크 해제는 `-L` 확인 후에만** — archive 훅에서 실제 디렉토리를 지우면 메인의 원본이 사라진다
6. **비밀정보를 본문에 쓰지 않는다** — `orca.yaml`은 커밋된다
7. **성공/실패를 사람이 읽을 수 있게 출력** — `✓`/`!` 접두와 마지막 요약

### 7. 검증 (게이트)

```bash
python3 "$C" check orca.yaml                 # 구조 + 안티패턴 + bash -n
bash "$D" --repo "$(git rev-parse --show-toplevel)"   # 실드라이런
```

정적 검사에서 **CRITICAL이 하나라도 남으면 다음 단계로 가지 않는다.**

드라이런은 임시 git 워크트리를 만들어 `set -e`를 주입한 러너로 실제 실행하고, 소요시간·종료코드·생성된 링크·`git status`를 보고한 뒤 **한 번 더 실행해 멱등성까지 확인**하고 워크트리를 지운다. 판정:

| 결과 | 조치 |
|---|---|
| 타임아웃(124) | 무거운 단계 제거 후 재작성 |
| 실패(≠0) | `set +e` 누락 또는 실제 오류 — 로그의 첫 실패 지점부터 고친다 |
| 90초 이상 | 통과해도 느린 호스트에서는 초과한다 — 단계를 줄인다 |
| 2회차 실패 | 멱등하지 않다 — 덮어쓰기/중복 추가 지점을 가드한다 |

### 8. 리포트

- 넣은 단계와 **뺀 단계 + 뺀 이유** (뺀 것을 감추지 않는다)
- 드라이런 실측 소요시간 / 120초
- 커밋해야 할 파일 목록 (`orca.yaml`, `tools/orca-setup.sh`)
- 최초 실행 시 Orca가 **"이 저장소의 orca.yaml 훅을 실행할까요?"** 신뢰 확인을 띄운다는 것 → "Always trust" 선택 시 이후 자동 실행
- 즉시 확인 방법: `orca worktree create --name hook-test --setup run` (CLI 해석은 `references/orca-yaml-schema.md`)

## archive 훅 (`--archive`)

워크트리가 아카이브/삭제되기 **직전**에 실행된다. 넣을 것은 사실상 하나뿐이다 — **setup이 만든 심볼릭 링크 끊기**.

```bash
set +e
for p in old .venv; do
  if [ -L "$p" ]; then rm -f "$p" && echo "  ✓ unlink $p"; fi
done
```

`-L` 검사는 타협 대상이 아니다. 링크가 아니라 실제 디렉토리였다면 메인 체크아웃의 원본이 사라진다. `orca worktree rm`은 `--run-hooks` 없이는 archive 훅을 건너뛴다.

## 실패 대응

| 증상 | 원인 | 조치 |
|---|---|---|
| 훅이 아예 실행되지 않음 | YAML 파싱 실패 → 전체 무시 / 미인식 키 | `python3 "$C" check orca.yaml` |
| 앞 단계만 실행되고 조용히 끝남 | `set -e` 미해제 | 첫머리에 `set +e` |
| 워크트리마다 `?? <name>` 잡음 | 링크가 `.gitignore`에 안 잡힘 | `info/exclude`에 등록 |
| 팀원 호스트에서만 실패 | 호스트 절대경로 / PATH 도구 부재 | 변수화 + `command -v` 가드 |
| 새 워크트리에서 훅이 매번 실패 | 분리 스크립트가 미추적 | `git add tools/orca-setup.sh` |
| Windows 팀원에게서 실패 | cmd.exe로 실행됨 | 분기 추가 또는 제약 명시 |

## 참조

| 파일 | 내용 |
|---|---|
| `references/orca-yaml-schema.md` | 인식 키 4종·훅 2종·환경변수·타임아웃·CLI 플래그·신뢰 프롬프트 |
| `references/repo-profiling.md` | 생태계별 탐지 마커 → 권장 단계 → 비용 등급 |
| `references/script-conventions.md` | 필수 관용구·안티패턴·실측 사례 |
| `assets/check_orca_yaml.py` | `check`(구조+안티패턴+`bash -n`) / `extract`(훅 본문 추출) |
| `assets/dryrun_setup.sh` | 임시 워크트리 실드라이런 + 멱등성 재실행 |
| `assets/templates/` | `orca.yaml` · `orca-setup.sh` 골격 |
