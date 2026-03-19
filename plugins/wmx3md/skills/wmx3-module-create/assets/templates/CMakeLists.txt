#==============================================================================
# CMakeLists.txt - {{MODULE_NAME}} 모듈 루트 빌드 설정
# 크로스플랫폼 빌드 지원: Windows (RTX64/Standard) / Linux (RT/Xenomai)
#==============================================================================

cmake_minimum_required(VERSION 3.14)

#==============================================================================
# WINDOWS 툴셋 설정
# 모든 Windows 빌드는 호환성을 위해 Visual Studio 2012 툴셋(v110)을 사용
# toolset은 반드시 project() 호출 이전에 설정해야 함
#==============================================================================
if(WIN32 AND NOT CMAKE_GENERATOR_TOOLSET)
    set(CMAKE_GENERATOR_TOOLSET "v110" CACHE STRING "Visual Studio toolset")
    message(STATUS "Visual Studio 2012 툴셋(v110) 사용 (호환성)")
endif()

#==============================================================================
# XENOMAI 컴파일러 선택 (Linux 전용)
# project() 호출 이전에 설정해야 적용됨
# Makefile 동작과 일치: CC = $(shell xeno-config --cc)
#==============================================================================
if(NOT WIN32)
    if(DEFINED OSL_TYPE AND OSL_TYPE STREQUAL "xeno")
        execute_process(
            COMMAND xeno-config --cc
            OUTPUT_VARIABLE XENO_CC
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
            RESULT_VARIABLE XENO_CC_RESULT
        )
        if(XENO_CC_RESULT EQUAL 0 AND XENO_CC)
            set(CMAKE_C_COMPILER "${XENO_CC}" CACHE STRING "C compiler" FORCE)
            message(STATUS "Xenomai 빌드: 컴파일러 ${XENO_CC} 사용")
        endif()
    endif()
endif()

project(WMX3_{{MODULE_NAME}} VERSION 1.0.0 LANGUAGES C CXX)

# 서브디렉토리에서 사용할 모듈 루트 디렉토리 정의
set(MODULE_ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR})

#==============================================================================
# 전역 설정
#==============================================================================
set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# MSVC 보안 함수 경고 억제
if(MSVC)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
endif()

#==============================================================================
# 빌드 옵션
#==============================================================================

# Linux 전용 옵션
if(NOT WIN32)
    set(OSL_TYPE "rt" CACHE STRING "OSL 타입: rt (표준 Linux) 또는 xeno (Xenomai)")
    set_property(CACHE OSL_TYPE PROPERTY STRINGS "rt" "xeno")
endif()

# Windows 전용 옵션
if(WIN32)
    set(WMX3_BUILD_CONFIG "RTX64_4.x" CACHE STRING "빌드 구성")
    set_property(CACHE WMX3_BUILD_CONFIG PROPERTY STRINGS
        "RTX64_4.x" "RTX64_3.0" "Windows")
endif()

#==============================================================================
# 외부 의존성 - 환경 변수
#==============================================================================
if(WIN32)
    # Windows: 환경 변수로부터 경로 설정
    set(WMX3_IM_RELEASE_PATH "$ENV{WMX3IMReleasePath}" CACHE PATH "IM 라이브러리 릴리즈 경로")
    set(WMX3_ENGINE_RELEASE_PATH "$ENV{WMX3EngineReleasePath}" CACHE PATH "Engine 릴리즈 경로")
    set(WMX3_MODULES_RELEASE_PATH "$ENV{WMX3ModulesReleasePath}" CACHE PATH "Modules 릴리즈 경로")

    # RTX SDK 경로
    set(RTX64_SDK_DIR3 "$ENV{RTX64SDKDir3}" CACHE PATH "RTX64 3.0 SDK 경로")
    set(RTX64_SDK_DIR4 "$ENV{RTX64SDKDir4}" CACHE PATH "RTX64 4.x SDK 경로")

    # 빌드 구성별 RTX SDK 경로 검증
    if(WMX3_BUILD_CONFIG STREQUAL "RTX64_4.x")
        if("${RTX64_SDK_DIR4}" STREQUAL "")
            message(FATAL_ERROR "RTX64SDKDir4 환경 변수가 설정되지 않았습니다. RTX64 4.x 빌드에 필요합니다.\n예: C:/Program Files/IntervalZero/RTX64 4.5/SDK")
        endif()
        if(NOT EXISTS "${RTX64_SDK_DIR4}/lib/amd64/startupDllCrt.lib")
            message(FATAL_ERROR "RTX64 SDK 라이브러리를 찾을 수 없습니다: ${RTX64_SDK_DIR4}/lib/amd64/startupDllCrt.lib\nRTX64SDKDir4 환경 변수를 확인하세요.")
        endif()
    endif()
    if(WMX3_BUILD_CONFIG STREQUAL "RTX64_3.0")
        if("${RTX64_SDK_DIR3}" STREQUAL "")
            message(FATAL_ERROR "RTX64SDKDir3 환경 변수가 설정되지 않았습니다. RTX64 3.0 빌드에 필요합니다.")
        endif()
        if(NOT EXISTS "${RTX64_SDK_DIR3}/lib/amd64/startupDllCrt.lib")
            message(FATAL_ERROR "RTX64 SDK 라이브러리를 찾을 수 없습니다: ${RTX64_SDK_DIR3}/lib/amd64/startupDllCrt.lib\nRTX64SDKDir3 환경 변수를 확인하세요.")
        endif()
    endif()
