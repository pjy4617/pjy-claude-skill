# React-Vite 플러그인 사용 설명서

## 개요

React-Vite 플러그인은 **React 19 + Vite 8 + TypeScript** 프론트엔드를 **구현 → 검증**의 역할 분리 흐름으로 개발하는 풀스택 도구입니다. 구현과 품질검증을 별도 에이전트의 별도 패스로 운용해, 한 에이전트가 자기 코드를 검증할 때 생기는 **자기검증 함정**을 구조적으로 차단합니다.

에이전트는 **6종**입니다 — 범용 2종(React/Vite/상태/구조·테스트 전략) + UI 라이브러리별 specialist 4종(Fluent UI·shadcn 각각 구현·QA). 범용이 골격을, specialist가 UI 레이어(테마·컴포넌트·전용 테스트)를 맡습니다.

| 레이어 | 구현 | 품질검증(QA) |
|--------|------|--------------|
| 범용 | `react-vite-program-expert` | `react-vite-qa-expert` |
| Fluent UI v9 | `react-vite-fluent-ui-expert` | `react-vite-fluent-ui-qa-expert` |
| shadcn/ui | `react-vite-shadcn-ui-expert` | `react-vite-shadcn-ui-qa-expert` |

UI specialist는 프로젝트가 선택한 **한 라이브러리 쪽만** 씁니다(Fluent/shadcn 혼용 금지). 각 description에 "상대 라이브러리 사용 금지" 경계가 있어 미선택 라이브러리 에이전트는 트리거되지 않습니다.

### 권장 기술 스택

- **React 19** — React Compiler로 수동 메모이제이션 최소화
- **Vite 8** — Node 20.19+ / 22.12+
- **TypeScript strict** — `any` 금지
- **UI 라이브러리 (택1)** — **Fluent UI v9**(Griffel `makeStyles`+`tokens`) 또는 **shadcn/ui**(Radix+Tailwind, `cn()`+`cva`)
- **Zustand + Immer** — selector 기반 상태관리
- (선택) **react-konva** — 캔버스 에디터
- (선택) **@dnd-kit** — 드래그앤드롭

프로젝트에 이미 다른 스택(MUI, Redux 등)이 있으면 그쪽을 존중합니다.

### UI 라이브러리 선택

UI 라이브러리는 **프로젝트당 하나만** 씁니다(Fluent UI v9와 shadcn/ui를 혼용하면 스타일링·번들이 중복·충돌). 워크플로는 다음 순서로 결정합니다:

1. **감지** — `@fluentui/react-components`가 있으면 Fluent UI, `components.json` + `tailwindcss`가 있으면 shadcn/ui
2. **기록 확인** — `CLAUDE.md`에 선택이 적혀 있으면 그것을 따름
3. **신규 프로젝트** — `"shadcn으로 만들어"` / `"Fluent UI로 만들어"`처럼 지정하거나, 미지정 시 질문

| 구분 | Fluent UI v9 | shadcn/ui |
|------|--------------|-----------|
| 설치 | `npm i @fluentui/react-components` | `npx shadcn@latest init` → `add <component>` |
| 형태 | npm 컴포넌트 패키지 | CLI가 소스를 `src/components/ui/`에 복사(내가 소유) |
| 스타일링 | Griffel `makeStyles` + `tokens` | Tailwind 토큰 클래스 + `cn()` |
| 기반 | Fluent 디자인 | Radix UI + Tailwind |
| 변형 | 컴포넌트 props | `cva` |

각 라이브러리의 상세 규칙은 `skills/react-vite-frontend/references/ui-fluent-ui.md` / `ui-shadcn-ui.md` 참조.

---

## 설치

### 사전 요구사항

- Claude Code CLI
- Node.js 20.19+ 또는 22.12+ (Vite 8 요구사항)

### 플러그인 설치

```
/plugin install react-vite@pjy-skills
```

### 에이전트 설치 (타겟 프로젝트)

React + Vite 프로젝트 디렉토리에서:

```
/react-vite-setup
```

질문에 따라 프로젝트 경로를 입력하면 에이전트 6개와 CLAUDE.md가 자동 설치됩니다.

설치되는 파일:
```
.claude/agents/
├── react-vite-program-expert.md       (범용 구현)
├── react-vite-qa-expert.md            (범용 품질검증)
├── react-vite-fluent-ui-expert.md     (Fluent UI 구현)
├── react-vite-fluent-ui-qa-expert.md  (Fluent UI QA)
├── react-vite-shadcn-ui-expert.md     (shadcn 구현)
└── react-vite-shadcn-ui-qa-expert.md  (shadcn QA)
CLAUDE.md                              (React-Vite 설정 추가)
```
> 프로젝트가 한 UI 라이브러리만 쓰면 반대쪽 specialist 2종은 삭제해도 됩니다.

---

## 사용법

### 기능 개발 (구현 → 검증 전체 흐름)

```
"이 PRD 기반으로 위젯 추가 화면 구현해줘"
"드래그로 카드를 정렬하는 보드 만들고 테스트까지 해줘"
```

`react-vite-frontend` 스킬이 트리거되어:
1. 컨텍스트 파악 (package.json / PRD / 기존 구조 / UI 라이브러리 감지)
2. 구현 위임 → 범용 `react-vite-program-expert` + UI specialist(`*-fluent-ui-expert` / `*-shadcn-ui-expert`)
3. 동작 확인 (`npm run dev` / `tsc --noEmit`)
4. 검증 위임 → 범용 `react-vite-qa-expert` + UI QA specialist (테스트·a11y·성능)
5. 지적사항 반영 → 다시 해당 구현 에이전트 (반복)

### 구현만

```
"Zustand 프로젝트 스토어에 addScreen 액션 추가해줘"   → react-vite-program-expert (범용)
"Fluent 테마/DataGrid 만들어줘"                       → react-vite-fluent-ui-expert
"shadcn으로 Combobox(Command+Popover) 만들어줘"       → react-vite-shadcn-ui-expert
```

### 검증만

```
"Zustand/성능 회귀 검증해줘"                          → react-vite-qa-expert (범용)
"이 Fluent Dialog 테스트 작성해줘 (portal/a11y)"      → react-vite-fluent-ui-qa-expert
"이 Radix Select 테스트가 안 열려, 폴리필 봐줘"        → react-vite-shadcn-ui-qa-expert
```

---

## 자주 만나는 함정

| 증상 | 원인 | 해결 |
|------|------|------|
| 리렌더가 과하다 | Zustand 전체 store 구독 | selector로 필요한 조각만 구독 |
| Compiler 경고 | 수동 `useMemo`/`useCallback` 잔존 | 제거하고 Compiler에 위임 |
| 캔버스 프레임 드랍 | 단일 레이어, 정적까지 리렌더 | 레이어 분리 + `listening={false}` + `cache()` |
| 테스트가 자주 깨진다 | 내부 state 단언 / 상태 격리 누락 | 사용자 관점 검증 + `beforeEach` setState 리셋 |
| 빌드가 크다 | 큰 라이브러리 단일 청크 | `manualChunks`로 분리 |

---

## 관련 플러그인

- `parallel-delegation` — 독립 기능 여러 개를 program-expert로 병렬 구현할 때
- `manual` — 완성된 프론트엔드의 사용자 매뉴얼 생성
