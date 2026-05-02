---
name: parallel-delegation
description: How to delegate independent work units to multiple subagents in parallel via the Agent tool — bundling Agent calls in a single response so they execute concurrently rather than sequentially. Use this skill whenever the user gives a multi-part task (e.g., "build A and B and C", "refactor X and add tests", "implement frontend + backend"), when the request spans multiple independent files/domains, when exploration + implementation can run side-by-side, when the user says "in parallel" / "동시에" / "한꺼번에", or mentions subagents / agent teams / multi-agent workflows — even if they do not explicitly say "delegate". Trigger this skill BEFORE reaching for sequential single-agent execution on any task that decomposes cleanly into independent units. 서브에이전트 병렬 위임, 다중 에이전트 동시 실행, 작업 분해 패턴.
---

# 서브에이전트 병렬 위임 (Parallel Subagent Delegation)

여러 독립 작업을 **하나의 응답 메시지**에 다수의 `Agent` 도구 호출로 묶어 동시에 실행하는 워크플로. 순차 실행 대비 벽시계 시간을 가장 느린 작업 하나의 길이로 압축한다.

## 왜 이 스킬이 중요한가

서브에이전트는 **하나의 응답 안에 여러 Agent 호출이 함께 있을 때만** 병렬 실행된다. 호출을 응답 사이로 나누면 순차 실행이 되어 시간 이득이 사라진다. 또한 각 서브에이전트는 **현재 대화 컨텍스트를 모르는 새 인스턴스**이므로, 프롬프트가 self-contained가 아니면 환각·오해·중복 작업이 발생한다. 이 스킬은 그 두 가지 함정을 피하기 위한 절차다.

## 핵심 원칙

1. **메시지 단위 = 병렬 단위.** 하나의 응답에 묶인 Agent 호출들만 동시에 시작된다. 첫 호출 결과를 보고 두 번째를 호출하면 순차다.
2. **독립성이 전제.** A의 결과가 B의 입력이라면 병렬 불가 — 순차로 짠다.
3. **Self-contained 프롬프트.** 서브에이전트에게는 대화 맥락이 없다. 목표·관련 파일·제약·산출물 형식을 매 호출마다 다시 적는다.
4. **결과 합성은 메인의 책임.** 서브에이전트의 요약을 그대로 사용자에게 전달하지 말고, 실제 산출물(파일 변경 등)을 검증하고 통합한다.

## 8단계 절차

### 1. 분해 (Decomposition)
사용자 요청을 독립 실행 가능한 단위로 자른다. 판단 기준:

- A의 결과가 B의 입력인가? → 순차
- 서로 다른 파일/도메인인가? → 병렬 가능
- 같은 파일을 동시 수정해야 하는가? → 병렬 + worktree 격리

### 2. 에이전트 매칭
각 작업에 가장 적합한 `subagent_type`을 고른다. 일반론:

| 작업 유형 | 권장 에이전트 | 모델 (§3 정책) |
|---|---|---|
| 코드베이스 탐색 / 심볼 위치 | `Explore` | sonnet |
| 단순 구현 / 리팩토링 | 일반 구현 에이전트 | opus |
| 복잡한 자율 작업 | 깊이 있는 구현 에이전트 | opus |
| 코드/보안 리뷰 | 리뷰 전문 에이전트 | opus |
| 테스트 작성 / 전략 | 테스트 엔지니어 | opus |
| 빌드 실패 / 타입 오류 | 빌드 픽서 | opus |
| 검증 / 완료 증거 수집 | 검증 에이전트 | opus |

프로젝트마다 도메인 전문 에이전트가 `.claude/agents/`에 있을 수 있다. 있다면 우선 사용한다. 카탈로그의 에이전트 frontmatter에 적힌 기본 모델(haiku/sonnet/opus)은 정보용이며, 본 스킬은 위 표의 §3 정책 모델로 호출한다.

### 3. 모델 라우팅
**기본값: `model: "opus"`. 단순 탐색만 `model: "sonnet"`.**

본 스킬은 비용 최적화보다 **품질 일관성**을 우선하지만, 추론 깊이가 거의 필요 없는 단순 탐색은 예외로 둔다.

| 작업 유형 | 모델 |
|---|---|
| 단순 탐색 — 파일 위치, 심볼 찾기, 키워드 grep, "어디에 정의되어 있나" 류 | **`sonnet`** |
| 그 외 모든 호출 — 구현, 분석, 리뷰, 테스트, 검증, 디버깅, 리팩토링 등 | **`opus`** |

```
Agent(Explore,         model="sonnet", "기존 X 위치 찾기")     ← 단순 탐색
Agent(executor,        model="opus",   "...")                  ← 구현
Agent(code-reviewer,   model="opus",   "...")                  ← 리뷰·검증
Agent(test-engineer,   model="opus",   "...")                  ← 테스트 작성
```

판단 기준: 서브에이전트가 **읽고 보고만** 하면 sonnet, **판단·작성·수정**을 하면 opus. `Explore` 에이전트 호출은 거의 항상 sonnet, 그 외 에이전트는 거의 항상 opus다. 의심스러우면 opus.

`model` 파라미터를 생략하면 에이전트 정의의 frontmatter 또는 부모 세션 모델을 상속받지만, **명시적으로 적어 의도를 분명히 한다**.

### 4. 단일 메시지 묶기 ★
이 단계가 병렬화의 결정적 순간이다. 같은 응답 안에 여러 Agent 호출을 동시에 발사한다.

