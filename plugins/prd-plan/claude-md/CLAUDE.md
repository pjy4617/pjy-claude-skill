# PRD · 실행계획 문서 규약 (prd-plan)

이 프로젝트는 `prd-plan` 플러그인으로 요구사항·계획 문서를 관리한다.

## 문서 위치

| 문서 | 경로 | 만드는 스킬 |
|------|------|-------------|
| PRD | `docs/prd/PRD-<slug>.md` | `/prd-write` |
| 실행 계획 | `docs/plan/PLAN-<slug>.md` | `/prd-plan` |
| 체크리스트 | `docs/checklist/CHECKLIST-<slug>.md` | `/prd-checklist` |
| 검수 리포트 | `docs/reviews/REVIEW-<대상>-r<N>.md` | 위 스킬들의 검수 라운드 |

## ID 규약 (추적성)

```
REQ-###  요구사항 (PRD)      → AC-###-#  수용 기준
TASK-### 작업 (PLAN)          → 근거 요구사항 REQ-### 필수
CHK-###  체크 항목 (체크리스트) → 참조 작업 TASK-### 필수
OPEN-### 미결 이슈            → 결정 주체 명시
```

- ID는 **재사용·재배치 금지**. 삭제 시 블록을 남기고 `삭제됨` 표기
- 연결이 끊기면 기계 검증에서 잡힌다:

```bash
python3 ~/.claude/plugins/**/prd-plan/skills/prd-checklist/assets/check_traceability.py \
  --prd docs/prd/PRD-x.md --plan docs/plan/PLAN-x.md --checklist docs/checklist/CHECKLIST-x.md
```

## 절대 규칙

1. **작성과 검수를 같은 컨텍스트에서 하지 않는다.** 작성은 `prd-writer`, 검수는 문서 종류별 전용 에이전트 — PRD·외부 문서는 `prd-reviewer`, PLAN은 `prd-plan-reviewer`, 체크리스트는 `prd-checklist-reviewer`. 검수자는 모두 **쓰기 권한이 없다**.
2. **`status: approved`는 사용자만 전이한다.** 에이전트가 자기 문서를 승인하지 않는다.
3. **모르는 값을 지어내지 않는다.** `(미정 — OPEN-###)`로 남기고 미결 이슈 표에 등록한다.
4. **절대 날짜·시간 공수를 만들지 않는다.** 규모는 S/M/L/XL, 일정은 상대 순번·마일스톤 라벨. 사용자가 제공한 값만 출처와 함께 기재.
5. **완료 표시에는 근거가 있어야 한다.** 근거 없는 `[x]`는 검증 스크립트가 ERROR로 잡는다.
6. **모든 요구사항에는 검증 가능한 수용 기준(AC)이 있다.**
7. **단계 전이는 자동으로 하지 않는다.** PRD가 끝났다고 이어서 PLAN을, PLAN이 끝났다고 이어서 체크리스트를 만들지 않는다. `/prd-plan`과 `/prd-checklist`는 **착수 확인 게이트**로 시작하며, 사용자가 진행을 선택하기 전에는 작성 에이전트를 호출하지 않는다. 미결 이슈가 범위·안전에 걸려 있는데 다음 단계로 넘어가면 문서를 두 번 만들게 된다.

## PRD 프로파일

| profile | stack | 대상 | 다음 단계 |
|---------|-------|------|-----------|
| `software` | `frontend` | React 화면·대시보드 | react-vite |
| `software` | `backend` | C++ / C# / Python 서비스·엔진 | 구현 |
| `software` | `full-stack` | 위 둘 + API 계약 섹션 필수 | react-vite + 백엔드 |
| `hardware-firmware` | — | 보드·MCU·FPGA·모션 장비 | kicad-design / stm32f4 / vivado |
| `research-PoC` | — | 가설 검증·타당성 | rlcontrol(rl-assess) |

## 요청 → 스킬 라우팅

| 요청 | 스킬 |
|------|------|
| "PRD 써줘", "요구사항 정리" | `/prd-write` |
| "실행 계획", "WBS", "작업 분해" | `/prd-plan <PRD경로>` |
| "체크리스트 만들어줘" | `/prd-checklist <PLAN경로>` |
| "진척 어때?" | `/prd-checklist --status <경로>` |
| "요구 바뀌었어" | `/prd-write`(PRD 갱신) → `/prd-checklist --sync` |
| "이 문서 검토해줘" (외부 문서) | `/prd-review <경로>` |

## 대용량 문서

PRD/PLAN이 **40KB를 넘으면**(줄 수가 아니라 바이트 기준) `doc-atomize`로 분할한다.
**검수 루프 중에는 분할하지 않고**, 승인 후에 분할해 이후 조회는 `<doc-id>.index.md`를 진입점으로 쓴다.
