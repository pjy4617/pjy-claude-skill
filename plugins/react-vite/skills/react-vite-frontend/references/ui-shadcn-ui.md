# UI 라이브러리 가이드 — shadcn/ui

> 프로젝트가 **shadcn/ui**를 UI 라이브러리로 선택한 경우 따르는 규칙.
> 선택 감지: 프로젝트 루트에 `components.json`이 있고 `tailwindcss`가 의존성에 있으면 shadcn 프로젝트.

## shadcn/ui는 npm 컴포넌트 라이브러리가 아니다

이 점을 먼저 이해해야 합니다. shadcn/ui는 설치해서 import하는 패키지가 **아니라**, CLI로 **컴포넌트 소스를 내 코드베이스에 복사**해 넣는 방식입니다. 복사된 컴포넌트(`src/components/ui/*`)는 내가 소유하고 직접 수정합니다.

- 기반: **Radix UI** 프리미티브(접근성·동작) + **Tailwind CSS**(스타일링).
- 변형: **class-variance-authority(cva)** 로 variant 정의.
- 클래스 병합: `cn()` 유틸(`clsx` + `tailwind-merge`), 보통 `src/lib/utils.ts`.

## 초기화

```bash
# 프로젝트 초기화 (Tailwind, components.json, lib/utils.ts, CSS 변수 생성)
npx shadcn@latest init
```

CLI가 React 19 / Tailwind v4 환경을 감지해 필요한 peer dependency와 설정을 처리합니다. 프롬프트(스타일, base color 등)를 따릅니다. 패키지명은 `shadcn`입니다(구 `shadcn-ui` 아님).

> 정확한 옵션·최신 절차는 공식 문서로 확인합니다(추측 금지). Context7 MCP가 있으면 우선 사용.

## 컴포넌트 추가

필요한 컴포넌트만 그때그때 추가합니다 — 쓰지 않는 것을 미리 넣지 않습니다.

```bash
npx shadcn@latest add button dialog input dropdown-menu table tabs
```

추가되면 `src/components/ui/button.tsx` 등이 생성됩니다. 사용:

```tsx
import { Button } from '@/components/ui/button';

export function SaveBar() {
  return <Button variant="default" size="sm">저장</Button>;
}
```

## 스타일링은 Tailwind 유틸리티 + `cn()`

```tsx
import { cn } from '@/lib/utils';

interface PanelProps { className?: string; }

export function Panel({ className }: PanelProps) {
  return (
    <div className={cn('rounded-md bg-background p-4 text-foreground', className)}>
      ...
    </div>
  );
}
```

- 색·간격은 **하드코딩 hex 대신 디자인 토큰 색**(`bg-background`, `text-foreground`, `border-border` 등)을 씁니다. 이 토큰들은 CSS 변수로 정의돼 다크모드와 테마가 일관되게 동작합니다.
- `cn()`으로 조건부/외부 className을 병합합니다 — 문자열 직접 결합은 Tailwind 충돌 클래스 문제를 일으킵니다.
- variant가 필요하면 `cva`로 정의합니다(shadcn 컴포넌트 패턴 그대로).
- Griffel/`makeStyles` 같은 CSS-in-JS를 섞지 않습니다(한 프로젝트는 한 스타일링 방식).

## 테마 / 다크모드

테마는 `globals.css`(또는 `index.css`)의 **CSS 변수**로 정의되고, 다크모드는 `.dark` 클래스 토글로 동작합니다. Tailwind v4는 CSS-first 설정(`@import "tailwindcss"` + `@theme`)을 사용합니다. 색을 직접 바꾸지 말고 변수/토큰을 수정합니다.

## 접근성

대부분의 동작·ARIA는 기반 Radix 프리미티브가 제공합니다. 단, **shadcn 컴포넌트는 내 코드라서 내가 수정하면 접근성이 깨질 수 있습니다** — Radix 슬롯/props를 임의로 제거하지 않습니다.

## Vite 청크 분리

shadcn는 단일 거대 컴포넌트 패키지가 아니라 Radix 프리미티브 묶음입니다. 필요 시 vendor 청크로 묶습니다(과도한 수동 청킹은 지양).

## 테스트 시 유의

- Provider 래핑이 강제되지 않습니다(테마는 CSS 변수). 다크모드 동작을 검증하려면 `.dark` 클래스가 적용된 컨테이너에서 렌더합니다.
- 역할 기반 쿼리(`getByRole`)를 우선합니다 — Radix가 적절한 ARIA를 부여합니다.
- `cn()` 병합 결과(클래스 문자열) 자체를 단언하지 말고, 사용자가 보는 상태(보임/disabled/selected)를 검증합니다.

## QA 체크포인트

- [ ] 컴포넌트가 `src/components/ui/`에 있고 import alias(`@/components/ui/...`) 사용
- [ ] 색·간격이 토큰 클래스(`bg-background` 등) 사용 (하드코딩 hex 없음)
- [ ] className 병합에 `cn()` 사용
- [ ] CSS-in-JS(Griffel 등) 혼용 없음
- [ ] Radix 접근성 슬롯/props 임의 제거 없음

## 참고

- shadcn/ui: https://ui.shadcn.com
- Radix UI: https://www.radix-ui.com
- Tailwind CSS: https://tailwindcss.com
