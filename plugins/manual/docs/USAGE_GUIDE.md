# Sphinx 문서화 플러그인 사용 가이드

> **플러그인 버전**: v1.1.0

## 1. 개요

이 플러그인은 프로그램 소스 코드, CHM 파일, MD 파일(Doxygen 포함), DOCX 파일을 **Sphinx 기반 다국어(한/영/일) 사용자 매뉴얼**로 변환합니다.
**4개 스킬 + 4개 에이전트**로 구성되며, 기본 테마는 `sphinx-rtd-theme`(녹색 `#27ae60` 커스텀)입니다.

```
스킬 4개 (절차서)                    에이전트 4명 (전문가)
──────────────                      ─────────────────
manual-write    문서 생성/변환        sphinx-manual-writer  Sphinx 시스템
manual-build    Sphinx 빌드          manual-writer         매뉴얼 내용 작성
manual-review   품질 리뷰            windows-manual-writer Windows 전용
manual-setup    환경 초기 설정        manual-reviewer       품질 리뷰 전문가
```

## 2. 설치

```bash
# 1. 마켓플레이스 추가 (한 번만)
/plugin marketplace add pjy4617/pjy-claude-skill

# 2. Manual 플러그인 설치 → 4개 스킬 활성화
/plugin install manual@pjy-skills

# 3. 에이전트 + CLAUDE.md 설치 (최초 1회)
/manual-setup
```

Python 의존성 (자동 안내됨):
```bash
pip install sphinx sphinx-rtd-theme myst-parser sphinx-copybutton
```

## 3. 플러그인 구조

```
plugins/manual/
├── skills/
│   ├── manual-write/
│   │   ├── SKILL.md                 # 메인: 6단계 문서 생성 (다국어+Doxygen)
│   │   └── references/
│   │       └── i18n-navigation.md   # 언어 전환 템플릿 (녹색 #27ae60)
│   ├── manual-build/SKILL.md        # Sphinx 빌드 (HTML/PDF/EPUB, 다국어)
│   ├── manual-review/SKILL.md       # 품질 리뷰 + 자동 수정 제안
│   └── manual-setup/SKILL.md        # 에이전트 4명 + CLAUDE.md 설치
├── agents/
│   ├── sphinx-manual-writer.md      # Sphinx 설정/확장/Doxygen 변환
│   ├── manual-writer.md             # 프로그램 매뉴얼 구조 설계
│   ├── windows-manual-writer.md     # Windows 전용 매뉴얼
│   └── manual-reviewer.md           # 6카테고리 100점 리뷰 + --fix
├── claude-md/CLAUDE.md
└── docs/USAGE_GUIDE.md              # 이 파일
```

## 4. 스킬 상세

### manual-write (메인 스킬)

6단계 프로세스로 다국어 문서를 생성합니다:

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
소스 분석   구조 제안   Sphinx 초기화  내용 작성   빌드 검증   변환 검증
            ↑ 승인 대기                                     ↑ 줄 수/이미지 비교
