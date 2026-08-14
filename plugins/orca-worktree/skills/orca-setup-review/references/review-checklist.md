# Orca 워크트리 훅 검토 체크리스트 (6카테고리 30항목)

각 항목은 **근거를 인용할 수 있을 때만** 지적한다. 근거는 `파일:라인` + 해당 코드.

## A. 구조·인식 (5)

| # | 확인 | 위반 시 |
|---|---|---|
| A1 | 최상위 키가 `scripts`·`issueCommand`·`defaultTabs`·`environmentRecipes` 안에 있는가 | CRITICAL — 미인식 키는 조용히 무시된다 |
| A2 | `scripts` 하위가 `setup`·`archive`뿐인가 | CRITICAL |
| A3 | 들여쓰기에 탭이 없는가 | CRITICAL — 파싱 실패 = 훅 전체 무시 |
| A4 | 블록 스칼라(`|`) 본문이 비어 있지 않고 한 단계 더 들여써졌는가 | CRITICAL |
| A5 | 같은 키가 중복 정의되지 않았는가 | CRITICAL |

## B. 실행 안전 (7)

| # | 확인 | 위반 시 |
|---|---|---|
| B1 | 본문 첫머리에 `set +e`가 있는가 (Orca가 주입한 `set -e` 해제) | MAJOR — 첫 실패에서 나머지 전부 누락 |
| B2 | `rm -rf`의 대상이 워크트리 안으로 한정되는가 | CRITICAL |
| B3 | archive의 링크 해제 전에 `[ -L ]` 검사가 있는가 | CRITICAL — 원본 디렉토리 삭제 위험 |
| B4 | `git clean` / `git reset --hard` / `git checkout .`이 없는가 | CRITICAL |
| B5 | `$ORCA_ROOT_PATH`(메인 체크아웃)에 쓰기를 하지 않는가 | CRITICAL |
| B6 | 시크릿(토큰·키·비밀번호)이 하드코딩되지 않았는가 — `orca.yaml`은 커밋된다 | CRITICAL |
| B7 | `sudo` / 패키지 매니저 설치(`apt-get`·`brew`)가 없는가 | MAJOR |

## C. 예산 (4)

| # | 확인 | 위반 시 |
|---|---|---|
| C1 | 전체 빌드(`cmake --build`·`make`·`cargo build`·`npm run build`)가 없는가 | MAJOR — 120초 초과 |
| C2 | 테스트 실행이 없는가 | MAJOR |
| C3 | 네트워크 대량 수신(`git clone`·`git lfs pull`·`docker build`)이 없는가 | MAJOR |
| C4 | 실측 소요가 90초(예산의 75%) 아래인가 — 콜드 캐시 기준 | MAJOR |

측정: `bash ../orca-setup-build/assets/dryrun_setup.sh --repo <repo>`

## D. 이식성 (5)

| # | 확인 | 위반 시 |
|---|---|---|
| D1 | 호스트 절대경로(`/home/<user>/`·`/Users/<user>/`·`C:\Users\`)가 없는가 | MAJOR |
| D2 | 경로를 `$ORCA_WORKTREE_PATH`/`$ORCA_ROOT_PATH`로 다루는가 | MAJOR |
| D3 | 외부 도구를 `command -v`로 가드하는가 | MAJOR |
| D4 | Windows 제약이 명시됐거나 분기가 있는가 | INFO (Windows 팀원이 있으면 MAJOR) |
| D5 | 분리 스크립트가 git에 추적되는가 | CRITICAL — 새 워크트리에 파일이 없다 |

## E. 멱등·복원력 (5)

| # | 확인 | 위반 시 |
|---|---|---|
| E1 | 기존 파일/링크를 덮어쓰지 않는가 (`[ -e ]` 가드) | MINOR |
| E2 | `info/exclude` 등 append 대상에 중복 추가를 막는가 (`grep -qxF`) | MINOR |
| E3 | 두 번 실행해도 종료코드 0인가 | MINOR |
| E4 | 마지막이 `exit 0`인가 — 점검 실패로 워크트리 생성을 막지 않는가 | MAJOR |
| E5 | `cd` 실패 등 전제 붕괴 시 안전하게 빠져나가는가 (`cd "$WT" \|\| exit 0`) | MINOR |

## F. 커버리지 (4)

| # | 확인 | 위반 시 |
|---|---|---|
| F1 | 탐지된 모든 lockfile/빌드시스템에 대응 단계가 있는가 (모노레포 하위 포함) | MAJOR |
| F2 | 비추적 필수 로컬 설정(`.env`·`settings.local.json`·`.serena`)이 승계되는가 | MINOR |
| F3 | 100MB 이상 비추적 디렉토리가 복사가 아닌 링크로 처리되는가 | MINOR |
| F4 | setup이 만든 링크를 archive가 정리하는가 | MINOR |

갭이 **의도된 것인지** 반드시 판단한다. 아무도 쓰지 않는 하위 패키지, 이미 전역 캐시로 해결되는 의존성은 갭이 아니다. 판단 근거를 리포트에 쓴다.

## 리포트 형식

```
## 요약
CRITICAL 1 · MAJOR 3 · MINOR 2 · INFO 1
결론: 커밋 전 CRITICAL·MAJOR 해소 필요

## CRITICAL
### [B3] archive 훅이 -L 검사 없이 디렉토리를 지운다
- 위치: orca.yaml:41
- 근거: `rm -rf "$WT/refdata"`
- 영향: refdata가 링크가 아닌 실제 디렉토리인 워크트리를 아카이브하면 메인 체크아웃의 원본이 사라진다
- 수정안: `if [ -L "$WT/refdata" ]; then rm -f "$WT/refdata"; fi`
...
```

각 항목은 **위치·근거·영향·수정안** 네 줄을 채운다. 영향을 쓸 수 없으면 그 지적은 등급을 낮추거나 뺀다.
