#==============================================================================
# {{MODULE_NAME}} - 동적 라이브러리 (DLL/RTDLL/SO) 빌드 설정
#==============================================================================

# 소스 파일 목록
set(DLL_SOURCES
    {{MODULE_NAME}}_Event.c
    {{MODULE_NAME}}_Funcs.c
    {{MODULE_NAME}}_Motion.c
    {{MODULE_NAME}}_PubFuncs.c
    {{MODULE_NAME}}_Util.c
)

# {{MODULE_NAME}}.c는 Windows DllMain 진입점을 포함 - Windows 전용
if(WIN32)
    list(APPEND DLL_SOURCES {{MODULE_NAME}}.c)
endif()

add_library({{MODULE_NAME}} SHARED ${DLL_SOURCES})

#==============================================================================
# 인클루드 디렉토리
#==============================================================================
target_include_directories({{MODULE_NAME}} PRIVATE
    ${MODULE_ROOT_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}
)

if(WIN32)
    target_include_directories({{MODULE_NAME}} PRIVATE
        ${WMX3_IM_RELEASE_PATH}/include
        ${WMX3_ENGINE_RELEASE_PATH}/include
        ${WMX3_MODULES_RELEASE_PATH}/include
    )
else()
    target_include_directories({{MODULE_NAME}} PRIVATE
        ${IM_REL}/include
        ${ENG_REL}/include
        ${MOD_REL}/include
    )
endif()

#==============================================================================
# WINDOWS (MSVC)
#==============================================================================
if(MSVC)
    # 모든 Windows 구성에 공통 컴파일 옵션
    target_compile_options({{MODULE_NAME}} PRIVATE
        /W3              # 경고 수준 3
        /Ox              # 최대 최적화
        /Oi              # 내장 함수 사용
        /MT              # 멀티스레드 런타임
        /GS-             # 버퍼 보안 검사 비활성화
        /TC              # C 컴파일
        /openmp-         # OpenMP 비활성화
        /Gs9999          # 스택 프로브 임계값
    )

    target_compile_definitions({{MODULE_NAME}} PRIVATE
        NDEBUG
        WMX3_EXPORTS
    )

    #==========================================================================
    # RTX64 4.x (기본)
    #==========================================================================
    if(WMX3_BUILD_CONFIG STREQUAL "RTX64_4.x")
        target_compile_definitions({{MODULE_NAME}} PRIVATE
            _AMD64_
            UNDER_RTSS
            RTX64_EXPORTS
            UNICODE
            _UNICODE
        )
        target_compile_options({{MODULE_NAME}} PRIVATE
            /Gy              # 함수 수준 링킹
        )
        target_include_directories({{MODULE_NAME}} PRIVATE
            ${RTX64_SDK_DIR4}/include
        )
        set_target_properties({{MODULE_NAME}} PROPERTIES
            OUTPUT_NAME "{{MODULE_NAME}}"
            SUFFIX ".rtdll"
            RUNTIME_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
            RUNTIME_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
            RUNTIME_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
            RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
            RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
            ARCHIVE_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/lib"
            ARCHIVE_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/lib"
            ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/lib"
            ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/lib"
            ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/lib"
            PDB_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
            PDB_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
            PDB_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
            PDB_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
            PDB_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 4.x/rtdll"
        )
        target_link_libraries({{MODULE_NAME}} PRIVATE
            startupDllCrt.lib
            libcmt.lib
            rtx_rtss.lib
            IMLib
        )
        target_link_directories({{MODULE_NAME}} PRIVATE
            "${WMX3_IM_RELEASE_PATH}/RTX64 4.x/lib"
            "${RTX64_SDK_DIR4}/lib/amd64"
        )
        target_link_options({{MODULE_NAME}} PRIVATE
            /DRIVER
            /ENTRY:_RtapiDllEntryCRT
            /NODEFAULTLIB
            /SUBSYSTEM:NATIVE
            /MANIFEST:NO
            /OPT:REF
            /OPT:ICF
        )

    #==========================================================================
    # RTX64 3.0
    #==========================================================================
    elseif(WMX3_BUILD_CONFIG STREQUAL "RTX64_3.0")
        target_compile_definitions({{MODULE_NAME}} PRIVATE
            _AMD64_
            UNDER_RTSS
            RTX64_EXPORTS
            UNICODE
            _UNICODE
        )
        target_compile_options({{MODULE_NAME}} PRIVATE
            /Gy              # 함수 수준 링킹
        )
        target_include_directories({{MODULE_NAME}} PRIVATE
            ${RTX64_SDK_DIR3}/include
        )
        set_target_properties({{MODULE_NAME}} PROPERTIES
            OUTPUT_NAME "{{MODULE_NAME}}"
            SUFFIX ".rtdll"
            RUNTIME_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
            RUNTIME_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
            RUNTIME_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
            RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
            RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
            ARCHIVE_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/lib"
            ARCHIVE_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/lib"
            ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/lib"
            ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/lib"
            ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/lib"
            PDB_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
            PDB_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
            PDB_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
            PDB_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
            PDB_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/RTX64 3.0/rtdll"
        )
        target_link_libraries({{MODULE_NAME}} PRIVATE
            startupDllCrt.lib
            libcmt.lib
            rtx_rtss.lib
            IMLib
        )
        target_link_directories({{MODULE_NAME}} PRIVATE
            "${WMX3_IM_RELEASE_PATH}/RTX64 3.0/lib"
            "${RTX64_SDK_DIR3}/lib/amd64"
        )
        target_link_options({{MODULE_NAME}} PRIVATE
            /DRIVER
            /ENTRY:_RtapiDllEntryCRT
            /NODEFAULTLIB
            /SUBSYSTEM:NATIVE
            /MANIFEST:NO
            /OPT:REF
            /OPT:ICF
        )

    #==========================================================================
    # 표준 Windows
    #==========================================================================
    elseif(WMX3_BUILD_CONFIG STREQUAL "Windows")
        target_compile_definitions({{MODULE_NAME}} PRIVATE
            _UNICODE
            UNICODE
        )
        if(WMX3_PLATFORM STREQUAL "x64")
            target_compile_definitions({{MODULE_NAME}} PRIVATE _AMD64_)
        endif()
        set_target_properties({{MODULE_NAME}} PROPERTIES
            OUTPUT_NAME "{{MODULE_NAME}}"
            SUFFIX ".dll"
            RUNTIME_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
            RUNTIME_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
            RUNTIME_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
            RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
            RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
            ARCHIVE_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/lib"
            ARCHIVE_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/lib"
            ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/lib"
            ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/lib"
            ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/lib"
            PDB_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
            PDB_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
            PDB_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
            PDB_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
            PDB_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/Windows/${WMX3_PLATFORM}/dll"
        )
        target_link_libraries({{MODULE_NAME}} PRIVATE
            IMLib
        )
        target_link_directories({{MODULE_NAME}} PRIVATE
            "${WMX3_IM_RELEASE_PATH}/Windows/${WMX3_PLATFORM}/lib"
        )
        target_link_options({{MODULE_NAME}} PRIVATE
            /SUBSYSTEM:WINDOWS
        )
    endif()