```

| Phase | 내용 | 사용자 개입 |
|-------|------|------------|
| 1 | 소스 분석 (CHM/MD/DOCX/Doxygen/소스코드 자동 분기) + 다국어 감지 | - |
| 2 | 다국어 문서 구조 제안 + `_structure.md` 저장 | **승인 필요** |
| 3 | Sphinx 프로젝트 초기화 (언어별 conf.py, 언어 전환 템플릿) | - |
| 4 | 각 언어/챕터별 MD 파일 작성 | - |
| 5 | 전체 언어 `sphinx-build -W --keep-going` 빌드 검증 | 경고 시 보고 |
| 6 | 줄 수 비교, 파일 매핑, 이미지 참조 검증 | 누락 시 보고 |

**지원 입력 형식:**

| 입력 형식 | Phase 1 분기 | 설명 |
|-----------|-------------|------|
| CHM 파일 | Phase 1-A | `extract_chmLib`로 HTML 추출 후 변환 |
| 일반 MD | Phase 1-B | MyST Markdown으로 직접 사용 |
| 소스 코드 | Phase 1-C | docstring 분석, autodoc 설정 |
| Doxygen MD | Phase 1-D | `\page`, `\subpage`, `@ref` 등 변환 |
| DOCX 파일 | Phase 1-E | pandoc으로 Markdown 변환 후 Sphinx 적용 |

### manual-build

```bash
/manual-build              # 전체 언어 HTML 빌드 (기본)
/manual-build kr           # 한국어만 빌드
/manual-build pdf          # PDF 빌드 (LaTeX 필요)
/manual-build epub         # EPUB 빌드
/manual-build html --clean # 클린 빌드
/manual-build html --open  # 빌드 후 미리보기 서버
```

### manual-review

완성된 매뉴얼의 품질을 6개 카테고리로 종합 리뷰합니다. 자동 수정 가능한 이슈가 발견되면 사용자에게 수정 여부를 질문합니다.

```bash
/manual-review                 # 리뷰 → 이슈 발견 시 "수정할까요?" 질문
/manual-review docs/kr         # 특정 경로 리뷰
/manual-review --fix           # 리뷰 + 질문 없이 바로 자동 수정 (자동화용)
```

**리뷰 카테고리 (100점 만점):**

| 카테고리 | 배점 | 검증 항목 |
|----------|------|----------|
| A. 구조 | 15점 | toctree 완전성, 고아 페이지, 파일 매핑 |
| B. 내용 | 30점 | Getting Started, 용어 병기, FAQ, 스크린샷 |
| C. 코드 | 15점 | 언어 명시, 복사-실행 가능, 들여쓰기 |
| D. 스타일 | 15점 | 문체 일관성, admonition, 헤더 계층 |
| E. 다국어 | 10점 | 파일 구조 동일, 코드 동일, 이미지 링크 |
| F. 빌드 | 15점 | 경고 0, suppress_warnings 최소, 참조 유효 |

점수 기준: 90+ 출시 가능 / 70~89 수정 후 출시 / 70 미만 대폭 수정

**자동 수정 가능 항목:**
- 코드 블록 언어 미명시 → 언어 추론 추가
- toctree caption 미번역 → 해당 언어로 번역
- en/jp 본문 한국어 잔류 → 해당 언어로 번역
- 헤더 레벨 점프 → 순차 조정
- (ID)= 타겟 누락 → 보충

### manual-setup

에이전트 4명과 CLAUDE.md를 현재 프로젝트에 설치합니다.
최초 1회만 실행하면 됩니다.

## 5. 에이전트 역할 분담

### 역할 요약

| 에이전트 | 전문 분야 | 위임 기준 |
|----------|----------|----------|
| `sphinx-manual-writer` | Sphinx 셋업, conf.py, 확장 기능, Doxygen→MyST 변환, DOCX→Sphinx 통합 | Sphinx 시스템 레벨 작업 |
| `manual-writer` | 소스 분석, 문서 구조 설계, 챕터별 내용 작성 | 매뉴얼 내용 작성 |
| `windows-manual-writer` | Windows 설치/제거, 트레이 아이콘, 관리자 권한 | Windows 전용 UI/기능 문서 |
| `manual-reviewer` | 6개 카테고리 품질 검증, 100점 만점 리뷰 + 자동 수정 | 완성된 문서 품질 검증 |

### 역할 경계 (범위)

각 에이전트는 명확한 담당/비담당 범위를 가집니다. 범위를 벗어나는 작업은 해당 에이전트에 위임합니다.

| 에이전트 | 담당 | 담당하지 않음 (위임 대상) |
|----------|------|--------------------------|
| `sphinx-manual-writer` | Sphinx 프로젝트 설정 (conf.py, 확장, 테마), RST/MyST 변환, Doxygen→Sphinx 마이그레이션, DOCX→Sphinx 통합, 빌드 파이프라인 구성 | 챕터별 콘텐츠 기획 및 작성 → `manual-writer` |
| `manual-writer` | 매뉴얼 콘텐츠 기획, 챕터별 내용 작성 (Markdown), 초보자 친화적 문서 구조 설계 | Sphinx conf.py 고급 설정, 테마 커스터마이징, Doxygen 마이그레이션 → `sphinx-manual-writer` |
| `windows-manual-writer` | Windows 7/10/11 환경 특화 설치 가이드, 사용법, 트러블슈팅 | Windows 외 범용 매뉴얼 → `manual-writer`, Sphinx 설정 → `sphinx-manual-writer` |
| `manual-reviewer` | 6개 카테고리 품질 검증, 점수 산출, 자동 수정 (리뷰 전용, 읽기 중심) | 콘텐츠 수정 → `manual-writer`, 빌드/설정 수정 → `sphinx-manual-writer`, Windows 수정 → `windows-manual-writer` |

### 에이전트 간 상호참조

각 에이전트는 자신의 범위를 벗어나는 작업을 적절한 에이전트에 위임합니다.

```
sphinx-manual-writer ←→ manual-writer
    │                        │
    │  콘텐츠 작성 위임 →    │
    │  ← Sphinx 설정 위임    │
    │                        │
    ├── windows-manual-writer ←─ Windows 외 범용 → manual-writer
    │       │
    └── manual-reviewer ←── 수정 필요 시 각 에이전트에 위임
            │
            ├─ 콘텐츠 수정 → manual-writer
            ├─ 설정/빌드 수정 → sphinx-manual-writer
            └─ Windows 수정 → windows-manual-writer
