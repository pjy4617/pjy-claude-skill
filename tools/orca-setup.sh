#!/usr/bin/env bash
#
# Orca 워크트리 setup 훅 — pjy-claude-skill (Claude Code 플러그인 마켓플레이스)
#
# 실행 시점 : 새 워크트리 생성 직후. cwd = 새 워크트리 루트.
# 호출 경로 : orca.yaml → scripts.setup → 이 스크립트
#
# 이 저장소는 빌드가 없는 **플러그인/문서 저장소**다. 따라서 setup 이 하는 일은 둘뿐이다.
#   1) git 이 따라오지 않는 비추적 로컬 자산을 메인 체크아웃에서 승계
#      (권한 allowlist·설치된 에이전트·다이제스트 산출물·프로젝트 메모리)
#   2) 작업 전제 점검 — python3 가용성과 마켓플레이스 JSON 유효성
#
# 설계 원칙
#   - 비파괴·멱등: 이미 있는 파일은 절대 덮어쓰지 않는다. 여러 번 실행해도 안전.
#   - 점검 실패는 경고만 남기고 워크트리 생성을 막지 않는다(항상 exit 0).
#   - 호스트 절대경로를 쓰지 않는다 — $ORCA_ROOT_PATH / $ORCA_WORKTREE_PATH 만 쓴다.
#   - 심볼릭 링크를 만들지 않는다(전체 승계량 1MB 미만) → archive 훅이 필요 없다.
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

# ORCA_ROOT_PATH 가 없으면 git 으로 메인 체크아웃을 역산한다.
# 링크된 워크트리에서 --git-common-dir 는 메인 저장소의 .git 을 가리킨다.
ROOT="${ORCA_ROOT_PATH:-}"
if [ -z "$ROOT" ]; then
  _common="$(git rev-parse --git-common-dir 2>/dev/null || true)"
  [ -n "$_common" ] && ROOT="$(cd "$(dirname "$_common")" && pwd 2>/dev/null || true)"
fi
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"

log "${C_BOLD}Orca setup — pjy-claude-skill${C_OFF}"
log "  워크트리 : $WT"
log "  브랜치   : $BRANCH${ORCA_WORKSPACE_NAME:+  (워크스페이스: $ORCA_WORKSPACE_NAME)}"
log "  메인     : ${ROOT:-<확인 불가>}"

# ──────────────────────────────────────────────────────────────
# 2. 비추적 로컬 자산 승계
#    .gitignore 로 무시되거나 미추적이라 새 워크트리에는 존재하지 않지만,
#    없으면 즉시 불편해지는 것들만 복사한다. 전부 합쳐 1MB 미만이라 링크가 아닌 복사.
# ──────────────────────────────────────────────────────────────
inherit() {   # inherit <상대경로> <설명>
  local rel="$1" desc="$2" src="$ROOT/$1" dst="$WT/$1"
  [ -n "$ROOT" ] || { skip "$rel (메인 경로 불명)"; return 0; }
  [ -e "$src" ]  || { skip "$rel (원본 없음)"; return 0; }
  if [ -e "$dst" ] || [ -L "$dst" ]; then skip "$rel (이미 있음)"; return 0; fi
  mkdir -p "$(dirname "$dst")" 2>/dev/null
  if cp -r "$src" "$dst" 2>/dev/null; then ok "$rel — $desc"; else warn "$rel 복사 실패"; fi
}

head2 "로컬 자산 승계"
# 권한 allowlist — 없으면 워크트리마다 같은 권한 프롬프트를 다시 받는다.
inherit ".claude/settings.local.json" "권한 allowlist"
# *-setup 스킬이 설치한 에이전트 복사본 — 없으면 서브에이전트 호출이 실패한다.
inherit ".claude/agents"              "설치된 에이전트"
inherit ".claude/agent-memory"        "에이전트 런타임 메모리"
# 다이제스트 산출물 — CLAUDE.md 의 조회 규칙이 이 경로를 전제한다.
inherit ".claude/manuals"             "매뉴얼 다이제스트"
inherit ".claude/pcb-designs"         "PCB 다이제스트"
inherit ".claude/atomized"            "원자 분할 문서"
# 프로젝트 메모리만 승계한다. .omc/sessions·plans 는 세션 국소 상태라 옮기지 않는다.
inherit ".omc/project-memory.json"    "프로젝트 메모리"

# ──────────────────────────────────────────────────────────────
# 3. 작업 전제 점검
#    이 저장소의 정본 검증 절차(CLAUDE.md)는 python3 로 JSON 유효성을 보는 것이다.
#    빌드가 없으므로 setup 이 확인할 것은 이 도구가 실제로 동작하는지 뿐이다.
# ──────────────────────────────────────────────────────────────
head2 "작업 전제"

PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import json" >/dev/null 2>&1; then PY="$c"; break; fi
done

if [ -z "$PY" ]; then
  warn "python3 없음 — marketplace.json/plugin.json 검증 명령을 쓸 수 없다"
  warn "  Windows 라면 python3 가 MS Store alias 일 수 있다 (exit 49) → 'py -3' 확인"
else
  ok "python ($PY)"

  if "$PY" -c "import json,sys; json.load(open('.claude-plugin/marketplace.json'))" 2>/dev/null; then
    ok "marketplace.json 파싱"
  else
    warn "marketplace.json 파싱 실패 — 체크아웃이 손상됐거나 편집 중인 상태다"
  fi

  # 모든 plugin.json 유효성 + marketplace 항목과의 정합성을 한 번에 본다.
  # 출력의 '!' 줄을 세어 마지막 요약의 경고 수에 합산한다.
  _out="$("$PY" - <<'PYEOF'
import json, os, sys

bad, missing, mismatch = [], [], []
try:
    mk = json.load(open('.claude-plugin/marketplace.json', encoding='utf-8'))
except Exception as e:
    print("  ! marketplace.json 읽기 실패: %s" % e)
    sys.exit(0)

for entry in mk.get('plugins', []):
    src = entry.get('source', '')
    path = os.path.join(src, 'plugin.json') if not src.startswith('./') else os.path.join(src[2:], 'plugin.json')
    if not os.path.isfile(path):
        missing.append(entry.get('name', src))
        continue
    try:
        pj = json.load(open(path, encoding='utf-8'))
    except Exception:
        bad.append(path)
        continue
    if pj.get('version') != entry.get('version'):
        mismatch.append("%s (plugin %s vs marketplace %s)" %
                        (entry.get('name'), pj.get('version'), entry.get('version')))

print("  ✓ 플러그인 %d개 등록" % len(mk.get('plugins', [])))
for p in bad:      print("  ! plugin.json 파싱 실패: %s" % p)
for m in missing:  print("  ! plugin.json 없음: %s" % m)
for m in mismatch: print("  ! 버전 불일치: %s" % m)
PYEOF
)"
  printf '%s\n' "$_out"
  _n="$(printf '%s\n' "$_out" | grep -c '^  !' || true)"
  WARN_COUNT=$((WARN_COUNT + _n))
fi

# ──────────────────────────────────────────────────────────────
# 4. 마무리 — 경고가 있어도 워크트리 생성은 막지 않는다
# ──────────────────────────────────────────────────────────────
log ""
if [ "$WARN_COUNT" -gt 0 ]; then
  log "${C_WARN}setup 완료 — 경고 ${WARN_COUNT}건${C_OFF} (작업은 가능하다)"
else
  log "${C_OK}setup 완료${C_OFF}"
fi
exit 0
