---
name: orca-project-config
description: "Orca에서 프로젝트(레포)를 설정하는 방법을 안내하고, 현재 프로젝트가 그 레포 특성에 맞게 설정됐는지 점검한다. 세 축을 다룬다 — ① Orca 등록(repo add·기본 base ref·워크트리 base path·프로젝트 호스트 setup) ② 레포 내 공유 설정(orca.yaml의 scripts·defaultTabs·issueCommand·environmentRecipes) ③ 레포 특성 대비 갭(탐지된 빌드 시스템·비추적 필수 파일이 setup 훅에 반영됐는가). 점검은 읽기 전용이며 Orca 런타임이 꺼져 있어도 레포 쪽 항목은 확인된다. 사용자가 'Orca 프로젝트 설정', 'Orca에 레포 등록', 'orca 설정 확인', '설정이 프로젝트에 맞는지 확인', 'Orca 워크트리 기본 브랜치 설정', 'defaultTabs 설정', 'issueCommand 설정', 'environmentRecipes', '/orca-project-config', 'orca 설정 점검' 등을 요청할 때 자동 적용. setup 훅 본문 작성은 orca-setup-build, 기존 orca.yaml 코드 진단은 orca-setup-review 담당."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# orca-project-config — Orca 프로젝트 설정과 적합성 점검

Orca에서 한 레포를 제대로 쓰려면 **두 곳**을 설정해야 한다. 둘 중 하나만 해두고 나머지를 놓치는 것이 가장 흔한 실패다.

| 설정 위치 | 저장 | 공유 | 내용 |
|---|---|---|---|
| **Orca 쪽** (앱/CLI) | Orca 로컬 상태 | 호스트마다 각자 | 레포 등록, 기본 base ref, 워크트리 base path, 프로젝트 호스트 setup, 로컬 워크트리 훅 |
| **레포 쪽** (`orca.yaml`) | git에 커밋 | 팀 전체 | `scripts`(setup·archive), `defaultTabs`, `issueCommand`, `environmentRecipes` |

## 서브커맨드

| 호출 | 동작 |
|------|------|
| `/orca-project-config` | **점검** — 3축 전체를 확인하고 4등급으로 보고 (기본, 읽기 전용) |
| `/orca-project-config --setup` | 안내 + 누락분 설정 (등록·base ref 등, 각 변경 전 확인) |
| `/orca-project-config --repo <경로>` | 대상 레포 지정 |
| `/orca-project-config --json` | 기계 판독용 출력 |

## 점검 워크플로

```bash
P="${CLAUDE_SKILL_DIR}/assets/check_orca_project.sh"
bash "$P" --repo "$(git rev-parse --show-toplevel)"
```

이 스크립트는 아무것도 바꾸지 않는다. 세 축을 확인한다:

- **A. Orca 등록 상태** — `repo list`에 이 경로가 있는지, 기본 base ref가 설정됐는지, 워크트리 base path는 어디인지
- **B. 레포 내 설정** — `orca.yaml` 존재/키 구성, 훅이 호출하는 분리 스크립트의 존재와 **추적 여부**, `orca.yaml` 자체의 추적 여부
- **C. 레포 특성 대비 갭** — 탐지된 생태계(pnpm·cargo·cmake…)와 비추적 필수 파일이 setup 훅에 반영됐는지

Orca 런타임이 꺼져 있으면 A만 건너뛰고 B·C는 그대로 수행한다.

### 출력 해석

| 코드 | 의미 | 조치 |
|---|---|---|
| `REPO_NOT_REGISTERED` | Orca에 레포가 없다 | `repo add` |
| `NO_BASE_REF` | 기본 base ref 미설정 — 새 워크트리가 엉뚱한 브랜치에서 갈라진다 | `repo set-base-ref` |
| `NO_ORCA_YAML` / `NO_SETUP_HOOK` | 워크트리가 맨 상태로 생성된다 | `/orca-setup-build` |
| `YAML_UNTRACKED` / `YAML_IGNORED` | 본인 호스트에서만 동작 | `git add orca.yaml` |
| `DELEGATE_MISSING` / `DELEGATE_UNTRACKED` | 훅이 호출하는 스크립트가 새 워크트리에 없다 → **매번 실패** | 스크립트를 커밋 |
| `GAP_<생태계>` | 그 생태계 프로젝트인데 준비 단계가 없다 | `/orca-setup-build`로 단계 추가 |
| `GAP_LOCAL_*` | 비추적 로컬 설정이 승계되지 않는다 | setup 훅에 복사 단계 추가 |
| `GAP_BIG_DIR` | 대용량 비추적 디렉토리 미처리 | 링크 여부 판단 |

갭을 발견하면 **자동으로 고치지 말고** 무엇이 왜 필요한지 보고한 뒤 `/orca-setup-build`로 넘긴다. 어떤 갭은 의도된 것이다(예: 그 하위 패키지를 아무도 안 쓴다).

