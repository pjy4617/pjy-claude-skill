# t1-design 사용 가이드

**요약.** 이 플러그인을 설치하면 어느 프로젝트에서든 HTML을 만들 때 T1 디자인(Kinetic Horizon)이 입혀진다.
Claude가 미리 변환된 `tokens.css` 를 그대로 붙여 넣고, 색은 변수로만 쓴다.
설정할 것이 없다 — 설치 후 Claude Code를 다시 시작하면 끝이다.

비유하면 회사 공용 서가에 브랜드 가이드를 꽂고 "HTML 만들 땐 이 책부터 펴라"는 표지를 붙인 것이다.

## 설치

```
/plugin install t1-design@pjy-skills
```

사용자 범위(user scope)로 설치하면 모든 프로젝트에서 보인다. 설치 뒤 세션을 새로 열어야 스킬 목록에 잡힌다.

## 어떻게 동작하나

1. "HTML 보고서 만들어줘" 같은 요청이 오면 스킬 설명을 보고 Claude가 `t1-design` 을 불러온다.
2. `assets/tokens.css` 를 `<style>` 맨 앞에 그대로 넣는다. 색·글꼴·모서리·간격·그림자가 전부 CSS 변수(`--primary` 등)로 들어 있다.
3. 버튼·카드 같은 기본 부품은 `assets/components.css` 의 클래스(`ui-btn`, `ui-card`, `ui-badge`, `ui-input`, `ui-table`, `ui-alert` …)로 그린다. 모양은 shadcn/ui 기본 스타일, 색은 T1 이다.
4. DESIGN.md 의 그라데이션 버튼 같은 브랜드 요소는 히어로 배너 등 강조 자리에만 쓴다. 매번 원본 전체(10.7 KB)를 읽지 않는다.

왜 tokens.css 를 따로 두나: Claude가 매번 YAML 토큰을 CSS로 옮기면 값이 조금씩 달라질 수 있다. 한 번 변환해 고정해 두면 모든 HTML이 같은 값을 쓴다.

## 기본 부품 = shadcn/ui 기본 스타일

부품의 틀(크기·모서리·테두리·포커스 링·그림자)은 shadcn/ui 기본(new-york) 스타일을, 색과 글꼴은 T1 을 쓴다.
두 갈래가 있다.

| 상황 | 쓰는 파일 | 방법 |
|---|---|---|
| 일반 HTML (보고서·Artifact·정적 페이지) | `tokens.css` + `components.css` | `<style>` 맨 앞에 이 순서로 붙이고 shadcn 이름에 `ui-` 를 붙인 클래스를 쓴다 (`<button class="ui-btn ui-btn-outline">`) |
| shadcn 이 설치된 React 프로젝트 (`components.json` 있음) | `shadcn-theme.css` | `globals.css` 의 `:root`/`.dark` 색 변수 값만 교체. 컴포넌트는 프로젝트의 shadcn 것을 그대로 쓴다 |

두 갈래를 섞지 않는다. T1 의 `--primary`(진한 갈색 글자색)와 shadcn 의 `--primary`(버튼 바탕)는 이름은 같고 뜻이 달라 서로 덮어쓴다.
그래서 일반 HTML 쪽은 shadcn 역할을 `--ui-primary` 처럼 접두사를 붙여 tokens.css 에 두었다.

클래스도 같은 이유로 `ui-` 접두사를 붙였다. archify 다이어그램 HTML 에 붙여 시험했을 때 접두사 없는 `.card`/`.card-header` 가
archify 의 같은 이름 카드를 덮어 제목이 밀렸다. 접두사를 붙인 뒤에는 원본과 픽셀 단위로 같다.
자체 디자인이 있는 생성기 결과물(archify 등)은 이 CSS 를 붙여도 **바뀌지 않는다** — 그쪽 부품은 그쪽 클래스를 쓰기 때문이다.

주 버튼은 주황 `#f58220` 바탕에 갈색 `#5b2a00` 글자다. 흰 글자는 대비가 2.59 로 기준(4.5)에 못 미쳐서, 원본 토큰의 짝(`primary-container` / `on-primary-container`, 4.56)을 썼다.

## archify 다이어그램에 T1 입히기

