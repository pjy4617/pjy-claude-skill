#!/bin/sh
# =============================================================================
# build_lin.sh — {{MODULE_NAME}} 모듈 Linux 빌드 스크립트
#
# 사용법:
#   ./build_lin.sh              # 기본 빌드
#   ./build_lin.sh -copy        # 빌드 후 릴리스 파일을 인스톨러 경로로 복사
#
# 환경변수 (미설정 시 기본값 사용):
#   osl_type      — OSL 타입 (기본: rt)
#   im_rel        — IM 릴리스 파일 경로
#   eng_rel       — 엔진 릴리스 파일 경로
#   mod_rel       — 모듈 릴리스 파일 경로
#   cross_compile — 크로스 컴파일러 접두어 (예: arm-linux-gnueabihf-)
#   gcc_suffix    — GCC 접미어
#   extra_options — 추가 컴파일 옵션
# =============================================================================

# -copy 옵션 파싱: 빌드 산출물을 인스톨러 경로로 복사할지 결정
file_copy=false
for arg in "$@"; do
    if [ "$arg" = "-copy" ]; then
        file_copy=true
    fi
done

# 스크립트 절대 경로 기준으로 빌드 디렉토리 설정 (심볼릭 링크 해제)
build_dir=$(dirname $(readlink -f "$0"))

# 환경변수 기본값 설정
[ -z $osl_type ] && osl_type=rt
[ -z $im_rel ]  && im_rel=${build_dir}/../../LmxInstallerFiles/lmx_im/releasefiles
[ -z $eng_rel ] && eng_rel=${build_dir}/../../LmxInstallerFiles/lmx_engine/releasefiles
[ -z $mod_rel ] && mod_rel=${build_dir}/../../LmxInstallerFiles/lmx_module/releasefiles

# =============================================================================
# 기존 릴리스 파일 정리 및 출력 디렉토리 재생성
# =============================================================================
rm -rf "${build_dir}/releasefiles/"

mkdir -p "${build_dir}/releasefiles/include"
mkdir -p "${build_dir}/releasefiles/lib"
mkdir -p "${build_dir}/releasefiles/so"

# =============================================================================
# {{MODULE_NAME}}Api (C++ 래퍼 라이브러리) 빌드
# =============================================================================
cd "${build_dir}/{{MODULE_NAME}}Api"
make clean
make OSL_TYPE=${osl_type} \
     IM_REL=${im_rel} \
     ENG_REL=${eng_rel} \
     MOD_REL=${mod_rel} \
     CROSS_COMPILE=${cross_compile} \
     GCC_SUFFIX=${gcc_suffix} \
     EXTRA_OPTIONS="${extra_options}" || exit 1

# 정적 라이브러리 복사 (lib{{module_name}}api.a)
cp lib{{module_name}}api.a "${build_dir}/releasefiles/lib"

# =============================================================================
# {{MODULE_NAME}} (RT 동적 모듈) 빌드
# =============================================================================
cd "${build_dir}/{{MODULE_NAME}}"
make clean
make OSL_TYPE=${osl_type} \
     IM_REL=${im_rel} \
     ENG_REL=${eng_rel} \
     MOD_REL=${mod_rel} \
     CROSS_COMPILE=${cross_compile} \
     GCC_SUFFIX=${gcc_suffix} \
     EXTRA_OPTIONS="${extra_options}" || exit 1

# 공유 라이브러리 복사 ({{module_name}}.so)
cp {{module_name}}.so "${build_dir}/releasefiles/so"

# =============================================================================
# 공개 헤더 파일 복사
# =============================================================================
cd "${build_dir}"
cp "${build_dir}/include/{{MODULE_NAME}}Api.h"      "${build_dir}/releasefiles/include"
cp "${build_dir}/include/{{MODULE_NAME}}ApiDef.h"   "${build_dir}/releasefiles/include"
cp "${build_dir}/include/{{MODULE_NAME}}ApiLocal.h" "${build_dir}/releasefiles/include"
cp "${build_dir}/include/{{MODULE_NAME}}ApiPub.h"   "${build_dir}/releasefiles/include"

# =============================================================================
# -copy 옵션: 릴리스 파일을 인스톨러 경로로 복사
# =============================================================================
if [ "$file_copy" = true ]; then
    out_dir=$(realpath "$mod_rel")

    cp "${build_dir}/releasefiles/include/{{MODULE_NAME}}Api.h"      "${out_dir}/include/{{MODULE_NAME}}Api.h"
    cp "${build_dir}/releasefiles/include/{{MODULE_NAME}}ApiDef.h"   "${out_dir}/include/{{MODULE_NAME}}ApiDef.h"
    cp "${build_dir}/releasefiles/include/{{MODULE_NAME}}ApiLocal.h" "${out_dir}/include/{{MODULE_NAME}}ApiLocal.h"
    cp "${build_dir}/releasefiles/include/{{MODULE_NAME}}ApiPub.h"   "${out_dir}/include/{{MODULE_NAME}}ApiPub.h"
    cp "${build_dir}/releasefiles/lib/lib{{module_name}}api.a"       "${out_dir}/lib/lib{{module_name}}api.a"
    cp "${build_dir}/releasefiles/so/{{module_name}}.so"             "${out_dir}/so/{{module_name}}.so"
fi