```

### 트리거 키워드

자연어 요청에 따라 적절한 에이전트가 자동 위임됩니다.

| 에이전트 | 트리거 키워드 |
|----------|-------------|
| `manual-writer` | "매뉴얼 작성", "문서 작성", "가이드 생성", "사용법 문서" |
| `windows-manual-writer` | "Windows 매뉴얼", "Windows 설치 가이드", "Windows 사용법" |
| `manual-reviewer` | "문서 리뷰", "매뉴얼 검토", "문서 품질 확인" |

**복합 프로젝트**: `sphinx-manual-writer`(Sphinx 셋업) + `manual-writer`(내용 작성) + `manual-reviewer`(품질 검증) 병행 가능

## 6. 전체 워크플로우

```
[환경 설정]
  /manual-setup → 에이전트 4명 + CLAUDE.md 설치 (manual-reviewer 포함)

[문서 생성]
  "이 프로젝트의 사용자 매뉴얼을 만들어줘"
    → manual-write 스킬 (Phase 1~6)
    → Phase 1: 소스/CHM/MD/DOCX 자동 분기
    → Phase 2에서 구조 제안 → 사용자 승인
    → 3개 언어 Sphinx 프로젝트 + MD 파일 생성 + 빌드
    → 에이전트 위임: sphinx-manual-writer(Sphinx 설정) + manual-writer(내용 작성)

[품질 리뷰]
  /manual-review
    → manual-reviewer 에이전트가 6개 카테고리 100점 만점 검증
    → 자동 수정 가능 이슈 발견 시 "수정할까요?" 질문
    → 승인 시 자동 수정 → 재빌드 → 점수 재산출
    → 수정 필요 시 해당 에이전트에 위임 (콘텐츠→manual-writer, 설정→sphinx-manual-writer)

[빌드만]
  /manual-build
    → 3개 언어 sphinx-build -b html 실행

[미리보기]
  /manual-build html --open
    → http://localhost:8000 에서 확인
```

## 7. 사용 예시

### 기본: 다국어 매뉴얼 생성
```
"이 프로젝트의 사용자 매뉴얼을 만들어줘"
```
→ 소스 분석 → 다국어 감지 → 구조 제안 → 승인 후 kr/en/jp 전체 생성

### Doxygen 프로젝트를 Sphinx로 마이그레이션
```
"kr/pages/ 폴더의 MD 파일들을 Sphinx 문서로 변환해줘"
```
→ Doxygen 문법 자동 감지 → Phase 1-D → \page 분리, \subpage→toctree, @ref→인라인 코드

### 매뉴얼 생성 + 리뷰 + 자동 수정
```
"매뉴얼 작성해주고 리뷰해줘. 문제 있으면 자동으로 고쳐줘"
```
→ manual-write (Phase 1~6) → manual-review (--fix) → 점수 보고

### DOCX 파일을 Sphinx 문서로 변환
```
"manual.docx 파일을 Sphinx 매뉴얼로 변환해줘"
```
→ Phase 1-E: pandoc으로 Markdown 변환 → Sphinx 프로젝트에 통합 → 다국어 문서 생성

### 검토만 요청
```
"매뉴얼 구조만 검토해줘"
```
→ Phase 1~2만 실행, 구조 제안까지만 진행

### PDF 빌드
```
/manual-build pdf
```
→ LaTeX 의존성 확인 → PDF 생성

## 8. 다국어 문서 (한국어/영어/일본어)

모든 매뉴얼은 한국어, 영어, 일본어 3개 언어로 생성합니다.

### 다국어 프로젝트 구조

```
docs/
├── _shared/
│   └── templates/
│       └── layout.html          # 언어 전환 바 (녹색 #27ae60)
├── kr/                          # 한국어 (language='ko')
│   ├── conf.py                  # current_lang='kr'
│   ├── index.md
│   └── _static/images -> ../../_shared/images
├── en/                          # 영어 (language='en')
│   ├── conf.py                  # current_lang='en'
│   └── ...
└── jp/                          # 일본어 (language='ja')
    ├── conf.py                  # current_lang='jp'
    └── ...
