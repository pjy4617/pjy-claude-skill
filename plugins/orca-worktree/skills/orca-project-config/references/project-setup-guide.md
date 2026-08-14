# Orca 프로젝트 설정 가이드

## CLI 실행 파일 해석 (먼저 할 일)

리눅스에서 bare `orca`는 GNOME Orca **스크린리더**로 잡힐 수 있다. 잘못 실행하면 사용자 머신에서 음성이 시작된다. 순서대로 해석한다:

1. `$ORCA_CLI_COMMAND` 가 있으면 그 값 (Orca가 관리하는 WSL 세션에서 내보낸다)
2. `$ORCA_DEV_REPO_ROOT` 가 있는 개발 체크아웃이면 `orca-dev`
3. Linux에서 Orca 관리 터미널 밖이면 `orca-ide`
4. 그 외 `orca`

선택한 실행 파일이 동작하지 않으면 **다른 것으로 폴백하지 말고** 에러를 그대로 보고한다. 폴백은 다른 Orca 빌드를 조작할 수 있다.

버전에 맞는 정본 가이드는 바이너리가 직접 제공한다:
```bash
<ORCA> skills get orca-cli
```
서브커맨드·플래그는 릴리스마다 바뀌므로 기억이나 캐시된 문서로 추측하지 않는다.

## 신규 프로젝트 설정 체크리스트

| # | 항목 | 명령 / 위치 | 없으면 생기는 일 |
|---|---|---|---|
| 1 | 런타임 기동 | `<ORCA> status --json` / `<ORCA> open --json` | 대부분의 명령이 실패 |
| 2 | 레포 등록 | `<ORCA> repo add --path <abs>` | Orca에서 워크트리를 만들 수 없다 |
| 3 | 기본 base ref | `<ORCA> repo set-base-ref --repo path:<abs> --ref <branch>` | 새 워크트리가 엉뚱한 브랜치에서 갈라진다 |
| 4 | 워크트리 저장 경로 | `<ORCA> project setups --json` → `project setup-update --worktree-base-path <abs>` | 기본 위치에 흩어진다 |
| 5 | **setup 훅** | `orca.yaml` `scripts.setup` → `/orca-setup-build` | 새 워크트리에서 의존성·로컬 설정이 비어 첫 명령이 실패 |
| 6 | archive 훅 | `orca.yaml` `scripts.archive` | setup이 만든 링크가 남는다 |
| 7 | 기본 탭 | `orca.yaml` `defaultTabs` | 매번 손으로 터미널을 연다 |
| 8 | 이슈 연동 | `orca.yaml` `issueCommand` | 이슈 기반 워크트리에서 수동 작업 |
| 9 | 일회용 환경 | `orca.yaml` `environmentRecipes` + `<ORCA> vm recipe doctor <id>` | 클라우드/VM 워크스페이스 미지원 |
| 10 | 커밋 | `git add orca.yaml tools/orca-setup.sh` | 본인 호스트에서만 동작 |
| 11 | 신뢰 승인 | Orca UI의 "Always trust" | 훅이 실행되지 않는다 |

5번이 실제 작업 경험을 좌우한다. 나머지가 다 돼 있어도 5번이 없으면 워크트리를 만들 때마다 손으로 준비해야 한다.

## 셀렉터 문법

| 형태 | 예 |
|---|---|
| `path:` | `--repo path:/home/me/Repos/proj` |
| `name:` | `--repo name:proj` · `--worktree name:feature-x` |
| `branch:` | `--worktree branch:me/feature` |
| `id:` | `--worktree id:<repo-id>::<worktree-path>` (`worktree list --json`이 주는 전체 값) |
| `active` | `--worktree active` (현재 컨텍스트) |

에이전트가 호출할 때는 항상 `--json`을 붙인다.

## 원격 호스트 / 다중 호스트

한 프로젝트를 여러 호스트에 두는 것은 **project host setup**으로 표현된다("프로젝트가 어느 호스트의 어느 경로에 있는가").

```bash
<ORCA> project list --json
<ORCA> project setups --project <project-id> --json
<ORCA> project setup-existing-folder --project <id> --host <host> --path <abs> --json   # 기존 폴더
<ORCA> project setup-clone --project <id> --host <host> --url <git-url> --destination <abs> --json
<ORCA> project setup-update --setup <setup-id> --worktree-base-path <abs> --json
<ORCA> project setup-delete --setup <setup-id> --json
```

원격 런타임에서는 `--path`/`--destination`이 **원격 서버의 절대 경로**여야 한다. SSH 대상은 데스크톱 UI가 연결을 소유하므로 UI에서 설정한다.

## 자주 겪는 증상 → 원인

| 증상 | 원인 | 확인 |
|---|---|---|
| 워크트리를 만들었는데 setup이 안 돈다 | 신뢰 확인 대기 / YAML 파싱 실패 / `--setup skip` | Orca UI 확인 → `check_orca_yaml.py check` |
| 훅이 앞부분만 실행되고 조용히 끝난다 | 주입된 `set -e` 미해제 | 훅 첫머리에 `set +e` |
| 팀원 호스트에서만 실패 | `orca.yaml`/분리 스크립트 미커밋, 호스트 절대경로, PATH 도구 부재 | `git ls-files orca.yaml tools/` |
| 새 워크트리가 엉뚱한 브랜치에서 갈라진다 | 기본 base ref 미설정 | `repo show --json` |
| 설정했는데 아무 효과가 없다 | 미인식 최상위 키(오타) — 조용히 무시된다 | `check_orca_yaml.py check` |
| Windows 팀원만 실패 | 훅이 cmd.exe로 실행됨 | 분기 추가 또는 제약 명시 |
| `orca` 실행 시 음성이 나온다 | GNOME Orca 스크린리더를 실행함 | `orca-ide` 또는 `$ORCA_CLI_COMMAND` 사용 |

## 점검을 정기적으로

레포는 변한다 — 새 하위 패키지가 생기고, 새 로컬 설정 파일이 늘고, 훅은 그대로 남는다. 다음 시점에 `/orca-project-config`를 다시 돌린다:

- 새 패키지/모듈(새 lockfile)이 추가됐을 때
- "새 워크트리에서 X가 안 된다"는 말이 나왔을 때
- 팀에 새 호스트/OS가 합류했을 때
- Orca를 업데이트한 뒤 (키 스키마가 늘어날 수 있다)
