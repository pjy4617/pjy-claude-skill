#!/usr/bin/env bash
#
# Orca 워크트리 setup 훅 — {{REPO_NAME}}
#
# 실행 시점 : 새 워크트리 생성 직후. cwd = 새 워크트리 루트.
# 호출 경로 : orca.yaml → scripts.setup → 이 스크립트
#
# 설계 원칙
#   - 비파괴·멱등(idempotent): 이미 있는 파일은 절대 덮어쓰지 않는다. 여러 번 실행해도 안전.
#   - 점검 실패는 경고만 남기고 워크트리 생성을 막지 않는다(항상 exit 0).
#   - 하드코딩된 호스트 경로를 쓰지 않는다 — $ORCA_ROOT_PATH / $ORCA_WORKTREE_PATH 만 쓴다.
#   - 120초 예산: 의존성 설치·configure까지. 빌드·테스트는 넣지 않는다.
#
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# 0. 출력 헬퍼
# ──────────────────────────────────────────────────────────────
if [ -t 1 ]; then
  C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_DIM=$'\033[2m'; C_BOLD=$'\033[1m'; C_OFF=$'\033[0m'
else
  C_OK=''; C_WARN=''; C_DIM=''; C_BOLD=''; C_OFF=''
fi

WARN_COUNT=0
log()  { printf '%s\n' "$*"; }
ok()   { printf '  %s✓%s %s\n' "$C_OK" "$C_OFF" "$*"; }
skip() { printf '  %s·%s %s\n' "$C_DIM" "$C_OFF" "$*"; }
warn() { printf '  %s!%s %s\n' "$C_WARN" "$C_OFF" "$*"; WARN_COUNT=$((WARN_COUNT + 1)); }
head2(){ printf '\n%s%s%s\n' "$C_BOLD" "$*" "$C_OFF"; }

# ──────────────────────────────────────────────────────────────
# 1. 경로 확정
# ──────────────────────────────────────────────────────────────
WT="${ORCA_WORKTREE_PATH:-$PWD}"
cd "$WT" 2>/dev/null || { log "setup: 워크트리 경로 접근 실패: $WT"; exit 0; }

# ORCA_ROOT_PATH가 없으면 git으로 메인 체크아웃을 역산한다.
# 링크된 워크트리에서 --git-common-dir는 메인 저장소의 .git을 가리킨다.
ROOT="${ORCA_ROOT_PATH:-}"
if [ -z "$ROOT" ]; then
  _common="$(git rev-parse --git-common-dir 2>/dev/null || true)"
  [ -n "$_common" ] && ROOT="$(cd "$(dirname "$_common")" && pwd 2>/dev/null || true)"
fi
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"

log "${C_BOLD}Orca setup — {{REPO_NAME}}${C_OFF}"
log "  워크트리 : $WT"
log "  브랜치   : $BRANCH${ORCA_WORKSPACE_NAME:+  (워크스페이스: $ORCA_WORKSPACE_NAME)}"
log "  메인     : ${ROOT:-<확인 불가>}"

# ──────────────────────────────────────────────────────────────
# 2. 공용 헬퍼
# ──────────────────────────────────────────────────────────────

# 메인 체크아웃의 비추적 파일을 승계한다. 이미 있으면 건드리지 않는다.
inherit_file() {
  local rel="$1"
  [ -n "$ROOT" ] || { skip "$rel (메인 경로 불명)"; return 0; }
  [ -f "$ROOT/$rel" ] || { skip "$rel (원본 없음)"; return 0; }
  [ -e "$WT/$rel" ] && { skip "$rel (이미 있음)"; return 0; }
  mkdir -p "$(dirname "$WT/$rel")" 2>/dev/null
  cp "$ROOT/$rel" "$WT/$rel" 2>/dev/null && ok "$rel" || warn "$rel 복사 실패"
}

# 대용량 비추적 디렉토리는 복사하지 않고 메인 체크아웃을 가리킨다.
link_shared() {
  local rel="$1"
  [ -n "$ROOT" ] || return 0
  [ -e "$ROOT/$rel" ] || { skip "$rel (원본 없음)"; return 0; }
  [ -e "$WT/$rel" ] || [ -L "$WT/$rel" ] && { skip "$rel (이미 있음)"; return 0; }
  mkdir -p "$(dirname "$WT/$rel")" 2>/dev/null
  ln -s "$ROOT/$rel" "$WT/$rel" 2>/dev/null && ok "link $rel" || warn "link 실패: $rel"
}

# .gitignore의 `dir/` 패턴은 심볼릭 링크에 매칭되지 않는다(실측).
# 그대로 두면 워크트리마다 `?? <name>`이 떠서 diff를 가린다.
# info/exclude는 커밋되지 않는 로컬 파일이라 .gitignore를 건드리지 않는다.
hide_locally() {
  local excl
  excl="$(git rev-parse --git-path info/exclude 2>/dev/null || true)"
  [ -n "$excl" ] || return 0
  mkdir -p "$(dirname "$excl")" 2>/dev/null
  touch "$excl" 2>/dev/null
  [ -f "$excl" ] || return 0
  local pat
  for pat in "$@"; do
    grep -qxF "$pat" "$excl" 2>/dev/null || printf '%s\n' "$pat" >> "$excl"
  done
}

# ──────────────────────────────────────────────────────────────
# 3. 비추적 로컬 설정 승계
# ──────────────────────────────────────────────────────────────
head2 "로컬 설정 승계"
{{INHERIT_STEPS}}

# ──────────────────────────────────────────────────────────────
# 4. 공유 자산 링크
# ──────────────────────────────────────────────────────────────
{{LINK_STEPS}}

# ──────────────────────────────────────────────────────────────
# 5. 의존성 / configure
# ──────────────────────────────────────────────────────────────
head2 "의존성"
{{DEPENDENCY_STEPS}}

# ──────────────────────────────────────────────────────────────
# 6. 작업 전제 점검
# ──────────────────────────────────────────────────────────────
{{PRECHECK_STEPS}}

# ──────────────────────────────────────────────────────────────
# 7. 마무리 — 경고가 있어도 워크트리 생성은 막지 않는다
# ──────────────────────────────────────────────────────────────
if [ "$WARN_COUNT" -gt 0 ]; then
  log ""
  log "${C_WARN}setup 완료 — 경고 ${WARN_COUNT}건${C_OFF} (작업은 가능하다)"
else
  log ""
  log "${C_OK}setup 완료${C_OFF}"
fi
exit 0
