#!/usr/bin/env bash
#
# Orca 프로젝트 설정 점검 — 읽기 전용.
#
# 이 레포가 Orca에서 "새 워크트리를 만들면 바로 작업 가능한" 상태로 설정돼 있는지
# 세 축으로 확인한다.
#   A. Orca 등록 상태   — repo 등록 여부, 기본 base ref, 워크트리 base path, 프로젝트 호스트 setup
#   B. 레포 내 설정      — orca.yaml 존재/키 구성, 훅 위임 스크립트, 커밋 여부
#   C. 레포 특성 대비 갭 — 탐지된 빌드 시스템·비추적 필수 파일이 setup 훅에 반영됐는가
#
# 아무것도 바꾸지 않는다. Orca 런타임이 꺼져 있어도 B·C는 동작한다.
#
# 사용법: check_orca_project.sh [--repo PATH] [--json]
set -uo pipefail

REPO=""
AS_JSON=0
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --json) AS_JSON=1; shift ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "알 수 없는 인자: $1" >&2; exit 2 ;;
  esac
done

[ -n "$REPO" ] || REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
REPO="$(cd "$REPO" 2>/dev/null && pwd)" || { echo "경로 접근 실패" >&2; exit 2; }

FINDINGS=()   # "SEVERITY|CODE|메시지|조치"
add() { FINDINGS+=("$1|$2|$3|${4:-}"); }

# ── Orca CLI 해석 ───────────────────────────────────────────────
# 리눅스에서 bare `orca` 는 GNOME Orca 스크린리더로 잡힐 수 있다. orca-cli 스킬의
# 해석 순서를 그대로 따른다: ORCA_CLI_COMMAND → orca-dev → orca-ide → orca
ORCA=""
if [ -n "${ORCA_CLI_COMMAND:-}" ]; then
  ORCA="$ORCA_CLI_COMMAND"
elif [ -n "${ORCA_DEV_REPO_ROOT:-}" ] && command -v orca-dev >/dev/null 2>&1; then
  ORCA="orca-dev"
elif [ "$(uname -s 2>/dev/null)" = "Linux" ] && command -v orca-ide >/dev/null 2>&1; then
  ORCA="orca-ide"
elif command -v orca >/dev/null 2>&1; then
  # 스크린리더 오인 방지 — CLI 헬프 시그니처를 확인한 뒤에만 채택한다.
  if orca --help 2>&1 | grep -q "Usage: orca <command>"; then
    ORCA="orca"
  fi
fi

ORCA_LIVE=0
if [ -n "$ORCA" ]; then
  if "$ORCA" status --json >/dev/null 2>&1; then ORCA_LIVE=1; fi
fi

# ── A. Orca 등록 상태 ───────────────────────────────────────────
# 필드명은 `orca repo show --json` 실측 기준:
#   worktreeBaseRef · worktreeBasePath · hookSettings{mode,setupRunPolicy,
#   commandSourcePolicy,scripts{setup,archive}}
REPO_REGISTERED="unknown"
REPO_BASE_REF=""; REPO_WT_BASE=""
HOOK_MODE=""; SETUP_RUN_POLICY=""; CMD_SOURCE_POLICY=""
LOCAL_SETUP_LEN=0; LOCAL_ARCHIVE_LEN=0
PY="$(command -v python3 || command -v python || true)"

if [ "$ORCA_LIVE" -eq 1 ]; then
  SHOW="$("$ORCA" repo show --repo "path:$REPO" --json 2>/dev/null)"
  if [ -n "$SHOW" ] && [ -n "$PY" ]; then
    ASSIGN="$(printf '%s' "$SHOW" | "$PY" -c '
import json, shlex, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
r = (d.get("result") or {}).get("repo") or {}
if not r:
    sys.exit(0)
h = r.get("hookSettings") or {}
s = h.get("scripts") or {}
def emit(k, v):
    print("%s=%s" % (k, shlex.quote(str(v if v is not None else ""))))
