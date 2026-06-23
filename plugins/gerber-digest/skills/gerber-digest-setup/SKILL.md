---
name: gerber-digest-setup
description: "gerber-digest 플러그인 사용 전 환경을 1회 초기화하는 셋업 스킬. ① gerber-pcb-analyst 에이전트를 타겟 프로젝트 .claude/agents/로 설치 ② .claude/gerbers/ 디렉토리(project 또는 global) 생성 ③ INDEX.md 헤더 작성 ④ CLAUDE.md에 거버 다이제스트 사용 규칙 마커 블록 주입 ⑤ 설치 검증 ⑥ 상태 리포트. 거버 파싱은 MCP·gerbv가 불필요하므로 MCP 등록 단계가 없다. idempotent — 여러 번 실행해도 안전하며 누락분만 보충, 기존 콘텐츠는 보존. 사용자가 'gerber-digest 셋업', '거버 다이제스트 설정', 'gerber-pcb-analyst 설치', '/gerber-digest-setup', '거버 다이제스트 환경 초기화' 등을 요청하거나, gerber-digest 첫 사용 직전에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# gerber-digest 환경 셋업

`gerber-digest` 플러그인을 처음 쓰기 전에 환경을 1회 초기화한다. **idempotent**: 여러 번 실행해도 안전하며, 이미 있는 항목은 건드리지 않고 누락된 것만 보충한다.

> **MCP 불필요**: 거버/드릴/리포트는 전부 텍스트라 `Read`/`Grep`/`Bash`로 파싱한다. `manual-digest`와 달리 PDF MCP 같은 외부 서버 등록이 없다. 대신 이 셋업은 깊은 분석용 **`gerber-pcb-analyst` 에이전트**를 설치한다.

## 핵심 원칙

- **사용자 콘텐츠 보존** — 기존 CLAUDE.md / INDEX.md를 절대 덮어쓰지 않는다. 마커 블록(`<!-- gerber-digest:start --> ... <!-- gerber-digest:end -->`) 사이만 갱신.
- **사용자 동의 우선** — 변경 예정 항목 미리 출력 + 확인. `--dry-run`으로 미리 검토 가능.
- **백업** — CLAUDE.md 수정 전 `CLAUDE.md.bak.<timestamp>` 백업.
- **부분 실패 안전** — 한 단계 실패해도 다른 단계 결과 손실 없음.

## 옵션

| 옵션 | 동작 |
|------|------|
| `--scope project\|global\|both` | 초기화 스코프 (기본: `project`) |
| `--agent-only` | 에이전트 설치만 (디렉토리/CLAUDE.md 건드리지 않음) |
| `--skip-agent` | 에이전트 설치 건너뜀 (직접 파싱 폴백만 사용) |
| `--repair` | 마커가 온전(start+end)하면 블록 재작성, 마커 전체 누락이면 재주입. end 마커 유실 등 비대칭 손상은 안전상 자동복구 않고 수동 확인 안내 |
| `--dry-run` | 실제 변경 없이 무엇을 할지만 출력 |

## 절차

### 1. 타겟 경로 확인

`kicad-setup`과 동일한 관례를 따른다: **에이전트 소스(`agents/`)는 플러그인 루트 기준 상대경로 `cp agents/...`로 복사**하고, **`$TARGET_PROJECT`에는 사용자의 프로젝트 절대경로를 따로 채운다**(둘은 독립 경로). ⚠️ **`$TARGET_PROJECT`를 `$(pwd)`로 폴백하지 마라** — 셋업 bash는 보통 플러그인 루트에서 돌아가 `$(pwd)`가 플러그인 폴더가 되고, 그러면 산출물(.claude/gerbers·CLAUDE.md 마커·에이전트)이 사용자 프로젝트가 아니라 플러그인 폴더에 잘못 설치된다.

사용자에게 거버를 다룰 **프로젝트 디렉토리 절대경로**를 질문해 `TARGET_PROJECT`에 넣는다(예: `/home/user/board/hw`). `--scope global` + `--skip-agent`면 생략 가능.

