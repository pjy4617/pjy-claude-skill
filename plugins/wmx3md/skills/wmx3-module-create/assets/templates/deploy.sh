#!/bin/bash
# {{MODULE_NAME}} 모듈 배포 스크립트
# 빌드된 파일을 /opt/lmx/ 경로에 배포합니다.
#
# 사용법:
#   ./deploy.sh              # 릴리스 빌드 배포
#   ./deploy.sh debug        # 디버그 빌드 배포
#   ./deploy.sh --dry-run    # 실제 복사 없이 대상 확인만
#   ./deploy.sh --check      # 현재 배포 상태 확인
#   ./deploy.sh --rollback   # 마지막 백업으로 롤백

set -euo pipefail

# === 설정 ===
MODULE_NAME="{{MODULE_NAME}}"
MODULE_NAME_LOWER="{{module_name}}"
MODULE_NAME_SNAKE="{{module_name_snake}}"
LMX_ROOT="${LMX_INSTALL_PATH:-/opt/lmx}"
BUILD_TYPE="${1:-release}"
DRY_RUN=false
CHECK_ONLY=false
ROLLBACK=false

# === 인자 처리 ===
case "${1:-}" in
    --dry-run)   DRY_RUN=true; BUILD_TYPE="release" ;;
    --check)     CHECK_ONLY=true ;;
    --rollback)  ROLLBACK=true ;;
    debug)       BUILD_TYPE="debug" ;;
    release)     BUILD_TYPE="release" ;;
    "")          BUILD_TYPE="release" ;;
    *)           echo "사용법: $0 [release|debug|--dry-run|--check|--rollback]"; exit 1 ;;
esac

# === 경로 설정 ===
INCLUDE_DIR="${LMX_ROOT}/include"
LIB_DIR="${LMX_ROOT}/lib"
MOTION_DIR="${LMX_ROOT}/motion"
BACKUP_DIR="backup"

# 공개 헤더 목록
HEADERS=(
    "include/${MODULE_NAME}Api.h"
    "include/${MODULE_NAME}ApiDef.h"
)

# 필수 심볼 목록
REQUIRED_SYMBOLS=("Motion_ModuleId" "Motion_ModuleInfo" "Motion_Setup" "Motion_Init" "Motion_Cleanup" "Motion_Process")

# === 빌드 출력 경로 결정 ===
find_build_outputs() {
    if [ -d "build/linux-${BUILD_TYPE}" ]; then
        SO_SOURCE="build/linux-${BUILD_TYPE}/${MODULE_NAME}/${MODULE_NAME_SNAKE}.so"
        LIB_SOURCE="build/linux-${BUILD_TYPE}/${MODULE_NAME}Api/lib${MODULE_NAME_LOWER}api.a"
    elif [ -d "releasefiles" ]; then
        SO_SOURCE="releasefiles/so/${MODULE_NAME_SNAKE}.so"
        LIB_SOURCE="releasefiles/lib/lib${MODULE_NAME_LOWER}api.a"
    else
        echo "ERROR: 빌드 출력을 찾을 수 없습니다. 먼저 빌드를 실행하세요."
        echo "  cmake --preset linux-${BUILD_TYPE} && cmake --build --preset linux-${BUILD_TYPE}"
        exit 1
    fi
}

# === 상태 확인 모드 ===
if [ "$CHECK_ONLY" = true ]; then
    echo "=== ${MODULE_NAME} 배포 상태 확인 ==="
    echo ""
    echo "[헤더] ${INCLUDE_DIR}/"
    for h in "${HEADERS[@]}"; do
        target="${INCLUDE_DIR}/$(basename "$h")"
        if [ -f "$target" ]; then
            mod_time=$(stat -c '%Y' "$target" | xargs -I{} date -d @{} '+%Y-%m-%d %H:%M')
            echo "  OK  $(basename "$h")  (${mod_time})"
        else
            echo "  --  $(basename "$h")  (미배포)"
        fi
    done
    echo ""
    echo "[라이브러리] ${LIB_DIR}/"
    target="${LIB_DIR}/lib${MODULE_NAME_LOWER}api.a"
    if [ -f "$target" ]; then
        echo "  OK  lib${MODULE_NAME_LOWER}api.a  ($(stat -c '%s' "$target") bytes)"
    else
        echo "  --  lib${MODULE_NAME_LOWER}api.a  (미배포)"
    fi
    echo ""
    echo "[모듈] ${MOTION_DIR}/"
    target="${MOTION_DIR}/${MODULE_NAME_SNAKE}.so"
    if [ -f "$target" ]; then
        sym_count=$(nm -D "$target" 2>/dev/null | grep -c 'Motion_' || true)
        echo "  OK  ${MODULE_NAME_SNAKE}.so  ($(stat -c '%s' "$target") bytes, ${sym_count}개 Motion_ 심볼)"
    else
        echo "  --  ${MODULE_NAME_SNAKE}.so  (미배포)"
    fi
    echo ""
    echo "[백업] ${BACKUP_DIR}/"
    if [ -d "$BACKUP_DIR" ]; then
        latest=$(ls -td "${BACKUP_DIR}"/*/ 2>/dev/null | head -1)
        if [ -n "$latest" ]; then
            echo "  최신 백업: ${latest}"
        else
            echo "  백업 없음"
        fi
    else
        echo "  백업 디렉토리 없음"
    fi
    exit 0
fi

# === 롤백 모드 ===
if [ "$ROLLBACK" = true ]; then
    latest=$(ls -td "${BACKUP_DIR}"/*/ 2>/dev/null | head -1)
    if [ -z "$latest" ]; then
        echo "ERROR: 롤백할 백업이 없습니다."
        exit 1
    fi
    echo "=== ${MODULE_NAME} 롤백 ==="
    echo "백업 원본: ${latest}"
    echo ""
    for f in "${latest}"*; do
        bn=$(basename "$f")
        case "$bn" in
            *.so)  dest="${MOTION_DIR}/${bn}" ;;
            *.a)   dest="${LIB_DIR}/${bn}" ;;
            *.h)   dest="${INCLUDE_DIR}/${bn}" ;;
            *)     continue ;;
        esac
        echo "  복원: ${bn} → ${dest}"
        sudo cp -v "$f" "$dest"
    done
    echo ""
    echo "=== 롤백 완료 ==="
    exit 0
