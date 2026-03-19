# WMX3 모듈 빌드 시스템

---

## 1. CMake 디렉토리 구조

```
wmx3_module_{{module}}/
├── CMakeLists.txt          ← 루트: 전역 설정, 환경변수 검증, 서브프로젝트 등록
├── CMakePresets.json        ← 5개 사전 정의 프리셋
├── {{Module}}Api/
│   └── CMakeLists.txt      ← 정적 라이브러리 (C++11)
└── {{Module}}/
    └── CMakeLists.txt      ← 공유 라이브러리 / RTDLL (C99)
```

빌드 순서: `{{Module}}Api` (정적 라이브러리) → `{{Module}}` (공유 라이브러리)

```cmake
# CMakeLists.txt (루트) - 빌드 순서 보장
add_subdirectory({{Module}}Api)   # 먼저 빌드
add_subdirectory({{Module}})      # 다음 빌드
```

---

## 2. 언어 표준 설정

```cmake
set(CMAKE_C_STANDARD 99)        # Core RTDLL: C99
set(CMAKE_CXX_STANDARD 11)      # API 라이브러리: C++11
set(CMAKE_CXX_STANDARD_REQUIRED ON)
```

---

## 3. 필수 환경변수 (Windows)

| 환경변수 | 용도 | 예시 경로 |
|----------|------|-----------|
| `WMX3IMReleasePath` | IM 라이브러리 릴리스 경로 | `C:\WMX3\IM\releasefiles` |
| `WMX3EngineReleasePath` | 엔진 릴리스 경로 | `C:\WMX3\Engine\releasefiles` |
| `WMX3ModulesReleasePath` | 모듈 릴리스 경로 | `C:\WMX3\Modules\releasefiles` |
| `RTX64SDKDir4` | RTX64 4.x SDK 경로 | `C:\Program Files\IntervalZero\RTX64 4.5\SDK` |
| `RTX64SDKDir3` | RTX64 3.0 SDK 경로 | `C:\Program Files\IntervalZero\RTX64 3.0\SDK` |

CMake에서 환경변수 읽기:
```cmake
set(WMX3_IM_RELEASE_PATH      "$ENV{WMX3IMReleasePath}"      CACHE PATH "IM Library release path")
set(WMX3_ENGINE_RELEASE_PATH  "$ENV{WMX3EngineReleasePath}"  CACHE PATH "Engine release path")
set(WMX3_MODULES_RELEASE_PATH "$ENV{WMX3ModulesReleasePath}" CACHE PATH "Modules release path")
set(RTX64_SDK_DIR3            "$ENV{RTX64SDKDir3}"            CACHE PATH "RTX64 3.0 SDK path")
set(RTX64_SDK_DIR4            "$ENV{RTX64SDKDir4}"            CACHE PATH "RTX64 4.x SDK path")
```

### Linux 환경변수

| 환경변수 | 용도 |
|----------|------|
| `LMX_INSTALLER_ROOT` | lmxinstallerfiles 루트 경로 |
| `CROSS_COMPILE` | 크로스 컴파일러 접두어 (선택) |

Linux 경로 파생 (LMX_INSTALLER_ROOT 기준):
```cmake
set(IM_REL  "${LMX_INSTALLER_ROOT}/lmx_im/releasefiles"     CACHE PATH "IM release path")
set(ENG_REL "${LMX_INSTALLER_ROOT}/lmx_engine/releasefiles"  CACHE PATH "Engine release path")
set(MOD_REL "${LMX_INSTALLER_ROOT}/lmx_module/releasefiles"  CACHE PATH "Modules release path")
set(OSL_REL "${LMX_INSTALLER_ROOT}/lmx_osl/releasefiles"     CACHE PATH "OSL release path")
```

---

## 4. CMakePresets.json - 5개 프리셋

| 프리셋 이름 | 플랫폼 | Generator | 빌드 디렉토리 | 비고 |
|-------------|--------|-----------|---------------|------|
| `windows` | Windows | Visual Studio 17 2022 | `build-windows` | RTX64 4.x 기본, v110 toolset |
| `linux-release` | Linux | Unix Makefiles | `build-linux-release` | OSL_TYPE=rt, Release |
| `linux-debug` | Linux | Unix Makefiles | `build-linux-debug` | OSL_TYPE=rt, Debug |
| `linux-relwithdebinfo` | Linux | Unix Makefiles | `build-linux-relwithdebinfo` | OSL_TYPE=rt, RelWithDebInfo |
| `linux-xenomai` | Linux | Unix Makefiles | `build-linux-xenomai` | OSL_TYPE=xeno, Release |

