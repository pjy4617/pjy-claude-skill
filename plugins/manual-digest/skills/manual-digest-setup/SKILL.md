---
name: manual-digest-setup
description: "manual-digest 플러그인 사용 전 환경을 1회 초기화하는 셋업 스킬. ① PDF 추출용 @sylphx/pdf-reader-mcp MCP를 claude mcp add로 등록 ② .claude/manuals/ 디렉토리(project 또는 global) 생성 ③ INDEX.md 헤더 작성 ④ CLAUDE.md에 매뉴얼 다이제스트 사용 규칙 마커 블록 주입 ⑤ MCP 연결성·디렉토리 권한 검증 ⑥ 상태 리포트. idempotent — 여러 번 실행해도 안전하며 누락분만 보충, 기존 콘텐츠는 보존. 사용자가 'manual-digest 셋업', '매뉴얼 다이제스트 설정', 'PDF MCP 등록', '/manual-digest-setup', '매뉴얼 다이제스트 환경 초기화', 'pdf-reader 설치' 등을 요청하거나, manual-digest 첫 사용 직전에 자동 적용."
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

## 옵션

| 옵션 | 동작 |
|------|------|
| `--scope project\|global\|both` | 초기화 스코프 (기본: `project`) |
| `--mcp-only` | MCP 등록만 (디렉토리/CLAUDE.md 건드리지 않음) |
| `--skip-mcp` | MCP 등록 단계 건너뜀 (이미 다른 PDF MCP 사용 중) |
| `--repair` | 누락된 항목만 보충 (CLAUDE.md 마커 손상 등 복구) |
| `--dry-run` | 실제 변경 없이 무엇을 할지만 출력 |

## 호출 시점

- **첫 사용**: 매뉴얼을 처음 등록하기 전
- **새 프로젝트**: project scope를 새 프로젝트에서 초기화
- **MCP 손상/제거**: `claude mcp list`에서 pdf-reader 사라졌을 때 → `--mcp-only`
- **CLAUDE.md 정리 후**: 사용자가 마커 블록을 지웠을 때 → `--repair`

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

### 2. PDF MCP 등록 검사 + 등록

```bash
if [ "$SKIP_MCP" != "true" ]; then
    # 등록 여부 확인
    if claude mcp list 2>/dev/null | grep -q "pdf-reader"; then
        STATE=$(claude mcp list 2>/dev/null | grep "pdf-reader" | grep -o "Connected\|Failed\|Disconnected" || echo "Unknown")
        echo "[1/5] pdf-reader MCP: 이미 등록됨 (state: $STATE)"
    else
        echo "[1/5] pdf-reader MCP: 미등록 → 등록 진행"
        if [ "$DRY_RUN" = "true" ]; then
            echo "  (dry-run) claude mcp add pdf-reader --scope user -- cmd /c npx -y @sylphx/pdf-reader-mcp"
        else
            claude mcp add pdf-reader --scope user -- cmd /c npx -y "@sylphx/pdf-reader-mcp"
            echo ""
            echo "  ⚠️  세션 재시작 필요 — Claude Code를 종료 후 다시 시작해야 read_pdf 도구가 활성화됩니다."
        fi
    fi
fi
```

> **Windows PowerShell 환경**: `cmd /c npx -y @sylphx/pdf-reader-mcp`로 등록한다 (cmd 래퍼가 stdio 안정성 확보).

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

## 참조 규칙

1. 매뉴얼 관련 질문 시 → 본 INDEX.md를 먼저 확인
2. 관련 `digest.md`를 1차 참조 → 부족하면 `index.md`로 페이지 포인터 → 원본 핀포인트
3. 답변에 출처(§/p./scope) 명시
4. 인덱싱되지 않은 매뉴얼이면 `/manual-digest <path>` 등록 제안
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

