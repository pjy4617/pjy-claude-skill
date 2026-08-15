---
name: doc-atomize
description: "대용량 마크다운(.md)을 무손실로 원자 분할하고 검색 인덱스를 만드는 워크플로. 큰 문서를 헤딩 우선 + 크기 가드로 조각내 `parts/*.md`로 저장하고, `<doc-id>.index.md`(라우팅 힌트·목차·포함 헤딩·키워드 역색인)를 진입점으로 만들어 이후 질문은 원본 대신 조각 1~3개만 읽는다. 요약이 아니라 분할이라 재조립하면 원본과 sha256이 일치한다. 사용자가 '이 md 파일 쪼개줘', '큰 마크다운 분할해줘', '문서 원자화', '컨텍스트 절약하게 문서 나눠줘', 'md 인덱싱', '/doc-atomize <file.md>', '/doc-atomize --update', '--list', '--remove', '--verify' 등을 요청하거나, 수백~수천 줄짜리 .md를 가리키며 분할·인덱싱·갱신·검증을 명시할 때 자동 적용. 외부 매뉴얼(PDF/CHM)을 '요약'해 등록하는 작업은 manual-digest 담당."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# doc-atomize — 마크다운 무손실 원자 분할

큰 마크다운을 **한 번만** 조각내어, 이후 모든 질문을 `인덱스 1개 + 조각 1~3개` 읽기로 끝내는 워크플로.

## manual-digest와 무엇이 다른가

| | manual-digest | **doc-atomize** |
|---|---|---|
| 입력 | PDF/CHM/HTML/EPUB/DOCX/코드베이스 | **이미 텍스트인 대용량 .md** |
| 처리 | **요약**(원본의 ~0.3%, 정보 손실 있음) | **분할**(무손실, 재조립 = 원본) |
| 정본 | 원본 — 다이제스트는 포인터 | **조각 자체가 정본** — 원문 그대로 인용 가능 |
| 목적 | 재추출 비용 제거 | 컨텍스트 절약 + 정확한 인용 |

PDF 매뉴얼을 등록하려면 `manual-digest`, 손안의 큰 `.md`를 쪼개려면 이 스킬이다.

## 사용 시기

다음 중 하나면 적용한다:
- 수백~수천 줄짜리 `.md`(PRD·설계서·규격서·회의록 누적본)를 반복 참조해야 함
- "이 문서 매번 통째로 읽기 부담된다", "필요한 절만 빨리 찾고 싶다"
- `/doc-atomize <file.md>` / `--update` / `--list` / `--remove` / `--verify` 명령
- 같은 대형 `.md`를 두 번째 이상 Read — 분할을 제안한다

다음은 **쓰지 않는다**:
- 300줄 미만 문서 (그냥 Read가 싸다 — 인덱스 유지비가 더 크다)
- 요약본이 필요한 경우 (분할은 총량을 줄이지 않는다)
- 원문 보존이 무의미한 임시 메모

## 사전 조건

`/doc-atomize-setup`으로 1회 초기화(디렉토리 + INDEX.md + CLAUDE.md 마커). 미초기화면 디렉토리는 자동 생성하고 마커 주입만 안내한다.
`python3` 필요 — 표준 라이브러리만 쓰므로 추가 설치·MCP는 없다. Windows에서 `python3`가 MS Store alias로 exit 49면 `py -3` 또는 `python`으로 대체한다.

## 산출물 위치와 명명 규칙

```
<scope_root>/.claude/atomized/
├── INDEX.md                          ← 마스터 카탈로그 (유일한 대문자 INDEX)
└── <doc-id>/
    ├── <doc-id>.index.md             ← 검색 진입점
    ├── <doc-id>.metadata.json        ← 정본 메타 (요약·키워드·라우팅 큐레이션 보관)
    └── parts/
        ├── 001-<slug>.md
        └── 002-<slug>.md …
```

**문서별 인덱스에 `<doc-id>.` 접두를 붙이는 것은 의도된 설계다.** 이유:
1. 문서가 10개면 `index.md`도 10개 — 파일명만으로 구분이 안 된다
2. `INDEX.md` vs `index.md`는 대소문자 한 글자 차이라 Windows/macOS 기본 파일시스템에서 혼동된다
3. `Glob **/*.index.md` 한 번으로 등록된 모든 문서 인덱스를 열거하고, `Grep <키워드> --glob "*.index.md"`로 전 문서 역색인을 한 번에 훑을 수 있다

