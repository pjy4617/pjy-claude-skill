---
name: manual-write
description: "프로그램 소스 코드, CHM 파일, MD 파일(Doxygen 포함)을 분석하여 Sphinx 기반 사용자 매뉴얼을 생성합니다. 기본 테마는 sphinx-rtd-theme입니다. '매뉴얼 만들어', '사용자 가이드 작성', 'Sphinx 문서 생성', '문서화해줘', 'CHM을 Sphinx로', 'MD를 Sphinx로 변환', 'Doxygen에서 Sphinx로', '사용법 문서', 'Getting Started 가이드', '프로그램 설명서', 'API 문서 생성', '웹 매뉴얼 만들어' 등의 요청에 자동 적용. 문서 작성, 매뉴얼, 가이드, Sphinx, reStructuredText, MyST Markdown 관련 요청이면 이 스킬을 사용하세요."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
argument-hint: "[소스 경로 또는 CHM/MD 파일 경로]"
---

# Sphinx 기반 프로그램 매뉴얼 생성

이 스킬은 프로그램 소스 코드, CHM 파일, MD 파일(Doxygen 스타일 포함)을 분석하여 Sphinx 기반의 체계적인 사용자 매뉴얼을 생성합니다.

## 전제 조건

다음 Python 패키지가 필요합니다. 없으면 자동 설치합니다:

```bash
pip install sphinx sphinx-rtd-theme myst-parser sphinx-copybutton
```

CHM 파일 변환이 필요한 경우:
```bash
# Ubuntu/Debian
sudo apt-get install libchm-dev
pip install pychm

# 또는 extract_chmLib 사용
sudo apt-get install libchm-bin
```

## 작업 프로세스

사용자가 문서화를 요청하면, 아래 단계를 순서대로 진행합니다. 각 단계의 결과를 사용자에게 보여주고 승인을 받은 후 다음 단계로 넘어가세요. 사용자가 "검토만 해줘"라고 하면 Phase 1~2까지만 진행하고 멈추세요.

### Phase 1: 소스 분석

1. `$ARGUMENTS`로 전달된 경로를 확인합니다.
   - 경로가 없으면 현재 프로젝트 루트를 대상으로 합니다.
   - CHM 파일이면 Phase 1-A로 분기합니다.
   - MD 파일에 `\page`, `\subpage`, `@ref` 등 Doxygen 명령이 있으면 Phase 1-D로 분기합니다.
   - 일반 MD 파일이면 Phase 1-B로, 소스 코드면 Phase 1-C로 분기합니다.

2. 프로젝트 구조, README, 기존 문서, 설정 파일을 분석합니다.
3. 핵심 기능과 사용자 시나리오를 식별합니다.
4. 대상 OS 환경을 파악합니다 (Windows/Linux/Cross-platform).
5. **다국어 소스 감지**: `kr/`, `en/`, `jp/` 등 언어별 디렉토리가 있는지 확인합니다. 다국어 소스가 발견되면 각 언어별로 독립 Sphinx 프로젝트를 생성합니다. `Common/` 디렉토리가 있으면 이미지 등 공유 리소스로 인식합니다.

#### Phase 1-A: CHM 파일 변환

CHM 파일이 입력된 경우:

```bash
# CHM에서 HTML 추출
mkdir -p /tmp/chm_extract
extract_chmLib "$CHM_FILE" /tmp/chm_extract/
```

추출된 HTML 파일들을 분석하여 문서 구조를 파악합니다:
- 목차(TOC) 파일 (`*.hhc`) 에서 챕터 구조 추출
- 인덱스 파일 (`*.hhk`) 에서 키워드 추출
- HTML 본문에서 내용 추출

#### Phase 1-B: MD 파일 변환

기존 MD 파일이 입력된 경우:
- MD 파일들의 구조와 상호 참조 관계를 분석합니다.
- MyST Markdown을 사용하면 MD 파일을 그대로 Sphinx에서 사용할 수 있으므로, 변환 비용이 최소화됩니다.
- 필요시 MD 문법을 MyST 확장 문법으로 보강합니다 (admonition, cross-reference 등).

#### Phase 1-C: 소스 코드 분석

소스 코드가 대상인 경우:
- 진입점(main), 설정 파일, UI 코드를 우선 분석합니다.
- docstring이 있으면 autodoc으로 API 문서 자동 생성을 계획합니다.
- 사용자가 수행할 주요 작업(use case)을 코드에서 도출합니다.

#### Phase 1-D: Doxygen 스타일 MD 변환

