---
name: manual-digest
description: "대용량 외부 매뉴얼(PDF/HTML/EPUB/DOCX/CHM/MD)뿐 아니라 소스코드 디렉토리(codebase)까지 한 번만 추출·요약하여 마크다운 다이제스트로 저장하고, 이후 작업에서 매뉴얼/코드맵이 필요할 때마다 원본을 다시 읽지 않고 다이제스트(원본의 ~0.3% 크기)를 1차 참조하는 워크플로. 디테일이 필요할 때만 원본의 특정 페이지/섹션(문서) 또는 파일/심볼(코드)만 핀포인트로 추출. 사용자가 '이 PDF 매뉴얼 등록해줘', 'STM32 RM 다이제스트 만들어줘', '이 레포/소스 코드베이스 다이제스트 만들어줘', '`src/` 디렉토리 인덱싱해줘', '/manual-digest <path 또는 dir>', '매뉴얼 다이제스트', '대용량 PDF 인덱싱', 'manual digest', '매뉴얼 갱신', '등록된 매뉴얼 목록', '매뉴얼 제거' 등을 요청하거나, 부품 데이터시트를 '전역 등록', '부품 등록', '이 부품 이미 등록됐나', '데이터시트 새 Rev로 갱신', '부품 심볼 풋프린트 3D 위치', '/manual-digest --component' 처럼 요청할 때(부품 모드: 전역 고정·원본 복사·중복/개정판 판정·KiCad 심볼/풋프린트/3D는 복사 없이 위치만 기록), 큰 PDF/HTML/CHM 매뉴얼 파일 또는 소스코드 디렉토리를 가리키며 등록·요약·인덱싱·갱신·삭제·목록을 명시할 때 자동 적용. 다이제스트가 커지면(700줄/50 KB 초과) doc-atomize의 split_md.py로 무손실 분할해 인덱스 1개 + 조각 1~3개만 읽도록 전환한다('다이제스트 분할', '--atomize', '--deatomize'). 첫 사용 전에는 manual-digest-setup으로 환경을 1회 초기화한다(PDF 추출은 동봉 스크립트 assets/pdf_extract.py + PyMuPDF, 코드베이스 인제스트는 그마저도 불필요)."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

# 매뉴얼 다이제스트 (Manual Digest)

대용량 외부 매뉴얼 **또는 소스코드 디렉토리**를 **한 번만** 추출·요약하여 마크다운 다이제스트로 만들고, 이후 작업에서는 다이제스트를 1차 참조원으로 삼는 워크플로. 디테일이 필요할 때만 원본의 **특정 페이지/섹션(문서)** 또는 **특정 파일/심볼(코드)** 만 핀포인트로 다시 읽는다.

## 입력 종류 — 문서 vs 코드베이스

`<path>`가 **파일**이면 문서 다이제스트(PDF/HTML/EPUB/DOCX/CHM/MD), **디렉토리**이면 코드베이스 다이제스트(`format: codebase`)로 자동 분기한다. 코드베이스는 "페이지"가 없으므로 단위가 디렉토리·파일·심볼이고, 핀포인트가 `assets/pdf_extract.py`가 아닌 `Read`/`Grep`/`Glob`이다. 코드베이스 인제스트 전용 절차·산출물 형식은 `references/codebase-extract.md`를 따른다.

## 왜 이 스킬이 중요한가

매뉴얼을 매번 직접 읽으면 ① 토큰을 매번 소비하고 ② PDF/CHM 추출 자체가 무거우며 ③ 위치를 매번 다시 찾는 낭비가 발생한다. 한 번 다이제스트를 만들면 동일 정보가 ~0.3% 크기로 압축되어, 이후 모든 질문이 빠르게 처리된다 (TwinCAT 168p 매뉴얼 실측: 6.29 MB → 18.6 KB).

## 사용 시기

다음 중 하나라도 해당하면 본 스킬을 적용한다:
- 사용자가 매뉴얼 파일 경로 **또는 소스코드 디렉토리**를 지목하며 "등록", "다이제스트", "요약", "인덱싱", "코드맵"을 요청
- `/manual-digest <path 또는 dir>`, `/manual-digest --update`, `/manual-digest --list`, `/manual-digest --remove`, `/manual-digest --component` 명령
- 부품 데이터시트를 "전역으로", "공용으로" 등록하거나, 이미 등록된 부품인지 확인하거나, 새 Rev로 갱신하거나, KiCad 심볼·풋프린트 위치를 묻는 요청
- "이 매뉴얼 자주 볼 것 같아", "큰 PDF인데 매번 읽기 싫어", "이 레포 구조 빨리 파악하게 코드 다이제스트 만들어줘" 같은 의도 표현
- 같은 매뉴얼/코드베이스를 두 번째 이상 참조 — 다이제스트화 제안

