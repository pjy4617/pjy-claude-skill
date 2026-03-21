---
name: manual-build
description: "Sphinx 문서 빌드를 실행합니다. HTML, PDF, EPUB 등 다양한 출력 형식을 지원합니다. '문서 빌드', 'make html', 'Sphinx 빌드', '매뉴얼 빌드', 'HTML 생성', '문서 미리보기', 'sphinx-build' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
argument-hint: "[html|pdf|epub] [--clean] [--open]"
---

# Sphinx 문서 빌드

Sphinx 프로젝트를 빌드하여 HTML/PDF/EPUB 출력을 생성합니다.

## 실행 절차

### 1단계: docs 디렉토리 탐색

프로젝트에서 `conf.py`가 있는 Sphinx 문서 디렉토리를 찾습니다:

```bash
find . -name "conf.py" -path "*/docs/*" -o -name "conf.py" -path "*/doc/*" | head -10
```

**다국어 프로젝트 감지**: `docs/kr/conf.py`, `docs/en/conf.py`, `docs/jp/conf.py`처럼 언어별 conf.py가 여러 개 발견되면 다국어 프로젝트로 판단합니다.

`conf.py`를 찾지 못하면 사용자에게 안내합니다:
> Sphinx 프로젝트를 찾을 수 없습니다. `/manual-write`로 먼저 문서를 생성하세요.

### 2단계: 의존성 확인

```bash
pip install sphinx sphinx-rtd-theme myst-parser sphinx-copybutton 2>/dev/null
```

### 3단계: 빌드 형식 결정

`$ARGUMENTS`를 파싱합니다:
- `html` (기본값): HTML 출력
- `pdf`: LaTeX → PDF (아래 의존성 필요)
- `epub`: EPUB 전자책

PDF 빌드 시 추가 의존성:
```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-recommended texlive-fonts-recommended texlive-latex-extra latexmk texlive-lang-cjk

# macOS (MacTeX)
brew install --cask mactex-no-gui
```

`--clean`이 포함되면 빌드 전에 `_build/` 디렉토리를 삭제합니다.

### 4단계: 빌드 실행

#### 단일 언어 프로젝트

```bash
cd docs

# --clean 옵션 시
rm -rf _build/

# HTML 빌드
sphinx-build -b html . _build/html -W --keep-going 2>&1

# PDF 빌드 (latexpdf)
# sphinx-build -b latex . _build/latex && cd _build/latex && make

# EPUB 빌드
# sphinx-build -b epub . _build/epub
```

#### 다국어 프로젝트

`$ARGUMENTS`에 언어 코드(`kr`, `en`, `jp`)가 지정되면 해당 언어만, 없으면 전체 언어를 빌드합니다.

```bash
# 전체 언어 빌드
for lang in kr en jp; do
  echo "=== Building $lang ==="
  cd docs/$lang
  [ "$CLEAN" = "true" ] && rm -rf _build/
  sphinx-build -b html . _build/html -W --keep-going 2>&1
  cd ../..
done

# 특정 언어만 빌드 (예: /manual-build kr)
cd docs/kr && sphinx-build -b html . _build/html -W --keep-going 2>&1
```

### 5단계: 결과 보고

빌드 결과를 요약합니다:

```
Sphinx 빌드 완료!

출력 형식: HTML
출력 경로: docs/_build/html/index.html
경고: 0개
에러: 0개

미리보기: 브라우저에서 열려면 --open 옵션을 사용하세요.
```

에러/경고가 있으면 상세 내용과 수정 방법을 안내합니다.

### 6단계: 미리보기 (선택)

`--open`이 포함되었거나 사용자가 미리보기를 요청하면:

```bash
# 간이 HTTP 서버로 미리보기
cd docs/_build/html
python -m http.server 8000 &
echo "브라우저에서 http://localhost:8000 을 열어주세요"
```