MD 파일에 Doxygen 명령어(`\page`, `\subpage`, `@ref` 등)가 포함된 경우, 기존 Doxygen/CHM 프로젝트를 Sphinx로 마이그레이션하는 시나리오입니다. 먼저 다음을 분석합니다:

1. **구조 분석**: `\page` 정의 수, `\subpage` 참조 관계, `{#anchor}` 앵커 목록을 수집합니다.
2. **다중 페이지 파일 식별**: 단일 MD 파일에 `\page`가 여러 개 정의된 경우를 식별합니다 (파일 분리 대상).
3. **이미지 참조 분석**: `<img src="">`, `![]()`의 경로 패턴과 이미지 실제 위치를 매핑합니다.
4. **코드 블록 문법 확인**: `~~~{.cpp}`, `~~~{.python}` 등 Doxygen 전용 코드 블록을 식별합니다.
5. **릴리즈 노트 구조 확인**: `Release Note`, `Changelog`, `변경 이력` 등의 파일을 식별합니다.

**릴리즈 노트 제목 규칙:**

릴리즈 노트/변경 이력 파일은 **타겟 버전 기준**으로 제목을 작성합니다. "X to Y" 형식이 아니라 "vY" 형식을 사용하세요:
- kr: `# vY 릴리즈 노트` + `> vX에서 변경된 사항`
- en: `# vY Release Notes` + `> Changes from vX`
- jp: `# vY リリースノート` + `> vXからの変更点`

예시:
```
(CHANGELOG_3_6_u3to3_7_0)=
# v3.7 릴리즈 노트

> v3.6u3에서 변경된 사항

## 새로운 기능
...
```

이전 버전 정보는 부제(blockquote)로 남기고, 하위 섹션은 H2(`##`)로 작성합니다.

**Doxygen → MyST 변환 매핑 테이블:**

| Doxygen 문법 | MyST Markdown 변환 |
|---|---|
| `{#ANCHOR_ID}` (제목 뒤) | `(ANCHOR_ID)=` (제목 위 별도 줄) |
| `\page ID Title` | 별도 파일로 분리 + `(ID)=` 타겟 + `# Title` 헤더 |
| `\subpage ID "Title"` | toctree 항목 (목록형이면) 또는 `{ref}\`Title <ID>\`` 인라인 링크 |
| `@ref wmx3Api::Class` | 인라인 코드 `` `wmx3Api::Class` `` (API 문서 없을 때) |
| `@ref ID "Title"` | `{ref}\`Title <ID>\`` |
| `~~~{.cpp}` ... `~~~` | ` ```cpp ` ... ` ``` ` |
| `~~~{.python}` ... `~~~` | ` ```python ` ... ` ``` ` |
| `<div align="center"><img src="X.png" .../>` | `:::{figure} /_static/images/X.png` + `:align: center` |
| `![alt](X.png)` | `![alt](/_static/images/X.png)` (경로 보정) |

**헤더 레벨 정규화 (중요):**

Doxygen `\page`로 분리된 내용은 원본에서 하위 헤더(H2, H3, H4 등)로 작성되어 있는 경우가 많습니다. 별도 파일로 분리할 때 반드시 헤더 레벨을 정규화하세요:
- 분리된 파일의 첫 번째 헤더는 항상 `# (H1)` 이어야 합니다.
- 나머지 헤더도 상대적으로 올려줍니다 (H3→H1이면 H4→H2, H5→H3).
- Sphinx는 각 문서의 첫 헤더가 H1으로 시작하는 것을 기대합니다. H2나 H3으로 시작하면 `myst.header` 경고가 발생합니다.
- 헤더 레벨 점프(H1→H4 등 비연속)도 경고를 유발하므로, 연속적으로 유지하세요.

예시:
```
원본 (single file):           분리 후 (separate file):
## 로봇 설정                  →  # 로봇 설정
### 로봇 타입                 →  ## 로봇 타입
#### 6축 로봇                 →  ### 6축 로봇
```

**index.md와 toctree 생성 규칙 (중요):**

Doxygen의 `mainpage`(보통 `000_main.md`)는 내용이 짧고 `\subpage` 링크만 나열하는 경우가 많습니다. 이를 index.md로 변환할 때:
- 원본의 텍스트 내용은 유지하되, `\subpage` 목록을 반드시 `toctree` 디렉티브로 변환합니다.
- 원본을 그대로 복사하면 toctree가 없어서 모든 문서가 "고아 페이지"가 됩니다.
- 각 하위 디렉토리의 index.md에도 해당 섹션의 toctree를 포함해야 합니다.