다음은 **본 스킬을 쓰지 않는다**:
- 1회성 짧은 PDF 조회
- 사용자가 명시적으로 "지금만 보고 등록은 안 함"

## 사전 조건

`/manual-digest-setup`으로 환경 초기화가 끝나 있어야 한다. 미초기화면 인제스트 시도 시 다음 중 하나가 발생:
- PyMuPDF 미설치 → PDF 인제스트가 `pdf_extract.py` exit 2를 받는다. **인제스트를 중단하지 않는다** — `pip install pymupdf` 안내와 함께 L2(`pdftotext -layout`)로 진행한다. **코드베이스 인제스트는 둘 다 불필요** — `Read`/`Grep`/`Glob`만 쓴다
- `.claude/manuals/` 부재 → 자동 생성 후 진행 (CLAUDE.md 마커는 별도 안내)

## 산출물 위치

```
<scope_root>/.claude/manuals/
├── INDEX.md                              ← 마스터 카탈로그 (1줄 요약)
├── <manual-id>/
│   ├── digest.md                         ← 전체 개요 + 섹션 요약
│   ├── index.md                          ← 섹션 → 페이지 매핑
│   ├── metadata.json                     ← id/source/sha256/scope/...
│   └── digest.atomized/                  ← (다이제스트가 클 때만) 무손실 분할본
│       ├── <id>-digest.index.md          ← 분할 시 조회 진입점
│       └── parts/001-….md …
└── ...
```

- `--scope project` (기본): `<project>/.claude/manuals/`
- `--scope global`: `~/.claude/manuals/`

## 서브커맨드

| 호출 | 동작 |
|------|------|
| `/manual-digest <path 또는 dir> [--scope project\|global] [--depth shallow\|standard\|deep]` | 신규 인제스트 (파일=문서, 디렉토리=코드베이스 자동 분기) |
| `/manual-digest --update <id>` | 문서: sha256 비교 / 코드베이스: git ref 비교 후 변경분만 재요약 |
| `/manual-digest --list [--scope project\|global\|all]` | 등록 매뉴얼 나열 |
| `/manual-digest --remove <id>` | 다이제스트 디렉토리 + INDEX.md 항목 제거 (CLAUDE.md는 건드리지 않음) |
| `/manual-digest --atomize <id> [--max-lines N]` | 이미 등록된 매뉴얼의 `digest.md`(필요시 `index.md`)를 무손실 분할 |
| `/manual-digest --deatomize <id>` | 분할본 제거, `digest.md` 단독 조회로 복귀 |
| `/manual-digest --component <file> [--step <stp>] [--lcsc <코드>]` | **부품 모드** 등록 — 전역 고정, 원본 복사, 중복·개정판 판정, KiCad 파일 위치 기록. `--step`(제조사 STEP) 이나 `--lcsc`(JLCPCB/LCSC 주문 코드) 가 하나라도 있으면 등록 뒤 `--kicad` 를 **자동으로 이어** 심볼·풋프린트·3D 까지 한 명령으로 끝낸다 |
| `/manual-digest --component --check <file...>` | 등록 없이 판정만 (이미 있음 / 개정판 있음 / 새 부품) |
| `/manual-digest --component --update <id> <file>` | 새 Rev 원본으로 갱신 (개정 이력 확인 → 재요약 → `revisions` 기록) |
| `/manual-digest --component --kicad <id> [--step <stp>] [--lcsc <코드>]` | 빠진 심볼·풋프린트·3D를 부품 생성 스킬로 만들고 위치 기록. STEP 경로와 주문 코드를 생성 스킬에 그대로 넘긴다 |
| `/manual-digest --component --list` | 부품마다 Rev와 KiCad 세 파일 상태(있음/없음/위치 끊김) 한 줄 |
| `/manual-digest --component --migrate <프로젝트>` | 프로젝트에 만들어 둔 부품 다이제스트를 재요약 없이 전역으로 이전 (계획, 분류 확인, 실행, 문구 정리, 프로젝트 폴더 삭제 순) |

인제스트 시 `--no-atomize`를 주면 크기와 무관하게 분할 판정을 건너뛴다.

## 부품 모드 (`--component`)

