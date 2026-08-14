---
name: prd-write
description: "요구 인터뷰부터 PRD(제품/시스템 요구사항 문서) 작성과 검수까지 수행하는 워크플로. 메인 세션이 사용자와 인터뷰해 문제·사용자·성공지표·범위/비범위·제약을 확정하고, 30년 경력 PM 페르소나 작성 에이전트(prd-writer)가 프로파일별(software/hardware-firmware/research-PoC) PRD를 REQ-ID + 검증 가능한 수용 기준으로 작성한 뒤, 쓰기 권한이 없는 검수 에이전트(prd-reviewer)가 7카테고리로 등급 리뷰하고 최대 3라운드 반영 루프를 돈다. 승인은 사용자만 한다. 사용자가 'PRD 작성해줘', '요구사항 문서 만들어줘', '제품 요구사항 정의서', '기획서 작성', 'PRD 써줘', '/prd-write <주제>' 등을 요청하거나, 새 프로젝트/기능의 요구를 정리해 문서로 남기려 할 때 자동 적용. 기존 PRD를 고치지 않고 검수만 원하면 prd-review 담당."
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion
---

# prd-write — 인터뷰 → PRD 작성 → 검수 루프

PRD를 **쓰는 사람과 보는 사람을 분리**해서 만드는 워크플로. 작성 에이전트는 자기 문서를 통과시킬 수 없고, 검수 에이전트는 문서를 고칠 수 없다.

## 이 스킬의 전제 3가지

1. **인터뷰는 메인 세션이 한다.** 서브에이전트는 사용자에게 질문할 수 없다(AskUserQuestion 불가). 확정된 답변을 블록으로 만들어 작성 에이전트에 넘긴다.
2. **모르는 것은 미결 이슈로 남긴다.** 빈칸을 그럴싸한 문장으로 메우는 것이 PRD 최대의 해악이다.
3. **`approved` 전이는 사용자만 한다.** 에이전트도, 이 스킬도 자가 승인하지 않는다.

## 사전 조건

- 에이전트 2종 설치 필요 → 미설치면 `/prd-setup` 안내 (없으면 메인 세션이 역할을 흉내내되, 검수 라운드는 반드시 **별도 Task 호출**로 분리한다)
- `python3` (추적성 스크립트용, 선택)
- 대용량 문서 취급 시 `doc-atomize` 플러그인 (선택, 없으면 폴백)

---

## 실행 절차 (8단계)

### 1단계 — 입력 모드 판별

| 모드 | 상황 | 처리 |
|------|------|------|
| **A. 인터뷰** | 백지에서 시작 | 2단계 인터뷰 전체 수행 |
| **B. 자료 기반** | 기존 기획서·회의록·이슈가 있음 | 자료를 먼저 읽고 **채워진 항목은 확인만**, 빈 항목만 인터뷰 |
| **C. 역공학** | 이미 만든 것을 문서화 | 코드베이스·PCB·설계 산출물을 읽어 현행 사양을 추출한 뒤 빈 항목 인터뷰 |

B·C에서 입력 자료가 크면(**40KB 초과** — 줄 수가 아니라 바이트 기준) `references/large-doc-handling.md`의 **입력 인제스트** 절차를 따른다 (doc-atomize 또는 manual-digest로 먼저 분할/요약).

### 2단계 — 프로파일 확정

`references/prd-profiles.md`를 읽고 AskUserQuestion으로 하나를 고른다.

| 프로파일 | `stack` | 대상 |
|----------|---------|------|
| `software` | `frontend` | React 화면·대시보드·조작 UI (react-vite 입력 규격 포함) |
| `software` | `backend` | C++ / C# / Python 서비스·엔진·CLI |
| `software` | `full-stack` | 위 둘 + API 인터페이스 계약 섹션 필수 |
| `hardware-firmware` | — | 보드·MCU 펌웨어·FPGA·모션 장비 (kicad-design / stm32f4 / vivado 입력 규격 포함) |
| `research-PoC` | — | 가설 검증·실험·타당성 조사 |

판단이 명확하면(예: KiCad 회로도를 만들 예정, React 대시보드) 질문 없이 제안하고 확인만 받는다.
`software`를 고르면 `stack`까지 반드시 확정한다 — 필수 항목이 스택별로 다르다.

### 3단계 — 인터뷰 (메인 세션)

`references/interview-guide.md`의 질문 세트를 사용한다. **AskUserQuestion으로 한 번에 최대 4문항**, 총 2~3회를 넘기지 않는다.

필수 확정 7항목: ①해결할 문제 ②사용자/이해관계자 ③성공 지표 ④필수 범위 ⑤비범위 ⑥제약(기술·일정·예산·규정) ⑦리스크/미지수

답변을 다음 형식으로 정리한다. **이 블록이 작성 에이전트의 유일한 사실 원천이다.**

```markdown
## 인터뷰 확정 사항
- 문제: ...
- 사용자: ...
- 성공 지표: ...
- 필수 범위: ...
- 비범위: ...
- 제약: ...
- 리스크/미지수: ...
- 사용자가 "모른다"고 한 항목: ...   ← 그대로 미결 이슈가 된다
```

사용자가 인터뷰를 생략하라고 하면 생략하되, 미확정 항목은 **전부 미결 이슈로 등록**하고 그 사실을 최종 보고에 명시한다. 이때는 확정 사항 블록 대신 아래를 그대로 넘긴다 — 무엇을 사실로 취급할지 작성 에이전트가 헷갈리지 않게 하는 것이 요점이다.