emit("REPO_REGISTERED", "yes")
emit("REPO_BASE_REF", r.get("worktreeBaseRef") or "")
emit("REPO_WT_BASE", r.get("worktreeBasePath") or "")
emit("HOOK_MODE", h.get("mode") or "")
emit("SETUP_RUN_POLICY", h.get("setupRunPolicy") or "")
emit("CMD_SOURCE_POLICY", h.get("commandSourcePolicy") or "")
emit("LOCAL_SETUP_LEN", len((s.get("setup") or "").strip()))
emit("LOCAL_ARCHIVE_LEN", len((s.get("archive") or "").strip()))
' 2>/dev/null)"
    [ -n "$ASSIGN" ] && eval "$ASSIGN"
  elif [ -n "$SHOW" ]; then
    # python 이 없을 때의 축소 폴백
    printf '%s' "$SHOW" | grep -q '"path"' && REPO_REGISTERED="yes"
    REPO_BASE_REF="$(printf '%s' "$SHOW" | grep -oE '"worktreeBaseRef"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"//; s/"$//')"
  fi

  if [ "$REPO_REGISTERED" = "yes" ]; then
    [ -n "$REPO_BASE_REF" ] || add MAJOR NO_BASE_REF \
      "Orca에 기본 base ref가 설정돼 있지 않다 — 새 워크트리가 의도치 않은 브랜치에서 갈라질 수 있다" \
      "$ORCA repo set-base-ref --repo path:$REPO --ref <기본브랜치>"
    if [ "${LOCAL_SETUP_LEN:-0}" -gt 0 ] || [ "${LOCAL_ARCHIVE_LEN:-0}" -gt 0 ]; then
      add MINOR LOCAL_HOOK_ONLY \
        "Orca 로컬 훅(Settings→General→Worktree hooks)에 스크립트가 있다 — 이 호스트에만 남고 팀에 공유되지 않는다" \
        "팀 표준이면 orca.yaml 의 scripts 로 옮긴다"
    fi
    case "$SETUP_RUN_POLICY" in
      ""|run-by-default) : ;;
      *) add INFO SETUP_POLICY \
           "setupRunPolicy=$SETUP_RUN_POLICY — setup 훅이 기본 실행되지 않는 설정이다" \
           "의도한 것이 아니면 Orca 레포 설정에서 되돌리거나 --setup run 으로 강제한다" ;;
    esac
  else
    REPO_REGISTERED="no"
    add MAJOR REPO_NOT_REGISTERED \
      "이 레포가 Orca에 등록돼 있지 않다 — Orca에서 워크트리를 만들 수 없다" \
      "$ORCA repo add --path $REPO"
  fi
else
  add INFO ORCA_OFFLINE \
    "Orca 런타임에 접속할 수 없어 등록 상태(A)를 확인하지 못했다" \
    "Orca 앱을 실행한 뒤 다시 점검한다 (${ORCA:-orca CLI 미탐지})"
fi

# ── B. 레포 내 설정 ─────────────────────────────────────────────
YAML=""
for cand in "$REPO/orca.yaml" "$REPO/orca.yml"; do
  [ -f "$cand" ] && { YAML="$cand"; break; }
done

HAS_SETUP=0; HAS_ARCHIVE=0; HAS_TABS=0; HAS_ISSUE=0; HAS_RECIPES=0
SETUP_BODY=""
if [ -n "$YAML" ]; then
  grep -qE '^\s+setup\s*:'   "$YAML" && HAS_SETUP=1
  grep -qE '^\s+archive\s*:' "$YAML" && HAS_ARCHIVE=1
  grep -qE '^defaultTabs\s*:'        "$YAML" && HAS_TABS=1
  grep -qE '^issueCommand\s*:'       "$YAML" && HAS_ISSUE=1
  grep -qE '^environmentRecipes\s*:' "$YAML" && HAS_RECIPES=1

  [ "$HAS_SETUP" -eq 1 ] || add MAJOR NO_SETUP_HOOK \
    "orca.yaml은 있으나 scripts.setup 훅이 없다" "setup 훅을 추가한다 (/orca-setup-build)"

  # 커밋되어야 팀 전체에 공유된다. 미추적이면 본인 호스트에서만 동작한다.
  if git -C "$REPO" rev-parse HEAD >/dev/null 2>&1; then
    if ! git -C "$REPO" ls-files --error-unmatch "$(basename "$YAML")" >/dev/null 2>&1; then
      add MAJOR YAML_UNTRACKED \
        "orca.yaml이 git에 추적되지 않는다 — 팀원에게 공유되지 않고 본인 호스트에서만 동작한다" \
        "git add $(basename "$YAML") 후 커밋한다"
    fi
    if git -C "$REPO" check-ignore -q "$YAML" 2>/dev/null; then
      add CRITICAL YAML_IGNORED "orca.yaml이 .gitignore로 무시되고 있다" ".gitignore에서 제외한다"
    fi
  fi

  # 훅이 별도 스크립트에 위임한다면 그 파일이 실제로 있어야 한다.
  DELEGATE="$(grep -oE '(bash|sh|source|\.)\s+[^ "]*orca[-_]setup[^ "]*\.sh' "$YAML" | head -1 | awk '{print $2}')"
  if [ -n "$DELEGATE" ]; then
    if [ ! -f "$REPO/$DELEGATE" ]; then
      add CRITICAL DELEGATE_MISSING \
        "훅이 $DELEGATE 를 호출하는데 그 파일이 없다 — 워크트리 생성 때마다 실패한다" \
        "스크립트를 추가하거나 호출을 제거한다"
    elif ! git -C "$REPO" ls-files --error-unmatch "$DELEGATE" >/dev/null 2>&1; then
      add CRITICAL DELEGATE_UNTRACKED \
        "$DELEGATE 가 git에 추적되지 않는다 — 새 워크트리에는 그 파일이 존재하지 않아 훅이 실패한다" \
        "git add $DELEGATE"
    fi
  fi

  PY="$(command -v python3 || command -v python || true)"
  CHECKER="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../orca-setup-build/assets" 2>/dev/null && pwd)/check_orca_yaml.py"
  if [ -n "$PY" ] && [ -f "$CHECKER" ]; then
    SETUP_BODY="$("$PY" "$CHECKER" extract "$YAML" --hook setup 2>/dev/null || true)"
  fi
  [ -n "$SETUP_BODY" ] || SETUP_BODY="$(cat "$YAML")"   # 폴백: 전체 텍스트로 갭 판정

  # 훅이 외부 스크립트에 위임하면 실제 로직은 그 파일에 있다. 합쳐야 갭 판정이 맞다.
  if [ -n "$DELEGATE" ] && [ -f "$REPO/$DELEGATE" ]; then
    SETUP_BODY="$SETUP_BODY
