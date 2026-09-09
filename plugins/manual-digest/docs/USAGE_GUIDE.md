# manual-digest 사용 가이드

대용량 매뉴얼을 한 번 추출·요약하여 마크다운 다이제스트로 저장하고, 이후 작업에서는 다이제스트만 참조하는 워크플로.

## 빠른 시작

### 1. 환경 셋업 (1회만)

```
/manual-digest-setup
```

수행 항목:
- PDF 추출용 MCP(`@sylphx/pdf-reader-mcp`) 등록
- `.claude/manuals/` 디렉토리 생성
- `INDEX.md` 헤더 작성
- `CLAUDE.md`에 마커 블록 주입

**MCP 신규 등록한 경우 Claude Code 재시작 필요**.

### 2. 첫 매뉴얼 등록

```
/manual-digest C:\docs\STM32F4-RM0090.pdf
```

- 자동: 추출 → 요약 → `digest.md` / `index.md` / `metadata.json` 작성
- 결과: `<project>/.claude/manuals/stm32f4-rm0090/`

### 3. 활용

이후 매뉴얼 관련 질문 시 Claude가 **자동으로 다이제스트를 1차 참조**한다 (CLAUDE.md 마커 가이드 동작).

```
사용자: SPI1 클럭 분주비 어떻게 설정해?
  → Claude: INDEX.md → digest.md(stm32f4-rm0090) → §RCC.PLL 확인
  → 디테일 부족 시 → index.md에서 페이지 포인터 → 원본 PDF p.220만 핀포인트 추출
  → 답변 + 출처 명시 (§6.2.3, p.220)
```

## 명령어

### 인제스트 (메인 스킬)

```
/manual-digest <path> [--scope project|global] [--depth shallow|standard|deep] [--no-atomize]
```

| 옵션 | 의미 |
|------|------|
| `--scope project` (기본) | `<project>/.claude/manuals/`에 저장 |
| `--scope global` | `~/.claude/manuals/`에 저장 (모든 프로젝트 공유) |
| `--depth shallow` | 압축비 우선 (~5KB 정도) |
| `--depth standard` (기본) | 균형 (~20KB) |
| `--depth deep` | 정확도 우선 (~50KB) |
| `--no-atomize` | 다이제스트가 커도 분할 판정을 건너뜀 |

### 갱신

```
/manual-digest --update <id>
```

변경분만 재요약 (비변경분 보존). 문서는 sha256 비교, 코드베이스는 git ref 비교(`git diff --stat`로 변경 디렉토리 식별).
분할본이 있으면 재요약 후 `split_md.py update`가 이어서 돌아 변경된 조각만 재생성한다.

### 다이제스트 분할 / 해제

```
/manual-digest --atomize <id> [--max-lines N]
/manual-digest --deatomize <id>
```

큰 다이제스트를 무손실로 쪼개 조회 비용을 줄인다 (아래 "큰 다이제스트 분할" 참조).

### 목록

```
/manual-digest --list                    # project + global 통합 (project override)
/manual-digest --list --scope global     # global만
```

### 삭제

```
/manual-digest --remove <id>
```

해당 매뉴얼 디렉토리 + INDEX.md 항목 + CLAUDE.md 카탈로그 갱신.

## 스코프 결정 가이드

| 상황 | 권장 스코프 |
|------|------------|
| 특정 보드 데이터시트 | `project` |
| 프로젝트별 SDK 매뉴얼 | `project` |
| ARM Cortex-M TRM, C99 표준 같은 표준 매뉴얼 | `global` |
| 여러 프로젝트에서 공유하는 라이브러리 매뉴얼 | `global` |

## 지원 포맷

| 포맷 | V1 검증 | 추출 도구 |
|------|--------|-----------|
| PDF | ✓ 검증 (TwinCAT 168p, 0.29% 압축) | `@sylphx/pdf-reader-mcp` MCP → 실패 시 `pdftotext -layout` |
| HTML | 미검증 | Claude Read |
| TXT/MD | 부분 검증 | Claude Read |
| EPUB | 미검증 | PowerShell `Expand-Archive` |
| DOCX | 미검증 | PowerShell `Expand-Archive` |
| CHM | 미검증 (Windows 전용) | `hh.exe -decompile` |
| **codebase (디렉토리)** | ✓ 검증 (HMI Frontend 18,079 LOC → ~14 KB) | Claude `Read`/`Grep`/`Glob` + `find`/`git` (**PDF MCP 불필요**) |

### 코드베이스 다이제스트

`<path>`가 **디렉토리**이면 자동으로 `format: codebase`로 분기한다. 단일 문서가 아니라 레포/패키지를 하나의 "매뉴얼"로 인덱싱한다.

```
/manual-digest /home/me/Repos/MyApp/Frontend
```

- 페이지 대신 **디렉토리 맵 + 심볼→파일 인덱스**, 핀포인트는 `Read`/`Grep`/`Glob`
- 인제스트 시작 시 **추출 목적**(재사용 탐색 / 온보딩 / 리팩토링 / 디버깅)을 1줄로 확인 — 샘플링과 디렉토리 맵 주석 컬럼이 거기서 결정됨
- 목적 직결 핵심 파일만 전수 Read, 나머지는 1줄 맵핑/경로 포인터 (전수 읽기 금지)
- `metadata.json`은 `sha256/pages` 대신 `loc/src_files/test_files/stack/version(git ref)/sampling_strategy`
- `--update`는 sha256 대신 **git ref 비교** → `git diff --stat`로 변경된 디렉토리만 재요약
- 자세한 절차·산출물 형식: `plugins/manual-digest/skills/manual-digest/references/codebase-extract.md`