index.md 템플릿:
```markdown
(MAINPAGE_ANCHOR)=
# 프로젝트 제목

원본의 소개 텍스트를 여기에 포함합니다.

```{toctree}
:maxdepth: 2
:caption: 목차

section-a/index
section-b/index
...
```
```

**`@ref` → `(ID)=` 타겟 누락 방지:**

`@ref ID` 또는 `{ref}` 링크를 사용하려면, 참조 대상 파일에 `(ID)=` 타겟이 반드시 존재해야 합니다. `\page ID Title`을 분리할 때 `(ID)=` 타겟을 헤더 위에 추가하는 것을 빠뜨리면 `ref.ref` 경고가 발생합니다. 변환 후 모든 `{ref}` 참조에 대응하는 타겟이 있는지 검증하세요:
```bash
# 참조된 라벨 목록
grep -roh '{ref}`[^`]*`' docs/kr/ | grep -oP '<\K[^>]+' | sort -u > /tmp/refs.txt
# 정의된 타겟 목록
grep -roh '^([a-zA-Z_]*)=' docs/kr/ | tr -d '()=' | sort -u > /tmp/targets.txt
# 누락된 타겟
comm -23 /tmp/refs.txt /tmp/targets.txt
```

### Phase 2: 문서 구조 제안

분석 결과를 바탕으로 문서 구조를 사용자에게 제안합니다.

#### 단일 언어 프로젝트

```
docs/
├── conf.py              # Sphinx 설정
├── index.md             # 메인 페이지 + toctree
├── getting-started.md   # 1장: 빠른 시작 (5분 완성 목표)
├── installation.md      # 2장: 설치 가이드
├── usage/               # 3장~: 기능별 상세 가이드
│   ├── basic.md
│   └── advanced.md
├── reference/           # API 레퍼런스 (autodoc 사용 시)
├── troubleshooting.md   # 문제 해결 / FAQ
├── glossary.md          # 용어 사전
└── _static/             # 커스텀 CSS, 이미지 등
```

#### 다국어 프로젝트 (한국어/영어/일본어)

다국어 소스(`kr/`, `en/`, `jp/`)가 감지되면, 각 언어별로 독립 Sphinx 프로젝트를 생성합니다. 이미지 등 공유 리소스는 `_shared/`에 한 번만 저장하고 심볼릭 링크로 연결합니다.

```
docs/
├── _shared/                     # 공유 리소스
│   ├── images/                  # Common/images/ 에서 복사
│   └── templates/
│       └── layout.html          # 언어 전환 네비게이션 템플릿
│
├── kr/                          # 한국어 (기본)
│   ├── conf.py                  # language = 'ko'
│   ├── index.md
│   ├── _static/
│   │   └── images -> ../../_shared/images  # 심볼릭 링크
│   ├── getting-started.md
│   ├── guide/
│   └── ...
│
├── en/                          # 영어
│   ├── conf.py                  # language = 'en'
│   ├── index.md
│   ├── _static/
│   │   └── images -> ../../_shared/images
│   ├── getting-started.md
│   ├── guide/
│   └── ...
│
└── jp/                          # 일본어
    ├── conf.py                  # language = 'ja'
    ├── index.md
    ├── _static/
    │   └── images -> ../../_shared/images
    ├── getting-started.md
    ├── guide/
    └── ...
```

**다국어 구조 원칙:**
- 각 언어는 독립적인 Sphinx 프로젝트로, 개별 빌드가 가능합니다.
- 이미지는 `_shared/images/`에 한 번만 저장하여 중복을 방지합니다.
- 문서 구조(파일명, 디렉토리)는 모든 언어에서 동일하게 유지합니다 — 언어 간 페이지 매핑이 명확해야 합니다.
- 코드 예제는 언어와 무관하므로 모든 버전에서 동일하게 유지합니다.

이 구조를 사용자에게 보여주고, 수정 요청이 있으면 반영합니다.
**사용자의 승인 없이 Phase 3로 진행하지 마세요.**

승인된 구조는 `docs/_structure.md`에 저장합니다. 이 파일은 Phase 3~5에서 변환 기준으로 참조됩니다. 파일명, 디렉토리 구조, 원본↔변환 파일 매핑을 포함하세요. 다국어 프로젝트의 경우 각 언어별 원본↔변환 매핑도 포함합니다. Sphinx 빌드 대상이 아니므로 `_` 접두어를 사용합니다.

### Phase 3: Sphinx 프로젝트 초기화

사용자가 구조를 승인하면 Sphinx 프로젝트를 생성합니다.
**`docs/_structure.md`에 기록된 구조를 그대로 따르세요.** 임의로 파일을 통합하거나 구조를 변경하지 마세요.

```bash
# docs 디렉토리 생성
mkdir -p docs/_static docs/_templates

# conf.py 생성 (sphinx-quickstart 대신 직접 작성 — 더 깔끔함)
```

#### conf.py 기본 설정

```python
# -- 프로젝트 정보 --
project = '{{PROJECT_NAME}}'
copyright = '{{YEAR}}, {{AUTHOR}}'
author = '{{AUTHOR}}'
release = '{{VERSION}}'

# -- 일반 설정 --
extensions = [
    'myst_parser',           # Markdown 지원
    'sphinx.ext.autodoc',    # docstring → API 문서
    'sphinx.ext.viewcode',   # 소스 코드 링크
    'sphinx_copybutton',     # 코드 블록 복사 버튼
]

# -- MyST 설정 --
myst_enable_extensions = [
    'colon_fence',    # ::: 문법으로 admonition
    'deflist',        # 정의 목록
    'tasklist',       # 체크박스 목록
]

# -- HTML 출력 설정 --
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 3,
    'collapse_navigation': False,
    'sticky_navigation': True,
}
html_static_path = ['_static']