**요약.** archify 는 사용자 테마를 받는 입력이 없다. 그래서 archify 가 다 만든 HTML 에 T1 색을 덧칠한 사본을 만든다.
비유하면 공장(archify)은 그대로 두고, 출고된 제품에 T1 포장지를 씌우는 것이다.

```bash
python3 plugins/t1-design/skills/t1-design/assets/apply_archify.py 다이어그램.html   # → 다이어그램.t1.html
```

- 넣는 것: Google Fonts 링크, `archify-t1.css`(archify 기본 프리셋 `classic` 의 색 변수 약 48개를 DESIGN.md 값으로 덮어쓰기, 라이트·다크), 제목 옆 T1 로고.
- 원본은 고치지 않는다. 두 번 돌려도 한 번만 들어간다(`--selftest` 로 확인 가능).
- archify 템플릿(`~/.agents/skills/archify/assets/template.html`)을 직접 고치는 방법은 쓰지 않았다. archify 를 업데이트하면 덮어써지기 때문이다.

주의: T1 을 입힌 사본은 바이트가 원본과 달라 `archify check --require-provenance`(출고 증명 검사 — 결과물이 archify 가 만든 그대로인지 확인)가 실패한다.
일반 `archify check` 는 통과한다. 출고 증명이 필요한 곳에는 원본을 넘긴다.

확인: 원본과 `.t1.html` 을 나란히 열면 원본은 청록·회색, 사본은 크림 바탕에 주황 노드와 T1 로고다.
OS 를 다크 모드로 바꾸면 사본도 짙은 갈색 바탕으로 바뀐다.

## 확인 방법

1. 다른 프로젝트에서 새 세션을 연다.
2. "간단한 HTML 보고서 하나 만들어줘" 라고 요청한다.
3. 결과 HTML에 `--primary: #964900` 와 `Outfit` 글꼴 링크가 있으면 적용된 것이다.
4. 버튼이 주황 바탕·갈색 글자, 모서리 6px, 높이 36px 이면 shadcn 기본 스타일이 적용된 것이다.
5. SKILL.md "다 만든 뒤 확인" 절의 한 줄 명령으로 직접 적은 색 코드가 없는지 본다.

## 다크 모드

DESIGN.md 에는 라이트 팔레트만 있다. tokens.css 의 다크 값은 원본 톤 계열(예: `primary-fixed-dim #ffb786` → 다크 `--primary`)에서
Material 3 다크 규칙으로 **유도한 값**이다. 공식 다크 팔레트가 정해지면 tokens.css 의 다크 블록 두 곳
(`@media (prefers-color-scheme: dark)` 안과 `:root[data-theme="dark"]`)과 shadcn-theme.css 의 `.dark` 를 같은 값으로 교체한다.
`*-fixed` 계열은 Material 3 에서 테마와 무관하게 고정이라 다크 블록에 없다 — 누락이 아니다.

## 원본과 동기화

`skills/t1-design/DESIGN.md` 는 `~/Repos/T1/esc-chip/docs/design/DESIGN.md` 의 **복사본**이다.
플러그인은 git으로 배포되므로 다른 레포를 가리키는 링크를 쓸 수 없다.

원본이 바뀌었는지 확인:

```bash
diff ~/Repos/T1/esc-chip/docs/design/DESIGN.md plugins/t1-design/skills/t1-design/DESIGN.md && echo 동일
```

다르면 원본을 복사하고, 프론트매터의 색이 바뀌었으면 tokens.css 라이트 블록과 shadcn-theme.css `:root` 도 같이 고친다.
그다음 아래 검증으로 라이트 값이 원본과 맞는지 본다(PyYAML 필요). 출력이 `불일치: []` 이면 통과다.

```bash
python3 -c "import yaml;d=yaml.safe_load(open('plugins/t1-design/skills/t1-design/DESIGN.md').read().split('---')[1]);c=open('plugins/t1-design/skills/t1-design/assets/tokens.css').read().split('@media')[0];print('불일치:',[k for k,v in d['colors'].items() if f'--{k}: {v};' not in c])"
```

고쳤으면 `plugin.json` 과 `marketplace.json` 의 `version` 을 함께 올린다.

## 다른 지침과의 우선순위

- Artifact 디자인 지침과 겹치면: 레이아웃·접근성·모바일 폭은 그쪽, **색·글꼴·모서리·그림자는 이 스킬**.
- 사용자가 다른 디자인을 명시하면 그 요청이 우선이다.
