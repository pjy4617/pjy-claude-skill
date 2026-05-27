# UI 라이브러리 가이드 — Fluent UI v9

> 프로젝트가 **Fluent UI v9**를 UI 라이브러리로 선택한 경우 따르는 규칙.
> 선택 감지: `package.json`에 `@fluentui/react-components`가 있으면 Fluent UI 프로젝트.

## 설치

```bash
npm i @fluentui/react-components
# 아이콘이 필요하면:
npm i @fluentui/react-icons
```

## 핵심 패턴

### Provider는 최상위에 한 번만

`FluentProvider`는 앱 루트에 단 한 번만 둡니다. 중첩하면 테마 컨텍스트가 충돌하고 토큰이 어긋납니다.

```tsx
import { FluentProvider, webLightTheme } from '@fluentui/react-components';

function App() {
  return (
    <FluentProvider theme={webLightTheme}>
      <Router />
    </FluentProvider>
  );
}
```

다크모드는 테마 객체를 교체합니다(`webDarkTheme`). 직접 색을 바꾸지 않습니다.

### 스타일링은 Griffel(`makeStyles` + `tokens`)

인라인/하드코딩 색상 대신 토큰을 씁니다 — 토큰을 써야 테마/다크모드가 일관되게 동작하고, 디자인 시스템 변경이 한 곳에서 반영됩니다.

```tsx
import { makeStyles, tokens, Button } from '@fluentui/react-components';

const useStyles = makeStyles({
  panel: {
    backgroundColor: tokens.colorNeutralBackground1,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusMedium,
  },
});

export function Panel() {
  const styles = useStyles();
  return <div className={styles.panel}><Button appearance="primary">저장</Button></div>;
}
```

- 간격·색·반경·타이포는 전부 `tokens.*`에서 가져옵니다.
- Griffel 외 CSS-in-JS(styled-components, emotion 등)를 추가하지 않습니다 — 번들·런타임이 중복됩니다.
- shadcn 식 Tailwind 클래스를 섞지 않습니다(한 프로젝트는 한 스타일링 방식).

### 컴포넌트는 Fluent 것을 우선 사용

`Button`, `Input`, `Dialog`, `Menu`, `Table`, `Tab` 등은 Fluent 컴포넌트를 그대로 사용하고 토큰/슬롯으로 커스터마이즈합니다. 접근성(키보드·ARIA)이 기본 내장돼 있어, 직접 만든 div 버튼보다 안전합니다.

## Vite 청크 분리

Fluent는 큰 라이브러리이므로 별도 청크로 분리해 캐시 효율을 높입니다.

```ts
build: {
  rollupOptions: {
    output: { manualChunks: { fluent: ['@fluentui/react-components'] } },
  },
},
```

## 테스트 시 유의

- `render` 대상이 Fluent 컴포넌트를 쓰면 테스트에서도 `FluentProvider`로 감쌉니다(테마 컨텍스트 없으면 경고/오작동).
- 역할 기반 쿼리(`getByRole('button', { name: '저장' })`)를 우선합니다 — Fluent가 적절한 ARIA를 부여하므로 사용자 관점 검증에 적합합니다.

## QA 체크포인트

- [ ] `FluentProvider`가 루트에 1회만
- [ ] 색·간격이 `tokens.*` 사용 (하드코딩 없음)
- [ ] Griffel 외 CSS-in-JS 없음
- [ ] 테스트가 `FluentProvider`로 감쌈

## 참고

- Fluent UI v9: https://react.fluentui.dev
- Griffel: https://griffel.js.org