```json
{
  "version": 3,
  "configurePresets": [
    {
      "name": "windows",
      "displayName": "Windows VS2022 (v110 toolset)",
      "generator": "Visual Studio 17 2022",
      "architecture": "x64",
      "toolset": "v110",
      "binaryDir": "${sourceDir}/build-windows",
      "cacheVariables": { "WMX3_BUILD_CONFIG": "RTX64_4.x" },
      "condition": { "type": "equals", "lhs": "${hostSystemName}", "rhs": "Windows" }
    },
    {
      "name": "linux-release",
      "displayName": "Linux GCC Release",
      "generator": "Unix Makefiles",
      "binaryDir": "${sourceDir}/build-linux-release",
      "cacheVariables": { "CMAKE_BUILD_TYPE": "Release", "OSL_TYPE": "rt" },
      "condition": { "type": "equals", "lhs": "${hostSystemName}", "rhs": "Linux" }
    }
  ]
}
```

---

## 5. 플랫폼별 컴파일러 플래그

### 5.1 MSVC (Windows) - RTDLL 공유 라이브러리

```cmake
target_compile_options({{Module}} PRIVATE
    /W3       # 경고 레벨 3
    /Ox       # 최대 최적화
    /Oi       # 인트린식 함수 활성화
    /MT       # 멀티스레드 정적 런타임 (RTX64 필수)
    /GS-      # 버퍼 보안 검사 비활성화 (RTX64 필수)
    /TC       # C로 컴파일
    /openmp-  # OpenMP 비활성화
    /Gs9999   # 스택 프로브 임계값
)

target_compile_definitions({{Module}} PRIVATE
    NDEBUG
    WMX3_EXPORTS
)
```

### 5.2 MSVC (Windows) - API 정적 라이브러리

```cmake
target_compile_options({{Module}}Api PRIVATE
    /W3       # 경고 레벨 3
    /O2       # 최대 속도 최적화
    /Oi       # 인트린식 함수
    /Gy       # 함수 수준 링킹
    /MT       # 멀티스레드 정적 런타임
    /Gz       # __stdcall 호출 규약
    /sdl      # SDL 보안 검사
)

target_compile_definitions({{Module}}Api PRIVATE
    WIN32
    _UNICODE UNICODE
    NDEBUG
    _LIB
)
```

### 5.3 GCC (Linux) - RTDLL 공유 라이브러리

```cmake
target_compile_options({{Module}} PRIVATE
    -fPIC
    -Wno-format-truncation
)

target_link_options({{Module}} PRIVATE
    -shared
    -Wl,--version-script=${CMAKE_CURRENT_SOURCE_DIR}/export  # 심볼 가시성
    -Wl,--no-undefined
)

target_link_libraries({{Module}} PRIVATE
    ${WMX3_OSL}       # OSL 라이브러리
    ${WMX3_IMLIB}     # IMLib 정적 라이브러리
    dl pthread rt m   # POSIX 라이브러리
)
```

### 5.4 GCC (Linux) - API 정적 라이브러리

```cmake
target_compile_options({{Module}}Api PRIVATE
    -std=c++11
    -fPIC
    -Wno-write-strings
)
```

---

## 6. RTX64 3.x vs 4.x 차이점

| 항목 | RTX64 3.x | RTX64 4.x |
|------|-----------|-----------|
| SDK 환경변수 | `RTX64SDKDir3` | `RTX64SDKDir4` |
| 출력 경로 | `ReleaseFiles/RTX64 3.0/rtdll` | `ReleaseFiles/RTX64 4.x/rtdll` |
| IM 라이브러리 경로 | `${WMX3_IM_RELEASE_PATH}/RTX64 3.0/lib` | `${WMX3_IM_RELEASE_PATH}/RTX64 4.x/lib` |
| 컴파일 정의 | `_AMD64_`, `UNDER_RTSS`, `RTX64_EXPORTS` | 동일 |
| 링크 라이브러리 | `startupDllCrt.lib`, `libcmt.lib`, `rtx_rtss.lib` | 동일 |

RTX64 공통 링커 옵션:
```cmake
target_link_options({{Module}} PRIVATE
    /DRIVER
    /ENTRY:_RtapiDllEntryCRT
    /NODEFAULTLIB           # Windows 기본 라이브러리 제외 (중요)
    /SUBSYSTEM:NATIVE
    /MANIFEST:NO
    /OPT:REF
    /OPT:ICF
)
```

RTX64 빌드 시 Windows 기본 라이브러리 제거 (필수):
```cmake
# project() 호출 전에 설정
if(WMX3_BUILD_CONFIG STREQUAL "RTX64_4.x" OR WMX3_BUILD_CONFIG STREQUAL "RTX64_3.0")
    set(CMAKE_C_STANDARD_LIBRARIES   "" CACHE STRING "" FORCE)
    set(CMAKE_CXX_STANDARD_LIBRARIES "" CACHE STRING "" FORCE)
endif()
```

