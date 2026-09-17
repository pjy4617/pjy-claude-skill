---
name: graft-serena-doctor
description: "graft(사전 빌드 그래프)와 serena(LSP)를 병행해 쓰기 위한 레포별 배선을 점검하고 고친다. 세 축을 본다 — ① graft(CLI·MCP 등록·그래프 실존 INDEX.md·파일 카드/배선 그래프 신선도·--deep 대기) ② serena(.serena/project.yml 존재·language_servers 비었는지·탐지 언어와 불일치·상위 디렉토리 설정 간섭) ③ rtk(설치·`rtk gain` 이름 충돌·재작성 훅 등록). 두 도구는 배선이 틀어져도 에러 대신 빈 결과를 돌려주므로 고장이 몇 주씩 안 보인다 — 그것을 기계 판정으로 드러낸다. 기본은 읽기 전용이고 --fix 는 파일을 고치면 끝나는 것(serena project.yml)만 고친다. 사용자가 'graft serena 점검', 'graft serena 배선', '코드 검색 도구 점검', 'serena 심볼 도구가 안 된다', 'activate_project 실패', 'No active project', 'language servers 비었다', 'graft 그래프 확인', 'graft 그래프 오래됐나', 'graft 빌드해야 하나', 'rtk 확인', '/graft-serena-doctor', '/graft-serena-doctor --fix' 등을 요청하거나, 심볼 검색·참조 추적이 빈 결과를 돌려줘 원인을 찾을 때 자동 적용. 라우팅 규칙(언제 graft를 쓰고 언제 serena를 쓰는가)은 이 스킬이 아니라 ~/.claude/CLAUDE.md '코드 검색 규칙' 과 setup 레포 문서가 정본이다."
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
---

# graft-serena-doctor — 병행 배선 점검·수리

graft와 serena는 **배선이 틀어져도 에러를 내지 않는다.** 그래프가 없으면 빈
결과, 언어 서버가 안 뜨면 `No active project`, 그래프가 오래됐으면 옛 좌표를
돌려준다. 그래서 고장이 몇 주씩 안 보인다(실측: 심볼 도구 7일간 5회 호출,
성공 0회). 이 스킬은 그 침묵을 **기계 판정**으로 바꾼다.

**라우팅 규칙은 여기 없다.** 언제 graft를 쓰고 언제 serena를 쓰는지는
`~/.claude/CLAUDE.md` "코드 검색 규칙" 과
`~/Repos/setup/docs/code-search-serena-graft-routing.md` 가 정본이다. 규칙을
여기에 다시 적으면 복사본이 세 개가 되어 서로 다른 말을 하게 된다.

## 서브커맨드

| 호출 | 동작 |
|------|------|
| `/graft-serena-doctor` | **점검** — 3축 확인, 읽기 전용 (기본) |
| `/graft-serena-doctor --fix` | 점검 + serena `project.yml` 수리 (백업 후) |
| `/graft-serena-doctor --repo <경로>` | 대상 레포 지정 (기본: 현재 git 루트) |
| `/graft-serena-doctor --json` | 기계 판독용 출력 |
| `/graft-serena-doctor --strict` | CRITICAL/MAJOR 있으면 exit 1 (CI용) |

## 실행

```bash
python3 "${CLAUDE_SKILL_DIR}/assets/check_wiring.py" --repo "$(git rev-parse --show-toplevel)"
```

`--fix` 없이는 아무것도 바꾸지 않는다. 한 화면 표로 끝난다.

## 무엇을 보는가

### A. graft — 그래프가 실제로 있는가, 최신인가

| 판정 | 뜻 |
|---|---|
| `GRAFT_CLI_MISSING` | `graft` 가 PATH 에 없다 |
| `GRAFT_MCP_UNREGISTERED` | MCP 서버 미등록 — `graft_*` 도구 자체를 못 부른다 |
| `GRAFT_CACHE_ONLY` | `graft/` 는 있는데 `INDEX.md` 가 없다 — **디렉토리가 있어 있는 것처럼 보이는 함정** |
| `GRAFT_NO_GRAPH` | 그래프가 없다 (심볼 없는 문서 레포면 INFO — 빌드해도 얻을 것이 없다) |
| `GRAFT_CARDS_MISSING` / `GRAFT_CARDS_STALE` | 파일 카드 층 문제 — `graft_file_api`·`graft_repo_map` 이 빈다 |
| `GRAFT_MANIFEST_ABSENT` | `graft/manifest.json` 이 없어 카드 **내용 드리프트**를 판정 못 한다 (배선 판정은 유효) |
| `GRAFT_WIRING_MISSING` / `GRAFT_WIRING_STALE` | 배선 그래프 문제 — `graft_find_code`·`graft_trace_calls` 가 빈다 |
| `GRAFT_DEEP_PENDING` | 심볼 요약(`--deep`) 미실행 — 고장이 아니라 선택(LLM 키·비용) |

판정 기준은 **디렉토리 존재가 아니라 `graft/INDEX.md` 파일**이다. 신선도는
직접 비교하지 않고 `graft check --json` 에게 묻는다 — 다만 stale 이어도
exit 0 이라 JSON 을 파싱해야 한다.

graft 산출물은 두 층(파일 카드 `context` / 배선 그래프 `graph`)이고,
**한 층만 멀쩡한 경우가 실제로 흔하다.** 그래서 따로 보고한다.

**카드 실존은 `graft check` 가 아니라 파일 개수로 판정한다.** `check` 의
`context.missing` 은 "카드가 없다"가 아니라 **`graft/manifest.json` 이 없다**는
뜻이고(구 버전으로 빌드된 그래프), 카드가 164장 멀쩡한 레포에서도 참으로 나온다.
그것으로 판정하면 **모든 레포에서 MAJOR 가 뜨는 오탐**이 된다(실측으로 확인).

