---
name: prd-plan
description: "승인된 PRD를 실행 계획(PLAN)으로 전개하는 워크플로. 요구사항(REQ)을 작업(TASK)으로 분해해 WBS·선행 의존 그래프·마일스톤·리스크 등록부를 만들고, 모든 TASK에 근거 REQ를 붙여 추적성을 보장한다. 절대 날짜와 임의 공수를 만들지 않고 상대 규모(S/M/L/XL)와 상대 순번만 쓴다. 작성은 prd-writer, 검수는 쓰기 권한 없는 prd-reviewer가 맡고 최대 3라운드 반영 루프를 돈다. 사용자가 '실행 계획 세워줘', 'PLAN 문서 만들어줘', 'WBS 작성', '작업 분해', '개발 계획 수립', '프로젝트 계획서', '/prd-plan <PRD경로>' 등을 요청할 때 적용. 착수 확인 게이트로 시작하므로 PRD 승인 직후 자동으로 이어지지 않는다 — 사용자가 계획 수립을 명시적으로 요청해야 한다."
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion
---

# prd-plan — PRD → 실행 계획(PLAN)

요구사항을 **작업으로 번역**하는 단계. 여기서 만들어지는 것은 일정표가 아니라 **의존 관계가 성립하는 작업 목록**이다.

## 전제

1. **착수 여부를 먼저 묻는다.** PRD가 존재한다는 사실이 계획을 세울 때가 되었다는 뜻은 아니다. 1단계 게이트에서 사용자 확인을 받기 전에는 아무것도 작성하지 않는다. 특히 `status`가 `approved`가 아니거나 미결 이슈가 범위·안전에 걸려 있으면 **계획을 두 번 만들게 된다**.
2. **날짜를 만들지 않는다.** LLM이 지어낸 "3월 2주차"는 근거가 없다. `references/estimation-policy.md` 규칙을 강제한다.
3. **모든 TASK는 근거 REQ를 갖는다.** 근거 없는 작업은 범위 밖이거나, PRD에 빠진 요구다 — 둘 다 문제다.

## 사전 조건

- 입력 PRD 경로 (또는 `*.index.md`)
- 에이전트 2종 (미설치면 `/prd-setup`)
- `python3` (추적성 검증, 선택)

---

## 실행 절차 (8단계)

### 1단계 — 착수 확인 (필수 게이트)

**PRD가 있다고 해서 곧바로 PLAN을 만들지 않는다.** 계획을 세울 때인지는 사용자가 결정한다.

먼저 PRD 상태를 읽어 판단 재료를 만든다.

```bash
head -20 <PRD 경로>                       # status / version / profile / stack
grep -cE "^\| OPEN-[0-9]{3}" <PRD 경로>    # 미결 이슈 수
```

그 다음 **AskUserQuestion으로 반드시 확인**한다. 다음을 함께 제시한다:

- PRD 상태(`draft`/`in-review`/`approved`)와 버전, 요구사항 규모(MUST 몇 건)
- **미결 이슈 수와, 그중 계획을 흔들 수 있는 것** — 특히 범위·안전·외부 의존에 걸린 항목
- 선택지 예시:

| 선택지 | 의미 |
|--------|------|
| **PLAN 작성 시작** | 현 PRD 기준으로 계획 수립 |
| **미결 먼저 해소** | `/prd-write`로 돌아가 OPEN 항목을 채운 뒤 재개 |
| **일부 범위만 계획** | 확정된 요구만 대상으로 부분 PLAN |
| **지금은 PRD까지만** | 종료 |

판단 기준을 그대로 제시한다 — 계획을 지금 세우면 좋은 경우와 아닌 경우가 다르다.

> - `status: approved` + 미결이 실행을 막지 않음 → **지금 세우는 것이 낫다**
> - `draft`이거나 범위·안전에 걸린 미결이 남음 → **계획을 두 번 만들게 된다.** 미결 해소를 먼저 권한다
> - 미결이 많아도 **착수 가능한 구간이 명확**하면 부분 PLAN이 유효하다

`status`가 `approved`가 아니면 그 사실을 선택지 설명에 명시한다. **사용자가 진행을 선택하기 전에는 작성 에이전트를 호출하지 않는다.**

### 2단계 — 입력 확인

```bash
head -20 <PRD 경로>          # 프론트매터에서 profile / stack / status / version 확인
```

