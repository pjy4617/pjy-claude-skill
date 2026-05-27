---
name: manual-digest
description: "대용량 외부 매뉴얼(PDF/HTML/EPUB/DOCX/CHM/MD)뿐 아니라 소스코드 디렉토리(codebase)까지 한 번만 추출·요약하여 마크다운 다이제스트로 저장하고, 이후 작업에서 매뉴얼/코드맵이 필요할 때마다 원본을 다시 읽지 않고 다이제스트(원본의 ~0.3% 크기)를 1차 참조하는 워크플로. 디테일이 필요할 때만 원본의 특정 페이지/섹션(문서) 또는 파일/심볼(코드)만 핀포인트로 추출. 사용자가 '이 PDF 매뉴얼 등록해줘', 'STM32 RM 다이제스트 만들어줘', '이 레포/소스 코드베이스 다이제스트 만들어줘', '`src/` 디렉토리 인덱싱해줘', '/manual-digest <path 또는 dir>', '매뉴얼 다이제스트', '대용량 PDF 인덱싱', 'manual digest', '매뉴얼 갱신', '등록된 매뉴얼 목록', '매뉴얼 제거' 등을 요청하거나, 큰 PDF/HTML/CHM 매뉴얼 파일 또는 소스코드 디렉토리를 가리키며 등록·요약·인덱싱·갱신·삭제·목록을 명시할 때 자동 적용. 첫 사용 전에는 manual-digest-setup으로 환경을 1회 초기화한다(코드베이스 전용 인제스트는 PDF MCP 없이도 동작)."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, mcp__pdf-reader__read_pdf
---

# 매뉴얼 다이제스트 (Manual Digest)

대용량 외부 매뉴얼 **또는 소스코드 디렉토리**를 **한 번만** 추출·요약하여 마크다운 다이제스트로 만들고, 이후 작업에서는 다이제스트를 1차 참조원으로 삼는 워크플로. 디테일이 필요할 때만 원본의 **특정 페이지/섹션(문서)** 또는 **특정 파일/심볼(코드)** 만 핀포인트로 다시 읽는다.

## 입력 종류 — 문서 vs 코드베이스

`<path>`가 **파일**이면 문서 다이제스트(PDF/HTML/EPUB/DOCX/CHM/MD), **디렉토리**이면 코드베이스 다이제스트(`format: codebase`)로 자동 분기한다. 코드베이스는 "페이지"가 없으므로 단위가 디렉토리·파일·심볼이고, 핀포인트가 `mcp__pdf-reader__read_pdf`가 아닌 `Read`/`Grep`/`Glob`이다. 코드베이스 인제스트 전용 절차·산출물 형식은 `references/codebase-extract.md`를 따른다.

## 왜 이 스킬이 중요한가

매뉴얼을 매번 직접 읽으면 ① 토큰을 매번 소비하고 ② PDF/CHM 추출 자체가 무거우며 ③ 위치를 매번 다시 찾는 낭비가 발생한다. 한 번 다이제스트를 만들면 동일 정보가 ~0.3% 크기로 압축되어, 이후 모든 질문이 빠르게 처리된다 (TwinCAT 168p 매뉴얼 실측: 6.29 MB → 18.6 KB).

## 사용 시기

다음 중 하나라도 해당하면 본 스킬을 적용한다:
- 사용자가 매뉴얼 파일 경로 **또는 소스코드 디렉토리**를 지목하며 "등록", "다이제스트", "요약", "인덱싱", "코드맵"을 요청
- `/manual-digest <path 또는 dir>`, `/manual-digest --update`, `/manual-digest --list`, `/manual-digest --remove` 명령
- "이 매뉴얼 자주 볼 것 같아", "큰 PDF인데 매번 읽기 싫어", "이 레포 구조 빨리 파악하게 코드 다이제스트 만들어줘" 같은 의도 표현
- 같은 매뉴얼/코드베이스를 두 번째 이상 참조 — 다이제스트화 제안

다음은 **본 스킬을 쓰지 않는다**:
- 1회성 짧은 PDF 조회
- 사용자가 명시적으로 "지금만 보고 등록은 안 함"