```bash
inject_marker() {
    local CLAUDE_MD="$1"
    local SCOPE_LABEL="$2"

    local MARKER_BLOCK
    MARKER_BLOCK="$(cat <<'EOF'
<!-- manual-digest:start -->
## 매뉴얼 다이제스트 사용 규칙

이 환경에는 외부 매뉴얼이 다이제스트로 등록될 수 있다 (현재 0개) — 도메인 매뉴얼이 필요한 질문을 받으면:

1. `.claude/manuals/INDEX.md` (project) + `~/.claude/manuals/INDEX.md` (global) 양쪽 확인
2. 관련 매뉴얼의 `digest.md` 우선 참조 → 부족하면 `index.md` 페이지 포인터로 원본 핀포인트
3. 답변에 출처(§/p./scope) 명시
4. 인덱싱되지 않은 매뉴얼이면 `/manual-digest <path>` 등록 제안

PDF 핀포인트 추출: `mcp__pdf-reader__read_pdf` `pages: "<범위 또는 혼합 범위>"`
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
        # 이미 마커 있음 → 카탈로그 요약만 갱신 (REPAIR 모드 아니면 스킵)
        echo "  $SCOPE_LABEL: CLAUDE.md 마커 이미 존재 — 보존"
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
if [ "$MCP_ONLY" != "true" ]; then
    case "${SCOPE:-project}" in
        project) inject_marker "$TARGET_PROJECT/CLAUDE.md" "project" ;;
        global)  inject_marker "$HOME/.claude/CLAUDE.md" "global" ;;
        both)    inject_marker "$TARGET_PROJECT/CLAUDE.md" "project"
                 inject_marker "$HOME/.claude/CLAUDE.md" "global" ;;
    esac
fi
```

### 5. 검증

```bash
echo "[4/5] 검증"

# MCP 연결 확인
if [ "$SKIP_MCP" != "true" ] && [ "$DRY_RUN" != "true" ]; then
    if claude mcp list 2>/dev/null | grep "pdf-reader" | grep -q "Connected"; then
        echo "  ✓ pdf-reader MCP: Connected"
    else
        echo "  ⚠️  pdf-reader MCP: 미연결 — 세션 재시작 후 자동 활성화"
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
if [ "$MCP_ONLY" != "true" ]; then
    case "${SCOPE:-project}" in
        project) grep -q "manual-digest:start" "$TARGET_PROJECT/CLAUDE.md" 2>/dev/null && echo "  ✓ project CLAUDE.md 마커 주입됨" ;;
        global)  grep -q "manual-digest:start" "$HOME/.claude/CLAUDE.md" 2>/dev/null && echo "  ✓ global CLAUDE.md 마커 주입됨" ;;
        both)    grep -q "manual-digest:start" "$TARGET_PROJECT/CLAUDE.md" 2>/dev/null && echo "  ✓ project CLAUDE.md 마커 주입됨"
                 grep -q "manual-digest:start" "$HOME/.claude/CLAUDE.md" 2>/dev/null && echo "  ✓ global CLAUDE.md 마커 주입됨" ;;
    esac
fi
```

### 6. 상태 리포트

```
[5/5] 셋업 완료

스코프: <project|global|both>
MCP:    <등록됨/이미있음/생략>
디렉토리: <생성됨/이미있음>
CLAUDE.md: <주입됨/이미있음>

다음 단계:
  ① (MCP 신규 등록한 경우) Claude Code 재시작
  ② /manual-digest <path>로 첫 매뉴얼 등록
  ③ /manual-digest --list로 등록된 매뉴얼 확인

문제 해결:
  - MCP 미연결: claude mcp list로 상태 확인, 재등록 시 /manual-digest-setup --mcp-only
  - CLAUDE.md 마커 손상: /manual-digest-setup --repair
  - 권한 에러: 디렉토리 권한 확인 또는 --scope 변경
```

## Non-goals

- ❌ 매뉴얼 인제스트 — 메인 스킬(`/manual-digest <path>`) 책임
- ❌ MCP 자동 제거 — 사용자가 직접 `claude mcp remove pdf-reader`
- ❌ Claude Code 자동 재시작 — 안내만, 사용자 동의 필요
- ❌ 마커 블록 외부 CLAUDE.md 내용 수정

$ARGUMENTS
