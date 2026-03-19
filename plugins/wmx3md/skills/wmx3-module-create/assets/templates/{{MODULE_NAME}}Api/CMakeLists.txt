#==============================================================================
# {{MODULE_NAME}}Api - C++ API 정적 라이브러리 빌드 설정
#==============================================================================

set(LIB_SOURCES
    {{MODULE_NAME}}Api.cpp
    {{MODULE_NAME}}ApiTypes.cpp
    {{MODULE_NAME}}ApiUtil.cpp
    {{MODULE_NAME}}Api_ApiLog.cpp
    {{MODULE_NAME}}Api_Event.cpp
)

add_library({{MODULE_NAME}}Api STATIC ${LIB_SOURCES})

#==============================================================================
# 인클루드 디렉토리
#==============================================================================
target_include_directories({{MODULE_NAME}}Api PUBLIC
    $<BUILD_INTERFACE:${MODULE_ROOT_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
)

if(WIN32)
    target_include_directories({{MODULE_NAME}}Api PRIVATE
        ${WMX3_IM_RELEASE_PATH}/include
        ${WMX3_ENGINE_RELEASE_PATH}/include
        ${WMX3_MODULES_RELEASE_PATH}/include
    )
else()
    target_include_directories({{MODULE_NAME}}Api PRIVATE
        ${IM_REL}/include
        ${ENG_REL}/include
        ${MOD_REL}/include
    )
endif()

#==============================================================================
# WINDOWS (MSVC)
#==============================================================================
if(MSVC)
    target_compile_definitions({{MODULE_NAME}}Api PRIVATE
        WIN32
        _UNICODE
        UNICODE
        NDEBUG
        _LIB
    )
    target_compile_options({{MODULE_NAME}}Api PRIVATE
        /W3              # 경고 수준 3
        /O2              # 최대 속도 최적화
        /Oi              # 내장 함수 사용
        /Gy              # 함수 수준 링킹
        /MT              # 멀티스레드 런타임
        /Gz              # __stdcall 호출 규약
        /sdl             # SDL 검사
    )

    set_target_properties({{MODULE_NAME}}Api PROPERTIES
        ARCHIVE_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
        ARCHIVE_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
        ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
        ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
        ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
        COMPILE_PDB_NAME "{{MODULE_NAME}}Api"
        COMPILE_PDB_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
        COMPILE_PDB_OUTPUT_DIRECTORY_DEBUG "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
        COMPILE_PDB_OUTPUT_DIRECTORY_RELEASE "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
        COMPILE_PDB_OUTPUT_DIRECTORY_RELWITHDEBINFO "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
        COMPILE_PDB_OUTPUT_DIRECTORY_MINSIZEREL "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}"
    )

#==============================================================================
# LINUX/GCC
#==============================================================================
else()
    # Xenomai는 별도 플래그 사용
    if(OSL_TYPE STREQUAL "xeno")
        target_compile_options({{MODULE_NAME}}Api PRIVATE -fPIC)
    else()
        target_compile_options({{MODULE_NAME}}Api PRIVATE -std=c++11 -fPIC)
    endif()

    target_compile_options({{MODULE_NAME}}Api PRIVATE -Wno-write-strings)

    set_target_properties({{MODULE_NAME}}Api PROPERTIES
        OUTPUT_NAME "{{module_name}}api"
        ARCHIVE_OUTPUT_DIRECTORY "${MODULE_ROOT_DIR}/releasefiles/lib"
    )

    # lmxinstallerfiles로 복사
    add_custom_command(TARGET {{MODULE_NAME}}Api POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "${MOD_REL}/lib"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:{{MODULE_NAME}}Api> "${MOD_REL}/lib/"
        COMMENT "{{MODULE_NAME}}Api를 lmxinstallerfiles로 복사"
    )
endif()

#==============================================================================
# 빌드 후 처리: 헤더 복사
#==============================================================================
set(LIB_HEADERS
    ${MODULE_ROOT_DIR}/include/{{MODULE_NAME}}Api.h
    ${MODULE_ROOT_DIR}/include/{{MODULE_NAME}}ApiDef.h
    ${MODULE_ROOT_DIR}/include/{{MODULE_NAME}}ApiLocal.h
)

# 릴리즈 디렉토리로 헤더 복사 (플랫폼별 경로)
if(WIN32)
    add_custom_command(TARGET {{MODULE_NAME}}Api POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "${WMX3_MODULES_RELEASE_PATH}/include"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${LIB_HEADERS} "${WMX3_MODULES_RELEASE_PATH}/include/"
        COMMENT "{{MODULE_NAME}}Api 헤더를 modules release 경로로 복사"
    )
else()
    add_custom_command(TARGET {{MODULE_NAME}}Api POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "${MOD_REL}/include"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${LIB_HEADERS} "${MOD_REL}/include/"
        COMMENT "{{MODULE_NAME}}Api 헤더를 modules release 경로로 복사"
    )
endif()

#==============================================================================
# 빌드 후 처리: IMDll.dll 복사 (Windows 전용)
#==============================================================================
if(WIN32)
    add_custom_command(TARGET {{MODULE_NAME}}Api POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${WMX3_IM_RELEASE_PATH}/Windows/${WMX3_PLATFORM}/lib/IMDll.dll"
            "${MODULE_ROOT_DIR}/ReleaseFiles/lib/${WMX3_PLATFORM}/"
        COMMENT "IMDll.dll을 ReleaseFiles/lib/${WMX3_PLATFORM}로 복사"
    )
endif()