#==============================================================================
# LINUX/GCC
#==============================================================================
else()
    # Xenomai 지원
    wmx3_apply_xenomai_flags({{MODULE_NAME}})

    target_compile_options({{MODULE_NAME}} PRIVATE -fPIC -Wno-format-truncation)

    target_link_options({{MODULE_NAME}} PRIVATE
        -shared
        -Wl,--version-script=${CMAKE_CURRENT_SOURCE_DIR}/export
        -Wl,--no-undefined
    )

    target_link_directories({{MODULE_NAME}} PRIVATE
        ${OSL_REL}/lib
        ${IM_REL}/lib
    )

    target_link_libraries({{MODULE_NAME}} PRIVATE
        ${WMX3_OSL}
        ${WMX3_IMLIB}
        dl pthread rt m
    )

    set_target_properties({{MODULE_NAME}} PROPERTIES
        PREFIX ""
        OUTPUT_NAME "{{module_name_snake}}"
        SUFFIX ".so"
        LIBRARY_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/releasefiles/so"
    )

    # Release 빌드 시 심볼 제거
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        add_custom_command(TARGET {{MODULE_NAME}} POST_BUILD
            COMMAND ${CMAKE_STRIP} $<TARGET_FILE:{{MODULE_NAME}}>
            COMMENT "공유 라이브러리 심볼 제거"
        )
    endif()

    # lmxinstallerfiles로 복사
    add_custom_command(TARGET {{MODULE_NAME}} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "${MOD_REL}/so"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:{{MODULE_NAME}}> "${MOD_REL}/so/"
        COMMENT "{{MODULE_NAME}}을 lmxinstallerfiles로 복사"
    )
endif()

#==============================================================================
# RTX 빌드 후 처리: StampTool
#==============================================================================
if(MSVC)
    if(WMX3_BUILD_CONFIG STREQUAL "RTX64_3.0" OR WMX3_BUILD_CONFIG STREQUAL "RTX64_4.x")
        if(DEFINED ENV{RTX64Common})
            add_custom_command(TARGET {{MODULE_NAME}} POST_BUILD
                COMMAND "$ENV{RTX64Common}/bin/StampTool.exe" "$<TARGET_FILE:{{MODULE_NAME}}>"
                COMMENT "RTX64 StampTool 실행"
            )
        endif()
    endif()
endif()

#==============================================================================
# 빌드 후 처리: 헤더 복사
#==============================================================================
set({{MODULE_NAME_UPPER}}_HEADERS
    ${MODULE_ROOT_DIR}/include/{{MODULE_NAME}}Api.h
    ${MODULE_ROOT_DIR}/include/{{MODULE_NAME}}ApiDef.h
    ${MODULE_ROOT_DIR}/include/{{MODULE_NAME}}ApiLocal.h
    ${MODULE_ROOT_DIR}/include/{{MODULE_NAME}}ApiPub.h
)

# 릴리즈 디렉토리로 헤더 복사 (플랫폼별 경로)
if(WIN32)
    add_custom_command(TARGET {{MODULE_NAME}} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "${WMX3_MODULES_RELEASE_PATH}/include"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${{{MODULE_NAME_UPPER}}_HEADERS} "${WMX3_MODULES_RELEASE_PATH}/include/"
        COMMENT "{{MODULE_NAME}} 헤더를 modules release 경로로 복사"
    )
else()
    add_custom_command(TARGET {{MODULE_NAME}} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "${MOD_REL}/include"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${{{MODULE_NAME_UPPER}}_HEADERS} "${MOD_REL}/include/"
        COMMENT "{{MODULE_NAME}} 헤더를 modules release 경로로 복사"
    )
endif()