부품 데이터시트·RM·정오표·앱노트처럼 **다른 프로젝트에서도 사실인 자료**를 전역 공용으로 등록한다.
일반 인제스트와 달라지는 점은 다섯 가지다. 나머지(추출·분할·워커 위임)는 아래 9단계를 그대로 쓴다.

1. scope가 항상 `global`이고, 원본을 `~/.claude/manuals/<id>/source.*`로 복사한다 (최신 Rev 1개만)
2. ID는 품번 기본형 소문자(`tps2051c`), 계열·주문 품번은 `aliases`
3. 등록 전에 **전역+프로젝트 전체**를 sha256·ID·별칭으로 판정 → 같은 파일이면 재사용, 같은 부품 다른 파일이면 Rev 비교 후 사용자 선택
4. 다이제스트는 부품 전용 고정 섹션(핀 기능 표는 전수)이고 **프로젝트 문구 금지**
5. KiCad 심볼·풋프린트·3D 모델은 복사하지 않고 `assets/kicad_locate.py`로 **위치만** 기록 + 핀 대조(경고만). 없으면 "없음"으로 두고 등록은 계속한다
6. `--step <stp>` / `--lcsc <코드>` 가 있으면 등록이 끝난 뒤 **`--kicad <id>` 를 묻지 않고 이어 돌린다.** 사용자가 STEP 과 주문 코드를 같이 준 것은
   "심볼·풋프린트·3D 까지 만들어 달라"는 뜻이다. 이미 등록된 같은 파일이면 등록은 건너뛰고 `--kicad` 만 돈다. 넘길 것과 순서는 `references/component-mode.md` 8절 `--kicad` 항목

절차·판정 스니펫·다이제스트 형식·명령 상세는 **`references/component-mode.md`** 를 따른다.
기존 프로젝트 다이제스트 이전은 같은 문서 11절(`assets/migrate_components.py`)이다.
`--component` 없이 "이 데이터시트 등록해줘"라고 하면, 입력이 부품 데이터시트로 보일 때 부품 모드를 제안한다.

## 인제스트 실행 주체 — 워커에게 위임한다

**신규 인제스트(`/manual-digest <path 또는 dir>`)와 `--update`는 메인이 직접 하지 않는다.
`Agent` 도구로 워커 서브에이전트를 하나 띄워 그 안에서 9단계를 전부 수행한다.**

```
Agent(
  subagent_type: "general-purpose",
  model:         "sonnet",              # Claude Sonnet 5 — 추출·요약 작업에 충분하다
  name:          "manual-digest-<id>",   # <id> 의 "." 은 "-" 로 바꾼다 (이름 검사가 거부한다)
  description:   "<id> 매뉴얼 다이제스트 생성",
  prompt:        <아래 필수 항목을 담은 self-contained 프롬프트>
)
```

**왜 위임하는가.** 인제스트는 원본 수백 페이지를 읽는 작업이다. 메인이 직접 하면 그 원문이
메인 컨텍스트에 그대로 쌓이고, 이후 **모든 턴에서 다시 전송된다** — 다이제스트로 토큰을 아끼려던
목적과 정반대가 된다. 워커에 격리하면 원문은 워커 안에서만 소비되고 메인에는 산출물 경로와
요약만 돌아온다. 비유하자면, 창고에서 짐을 다 꺼내 거실에 늘어놓는 대신 창고 안에서 정리하고
목록만 들고 나오는 것이다.

### 워커 프롬프트 필수 항목

워커는 현재 대화 맥락을 **모른다**. 매 호출마다 다음을 전부 적는다.

1. **이 SKILL.md의 절대 경로** — 메인은 스킬을 로드했으므로 경로를 안다. 워커에게
   "먼저 이 파일과 거기 적힌 `references/` 문서를 읽고 그 절차를 따르라"고 지시한다
2. 원본 절대 경로, 감지된 포맷, 결정된 `<manual-id>`
3. `--scope`(project/global)와 산출물 디렉토리 절대 경로
4. `--depth`, `--no-atomize` 등 사용자가 준 옵션
5. 산출물 계약: `digest.md` / `index.md` / `metadata.json` 생성 + `INDEX.md` 항목 추가
6. **PDF 폴백 사다리를 반드시 지킬 것** (L1 `assets/pdf_extract.py` → L2 `pdftotext -layout`
   → L3 `pdf_extract.py render` 후 육안 판독). L1의 exit 2는 PyMuPDF 미설치 신호이지 PDF 문제가
   아니다 — 스캔본으로 오판하지 말 것. `references/pdf-extract.md` 참조
