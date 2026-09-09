---
name: manual-digest-setup
description: "manual-digest 플러그인 사용 전 환경을 1회 초기화하는 셋업 스킬. ① PDF 추출 환경 검사(PyMuPDF 가용성 + poppler pdftotext 폴백, 미설치 시 pip install pymupdf 안내) ② .claude/manuals/ 디렉토리(project 또는 global) 생성 ③ INDEX.md 헤더 작성 ④ CLAUDE.md에 매뉴얼 다이제스트 사용 규칙 마커 블록 주입 ⑤ 디렉토리 권한·마커 검증 ⑥ 상태 리포트. MCP 서버를 쓰지 않는다 — PDF 추출은 manual-digest 스킬에 동봉된 assets/pdf_extract.py가 담당한다. idempotent — 여러 번 실행해도 안전하며 누락분만 보충, 기존 콘텐츠는 보존. 사용자가 'manual-digest 셋업', '매뉴얼 다이제스트 설정', '/manual-digest-setup', '매뉴얼 다이제스트 환경 초기화', 'PyMuPDF 설치' 등을 요청하거나, manual-digest 첫 사용 직전에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# manual-digest 환경 셋업

`manual-digest` 플러그인을 처음 쓰기 전에 환경을 1회 초기화한다. **idempotent**: 여러 번 실행해도 안전하며, 이미 있는 항목은 건드리지 않고 누락된 것만 보충한다.

## 핵심 원칙

- **사용자 콘텐츠 보존** — 기존 CLAUDE.md / INDEX.md를 절대 덮어쓰지 않는다. 마커 블록(`<!-- manual-digest:start --> ... <!-- manual-digest:end -->`) 사이만 갱신
- **사용자 동의 우선** — 변경 예정 항목 미리 출력 + 확인 후 적용. `--dry-run`으로 미리 검토 가능
- **백업** — CLAUDE.md 수정 전 `CLAUDE.md.bak.<timestamp>` 백업
- **부분 실패 안전** — 한 단계 실패해도 다른 단계 결과 손실 없음
- **선택 의존성 비강제** — `doc-atomize`(큰 다이제스트 분할용)는 없어도 셋업·인제스트가 정상 동작한다. 존재 여부만 리포트한다

## 옵션

| 옵션 | 동작 |
|------|------|
| `--scope project\|global\|both` | 초기화 스코프 (기본: `project`) |
| `--skip-pdf-check` | PDF 추출 환경 검사 건너뜀 (코드베이스 다이제스트만 쓸 때) |
| `--repair` | 누락된 항목만 보충 (CLAUDE.md 마커 손상 등 복구) |
| `--dry-run` | 실제 변경 없이 무엇을 할지만 출력 |

## 호출 시점

- **첫 사용**: 매뉴얼을 처음 등록하기 전
- **새 프로젝트**: project scope를 새 프로젝트에서 초기화
- **CLAUDE.md 정리 후**: 사용자가 마커 블록을 지웠을 때 → `--repair`
- **PDF 추출이 안 될 때**: `pdf_extract.py`가 exit 2를 낼 때 → 다시 실행해 PyMuPDF 설치 여부 확인

## 절차

### 1. 사전 검사

```bash
# Claude CLI 존재 확인
command -v claude || { echo "ERROR: claude CLI not found"; exit 1; }

# 현재 working directory가 git 저장소 또는 .claude/가 있을 위치인지 확인 (project scope일 때)
TARGET_PROJECT="$(pwd)"

# 사용자에게 confirm
echo "셋업 대상:"
echo "  Project scope: $TARGET_PROJECT/.claude/manuals/"
echo "  Global scope:  $HOME/.claude/manuals/"
echo "  스코프: ${SCOPE:-project}"
```

### 2. PDF 추출 환경 검사

PDF 추출은 `manual-digest` 스킬에 동봉된 `assets/pdf_extract.py`가 담당한다. **설치할 서버도
등록할 MCP도 없다.** 필요한 것은 파이썬 패키지 하나(PyMuPDF)뿐이고, 그마저 없어도
`pdftotext` 폴백으로 인제스트가 돌아간다. 여기서는 **있는지 확인하고 없으면 안내만** 한다.

