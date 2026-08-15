---
name: prd-checklist
description: "실행 계획(PLAN)을 실행 체크리스트로 전개하고 이후 진척을 관리하는 워크플로. TASK마다 구현/검증 항목을 CHK-ID로 만들고 실행 주체·수용 기준·완료 근거 칸을 강제해 '했다고 치는' 완료를 차단하며, REQ↔TASK↔CHK 추적성을 check_traceability.py로 기계 검증하며, 검수는 쓰기 권한 없는 체크리스트 전용 검수자 prd-checklist-reviewer가 맡는다. 서브모드로 --status(진척 집계·차단 항목), --sync(PRD/PLAN 변경 시 영향받는 항목 경고 표시)를 제공한다. 사용자가 '체크리스트 만들어줘', '작업 목록 뽑아줘', '실행 항목 정리', '진척 확인해줘', '체크리스트 진행 상황', '계획 바뀌었으니 체크리스트 갱신', '/prd-checklist <PLAN경로>', '--status', '--sync' 등을 요청할 때 자동 적용."
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion
---

# prd-checklist — PLAN → 실행 체크리스트 (+ 진척·동기화)

계획을 **완료를 증명할 수 있는 단위**로 쪼개고, 그 뒤로도 살아 있게 유지하는 스킬.

## 모드

| 모드 | 호출 | 하는 일 |
|------|------|---------|
| 생성 (기본) | `/prd-checklist <PLAN 경로>` | 체크리스트 신규 작성 + 검수 |
| 진척 | `/prd-checklist --status <체크리스트 경로>` | 집계·차단 항목·다음 착수 후보 |
| 동기화 | `/prd-checklist --sync <체크리스트 경로>` | 상위 문서 변경분 반영, 영향 항목에 ⚠️ |

---

## 모드 1: 생성

### 1단계 — 착수 확인 (필수 게이트)

**PLAN이 있다고 해서 곧바로 체크리스트를 만들지 않는다.** 실행에 들어갈 때인지는 사용자가 결정한다.

```bash
head -20 <PLAN 경로>     # source_prd / status / version
grep -cE "^### TASK-" <PLAN 경로>
```

**AskUserQuestion으로 반드시 확인**하며 다음을 함께 제시한다:

- PLAN 상태와 버전, TASK 수·규모 분포
- **미결 이슈에 막힌 TASK 수** — 이것이 실제 착수 가능 여부를 결정한다
- 선택지 예시: `체크리스트 생성` / `PLAN 먼저 확정` / `착수 가능한 마일스톤만` / `지금은 PLAN까지만`

> 계획이 흔들리는 상태에서 체크리스트를 만들면 항목 ID가 재배치되어 **진척 이력이 끊긴다.** CHK-ID는 재사용하지 않는 것이 원칙이므로, 만들기 전에 PLAN이 안정적인지 확인하는 편이 싸다.

**사용자가 진행을 선택하기 전에는 작성 에이전트를 호출하지 않는다.**

### 2단계 — 입력 확인

- 상태 확인은 1단계 게이트에서 끝났다 — **여기서 다시 묻지 않는다**
- PRD 경로를 함께 확보한다 — AC를 항목으로 만들려면 필요하다
- PLAN의 TASK·규모·선행 관계와 미결 의존(6절)을 읽어 둔다

### 3단계 — 작성 위임

`prd-writer`를 Task로 호출한다.

```
작업 종류: 체크리스트 작성
입력 PLAN: <절대 경로>
입력 PRD: <절대 경로>   ← AC를 검증 항목으로 전개하기 위해 필수
출력 경로: <PROJECT>/docs/checklist/CHECKLIST-<slug>.md
references 절대 경로:
  - <plugin>/skills/prd-checklist/references/checklist-format.md
규칙: TASK당 최소 2항목(구현/검증), AC마다 확인 항목, 주체 분리, 근거 칸 공란으로 생성
```

### 4단계 — 기계 검증

```bash
python3 <plugin>/skills/prd-checklist/assets/check_traceability.py \
  --prd <PRD> --plan <PLAN> --checklist <CHECKLIST>
```

ERROR가 있으면 작성 에이전트로 되돌린다. exit code 1이면 진행하지 않는다.

### 5단계 — 검수 위임 (라운드 최대 3)

**`prd-checklist-reviewer`**(체크리스트 전용 검수자) 호출. 상위 문서로 **PLAN과 PRD 둘 다** 전달한다.

5축을 본다: 완결성(형식이 아니라 판정 가능성) · 주체 분리(자기검증 차단의 마지막 방어선) · 완료 근거 칸의 실효성 · 차단 표기의 정확성 · 마일스톤 분리 구조의 무결성.
**마일스톤 단위로 나뉘어 있으면 인덱스와 전 파일 경로를 모두 넘긴다** — 일부만 넘기면 검증에서 오탐이 난다.
위임이 실패하면 1회 재위임하고, 그래도 실패하면 **메인 세션이 대신 검수하지 않고** `검수: 미수행`으로 보고한다 (`quality-rubric.md` → 검수 위임이 실패했을 때).

### 6단계 — 마무리

**체크리스트는 doc-atomize로 분할하지 않는다** — 크기와 무관하다. 항목을 체크할 때마다 재분할이 돌고, 주 조회인 전수 집계(진척률·착수 후보)에서 조각이 이득을 주지 못하기 때문이다 (`prd-write/references/large-doc-handling.md` → 읽히는 문서만 분할한다).

커져서 다루기 힘들면 **마일스톤 단위로 파일을 나눈다.** 손으로 하지 말고 도구를 쓴다 — 프론트매터 승계·차단 표 배분·항목 보존 검증이 자동으로 처리된다.