7. 반환 형식: 생성한 파일 경로 목록 + 압축비 + 실제 사용한 `extractor` + 미해결 사항

### 메인의 책임

- 워커 요약을 그대로 사용자에게 옮기지 않는다. **파일이 실제로 생겼는지 확인한다** —
  `digest.md`/`index.md`/`metadata.json` 존재, `INDEX.md` 항목 추가 여부, 프론트매터 필수 필드
- 9단계의 **사용자 확인이 필요한 지점**(ID 확인, 같은 ID 재등록 덮어쓰기, 분할 동의)은
  메인이 처리한다. 워커는 질문할 수 없다 — 위임 전에 미리 확정하거나, 워커가 "확인 필요"로
  보고하고 메인이 사용자에게 묻는다
- 워커가 실패하면 재위임하지 말고 실패 원인을 사용자에게 그대로 보고한다

### 위임하지 않는 것

`--list` / `--remove` / `--atomize` / `--deatomize`는 메인이 직접 처리한다.
부품 모드의 판정·위치 확인·`--check`·`--migrate`도 메인이 한다 (`references/component-mode.md` 10절).
원본을 읽지 않아 컨텍스트 부담이 없고, 위임 오버헤드가 이득보다 크다.

**워커는 이 절을 다시 적용하지 않는다** — 워커 자신이 실행 주체다. 재위임 금지.

## 인제스트 워크플로 (9단계)

### 1. 입력 검증 + 종류 판별
- 절대/상대 경로 정규화 (`[System.IO.Path]::GetFullPath`)
- 존재 + 읽기 권한 확인
- **파일 vs 디렉토리 판별** → 디렉토리면 `format: codebase`로 분기 (이하 코드베이스 단계는 `references/codebase-extract.md`)
- 파일이면 확장자 + 매직 바이트로 포맷 감지 (`.pdf` → `%PDF`, `.docx`/`.epub` → `PK\x03\x04`, `.chm` → `ITSF`)

### 2. ID 결정
- 문서: 파일명 → 소문자 kebab-case (예: `STM32F4-RM0090.pdf` → `stm32f4-rm0090`)
- 코드베이스: 디렉토리명(+필요시 용도 접미사) → kebab-case (예: `Frontend/` → `frontend-authoring-codebase`)
- 메타데이터 Title이 있으면 사용자 확인 후 우선
- 같은 ID 존재 시: 문서는 sha256, 코드베이스는 git ref 비교 → 일치하면 "이미 등록됨, --update 안내" 후 종료

### 3. 텍스트화 추출 (포맷별)
| 포맷 | 도구 | 참조 |
|------|------|------|
| PDF | `assets/pdf_extract.py` (PyMuPDF) → 실패 시 `pdftotext -layout` → 둘 다 실패 시에만 이미지 판독 | `references/pdf-extract.md` |
| HTML | Read 직접 | `references/html-extract.md` |
| TXT/MD | Read 직접 | `references/txt-md-extract.md` |
| EPUB | `Expand-Archive` → 내부 XHTML Read | `references/epub-extract.md` |
| DOCX | `Expand-Archive` → `word/document.xml` Read | `references/docx-extract.md` |
| CHM | `hh.exe -decompile` → HTML Read | `references/chm-extract.md` |
| **codebase** | **Read / Grep / Glob (+ `find`/`git`로 규모·스택)** | **`references/codebase-extract.md`** |

**PDF 추출기는 이 스킬에 동봉되어 있다.** 외부 MCP 서버를 쓰지 않는다.

```bash
S="${CLAUDE_SKILL_DIR}/assets/pdf_extract.py"   # 호출 시 실제 절대 경로로 치환된다
python3 "$S" info   "<abs>"                      # 메타데이터·페이지 수·목차 유무·텍스트 레이어 판정
python3 "$S" toc    "<abs>"                      # 목차 (outline 없으면 글꼴 휴리스틱 자동)
python3 "$S" text   "<abs>" --pages "9,14,16-18" # 필요한 페이지 본문만 (혼합 범위)
python3 "$S" tables "<abs>" --pages "6"          # 표만 마크다운으로
python3 "$S" find   "<abs>" "<검색어>"           # 페이지 열지도 (본문 미포함)
python3 "$S" render "<abs>" --pages "5" --out D  # PNG (L3 육안 판독 전용)
```

종료 코드 2는 **PyMuPDF 미설치** 신호다 (PDF 문제가 아니다) — `pip install pymupdf`를 안내하고
그 자리에서는 L2 `pdftotext -layout`으로 계속한다. 상세는 `references/pdf-extract.md`.