```bash
if [ "$SKIP_PDF_CHECK" != "true" ]; then
    echo "[1/5] PDF 추출 환경 검사"

    # L1: PyMuPDF — pdf_extract.py의 기본 경로
    if python3 -c "import fitz" 2>/dev/null; then
        PYMUPDF_VER="$(python3 -c "import fitz; print(fitz.VersionBind)" 2>/dev/null)"
        echo "  ✓ PyMuPDF: 설치됨 (${PYMUPDF_VER:-버전 확인 불가})"
        PYMUPDF_OK=true
    else
        echo "  ○ PyMuPDF: 미설치 — pdf_extract.py가 exit 2를 반환한다"
        echo "    설치 명령: pip install pymupdf"
        echo "    (설치는 사용자 동의 후에만 실행한다. 설치하지 않아도 L2 폴백으로 인제스트는 가능하다)"
        PYMUPDF_OK=false
    fi

    # L2: poppler pdftotext — 폴백 경로
    if command -v pdftotext >/dev/null 2>&1; then
        echo "  ✓ pdftotext(poppler): 사용 가능 — L2 폴백 확보"
    else
        echo "  ○ pdftotext(poppler): 없음 — L2 폴백 없음 (Windows 기본값)"
    fi

    if [ "$PYMUPDF_OK" != "true" ] && ! command -v pdftotext >/dev/null 2>&1; then
        echo "  ⚠️  PDF 추출 경로가 하나도 없다 — pip install pymupdf 를 먼저 하십시오."
        echo "     (코드베이스 다이제스트는 이것들 없이도 정상 동작한다)"
    fi
fi
```

> **Windows**: poppler(pdftotext)가 기본 포함되지 않는다. PyMuPDF는 `pip install pymupdf`
> 휠 하나로 설치되므로, Windows에서는 PyMuPDF 설치가 사실상 유일한 준비물이다.

### 3. manuals 디렉토리 초기화

`--scope`에 따라 한 곳 또는 양쪽:

```bash
init_manuals_dir() {
    local DIR="$1"
    local SCOPE_LABEL="$2"

    if [ -d "$DIR" ]; then
        echo "  $SCOPE_LABEL: 디렉토리 이미 존재"
    else
        if [ "$DRY_RUN" = "true" ]; then
            echo "  (dry-run) mkdir -p $DIR"
        else
            mkdir -p "$DIR"
            echo "  $SCOPE_LABEL: 디렉토리 생성"
        fi
    fi

    # 쓰기 권한 테스트
    if [ "$DRY_RUN" != "true" ]; then
        TEST_FILE="$DIR/.write-test"
        if touch "$TEST_FILE" 2>/dev/null; then
            rm "$TEST_FILE"
        else
            echo "  ⚠️  $SCOPE_LABEL: 쓰기 권한 없음 — 권한 확인 필요"
            return 1
        fi
    fi

    # INDEX.md 헤더 작성 (없을 때만)
    if [ ! -f "$DIR/INDEX.md" ]; then
        if [ "$DRY_RUN" != "true" ]; then
            cat > "$DIR/INDEX.md" <<'EOF'
# Indexed Manuals

> manual-digest 플러그인이 관리하는 매뉴얼 카탈로그. Claude는 외부 매뉴얼이 필요한 질문을 받으면 **먼저 이 파일을 확인**하고, 관련 매뉴얼의 `digest.md`를 1차 참조원으로 사용한다.

## 등록된 매뉴얼

_(아직 등록된 매뉴얼이 없습니다. `/manual-digest <path>`로 첫 매뉴얼을 등록하세요.)_

| id | 제목 | 포맷 | 분할 | 요약 |
|----|------|------|------|------|

## 참조 규칙

1. 매뉴얼 관련 질문 시 → 본 INDEX.md를 먼저 확인
2. "분할" 칸이 비어 있으면(`—`) `digest.md`를 1차 참조.
   채워져 있으면 `digest.md`를 통째로 읽지 말고 `<id>/digest.atomized/<id>-digest.index.md`를 먼저 읽고
   후보 조각 1~3개만 `parts/`에서 Read
3. 부족하면 `index.md`로 페이지/파일 포인터 → 원본 핀포인트
4. 답변에 출처(§/p./scope) 명시 — 조각을 인용해도 출처는 원본 기준으로 쓴다
5. 인덱싱되지 않은 매뉴얼이면 `/manual-digest <path>` 등록 제안
EOF
            echo "    INDEX.md 헤더 작성"
        fi
    else
        echo "    INDEX.md 이미 존재 — 보존"
    fi
}

echo "[2/5] manuals 디렉토리 초기화"
case "${SCOPE:-project}" in
    project) init_manuals_dir "$TARGET_PROJECT/.claude/manuals" "project" ;;
    global)  init_manuals_dir "$HOME/.claude/manuals" "global" ;;
    both)    init_manuals_dir "$TARGET_PROJECT/.claude/manuals" "project"
             init_manuals_dir "$HOME/.claude/manuals" "global" ;;
esac
```

