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
3. 버튼·카드 같은 부품을 그릴 때만 `DESIGN.md` 의 Components 절을 읽는다. 매번 원본 전체(10.7 KB)를 읽지 않는다.

왜 tokens.css 를 따로 두나: Claude가 매번 YAML 토큰을 CSS로 옮기면 값이 조금씩 달라질 수 있다. 한 번 변환해 고정해 두면 모든 HTML이 같은 값을 쓴다.

## 확인 방법

1. 다른 프로젝트에서 새 세션을 연다.
2. "간단한 HTML 보고서 하나 만들어줘" 라고 요청한다.
3. 결과 HTML에 `--primary: #964900` 와 `Outfit` 글꼴 링크가 있으면 적용된 것이다.
4. SKILL.md "다 만든 뒤 확인" 절의 한 줄 명령으로 직접 적은 색 코드가 없는지 본다.

## 다크 모드

DESIGN.md 에는 라이트 팔레트만 있다. tokens.css 의 다크 값은 원본 톤 계열(예: `primary-fixed-dim #ffb786` → 다크 `--primary`)에서
Material 3 다크 규칙으로 **유도한 값**이다. 공식 다크 팔레트가 정해지면 tokens.css 의 다크 블록 두 곳
(`@media (prefers-color-scheme: dark)` 안과 `:root[data-theme="dark"]`)을 같은 값으로 교체한다.
`*-fixed` 계열은 Material 3 에서 테마와 무관하게 고정이라 다크 블록에 없다 — 누락이 아니다.

## 원본과 동기화

`skills/t1-design/DESIGN.md` 는 `~/Repos/T1/esc-chip/docs/design/DESIGN.md` 의 **복사본**이다.
플러그인은 git으로 배포되므로 다른 레포를 가리키는 링크를 쓸 수 없다.

원본이 바뀌었는지 확인:

```bash
diff ~/Repos/T1/esc-chip/docs/design/DESIGN.md plugins/t1-design/skills/t1-design/DESIGN.md && echo 동일
```

다르면 원본을 복사하고, 프론트매터의 색이 바뀌었으면 tokens.css 라이트 블록도 같이 고친다.
그다음 아래 검증으로 라이트 값이 원본과 맞는지 본다(PyYAML 필요). 출력이 `불일치: []` 이면 통과다.

```bash
python3 -c "import yaml;d=yaml.safe_load(open('plugins/t1-design/skills/t1-design/DESIGN.md').read().split('---')[1]);c=open('plugins/t1-design/skills/t1-design/assets/tokens.css').read().split('@media')[0];print('불일치:',[k for k,v in d['colors'].items() if f'--{k}: {v};' not in c])"
```

고쳤으면 `plugin.json` 과 `marketplace.json` 의 `version` 을 함께 올린다.

## 다른 지침과의 우선순위

- Artifact 디자인 지침과 겹치면: 레이아웃·접근성·모바일 폭은 그쪽, **색·글꼴·모서리·그림자는 이 스킬**.
- 사용자가 다른 디자인을 명시하면 그 요청이 우선이다.
