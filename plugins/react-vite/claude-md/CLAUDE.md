## React 19 + Vite 8 프론트엔드 도구 설정

이 프로젝트에는 React 19 + Vite 8 프론트엔드 개발 도구가 설치되어 있습니다.

### 사용 가능한 스킬

- `/react-vite-frontend` — 구현→검증 흐름으로 프론트엔드 기능 개발 (에이전트 조율·라우팅)
- `/react-vite-setup` — 에이전트를 다른 프로젝트에 설치

### 에이전트 (6종 = 범용 2 + UI specialist 4)

| 레이어 | 구현 | 품질검증(QA) |
|--------|------|--------------|
| 범용 (React/Vite/상태/구조·테스트 전략) | `react-vite-program-expert` | `react-vite-qa-expert` |
| Fluent UI v9 (UI 레이어) | `react-vite-fluent-ui-expert` | `react-vite-fluent-ui-qa-expert` |
| shadcn/ui (UI 레이어) | `react-vite-shadcn-ui-expert` | `react-vite-shadcn-ui-qa-expert` |

**라우팅**: React 골격·상태·라우팅·비-UI 로직 → 범용. 테마·컴포넌트 커스터마이즈·SSR 스타일·portal/a11y 테스트 등 UI 라이브러리 심화 → 이 프로젝트가 선택한 라이브러리의 specialist. UI specialist는 선택한 한 라이브러리 쪽만 씁니다(Fluent/shadcn 혼용 금지).

### 워크플로우 (역할 분리)

```
구현 요청
  → react-vite-frontend 스킬 트리거
  → 범용(program-expert) + UI specialist 가 production 코드 작성
  → npm run dev / tsc 로 동작·타입 확인
  → 범용(qa-expert) + UI QA specialist 가 테스트·a11y·성능 검증
  → 지적사항을 다시 해당 구현 에이전트로 반영 (반복)
```

구현과 검증은 **별도 에이전트가 별도 패스**로 수행합니다. 같은 에이전트가 자기 코드를 검증하면 약점을 못 보는 자기검증 함정에 빠지기 때문입니다.

### 기술 스택 (권장)

- React 19 (React Compiler — 수동 메모이제이션 최소화)
- Vite 8 (Node 20.19+ / 22.12+)
- TypeScript strict (`any` 금지, `unknown` + 가드)
- Zustand + Immer (selector 필수, 액션은 동사로)
- (선택) react-konva — 캔버스 에디터, (선택) @dnd-kit — 드래그앤드롭

### UI 라이브러리 (프로젝트당 택1)

<!-- 이 프로젝트가 사용하는 UI 라이브러리를 하나만 남기세요 -->
- **Fluent UI v9 + Griffel** — `FluentProvider` 루트 1회, `makeStyles` + `tokens`(하드코딩 색 금지)
- **shadcn/ui** (Radix + Tailwind) — CLI(`npx shadcn@latest add`)로 `src/components/ui/`에 복사, Tailwind 토큰 클래스 + `cn()`, variant는 `cva`

> 두 라이브러리(Griffel/Tailwind)를 한 프로젝트에 **혼용하지 않습니다**. 상세 규칙은 react-vite 플러그인의 `references/ui-fluent-ui.md` / `references/ui-shadcn-ui.md` 참조.

### 코딩 규칙 핵심

- `forwardRef` / `React.FC` / 불필요한 `useMemo`·`useCallback` 금지 (React 19)
- 컴포넌트: 함수형 + named export, 단일 책임, Props ≤ 7개
- 중복 의존성(상태관리/UI·스타일링) 도입 금지 — 정해진 스택으로 해결
- 변수/함수명 영어 camelCase, 주석은 한국어 OK

### 테스트

- 단위/컴포넌트: Vitest + React Testing Library (happy-dom)
- E2E/시각·성능: Playwright
- 캔버스는 데이터 레벨 검증 우선, 픽셀 비교는 Playwright
- AAA 패턴 + 한국어 description, 사용자 관점(구현 디테일 검증 금지)
- 성능은 측정값으로 (fps, ms, KB)