```
[하나의 응답]
 ├─ Agent(executor,      "UI 컴포넌트 작성")     ┐
 ├─ Agent(executor,      "API 핸들러 작성")       ├─ 동시 시작
 ├─ Agent(architect,     "DB 스키마 설계")        │
 └─ Agent(test-engineer, "통합 테스트 작성")     ┘
```

### 5. Self-contained 프롬프트 작성
각 Agent 호출의 `prompt`에 다음을 포함한다.

- **목표**: 무엇을 왜 만드는가
- **컨텍스트**: 관련 파일 경로 (`src/foo.ts:120` 형식), 관련 함수, 이미 시도된 것
- **제약**: 코딩 규칙, 표준, 사용/금지 라이브러리
- **산출물 형식**: 파일 작성 vs 보고서 / 단어 수 / 산출물 위치
- **연구인지 코드 작성인지 명시**: 서브에이전트는 모른다

#### 프롬프트 템플릿
```
[목표] 무엇을 / 왜
[컨텍스트] 관련 파일·함수·이전 시도
[제약] 코딩 규칙·표준·금지사항
[산출물] 파일 변경 / 보고서 (분량·형식)
[모드] 연구만 vs 코드 작성
```

#### 좋은 예 / 나쁜 예
**❌ 나쁨**: `"로그인 만들어줘"`
**✅ 좋음**:
```
[목표] src/auth/ 아래에 JWT 검증 미들웨어 추가
[컨텍스트] 기존 src/middleware/logger.ts:42의 미들웨어 등록 패턴 따를 것.
       라우터 부착 위치는 src/server.ts:120
[제약] 프로젝트 인증 사양 문서 §X.Y 준수, 외부 라이브러리 추가 금지,
       프로젝트 코딩 규칙(.editorconfig) 따르기
[산출물] src/auth/jwt_middleware.ts 신규 파일 작성
[모드] 코드 작성. 테스트는 별도 에이전트가 담당하므로 구현만.
```

### 6. Worktree 격리 결정
같은 파일 영역을 여러 에이전트가 수정한다면 `isolation: "worktree"`를 추가한다. 각 에이전트가 독립 Git worktree에서 작업해 충돌을 막는다. 변경이 없으면 worktree는 자동 정리된다. 같은 파일을 건드리지 않는다면 격리 없이 본 워크트리에서 작업해도 된다 (오버헤드 ↓).

### 7. Foreground vs Background
- **Foreground (기본)**: 결과를 받아야 다음 단계 진행 — 리서치, 설계 검토
- **Background (`run_in_background: true`)**: 메인이 다른 일 하는 동안 돌리기 — 빌드, 긴 테스트, 독립 사이드 작업

Background로 돌렸다면 폴링하지 말고 완료 알림을 기다린다 (sleep / 폴링 금지).

### 8. 합성과 검증
서브에이전트가 반환하는 것은 **요약**이다. 메인의 책임:

1. 요약을 그대로 믿지 말고 실제 파일 변경을 직접 확인 (trust but verify)
2. 여러 에이전트 결과 간 충돌·중복 해소
3. 사용자에게는 통합된 결론 한 덩어리로 전달 — 각 raw 출력을 그대로 노출하지 않음

## 실패 처리

- 한 에이전트가 실패해도 다른 결과는 살린다.
- 재시도할 때 같은 프롬프트를 그대로 반복하지 말고 부족했던 컨텍스트를 추가한다.
- 진행 중인 에이전트와 이어서 작업하려면 새 `Agent` 호출이 아니라 `SendMessage({to: name})`을 쓴다.

## 흔한 함정

| 함정 | 증상 | 해결 |
|---|---|---|
| 호출을 응답 사이로 나눔 | 병렬이 아니라 순차로 실행됨 | 한 응답에 묶기 |
| 프롬프트에 "위에서 본 것처럼" | 서브에이전트가 맥락 없어 헤맴 | 매 호출마다 컨텍스트 다시 적기 |
| 탐색 작업까지 opus로 호출 | 불필요한 비용·지연 | `Explore` 호출만 sonnet으로 분리 (§3 참조) |
| 서브에이전트 요약을 그대로 사용자에게 | 거짓 완료 보고 위험 | 실제 파일 변경 검증 후 통합 |
| 병렬화에 집착 | 의존성 있는 작업까지 병렬화 시도 | 의존성 있으면 순차로 짜기 |
| 같은 파일을 여러 에이전트가 동시 수정 | 파일 충돌·덮어쓰기 | `isolation: "worktree"` 적용 (§6 참조) |

## 사용 시기 결정

다음 중 하나라도 해당하면 이 스킬을 적용한다.

- 사용자가 다중 의도를 표명 ("A 하고 B 하고 C")
- 프론트/백/DB/테스트 등 서로 다른 도메인 동시 작업
- 탐색(Explore)과 구현을 동시에 진행 가능
- 리뷰 + 구현 + 테스트 작성이 독립적
- 사용자가 "병렬", "동시", "한꺼번에", "team", "subagent" 명시
- 단일 에이전트로 진행하면 한참 걸릴 작업

다음 경우엔 **이 스킬을 쓰지 않는다**.

- 작업이 본질적으로 순차 (A → B → C 의존)
- 단순 한 줄 수정, 한 파일 읽기
- 사용자가 직접 단계별 확인을 원함

## 마무리 보고

서브에이전트 작업이 끝나면 사용자에게 다음을 한 덩어리로 전달한다.

1. 어떤 작업을 어느 에이전트에 병렬로 위임했는지 (한 줄 요약)
2. 통합된 결과 (변경된 파일 목록, 핵심 결정사항)
3. 추가 검증이 필요한 부분 (있다면)

raw 서브에이전트 출력을 그대로 붙여넣지 않는다.