fi

# === 배포 모드 ===
find_build_outputs

echo "=== ${MODULE_NAME} 배포 (${BUILD_TYPE}) ==="
echo ""

# 소스 파일 존재 확인
ERRORS=0
if [ ! -f "$SO_SOURCE" ]; then
    echo "ERROR: ${SO_SOURCE} 없음"
    ERRORS=$((ERRORS + 1))
fi
if [ ! -f "$LIB_SOURCE" ]; then
    echo "ERROR: ${LIB_SOURCE} 없음"
    ERRORS=$((ERRORS + 1))
fi
for h in "${HEADERS[@]}"; do
    if [ ! -f "$h" ]; then
        echo "ERROR: ${h} 없음"
        ERRORS=$((ERRORS + 1))
    fi
done
for dir in "$INCLUDE_DIR" "$LIB_DIR" "$MOTION_DIR"; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: ${dir} 디렉토리 없음"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -gt 0 ]; then
    echo "${ERRORS}개 오류. 배포 중단."
    exit 1
fi

# 심볼 검증
echo "[검증] .so 심볼 확인..."
for sym in "${REQUIRED_SYMBOLS[@]}"; do
    if nm -D "$SO_SOURCE" 2>/dev/null | grep -q "$sym"; then
        echo "  OK  ${sym}"
    else
        echo "  WARN  ${sym} 심볼 없음"
    fi
done
echo ""

# 배포 함수
deploy_file() {
    local src="$1"
    local dst="$2"
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY] ${src} → ${dst}"
    else
        sudo cp -v "$src" "$dst"
    fi
}

# 백업 (dry-run 아닌 경우)
if [ "$DRY_RUN" = false ]; then
    STAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DEST="${BACKUP_DIR}/${STAMP}"
    mkdir -p "$BACKUP_DEST"
    echo "[백업] → ${BACKUP_DEST}/"
    cp "${MOTION_DIR}/${MODULE_NAME_SNAKE}.so" "$BACKUP_DEST/" 2>/dev/null || true
    cp "${LIB_DIR}/lib${MODULE_NAME_LOWER}api.a" "$BACKUP_DEST/" 2>/dev/null || true
    for h in "${HEADERS[@]}"; do
        cp "${INCLUDE_DIR}/$(basename "$h")" "$BACKUP_DEST/" 2>/dev/null || true
    done
    echo ""
fi

# 배포 실행
echo "[헤더 배포] → ${INCLUDE_DIR}/"
for h in "${HEADERS[@]}"; do
    deploy_file "$h" "${INCLUDE_DIR}/$(basename "$h")"
done

echo ""
echo "[라이브러리 배포] → ${LIB_DIR}/"
deploy_file "$LIB_SOURCE" "${LIB_DIR}/lib${MODULE_NAME_LOWER}api.a"

echo ""
echo "[모듈 배포] → ${MOTION_DIR}/"
deploy_file "$SO_SOURCE" "${MOTION_DIR}/${MODULE_NAME_SNAKE}.so"

echo ""
if [ "$DRY_RUN" = true ]; then
    echo "=== DRY-RUN 완료. 실제 배포: $0 ${BUILD_TYPE} ==="
else
    echo "=== ${MODULE_NAME} 배포 완료 ==="
    echo ""
    echo "배포된 파일:"
    ls -lh "${INCLUDE_DIR}/${MODULE_NAME}Api.h" \
           "${INCLUDE_DIR}/${MODULE_NAME}ApiDef.h" \
           "${LIB_DIR}/lib${MODULE_NAME_LOWER}api.a" \
           "${MOTION_DIR}/${MODULE_NAME_SNAKE}.so" 2>/dev/null
    echo ""
    echo "WMX3 엔진을 재시작하면 새 모듈이 로딩됩니다."
    echo "롤백하려면: $0 --rollback"
fi