## 사전 조건

`/manual-digest-setup`으로 환경 초기화가 끝나 있어야 한다. 미초기화면 인제스트 시도 시 다음 중 하나가 발생:
- PDF MCP 미등록 → **문서(PDF) 인제스트만** 에러 + setup 실행 안내. **코드베이스 인제스트는 PDF MCP 불필요** — `Read`/`Grep`/`Glob`만 쓰므로 그대로 진행
- `.claude/manuals/` 부재 → 자동 생성 후 진행 (CLAUDE.md 마커는 별도 안내)

## 산출물 위치

```
<scope_root>/.claude/manuals/
├── INDEX.md                              ← 마스터 카탈로그 (1줄 요약)
├── <manual-id>/
│   ├── digest.md                         ← 전체 개요 + 섹션 요약
│   ├── index.md                          ← 섹션 → 페이지 매핑
│   └── metadata.json                     ← id/source/sha256/scope/...
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
| `/manual-digest --remove <id>` | 다이제스트 + INDEX.md 항목 + CLAUDE.md 카탈로그 갱신 |

## 인제스트 워크플로 (8단계)

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
| PDF | `mcp__pdf-reader__read_pdf` | `references/pdf-extract.md` |
| HTML | Read 직접 | `references/html-extract.md` |
| TXT/MD | Read 직접 | `references/txt-md-extract.md` |
| EPUB | `Expand-Archive` → 내부 XHTML Read | `references/epub-extract.md` |
| DOCX | `Expand-Archive` → `word/document.xml` Read | `references/docx-extract.md` |
| CHM | `hh.exe -decompile` → HTML Read | `references/chm-extract.md` |
| **codebase** | **Read / Grep / Glob (+ `find`/`git`로 규모·스택)** | **`references/codebase-extract.md`** |

코드베이스는 인제스트 시작 시 **추출 목적**(재사용 탐색 / 온보딩 / 리팩토링 / 디버깅)을 1줄로 확정한다 — 이것이 샘플링과 디렉토리 맵 주석 컬럼을 결정한다.

### 4. 구조 파싱 (TOC)
- PDF: 첫 5-10페이지 읽어 Table of Contents 페이지 식별 → 섹션·페이지 매핑 추출
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
extractor: <mcp-pdf-reader|claude-read|expand-archive|hh-decompile>
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
원본 핀포인트 추출 시: `mcp__pdf-reader__read_pdf` (PDF) / Read (그 외).
```

**코드베이스(`format: codebase`)는 본문 섹션 구성이 다르다** — 페이지 기반 §요약 대신 `개요 → 디렉토리 맵 → 데이터 모델 → 핵심 서브시스템 → 아키텍처 규칙 → 함정 → 빌드/게이트 → 테스트 자산 → 사용 가이드(핀포인트 파일:line)`. 프론트매터는 `pages/publication_date` 대신 `loc/files/version(git ref)/extractor: claude-read`. 전체 형식·예시는 `references/codebase-extract.md`.

#### index.md
- 문서: 섹션 트리 → 페이지 매핑 테이블. 모든 § 보존.
- 코드베이스: **심볼/파일 → 위치** 테이블 (카테고리별). 핀포인트는 페이지가 아닌 `파일`(+비자명한 핵심 `:line`).

#### metadata.json
부록 A 스키마 준수. 필수 + 선택 필드(`extractor_package`, `subsection_count`, `sampling_strategy` 등). 코드베이스는 `sha256/pages` 대신 `loc/src_files/test_files/stack/version(git ref)/sampling_strategy/<purpose>_targets` 사용 (`references/codebase-extract.md`).

### 8. 마스터 카탈로그 갱신
- `<scope>/.claude/manuals/INDEX.md`에 1줄 항목 추가
- 같은 scope의 `CLAUDE.md` 마커 블록(§부록 C) 카탈로그 요약 갱신 (`<!-- manual-digest:start -->`...`<!-- manual-digest:end -->`)

## 결정성 (NFR-6)

