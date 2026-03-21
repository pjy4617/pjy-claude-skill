# 다국어 언어 전환 네비게이션 설정

## conf.py 언어 전환 설정

각 언어의 conf.py에 다음을 추가합니다:

```python
# -- 언어 전환 네비게이션 --
html_context = {
    'languages': [
        ('kr', '한국어'),
        ('en', 'English'),
        ('jp', '日本語'),
    ],
    'current_lang': 'kr',  # en, jp로 각각 변경
}

# 공유 템플릿 경로 추가
templates_path = ['../_shared/templates']
```

| 언어 | `language` | `current_lang` |
|------|-----------|---------------|
| 한국어 | `'ko'` | `'kr'` |
| 영어 | `'en'` | `'en'` |
| 일본어 | `'ja'` | `'jp'` |

## 기본 layout.html 템플릿

`docs/_shared/templates/layout.html`을 생성합니다. 이 템플릿이 기본(default) 디자인입니다:
- 상단 언어 전환 바: `#27ae60` 녹색
- 사이드바 헤더: 동일 `#27ae60` 녹색 (파란색 제거)
- 언어 전환: JavaScript로 URL의 언어 접두어를 교체

sphinx-rtd-theme에는 `header` 블록이 없으므로 `extrabody` 블록을 사용합니다. Sphinx의 `pathto` 함수는 빌드 시 상대 경로를 생성하므로 언어 접두어 치환에 적합하지 않습니다. 대신 JavaScript로 현재 URL에서 언어 접두어를 치환합니다.

```html
{% extends "!layout.html" %}

{% block extrabody %}
{{ super() }}
<style>
/* 언어 전환 바 (기본: #27ae60 녹색) */
#lang-nav {
  background: #27ae60;
  padding: 0 16px;
  text-align: right;
  font-size: 13px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  height: 28px;
  line-height: 28px;
  margin: 0;
  box-sizing: border-box;
}
#lang-nav strong { color: #fff; margin: 0 8px; }
#lang-nav a { color: #d5f5e3; margin: 0 8px; text-decoration: none; }
#lang-nav a:hover { color: #fff; }

/* RTD 테마 사이드바 배경색을 상단바와 동일하게 통일 — 모든 하위 요소 포함 */
.wy-side-nav-search,
.wy-side-nav-search > a,
.wy-side-nav-search > a:hover,
.wy-side-nav-search > div,
.wy-side-nav-search .wy-dropdown,
.wy-side-nav-search .wy-dropdown > a {
  background: #27ae60 !important;
  background-color: #27ae60 !important;
}
.wy-side-nav-search input[type="text"] { border-color: #1e8e50 !important; }

/* RTD 테마 레이아웃 조정: 언어 바 높이(28px)만큼 아래로 */
.wy-nav-side { top: 28px !important; }
.wy-nav-content-wrap { margin-top: 28px; }
.wy-nav-top { top: 28px !important; }
</style>

<div id="lang-nav">
  {% for lang_code, lang_name in languages %}
    {% if lang_code == current_lang %}
      <strong>{{ lang_name }}</strong>
    {% else %}
      <a href="#" data-lang="{{ lang_code }}"
         onclick="switchLang('{{ lang_code }}', '{{ current_lang }}'); return false;">{{ lang_name }}</a>
    {% endif %}
  {% endfor %}
</div>

<script>
function switchLang(targetLang, currentLang) {
  var url = window.location.href;
  var pattern = new RegExp('/' + currentLang + '/');
  if (pattern.test(url)) {
    window.location.href = url.replace(pattern, '/' + targetLang + '/');
  }
}
</script>
{% endblock %}
```

## 디렉토리 구조

```
docs/
├── _shared/
│   └── templates/
│       └── layout.html          # 이 파일의 HTML을 여기에 생성
├── kr/  (conf.py: current_lang='kr')
├── en/  (conf.py: current_lang='en')
└── jp/  (conf.py: current_lang='jp')
```

## 동작 원리

1. 각 언어의 conf.py가 `html_context`로 언어 목록과 현재 언어를 전달
2. `layout.html` 템플릿이 JavaScript `switchLang()` 함수로 현재 URL에서 언어 접두어를 교체
3. 페이지 상단에 **한국어 | English | 日本語** 형태로 표시
4. 현재 언어는 굵은 글씨, 다른 언어는 클릭 가능한 링크

## 커스터마이징

- **바/사이드바 색상**: `#27ae60`을 회사 브랜드 색상으로 변경 (3개소: `#lang-nav`, `.wy-side-nav-search` 셀렉터들, `border-color`)
