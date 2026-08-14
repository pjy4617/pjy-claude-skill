#!/usr/bin/env bash
#
# Orca setup 훅 드라이런 — 임시 git worktree에서 실제로 실행해 본다.
#
# Orca의 실행 조건을 그대로 재현한다:
#   - 러너 스크립트 앞에 `set -e` 주입
#   - cwd = 새 워크트리 루트
#   - ORCA_WORKTREE_PATH / ORCA_ROOT_PATH / ORCA_WORKSPACE_NAME 주입
#   - 120초 타임아웃
#
# 사용법
#   dryrun_setup.sh [--repo PATH] [--hook setup|archive] [--script FILE]
#                   [--timeout SEC] [--keep] [--checker PATH]
#
#   --repo     대상 레포 (기본: 현재 디렉토리의 git 루트)
#   --hook     orca.yaml에서 뽑아 실행할 훅 (기본: setup)
#   --script   orca.yaml 대신 이 셸 스크립트 파일을 실행 (생성 전 초안 검증용)
#   --timeout  타임아웃 초 (기본 120 — Orca 실측값)
#   --keep     임시 워크트리를 지우지 않는다 (결과 확인용)
#   --checker  check_orca_yaml.py 경로 (기본: 이 스크립트 옆)
#
# 종료 코드: 0 정상 · 1 훅 실패 · 124 타임아웃 · 2 준비 실패
set -uo pipefail

REPO=""
HOOK="setup"
SCRIPT_FILE=""
TIMEOUT=120
KEEP=0
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER="$SELF_DIR/check_orca_yaml.py"

while [ $# -gt 0 ]; do
  case "$1" in
    --repo)    REPO="${2:-}"; shift 2 ;;
    --hook)    HOOK="${2:-}"; shift 2 ;;
    --script)  SCRIPT_FILE="${2:-}"; shift 2 ;;
    --timeout) TIMEOUT="${2:-}"; shift 2 ;;
    --checker) CHECKER="${2:-}"; shift 2 ;;
    --keep)    KEEP=1; shift ;;
    -h|--help) sed -n '2,25p' "$0"; exit 0 ;;
    *) echo "알 수 없는 인자: $1" >&2; exit 2 ;;
  esac
done

# ── 1. 레포 확정 ────────────────────────────────────────────────
if [ -z "$REPO" ]; then
  REPO="$(git rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [ -z "$REPO" ] || [ ! -d "$REPO/.git" ] && [ ! -f "$REPO/.git" ]; then
  echo "git 레포를 찾을 수 없다 (--repo 로 지정)" >&2
  exit 2
fi
REPO="$(cd "$REPO" && pwd)"

if ! git -C "$REPO" rev-parse HEAD >/dev/null 2>&1; then
  echo "커밋이 없는 레포다 — worktree를 만들 수 없다" >&2
  exit 2
fi

# ── 2. 실행할 본문 확보 ─────────────────────────────────────────
BODY="$(mktemp "${TMPDIR:-/tmp}/orca-hook-XXXXXX.sh")"
cleanup_body() { rm -f "$BODY" "$BODY.runner" 2>/dev/null || true; }
trap cleanup_body EXIT

if [ -n "$SCRIPT_FILE" ]; then
  [ -f "$SCRIPT_FILE" ] || { echo "스크립트 파일 없음: $SCRIPT_FILE" >&2; exit 2; }
  cat "$SCRIPT_FILE" > "$BODY"
  SOURCE_DESC="$SCRIPT_FILE"
else
  YAML="$REPO/orca.yaml"
  [ -f "$YAML" ] || YAML="$REPO/orca.yml"
  [ -f "$YAML" ] || { echo "orca.yaml 이 없다: $REPO" >&2; exit 2; }
  PY="$(command -v python3 || command -v python || true)"
  [ -n "$PY" ] || { echo "python3 가 필요하다 (훅 본문 추출)" >&2; exit 2; }
  [ -f "$CHECKER" ] || { echo "checker 를 찾을 수 없다: $CHECKER" >&2; exit 2; }
  if ! "$PY" "$CHECKER" extract "$YAML" --hook "$HOOK" > "$BODY"; then
    echo "scripts.$HOOK 추출 실패" >&2
    exit 2
  fi
  SOURCE_DESC="$YAML (scripts.$HOOK)"
fi

if [ ! -s "$BODY" ]; then
  echo "실행할 본문이 비어 있다" >&2
  exit 2
fi

# ── 3. 임시 워크트리 생성 ───────────────────────────────────────
WT="${TMPDIR:-/tmp}/orca-dryrun-$$-$(git -C "$REPO" rev-parse --short HEAD)"
NAME="orca-dryrun-$$"

