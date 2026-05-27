---
name: react-vite-frontend
description: "React 19 + Vite 8 + TypeScript 프론트엔드 개발 워크플로. 범용 구현/품질검증(program-expert/qa-expert) + UI 라이브러리별 심화 specialist(fluent-ui/shadcn-ui 구현·QA) 6개 에이전트를 역할 분리로 조율·라우팅해 production 코드를 작성하고 검증한다. UI 라이브러리는 Fluent UI v9 또는 shadcn/ui(Radix+Tailwind) 중 프로젝트당 택1, Zustand+Immer, (선택) react-konva 캔버스·@dnd-kit 드래그앤드롭 스택 지원. 'React 컴포넌트 만들어', 'Vite 프론트엔드 개발', '이 PRD로 화면 구현해줘', 'Zustand 스토어 추가', 'shadcn으로 만들어', 'Fluent UI로 만들어', 'react-konva 캔버스 에디터', '프론트 기능 구현하고 테스트까지', 'React 19 코드 리뷰', '컴포넌트 테스트 작성' 등 React 19 + Vite 프론트엔드 작업 요청에 자동 적용."
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# React 19 + Vite 8 프론트엔드 개발

> 이 스킬은 React 19 + Vite 8 + TypeScript 프론트엔드를 **구현 → 검증**의 역할 분리 흐름으로 개발합니다.
> 구현/검증은 범용 에이전트와 UI 라이브러리 specialist가 나눠 맡고, `react-vite-setup` 스킬로 타겟 프로젝트의 `.claude/agents/`에 설치됩니다.

## 에이전트 구성 (6종 = 범용 2 + UI specialist 4)

| 레이어 | 구현 | 품질검증(QA) |
|--------|------|--------------|
| **범용** (React/Vite/상태/구조·테스트 전략) | `react-vite-program-expert` | `react-vite-qa-expert` |
| **Fluent UI v9** (UI 레이어) | `react-vite-fluent-ui-expert` | `react-vite-fluent-ui-qa-expert` |
| **shadcn/ui** (UI 레이어) | `react-vite-shadcn-ui-expert` | `react-vite-shadcn-ui-qa-expert` |

**라우팅 규칙**: React 골격·상태·라우팅·비-UI 로직 → 범용. 테마·컴포넌트 커스터마이즈·SSR 스타일·portal/a11y 테스트 등 UI 라이브러리 심화 → 프로젝트가 선택한 라이브러리의 specialist(단계 1에서 감지). UI specialist는 **프로젝트가 선택한 한 라이브러리 쪽만** 씁니다 — Fluent와 shadcn을 섞지 않습니다.

## 왜 역할을 나누는가

한 에이전트가 구현과 검증을 모두 하면 **자기 검증의 함정**에 빠집니다 — 자기가 짠 코드의 약점을 자기가 보지 못합니다. 구현과 품질검증(QA)을 분리하면, QA가 독립된 시각으로 사용자 관점·성능·회귀를 점검해 함정이 구조적으로 차단됩니다. 그래서 이 워크플로는 구현/검증을 **별도 패스**로 운용합니다.

## 워크플로우 개요

```
[1] 컨텍스트 파악 — package.json / PRD / 기존 구조 읽기
 ↓
[2] 분해 — 기능을 타입·스토어·컴포넌트 단위로 나누기
 ↓
[3] 구현 — 범용(program-expert) + UI specialist에 위임 (production 코드)
 ↓
[4] 동작 확인 — npm run dev / 빌드로 컴파일·렌더 확인
 ↓
[5] 검증 — 범용(qa-expert) + UI QA specialist에 위임 (테스트·a11y·성능)
 ↓
[6] 회귀 수정 — QA 지적사항을 다시 해당 구현 에이전트로 반영
```

구현과 검증은 동일한 활성 컨텍스트에서 한 에이전트가 겸하지 않습니다. 구현이 끝난 산출물을 QA 에이전트가 받아 평가하는 **순차 핸드오프**입니다.

---

## 단계 1: 컨텍스트 파악