# -- 언어 설정 --
language = 'ko'
```

#### 다국어 프로젝트 conf.py

다국어 프로젝트에서는 각 언어별 `conf.py`를 생성합니다. 공통 설정은 동일하고 `language`와 언어 전환 링크 설정이 다릅니다.

| 언어 | `language` | `current_lang` | 작성 문체 |
|------|-----------|---------------|----------|
| 한국어 | `'ko'` | `'kr'` | 경어체 (~합니다, ~하세요) |
| 영어 | `'en'` | `'en'` | Imperative ("Click the button", "Run the command") |
| 일본어 | `'ja'` | `'jp'` | 丁寧語 (~です, ~ます, ~してください) |

각 언어의 conf.py에 언어 전환 네비게이션 설정(`html_context`, `templates_path`)을 추가하고, `docs/_shared/templates/layout.html`에 공유 템플릿을 생성합니다. 이 템플릿은 페이지 상단에 **한국어 | English | 日本語** 언어 전환 링크를 표시합니다.

**상세 설정은 `references/i18n-navigation.md`를 참조하세요** — conf.py 설정값, layout.html 템플릿 코드, 동작 원리가 포함되어 있습니다.

모든 매뉴얼은 한국어, 영어, 일본어 3개 언어로 생성합니다. 단일 언어 프로젝트는 없습니다.

각 언어별 빌드 명령:
```bash
# 전체 빌드
for lang in kr en jp; do
  echo "=== Building $lang ===" && cd docs/$lang && sphinx-build -b html . _build/html -W --keep-going && cd ../..
done
```

#### suppress_warnings 사용 원칙

`suppress_warnings`는 **변환 과정에서 구조적으로 해결 불가능한 경고**에만 최소한으로 사용합니다. 사용 시 반드시 주석으로 이유를 명시하세요.

```python
# 예: Doxygen @ref → 인라인 코드 변환으로 참조 대상이 없는 경우에만 허용
suppress_warnings = [
    'myst.xref_missing',  # @ref → 인라인 코드 변환에 의한 참조 누락
]
```

경고를 억제하는 대신 근본 원인을 해결하는 것이 우선입니다:
- `myst.header` 경고 → 헤더 레벨 수정으로 해결
- `misc.highlighting_failure` → 코드 블록 언어 명시로 해결
- `ref.ref` → 앵커 타겟 추가로 해결

### Phase 4: 문서 내용 작성

각 MD 파일을 작성합니다. 작성 원칙:

#### 초보자 우선 원칙
- Getting Started 챕터만 읽어도 프로그램을 바로 사용할 수 있어야 합니다.
- 모든 작업을 번호가 매겨진 단계로 분해합니다.
- 전문 용어는 첫 등장 시 설명을 병기합니다: "훅킹(Hooking)"

#### 작성 스타일

**공통 원칙** (모든 언어):
- **코드 블록**: 반드시 언어를 명시하세요 (` ```cpp `, ` ```python `, ` ```ini `, ` ```bash ` 등). 언어 없는 ` ``` `는 금지합니다 — Sphinx가 하이라이팅 실패 경고를 발생시킵니다. 설정 파일은 `ini`, 셸 명령은 `bash`, 출력 결과는 `text`를 사용하세요.
- **코드 내용 동일**: 코드 예제는 모든 언어 버전에서 동일해야 합니다. 한 언어에서 코드 블록을 추가/수정하면 다른 언어에도 반영하세요.
- **UI 요소**: **굵은 글씨**로 표시 — 모든 언어에서 동일한 수준으로 적용
- **admonition 적극 활용**: 주의사항에는 `:::{warning}`, 팁에는 `:::{tip}`, 참고에는 `:::{note}`를 사용하세요. "주의:", "참고:", "팁:" 같은 텍스트 대신 admonition 디렉티브를 사용하면 시각적으로 눈에 띄고 일관성이 높아집니다.
- **이미지**: 공유 리소스 경로 사용 (`/_static/images/`)