else()
    # Linux: LMX_INSTALLER_ROOT 기반 경로 설정
    # 최상위 빌드와 독립 모듈 빌드 모두 지원

    # 1단계: LMX_INSTALLER_ROOT 결정 (상위에서 설정되지 않은 경우)
    if(NOT DEFINED LMX_INSTALLER_ROOT)
        if(DEFINED ENV{LMX_INSTALLER_ROOT})
            get_filename_component(LMX_INSTALLER_ROOT "$ENV{LMX_INSTALLER_ROOT}" ABSOLUTE)
        else()
            get_filename_component(LMX_INSTALLER_ROOT
                "${CMAKE_CURRENT_SOURCE_DIR}/../../LmxInstallerFiles" ABSOLUTE)
        endif()
        set(LMX_INSTALLER_ROOT "${LMX_INSTALLER_ROOT}" CACHE PATH
            "lmxinstallerfiles 디렉토리 루트 경로")
    endif()

    # 2단계: LMX_INSTALLER_ROOT 존재 여부 검증
    if(NOT EXISTS "${LMX_INSTALLER_ROOT}")
        message(FATAL_ERROR
            "lmxinstallerfiles를 찾을 수 없습니다: ${LMX_INSTALLER_ROOT}\n"
            "-DLMX_INSTALLER_ROOT=/path/to/lmxinstallerfiles 로 지정하세요")
    endif()

    # 3단계: LMX_INSTALLER_ROOT에서 경로 파생 (개별 재정의 가능)
    if(NOT DEFINED IM_REL)
        set(IM_REL "${LMX_INSTALLER_ROOT}/lmx_im/releasefiles" CACHE PATH "IM 릴리즈 경로")
    endif()
    if(NOT DEFINED ENG_REL)
        set(ENG_REL "${LMX_INSTALLER_ROOT}/lmx_engine/releasefiles" CACHE PATH "Engine 릴리즈 경로")
    endif()
    if(NOT DEFINED MOD_REL)
        set(MOD_REL "${LMX_INSTALLER_ROOT}/lmx_module/releasefiles" CACHE PATH "Modules 릴리즈 경로")
    endif()
    if(NOT DEFINED OSL_REL)
        set(OSL_REL "${LMX_INSTALLER_ROOT}/lmx_osl/releasefiles" CACHE PATH "OSL 릴리즈 경로")
    endif()

    # 크로스 컴파일 지원
    if(DEFINED ENV{CROSS_COMPILE} AND NOT CMAKE_C_COMPILER)
        set(CMAKE_C_COMPILER "$ENV{CROSS_COMPILE}gcc")
        set(CMAKE_CXX_COMPILER "$ENV{CROSS_COMPILE}g++")
    endif()
endif()

#==============================================================================
# 출력 경로를 위한 플랫폼 감지
#==============================================================================
if(WIN32)
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(WMX3_PLATFORM "x64")
    else()
        set(WMX3_PLATFORM "Win32")
    endif()
endif()