$(cat "$REPO/$DELEGATE")"
  fi
else
  add MAJOR NO_ORCA_YAML \
    "orca.yaml이 없다 — 새 워크트리는 git이 추적하는 파일만 가진 맨 상태로 생성된다" \
    "/orca-setup-build 로 setup 훅을 만든다"
fi

# ── C. 레포 특성 대비 갭 ────────────────────────────────────────
# 탐지된 생태계가 setup 훅에서 다뤄지는지 본다. 다루지 않으면 새 워크트리에서
# 의존성이 없어 첫 명령이 실패한다.
ECOS=()
# 템플릿·예제·픽스처 경로의 마커는 그 레포의 실제 빌드 대상이 아니다
# (예: 스킬이 배포하는 CMakePresets.json 템플릿). 갭 등급을 INFO로 낮춘다.
NON_BUILD_RE='(^|/)(templates?|fixtures?|testdata|__fixtures__|examples?|samples?)/'

check_eco() {  # 마커파일 필요패턴 라벨 조치
  local marker="$1" pattern="$2" label="$3" fix="$4"
  local all real found sev
  all="$(cd "$REPO" && git ls-files --cached -- "$marker" "*/$marker" 2>/dev/null)"
  [ -n "$all" ] || return 0
  real="$(printf '%s\n' "$all" | grep -vE "$NON_BUILD_RE" | head -1)"
  if [ -n "$real" ]; then
    found="$real"; sev="MAJOR"
  else
    found="$(printf '%s\n' "$all" | head -1)"; sev="INFO"
  fi
  ECOS+=("$label ($found)")
  if [ -z "$SETUP_BODY" ] || ! printf '%s' "$SETUP_BODY" | grep -qE "$pattern"; then
    if [ "$sev" = "MAJOR" ]; then
      add MAJOR "GAP_${label}" \
        "$label 프로젝트($found)인데 setup 훅에 해당 준비 단계가 없다 — 새 워크트리에서 의존성이 비어 있다" \
        "$fix"
    else
      add INFO "GAP_${label}" \
        "$label 마커가 템플릿/예제 경로에만 있다($found) — 이 레포의 빌드 대상이 아니면 무시해도 된다" \
        "실제 빌드 대상이면 setup 훅에 추가한다"
    fi
  fi
}