**언어별 스타일:**

| 항목 | 한국어 (kr) | 영어 (en) | 일본어 (jp) |
|------|------------|----------|------------|
| 문체 | 경어체 (~합니다, ~하세요) | Imperative (Click, Run, Set) | 丁寧語 (~です, ~してください) |
| 용어 병기 | 영문 병기: "훅킹(Hooking)" | 원어 그대로 사용 | 영문 병기: "フッキング(Hooking)" |
| 경로 예시 | `C:\Users\사용자\` | `C:\Users\Username\` | `C:\Users\ユーザー\` |
| admonition | `:::{tip}`, `:::{warning}` | 동일 | 동일 |
| toctree caption | 한국어 (목차, 가이드 등) | 영어 (Contents, Guide 등) | 일본어 (目次, ガイド 등) |

**다국어 작성 시 흔한 실수 방지:**

1. **toctree caption 번역 누락**: 각 언어의 toctree `:caption:` 값은 반드시 해당 언어로 작성하세요. 한국어 원본을 복사한 후 caption을 번역하지 않는 실수가 자주 발생합니다.
2. **본문 번역 누락**: 한국어 원본을 en/jp로 복사한 뒤, 일부 섹션을 번역하지 않고 한국어로 남기는 실수가 발생합니다. 변환 완료 후 각 언어 파일에서 다른 언어 텍스트가 남아있지 않은지 검증하세요.
   ```bash
   # en 파일에서 한국어 잔류 확인
   grep -rn '[가-힣]' docs/en/ --include="*.md" | grep -v '/_static/' | grep -v '_structure'
   # jp 파일에서 한국어 잔류 확인
   grep -rn '[가-힣]' docs/jp/ --include="*.md" | grep -v '/_static/' | grep -v '_structure'
   ```
3. **en 문체 수동태 주의**: 영어 기술 문서는 명령형(Imperative)이 표준입니다. "The file is saved" 대신 "Save the file"로 작성하세요.

```markdown
:::{tip}
팁 내용을 여기에 작성합니다.
:::

:::{warning}
주의사항을 여기에 작성합니다.
:::

:::{note}
참고사항을 여기에 작성합니다.
:::
```

#### 스크린샷 위치 표시
이미지가 필요한 곳에 플레이스홀더를 배치합니다:

```markdown
![메인 화면 스크린샷](/_static/images/main-screen.png)
```

#### Windows 환경 고려
Windows 대상 프로그램의 경우:
- 경로 표기: 백슬래시(`\`) 사용
- 관리자 권한 필요 시 명시
- 트레이 아이콘 등 Windows 고유 UI 설명 포함
- 설치/제거 과정 상세 안내

### Phase 5: 빌드 및 검증

단일 언어:
```bash
cd docs
sphinx-build -b html . _build/html -W --keep-going
```

다국어 프로젝트:
```bash
# 전체 언어 빌드
for lang in kr en jp; do
  echo "=== Building $lang ==="
  cd docs/$lang && sphinx-build -b html . _build/html -W --keep-going && cd ../..