### 4. CLAUDE.md 마커 블록 주입

`<!-- manual-digest:start -->` ~ `<!-- manual-digest:end -->` 마커로 감싼 가이드 블록을 주입한다.

**이 블록은 등록 매뉴얼 수도 목록도 담지 않는다 — INDEX.md를 보라는 고정 포인터다.**
CLAUDE.md는 매 세션 무조건 로드되므로, 여기에 카탈로그를 넣으면 매뉴얼이 늘 때마다 상주 비용이
같이 커지고 매뉴얼을 안 쓰는 세션도 그 비용을 낸다. 게다가 개수는 등록·삭제 때마다 갱신하지 않으면
곧 틀린 값이 된다(실측: 블록은 "1개"라고 적혀 있는데 실제 global에는 8종이 등록돼 있었다).
카탈로그는 필요할 때만 읽히는 `INDEX.md`가 유일한 정본이다.

블록이 고정이므로 **인제스트·삭제는 CLAUDE.md를 건드리지 않는다.** 세션 중 CLAUDE.md 수정은
프롬프트 캐시를 무효화하는데, 그 비용을 갱신할 것도 없는 블록 때문에 낼 이유가 없다.

```bash
inject_marker() {
    local CLAUDE_MD="$1"
    local SCOPE_LABEL="$2"

    local MARKER_BLOCK
    MARKER_BLOCK="$(cat <<'EOF'
<!-- manual-digest:start -->
## 매뉴얼 다이제스트 사용 규칙

외부 매뉴얼이 다이제스트로 등록되어 있을 수 있다 — 도메인 매뉴얼이 필요한 질문을 받으면:

1. `.claude/manuals/INDEX.md` (project) + `~/.claude/manuals/INDEX.md` (global) 양쪽 확인
2. 관련 매뉴얼의 `digest.md` 우선 참조 → 부족하면 `index.md` 페이지 포인터로 원본 핀포인트
3. **분할된 다이제스트**: INDEX.md "분할" 칸이 채워진 매뉴얼은 `digest.md`를 통째로 읽지 않는다 —
   `<id>/digest.atomized/<id>-digest.index.md`를 먼저 읽고 후보 조각 1~3개만 `parts/`에서 Read
4. 답변에 출처(§/p./scope) 명시 — 조각 인용 시에도 출처는 원본 기준(§/p.)
5. 인덱싱되지 않은 매뉴얼이면 `/manual-digest <path>` 등록 제안

PDF 핀포인트 추출: manual-digest 스킬의 `assets/pdf_extract.py` — 위치를 모르면
`find <원본> "<검색어>"`로 페이지 열지도를 먼저 받고, 그다음 `text <원본> --pages "<범위 또는 혼합 범위>"`.
exit 2(PyMuPDF 미설치)나 빈 텍스트면 `pdftotext -layout`으로 재시도하고, 추출 실패를 스캔본으로 단정하지 않는다.
<!-- manual-digest:end -->
EOF
    )"

    if [ ! -f "$CLAUDE_MD" ]; then
        if [ "$DRY_RUN" = "true" ]; then
            echo "  (dry-run) $SCOPE_LABEL CLAUDE.md 신규 생성 + 마커 블록"
        else
            echo "$MARKER_BLOCK" > "$CLAUDE_MD"
            echo "  $SCOPE_LABEL: CLAUDE.md 신규 생성 + 마커 주입"
        fi
        return
    fi

    # 백업
    if [ "$DRY_RUN" != "true" ]; then
        cp "$CLAUDE_MD" "$CLAUDE_MD.bak.$(date +%Y%m%d-%H%M%S)"
    fi

    if grep -q "<!-- manual-digest:start -->" "$CLAUDE_MD"; then
        # 블록은 고정 포인터라 평소엔 갱신할 것이 없다.
        # --repair 일 때만 낡은 블록(예: "현재 N개" 문구가 남은 구버전)을 현재 형식으로 교체한다.
        if [ "${REPAIR:-false}" = "true" ]; then
            if [ "$DRY_RUN" = "true" ]; then
                echo "  (dry-run) $SCOPE_LABEL CLAUDE.md 마커 블록을 현재 형식으로 교체"
            else
                MARKER_BLOCK="$MARKER_BLOCK" python3 - "$CLAUDE_MD" <<'PY'
import os, re, sys, pathlib
p = pathlib.Path(sys.argv[1])
p.write_text(re.sub(
    r"<!-- manual-digest:start -->.*?<!-- manual-digest:end -->",
    lambda _: os.environ["MARKER_BLOCK"],
    p.read_text(encoding="utf-8"), count=1, flags=re.S), encoding="utf-8")
PY
                echo "  $SCOPE_LABEL: CLAUDE.md 마커 블록 교체 (백업: $CLAUDE_MD.bak.*)"
            fi
        else
            echo "  $SCOPE_LABEL: CLAUDE.md 마커 이미 존재 — 보존 (구버전 문구 정리는 --repair)"
        fi
    else
        if [ "$DRY_RUN" = "true" ]; then
            echo "  (dry-run) $SCOPE_LABEL CLAUDE.md 끝에 마커 블록 추가"
        else
            echo "" >> "$CLAUDE_MD"
            echo "$MARKER_BLOCK" >> "$CLAUDE_MD"
            echo "  $SCOPE_LABEL: CLAUDE.md 끝에 마커 추가 (백업: $CLAUDE_MD.bak.*)"
        fi
    fi
}

echo "[3/5] CLAUDE.md 마커 블록 주입"
case "${SCOPE:-project}" in
    project) inject_marker "$TARGET_PROJECT/CLAUDE.md" "project" ;;
    global)  inject_marker "$HOME/.claude/CLAUDE.md" "global" ;;
    both)    inject_marker "$TARGET_PROJECT/CLAUDE.md" "project"
             inject_marker "$HOME/.claude/CLAUDE.md" "global" ;;
esac
```