#==============================================================================
# RTX64: Windows 기본 라이브러리 비활성화
# RTX64 빌드는 /NODEFAULTLIB을 사용하므로 Windows SDK 라이브러리
# (kernel32.lib, user32.lib 등)를 링크해서는 안 됨
# CMake는 기본적으로 CMAKE_C_STANDARD_LIBRARIES에 이를 추가하므로
# RTX64 빌드에서는 반드시 이를 비워야 함 (링킹 단계에만 영향)
#==============================================================================
if(WIN32)
    if(WMX3_BUILD_CONFIG STREQUAL "RTX64_4.x" OR WMX3_BUILD_CONFIG STREQUAL "RTX64_3.0")
        set(CMAKE_C_STANDARD_LIBRARIES "" CACHE STRING "" FORCE)
        set(CMAKE_CXX_STANDARD_LIBRARIES "" CACHE STRING "" FORCE)
        message(STATUS "RTX64 빌드: Windows 기본 라이브러리 비활성화")
    endif()
endif()

#==============================================================================
# 외부 라이브러리 설정 (Linux)
# 독립 빌드 또는 최상위 cmake/ 헬퍼와 함께 동작
#==============================================================================
if(NOT WIN32)
    # 플랫폼 헬퍼 포함 시도 (선택적 - 최상위 빌드용)
    if(NOT COMMAND wmx3_find_external_libraries)
        include(${CMAKE_CURRENT_SOURCE_DIR}/../cmake/WMX3Platform.cmake OPTIONAL)
    endif()

    # 헬퍼가 있으면 사용, 없으면 라이브러리 변수를 직접 설정
    if(COMMAND wmx3_find_external_libraries)
        wmx3_find_external_libraries()
    else()
        # 독립 폴백: 라이브러리 이름 사용 (링커가 target_link_directories를 통해 찾음)
        if(NOT DEFINED WMX3_IMLIB)
            set(WMX3_IMLIB "imlib" CACHE STRING "IM 정적 라이브러리")
        endif()
        if(NOT DEFINED WMX3_IMDLL)
            set(WMX3_IMDLL "imdll" CACHE STRING "IM 공유 라이브러리")
        endif()
        if(NOT DEFINED WMX3_OSL)
            set(WMX3_OSL "osl" CACHE STRING "OSL 라이브러리")
        endif()
    endif()

    # 플랫폼 헬퍼가 없는 경우를 위한 인라인 Xenomai 헬퍼 정의
    if(NOT COMMAND wmx3_apply_xenomai_flags)
        function(wmx3_apply_xenomai_flags target)
            if(NOT OSL_TYPE STREQUAL "xeno")
                return()
            endif()
            execute_process(
                COMMAND xeno-config --alchemy --posix --cflags
                OUTPUT_VARIABLE _xeno_cflags
                OUTPUT_STRIP_TRAILING_WHITESPACE
                ERROR_QUIET
            )
            execute_process(
                COMMAND xeno-config --alchemy --posix --ldflags --auto-init-solib
                OUTPUT_VARIABLE _xeno_ldflags
                OUTPUT_STRIP_TRAILING_WHITESPACE
                ERROR_QUIET
            )
            if(_xeno_cflags)
                separate_arguments(_cflags_list UNIX_COMMAND "${_xeno_cflags}")
                target_compile_options(${target} PRIVATE ${_cflags_list})
            endif()
            if(_xeno_ldflags)
                separate_arguments(_ldflags_list UNIX_COMMAND "${_xeno_ldflags}")
                target_link_options(${target} PRIVATE ${_ldflags_list})
            endif()
        endfunction()
    endif()
endif()

#==============================================================================
# 서브 프로젝트 (빌드 순서: {{MODULE_NAME}}Api -> {{MODULE_NAME}})
#==============================================================================
add_subdirectory({{MODULE_NAME}}Api)
add_subdirectory({{MODULE_NAME}})

#==============================================================================
# 빌드 설정 요약
#==============================================================================
message(STATUS "==============================================")
message(STATUS "{{MODULE_NAME}} 모듈 CMake 설정 요약")
message(STATUS "==============================================")
if(WIN32)
    message(STATUS "플랫폼: Windows (${WMX3_PLATFORM})")
    message(STATUS "빌드 구성: ${WMX3_BUILD_CONFIG}")
else()
    message(STATUS "플랫폼: Linux")
    message(STATUS "OSL 타입: ${OSL_TYPE}")
endif()
message(STATUS "==============================================")