remove_worktree() {
  if [ "$KEEP" -eq 1 ]; then
    echo "  · 워크트리 보존: $WT   (정리: git -C \"$REPO\" worktree remove --force \"$WT\")"
    return
  fi
  git -C "$REPO" worktree remove --force "$WT" >/dev/null 2>&1 \
    || rm -rf "$WT" 2>/dev/null
  git -C "$REPO" worktree prune >/dev/null 2>&1
}

echo "▶ Orca setup 훅 드라이런"
echo "  레포     : $REPO"
echo "  본문     : $SOURCE_DESC ($(wc -l < "$BODY")줄)"
echo "  워크트리 : $WT"
echo "  타임아웃 : ${TIMEOUT}초"
echo

if ! git -C "$REPO" worktree add --detach "$WT" HEAD >/dev/null 2>&1; then
  echo "임시 워크트리 생성 실패" >&2
  exit 2
fi
trap 'remove_worktree; cleanup_body' EXIT

# ── 4. Orca 러너 재현 (set -e 주입) ─────────────────────────────
RUNNER="$BODY.runner"
{
  echo "#!/usr/bin/env bash"
  echo "set -e   # ← Orca가 주입하는 줄. 훅이 해제하지 않으면 첫 실패에서 전부 중단된다."
  cat "$BODY"
} > "$RUNNER"
chmod +x "$RUNNER"

TIMEOUT_BIN="$(command -v timeout || true)"
START=$SECONDS
set +e
if [ -n "$TIMEOUT_BIN" ]; then
  ( cd "$WT" && \
    ORCA_WORKTREE_PATH="$WT" \
    ORCA_ROOT_PATH="$REPO" \
    ORCA_WORKSPACE_NAME="$NAME" \
    "$TIMEOUT_BIN" "$TIMEOUT" bash "$RUNNER" )
  RC=$?
else
  echo "  ! timeout 명령이 없다 — 시간 초과를 강제 중단하지 못한다"
  ( cd "$WT" && \
    ORCA_WORKTREE_PATH="$WT" \
    ORCA_ROOT_PATH="$REPO" \
    ORCA_WORKSPACE_NAME="$NAME" \
    bash "$RUNNER" )
  RC=$?
fi
set -o pipefail
ELAPSED=$((SECONDS - START))

# ── 5. 판정 ─────────────────────────────────────────────────────
echo
echo "▶ 결과"
echo "  종료코드 : $RC"
echo "  소요시간 : ${ELAPSED}초 / ${TIMEOUT}초 예산"

STATUS=0
if [ "$RC" -eq 124 ]; then
  echo "  판정     : ✗ 타임아웃 — Orca에서도 중단된다. 무거운 단계를 제거하라"
  STATUS=124
elif [ "$RC" -ne 0 ]; then
  echo "  판정     : ✗ 실패 (종료코드 $RC)"
  echo "             set -e 를 해제하지 않았다면 첫 실패 지점에서 나머지가 통째로 누락된 것이다"
  STATUS=1
elif [ "$ELAPSED" -ge $((TIMEOUT * 3 / 4)) ]; then
  echo "  판정     : ⚠ 통과했으나 예산의 75%를 넘겼다 — 느린 호스트/콜드 캐시에서는 초과한다"
else
  echo "  판정     : ✓ 통과"
fi

# 워크트리에 무엇이 생겼는지 (증거)
echo
echo "▶ 워크트리 변화 (git status)"
git -C "$WT" status --short 2>/dev/null | head -20
UNTRACKED_LINKS="$(find "$WT" -maxdepth 2 -type l 2>/dev/null | head -10)"
if [ -n "$UNTRACKED_LINKS" ]; then
  echo
  echo "▶ 생성된 심볼릭 링크"
  printf '%s\n' "$UNTRACKED_LINKS" | while read -r l; do
    echo "  $(basename "$l") → $(readlink "$l")"
  done
fi

# 멱등성 확인 — 같은 워크트리에서 한 번 더 돌려 실패하지 않는지 본다.
if [ "$RC" -eq 0 ]; then
  echo
  echo "▶ 멱등성 재실행"
  set +e
  ( cd "$WT" && \
    ORCA_WORKTREE_PATH="$WT" \
    ORCA_ROOT_PATH="$REPO" \
    ORCA_WORKSPACE_NAME="$NAME" \
    bash "$RUNNER" ) >/dev/null 2>&1
  RC2=$?
  set -o pipefail
  if [ "$RC2" -eq 0 ]; then
    echo "  ✓ 두 번째 실행도 성공 — 멱등"
  else
    echo "  ✗ 두 번째 실행 실패 (종료코드 $RC2) — 멱등하지 않다"
    echo "    이미 존재하는 파일/링크를 덮어쓰거나 중복 추가하는 단계가 있다"
    STATUS=1
  fi
fi

exit "$STATUS"
