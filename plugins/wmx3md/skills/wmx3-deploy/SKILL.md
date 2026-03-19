---
name: wmx3-deploy
description: "WMX3 모듈 배포 스크립트 생성 및 실행. 빌드된 .so/.a 파일과 헤더를 /opt/lmx/ 경로에 배포합니다. '배포', 'deploy', '설치', 'install', '배포 스크립트', 'lmx에 복사', '모듈 배포해줘' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[프리셋명 또는 --dry-run]"
---

# WMX3 모듈 배포

> 빌드된 모듈을 WMX3 런타임 경로(`/opt/lmx/`)에 배포합니다.
> 배포 스크립트 생성과 실행을 모두 지원합니다.

## 배포 대상 경로

| 경로 | 대상 파일 | 설명 |
|------|-----------|------|
| `/opt/lmx/include/` | `{{MODULE_NAME}}Api.h`, `{{MODULE_NAME}}ApiDef.h` | 공개 API 헤더 |
| `/opt/lmx/lib/` | `lib{{module_name}}api.a` | C++ API 정적 라이브러리 |
| `/opt/lmx/motion/` | `{{module_name_snake}}.so` | Core RTDLL/SO 모듈 |

## 배포 워크플로우

### 1단계: 프로젝트 분석

빌드 출력물의 위치를 확인합니다.

```bash
# 빌드 디렉토리 확인
ls -la build/ releasefiles/ 2>/dev/null

# .so 파일 위치
find . -name "*.so" -not -path "./build/*" | head -10

# .a 파일 위치
find . -name "*.a" -not -path "./build/*" | head -10

# 공개 헤더 위치
ls include/*.h 2>/dev/null
```

빌드 출력물 위치 규칙:

| 빌드 방식 | .so 경로 | .a 경로 |
|-----------|----------|---------|
| CMake (릴리스) | `build/linux-release/{{MODULE_NAME}}/` | `build/linux-release/{{MODULE_NAME}}Api/` |
| CMake (디버그) | `build/linux-debug/{{MODULE_NAME}}/` | `build/linux-debug/{{MODULE_NAME}}Api/` |
| Makefile (레거시) | `releasefiles/so/` | `releasefiles/lib/` |

### 2단계: 배포 스크립트 생성

프로젝트 루트에 `deploy.sh`를 생성합니다.

```bash
#!/bin/bash
# {{MODULE_NAME}} 모듈 배포 스크립트
# 빌드된 파일을 /opt/lmx/ 경로에 배포합니다.
#
# 사용법:
#   ./deploy.sh              # 릴리스 빌드 배포
#   ./deploy.sh debug        # 디버그 빌드 배포
#   ./deploy.sh --dry-run    # 실제 복사 없이 대상 확인만
#   ./deploy.sh --check      # 현재 배포 상태 확인

set -euo pipefail

# === 설정 ===
MODULE_NAME="{{MODULE_NAME}}"
MODULE_NAME_LOWER="{{module_name}}"
MODULE_NAME_SNAKE="{{module_name_snake}}"
LMX_ROOT="${LMX_INSTALL_PATH:-/opt/lmx}"
BUILD_TYPE="${1:-release}"
DRY_RUN=false
CHECK_ONLY=false

# === 인자 처리 ===
case "${1:-}" in
    --dry-run)  DRY_RUN=true; BUILD_TYPE="release" ;;
    --check)    CHECK_ONLY=true ;;
    debug)      BUILD_TYPE="debug" ;;
    release)    BUILD_TYPE="release" ;;
    "")         BUILD_TYPE="release" ;;
    *)          echo "사용법: $0 [release|debug|--dry-run|--check]"; exit 1 ;;
esac

# === 경로 설정 ===
INCLUDE_DIR="${LMX_ROOT}/include"
LIB_DIR="${LMX_ROOT}/lib"
MOTION_DIR="${LMX_ROOT}/motion"

# 빌드 출력 경로 (CMake 우선, Makefile 폴백)
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

# 공개 헤더 목록
HEADERS=(
    "include/${MODULE_NAME}Api.h"
    "include/${MODULE_NAME}ApiDef.h"
)

# === 상태 확인 모드 ===
if [ "$CHECK_ONLY" = true ]; then
    echo "=== ${MODULE_NAME} 배포 상태 확인 ==="
    echo ""
    echo "[헤더] ${INCLUDE_DIR}/"
    for h in "${HEADERS[@]}"; do
        target="${INCLUDE_DIR}/$(basename "$h")"
        if [ -f "$target" ]; then
            echo "  OK  $(basename "$h")  ($(stat -c '%Y' "$target" | xargs -I{} date -d @{} '+%Y-%m-%d %H:%M'))"
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
        echo "  OK  ${MODULE_NAME_SNAKE}.so  ($(stat -c '%s' "$target") bytes)"
        echo "       심볼: $(nm -D "$target" 2>/dev/null | grep -c 'Motion_') 개 Motion_ 함수"
    else
        echo "  --  ${MODULE_NAME_SNAKE}.so  (미배포)"
    fi
    exit 0
fi

# === 배포 전 검증 ===
echo "=== ${MODULE_NAME} 배포 (${BUILD_TYPE}) ==="
echo ""

ERRORS=0

# 소스 파일 존재 확인
if [ ! -f "$SO_SOURCE" ]; then
    echo "ERROR: ${SO_SOURCE} 파일이 없습니다."
    ERRORS=$((ERRORS + 1))
fi
if [ ! -f "$LIB_SOURCE" ]; then
    echo "ERROR: ${LIB_SOURCE} 파일이 없습니다."
    ERRORS=$((ERRORS + 1))
fi
for h in "${HEADERS[@]}"; do
    if [ ! -f "$h" ]; then
        echo "ERROR: ${h} 파일이 없습니다."
        ERRORS=$((ERRORS + 1))
    fi
done

# 대상 디렉토리 존재 확인
for dir in "$INCLUDE_DIR" "$LIB_DIR" "$MOTION_DIR"; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: ${dir} 디렉토리가 없습니다."
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "${ERRORS}개 오류 발견. 배포를 중단합니다."
    exit 1
fi

# === 심볼 검증 ===
echo "[검증] .so 심볼 확인..."
REQUIRED_SYMBOLS=("Motion_ModuleId" "Motion_ModuleInfo" "Motion_Setup" "Motion_Init" "Motion_Cleanup" "Motion_Process")
for sym in "${REQUIRED_SYMBOLS[@]}"; do
    if nm -D "$SO_SOURCE" 2>/dev/null | grep -q "$sym"; then
        echo "  OK  ${sym}"
    else
        echo "  WARN  ${sym} 심볼 없음"
    fi
done
echo ""

# === 배포 실행 ===
if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN] 실제 복사 없이 대상만 확인합니다."
    echo ""
fi

deploy_file() {
    local src="$1"
    local dst="$2"
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY] ${src} → ${dst}"
    else
        sudo cp -v "$src" "$dst"
    fi
}

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
    echo "=== DRY-RUN 완료. 실제 배포하려면 --dry-run 없이 실행하세요. ==="
else
    echo "=== ${MODULE_NAME} 배포 완료 ==="
    echo ""
    echo "배포된 파일:"
    ls -la "${INCLUDE_DIR}/${MODULE_NAME}Api.h" "${INCLUDE_DIR}/${MODULE_NAME}ApiDef.h" \
           "${LIB_DIR}/lib${MODULE_NAME_LOWER}api.a" \
           "${MOTION_DIR}/${MODULE_NAME_SNAKE}.so" 2>/dev/null
    echo ""
    echo "WMX3 엔진을 재시작하면 새 모듈이 로딩됩니다."
fi
```