```markdown
## 인터뷰 확정 사항
**인터뷰 미수행.** 사용자 확인을 받은 항목이 없다.
- <입력 자료 경로>에 **명시적으로 적힌 것만** 확정 사실로 취급한다
- 그 밖의 값은 지어내지 말고 `OPEN-###`로 등록하고 본문에는 `(미정 — OPEN-###)`로 표기한다
- 특히 다음은 반드시 미결로: <값이 필요한 항목을 나열 — 한도·기준·상한·외부 사실 등>
```

### 4단계 — 작성 위임

`prd-writer` 에이전트를 Task로 호출한다. 프롬프트에 반드시 포함:

```
작업 종류: PRD 작성
프로파일: <software|hardware-firmware|research-PoC> / stack: <frontend|backend|full-stack — software일 때만>
출력 경로: <PROJECT>/docs/prd/PRD-<slug>.md
references 절대 경로:
  - <plugin>/skills/prd-write/references/prd-template-core.md
  - <plugin>/skills/prd-write/references/prd-profiles.md
입력 자료 경로: <있으면>
## 인터뷰 확정 사항
<3단계 블록 그대로>
```

`docs/prd/` 디렉토리는 메인 세션이 미리 생성한다. `<slug>`는 kebab-case 주제명.

### 5단계 — 검수 위임 (라운드 1)

`prd-reviewer` 에이전트를 **별도 Task**로 호출한다. 작성 에이전트의 응답 요약을 근거로 주지 않고, **파일 경로만** 준다.

```
검수 대상: <PRD 경로>
프로파일: <profile> / stack: <stack> / 라운드: 1
상위 문서: (없음)
references 절대 경로: quality-rubric.md, prd-template-core.md, prd-profiles.md
검증 스크립트: <plugin>/skills/prd-checklist/assets/check_traceability.py
```

반환된 리포트 본문을 메인 세션이 `docs/reviews/REVIEW-<slug>-r1.md`로 저장한다(검수 에이전트는 파일을 쓰지 않는다).

검수 에이전트가 리포트를 반환하지 못하면 **메인 세션이 대신 검수하지 않는다** — 1회 재위임하고, 그래도 실패하면 `검수: 미수행`을 명시한 채 사용자에게 선택지를 제시한다 (`quality-rubric.md` → 검수 위임이 실패했을 때).

### 6단계 — 반영 루프 (최대 3라운드)

```
while (CRITICAL > 0 || MAJOR > 0) && 라운드 <= 3:
    prd-writer 재호출 (작업 종류: 리뷰 반영, 직전 리포트 경로, 라운드 N)
    prd-reviewer 재호출 (라운드 N)
    리포트 저장
```

- 라운드마다 리포트를 별도 파일로 남긴다 — 이력이 곧 검수 증거다.
- **지적 건수가 늘어나면** 리뷰어의 `⚠️ 범위 확대 감지`를 확인하고, 사용자에게 방향을 물을지 판단한다.
- 3라운드 후에도 잔여가 있으면 **임의로 통과시키지 않고** 7단계로 간다.

### 7단계 — 사용자 확인 및 승인

AskUserQuestion으로 결과를 제시한다:

- 잔여 CRITICAL/MAJOR 목록 (있으면)
- 미결 이슈 목록 — **사용자 결정이 필요한 것**을 앞에 둔다
- 선택지: `승인(approved)` / `미결 해소 후 재작성` / `현 상태로 보류(in-review 유지)`

`승인`을 선택한 경우에만 프론트매터 `status: approved`, `approved_at`(사용자 제공 날짜 또는 생략), `approved_by`를 기록한다.

### 8단계 — 마무리

1. **대용량 분할**: 승인된 PRD가 **40KB를 넘으면** `references/large-doc-handling.md`에 따라 `/doc-atomize`를 실행한다. **검수 루프 중에는 절대 분할하지 않는다.**
2. **추적성 스크립트**: `check_traceability.py --prd <경로>`로 REQ 중복·AC 누락을 최종 확인한다.
3. 보고 형식:

```
PRD 작성 완료: docs/prd/PRD-<slug>.md (프로파일 X, 상태 approved|in-review, v1.0)
요구사항: REQ n건 (MUST n / SHOULD n / MAY n)
검수: R1 C n/M n → R2 C n/M n → 최종 C 0/M 0
미결 이슈: n건 (사용자 결정 대기 n건)
분할: 적용(.claude/atomized/<id>) | 미적용(임계값 미만)
다음 단계 제안: /prd-plan docs/prd/PRD-<slug>.md  ← 제안일 뿐, 자동 실행하지 않는다
```

4. **여기서 멈춘다.** PRD가 승인되었더라도 **이어서 PLAN을 만들지 않는다.** 다음 단계는 사용자가 명시적으로 요청할 때만 시작한다 — `/prd-plan`은 자체 착수 확인 게이트를 갖고 있으므로, 사용자가 요청해도 그 게이트를 건너뛰지 않는다.

---

## 하지 않는 것

- 설계·구현 방식 결정 (PRD는 무엇을/왜이지 어떻게가 아니다)
- 절대 날짜·인원 배정 (→ `prd-plan`의 `estimation-policy.md` 규칙)
- 사용자 승인 없는 `approved` 전이
- 검수 없이 산출물 확정
- **사용자 요청 없이 다음 단계(PLAN·체크리스트)로 자동 진행**