```bash
python3 <plugin>/skills/prd-checklist/assets/split_checklist.py \
    docs/checklist/CHECKLIST-<slug>.md --dry-run   # 계획 먼저 확인
python3 ... split_checklist.py docs/checklist/CHECKLIST-<slug>.md --force
```

산출 구조 — **인덱스 1개 + 마일스톤 n개**:

```
CHECKLIST-<slug>.md          인덱스 (읽는 방법·선행 관계·파일 목록·진척 요약·검증 명령)
CHECKLIST-<slug>-M1.md       M1 항목 + M1에 걸린 차단 표 행
CHECKLIST-<slug>-M2.md       ...
```

스크립트는 **CHK ID를 건드리지 않는다.** 항목 수가 보존되지 않거나 ID가 중복되면 파일을 쓰지 않고 exit 1로 멈춘다.
`## M1 — 제목` 구획이 없으면 나눌 수 없으므로, 체크리스트는 처음부터 마일스톤으로 구획해 작성한다.

- CHK 연번은 **파일을 넘어 이어서** 부여한다 (M1이 CHK-001~040이면 M2는 CHK-041부터). ID 재사용 금지 원칙은 그대로다
- 검증 스크립트에 **`--checklist`를 여러 번 넘긴다** — 그래야 커버리지와 진척이 전체 기준으로 계산된다
  ```bash
  python3 <...>/check_traceability.py --prd <PRD> --plan <PLAN> \
      --checklist docs/checklist/CHECKLIST-x-M1.md \
      --checklist docs/checklist/CHECKLIST-x-M2.md --status
  ```
  한 파일만 넘기면 다른 파일이 커버하는 TASK가 `TASK_UNCHECKED`로 잘못 잡히고 진척률도 그 파일 기준이 된다.
  연번을 잇지 않고 재사용하면 `DUP_CHK` ERROR로 잡힌다
- 나누는 시점은 **마일스톤이 끝났을 때**가 안전하다 (진행 중 분리는 진척 이력이 흩어진다)

```
체크리스트 생성 완료: docs/checklist/CHECKLIST-<slug>.md
항목: CHK n건 (구현 n / 검증 n / 사용자 결정 n)
커버리지: TASK n/n, AC n/n
차단: n건 (OPEN-### 대기)
검증: ERROR 0 / WARN n
다음: 항목을 TodoWrite로 옮겨 실행하거나 /parallel-delegation 으로 병렬 위임
```

---

## 모드 2: `--status` (진척 집계)

1. 스크립트 실행

```bash
python3 <...>/check_traceability.py --checklist <경로> --status
python3 <...>/check_traceability.py --prd <P> --plan <L> --checklist <C> --status --json
# 마일스톤 단위로 나눴으면 전부 넘긴다 (일부만 넘기면 집계가 그 파일 기준이 된다)
python3 <...>/check_traceability.py --plan <L> --checklist <M1> --checklist <M2> --status
```

2. 결과를 정리해 보고한다:

- 완료 / 진행중 / 차단 / 미착수 건수와 비율
- **TASK 단위 완료**(그 TASK의 모든 CHK가 완료) 수
- 차단 항목과 사유 — 사용자 결정 대기 항목을 맨 위에
- **다음 착수 후보**: 선행 TASK가 모두 완료된 미착수 항목
- ⚠️ **근거 없는 완료 표시**가 있으면 ERROR로 먼저 보고한다 (진척률보다 우선)

3. 체크리스트의 `## 진척 요약` 섹션을 갱신한다 (항목 상태 자체는 임의로 바꾸지 않는다).

> 진척률을 올려 보이려고 항목을 완료 처리하지 않는다. 상태 변경은 실제 근거가 있을 때만 한다.

---

## 모드 3: `--sync` (변경 동기화)

PRD나 PLAN이 바뀐 뒤 체크리스트를 맞춘다.

1. 프론트매터의 `source_plan (v?)` / `source_prd (v?)`와 현재 상위 문서 버전을 비교
2. 변경 지점 확인 — git이 있으면 diff, 없으면 ID 집합 비교

```bash
git diff --stat -- docs/prd docs/plan
```

3. 분류해서 반영:

| 변경 | 반영 |
|------|------|
| REQ/TASK **추가** | 대응 CHK 항목 신규 추가 (미착수) |
| REQ/TASK **삭제** | 해당 CHK를 지우지 말고 `~~취소선~~ (TASK-### 삭제됨)` 표기 |
| AC/요구 **내용 변경** | 영향 CHK 본문 끝에 `⚠️ 상위 변경(v1.2) — 재확인 필요` 추가. **완료 표시는 유지하되 재검증 항목을 새로 추가** |
| 선행 관계 변경 | 착수 후보 재계산 |

4. 프론트매터 `source_*` 버전과 `version`을 올리고, 변경 요약을 보고한다.

> **완료된 항목을 조용히 되돌리지 않는다.** 상위가 바뀌었으면 완료를 지우는 게 아니라 ⚠️를 붙이고 재검증 항목을 추가한다 — 무엇이 이미 검증됐고 무엇이 다시 필요한지 남기기 위해서다.

---

## 하지 않는 것

- 체크리스트 항목을 실제로 **실행**하기 (실행은 TodoWrite / parallel-delegation / 사용자)
- 근거 없이 완료 표시하기
- PLAN에 없는 작업을 체크리스트에서 새로 만들기 (필요하면 PLAN 갱신 권고)
- 진척률을 위해 항목을 합치거나 삭제하기
- **착수 확인 없이 체크리스트 생성 시작** (1단계 게이트 필수)
- 체크리스트를 doc-atomize로 분할하기 (커지면 마일스톤 단위 파일 분리)