## 큰 다이제스트 분할 (doc-atomize 연동)

다이제스트는 매뉴얼 질문마다 통째로 읽힌다. 1000페이지급 매뉴얼이나 대형 모노레포를 인제스트하면
다이제스트 자체가 수천 줄이 되어, 질문 한 번에 2만 토큰 넘게 태우게 된다.

이때 **요약을 한 번 더 하지 않는다** — 손실이 누적된다. 대신 `doc-atomize`의 `split_md.py`로
`digest.md`를 **무손실 분할**하고, 이후 조회를 `인덱스 1개 + 조각 1~3개`로 바꾼다.
조각을 합치면 원본 다이제스트와 sha256이 일치한다.

### 언제 분할되나

| `digest.md` 크기 | 동작 |
|---|---|
| 300줄 미만 | 분할 안 함 (인덱스 유지비가 더 큼) |
| 300~699줄 | 분할 안 함. `--atomize`를 직접 주면 진행 |
| **700줄 이상 또는 50 KB 이상** | 인제스트 마무리에서 **분할 제안** → 동의 시 실행 |
| 1200줄 이상 또는 90 KB 이상 | 강하게 권고 |

`index.md`(섹션→페이지 표)에도 같은 임계를 적용한다.

### 준비물

`doc-atomize` 플러그인이 설치돼 있어야 한다 (`/plugin`에서 설치). **없어도 인제스트는 정상 동작**하고
분할만 건너뛴다. `python3` 외 추가 설치·MCP는 없다.

### 분할 후 조회가 어떻게 바뀌나

```
분할 전: INDEX.md → digest.md 전체(1,340줄) → 답변
분할 후: INDEX.md → digest.atomized/<id>-digest.index.md → parts/007-….md 1~2개 → 답변
```

`INDEX.md`의 "분할" 칸이 채워진 매뉴얼은 Claude가 `digest.md`를 통째로 읽지 않는다.
출처 표기는 그대로 원본 기준(`§4.2, p.82`)이다 — 조각 번호는 다이제스트 내부 위치일 뿐이다.

### 되돌리기

```
/manual-digest --deatomize <id>
```

분할본만 지운다. `digest.md`는 손대지 않으므로 조회가 즉시 종전 방식으로 돌아간다.

자세한 절차·검증 게이트·큐레이션: `plugins/manual-digest/skills/manual-digest/references/digest-atomize.md`

## 산출물 구조

```
<scope>/.claude/manuals/
├── INDEX.md                              ← 마스터 카탈로그
└── <manual-id>/
    ├── digest.md                         ← 개요 + 섹션 요약 + 키워드 (분할해도 남는 정본)
    ├── index.md                          ← 섹션 → 페이지 매핑
    ├── metadata.json                     ← 메타데이터 + 샘플링 전략 + atomized 상태
    └── digest.atomized/                  ← (분할한 경우만) 무손실 조각
        ├── <id>-digest.index.md          ← 조회 진입점
        ├── <id>-digest.metadata.json
        └── parts/001-….md …
```

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| `pdf-reader MCP 미등록` | `/manual-digest-setup --mcp-only` |
| `MCP 등록했는데 read_pdf 도구 없음` | Claude Code 세션 재시작 |
| `CLAUDE.md 마커 손상` | `/manual-digest-setup --repair` |
| `같은 ID 중복 인제스트` | sha256 같으면 자동 스킵, 다르면 확인 후 덮어쓰기 |
| `대형 PDF (1000p+) 시간 초과` | 자동으로 페이지 청크 분할 — 진행률 표시 확인 |
| `read_pdf` 에러(`invalid horizontal advance` 등) | MCP 버그다 — `pdftotext -layout`으로 자동 재시도. PDF 자체는 대개 멀쩡하다 |
| `스캔 PDF (텍스트 레이어 없음)` | `pdftotext`로 3페이지 표본 검증 후 확정된 경우만 "OCR 필요, V2 이후" — 현재 미지원 |
| `pdftotext 없음 (Windows)` | poppler 설치 필요 (`scoop install poppler`) — 없으면 MCP 실패 시 대안이 사라진다 |
| `다이제스트가 커서 매번 무거움` | `/manual-digest --atomize <id>` (doc-atomize 필요) |
| `분할했는데 split_md.py를 못 찾음` | `/plugin`에서 doc-atomize 설치, 또는 `DOC_ATOMIZE_SPLIT_MD` 환경변수로 경로 지정 |
| `분할 verify FAIL` | 분할본 자동 삭제 후 원상 복구 — `digest.md`는 무손상, 조회는 종전대로 |
| `갱신 후 조각에 ⚠️ 표시` | 본문이 바뀐 조각 — 요약을 다시 쓰고 `split_md.py reindex` → `audit --strict` |
| `분할 후 audit BLOCK` | 요약이 제목 재진술·자동 폴백이거나 라우팅 힌트 부족 — metadata.json 수정 후 `reindex`. 분할본은 지우지 않는다 |