## 설정 방법 (`--setup`)

CLI 실행 파일부터 해석한다 — 리눅스에서 bare `orca`는 GNOME Orca 스크린리더일 수 있다:
`$ORCA_CLI_COMMAND` → (`$ORCA_DEV_REPO_ROOT` 있으면) `orca-dev` → (Linux) `orca-ide` → `orca`

아래에서 `<ORCA>`는 해석한 실행 파일이다. 런타임이 꺼져 있으면 `<ORCA> open` 후 진행한다.

### 1. 레포 등록

```bash
<ORCA> status --json                      # 런타임 확인
<ORCA> repo list --json                   # 이미 등록됐는지
<ORCA> repo add --path /abs/path/to/repo --json
<ORCA> repo show --repo path:/abs/path/to/repo --json
```

셀렉터는 `path:` · `name:` · `id:`를 쓴다.

### 2. 기본 base ref

새 워크트리가 어느 ref에서 갈라질지 정한다. 미설정이면 의도치 않은 브랜치에서 갈라질 수 있다.

```bash
<ORCA> repo search-refs --repo path:<repo> --query main    # 실제 존재하는 ref 확인
<ORCA> repo set-base-ref --repo path:<repo> --ref main --json
```

### 3. 워크트리 저장 위치 / 프로젝트 호스트 setup

Orca에서 "프로젝트가 어느 호스트의 어느 경로에 있는가"는 **project host setup**으로 관리된다.

```bash
<ORCA> project list --json
<ORCA> project setups --json                        # 어떤 호스트에 어떤 경로로 있는지
<ORCA> project setup-update --setup <setup-id> --worktree-base-path <abs> --json
```

원격 런타임에 같은 프로젝트를 두려면 `project setup-existing-folder`(기존 폴더 임포트) 또는 `project setup-clone`(클론)을 쓴다. 원격에서는 절대 경로여야 한다.

### 4. 레포 쪽 공유 설정 (`orca.yaml`)

인식되는 최상위 키는 **넷뿐**이며, 그 밖의 키는 조용히 무시된다. 파싱 에러가 나면 훅이 부분 적용되지 않고 **통째로 무시**된다.

| 키 | 언제 쓰나 |
|---|---|
| `scripts.setup` | 워크트리 생성 직후 준비 — 거의 모든 레포에 필요 → `/orca-setup-build` |
| `scripts.archive` | setup이 만든 심볼릭 링크 정리 등 |
| `defaultTabs` | 새 워크트리에서 기본으로 열 터미널 탭 (dev 서버·로그 등 고정 작업이 있을 때) |
| `issueCommand` | 이슈 연동 워크트리 생성 시 실행할 명령 |
| `environmentRecipes` | 워크스페이스별 일회용 환경(클라우드 샌드박스/VM) — `<ORCA> vm recipe doctor <id>`로 검증 |

`defaultTabs`·`issueCommand`·`environmentRecipes`의 필드 스키마는 Orca 버전에 따라 달라진다. **작성 전에 버전 정본을 읽는다**:

```bash
<ORCA> skills get orca-cli
<ORCA> skills get orca-per-workspace-env     # environmentRecipes 전용
```

버전 정본을 확인할 수 없으면 추측해서 쓰지 않는다 — 미인식 키는 에러 없이 무시되어 "설정했는데 안 되는" 상태가 된다.

### 5. 로컬 훅 vs 커밋되는 훅

Orca 앱의 Settings → General → 레포 → **Worktree hooks**는 그 호스트에만 남는다. 팀에 공유하려면 `orca.yaml`에 넣어야 한다. 개인 실험은 로컬 훅, 팀 표준은 `orca.yaml`로 나누면 된다.

### 6. 신뢰 확인

레포의 `orca.yaml` 훅이 처음 실행될 때 Orca가 "이 저장소의 orca.yaml 훅을 실행할까요?"를 묻는다. **"Always trust"** 이후부터 자동 실행된다. 설정했는데 아무 일도 없으면 이 확인이 대기 중인지 먼저 본다.

## 설정 후 확인

```bash
<ORCA> worktree create --name config-check --setup run --json
<ORCA> worktree list --repo path:<repo> --json
<ORCA> worktree rm --worktree name:config-check --force --json
```

Orca 런타임 없이 훅만 확인하려면 `orca-setup-build`의 `assets/dryrun_setup.sh`를 쓴다.

## 참조

| 파일 | 내용 |
|---|---|
| `references/project-setup-guide.md` | 신규 프로젝트 설정 순서(체크리스트), 셀렉터 문법, 원격 호스트, 자주 겪는 증상 |
| `assets/check_orca_project.sh` | 3축 점검 (읽기 전용, `--json` 지원) |
| `../orca-setup-build/references/orca-yaml-schema.md` | `orca.yaml` 키·훅·환경변수·타임아웃 정본 |
