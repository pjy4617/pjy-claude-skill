---
name: prd-setup
description: "prd-plan 플러그인 환경 초기 설정. 작성 에이전트(prd-writer) 1종과 문서 종류별 검수 에이전트 3종(prd-reviewer: PRD·외부 문서 / prd-plan-reviewer: PLAN / prd-checklist-reviewer: 체크리스트), CLAUDE.md 규약, docs/prd·plan·checklist·reviews 디렉토리를 프로젝트에 설치한다. 플러그인 설치 후 최초 1회 실행. idempotent — 여러 번 실행해도 안전하며 누락분만 보충한다. 'prd-plan 설정', 'PRD 플러그인 셋업', 'prd 에이전트 설치', '/prd-setup', 'PRD 환경 초기화' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, AskUserQuestion
---

# prd-plan 환경 초기 설정

작성/검수 에이전트와 문서 규약을 현재 프로젝트에 설치합니다.

> **왜 에이전트를 설치하는가**: 이 워크플로의 핵심은 작성자와 검수자의 분리입니다.
> 에이전트가 없으면 메인 세션이 자기가 쓴 문서를 자기가 검수하게 되고, 그 순간 검수는 형식이 됩니다.

## 실행 절차

### 1단계 — 플러그인 디렉토리 확인

`${CLAUDE_SKILL_DIR}` 기준 상위에서 `agents/`와 `claude-md/`를 찾습니다.

```
PLUGIN_DIR = ${CLAUDE_SKILL_DIR}/../../
```

찾지 못하면 Glob으로 탐색합니다: `~/.claude/plugins/**/prd-plan/agents/*.md`

### 2단계 — 프로젝트 경로 확인

> PRD·계획 문서를 관리할 프로젝트 경로를 알려주세요.
> (엔터만 누르면 현재 디렉토리에 설치합니다)

- 입력이 있으면 그 경로를 `PROJECT_ROOT`로, 없으면 현재 작업 디렉토리
- 존재하지 않으면 생성 여부를 확인 후 생성

### 3단계 — 에이전트 설치

```bash
mkdir -p ${PROJECT_ROOT}/.claude/agents
```

복사 대상 (`PLUGIN_DIR/agents/`) — 작성 1 + 검수 3:

| 파일 | 역할 | 권한 |
|------|------|------|
| `prd-writer.md` | 30년 경력 PM 페르소나 작성 전문가 (PRD·PLAN·체크리스트 작성, 리뷰 반영) | 읽기+쓰기 |
| `prd-reviewer.md` | **PRD·외부 문서** 검수 (7카테고리) | **쓰기 없음** |
| `prd-plan-reviewer.md` | **PLAN 전용** 검수 (커버리지 실질·의존 강제·순환 우회·분해 실질 6축) | **쓰기 없음** |
| `prd-checklist-reviewer.md` | **체크리스트 전용** 검수 (완결성·주체 분리·근거 칸·차단 표기·분리 구조 5축) | **쓰기 없음** |

> 검수자를 문서 종류별로 나눈 이유: 각 문서에서 사고가 나는 지점이 다릅니다. PLAN은 "작업을 다 해도 요구가 달성되지 않는" 연결과 순서 미강제, 체크리스트는 "다 체크해도 완료를 증명 못 하는" 주체 혼입과 근거 부재입니다. 범용 검수자 하나로는 이 관점이 프롬프트에 매번 실려야 합니다.

각 파일을 Read해서 `${PROJECT_ROOT}/.claude/agents/`에 동일한 이름으로 Write합니다.
이미 존재하면 덮어쓰기 전에 사용자에게 확인합니다.

> 이름 충돌 확인: `.claude/agents/`에 같은 이름의 다른 에이전트가 있으면 설치를 멈추고 사용자에게 알립니다.

### 4단계 — 문서 디렉토리 생성

```bash
mkdir -p ${PROJECT_ROOT}/docs/prd ${PROJECT_ROOT}/docs/plan ${PROJECT_ROOT}/docs/checklist ${PROJECT_ROOT}/docs/reviews
```

프로젝트가 이미 다른 문서 구조를 쓰고 있으면(예: `documents/`, `spec/`) 그 구조를 확인하고 사용자에게 물어 맞춥니다. 억지로 `docs/`를 만들지 않습니다.

### 5단계 — CLAUDE.md 병합

`PLUGIN_DIR/claude-md/CLAUDE.md` 내용을 `${PROJECT_ROOT}/.claude/CLAUDE.md`(없으면 `${PROJECT_ROOT}/CLAUDE.md`)에 추가합니다.

- 대상 파일이 없으면 새로 생성
- 있으면 **마커 블록**으로 감싸 추가하고, 기존 내용은 보존

```markdown
<!-- prd-plan:start -->
...템플릿 내용...
<!-- prd-plan:end -->
```

- 마커가 이미 있으면 블록 내부만 교체 (중복 주입 방지)
- 4단계에서 문서 경로를 바꿨다면 템플릿의 경로도 함께 치환합니다

### 6단계 — 선택 의존성 확인

```bash
python3 --version 2>&1 || py -3 --version 2>&1     # 추적성 스크립트용
ls ~/.claude/plugins/**/doc-atomize 2>/dev/null     # 대용량 문서 분할용
```

| 항목 | 없을 때 |
|------|---------|
| `python3` | 추적성 검증을 수동 대조로 대체한다고 안내 (Windows는 `py -3`/`python` 시도) |
| `doc-atomize` | 대용량 문서는 통독으로 처리. `/plugin install doc-atomize@pjy-skills` 안내 |

둘 다 **필수가 아닙니다** — 없어도 워크플로는 동작합니다.

### 7단계 — 검증 및 리포트

```bash
ls ${PROJECT_ROOT}/.claude/agents/prd-{writer,reviewer,plan-reviewer,checklist-reviewer}.md
ls -d ${PROJECT_ROOT}/docs/prd ${PROJECT_ROOT}/docs/plan ${PROJECT_ROOT}/docs/checklist ${PROJECT_ROOT}/docs/reviews
grep -c "prd-plan:start" ${PROJECT_ROOT}/.claude/CLAUDE.md
```

리포트 형식:

```
prd-plan 설치 완료: <PROJECT_ROOT>
에이전트: prd-writer ✅ / prd-reviewer ✅ / prd-plan-reviewer ✅ / prd-checklist-reviewer ✅
디렉토리: docs/prd, docs/plan, docs/checklist, docs/reviews ✅
CLAUDE.md: 마커 주입 ✅ (신규 생성 | 기존에 추가)
선택 의존성: python3 ✅ / doc-atomize ⚠️ 미설치
다음: /prd-write <주제> 로 PRD 작성 시작
```

**에이전트는 새 세션부터 인식**됩니다 — 필요하면 세션 재시작을 안내합니다.

## idempotent 보장

- 이미 있는 파일은 덮어쓰기 확인 후에만 갱신
- 디렉토리는 `mkdir -p`
- CLAUDE.md는 마커 블록 내부만 교체
- 여러 번 실행해도 중복 주입·기존 내용 손실이 없어야 합니다