LLM 요약은 비결정적이지만 다음 보장:
- 동일 sha256(문서) / 동일 git ref(코드베이스) 재인제스트 → "이미 등록됨" 안내, 요약 재실행 안 함
- `--update`는 변경분만 재요약(문서=변경 섹션, 코드베이스=`git diff --stat`로 식별한 변경 디렉토리), 비변경분 보존
- 산출물 형식 (스키마, JSON 키, 헤딩 구조)은 결정적

## 활용 (Claude의 동작 규칙)

사용자가 도메인 매뉴얼이 필요한 질문을 할 때:

1. 두 INDEX.md 모두 확인 (project가 global을 override):
   - `<project>/.claude/manuals/INDEX.md`
   - `~/.claude/manuals/INDEX.md`
2. 관련 매뉴얼이 있으면 `digest.md`를 먼저 읽는다
3. digest로 답할 수 있으면 출처(§/p./scope)를 명시
4. 디테일이 부족하면 `index.md`에서 위치 포인터 → 원본의 해당 부분만 추출
   - PDF: `mcp__pdf-reader__read_pdf` `pages: "82-83,100-102"` (혼합 범위 지원)
   - HTML/EPUB/DOCX/CHM: 추출된 마크다운 또는 원본의 해당 섹션
   - **codebase: `index.md`의 심볼→파일로 `Read`, 위치 모르면 `Grep`(정의/사용처)/`Glob`(파일 패턴) — PDF MCP 불필요**
5. 인덱싱되지 않은 매뉴얼/코드베이스면 사용자에게 `/manual-digest <path 또는 dir>` 등록 제안

## 에지케이스

| 상황 | 동작 |
|------|------|
| 같은 ID 재등록 (동일 sha256) | "이미 등록됨, --update로 갱신" 안내 후 종료 |
| 같은 ID 재등록 (다른 sha256) | 사용자 확인 후 덮어쓰기 |
| 비ASCII 경로 | quote + UTF-8 정규화 |
| PDF MCP 미등록 | 즉시 종료, setup 실행 안내 |
| `.claude/manuals/` 쓰기 권한 부재 | 명시적 에러 + scope 변경 제안 |
| ID 충돌 (project + global) | project가 override; `--scope global` 명시 시 경고 |
| 메타데이터 Title 없음 | 파일명 기반 자동 생성, 사용자 확인 |
| 1000p+ 대형 PDF | 페이지 범위 청크 분할 호출 (예: 1-100, 101-200…) |
| 텍스트 레이어 없는 스캔 PDF | "OCR 필요, V2 이후 지원" 명시 후 종료 |
| 디렉토리 입력 (codebase) | `format: codebase`로 분기, PDF MCP 없이 진행 (`references/codebase-extract.md`) |
| 코드베이스 추출 목적 불명 | 인제스트 시작 시 목적 1줄 확인 (재사용/온보딩/리팩토링/디버깅) |
| git 레포 아닌 디렉토리 | `version`을 디렉토리 mtime/파일목록 기반으로, `--update`는 파일목록 diff 폴백 |
| 거대 모노레포 | 사용자에게 하위 패키지 경로로 좁히도록 제안 (전체 1회 대신 패키지별 다이제스트) |

## 흔한 함정

| 함정 | 해결 |
|------|------|
| 모든 페이지를 추출하려 함 | 핵심 섹션만 샘플링, 절차 페이지는 TOC 제목으로 요약 |
| `pages` 인자 단일 범위만 사용 | `"7-12,28-30,82-83"` 혼합 범위로 한 호출에 묶기 |
| 다이제스트만으로 모호하게 답변 | 출처 명시 + 모호하면 원본 핀포인트 추출 |
| 메타데이터 무시 | `include_metadata: true`로 Author/Title/Subject 자동 확보 |

## 마무리 보고

인제스트 완료 시 사용자에게:
1. 산출물 경로 (digest.md / index.md / metadata.json)
2. 압축비 (원본 vs 다이제스트, 목표 ≤3%)
3. 등록된 scope, 다음 단계 안내 (이후 매뉴얼 질문 시 자동 참조됨)

$ARGUMENTS