- `--scope project`(기본): `<project>/.claude/atomized/`
- `--scope global`: `~/.claude/atomized/`
- `--in-place`: `<원본과 같은 디렉토리>/<doc-id>/` — repo 문서 자체를 재구성 (아래 별도 절차)

## 서브커맨드

| 호출 | 동작 |
|------|------|
| `/doc-atomize <file.md> [--scope project\|global] [--max-lines N] [--min-lines N] [--base-level 2\|3] [--slug auto\|ascii] [--doc-id ID]` | 신규 분할 |
| `/doc-atomize <file.md> --in-place` | 원본 자리에서 문서 재구성 (git 클린 상태 필수) |
| `/doc-atomize --update <id>` | 원본 sha256 비교 → 변경분만 재분할, 큐레이션 승계 |
| `/doc-atomize --verify <id>` | 재조립 sha256 대조 + 구조 무결성 검사 |
| `/doc-atomize --list [--scope project\|global\|all]` | 등록 문서 나열 |
| `/doc-atomize --remove <id>` | 디렉토리 + INDEX.md 항목 제거 |

## 워크플로 (8단계)

스크립트는 `${CLAUDE_SKILL_DIR}/assets/split_md.py`이며, 기계적 작업(경계 탐지·분할·프론트매터·라인 매핑·역색인·검증)을 결정적으로 처리한다. **의미 판단(요약 다듬기·키워드 선별·라우팅 힌트)만 네가 한다.**

### 1. 입력 검증

```bash
S="${CLAUDE_SKILL_DIR}/assets/split_md.py"
wc -l "<파일경로>"; wc -c "<파일경로>"
grep -cE "^#{1,6} " "<파일경로>"        # 헤딩 개수 — 구조 파악
```

- `.md`/`.markdown`이 아니면 중단하고 적합한 스킬 안내(PDF→manual-digest, 거버/KiCad→pcb-design-digest)
- 300줄 미만이면 "분할 이득이 인덱스 유지비보다 작다"고 알리고 사용자 확인 후 진행

### 2. doc-id 결정

파일명 → 소문자 kebab-case (`HW_PRD.md` → `hw-prd`). 이미 같은 id가 있으면 sha256을 비교해 동일하면 "이미 등록됨, `--update` 안내" 후 종료, 다르면 접미사(`hw-prd-v2`) 또는 `--update`를 사용자에게 묻는다. 파일명이 같은 다른 경로 문서는 상위 디렉토리명을 붙여 구분한다(`references-eni-guide`).

### 3. 분할 옵션 결정

기본값(최소 40줄 / 최대 250줄 / 하드 400줄 / 기준 레벨 자동)으로 충분한 경우가 대부분이다. 문서 유형별 조정은 `references/split-rules.md` 참조.

### 4. 분할 실행

```bash
python3 "$S" split "<파일경로>" --out "<scope_root>/.claude/atomized/<doc-id>"
```

출력에 조각 수·크기 분포·인덱스 크기·무손실 검증 결과가 나온다. **조각이 80개를 넘으면 경고**가 뜬다 — 인덱스가 무거워지므로 `--max-lines`를 키워 재분할을 검토한다.

### 5. 무손실 검증 (게이트)

```bash
python3 "$S" verify "<scope_root>/.claude/atomized/<doc-id>"
```

`PASS`가 아니면 **다음 단계로 가지 않는다.** 조각을 재조립한 sha256이 원본(정규화본)과 일치하는지, 라인 커버리지가 빈틈없는지, 고아 조각·깨진 링크가 없는지를 본다. 실패 시 조각을 지우고 원인을 보고한다 — 무손실이 깨진 분할은 쓸모가 없다.

### 6. 의미 큐레이션 (여기가 네 몫)

`<doc-id>.metadata.json`이 요약·키워드·라우팅의 **정본**이다. 인덱스는 여기서 생성되는 뷰이므로, 인덱스 마크다운을 직접 고치지 말고 metadata를 고친 뒤 재생성한다(그래야 `--update` 때 큐레이션이 살아남는다).