```bash
echo "[1/5] 타겟 경로 확인"
# 모순 옵션 조합 차단 — 둘 다 주면 수행할 작업이 없음
[ "$AGENT_ONLY" = "true" ] && [ "$SKIP_AGENT" = "true" ] && { echo "  ⚠️ --agent-only와 --skip-agent를 함께 쓰면 수행할 작업이 없습니다 — 종료"; exit 0; }
# scope 값 선검증 — 잘못된 값이 case의 default arm 부재로 조용히 no-op 되는 것 차단
case "${SCOPE:-project}" in project|global|both) ;; *) echo "  ERROR: 알 수 없는 scope '$SCOPE' (project|global|both 중 하나)"; exit 1 ;; esac
# TARGET_PROJECT = 사용자가 답한 프로젝트 절대경로 (플러그인 루트 $(pwd)로 폴백 금지).
# project/both scope이거나 에이전트 설치가 필요하면 절대경로 필수 — 미설정 시 즉시 중단(빈 값이 /.claude·/CLAUDE.md 루트로 새는 것 차단).
if [ "$DRY_RUN" != "true" ] && [ -z "$TARGET_PROJECT" ] && { [ "${SCOPE:-project}" != "global" ] || [ "$SKIP_AGENT" != "true" ]; }; then
    echo "  ERROR: 프로젝트 절대경로를 TARGET_PROJECT에 지정하세요 (예: TARGET_PROJECT=/path/to/project). 미설정 상태로 진행 금지."; exit 1
fi
# dry-run + project 경로 미지정이면 미리보기용 placeholder 사용(실제 쓰기 없음, 루트 가드에도 안 걸려 'would create' 미리보기가 의미있게 나옴)
[ "$DRY_RUN" = "true" ] && [ -z "$TARGET_PROJECT" ] && TARGET_PROJECT="<프로젝트경로>"
echo "  Project scope: ${TARGET_PROJECT:-<프로젝트 경로 필요>}/.claude/gerbers/  + .claude/agents/"
echo "  Global scope:  $HOME/.claude/gerbers/"
echo "  스코프: ${SCOPE:-project}"
```

### 2. gerber-pcb-analyst 에이전트 설치

플러그인의 `agents/gerber-pcb-analyst.md`를 타겟 프로젝트의 `.claude/agents/`로 복사한다(에이전트는 항상 project 위치에 둔다 — 보드 메모리가 프로젝트와 함께 버전 관리됨):

```bash
if [ "$SKIP_AGENT" = "true" ]; then
    echo "[2/5] gerber-pcb-analyst 에이전트: 건너뜀(--skip-agent)"
else
    AGENT_DIR="$TARGET_PROJECT/.claude/agents"
    if [ -z "$TARGET_PROJECT" ]; then
        echo "[2/5] ⚠️ TARGET_PROJECT 미설정 — 에이전트 설치 중단"
    elif [ -f "$AGENT_DIR/gerber-pcb-analyst.md" ]; then
        echo "[2/5] gerber-pcb-analyst 에이전트: 이미 설치됨 — 보존(사용자 커스터마이즈 가능성)"
    elif [ "$DRY_RUN" = "true" ]; then
        echo "[2/5] (dry-run) cp agents/gerber-pcb-analyst.md $AGENT_DIR/"
    else
        mkdir -p "$AGENT_DIR"
        cp agents/gerber-pcb-analyst.md "$AGENT_DIR/"
        echo "[2/5] gerber-pcb-analyst 에이전트: 설치 완료 → $AGENT_DIR/"
    fi
fi
```

> 에이전트 설치 후 Claude Code가 `subagent_type: "gerber-pcb-analyst"`로 호출할 수 있게 되려면 **세션 재시작**이 필요할 수 있다.

### 3. gerbers 디렉토리 초기화

`--scope`에 따라 한 곳 또는 양쪽. 각 디렉토리에 INDEX.md 헤더를 없을 때만 작성:

