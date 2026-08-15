# prd-plan 사용 가이드

PRD → 실행 계획(PLAN) → 체크리스트를 **작성자와 검수자를 분리해** 만드는 플러그인.

## 왜 이 플러그인인가

문서를 만들어 주는 도구는 많다. 이 플러그인이 다른 점은 세 가지다.

1. **자기검증을 구조적으로 차단한다** — 작성 에이전트(`prd-writer`)와 검수 에이전트(`prd-reviewer`)가 분리되고, 검수자는 **쓰기 권한이 없으며 대화가 아니라 파일을 읽고** 판정한다.
2. **추적성이 기계 검증된다** — `REQ → TASK → CHK` 연결이 끊기면 `check_traceability.py`가 exit 1로 잡는다.
3. **지어낸 값을 만들지 않는다** — 절대 날짜·시간 공수 금지, 모르는 값은 미결 이슈(`OPEN-###`), 완료 표시에는 근거 필수.
4. **단계가 자동으로 흘러가지 않는다** — PRD가 끝났다고 PLAN이, PLAN이 끝났다고 체크리스트가 이어서 만들어지지 않는다. 각 단계는 **착수 확인 게이트**로 시작하며 사용자가 진행을 선택해야 움직인다.

## OMC의 plan / planner와 무엇이 다른가

| | OMC `plan`·`planner`·`ralplan` | **prd-plan** |
|---|---|---|
| 산출물 | 세션 내 작업 계획(휘발성) | **저장되는 문서**(PRD/PLAN/체크리스트) |
| 관점 | 코드 작업 순서 | **PM 관점** — 범위·이해관계자·성공지표·리스크 |
| 품질 게이트 | 없음(또는 자율) | **분리된 검수 라운드 + 승인 전이** |
| 추적성 | 없음 | REQ↔TASK↔CHK 기계 검증 |
| 수명 | 세션 | 프로젝트 전체 |

"지금 뭘 어떤 순서로 짤까"는 OMC, "이 프로젝트가 무엇이고 무엇이 완료인가"는 prd-plan이다. 둘은 이어서 쓸 수 있다 — 체크리스트를 만든 뒤 항목 실행은 OMC/`parallel-delegation`에 넘긴다.

## 설치

```
/plugin install prd-plan@pjy-skills
/prd-setup
```

`/prd-setup`이 하는 일: 에이전트 2종 → `.claude/agents/`, CLAUDE.md 규약 주입, `docs/{prd,plan,checklist,reviews}` 생성, 선택 의존성(python3 / doc-atomize) 확인. **에이전트는 새 세션부터 인식**된다.

## 기본 흐름

```
/prd-write 서보 드라이버 모니터링 툴
   ↓ 인터뷰(메인 세션) → 작성 위임 → 검수 위임 → 반영 루프 → 사용자 승인
docs/prd/PRD-servo-monitor.md (approved)

/prd-plan docs/prd/PRD-servo-monitor.md
   ↓ ⛔ 착수 확인 게이트 — 지금 계획을 세울 때인지 먼저 묻는다
   ↓ WBS·의존그래프·마일스톤·리스크 → 검수 루프
docs/plan/PLAN-servo-monitor.md

/prd-checklist docs/plan/PLAN-servo-monitor.md
   ↓ ⛔ 착수 확인 게이트 — 실행에 들어갈 때인지 먼저 묻는다
   ↓ TASK당 구현/검증 항목 + AC 확인 항목 → 추적성 검증
docs/checklist/CHECKLIST-servo-monitor.md

/prd-checklist --status docs/checklist/CHECKLIST-servo-monitor.md
```

## 스킬 5종

| 스킬 | 하는 일 |
|------|---------|
| `/prd-write <주제>` | 인터뷰 → PRD 작성 → 검수 루프 → 승인 |
| `/prd-plan <PRD>` | PRD → WBS·의존·마일스톤·리스크 |
| `/prd-checklist <PLAN>` | 체크리스트 생성 / `--status` 진척 / `--sync` 변경 동기화 |
| `/prd-review <문서>` | 외부·기존 문서 검수만 (읽기 전용 리포트) |
| `/prd-setup` | 에이전트·디렉토리·CLAUDE.md 설치 (1회) |

## 에이전트 2종

| 에이전트 | 페르소나 | 권한 |
|----------|----------|------|
| `prd-writer` | 30년 경력 PM — 모호한 범위와 측정 불가 기준이 프로젝트를 죽인다는 것을 아는 사람 | Read/Write/Edit/Glob/Grep/Bash |
| `prd-reviewer` | 30년 경력 PMO 게이트 심사관 — 통과시킨 계획의 실패에 책임지는 사람 | Read/Glob/Grep/Bash (**Write 없음**) |

## PRD 프로파일

