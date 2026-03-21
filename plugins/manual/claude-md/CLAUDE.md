## Sphinx 문서화 프로젝트

이 프로젝트는 Sphinx 기반 문서화 시스템을 사용합니다.

### 문서 빌드

```bash
# 의존성 설치
pip install sphinx sphinx-rtd-theme myst-parser sphinx-copybutton

# HTML 빌드
cd docs && sphinx-build -b html . _build/html

# 미리보기
cd docs/_build/html && python -m http.server 8000
```

### 문서 구조

- `docs/conf.py` — Sphinx 설정
- `docs/index.md` — 메인 페이지 (toctree)
- `docs/*.md` — 각 챕터 (MyST Markdown)
- `docs/_static/` — 이미지, CSS 등 정적 파일

### 문서 작성 규칙

- 언어: 한국어 (코드 예제 제외)
- 문체: 경어체 (~합니다, ~하세요)
- 용어: 첫 등장 시 영문 병기 (예: "훅킹(Hooking)")
- 코드 블록: 언어 명시, 실행 가능한 예제
- admonition: `:::{tip}`, `:::{warning}`, `:::{note}` 사용

### 에이전트

- `sphinx-manual-writer` — Sphinx 설정/확장/테마 전문가
- `manual-writer` — 프로그램 매뉴얼 구조 설계 및 작성
- `windows-manual-writer` — Windows 프로그램 전용 매뉴얼