### 5. 검증

```bash
echo "[4/5] 검증"

# PDF 추출기 동작 확인 (스크립트 자체가 도는지)
if [ "$SKIP_PDF_CHECK" != "true" ] && [ "$DRY_RUN" != "true" ]; then
    PDF_TOOL="$(find "$HOME/.claude/plugins" -path "*manual-digest*/skills/manual-digest/assets/pdf_extract.py" -print -quit 2>/dev/null)"
    [ -z "$PDF_TOOL" ] && [ -f "./plugins/manual-digest/skills/manual-digest/assets/pdf_extract.py" ] \
        && PDF_TOOL="./plugins/manual-digest/skills/manual-digest/assets/pdf_extract.py"
    if [ -n "$PDF_TOOL" ] && python3 "$PDF_TOOL" --help >/dev/null 2>&1; then
        echo "  ✓ pdf_extract.py: $PDF_TOOL"
    else
        echo "  ○ pdf_extract.py: 위치 확인 실패 — 스킬 호출 시 \${CLAUDE_SKILL_DIR}/assets/pdf_extract.py 로 접근된다"
    fi
fi

# INDEX.md 확인
case "${SCOPE:-project}" in
    project) [ -f "$TARGET_PROJECT/.claude/manuals/INDEX.md" ] && echo "  ✓ project INDEX.md 존재" ;;
    global)  [ -f "$HOME/.claude/manuals/INDEX.md" ] && echo "  ✓ global INDEX.md 존재" ;;
    both)    [ -f "$TARGET_PROJECT/.claude/manuals/INDEX.md" ] && echo "  ✓ project INDEX.md 존재"
             [ -f "$HOME/.claude/manuals/INDEX.md" ] && echo "  ✓ global INDEX.md 존재" ;;
esac

# CLAUDE.md 마커 확인
case "${SCOPE:-project}" in
    project) grep -q "manual-digest:start" "$TARGET_PROJECT/CLAUDE.md" 2>/dev/null && echo "  ✓ project CLAUDE.md 마커 주입됨" ;;
    global)  grep -q "manual-digest:start" "$HOME/.claude/CLAUDE.md" 2>/dev/null && echo "  ✓ global CLAUDE.md 마커 주입됨" ;;
    both)    grep -q "manual-digest:start" "$TARGET_PROJECT/CLAUDE.md" 2>/dev/null && echo "  ✓ project CLAUDE.md 마커 주입됨"
             grep -q "manual-digest:start" "$HOME/.claude/CLAUDE.md" 2>/dev/null && echo "  ✓ global CLAUDE.md 마커 주입됨" ;;
esac

# 선택 의존성: doc-atomize (큰 다이제스트 무손실 분할용) — 없어도 인제스트는 정상 동작
SPLIT_MD=""
if [ -n "$DOC_ATOMIZE_SPLIT_MD" ] && [ -f "$DOC_ATOMIZE_SPLIT_MD" ]; then
    SPLIT_MD="$DOC_ATOMIZE_SPLIT_MD"
else
    SPLIT_MD="$(find "$HOME/.claude/plugins" -path "*doc-atomize*/skills/doc-atomize/assets/split_md.py" -print -quit 2>/dev/null)"
fi
if [ -n "$SPLIT_MD" ]; then
    echo "  ✓ doc-atomize split_md.py: $SPLIT_MD (큰 다이제스트 분할 가능)"
else
    echo "  ○ doc-atomize 미설치 — 선택 사항. 설치하면 700줄 넘는 다이제스트를 무손실 분할해 조회 비용을 줄일 수 있다"
fi
```

