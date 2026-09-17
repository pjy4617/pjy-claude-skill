# graft-serena 사용 가이드

graft와 serena를 병행해 쓰기 위한 **레포별 배선**을 점검하고 고친다.

## 왜 필요한가

두 도구는 **배선이 틀어져도 에러를 내지 않는다.**

| 틀어진 것 | 겉으로 보이는 것 | 실제 |
|---|---|---|
| graft 그래프가 없다 | 빈 결과 | 검색이 안 된 게 아니라 그래프가 없다 |
| `language_servers` 가 비었다 | `No active project` 또는 빈 목록 | 언어 서버를 아예 안 띄웠다 |
| 그래프가 오래됐다 | 결과가 나온다 | 옛 `file:line` 좌표다 |

그래서 고장이 오래 안 보인다. 실측으로 심볼 도구가 7일간 5회 호출되어
성공 0회였고, 그 사실은 아무 에러 메시지로도 드러나지 않았다.

이 플러그인은 그 침묵을 판정 코드로 바꾼다.

## 담지 않는 것

**"언제 graft를 쓰고 언제 serena를 쓰는가"(라우팅 규칙)는 이 플러그인에 없다.**
그 규칙은 `~/.claude/CLAUDE.md` "코드 검색 규칙" 과
`~/Repos/setup/docs/code-search-serena-graft-routing.md` 가 정본이다. 같은
규칙을 플러그인에도 적으면 복사본이 세 개가 되고, 하나만 고치는 순간 서로
다른 말을 하는 문서가 남는다.

이 플러그인이 하는 일은 **"그 규칙을 실행할 수 있는 상태인가"** 하나다.

## 설치

```
/plugin marketplace add pjy-rtx/pjy-claude-skill
/plugin install graft-serena@pjy-skills
```

설치만 하면 끝이다 — 셋업 스킬도, 에이전트도, MCP도 없다.

## 사용

```bash
/graft-serena-doctor              # 점검 (읽기 전용)
/graft-serena-doctor --fix        # serena project.yml 수리
/graft-serena-doctor --repo ../other-repo
/graft-serena-doctor --json       # 기계 판독
/graft-serena-doctor --strict     # CI: CRITICAL/MAJOR 있으면 exit 1
```

### 출력 예

