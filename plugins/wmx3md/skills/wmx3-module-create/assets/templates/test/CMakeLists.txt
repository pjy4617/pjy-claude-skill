cmake_minimum_required(VERSION 3.14)
project({{MODULE_NAME}}_Test CXX)

# C++14 표준 사용 (GoogleTest 요구사항)
set(CMAKE_CXX_STANDARD 14)

# =============================================================================
# GoogleTest 자동 다운로드 및 빌드 (FetchContent)
# =============================================================================
include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG v1.14.0
)
FetchContent_MakeAvailable(googletest)

# =============================================================================
# 테스트 대상 소스 (Core 모듈 — RT 의존 파일 제외)
# Motion_Process, 인터럽트 핸들러가 포함된 파일은 테스트 대상에서 제외
# =============================================================================
set(SUT_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/../{{MODULE_NAME}}/{{MODULE_NAME}}_Funcs.c
    ${CMAKE_CURRENT_SOURCE_DIR}/../{{MODULE_NAME}}/{{MODULE_NAME}}_Util.c
    ${CMAKE_CURRENT_SOURCE_DIR}/../{{MODULE_NAME}}/{{MODULE_NAME}}_PubFuncs.c
)

# =============================================================================
# 테스트 소스
# =============================================================================
set(TEST_SOURCES
    test_{{MODULE_NAME}}_Funcs.cpp
)

# =============================================================================
# 테스트 실행 파일 생성
# =============================================================================
add_executable({{module_name}}_test ${TEST_SOURCES} ${SUT_SOURCES})

# 헤더 검색 경로: 공개 include + Core 내부 헤더 + 테스트 디렉토리 (mock 포함)
target_include_directories({{module_name}}_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../{{MODULE_NAME}}
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# UNIT_TEST 정의: 테스트 빌드에서만 활성화되는 코드 가드 (#ifdef UNIT_TEST)
target_compile_definitions({{module_name}}_test PRIVATE UNIT_TEST)

# GoogleTest / GoogleMock 링크
target_link_libraries({{module_name}}_test
    GTest::gtest_main
    GTest::gmock
)

# CTest 자동 등록 (cmake --build 후 ctest 명령으로 실행 가능)
include(GoogleTest)
gtest_discover_tests({{module_name}}_test)