### 6. 상태 리포트

```
[5/5] 셋업 완료

스코프: <project|global|both>
PDF 추출: PyMuPDF <있음 버전/없음> / pdftotext <있음/없음>
디렉토리: <생성됨/이미있음>
CLAUDE.md: <주입됨/이미있음>
doc-atomize: <있음(분할 가능)/없음(선택 사항)>

다음 단계:
  ① (PyMuPDF 미설치인 경우) pip install pymupdf — 사용자 동의 후
  ② /manual-digest <path>로 첫 매뉴얼 등록
  ③ /manual-digest --list로 등록된 매뉴얼 확인

문제 해결:
  - PDF 추출이 exit 2: PyMuPDF 미설치 신호다(PDF 문제 아님) — pip install pymupdf
  - PyMuPDF도 pdftotext도 없음: PDF 인제스트 불가. 코드베이스 다이제스트는 그대로 가능
  - CLAUDE.md 마커 손상: /manual-digest-setup --repair
  - 권한 에러: 디렉토리 권한 확인 또는 --scope 변경
  - 다이제스트가 너무 커서 매번 무거움: /plugin 에서 doc-atomize 설치 후 /manual-digest --atomize <id>
```

## Non-goals

- 하지 않음: 매뉴얼 인제스트 — 메인 스킬(`/manual-digest <path>`) 책임
- 하지 않음: 패키지 자동 설치 — `pip install pymupdf`는 사용자 동의 후에만 실행한다
- 하지 않음: 기존 MCP 등록 제거 — 이 플러그인은 더 이상 PDF MCP를 쓰지 않지만 등록을 지우지 않는다. 다른 용도로 쓰고 있을 수 있으므로, 필요 없으면 사용자가 직접 `claude mcp remove pdf-reader`
- 하지 않음: 마커 블록 외부 CLAUDE.md 내용 수정

$ARGUMENTS