```bash
init_gerbers_dir() {
    local DIR="$1"; local LABEL="$2"
    case "$DIR" in ""|/.claude/*) echo "  ⚠️ $LABEL: 잘못된 대상 경로 '$DIR' (TARGET_PROJECT 미설정?) — 중단"; return 1 ;; esac
    [ -d "$DIR" ] && echo "  $LABEL: 디렉토리 이미 존재" || { [ "$DRY_RUN" = "true" ] && echo "  (dry-run) mkdir -p $DIR" || { mkdir -p "$DIR"; echo "  $LABEL: 디렉토리 생성"; }; }
    # 쓰기 권한 사전 검출 (INDEX.md 작성 시점이 아니라 미리 명확히 실패)
    if [ "$DRY_RUN" != "true" ]; then
        if touch "$DIR/.write-test" 2>/dev/null; then rm -f "$DIR/.write-test"; else echo "  ⚠️  $LABEL: 쓰기 권한 없음 — 권한 확인 또는 --scope 변경 필요"; return 1; fi
    fi
    if [ "$DRY_RUN" != "true" ] && [ ! -f "$DIR/INDEX.md" ]; then
        cat > "$DIR/INDEX.md" <<'EOF'
# Indexed Gerber Boards

> gerber-digest 플러그인이 관리하는 보드(거버 세트) 카탈로그. Claude는 보드/거버 정보가 필요한 질문을 받으면 **먼저 이 파일을 확인**하고, 관련 보드의 `digest.md`를 1차 참조원으로 사용한다.

## 등록된 보드

_(아직 등록된 보드가 없습니다. `/gerber-digest <폴더>`로 첫 보드를 등록하세요.)_

## 참조 규칙

1. 보드/거버 관련 질문 시 → 본 INDEX.md를 먼저 확인
2. 관련 `digest.md`를 1차 참조 → 부족하면 `index.md`로 파일/라인 포인터 → 원본 거버 핀포인트
3. 답변에 출처(파일·D-code·scope) 명시
4. 깊은 분석(SI/PI·플레인 분할 등)은 `gerber-pcb-analyst` 에이전트 호출
5. 인덱싱되지 않은 거버 폴더면 `/gerber-digest <폴더>` 등록 제안
EOF
        echo "    INDEX.md 헤더 작성"
    elif [ "$DRY_RUN" = "true" ] && [ ! -f "$DIR/INDEX.md" ]; then
        echo "    (dry-run) INDEX.md 헤더 작성 예정"
    elif [ -f "$DIR/INDEX.md" ]; then
        echo "    INDEX.md 이미 존재 — 보존"
    fi
}

echo "[3/5] gerbers 디렉토리 초기화"
if [ "$AGENT_ONLY" = "true" ]; then
    echo "  --agent-only: 디렉토리/INDEX.md 생성 건너뜀"
else
    case "${SCOPE:-project}" in
        project) init_gerbers_dir "$TARGET_PROJECT/.claude/gerbers" "project" ;;
        global)  init_gerbers_dir "$HOME/.claude/gerbers" "global" ;;
        both)    init_gerbers_dir "$TARGET_PROJECT/.claude/gerbers" "project"
                 init_gerbers_dir "$HOME/.claude/gerbers" "global" ;;
    esac
fi
```

### 4. CLAUDE.md 마커 블록 주입

`<!-- gerber-digest:start -->` ~ `<!-- gerber-digest:end -->` 마커로 감싼 가이드 블록을 주입한다. 마커가 이미 있으면 보존(--repair 시 갱신).