```

### 기본 디자인

- **상단 언어 전환 바**: `#27ae60` 녹색, 페이지 상단 고정
- **사이드바 헤더**: 동일 `#27ae60` 녹색 (RTD 기본 파란색 제거)
- **언어 전환**: 한국어 | English | 日本語 — 클릭 시 같은 페이지의 다른 언어로 이동

### 언어별 작성 스타일

| 항목 | 한국어 (kr) | 영어 (en) | 일본어 (jp) |
|------|------------|----------|------------|
| 문체 | 경어체 (~합니다, ~하세요) | Imperative (Click, Run) | 丁寧語 (~です, ~してください) |
| 용어 병기 | 영문 병기: "훅킹(Hooking)" | 원어 그대로 사용 | 영문 병기: "フッキング(Hooking)" |
| toctree caption | 한국어 (목차, 가이드) | 영어 (Contents, Guide) | 일본어 (目次, ガイド) |
| 릴리즈 노트 | v3.7 릴리즈 노트 | v3.7 Release Notes | v3.7 リリースノート |

### 다국어 빌드

```bash
/manual-build        # 전체 언어
/manual-build kr     # 한국어만
/manual-build en     # 영어만
/manual-build jp     # 일본어만
```

### 다국어 원칙
- 파일 구조(파일명, 디렉토리)는 모든 언어에서 동일하게 유지
- 코드 예제는 언어와 무관하므로 모든 버전에서 동일
- 이미지는 `_shared/images/`에 한 번만 저장 → 심볼릭 링크
- 릴리즈 노트는 **타겟 버전 기준** 제목 사용 (v3.7 릴리즈 노트)

## 9. Doxygen → Sphinx 변환 매핑

| Doxygen 문법 | MyST Markdown 변환 |
|---|---|
| `{#ANCHOR_ID}` | `(ANCHOR_ID)=` |
| `\page ID Title` | 별도 파일 + `(ID)=` + `# Title` |
| `\subpage ID "Title"` | toctree 항목 또는 `{ref}` 링크 |
| `@ref Class::Method` | 인라인 코드 `` `Class::Method` `` |
| `~~~{.cpp}` | ` ```cpp ` |
| `<img src="X.png">` | `![](/_static/images/X.png)` |

### 변환 시 주의사항
- **헤더 레벨 정규화**: `\page` 분리 파일의 첫 헤더는 반드시 H1(#)
- **(ID)= 타겟**: 모든 `\page ID Title` 분리 시 파일 첫 줄에 추가
- **코드 블록 언어 명시**: ` ``` ` 금지 → ` ```cpp `, ` ```ini `, ` ```bash ` 등
- **릴리즈 노트**: "변경 이력 (X to Y)" → "vY 릴리즈 노트" 형식

## 10. 제한사항

- Sphinx/Python 환경이 필요 — `pip install sphinx sphinx-rtd-theme myst-parser sphinx-copybutton`
- PDF 빌드는 LaTeX 패키지 별도 설치 필요 (`texlive-latex-recommended` 등)
- CHM 파일 변환은 `libchm-bin` 또는 `pychm` 패키지 필요
- DOCX 파일 변환은 `pandoc` 패키지 필요 (`sudo apt-get install pandoc`)
- Doxygen `@ref`로 참조된 API 심볼은 autodoc 대상이 아니면 인라인 코드로 대체됨
- 이미지 파일은 자동 복사되지만, 스크린샷은 사용자가 직접 추가해야 함

## 11. 변경 이력

### v1.1.0

- **DOCX 입력 지원 추가**: pandoc 기반 Phase 1-E로 DOCX 파일을 Sphinx 문서로 변환 가능
- **에이전트 역할 경계 명확화**: 4개 에이전트에 담당/비담당 범위(범위 섹션) 추가
- **에이전트 간 상호참조 추가**: 각 에이전트가 범위 밖 작업을 적절한 에이전트에 위임하는 구조 명시
- **트리거 키워드 보강**: manual-writer, windows-manual-writer에 자동 위임 트리거 키워드 추가
- **claude-md에 manual-reviewer 등록**: 프로젝트 CLAUDE.md 템플릿에 manual-reviewer 에이전트 포함

### v1.0.0

- 초기 릴리스: 4개 스킬 + 4개 에이전트
- CHM/MD/소스코드/Doxygen 입력 지원
- 다국어(한/영/일) Sphinx 문서 생성
- 6개 카테고리 100점 만점 품질 리뷰
