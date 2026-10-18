---
name: t1-design
description: "HTML을 만들 때 T1 회사 디자인 시스템(Kinetic Horizon — 주황 #F58220·호박색 그라데이션, Outfit/Plus Jakarta Sans 글꼴)을 입힌다. 어느 프로젝트든 HTML 페이지·보고서·대시보드·랜딩 페이지·발표형 HTML·사내 문서·Artifact 페이지를 새로 만들거나 고칠 때 자동 적용. 미리 변환해 둔 tokens.css(라이트+다크 CSS 변수)를 그대로 붙여 넣어 모든 HTML이 같은 값을 쓰게 하고, 버튼·카드·배지·입력창·표·알림 같은 기본 부품은 shadcn/ui 기본 스타일(크기·모서리·테두리·포커스 링)에 T1 색을 입힌 components.css 를 쓰고, shadcn 이 설치된 React 프로젝트에서는 shadcn-theme.css 로 테마 변수만 바꾼다. 'HTML 만들어줘', 'HTML 보고서', '웹 페이지', '대시보드 페이지', 'T1 디자인', '회사 디자인 적용', '브랜드 색', 'Kinetic Horizon', '디자인 토큰', 'shadcn 테마', 'shadcn T1', '/t1-design' 등에 적용. 색·글꼴·모서리·그림자는 Artifact 기본 디자인 지침보다 이 스킬이 우선한다."
user-invocable: true
allowed-tools: Read, Bash, Write, Edit
---

# t1-design — HTML에 T1 디자인 입히기

HTML을 만들 때 **색·글꼴·모서리·그림자를 이 스킬의 토큰으로만** 쓴다.
비유하면 페인트 가게의 조색표다. 매번 눈대중으로 색을 섞지 않고, 정해 둔 번호로만 칠한다.

기본 부품의 **모양은 shadcn/ui 기본 스타일**, **색·글꼴은 T1** 이다.
shadcn 의 틀(크기·모서리·테두리·포커스 링)에 T1 페인트를 칠한다고 보면 된다.

| 파일 | 역할 | 언제 읽나 |
|---|---|---|
| `${CLAUDE_SKILL_DIR}/assets/tokens.css` | 토큰을 CSS 변수로 옮긴 것 (라이트+다크, 부품 역할 `--ui-*` 포함) | 일반 HTML — **항상** 통째로 |
| `${CLAUDE_SKILL_DIR}/assets/components.css` | shadcn 기본 부품을 순수 CSS 클래스로 옮긴 것 | 일반 HTML — **항상** tokens.css 바로 뒤에 통째로 |
| `${CLAUDE_SKILL_DIR}/assets/shadcn-theme.css` | shadcn 테마 변수(`:root`/`.dark`)를 T1 색으로 채운 것 | shadcn 이 설치된 React 프로젝트일 때만 |
| `${CLAUDE_SKILL_DIR}/DESIGN.md` | 원본. 위쪽 YAML = 토큰, 아래 = 브랜드 규칙 | 히어로 배너 같은 브랜드 강조 요소를 그릴 때 해당 절만 |
| `${CLAUDE_SKILL_DIR}/assets/t1_logo.jpg`, `t1_logo2.jpg` | 로고 (흰 배경 JPEG). `t1_logo2` 는 "Team Trust Technology" 문구 포함 | 로고가 필요할 때만 |

## 먼저 갈래를 고른다

- 프로젝트에 `components.json` 이 있다(shadcn 설치됨) → **React 갈래**: 아래 "shadcn 프로젝트" 절만 따른다.
- 그 밖의 모든 HTML(단일 파일 보고서·Artifact·정적 페이지) → **일반 HTML 갈래**: 아래 절차를 따른다.

## 절차 (일반 HTML)

1. **토큰·부품 붙이기.** `tokens.css` 와 `components.css` 를 Read 해서 `<style>` 맨 앞에 이 순서로 **한 글자도 바꾸지 않고** 넣는다.
   값을 YAML에서 다시 옮겨 적지 않는다 — 옮길 때마다 값이 조금씩 달라지는 것을 막으려고 미리 변환해 둔 파일이다.
2. **글꼴 연결.** `<head>` 에 tokens.css 첫 주석의 Google Fonts `<link>` 를 넣는다.
3. **색은 변수로만.** `color: var(--on-surface)`, `background: var(--surface)` 처럼 쓴다.
   tokens.css 밖에서 `#f58220` 같은 색 코드를 직접 적지 않는다.
   - 본문 글자 `--on-surface`, 보조 글자 `--on-surface-variant`, 바탕 `--surface`, 카드 `--surface-container-lowest`, 테두리 `--outline-variant`
   - 강조 글자·링크 `--primary` (라이트에선 진한 갈색 `#964900` — 흰 바탕 위 주황 글자는 대비가 부족해서다)
   - 주황 원색이 필요한 면(히어로 배너·강조선)은 `--brand-orange` / `--gradient-brand`
4. **글자 크기는 짝으로.** `font: var(--font-body-md); letter-spacing: var(--tracking-body-md);`
   제목 `--font-headline-*`(Outfit), 본문 `--font-body-*`(Plus Jakarta Sans). 대문자는 `label-sm` 배지에만.