1. `<doc-id>.index.md`를 읽어 자동 생성된 요약을 훑는다
2. 부실한 요약(`(요약 필요)`, 문맥 없는 첫 문장)을 가진 조각만 골라 본문을 읽고 다시 쓴다
3. metadata.json의 해당 `parts[].summary`를 고치고 **`summary_source`를 `"curated"`로 바꾼다** — 이 표시가 있어야 `--update`가 요약을 보존한다
4. `routing_hints`를 5~10개 채운다. 형식:
   ```json
   "routing_hints": [
     {"question": "전원 레일 구성·전류 버짓", "parts": ["005-5-전원-설계"]},
     {"question": "PHY 스트랩 핀 / RMII 배선", "parts": ["006-6-DP83848-PHY-주변회로"]}
   ]
   ```
   사용자가 실제로 물어볼 법한 질문을 쓴다 — 목차 제목을 그대로 옮기지 않는다(그건 이미 목차에 있다)
5. 재생성:
   ```bash
   python3 "$S" reindex "<scope_root>/.claude/atomized/<doc-id>"
   ```

요약은 **한 줄, 90자 이내, 그 조각에만 있는 정보**로 쓴다. "이 절은 ~를 설명한다" 같은 빈 문장은 금지.

### 7. 마스터 카탈로그 등록

`<scope_root>/.claude/atomized/INDEX.md`의 표에 행을 추가한다:

```markdown
| id | 제목 | 원본 | 줄수 | 조각 | scope |
|----|------|------|------|------|-------|
| hw-prd | M.2 Artix-7 EtherCAT 마스터 카드 PRD | temp/HW_PRD.md | 884 | 13 | project |
```

### 8. 리포트

분할 결과(조각 수·크기 분포), 무손실 검증 결과, 인덱스 경로, 그리고 **다음부터의 조회 방법**을 알린다:

```
이제 이 문서 질문은 다음 순서로 처리됩니다:
  .claude/atomized/hw-prd/hw-prd.index.md → 후보 조각 → parts/*.md 만 Read
```

## `--in-place` 모드 (원본 자리 재구성)

repo 문서 자체를 쪼개 커밋하는 모드. **파괴적이므로 순서를 지킨다:**

1. `git status --short` — 클린이 아니면 중단(변경분과 섞이면 되돌리기 어렵다)
2. 사용자에게 대상 경로·생성될 구조를 보여주고 **명시적 확인**을 받는다
3. `python3 "$S" split "<원본>" --out "<원본디렉토리>/<doc-id>" --mode in-place`
4. `python3 "$S" verify "<원본디렉토리>/<doc-id>"` — **PASS일 때만** 다음으로
5. 원본을 `git rm`(추적 중) 또는 삭제. 삭제 전 `<doc-id>/.original-<파일명>.bak`으로 복사해 둔다
6. 원본을 가리키던 링크가 있는지 확인: `grep -rn "<원본파일명>" --include="*.md" .` → 발견 시 인덱스 경로로 갱신 제안

verify가 실패하면 **원본을 절대 지우지 않는다.**

## 자동 갱신 훅 (설치하면 바로 동작)

플러그인에 `hooks/hooks.json`이 포함되어 있어, **원본을 Edit/Write 하면 분할본이 자동으로 갱신**된다. 별도 설정은 없다.

```
사용자가 docs/prd/PRD-x.md 수정
  → PostToolUse 훅이 그 파일이 등록된 원본인지 확인 (metadata.json의 source 대조)
  → 맞으면 split_md.py update 실행 → 변경된 조각만 재생성 + 무손실 재검증
  → 결과를 additionalContext로 반환 (⚠️ 요약 재검토 필요 조각 포함)
```

동작 규칙:

| 상황 | 훅의 반응 |
|------|-----------|
| 등록되지 않은 `.md` 수정 | **아무 일도 하지 않는다** (분할 전 문서·검수 루프 중 문서 포함) |
| 내용이 실제로 안 바뀜 | 조용히 종료 (sha256 동일) |
| 변경 있음 | 변경 조각만 재생성, 큐레이션 승계, 결과 보고 |
| `split_md.py`를 못 찾음 | `--update` 수동 실행을 안내만 한다 |
| 갱신 실패·타임아웃(25초) | 실패 사실과 `--verify` 권고를 알린다 |
| 어떤 예외든 | **exit 0** — 훅이 사용자의 편집을 막지 않는다 |