코드베이스는 인제스트 시작 시 **추출 목적**(재사용 탐색 / 온보딩 / 리팩토링 / 디버깅)을 1줄로 확정한다 — 이것이 샘플링과 디렉토리 맵 주석 컬럼을 결정한다.

### 4. 구조 파싱 (TOC)
- PDF: `pdf_extract.py toc`로 목차를 받는다 (내장 outline 우선, 없으면 글꼴 크기 휴리스틱으로 자동 복원). **첫 5-10페이지를 본문으로 읽어 목차 페이지를 찾지 않는다** — 같은 정보를 6배 이상 싸게 받는다
- HTML/EPUB: `h1~h6` + `id` 속성
- DOCX: `<w:pStyle w:val="Heading*"/>`
- CHM: `*.hhc` (목차) / `*.hhk` (인덱스)
- TXT/MD: 헤딩 라인
- **codebase**: 디렉토리 트리(`Glob`/`find -maxdepth 2`) + 진입점·manifest(`package.json` scripts, 빌드설정, 라우터, 프로젝트 CLAUDE.md) → 디렉토리별 역할 + 핵심 심볼(타입/스키마/공개 인터페이스/store) 인덱스

### 5. 섹션 청킹
TOC 기반으로 본문을 섹션 단위 분할. **모든 섹션을 본문 추출하지 않는다** — 핵심 섹션만 샘플링하여 요약 (커버리지 ~20% 목표).

샘플링 우선순위 (문서):
1. 목차 페이지 (구조 파악용)
2. 각 주요 섹션의 도입 페이지
3. 핵심 개념·다이어그램 페이지
4. 절차/대화상자 페이지는 TOC 제목만으로 요약 충분

샘플링 우선순위 (codebase) — **목적 직결 파일만 전수**:
1. 타입/스키마 단일소스, 공유/재사용 후보, 데이터 모델 → 전체 본문 Read
2. 목적 무관 UI/보일러플레이트 → 파일명·역할 1줄 맵핑만
3. 빌드/lint/테스트 설정 → 게이트·규칙만 추출
4. 나머지 → `index.md`에 경로 포인터만 (`node_modules`/`.git`/빌드산출물 제외)

> ★ 우선순위 1 파일은 **디렉토리 맵 추론으로 때우지 말고 반드시 Read** — 실제 수치·시그니처·임계치(예: deque 20단계, `GRID=10`, `fn(type,pos)`)를 본문에 박는다. 정체성(패키지명/버전)은 manifest로 확정(추측 금지). 상세는 `references/codebase-extract.md`.

### 6. 계층 요약 생성 (Claude가 직접 수행)
세 단계로 작성:
- **개요**: 매뉴얼 전체 목적·구성 (2-3문단)
- **섹션 요약**: 주요 §별 핵심 개념·키워드·페이지 포인터
- **키워드 인덱스**: 자주 쓰일 용어 → §/페이지

### 7. 산출물 작성

#### digest.md
```markdown
---
id: <kebab-case-id>
title: <제목>
source: <절대 경로>
format: <pdf|html|epub|docx|chm|md|txt>
scope: <project|global>
pages: <int>
publisher: <author/제조사>
version: <매뉴얼 버전>
publication_date: <ISO 날짜>
language: <BCP47>
sha256: <hex>
indexed_at: <ISO 타임스탬프>
extractor: <pymupdf|pdftotext-layout|page-render|claude-read|expand-archive|hh-decompile>
---

# <제목> — 다이제스트

## 개요
...

## 섹션별 요약

### §<n> <제목> [p.<범위>]
- 핵심 개념 1
- 핵심 개념 2
- 주의사항/제약

## 키워드 인덱스
| 키워드 | 위치 |
|--------|------|
| ... | §x.y, p.NN |

## 사용 가이드
원본 핀포인트 추출 시: `python3 <assets/pdf_extract.py> text <원본> --pages "<범위>"` (PDF, 실패 시 `pdftotext -layout -f <시작> -l <끝>`) / Read (그 외).
```

**코드베이스(`format: codebase`)는 본문 섹션 구성이 다르다** — 페이지 기반 §요약 대신 `개요 → 디렉토리 맵 → 데이터 모델 → 핵심 서브시스템 → 아키텍처 규칙 → 함정 → 빌드/게이트 → 테스트 자산 → 사용 가이드(핀포인트 파일:line)`. 프론트매터는 `pages/publication_date` 대신 `loc/files/version(git ref)/extractor: claude-read`. 전체 형식·예시는 `references/codebase-extract.md`.