done
```

`-W` 플래그로 경고를 에러로 처리하여 품질을 보장합니다.
`--keep-going`으로 모든 경고/에러를 한 번에 수집합니다.

빌드 결과를 확인하고:
- 에러가 있으면 수정합니다.
- 경고가 있으면 **경고의 근본 원인을 먼저 해결**합니다. suppress_warnings로 숨기는 것은 최후의 수단입니다.
- 다국어 프로젝트는 **모든 언어의 빌드가 성공해야** 합니다.

경고를 유형별로 분류하여 우선순위대로 수정합니다:
```bash
sphinx-build -b html . _build/html --keep-going 2>&1 | grep "WARNING" | sed 's/.*WARNING: //' | sort | uniq -c | sort -rn
```

| 경고 유형 | 원인 | 수정 방법 |
|-----------|------|----------|
| `toc.not_included` | toctree에 포함되지 않은 문서 | index.md의 toctree에 해당 파일 추가 |
| `myst.header` (starts at H3/H4) | \page 분리 시 헤더 레벨 미정규화 | 분리된 파일의 첫 헤더를 H1으로 조정 |
| `myst.header` (non-consecutive) | H1→H4 등 헤더 레벨 점프 | 중간 레벨 보충 또는 레벨 조정 |
| `ref.ref` (undefined label) | `{ref}` 참조에 대응하는 `(ID)=` 타겟 누락 | 대상 파일에 `(ID)=` 타겟 추가 |

### Phase 6: 변환 결과 검증

빌드 성공 후, 변환 품질을 검증합니다:

1. **줄 수 비교**: 원본과 변환 결과의 총 줄 수를 비교합니다. Doxygen 명령어 제거에 의한 자연 감소(5~10%)는 정상이지만, 20% 이상 감소하면 내용 누락을 의심합니다.
   ```bash
   echo "원본:" && find <원본경로> -name "*.md" -exec cat {} + | wc -l
   echo "변환:" && find docs -name "*.md" -exec cat {} + | wc -l
   ```

2. **파일 매핑 검증**: `docs/_structure.md`에 기록된 매핑과 실제 생성 파일을 비교합니다. 누락된 파일이 있으면 보고합니다.

3. **이미지 참조 검증**: 변환된 MD에서 참조하는 이미지가 `_static/images/`에 실제로 존재하는지 확인합니다.
   ```bash
   grep -roh '/_static/images/[^)]*' docs/*.md docs/**/*.md | sort -u | while read img; do
     [ ! -f "docs$img" ] && echo "누락: $img"
   done
   ```

4. **검증 결과 보고**: 줄 수 비교, 파일 매핑, 이미지 참조 결과를 사용자에게 보고합니다.

## 품질 체크리스트

문서 작성 완료 후 반드시 확인:
- [ ] Getting Started만으로 프로그램 즉시 사용 가능한가?
- [ ] 모든 코드 예제가 복사-실행 가능한가?
- [ ] 전문 용어에 설명이 있는가?
- [ ] toctree가 올바르게 구성되었는가?
- [ ] Sphinx 빌드가 에러/경고 없이 완료되는가? (suppress_warnings 최소)
- [ ] 상호 참조 링크가 유효한가?
- [ ] 스크린샷 위치가 표시되어 있는가?
- [ ] 원본 대비 변환 줄 수 감소가 10% 이내인가?
- [ ] `_structure.md` 매핑과 실제 파일이 일치하는가?
- [ ] (다국어) 모든 언어의 Sphinx 빌드가 성공하는가?
- [ ] (다국어) 모든 언어의 파일 구조(파일명, 디렉토리)가 동일한가?
- [ ] (다국어) 코드 예제가 모든 언어 버전에서 동일한가?
- [ ] (다국어) 공유 이미지가 `_shared/images/`에 있고 심볼릭 링크가 유효한가?

## 에이전트 위임

복잡한 프로젝트의 경우 에이전트를 활용합니다. 위임 기준:

- **sphinx-manual-writer**: Sphinx 프로젝트 셋업, conf.py 최적화, 확장 기능 설정, Doxygen→MyST 문법 변환 등 **Sphinx 시스템 레벨** 작업
- **manual-writer**: 소스 코드 분석 → 문서 구조 설계 → 챕터별 내용 작성 등 **매뉴얼 내용** 작성
- **windows-manual-writer**: Windows 전용 프로그램 매뉴얼 — 설치/제거 가이드, 트레이 아이콘, 관리자 권한, Windows 서비스 등 **Windows 고유 기능** 문서화

판단 기준:
- 대상이 Windows 전용 GUI 프로그램이면 → `windows-manual-writer`
- Sphinx 설정이 복잡하거나 Doxygen 마이그레이션이면 → `sphinx-manual-writer`
- 그 외 일반적인 매뉴얼 작성이면 → `manual-writer`
- 복합 프로젝트면 `sphinx-manual-writer`(Sphinx 셋업) + `manual-writer`(내용 작성) 병행
- 완성된 문서의 품질 검증이면 → `manual-reviewer` (6개 카테고리 100점 만점 리뷰)