> **훅은 요약을 다시 써주지 않는다.** 본문이 바뀐 조각에는 `⚠️`가 붙어 돌아오므로,
> 그 조각의 요약을 다듬고 `reindex`하는 것은 여전히 사람(모델)의 몫이다. 자동화한 것은
> **기계적 재분할과 무손실 검증**이지 의미 큐레이션이 아니다.

끄고 싶으면 `/plugin` 에서 doc-atomize를 비활성화하거나, 훅 명령을 프로젝트 설정에서 덮어쓴다.
`DOC_ATOMIZE_SPLIT_MD` 환경변수로 사용할 `split_md.py` 경로를 고정할 수도 있다.

## 갱신 (`--update`)

```bash
python3 "$S" update "<scope_root>/.claude/atomized/<doc-id>"
```

- 원본 sha256이 같으면 아무것도 하지 않는다
- 슬러그 기준으로 이전 조각과 매칭해 `curated` 요약·키워드를 승계한다
- 본문이 바뀐 조각의 승계 요약에는 `summary_stale` 표시가 붙는다 → **인덱스에 ⚠️로 나타나며, 해당 요약은 다시 검토해야 한다**
- 추가/변경/유지/삭제 조각 수를 보고하고 무손실 재검증까지 수행한다

갱신 후 `⚠️`가 붙은 조각의 요약을 다듬고 `summary_stale`을 지운 뒤 `reindex`한다.

## 목록 / 삭제

```bash
# 목록
cat "<scope_root>/.claude/atomized/INDEX.md"
ls -d "<scope_root>"/.claude/atomized/*/ 2>/dev/null

# 삭제 (사용자 확인 후)
rm -rf "<scope_root>/.claude/atomized/<doc-id>"
```
삭제 시 INDEX.md 행도 함께 제거한다. `--in-place` 산출물은 repo 파일이므로 `git rm -r` 여부를 사용자에게 확인한다.

## 실패 대응

| 증상 | 원인 | 조치 |
|------|------|------|
| `재조립 sha256 불일치` | 조각 파일이 외부에서 편집됨 | 조각을 직접 고치지 말 것 — 원본을 고치고 `update` |
| `라인 커버리지 불연속` | 스크립트 버그 | 조각 폐기 + 재현 입력과 함께 보고 |
| `고아 조각` | 이전 분할의 잔재 | `split --force`로 재분할 |
| 조각 80개 초과 경고 | 분할이 과도하게 잘음 | `--max-lines`를 키워 재분할 |
| `(요약 필요)` 다수 | 표·체크리스트 위주 문서 | 6단계 큐레이션에서 직접 작성 |

## 한계 (문서화된 것)

- **ATX 헤딩(`#`)만 인식** — setext 헤딩(`===`/`---` 밑줄)은 표·수평선과 구별이 모호해 지원하지 않는다
- **상대경로 자산은 재작성하지 않는다** — 본문을 그대로 두는 것이 무손실의 조건이다. 이미지/링크는 인덱스에 기록된 `source_dir` 기준으로 해석한다
- 무손실 보증은 **정규화(BOM 제거, CRLF→LF) 기준**이다. 원본 바이트 sha256은 변경 감지용으로 따로 보관한다
- 분할은 총량을 줄이지 않는다 — 절약은 "필요한 조각만 읽는" 조회 단계에서 발생한다

## 참조

| 파일 | 내용 |
|------|------|
| `references/split-rules.md` | 분할 경계·크기 정책·병합 규칙·엣지케이스·문서 유형별 옵션 튜닝 |
| `references/index-format.md` | 인덱스 5섹션 스키마, 조각 프론트매터 필드 사전, metadata.json 스키마 |
| `references/retrieval-guide.md` | 조회(읽는 쪽) 프로토콜, Grep 패턴, 원본으로 내려가는 기준 |
| `assets/split_md.py` | 분할기 — `split` / `verify` / `reindex` / `update` 서브커맨드 |