check_eco "pnpm-lock.yaml"    'pnpm'                    "pnpm"    "setup에 pnpm install --frozen-lockfile 추가"
check_eco "yarn.lock"         'yarn'                    "yarn"    "setup에 yarn install --frozen-lockfile 추가"
check_eco "bun.lockb"         'bun'                     "bun"     "setup에 bun install 추가"
check_eco "package-lock.json" '\bnpm\b'                 "npm"     "setup에 npm ci 추가"
check_eco "Cargo.lock"        'cargo'                   "cargo"   "setup에 cargo fetch 추가 (build는 예산 초과 위험)"
check_eco "go.sum"            '\bgo\b'                  "go"      "setup에 go mod download 추가"
check_eco "uv.lock"           '\buv\b'                  "uv"      "setup에 uv sync 추가"
check_eco "poetry.lock"       'poetry'                  "poetry"  "setup에 poetry install 추가"
check_eco "requirements.txt"  'pip|requirements'        "pip"     "setup에 가상환경 생성 + pip install -r 추가"
check_eco "CMakePresets.json" 'cmake'                   "cmake"   "setup에 cmake --preset <preset> (configure만) 추가"
check_eco "*.sln"             'dotnet|nuget'            "dotnet"  "setup에 dotnet restore 추가"
check_eco "gradlew"           'gradle'                  "gradle"  "setup은 무겁다 — 캐시 링크만 검토"

# 새 워크트리에 따라오지 않는 로컬 설정 — 있으면 승계 대상 후보다.
LOCAL_ASSETS=()
check_local() {  # 경로 패턴 라벨
  local p="$1" pattern="$2" label="$3"
  [ -e "$REPO/$p" ] || return 0
  git -C "$REPO" ls-files --error-unmatch "$p" >/dev/null 2>&1 && return 0   # 추적 중이면 따라온다
  LOCAL_ASSETS+=("$p")
  if [ -z "$SETUP_BODY" ] || ! printf '%s' "$SETUP_BODY" | grep -qE "$pattern"; then
    add MINOR "GAP_LOCAL_$label" \
      "$p 는 비추적이라 새 워크트리에 없다 — setup 훅이 승계하지 않는다" \
      "메인 체크아웃(\$ORCA_ROOT_PATH)에서 복사하거나 링크한다"
  fi
}
check_local ".claude/settings.local.json" 'settings\.local\.json' "CLAUDE_SETTINGS"
check_local ".serena"                     '\.serena'              "SERENA"
check_local ".env"                        '\.env'                 "ENV"
check_local ".env.local"                  '\.env'                 "ENV_LOCAL"
check_local ".venv"                       '\.venv'                "VENV"

# 대용량 비추적 디렉토리 — 워크트리마다 복사하면 디스크가 폭발한다. 링크 후보.
BIG_DIRS=""
while IFS= read -r d; do
  [ -n "$d" ] || continue
  sz="$(du -sm "$REPO/$d" 2>/dev/null | cut -f1)"
  [ -n "$sz" ] || continue
  if [ "$sz" -ge 100 ]; then
    BIG_DIRS="$BIG_DIRS $d(${sz}M)"
    if [ -z "$SETUP_BODY" ] || ! printf '%s' "$SETUP_BODY" | grep -qF "$d"; then
      add MINOR GAP_BIG_DIR \
        "$d 가 ${sz}MB 비추적 디렉토리인데 setup 훅이 다루지 않는다" \
        "작업에 필요하면 복사 대신 심볼릭 링크로 메인 체크아웃을 가리킨다"
    fi
  fi
done < <(cd "$REPO" && find . -maxdepth 2 -type d -name '.*' -prune -o -maxdepth 2 -type d -print 2>/dev/null \
          | sed 's|^\./||' | grep -vE '^\.$|^\.git' \
          | while read -r c; do git -C "$REPO" check-ignore -q "$c" 2>/dev/null && echo "$c"; done | head -20)

# ── 출력 ────────────────────────────────────────────────────────
crit=0; major=0; minor=0; info=0
for f in "${FINDINGS[@]:-}"; do
  case "${f%%|*}" in
    CRITICAL) crit=$((crit+1)) ;; MAJOR) major=$((major+1)) ;;
    MINOR) minor=$((minor+1)) ;; INFO) info=$((info+1)) ;;
  esac
done