#### index.md
- 문서: 섹션 트리 → 페이지 매핑 테이블. 모든 § 보존.
- 코드베이스: **심볼/파일 → 위치** 테이블 (카테고리별). 핀포인트는 페이지가 아닌 `파일`(+비자명한 핵심 `:line`).

#### metadata.json
`references/metadata-schema.md` 스키마 준수. 필수 + 선택 필드(`extractor_package`, `subsection_count`, `sampling_strategy` 등). 코드베이스는 `sha256/pages` 대신 `loc/src_files/test_files/stack/version(git ref)/sampling_strategy/<purpose>_targets` 사용 (`references/codebase-extract.md`).

### 8. 마스터 카탈로그 갱신
- `<scope>/.claude/manuals/INDEX.md`에 1줄 항목 추가 (분할했으면 "분할" 칸 표기)
- **`CLAUDE.md`는 건드리지 않는다.** 마커 블록은 INDEX.md를 보라는 고정 포인터이며 개수도 목록도 담지 않으므로
  갱신할 것이 없다. 세션 중 CLAUDE.md 수정은 프롬프트 캐시를 무효화하므로 이유 없이 쓰지 않는다.
  블록이 손상·구버전이면 `/manual-digest-setup --repair`가 담당한다

### 9. 다이제스트 분할 판정 (크면 쪼갠다)

다이제스트가 커지면 그 자체가 컨텍스트 부담이 된다 — 매뉴얼 질문 한 번마다 통째로 읽히기 때문이다.
`digest.md`(및 `index.md`)의 크기를 재고 임계를 넘으면 `doc-atomize`의 `split_md.py`로 **무손실 분할**한다.
요약을 한 번 더 하지 않는다(정보 손실 누적) — 분할이므로 조각을 합치면 원본과 sha256이 일치한다.

```bash
wc -l "<scope_root>/.claude/manuals/<id>/digest.md"
wc -c "<scope_root>/.claude/manuals/<id>/digest.md"
```

| 크기 | 동작 |
|------|------|
| 300줄 미만 | 분할하지 않는다 (인덱스 유지비 > 이득) |
| 300~699줄 | 분할하지 않는다. 사용자가 `--atomize`를 명시하면 진행 |
| **700줄 이상 또는 50 KB 이상** | 사용자에게 분할을 **제안**하고 동의 시 실행 |
| 1200줄 이상 또는 90 KB 이상 | 강하게 권고 |

절차·명령·검증 게이트·큐레이션·되돌리기는 **`references/digest-atomize.md`**를 따른다. 요점만:

- `python3 <split_md.py> split "<...>/digest.md" --out "<...>/digest.atomized" --doc-id "<id>-digest"`
- `verify`가 `PASS`가 아니면 분할본을 지우고 원상 복구 — 무손실이 깨진 분할은 쓸모가 없다
- `digest.md`는 **지우지 않는다** (`--mode in-place` 금지). verify·update가 원본을 필요로 한다
- 분할본은 `.claude/atomized/`가 아니라 **매뉴얼 디렉토리 안**에 둔다 (카탈로그 이원화·훅 충돌 방지)
- `doc-atomize` 플러그인이 없어 `split_md.py`를 못 찾으면 **인제스트를 실패시키지 않는다** — 분할만 건너뛰고 안내
- 분할 후 **큐레이션이 게이트다**: 조각 요약을 다시 쓰고 `routing_hints`를 채운 뒤 `reindex` → `audit --strict`가 통과해야 metadata 기록·카탈로그 표기로 넘어간다. 조회 비용은 조각 크기가 아니라 **조회당 여는 조각 수**가 정하고, 그 수는 요약·힌트의 질이 정한다
- `audit` BLOCK은 `verify` FAIL과 대응이 다르다 — 분할본을 지우지 않고 큐레이션을 더 해서 통과시킨다

## 결정성 (NFR-6)

LLM 요약은 비결정적이지만 다음 보장:
- 동일 sha256(문서) / 동일 git ref(코드베이스) 재인제스트 → "이미 등록됨" 안내, 요약 재실행 안 함
- `--update`는 변경분만 재요약(문서=변경 섹션, 코드베이스=`git diff --stat`로 식별한 변경 디렉토리), 비변경분 보존
- 분할본이 있는 매뉴얼은 `--update` 마지막에 `split_md.py update <...>/digest.atomized`를 **반드시** 이어서 실행한다 — 건너뛰면 다이제스트와 조각이 어긋난 채 조회된다
- 갱신 후에는 `⚠️`가 붙은 조각 요약을 다시 쓰고 `reindex` → `audit --strict`로 게이트를 다시 통과시킨다. 절이 늘거나 쪼개졌으면 그 조각을 가리키는 라우팅 힌트도 새로 필요하다
- 산출물 형식 (스키마, JSON 키, 헤딩 구조)은 결정적

