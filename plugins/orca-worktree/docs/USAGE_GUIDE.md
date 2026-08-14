# orca-worktree 사용 가이드

Orca가 새 워크트리를 만들 때 실행할 **setup 명령**을 레포에 맞게 자동 작성·검증하고, 프로젝트가 Orca에 제대로 설정됐는지 점검하는 메타 도구 플러그인이다.

## 왜 필요한가

git 워크트리에는 **추적되는 파일만** 따라온다. `node_modules`, `.venv`, `.env`, `.claude/settings.local.json`, 빌드 캐시, 대용량 참조 자산은 전부 빠진 채 새 워크트리가 만들어진다. Orca UI가 "Add a setup command to run when Orca creates new worktrees"를 권하는 이유이며, 그 명령을 손으로 쓰다 보면 다음 함정을 그대로 밟게 된다:

| 함정 | 증상 |
|---|---|
| Orca가 러너에 `set -e`를 주입한다 | 훅이 앞부분만 실행되고 조용히 끝난다 |
| YAML 파싱 실패 시 훅을 **통째로 무시**한다 | 아무 에러 없이 "훅이 안 돈다" |
| 120초 타임아웃 | 빌드를 넣으면 워크트리 생성이 중단된다 |
| `.gitignore`가 심볼릭 링크에 매칭되지 않는다 | 워크트리마다 `?? old` 잡음이 diff를 가린다 |
| 분리 스크립트를 커밋하지 않음 | 새 워크트리마다 훅이 실패한다 |
| archive에서 `-L` 없이 `rm` | 메인 체크아웃의 원본이 사라진다 |

이 플러그인은 이 함정들을 기본으로 회피하는 훅을 생성하고, **임시 워크트리에서 실제로 돌려본 뒤** 넘긴다.

## 설치

```
/plugin marketplace add pjy4617/pjy-claude-skill
/plugin install orca-worktree@pjy-skills
```

에이전트도 MCP도 필요 없다. `python3`와 `bash`만 있으면 된다. 별도 셋업 스킬이 없어 설치 후 바로 쓸 수 있다.

## 스킬 3개

| 스킬 | 역할 | 쓰기 |
|---|---|---|
| `orca-setup-build` | 레포 분석 → setup/archive 훅 작성 → 드라이런 검증 | O |
| `orca-project-config` | Orca 프로젝트 설정 방법 안내 + 3축 적합성 점검 | 점검은 읽기 전용 |
| `orca-setup-review` | 기존 `orca.yaml` 4등급 진단 | 읽기 전용 |

작성(build)과 검토(review)를 분리한 것은 의도된 설계다 — 같은 컨텍스트에서 자기가 쓴 스크립트를 자기가 승인하면 검토가 형식이 된다.

## 시작하기

### 1. 지금 상태부터 본다

```
/orca-project-config
```

3축(Orca 등록 · 레포 내 설정 · 레포 특성 대비 갭)을 확인해 무엇이 빠졌는지 알려준다. Orca 런타임이 꺼져 있어도 레포 쪽 항목은 점검된다.

```
A. Orca 등록 상태
   등록          : yes
   기본 base ref : <미설정>
   훅 모드       : auto / setupRunPolicy=run-by-default
B. 레포 내 설정
   orca.yaml     : <없음>
C. 레포 특성
   탐지된 생태계 : pnpm (web/pnpm-lock.yaml) cmake (fw/CMakePresets.json)
   비추적 로컬설정: .claude/settings.local.json .serena

[MAJOR] NO_ORCA_YAML: orca.yaml이 없다 — 새 워크트리는 맨 상태로 생성된다
[MAJOR] GAP_pnpm: pnpm 프로젝트인데 setup 훅에 해당 준비 단계가 없다
```

### 2. setup 훅을 만든다

```
/orca-setup-build
```

레포를 프로파일링(락파일·빌드시스템·모노레포 하위 경로)하고, `git status --ignored`로 비추적 자산을 스캔해 **재설치 / 복사 / 링크 / 무시**로 분류한 뒤, 120초 예산 안에 들어오는 단계만 남겨 `orca.yaml`을 작성한다.

단계가 많으면 `tools/orca-setup.sh`로 분리하고 `orca.yaml`은 두 줄로 유지한다:

```yaml
scripts:
  setup: |
    set -u
    bash tools/orca-setup.sh
```

### 3. 검증은 자동으로 따라온다

```bash
python3 assets/check_orca_yaml.py check orca.yaml   # 구조 + 안티패턴 + bash -n
bash assets/dryrun_setup.sh --repo "$(git rev-parse --show-toplevel)"
```

드라이런은 임시 git 워크트리를 만들어 **`set -e`를 주입한 러너로 실제 실행**하고, 소요시간·종료코드·생성된 링크·`git status`를 보고한 뒤 **한 번 더 실행해 멱등성까지 확인**하고 워크트리를 지운다.

```
▶ 결과
  종료코드 : 0
  소요시간 : 6초 / 120초 예산
  판정     : ✓ 통과
▶ 멱등성 재실행
  ✓ 두 번째 실행도 성공 — 멱등
```

### 4. 커밋 + 신뢰 승인

```bash
git add orca.yaml tools/orca-setup.sh
```

`orca.yaml`은 **커밋되어야 팀에 공유된다**(Orca 앱의 로컬 훅은 그 호스트에만 남는다). 최초 실행 시 Orca가 "이 저장소의 orca.yaml 훅을 실행할까요?"를 묻는다 — **Always trust**를 선택하면 이후 자동 실행된다.

## 명령 요약

| 하고 싶은 일 | 명령 |
|---|---|
| 설정 상태 점검 | `/orca-project-config` |
| Orca 등록·base ref 설정 | `/orca-project-config --setup` |
| setup 훅 신규 작성 | `/orca-setup-build` |
| 훅에 단계 추가 (병합) | `/orca-setup-build` (기존 파일이 있으면 병합 모드) |
| archive 훅도 함께 | `/orca-setup-build --archive` |
| 기존 훅만 돌려보기 | `/orca-setup-build --dry-run-only` |
| 기존 훅 진단 | `/orca-setup-review` |

## 트러블슈팅

| 증상 | 원인 | 확인 |
|---|---|---|
| 훅이 아예 안 돈다 | 신뢰 확인 대기 / YAML 파싱 실패 / 미인식 키 | `/orca-setup-review` |
| 앞부분만 실행되고 끝난다 | 주입된 `set -e` 미해제 | 훅 첫머리에 `set +e` |
| 새 워크트리마다 훅 실패 | 분리 스크립트 미커밋 | `git ls-files tools/` |
| 워크트리 생성이 중단된다 | 120초 초과 | 드라이런 소요시간 확인 |
| `git status`에 `??` 잡음 | 링크가 `.gitignore`에 안 잡힘 | `info/exclude` 등록 |
| 팀원 호스트에서만 실패 | 호스트 절대경로 / 도구 부재 | `/orca-setup-review` |
| `orca` 실행 시 음성이 난다 | GNOME Orca 스크린리더 실행 | `orca-ide` 또는 `$ORCA_CLI_COMMAND` |

## 다른 플러그인과의 구분

| | 이 플러그인 | harness |
|---|---|---|
| 대상 | **Orca 워크트리 생성 시 실행되는 셸 훅** | Claude Code 하네스(CLAUDE.md·Permissions·Hooks·MCP) |
| 산출물 | `orca.yaml`, `tools/orca-setup.sh` | `.claude/settings.json` 등 |

둘은 겹치지 않는다 — Orca 워크트리 준비는 이쪽, Claude Code 자체 설정 진단은 `harness`다.