- `status` 관련 확인은 1단계 게이트에서 이미 끝났다 — **여기서 다시 묻지 않는다**
- 인덱스 파일이면 인덱스를 읽고 **요구사항 조각 전체**를 확보한다 (계획 수립은 전 요구를 봐야 한다)
- 미결 이슈(OPEN-###) 목록을 뽑아 둔다 — 이것이 계획의 최대 리스크다

### 3단계 — 분해 방침 확정

`references/wbs-guide.md`를 읽고 분해 축을 정한다. 프로파일별 기본값:

| 프로파일/스택 | 기본 분해 축 |
|---------------|--------------|
| software / frontend | 화면·컴포넌트 단위 → 상태/데이터 연동 → 검증 |
| software / backend | 인터페이스(계약) 단위 → 도메인 로직 → 영속/배포 |
| software / full-stack | **계약 먼저**(API 확정) → 백엔드/프론트 병행 → 통합 |
| hardware-firmware | 회로 블록 → 아트웍/제조 → 펌웨어 브링업 → 검증 |
| research-PoC | 환경 구축 → 베이스라인 → 실험 → 판정 |

사용자가 특정 순서를 원하면 그것을 우선한다. 애매하면 AskUserQuestion으로 확인하되 기본값을 추천으로 제시한다.

### 4단계 — 작성 위임

`prd-writer`를 Task로 호출한다.

```
작업 종류: PLAN 작성
프로파일: <profile> / stack: <stack>
입력 PRD: <절대 경로 또는 index 경로>
출력 경로: <PROJECT>/docs/plan/PLAN-<slug>.md
분해 축: <3단계 결정>
references 절대 경로:
  - <plugin>/skills/prd-plan/references/wbs-guide.md
  - <plugin>/skills/prd-plan/references/estimation-policy.md
미결 이슈: <OPEN 목록 — 의존 작업으로 반영할 것>
```

### 5단계 — 기계 검증

```bash
python3 <plugin>/skills/prd-checklist/assets/check_traceability.py \
  --prd docs/prd/PRD-<slug>.md --plan docs/plan/PLAN-<slug>.md
```

ERROR가 있으면 검수 위임 전에 작성 에이전트로 되돌린다 (사람 검수에 기계가 잡을 것을 올리지 않는다).

### 6단계 — 검수 위임 + 반영 루프 (최대 3라운드)

`prd-reviewer`를 별도 Task로 호출한다. 상위 문서로 **PRD 경로를 반드시 함께** 준다 (추적성 판정에 필요).

```
검수 대상: <PLAN 경로>
상위 문서: <PRD 경로>
프로파일: <profile>/<stack> / 라운드: N
references: quality-rubric.md, estimation-policy.md, wbs-guide.md
검증 스크립트: check_traceability.py
```

리포트는 메인 세션이 `docs/reviews/REVIEW-plan-<slug>-r<N>.md`로 저장한다.
위임이 실패하면 1회 재위임하고, 그래도 실패하면 **메인 세션이 대신 검수하지 않고** `검수: 미수행`으로 보고한다 (`quality-rubric.md` → 검수 위임이 실패했을 때).
`CRITICAL 0 && MAJOR 0`이 될 때까지 작성↔검수를 반복하되 3라운드를 넘기지 않는다.

### 7단계 — 사용자 확인

AskUserQuestion으로 제시한다:
- 총 TASK 수, 규모 분포(S/M/L/XL), 최장 의존 사슬 길이
- 미결 이슈에 막힌 TASK 목록 — **이것이 실제 착수 가능 여부를 결정한다**
- 선택지: `승인` / `분해 조정(더 잘게/크게)` / `보류`

### 8단계 — 마무리

1. **40KB 초과** 시 `/doc-atomize` (승인 후에만 — `large-doc-handling.md`)
2. 보고:

```
PLAN 작성 완료: docs/plan/PLAN-<slug>.md (v1.0, PRD v<n> 기준)
작업: TASK n건 (S n / M n / L n / XL n)
커버리지: MUST REQ n/n 커버, 근거 없는 TASK 0건
의존: 최장 사슬 n단계, 순환 0건
차단: 미결 이슈로 막힌 TASK n건 (OPEN-###)
검수: R1 C n/M n → 최종 C 0/M 0
다음 단계 제안: /prd-checklist docs/plan/PLAN-<slug>.md  ← 제안일 뿐, 자동 실행하지 않는다
```

---

## PLAN 문서 규격 (요약 — 상세는 wbs-guide.md)

```markdown
---
id: PLAN-<slug>
source_prd: PRD-<slug> (v1.2)
status: draft | in-review | approved
version: 1.0
---

## 1. 계획 개요        # 무엇을 어떤 순서로, 왜 그 순서인가
## 2. 작업 분해 (WBS)  # TASK 블록들
## 3. 의존 그래프      # 표 + mermaid(선택)
## 4. 마일스톤         # M1/M2... 라벨 + 완료 조건(TASK 집합)
## 5. 리스크 등록부    # PRD 리스크 승계 + 실행 리스크 추가
## 6. 가정 · 미결 의존 # OPEN-### 에 막힌 작업
## 7. 요구사항 커버리지 매트릭스   # REQ ↔ TASK 표
```

## 하지 않는 것

- 절대 날짜·캘린더 일정 생성 (사용자가 제공한 경우만 기재)
- 인원 배정·공수 시간 추정 (상대 규모만)
- 구현 방식 확정 (설계는 다음 단계 — 단, 선택지가 계획을 바꾸면 미결 이슈로)
- PRD에 없는 요구를 계획에 슬쩍 추가 (발견하면 PRD 갱신을 권고)
- **착수 확인 없이 계획 작성 시작** (1단계 게이트 필수)
- PLAN 완료 후 체크리스트로 자동 진행
