# orca.yaml 스키마와 실행 규약

레포 루트의 `orca.yaml`은 Orca가 그 레포에서 워크트리를 다룰 때 참조하는 **커밋되는 팀 공유 설정**이다. Orca 앱의 로컬 훅(Settings → General → 레포 → Worktree hooks)과 목적은 같지만, 로컬 훅은 그 호스트에만 남고 `orca.yaml`은 저장소를 통해 전파된다.

## 인식되는 최상위 키 (4개)

| 키 | 용도 |
|---|---|
| `scripts` | 워크트리 생명주기 훅 (`setup` · `archive`) |
| `issueCommand` | 이슈 연동 워크트리를 만들 때 실행할 명령 |
| `defaultTabs` | 새 워크트리에서 기본으로 열 터미널 탭 구성 |
| `environmentRecipes` | 워크스페이스별 일회용 환경(클라우드 샌드박스·VM·로컬) 레시피. `orca vm recipe doctor <id>`가 이 키를 읽어 검증한다 |

**이 넷 밖의 키는 조용히 무시된다.** 오타는 에러가 아니라 기능 상실로 나타난다.

> `defaultTabs`·`issueCommand`·`environmentRecipes`의 세부 필드는 Orca 버전에 따라 달라진다. 작성 전에 반드시 버전에 맞는 정본을 확인한다:
> ```
> <ORCA> skills get orca-cli
> <ORCA> skills get orca-per-workspace-env     # environmentRecipes
> ```
> 이 스킬이 확실하게 다루는 범위는 `scripts`다.

## scripts 훅

```yaml
scripts:
  setup: |
    <워크트리 생성 직후 실행>
  archive: |
    <워크트리 아카이브/삭제 직전 실행>
```

| 항목 | 값 |
|---|---|
| 실행 시점 | `setup` = 새 워크트리 체크아웃 완료 직후 / `archive` = 아카이브·삭제 직전 |
| cwd | 대상 워크트리 루트 |
| 셸 | Linux·macOS `/bin/bash` · Windows `%ComSpec%`(cmd.exe) |
| 실행 형태 | 본문 전체를 하나의 러너 스크립트로 만들어 한 번에 실행 |
| **`set -e` 주입** | Orca가 러너 첫머리에 넣는다 |
| 타임아웃 | **120초** |

### 제공 환경변수

| 변수 | 의미 |
|---|---|
| `ORCA_WORKTREE_PATH` | 지금 생성/정리 중인 워크트리 경로 |
| `ORCA_ROOT_PATH` | 메인 레포 체크아웃 경로 — 비추적 자산의 유일한 출처 |
| `ORCA_WORKSPACE_NAME` | 워크스페이스 이름 (보통 브랜치명) |

`ORCA_ROOT_PATH`가 비어 있는 경우를 대비한 역산:
```bash
ROOT="${ORCA_ROOT_PATH:-}"
if [ -z "$ROOT" ]; then
  _c="$(git rev-parse --git-common-dir 2>/dev/null || true)"   # 링크된 워크트리에서 메인 .git을 가리킨다
  [ -n "$_c" ] && ROOT="$(cd "$(dirname "$_c")" && pwd 2>/dev/null || true)"
fi
```

## 실측된 함정 3가지

### ① `set -e` 주입

Orca가 만드는 `setup-runner.sh`의 첫 줄이 `set -e`다. 훅 본문에서 해제하지 않으면 **어떤 단계든 0이 아닌 종료코드를 내는 순간 나머지가 통째로 누락**된다.

실제 사례: pnpm 10+는 미승인 빌드 스크립트가 있으면 설치가 정상 완료돼도 `ERR_PNPM_IGNORED_BUILDS`로 종료코드 1을 반환한다. `set -e` 아래에서는 그 뒤의 판정 코드에 닿지도 못하고 스크립트가 죽는다.

```bash
set +e   # 본문 첫머리
```

### ② YAML 파싱 실패 = 훅 전체 무시

파싱 에러가 나면 Orca는 유효한 부분만 적용하지 않고 **훅을 통째로 무시**한다. 에러 메시지 없이 "훅이 안 도는" 상태로 보인다. 블록 스칼라 들여쓰기가 가장 흔한 원인이므로 수정 후에는 항상 검사한다:

```bash
python3 assets/check_orca_yaml.py check orca.yaml
```

### ③ `.gitignore`는 심볼릭 링크에 매칭되지 않는다

`.gitignore`의 `dir/` 형태 패턴은 심볼릭 링크에 매칭되지 않는다(실측). setup이 링크를 만들면 워크트리마다 `?? old`, `?? .venv`가 떠서 `git status`와 diff를 가린다. 커밋되지 않는 로컬 파일인 `info/exclude`에 등록해 해결한다:

```bash
excl="$(git rev-parse --git-path info/exclude)"
grep -qxF "/old" "$excl" 2>/dev/null || echo "/old" >> "$excl"
```

## 신뢰 프롬프트

레포의 `orca.yaml` 훅이 처음 실행될 때 Orca가 **"이 저장소의 orca.yaml 훅을 실행할까요?"**를 묻는다. "Always trust"를 선택하면 이후 워크트리부터 자동 실행된다. 훅을 만들었는데 아무 일도 일어나지 않으면 이 확인이 대기 중인지 먼저 본다.

## 관련 CLI

CLI 실행 파일 해석 순서(리눅스에서 bare `orca`는 GNOME Orca 스크린리더일 수 있다):
`$ORCA_CLI_COMMAND` → (`$ORCA_DEV_REPO_ROOT` 있으면) `orca-dev` → (Linux) `orca-ide` → `orca`

| 명령 | 훅 관련 동작 |
|---|---|
| `<ORCA> worktree create --name <n> --setup run` | 레포 setup 훅을 **강제 실행**하며 워크트리 생성 |
| `... --setup skip` | 훅 건너뜀 |
| `... --setup inherit` | 기본값 — 레포 setup 정책을 따름 |
| `... --run-hooks` | `--setup run`의 레거시 별칭 (워크트리를 앱에서 드러냄) |
| `<ORCA> worktree rm --worktree <sel> --run-hooks` | archive 훅 실행. **없으면 건너뛴다** |
| `<ORCA> vm recipe doctor <id> --repo-path <p>` | `environmentRecipes` 검증 (기본은 비파괴) |

훅을 고친 뒤 실제 확인:
```bash
<ORCA> worktree create --name hook-test --setup run --json
# 결과 확인 후
<ORCA> worktree rm --worktree name:hook-test --force --json
```
Orca 런타임 없이 확인하려면 이 스킬의 `assets/dryrun_setup.sh`를 쓴다.