## 활용 (Claude의 동작 규칙)

사용자가 도메인 매뉴얼이 필요한 질문을 할 때:

1. 두 INDEX.md 모두 확인 (project가 global을 override):
   - `<project>/.claude/manuals/INDEX.md`
   - `~/.claude/manuals/INDEX.md`
2. 관련 매뉴얼이 있으면 `digest.md`를 먼저 읽는다
   - **단, INDEX.md의 "분할" 칸이 채워져 있으면 `digest.md`를 통째로 읽지 않는다.**
     `digest.atomized/<id>-digest.index.md`(라우팅 힌트 → 목차 → 키워드 역색인)를 먼저 읽고
     후보 조각 1~3개만 `parts/`에서 Read한다
3. digest로 답할 수 있으면 출처(§/p./scope)를 명시. 조각을 인용해도 출처는 **원본 기준**(§/p.)으로 쓴다 —
   조각 번호는 다이제스트 내부 위치일 뿐 원본 페이지가 아니다
4. 디테일이 부족하면 `index.md`에서 위치 포인터 → 원본의 해당 부분만 추출
   - PDF: 위치를 모르면 `pdf_extract.py find "<abs>" "<검색어>"`로 **페이지 열지도부터** 받고,
     그다음 `pdf_extract.py text "<abs>" --pages "82-83,100-102"` (혼합 범위 지원).
     표가 핵심이면 `tables --pages`. exit 2(PyMuPDF 미설치)나 빈 텍스트면
     `pdftotext -layout -enc UTF-8 -f 82 -l 83 "<abs>" -`로 재시도
   - HTML/EPUB/DOCX/CHM: 추출된 마크다운 또는 원본의 해당 섹션
   - **codebase: `index.md`의 심볼→파일로 `Read`, 위치 모르면 `Grep`(정의/사용처)/`Glob`(파일 패턴) — PDF 도구 불필요**
5. 인덱싱되지 않은 매뉴얼/코드베이스면 사용자에게 `/manual-digest <path 또는 dir>` 등록 제안

## 에지케이스