### 3단계: 배포 실행

사용자 확인 후 스크립트를 실행합니다.

```bash
# 먼저 dry-run으로 확인
./deploy.sh --dry-run

# 실제 배포 (sudo 필요)
./deploy.sh release

# 현재 배포 상태 확인
./deploy.sh --check
```

### 4단계: 배포 결과 보고

```
=== {{MODULE_NAME}} 배포 결과 ===

[헤더]
  /opt/lmx/include/{{MODULE_NAME}}Api.h        OK
  /opt/lmx/include/{{MODULE_NAME}}ApiDef.h      OK

[라이브러리]
  /opt/lmx/lib/lib{{module_name}}api.a          OK (12,345 bytes)

[모듈]
  /opt/lmx/motion/{{module_name_snake}}.so      OK (45,678 bytes)
  심볼: Motion_ModuleId, Motion_ModuleInfo, Motion_Setup,
        Motion_Init, Motion_Cleanup, Motion_Process (6/6 OK)

WMX3 엔진을 재시작하면 새 모듈이 로딩됩니다.
```

## 롤백

배포 전 기존 파일을 백업하려면:

```bash
# 백업 디렉토리 생성
BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 기존 파일 백업
cp /opt/lmx/motion/{{module_name_snake}}.so "$BACKUP_DIR/" 2>/dev/null
cp /opt/lmx/lib/lib{{module_name}}api.a "$BACKUP_DIR/" 2>/dev/null
cp /opt/lmx/include/{{MODULE_NAME}}Api.h "$BACKUP_DIR/" 2>/dev/null
cp /opt/lmx/include/{{MODULE_NAME}}ApiDef.h "$BACKUP_DIR/" 2>/dev/null
```

## 주의사항

- 배포에는 `sudo` 권한이 필요합니다 (`/opt/lmx/`는 root 소유)
- 배포 전 반드시 빌드가 성공한 상태여야 합니다
- `.so` 파일의 6개 필수 심볼을 자동 검증합니다
- `--dry-run` 옵션으로 먼저 확인 후 실제 배포를 권장합니다
- WMX3 엔진 실행 중 `.so` 교체 시 다음 엔진 재시작에 반영됩니다
- `LMX_INSTALL_PATH` 환경변수로 기본 경로(`/opt/lmx`)를 변경할 수 있습니다

$ARGUMENTS