```bash
inject_marker() {
    local CLAUDE_MD="$1"; local LABEL="$2"
    case "$CLAUDE_MD" in ""|/CLAUDE.md|/.claude/*) echo "  ⚠️ $LABEL: 잘못된 CLAUDE.md 경로 '$CLAUDE_MD' (TARGET_PROJECT 미설정?) — 중단"; return 1 ;; esac
    local BLOCK
    BLOCK="$(cat <<'EOF'
<!-- gerber-digest:start -->
## 거버 다이제스트 사용 규칙

이 환경에는 보드 거버 세트가 다이제스트로 등록될 수 있다 (현재 0개) — 보드/거버 정보가 필요한 질문을 받으면:

1. `.claude/gerbers/INDEX.md` (project) + `~/.claude/gerbers/INDEX.md` (global) 양쪽 확인
2. 관련 보드의 `digest.md` 우선 참조 → 부족하면 `index.md` 파일/라인 포인터로 원본 거버 핀포인트(Read/Grep)
3. 답변에 출처(파일·D-code·scope) 명시
4. 깊은 분석(SI/PI·차동쌍·플레인 분할·제조성)은 `gerber-pcb-analyst` 에이전트 호출
5. 인덱싱되지 않은 거버 폴더면 `/gerber-digest <폴더>` 등록 제안

거버는 전부 텍스트 — MCP·gerbv 불필요, Read/Grep으로 파싱.
<!-- gerber-digest:end -->
EOF
    )"
    if [ ! -f "$CLAUDE_MD" ]; then
        [ "$DRY_RUN" = "true" ] && echo "  (dry-run) $LABEL CLAUDE.md 신규 생성 + 마커" || { echo "$BLOCK" > "$CLAUDE_MD"; echo "  $LABEL: CLAUDE.md 신규 생성 + 마커 주입"; }
        return
    fi
    # 백업은 '실제 쓰기'가 일어나는 분기(append/repair)에서만 생성 — no-op 재실행 시 .bak 누적 방지
    if grep -q "<!-- gerber-digest:start -->" "$CLAUDE_MD"; then
        if [ "$REPAIR" = "true" ]; then
            if ! grep -q "<!-- gerber-digest:end -->" "$CLAUDE_MD"; then
                # 고아 start 마커(end 누락=손상): awk 교체는 start 이후 전부를 삭제하므로 금지. 사용자 콘텐츠 보호.
                echo "  ⚠️  $LABEL: start 마커는 있으나 end 마커 없음(손상) — 자동 교체 생략(읽기 전용, 백업 미생성), 수동 확인 필요"
            elif [ "$DRY_RUN" = "true" ]; then
                echo "  (dry-run) $LABEL CLAUDE.md 마커 블록 갱신(--repair)"
            else
                cp "$CLAUDE_MD" "$CLAUDE_MD.bak.$(date +%Y%m%d-%H%M%S)"
                # start~end 사이를 새 BLOCK으로 교체 (마커 외부 보존). end 마커 존재는 위에서 보장.
                # BLOCK은 ENVIRON 경유 — awk -v의 백슬래시 escape 해석을 회피(경로/정규식 안전).
                BLOCK="$BLOCK" awk '
                    /<!-- gerber-digest:start -->/ {print ENVIRON["BLOCK"]; skip=1; next}
                    /<!-- gerber-digest:end -->/   {skip=0; next}
                    skip!=1 {print}
                ' "$CLAUDE_MD" > "$CLAUDE_MD.tmp" && mv "$CLAUDE_MD.tmp" "$CLAUDE_MD" || rm -f "$CLAUDE_MD.tmp"
                echo "  $LABEL: CLAUDE.md 마커 블록 갱신(--repair) (백업: $CLAUDE_MD.bak.*)"
            fi
        else
            echo "  $LABEL: CLAUDE.md 마커 이미 존재 — 보존 (갱신하려면 --repair)"
        fi
    else
        [ "$DRY_RUN" = "true" ] && echo "  (dry-run) $LABEL CLAUDE.md 끝에 마커 추가" || { cp "$CLAUDE_MD" "$CLAUDE_MD.bak.$(date +%Y%m%d-%H%M%S)"; printf '\n%s\n' "$BLOCK" >> "$CLAUDE_MD"; echo "  $LABEL: CLAUDE.md 끝에 마커 추가 (백업: $CLAUDE_MD.bak.*)"; }
    fi
}

echo "[4/5] CLAUDE.md 마커 블록 주입"
if [ "$AGENT_ONLY" != "true" ]; then
    case "${SCOPE:-project}" in
        project) inject_marker "$TARGET_PROJECT/CLAUDE.md" "project" ;;
        global)  inject_marker "$HOME/.claude/CLAUDE.md" "global" ;;
        both)    inject_marker "$TARGET_PROJECT/CLAUDE.md" "project"
                 inject_marker "$HOME/.claude/CLAUDE.md" "global" ;;
    esac
fi
```

### 5. 검증 + 상태 리포트