| profile | stack | 필수 추가 항목 |
|---------|-------|----------------|
| `software` | `frontend` | 화면 목록 / UI 라이브러리(Fluent vs shadcn 택1) / 실시간 갱신 방식 / 브라우저·해상도 / 접근성 |
| `software` | `backend` | 언어·런타임(C++·C#·Python) / 실행 형태 / 인터페이스 계약 / 동시성·지연 / 자원·실시간성 / 오류·복구 |
| `software` | `full-stack` | 위 둘 + **API 인터페이스 계약 섹션** |
| `hardware-firmware` | — | 기능 요구 / 인터페이스 목록 / 성능 사양 / 전원 요구 (+ 폼팩터·환경·펌웨어) |
| `research-PoC` | — | 가설 / 판정 기준 / 실험 요구 / **중단 기준** |

hardware 프로파일 PRD는 `kicad-design`이 요구하는 4항목을 그대로 만족하므로 **회로도 생성 스킬에 바로 넘길 수 있다**.

## 추적성 검증

```bash
python3 <plugin>/skills/prd-checklist/assets/check_traceability.py \
  --prd docs/prd/PRD-x.md --plan docs/plan/PLAN-x.md --checklist docs/checklist/CHECKLIST-x.md
python3 ... --checklist docs/checklist/CHECKLIST-x.md --status     # 진척
python3 ... --checklist CHECKLIST-x-M1.md --checklist CHECKLIST-x-M2.md --status   # 마일스톤 분리 시 전부 넘긴다
python3 ... --json --strict                                        # CI/훅 게이트
```

주요 ERROR: `MUST_UNCOVERED`(MUST 요구를 아무 작업도 커버 안 함) · `REQ_NO_AC`(수용 기준 없음) · `TASK_NO_BASIS`(근거 없는 작업) · `CYCLE`(선행 순환) · `CHK_NO_EVIDENCE`(**근거 없는 완료 표시**) · `TASK_BAD_REF`/`CHK_BAD_REF`/`AC_BAD_REF`/`OPEN_BAD_REF`(존재하지 않는 ID 참조) · `AC_PREFIX`(소속이 다른 번호의 AC 정의)

주요 WARN: `TASK_XL`(분해 필요) · `ABS_DATE`/`EFFORT`(산정 정책 위반 — 코드블록·문서 메타데이터 줄은 제외) · `TASK_UNCHECKED` · `CHK_NO_OWNER` · `OPEN_ORPHAN`(미결 표에만 있고 본문에 `(미정 — OPEN-###)` 표기 없음)

> Windows에서 `python3`가 MS Store alias로 exit 49면 `py -3` 또는 `python`을 쓴다.

## 대용량 문서 (doc-atomize 연동)

| 시점 | 처리 |
|------|------|
| 입력 자료가 큼 | **읽기 전에** 분할 → 에이전트에 인덱스 경로 전달 |
| 검수 루프 중 | **분할 금지** (라운드마다 재분할 + 라인 근거 어긋남) |
| 승인 후 | 분할 → 다운스트림은 `<doc-id>.index.md`로 조회 |
| 원본 수정 | doc-atomize 훅이 변경 조각만 **자동 재생성** (요약 재작성은 사람 몫) |
| **체크리스트** | **분할하지 않는다** — 자주 바뀌고 전수 집계로 읽히는 문서라 이득이 없다. 커지면 `split_checklist.py`로 **마일스톤 단위 파일 분리**(인덱스 1 + 마일스톤 n, CHK 연번은 파일을 넘어 연속) |

미설치여도 동작한다(통독 폴백 + 1회 안내). PDF·CHM 등 비마크다운 원본은 `manual-digest` 담당.

## 자주 겪는 상황

**"PRD 만들었는데 왜 PLAN을 안 만드나"** → 의도된 동작입니다. `/prd-plan`을 호출하면 **착수 확인 게이트**가 먼저 뜨고, PRD 상태와 미결 이슈를 보여준 뒤 `PLAN 작성 시작` / `미결 먼저 해소` / `일부 범위만 계획` / `지금은 PRD까지만` 중에서 고르게 합니다. 범위·안전에 걸린 미결이 남은 채로 계획을 세우면 그 계획을 다시 만들게 되기 때문입니다. 체크리스트도 같습니다.

**"인터뷰가 귀찮다"** → 생략 가능. 단 미확정 항목이 전부 `OPEN-###`로 남고, 그 상태가 최종 보고에 표시된다.

**"검수에서 계속 지적이 나온다"** → 3라운드에서 멈추고 잔여를 `문서로 해소 가능 / 사용자 결정 필요`로 분류해 올린다. 임의 통과는 하지 않는다. 지적이 라운드마다 **늘어나면** 리뷰어가 `⚠️ 범위 확대 감지`를 붙인다.

**"요구가 바뀌었다"** → `/prd-write`로 PRD 갱신(version↑) → `/prd-checklist --sync`. 완료된 항목은 지우지 않고 ⚠️ 표시 + 재검증 항목을 추가한다.

**"일정표를 달라"** → 착수일·가용 인원·외부 납기를 주면 상대 순번을 캘린더에 매핑한다. 주지 않으면 의존 사슬 기반 상대 일정까지만 낸다. 날짜를 지어내지 않는다.

## 이 플러그인이 하지 않는 것

- 실제 구현 (체크리스트 이후는 `parallel-delegation` / OMC / 사용자)
- Jira·Notion 등 외부 이슈 트래커 연동
- 인력 배정·원가 산정
- 사용자 승인 없는 문서 확정