### B. serena — 언어 서버가 뜨는가

| 판정 | 뜻 |
|---|---|
| `SERENA_UNREGISTERED` | 플러그인·MCP 어느 쪽에도 serena 가 없다 |
| `SERENA_NO_PROJECT` | `.serena/project.yml` 없음 — `activate_project` 가 실패한다 |
| `SERENA_NO_LANGSERVER` | `language_servers` 가 비었다 — **CRITICAL.** 언어 서버를 안 띄우므로 심볼 도구가 전부 실패한다 |
| `SERENA_LANG_MISMATCH` | 소스에 있는 언어가 설정에 없다 (예: C++ 만 적혀 있고 Python 이 빠졌다) |
| `SERENA_ANCESTOR_COVER` | 자체 설정이 없어 **상위 디렉토리 설정이 잡힌다** — 상위가 엉뚱한 언어면 통째로 안 된다 |
| `SERENA_LOCAL_OVERRIDE` | `project.local.yml` 이 `language_servers` 를 덮어쓴다 — 유효값과 **수리 대상**이 그쪽이다 |
| `SERENA_LANG_UNUSED` / `SERENA_LANG_UNMAPPED` / `SERENA_LS_NOT_LOCAL` | 참고 항목 |

**활성화가 0.0x초에 끝나면 성공이 아니라 고장이다.** 언어 서버를 아예 안
띄운 것이고, 원인은 `language_servers` 가 빈 것이다. 정상이면 첫
`activate_project` 는 수 초~수십 초 걸린다.

언어는 추적 파일(`git ls-files`)의 확장자를 세어 판정한다. 3개 이상이면 그
언어가 있다고 본다. 코드 파일이 전체의 10% 미만이면 문서 레포로 보고 graft
관련 판정을 INFO 로 낮춘다 — 템플릿 몇 개로 코드 레포가 되지는 않는다.

### C. rtk

| 판정 | 뜻 |
|---|---|
| `RTK_MISSING` | PATH 에 없다 (없어도 graft·serena 는 동작한다) |
| `RTK_NAME_COLLISION` | `rtk` 는 있는데 `rtk gain` 이 실패 — 동명의 다른 rtk(Rust Type Kit)일 수 있다 |
| `RTK_HOOK_MISSING` | 재작성 훅 미등록 — 명령이 rtk 를 거치지 않아 절약이 안 걸린다 |

rtk 는 전역 설치 + 훅이면 끝이라 **레포마다 설정할 것이 없다.** 그래서
점검만 한다.

## --fix 가 고치는 것과 안 고치는 것

| 대상 | --fix | 이유 |
|---|---|---|
| `.serena/project.yml` 생성 | 고친다 | 파일 한 개 쓰면 끝난다 |
| `language_servers` 채우기/보충 | 고친다 (`.bak` 백업) | 같음 |
| `graft build` | **안 한다** — 명령만 출력 | 시간·CPU 를 쓴다. 문서 레포는 빌드가 낭비다 |
| `graft build --deep` | 안 한다 | LLM 키와 **비용**이 든다 |
| graft/rtk 설치·MCP 등록 | 안 한다 | 패키지 매니저·전역 설정 변경이다 |

**serena 수리 후에는 MCP 서버를 재시작해야 반영된다.** `activate_project`
재호출로는 안 고쳐진다. 스크립트가 이 문구를 출력한다.

## 보고 형식

점검 결과를 그대로 옮기지 말고 이렇게 정리한다.

1. **한 줄 결론** — "이 레포에서 graft는 쓸 수 있고 serena 심볼 도구는 못 쓴다" 처럼 사용 가능 여부로.
2. **막는 것부터** — CRITICAL/MAJOR 를 먼저, 각 항목에 "그래서 어떤 도구가 빈 결과를 주는가"를 붙인다.
3. **조치** — `--fix` 로 끝나는 것과 사람이 명령을 걸어야 하는 것을 분리한다.
4. **INFO 는 접어둔다** — `GRAFT_DEEP_PENDING` 처럼 선택인 항목을 고장처럼 보고하지 않는다.

## 함정

- `graft/` 디렉토리가 있어도 `.cache` 만 있으면 그래프가 없다. 존재 판정은 `INDEX.md` 로.
- `graft check` 는 stale 이어도 **exit 0** 이다. 종료 코드로 판정하면 항상 정상으로 보인다.
- 상위 디렉토리(`~/Repos/.serena` 같은)의 `project.yml` 은 자체 설정이 없을 때만 문제가 된다. 자체 설정이 있으면 상위는 무관하므로 보고하지 않는다.
- **`.serena/project.local.yml` 은 `project.yml` 을 덮어쓴다.** 유효값을 그쪽에서 읽어야 하고, 수리도 그쪽에 해야 한다 — `project.yml` 만 고치면 serena 가 무시해 "고친 척"이 된다.
- 옛 설정 파일은 키 이름이 `languages:` 다(serena 가 `language_servers` 로 리네임했다). 이 키를 못 읽으면 "비어 있다"로 오판해 없는 CRITICAL 을 만든다 — 둘 다 읽는다.
- C/C++/C# 은 graft 에서 이름 기반 엣지(broad 등급)라 동명 심볼이 섞인다. 배선이 정상이어도 `graft_trace_calls` 결과는 고치기 전에 `find_referencing_symbols` 로 거른다 — 이 스킬이 판정할 수 있는 항목이 아니라 라우팅 규칙 쪽이다.
- 스크립트 자체 검증: `python3 assets/check_wiring.py --selftest` (YAML 블록 치환 로직 assert).