5. **부품은 components.css 클래스로.** 이름은 shadcn 컴포넌트·변형 이름에 `ui-` 접두사를 붙인 것이다. 부품 모양을 새로 지어내지 않는다.
   접두사는 이미 자체 CSS 가 있는 페이지에 붙여도 `.card` 같은 흔한 이름과 겹치지 않게 하려는 것이다.
   - 버튼 `ui-btn` + `ui-btn-secondary`/`ui-btn-outline`/`ui-btn-ghost`/`ui-btn-destructive`/`ui-btn-link`, 크기 `ui-btn-sm`/`ui-btn-lg`/`ui-btn-icon`
   - 카드 `ui-card` > `ui-card-header`(`ui-card-title`, `ui-card-description`) / `ui-card-content` / `ui-card-footer`
   - 배지 `ui-badge` (+`ui-badge-secondary`/`ui-badge-destructive`/`ui-badge-outline`), 알림 `ui-alert` (+`ui-alert-destructive`, `ui-alert-title`, `ui-alert-description`)
   - 입력 `ui-input`/`ui-textarea`/`ui-select`(네이티브 `<select>`)/`ui-label`, 오류 표시는 `aria-invalid="true"`
   - 표 `ui-table`, 구분선 `<hr class="ui-separator">`
   - 체크박스·라디오·진행바는 네이티브 그대로 두고 `<body class="ui-accent">` 를 한 번 붙인다(주황이 안쪽 전체에 상속된다)
   - 목록에 없는 부품(탭·대화상자 등)이 필요하면 같은 규칙으로 만든다: 색은 `--ui-*`, 모서리 `calc(var(--ui-radius) - 2px)`, 테두리 `1px solid var(--ui-border)`, 포커스 링 `0 0 0 3px` 의 `--ui-ring` 50%.
   - DESIGN.md `## Components` 의 그라데이션 버튼 등은 **기본 부품에 쓰지 않는다.** 히어로 배너·강조 수치처럼 브랜드를 드러내는 자리에만 쓴다.
6. **로고.** 한 파일로 끝나는 HTML이면 base64 로 박는다: `base64 -w0 "${CLAUDE_SKILL_DIR}/assets/t1_logo.jpg"` → `<img src="data:image/jpeg;base64,...">`.
   JPEG 흰 배경이 그대로 보이므로 **다크 모드에선 흰 판(`background:#fff; border-radius: var(--radius-default); padding: 8px`) 위에** 올린다.
7. **다크 모드.** tokens.css 가 `prefers-color-scheme` 과 `data-theme` 둘 다 처리한다. `body { background: var(--background); color: var(--on-background); }` 만 잊지 않으면 된다.

## shadcn 프로젝트 (React)

1. `globals.css`(또는 `index.css`)에서 shadcn init 이 만든 `:root {...}` 와 `.dark {...}` 의 **색 변수 값만** `shadcn-theme.css` 의 값으로 바꾼다. `@theme inline` 과 컴포넌트 파일은 건드리지 않는다.
2. 글꼴은 shadcn-theme.css 첫 주석대로 넣는다.
3. 부품은 프로젝트의 shadcn 컴포넌트(`@/components/ui/*`)를 그대로 쓴다. `tokens.css`·`components.css` 는 넣지 않는다 — `--primary` 등 이름이 겹쳐 서로 덮어쓴다.
4. 확인: 개발 서버에서 `<Button>` 이 주황(`#f58220`) 바탕에 갈색 글자로 보이면 적용된 것이다.

## 다른 지침과 부딪힐 때

- **Artifact 디자인 지침**(artifact-design 스킬 등)과 함께 쓰면: 레이아웃·접근성·모바일 폭·외부 스크립트 규칙은 그쪽을 따른다.
  **색·글꼴·모서리·그림자는 이 스킬이 이긴다.** 그쪽이 요구하는 `:root` 토큰·다크 모드 블록은 tokens.css 가 이미 갖췄다.
- 사용자가 다른 디자인을 명시하면 그 요청이 우선이다. 이 스킬은 "따로 말이 없을 때의 기본값"이다.

## 다 만든 뒤 확인

색을 직접 적은 곳이 없는지 기계로 본다. 붙여 넣은 두 CSS 를 빼고 남은 부분에서 색 코드를 찾는다:

```bash
python3 -c "import sys,re;h=open(sys.argv[1]).read();cs=[open(f).read() for f in sys.argv[2:]];print('원문 그대로:',[c in h for c in cs]);[h:=h.replace(c,'') for c in cs];print('직접 적은 색:',re.findall(r'#[0-9a-fA-F]{6}\b',h) or '없음')" out.html "${CLAUDE_SKILL_DIR}/assets/tokens.css" "${CLAUDE_SKILL_DIR}/assets/components.css"
```

- `원문 그대로: [True, True]` 와 `직접 적은 색: 없음` 이면 통과다. 로고 흰 판의 `#fff`(3자리)는 잡히지 않는다 — 의도한 예외다.
- 브라우저에서 열어 OS 다크 모드를 켜면 바탕이 짙은 갈색(`#161311`)으로 바뀌어야 한다.

## 주의

- 다크 팔레트는 **DESIGN.md 에 없다.** 원본의 톤 계열(`primary-fixed-dim` 등)에서 유도한 값이라 공식 값이 아니다. 사용자에게 보고서를 넘길 때 필요하면 그렇게 말한다.
- DESIGN.md 원본은 `~/Repos/T1/esc-chip/docs/design/` 에 있다. 이 플러그인 안의 것은 복사본이다(동기화 방법은 플러그인 `docs/USAGE_GUIDE.md`).