if [ "$AS_JSON" -eq 1 ]; then
  printf '{\n'
  printf '  "repo": "%s",\n' "$REPO"
  printf '  "orcaCli": "%s",\n  "orcaLive": %s,\n' "${ORCA:-}" "$([ "$ORCA_LIVE" -eq 1 ] && echo true || echo false)"
  printf '  "registered": "%s",\n  "baseRef": "%s",\n  "worktreeBasePath": "%s",\n' "$REPO_REGISTERED" "$REPO_BASE_REF" "$REPO_WT_BASE"
  printf '  "orcaYaml": "%s",\n' "${YAML:-}"
  printf '  "keys": {"scripts.setup": %s, "scripts.archive": %s, "defaultTabs": %s, "issueCommand": %s, "environmentRecipes": %s},\n' \
    "$([ $HAS_SETUP -eq 1 ] && echo true || echo false)" "$([ $HAS_ARCHIVE -eq 1 ] && echo true || echo false)" \
    "$([ $HAS_TABS -eq 1 ] && echo true || echo false)" "$([ $HAS_ISSUE -eq 1 ] && echo true || echo false)" \
    "$([ $HAS_RECIPES -eq 1 ] && echo true || echo false)"
  printf '  "counts": {"CRITICAL": %d, "MAJOR": %d, "MINOR": %d, "INFO": %d},\n' "$crit" "$major" "$minor" "$info"
  printf '  "findings": [\n'
  first=1
  for f in "${FINDINGS[@]:-}"; do
    [ -n "$f" ] || continue
    IFS='|' read -r sev code msg fix <<< "$f"
    [ $first -eq 1 ] || printf ',\n'; first=0
    printf '    {"severity": "%s", "code": "%s", "message": "%s", "fix": "%s"}' \
      "$sev" "$code" "$(printf '%s' "$msg" | sed 's/"/\\"/g')" "$(printf '%s' "$fix" | sed 's/"/\\"/g')"
  done
  printf '\n  ]\n}\n'
  exit 0
fi

echo "▶ Orca 프로젝트 설정 점검"
echo "  레포        : $REPO"
echo "  Orca CLI    : ${ORCA:-<미탐지>}  (런타임 $([ "$ORCA_LIVE" -eq 1 ] && echo 접속됨 || echo 접속불가))"
echo
echo "A. Orca 등록 상태"
echo "   등록          : $REPO_REGISTERED"
if [ "$REPO_REGISTERED" = "yes" ]; then
  echo "   기본 base ref : ${REPO_BASE_REF:-<미설정>}"
  echo "   워크트리 base : ${REPO_WT_BASE:-<기본값>}"
  echo "   훅 모드       : ${HOOK_MODE:-?} / setupRunPolicy=${SETUP_RUN_POLICY:-?} / commandSource=${CMD_SOURCE_POLICY:-?}"
  echo "   Orca 로컬 훅  : setup ${LOCAL_SETUP_LEN:-0}자 · archive ${LOCAL_ARCHIVE_LEN:-0}자 (호스트 전용)"
else
  # 등록되지 않았거나 확인 불가 — 아래 항목은 알 수 없다. 0/기본값으로 보이지 않게 감춘다.
  echo "   (레포 설정 항목은 등록 확인 후에만 조회된다)"
fi
echo
echo "B. 레포 내 설정"
echo "   orca.yaml     : ${YAML:-<없음>}"
echo "   scripts.setup : $([ $HAS_SETUP -eq 1 ] && echo 있음 || echo 없음)"
echo "   scripts.archive: $([ $HAS_ARCHIVE -eq 1 ] && echo 있음 || echo 없음)"
echo "   defaultTabs   : $([ $HAS_TABS -eq 1 ] && echo 있음 || echo 없음)"
echo "   issueCommand  : $([ $HAS_ISSUE -eq 1 ] && echo 있음 || echo 없음)"
echo "   environmentRecipes: $([ $HAS_RECIPES -eq 1 ] && echo 있음 || echo 없음)"
echo
echo "C. 레포 특성"
echo "   탐지된 생태계 : ${ECOS[*]:-<없음>}"
echo "   비추적 로컬설정: ${LOCAL_ASSETS[*]:-<없음>}"
echo "   대용량 비추적 : ${BIG_DIRS:-<없음>}"
echo
echo "▶ 지적 사항"
if [ "${#FINDINGS[@]}" -eq 0 ]; then
  echo "   없음 — 설정이 레포 특성에 맞게 갖춰져 있다."
else
  for sev in CRITICAL MAJOR MINOR INFO; do
    for f in "${FINDINGS[@]:-}"; do
      [ -n "$f" ] || continue
      IFS='|' read -r s code msg fix <<< "$f"
      [ "$s" = "$sev" ] || continue
      echo "   [$s] $code: $msg"
      [ -n "$fix" ] && echo "          → $fix"
    done
  done
fi
echo
echo "요약: CRITICAL $crit · MAJOR $major · MINOR $minor · INFO $info"

[ "$crit" -gt 0 ] && exit 1
exit 0