실제 레포(C++/C#/TS/Python 혼합) 출력이다.

```
레포: /home/user/Repos/heller/vision-se
탐지 언어: ['cpp', 'csharp', 'python', 'typescript']

[MAJOR   ] SERENA_LANG_MISMATCH   탐지된 언어 ['csharp', 'python'] 가 설정에 없다 (현재: ['cpp', 'typescript'])
                                  → --fix 로 추가한 뒤 serena MCP 재시작
[INFO    ] GRAFT_MANIFEST_ABSENT  graft/manifest.json 이 없어 카드 164장의 내용 드리프트를 판정할 수 없다 (배선 그래프 판정은 그대로 유효하다)
[INFO    ] GRAFT_DEEP_PENDING     심볼 1438개가 LLM 요약(--deep) 대기 — 요약·crux 없이 배선만 쓰는 상태다
[INFO    ] SERENA_LOCAL_OVERRIDE  project.local.yml 이 language_servers 를 덮어쓴다 (유효값: ['cpp', 'typescript'])
[INFO    ] SERENA_LS_NOT_LOCAL    로컬에 언어 서버가 안 보이는 언어: ['csharp']
```

읽는 법: MAJOR 한 줄은 "이 레포에서 C#(31파일)과 Python(29파일) 심볼 검색이
지금 빈 결과를 준다"는 뜻이다. C++ 과 TypeScript 만 언어 서버가 뜬다.
INFO 넷은 고장이 아니라 상태 설명이다 — `--deep` 은 비용 선택이고,
`SERENA_LOCAL_OVERRIDE` 는 수리해야 할 파일이 `project.yml` 이 아니라
`project.local.yml` 이라는 뜻이다.

## 점검 항목

### A. graft

`graft/INDEX.md` 파일로 그래프 실존을 판정한다. **디렉토리 존재로 판정하지
않는다** — `graft/` 에 `.cache` 만 남은 상태가 실제로 흔하고, 그때
디렉토리는 멀쩡해 보인다.

신선도는 `graft check --json` 에게 묻는다. 주의: stale 이어도 **exit 0** 이라
종료 코드로 판정하면 항상 정상으로 보인다.

graft 산출물은 두 층이고 따로 본다.

| 층 | JSON 키 | 이 층이 없으면 비는 도구 |
|---|---|---|
| 파일 카드 | `context` | `graft_file_api`, `graft_repo_map` |
| 배선 그래프 | `graph` | `graft_find_code`, `graft_find_all`, `graft_trace_calls` |

`graph.pending` 은 LLM 요약(`--deep`) 대기 수다. 배선 자체는 쓸 수 있으므로
고장이 아니라 선택으로 INFO 처리한다(키와 비용이 든다).

**카드 실존은 파일 개수로 판정한다.** `graft check` 의 `context.missing` 은
"카드가 없다"가 아니라 **`graft/manifest.json` 이 없다**는 뜻이고(구 버전으로
빌드된 그래프), 카드가 멀쩡한 레포에서도 참으로 나온다. 그것으로 판정하면 모든
레포에서 MAJOR 가 뜨는 오탐이 된다 — 실제 레포 3곳에서 확인했다. 그래서 이
경우는 `GRAFT_MANIFEST_ABSENT`(INFO, "내용 드리프트 판정 불가")로 따로 보고하고,
배선 그래프 판정은 그대로 유효하게 둔다.

### B. serena

`.serena/project.yml` 의 `language_servers` 가 핵심이다. 비어 있으면
언어 서버를 안 띄우므로 심볼 도구가 **전부** 실패한다 — 유일한 CRITICAL 항목이다.

**활성화가 0.0x초에 끝나면 성공이 아니라 고장 신호다.** 정상이면 첫
`activate_project` 가 수 초~수십 초 걸린다(언어 서버를 띄우는 시간).

언어는 `git ls-files` 확장자를 세어 판정하고, 3개 이상이면 그 언어가 있다고
본다. 코드 파일이 전체의 10% 미만이면 문서 레포로 보고 graft 판정을 INFO 로
낮춘다.

**`.serena/project.local.yml` 이 있으면 그쪽이 `project.yml` 을 덮어쓴다.**
serena 가 그렇게 로드하므로 유효값도, 수리 대상도 local 파일이다 —
`project.yml` 만 고치면 serena 가 무시해 "고친 척"이 된다(`SERENA_LOCAL_OVERRIDE`).
옛 설정의 `languages:` 키도 함께 읽는다(serena 가 `language_servers` 로 리네임한
필드라, 못 읽으면 "비어 있다"로 오판한다).

자체 `project.yml` 이 없으면 상위 디렉토리 설정이 잡힌다. 상위가 엉뚱한
언어 하나만 갖고 있으면 그 아래 레포 전부가 조용히 안 된다 —
`SERENA_ANCESTOR_COVER` 가 그 경우다. 자체 설정이 있으면 상위는 무관하므로
보고하지 않는다.

### C. rtk

전역 설치 + 훅이면 끝이라 레포마다 설정할 것이 없다. 점검만 한다.
`rtk` 는 있는데 `rtk gain` 이 실패하면 동명의 다른 패키지(Rust Type Kit)다.

## --fix 의 경계

| 대상 | --fix | 이유 |
|---|---|---|
| `.serena/project.yml` 생성 | 고친다 | 파일 한 개 쓰면 끝난다 |
| `language_servers` 채우기 | 고친다 (`.bak` 백업) | 같음 |
| `graft build` | 명령만 출력 | 시간·CPU. 문서 레포는 빌드가 낭비다 |
| `graft build --deep` | 명령만 출력 | LLM 키와 비용 |
| graft·rtk 설치, MCP 등록 | 명령만 출력 | 패키지 매니저·전역 설정 변경 |

**serena 수리 후 MCP 서버 재시작이 필요하다.** `activate_project` 재호출로는
반영되지 않는다.

## CI 에서

```bash
python3 skills/graft-serena-doctor/assets/check_wiring.py --strict
```

CRITICAL/MAJOR 가 있으면 exit 1. 문서 레포에서 graft 항목이 INFO 로 내려가므로
"그래프 없음"만으로 CI 가 깨지지는 않는다.

## 자체 검증

```bash
python3 skills/graft-serena-doctor/assets/check_wiring.py --selftest
```

YAML `language_servers` 블록 치환(블록·인라인·키 부재 세 경우)을 assert 로
확인한다. Python 표준 라이브러리만 쓴다 — PyYAML 불필요.