| 상황 | 동작 |
|------|------|
| 같은 ID 재등록 (동일 sha256) | "이미 등록됨, --update로 갱신" 안내 후 종료 |
| 같은 ID 재등록 (다른 sha256) | 사용자 확인 후 덮어쓰기 |
| 비ASCII 경로 | quote + UTF-8 정규화 |
| PyMuPDF 미설치 (`pdf_extract.py` exit 2) | 중단하지 않는다 — `pip install pymupdf` 안내 + L2(`pdftotext -layout`)로 인제스트 계속, `extractor: pdftotext-layout` 기록 |
| `.claude/manuals/` 쓰기 권한 부재 | 명시적 에러 + scope 변경 제안 |
| ID 충돌 (project + global) | project가 override; `--scope global` 명시 시 경고 |
| 부품 모드: 같은 파일이 다른 ID로 이미 있음 | 재등록하지 않고 별칭 추가만 제안 |
| 부품 모드: 같은 부품의 다른 Rev | Rev 비교 후 갱신 / 프로젝트에 따로 등록 / 다른 문서로 새 ID / 취소 중 선택 |
| 부품 모드: 원본 복사본 때문에 `--update <id>`가 늘 "변경 없음" | 새 원본 경로를 받는 `--component --update <id> <file>`을 쓴다 |
| 부품 모드: KiCad 사용자 설정 디렉토리 없음 | 위치를 판정하지 않고 `kicad` 칸을 비운 채 등록을 계속한다 |
| 부품 모드: `--step`/`--lcsc` 를 줬는데 부품 생성 스킬이 없음 | 등록은 끝내고, STEP 경로와 주문 코드를 digest.md "KiCad 파일" 표에 적어 둔 채 "생성 도구 없음" 으로 보고한다. 값을 버리지 않는다 |
| 메타데이터 Title 없음 | 파일명 기반 자동 생성, 사용자 확인 |
| 1000p+ 대형 PDF | `toc`/`find`는 그대로 1회 호출(출력이 작다), `text`만 필요한 구간으로 나눠 호출 |
| 추출 도구가 `invalid horizontal advance` 등 에러 반환 (구버전 PDF MCP 잔존 시) | **PDF 손상이 아니라 그 도구의 버그다.** `pdf_extract.py` 또는 `pdftotext -layout`으로 재시도 — 이미지 렌더링으로 넘어가지 않는다 |
| `pdf_extract.py text`가 빈 텍스트 반환 | 스캔본으로 단정하지 않는다 — `info`의 표본 판정 + `pdftotext -layout` 3페이지 이상 표본 검증 후 판정 |
| PDF에 내장 목차(outline)가 없음 | `toc`가 자동으로 글꼴 크기 휴리스틱으로 복원 (본문+2pt & 번호 절 패턴). 결과가 부실하면 `--min-size`로 임계 조정 |
| 텍스트 레이어 없는 스캔 PDF (L1·L2 모두 실패 확인) | "OCR 필요, V2 이후 지원" 명시 후 종료 |
| `pdftotext` 미설치 (주로 Windows) | "판정 불가"로 처리 — poppler 설치 안내, 스캔본으로 기록하지 않는다 |
| 디렉토리 입력 (codebase) | `format: codebase`로 분기, PDF 도구 없이 진행 (`references/codebase-extract.md`) |
| 코드베이스 추출 목적 불명 | 인제스트 시작 시 목적 1줄 확인 (재사용/온보딩/리팩토링/디버깅) |
| git 레포 아닌 디렉토리 | `version`을 디렉토리 mtime/파일목록 기반으로, `--update`는 파일목록 diff 폴백 |
| 거대 모노레포 | 사용자에게 하위 패키지 경로로 좁히도록 제안 (전체 1회 대신 패키지별 다이제스트) |
| 다이제스트가 700줄/50 KB 초과 | 9단계 분할 판정 — 사용자 동의 후 `digest.atomized/` 생성 (`references/digest-atomize.md`) |
| `split_md.py` 못 찾음 (doc-atomize 미설치) | 분할만 건너뛰고 인제스트는 성공 처리, `/plugin` 설치 후 `--atomize <id>` 안내 |
| 분할 verify FAIL | `digest.atomized/` 삭제 후 원상 복구, 원인 보고 (`digest.md`는 무손상) |
| 분할본 있는 매뉴얼 `--update` | 재요약 후 `split_md.py update` 이어서 실행 + `⚠️` 붙은 조각 요약 재작성 → `audit --strict` 재통과 |
| 분할 `audit` BLOCK 잔존 | 분할본은 유지. 요약이 제목 재진술·자동 폴백이거나 라우팅 힌트가 부족한 것 — metadata 수정 후 `reindex` → 재감사 |
| 힌트당 평균 조각 수 > 1.5 | 힌트가 넓게 걸쳐 좁히지 못함 — 질문 단위로 쪼개 조각 1개씩 지시 |

## 흔한 함정

| 함정 | 해결 |
|------|------|
| 모든 페이지를 추출하려 함 | 핵심 섹션만 샘플링, 절차 페이지는 TOC 제목으로 요약 |
| `--pages` 단일 범위만 사용 | `"7-12,28-30,82-83"` 혼합 범위로 한 호출에 묶기 |
| 목차 찾겠다고 앞 페이지를 본문으로 읽음 | `toc` 한 번으로 대체 (WOS 실측: 19,442자 → 약 3 KB) |
| 다이제스트만으로 모호하게 답변 | 출처 명시 + 모호하면 원본 핀포인트 추출 |
| 메타데이터 무시 | `pdf_extract.py info` 1회로 Title/Author/Producer/페이지 수/목차 유무 자동 확보 |
| 큰 다이제스트를 매번 통째로 Read | 700줄 넘으면 분할 — 조회는 인덱스 1 + 조각 1~3개 |
| 다이제스트가 크다고 한 번 더 요약 | 금지. 손실이 누적된다. 분할(무손실)로 해결한다 |

## 마무리 보고

인제스트 완료 시 사용자에게:
1. 산출물 경로 (digest.md / index.md / metadata.json, 분할 시 `digest.atomized/`)
2. 압축비 (원본 vs 다이제스트, 목표 ≤3%)
3. 분할 여부 — 분할했으면 조각 수·무손실 검증 결과·조회 진입점 경로. 분할하지 않았으면 이유(임계 미만 / doc-atomize 미설치)
4. 등록된 scope, 다음 단계 안내 (이후 매뉴얼 질문 시 자동 참조됨)

$ARGUMENTS