```bash
echo "[5/5] 검증"
if [ "$DRY_RUN" = "true" ]; then
    echo "  (dry-run) 실제 변경이 없으므로 검증 생략"
else
    [ "$SKIP_AGENT" != "true" ] && { [ -f "$TARGET_PROJECT/.claude/agents/gerber-pcb-analyst.md" ] && echo "  ✓ gerber-pcb-analyst 에이전트 설치됨" || echo "  ⚠️ 에이전트 미설치"; }
    if [ "$AGENT_ONLY" = "true" ]; then
        echo "  --agent-only: 디렉토리/INDEX.md 검증 생략"
    else
        case "${SCOPE:-project}" in
            project) { [ -f "$TARGET_PROJECT/.claude/gerbers/INDEX.md" ] && echo "  ✓ project INDEX.md 존재"; } || echo "  ⚠️ project INDEX.md 없음(디렉토리 초기화 실패?)" ;;
            global)  { [ -f "$HOME/.claude/gerbers/INDEX.md" ] && echo "  ✓ global INDEX.md 존재"; } || echo "  ⚠️ global INDEX.md 없음(디렉토리 초기화 실패?)" ;;
            both)    { [ -f "$TARGET_PROJECT/.claude/gerbers/INDEX.md" ] && echo "  ✓ project INDEX.md 존재"; } || echo "  ⚠️ project INDEX.md 없음"
                     { [ -f "$HOME/.claude/gerbers/INDEX.md" ] && echo "  ✓ global INDEX.md 존재"; } || echo "  ⚠️ global INDEX.md 없음" ;;
        esac
    fi
    if [ "$AGENT_ONLY" != "true" ]; then
        check_marker() {  # start·end 둘 다 있어야 정상 — 한쪽만 있으면 손상(비대칭)으로 보고
            local s e; grep -q "gerber-digest:start" "$1" 2>/dev/null && s=1; grep -q "gerber-digest:end" "$1" 2>/dev/null && e=1
            if [ "$s" = 1 ] && [ "$e" = 1 ]; then
                echo "  ✓ $2 CLAUDE.md 마커 주입됨"
            elif [ "$s" = 1 ] || [ "$e" = 1 ]; then
                echo "  ⚠️ $2 CLAUDE.md 마커 손상(start/end 비대칭) — /gerber-digest-setup --repair 또는 수동 확인"
            else
                echo "  ⚠️ $2 CLAUDE.md 마커 없음(주입 실패?) — /gerber-digest-setup --repair 또는 수동 확인"
            fi
        }
        case "${SCOPE:-project}" in
            project) check_marker "$TARGET_PROJECT/CLAUDE.md" "project" ;;
            global)  check_marker "$HOME/.claude/CLAUDE.md" "global" ;;
            both)    check_marker "$TARGET_PROJECT/CLAUDE.md" "project"; check_marker "$HOME/.claude/CLAUDE.md" "global" ;;
        esac
    fi
fi
```

상태 리포트:

```
셋업 완료

스코프: <project|global|both>
에이전트: <설치됨/이미있음/생략>
디렉토리: <생성됨/이미있음>
CLAUDE.md: <주입됨/이미있음>

다음 단계:
  ① (에이전트 신규 설치한 경우) Claude Code 재시작 → gerber-pcb-analyst 활성화
  ② /gerber-digest <거버 폴더>로 첫 보드 등록
  ③ /gerber-digest --list로 등록된 보드 확인

문제 해결:
  - 에이전트 미인식: Claude Code 재시작, 또는 /gerber-digest-setup --agent-only
  - CLAUDE.md 마커 손상: /gerber-digest-setup --repair
  - 권한 에러: 디렉토리 권한 확인 또는 --scope 변경
```

## Non-goals

- ❌ 거버 인제스트 — 메인 스킬(`/gerber-digest <폴더>`) 책임
- ❌ MCP 등록 — 거버 파싱은 MCP 불필요(텍스트 파싱)
- ❌ Claude Code 자동 재시작 — 안내만, 사용자 동의 필요
- ❌ 마커 블록 외부 CLAUDE.md 내용 수정 / 기존 에이전트 덮어쓰기

$ARGUMENTS