---

## 7. Xenomai 빌드 특수 사항

### 컴파일러 선택 (project() 호출 전에 설정)

```cmake
if(NOT WIN32 AND OSL_TYPE STREQUAL "xeno")
    execute_process(
        COMMAND xeno-config --cc
        OUTPUT_VARIABLE XENO_CC
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE XENO_CC_RESULT
    )
    if(XENO_CC_RESULT EQUAL 0 AND XENO_CC)
        set(CMAKE_C_COMPILER "${XENO_CC}" CACHE STRING "C compiler" FORCE)
    endif()
endif()
```

### Xenomai 플래그 적용 함수

```cmake
function(wmx3_apply_xenomai_flags target)
    if(NOT OSL_TYPE STREQUAL "xeno")
        return()
    endif()
    execute_process(
        COMMAND xeno-config --alchemy --posix --cflags
        OUTPUT_VARIABLE _xeno_cflags OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET
    )
    execute_process(
        COMMAND xeno-config --alchemy --posix --ldflags --auto-init-solib
        OUTPUT_VARIABLE _xeno_ldflags OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET
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
```

---

## 8. export 심볼 파일 규칙

Linux에서 `--version-script` 옵션으로 심볼 가시성을 제어합니다.

```
# ApiBuffer/export
{
    global:
        Motion_ModuleId;
        Motion_ModuleInfo;
        Motion_Setup;
        Motion_Init;
        Motion_Cleanup;
        Motion_Process;
    local:*;    ← 나머지 모든 심볼 숨김
};
```

CMakeLists.txt에서 참조:
```cmake
target_link_options({{Module}} PRIVATE
    -Wl,--version-script=${CMAKE_CURRENT_SOURCE_DIR}/export
)
```

선택적 진입점을 구현한 경우 `global:` 섹션에 해당 함수를 추가합니다.

---

## 9. StampTool 후처리 (RTX64)

RTX64 빌드 완료 후 StampTool로 RTDLL에 서명해야 엔진이 로딩할 수 있습니다.

```cmake
if(MSVC)
    if(WMX3_BUILD_CONFIG STREQUAL "RTX64_3.0" OR WMX3_BUILD_CONFIG STREQUAL "RTX64_4.x")
        if(DEFINED ENV{RTX64Common})
            add_custom_command(TARGET {{Module}} POST_BUILD
                COMMAND "$ENV{RTX64Common}/bin/StampTool.exe" "$<TARGET_FILE:{{Module}}>"
                COMMENT "Running RTX64 StampTool"
            )
        endif()
    endif()
endif()
```

`RTX64Common` 환경변수는 RTX64 설치 시 자동 설정됩니다.

---

## 10. 레거시 빌드 도구 관계

| 도구 | 파일 | 용도 |
|------|------|------|
| Visual Studio | `{{Module}}.sln` | 3개 프로젝트 모두 포함 (CLRLib 포함), CMake 미지원 CLR 빌드용 |
| 레거시 Makefile | `{{Module}}/Makefile` | Linux 독립 빌드 (CMake 대체) |
| 셸 스크립트 | `build_lin.sh` | Makefile 기반 빌드 + 릴리스 파일 복사 |
| 배치 스크립트 | `build_win.bat`, `BuildAll.bat` | MSBuild 기반 (6개 타겟) |

CLRLib(C++/CLI .NET 래퍼)는 CMakeLists.txt에 포함되지 않으며, Visual Studio 솔루션에서만 빌드합니다.

---

## 11. 출력 경로 구조

### Windows 출력 경로

```
ReleaseFiles/
├── RTX64 4.x/
│   ├── rtdll/   ← ApiBuffer.rtdll, ApiBuffer.pdb
│   └── lib/     ← ApiBuffer.lib (임포트 라이브러리)
├── RTX64 3.0/
│   ├── rtdll/
│   └── lib/
├── Windows/
│   └── x64/
│       ├── dll/ ← ApiBuffer.dll
│       └── lib/ ← ApiBuffer.lib, IMDll.dll
└── lib/
    └── x64/     ← ApiBufferApi.lib (정적 라이브러리)
```

### Linux 출력 경로

```
releasefiles/
├── so/    ← api_buffer.so (공유 라이브러리, PREFIX 없음)
└── lib/   ← libapibufferapi.a (정적 라이브러리)
```

Linux에서는 빌드 후 `${MOD_REL}/so/` 및 `${MOD_REL}/lib/`로 자동 복사됩니다.