작업 전 프로젝트 실제 상태를 읽습니다. 추측은 환각의 원인입니다.

| 읽을 것 | 얻는 정보 |
|---------|----------|
| `package.json` | React/Vite/의존성 버전, 스크립트(dev/build/test), **UI 라이브러리** |
| `vite.config.ts`, `tsconfig.json` | React Compiler 사용 여부, strict 설정, 청크 분리 |
| `components.json`, `tailwind.config.*` | shadcn/ui 사용 여부 |
| PRD/요구사항 문서, `CLAUDE.md` | 제품 범위, **성능 목표**, 지원 브라우저, UI 라이브러리 선택 기록 |
| 기존 `src/` 구조 | 폴더 컨벤션, 상태관리 선택, 컴포넌트 패턴 |

### UI 라이브러리 결정 (Fluent UI v9 vs shadcn/ui)

이 워크플로는 두 UI 라이브러리를 지원하되, **프로젝트당 하나만** 씁니다(섞으면 스타일링·번들이 중복·충돌). 다음 순서로 결정합니다:

1. **감지** — `@fluentui/react-components`가 있으면 Fluent UI, `components.json` + `tailwindcss`가 있으면 shadcn/ui.
2. **기록 확인** — `CLAUDE.md`에 선택이 적혀 있으면 그것을 따름.
3. **둘 다 없는 신규 프로젝트** — 사용자에게 질문해 결정. (질문하지 않고 임의로 고르지 않음)

결정된 라이브러리의 상세 규칙은 해당 참조 문서를 읽고 위임 프롬프트에 반영합니다:
- Fluent UI v9 → `references/ui-fluent-ui.md`
- shadcn/ui → `references/ui-shadcn-ui.md`

신규 프로젝트라 설정이 없으면, 먼저 스캐폴딩을 제안합니다(아래 "신규 프로젝트 스캐폴딩").

## 단계 2: 분해

기능을 의존 방향(안→밖)으로 나눕니다:

1. **타입** (`types/`) — 데이터 모델
2. **스토어** (`store/`) — Zustand 액션·상태
3. **컴포넌트** (`components/`) — UI
4. **통합** — 라우트/페이지에 연결

독립적인 기능 여러 개를 동시에 만들 때는 `parallel-delegation` 패턴으로 program-expert를 병렬 호출할 수 있습니다(서로 다른 파일이라 충돌 없을 때만).

## 단계 3: 구현 (구현 에이전트에 위임)

작업 성격에 따라 에이전트를 고릅니다:
- **React 골격·상태·라우팅·비-UI 로직** → `react-vite-program-expert`
- **UI 레이어 심화**(테마, 컴포넌트 커스터마이즈, SSR 스타일) → 단계 1에서 감지한 라이브러리의 specialist (`react-vite-fluent-ui-expert` 또는 `react-vite-shadcn-ui-expert`)
- 한 기능이 둘 다 걸치면 골격 먼저(program-expert), UI 레이어를 specialist로 — 또는 서로 다른 파일이면 `parallel-delegation`으로 병렬.

에이전트는 대화 맥락이 없으므로 self-contained 프롬프트에 매번 다음을 적습니다:

- **목표**: 구현할 기능 한 줄 요약
- **관련 파일**: 수정/생성할 경로, 참고할 타입·스토어
- **제약**: 성능 목표, **UI 라이브러리(Fluent UI v9 / shadcn/ui)**, 상태관리(Zustand), PRD 범위
- **산출물**: 어떤 파일이 어떤 export를 가져야 하는지

구현 에이전트가 보장하는 것: React 19 패턴(no forwardRef/React.FC, Compiler 위임), TS strict(no `any`), Zustand selector, 선택된 UI 라이브러리 컨벤션(Fluent=토큰/Griffel, shadcn=Tailwind 토큰 클래스/`cn()`), (캔버스 시) Konva 레이어 분리. 자세한 규칙은 에이전트 정의와 `references/ui-*.md`에 있습니다.

## 단계 4: 동작 확인

구현 직후 컴파일·타입·렌더가 깨지지 않는지 가볍게 확인합니다:

```bash
npm run dev      # 또는 프로젝트 dev 스크립트 — HMR로 렌더 확인
npx tsc --noEmit # 타입 에러 빠른 확인 (스크립트가 있으면 그것 사용)
```

여기서 잡히는 건 명백한 컴파일/타입 오류뿐입니다. 동작·회귀·성능은 단계 5에서 QA가 봅니다.

## 단계 5: 검증 (QA 에이전트에 위임)

검증 대상에 따라 QA 에이전트를 고릅니다:
- **테스트 전략·Zustand·성능·전반 코드 리뷰** → `react-vite-qa-expert`
- **UI 컴포넌트 심화 테스트**(provider 래퍼, jsdom 폴리필, portal/a11y) → 라이브러리의 QA specialist (`react-vite-fluent-ui-qa-expert` 또는 `react-vite-shadcn-ui-qa-expert`)

self-contained 프롬프트에 다음을 담습니다:

- **검증 대상**: 방금 구현된 파일/기능
- **품질 기준**: PRD의 커버리지·성능 수치(없으면 에이전트 기본값)
- **요청 범위**: 단위 테스트 / 컴포넌트 테스트 / E2E / a11y / 성능 / 코드 리뷰 중 무엇을

QA 에이전트가 산출하는 것: AAA 패턴 Vitest 테스트, 사용자 관점 RTL 테스트(role 쿼리), (UI 라이브러리 시) provider 래퍼·jsdom 폴리필·portal/axe-core a11y, (캔버스/E2E 시) Playwright, 성능 측정값, Critical/Major/Minor/Cosmetic 분류된 리뷰.

## 단계 6: 회귀 수정

QA가 Major 이상 이슈를 보고하면, 그 패치를 **해당 구현 에이전트**(골격이면 program-expert, UI 레이어면 UI specialist)에게 다시 위임합니다(QA는 프로덕션 코드를 직접 고치지 않습니다). 수정 후 단계 5를 다시 돌려 회귀가 닫혔는지 확인합니다. 이슈가 모두 닫히고 테스트가 통과할 때까지 5↔6을 반복합니다.

---

## 신규 프로젝트 스캐폴딩

설정 파일이 없는 신규 프로젝트면 다음을 제안합니다:

공통 베이스:

```bash
npm create vite@latest <app> -- --template react-ts
cd <app>
npm i zustand immer
npm i -D vitest @testing-library/react @testing-library/jest-dom \
        @testing-library/user-event @vitest/coverage-v8 happy-dom @playwright/test
# 캔버스 에디터가 필요하면: npm i react-konva konva
# 복잡한 드래그앤드롭이 필요하면: npm i @dnd-kit/core
```

UI 라이브러리는 단계 1에서 결정한 쪽 하나만 추가합니다:

```bash
# A) Fluent UI v9
npm i @fluentui/react-components

# B) shadcn/ui — CLI가 Tailwind/components.json/lib·utils를 구성 (npm 컴포넌트 설치 아님)
npx shadcn@latest init
#   이후 필요한 컴포넌트만: npx shadcn@latest add button dialog input ...
```

이후 `vite.config.ts`에 React Compiler 플러그인 + Vitest test 블록을, `src/test/setup.ts`에 브라우저 API 모킹을 추가합니다(구체 설정은 에이전트 정의와 `references/ui-*.md` 참조). 기본 폴더 구조:

```
src/
├── components/   layout / 도메인별 컴포넌트
├── store/        Zustand 스토어
├── types/        TypeScript 타입
├── lib/          IO·외부 연동
├── utils/        순수 유틸
└── test/         setup.ts, 테스트 헬퍼
```

## 출력 스타일

- 한국어로 짧게, 코드 우선.
- 라이브러리 API를 추측하지 않습니다 — 불확실하면 Context7 MCP(있으면) 또는 공식 문서를 확인합니다.
- 구현·검증 사이마다 무엇을 누구에게 위임했고 결과가 무엇인지 한 줄로 보고합니다.

$ARGUMENTS
