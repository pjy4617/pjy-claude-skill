---
name: wmx3-tdd
description: "WMX3 모듈의 호스트 기반 단위 테스트 생성 및 실행. gtest + gmock을 사용하여 PC에서 API 모드 핸들러 로직, 상태 머신, 데이터 변환, 조건 평가를 테스트한다. 'wmx3 테스트', 'TDD', '단위 테스트', 'gtest', '테스트 작성', '함수 테스트해줘', 'RT 로직 검증' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[모듈명 또는 함수명]"
---

# WMX3 모듈 호스트 기반 TDD (Test-Driven Development)

> 이 스킬은 테스트 체계와 패턴을 정의합니다.
> 실제 테스트 코드 작성은 **wmx3-test-writer 에이전트**에게 위임됩니다.

## 핵심 원칙

1. **호스트 기반 테스트**: PC(x86/x64)에서 실행. RT 하드웨어(RTX64, Xenomai) 불필요.
2. **IMLib/OSL을 gmock으로 대체**: 실시간 IPC 함수를 인터페이스 추상화 + gmock으로 치환.
3. **Red → Green → Refactor**: 실패하는 테스트 먼저 → 최소 구현 → 리팩토링.
4. **테스트 가능한 것만 테스트**: RT 타이밍, 실제 IPC, 인터럽트 레이턴시는 대상 제외.

---

## 테스트 가능 / 불가능 범위

### 테스트 가능 (호스트에서 실행)

| 대상 | 예시 | 가치 |
|------|------|------|
| API 모드 핸들러 로직 | `Execute()` 핸들러, `Halt()` 핸들러 | 높음 |
| 조건 평가 엔진 | AND/OR/XOR/NOT 게이트, 비교 연산 | 높음 |
| 상태 머신 | 버퍼 상태 전이 (IDLE→RUNNING→HALTED) | 높음 |
| 유틸리티 함수 | CRC 계산, 구조체 변환, 범위 검사 | 높음 |
| 데이터 변환 | C++ ↔ C 구조체 변환 (`ApiUtil.cpp`) | 중간 |
| 버퍼 관리 로직 | 명령 큐 삽입/제거, Rewind 로직 | 중간 |
| 에러 코드 분기 | 에러 코드별 처리 경로 | 중간 |

### 테스트 불가 (RT 환경 필요)

- RT 타이밍 (제어 사이클 지연, 인터럽트 레이턴시)
- 실제 IPC 통신 (공유 메모리, 명령 큐 IMDll)
- DMA 전송, 실제 모션 축 제어
- RTX64 / Xenomai 실시간 스케줄링

---

## 테스트 프로젝트 구조

기존 모듈에 `test/` 디렉토리를 추가:

```
wmx3_module_{{module_name}}/
├── {{MODULE_NAME}}/                    ← 기존 Core RTDLL 소스
├── {{MODULE_NAME}}Api/                 ← 기존 C++ API 소스
├── include/                            ← 기존 공유 헤더
└── test/                               ← 테스트 루트
    ├── CMakeLists.txt                  ← 호스트 빌드 (x86/x64 gcc)
    ├── mocks/                          ← IMLib/OSL 모의 객체
    │   ├── MockImLib.h                   IMLib 인터페이스 + gmock
    │   ├── MockOsl.h                     OSL 인터페이스 + gmock
    │   └── FakeMotionContext.h           Motion 컨텍스트 스텁
    ├── test_funcs.cpp                  ← API 모드 핸들러 테스트
    ├── test_util.cpp                   ← 유틸리티 함수 테스트
    ├── test_state_machine.cpp          ← 상태 머신 테스트
    ├── test_condition.cpp              ← 조건 평가 엔진 테스트
    └── test_api_util.cpp               ← C++ ↔ C 변환 테스트
```

---

## 테스트 프레임워크

### gtest (단위 테스트)

```cpp
#include <gtest/gtest.h>
#include "ApiBuffer_Funcs.h"
#include "ApiBufferApiLocal.h"

class ApiFuncsTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 각 테스트 전 초기화
        memset(&g_moduleState, 0, sizeof(g_moduleState));
    }

    void TearDown() override {
        // 각 테스트 후 정리
    }
};

TEST_F(ApiFuncsTest, Execute_ValidChannel_ReturnsSuccess) {
    ApiBufferExecuteInput input;
    input.channelNo = 0;
    input.startIndex = 0;

    int result = AB_Execute(&input, nullptr);

    EXPECT_EQ(0, result);
    EXPECT_EQ(MODULE_STATE_RUNNING, g_moduleState.status);
}

TEST_F(ApiFuncsTest, Execute_InvalidChannel_ReturnsError) {
    ApiBufferExecuteInput input;
    input.channelNo = 999;  // 범위 초과

    int result = AB_Execute(&input, nullptr);

    EXPECT_LT(result, 0);  // 에러 코드는 음수
}
```

### gmock (IMLib/OSL 모의 객체)

IMLib와 OSL은 함수 포인터 테이블 또는 추상 인터페이스로 감싸서 gmock으로 대체합니다.

**인터페이스 추상화 패턴:**

```cpp
// mocks/MockImLib.h
#pragma once
#include <gmock/gmock.h>

// IMLib 함수를 추상 인터페이스로 감싼다
class IImLib {
public:
    virtual ~IImLib() = default;
    virtual int IM_GetApiData(int channel, void *pData, int size) = 0;
    virtual int IM_SetApiData(int channel, const void *pData, int size) = 0;
    virtual int IM_QueueCommand(int channel, int funcId,
                                const void *pArgs, int argSize) = 0;
};

class MockImLib : public IImLib {
public:
    MOCK_METHOD(int, IM_GetApiData,
                (int channel, void *pData, int size), (override));
    MOCK_METHOD(int, IM_SetApiData,
                (int channel, const void *pData, int size), (override));
    MOCK_METHOD(int, IM_QueueCommand,
                (int channel, int funcId, const void *pArgs, int argSize),
                (override));
};
```

**gmock 사용 예시:**

```cpp
#include "mocks/MockImLib.h"

TEST(ApiBufferApiTest, Execute_SendsCorrectCommand) {
    MockImLib mockIm;

    // 기대값 설정: QueueCommand가 정확한 funcId로 호출되어야 함
    EXPECT_CALL(mockIm, IM_QueueCommand(
        /*channel=*/0,
        /*funcId=*/AB_APIFUNC_EXECUTE,
        testing::NotNull(),
        testing::Gt(0)
    )).WillOnce(testing::Return(0));

    // 테스트 대상: IMLib 의존성을 주입
    wmx3Api::ApiBuffer api(&mockIm);
    int result = api.Execute(0);

    EXPECT_EQ(0, result);
}

TEST(ApiBufferApiTest, Execute_ImQueueFails_ReturnsError) {
    MockImLib mockIm;

    // IPC 실패 시나리오
    EXPECT_CALL(mockIm, IM_QueueCommand(testing::_, testing::_, testing::_,
                                         testing::_))
        .WillOnce(testing::Return(-1));

    wmx3Api::ApiBuffer api(&mockIm);
    int result = api.Execute(0);

    EXPECT_LT(result, 0);
}
```

---

## IMLib/OSL 모킹 전략

WMX3 모듈은 IMLib/OSL과 직접 링크하므로, 테스트 빌드에서 다음 두 가지 전략 중 선택합니다.

### 전략 A: 함수 포인터 테이블 주입 (C 모듈용, 권장)

```c
// Core RTDLL 소스에 함수 포인터 테이블 추가
typedef struct {
    int (*GetApiData)(int channel, void *pData, int size);
    int (*SetApiData)(int channel, const void *pData, int size);
    int (*QueueCommand)(int channel, int funcId,
                        const void *pArgs, int argSize);
} ImLibVtable;

// 프로덕션에서는 실제 IMLib 함수를 테이블에 등록
// 테스트에서는 스텁 함수를 테이블에 등록
extern ImLibVtable g_imlib;
```

### 전략 B: 링크 치환 (빌드 시스템 레벨)

테스트 빌드 CMakeLists.txt에서 IMLib/OSL을 링크하지 않고, 동일한 심볼을 가진 스텁 라이브러리를 대신 링크합니다.

```cmake
# test/CMakeLists.txt
target_link_libraries(wmx3_tests
    PRIVATE
        gtest_main
        gmock_main
        wmx3_module_stubs    # ← IMLib/OSL 스텁
        # (실제 libimlib.a 대신)
)
```

---

## 테스트 프로젝트 CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.20)
project({{MODULE_NAME}}_Tests CXX)

set(CMAKE_CXX_STANDARD 17)

# Google Test 설치 경로
find_package(GTest REQUIRED)
find_package(GMock REQUIRED)

# 테스트 대상 소스 (IMLib/OSL 미의존 파일만)
set(SUT_SOURCES
    ../{{MODULE_NAME}}/{{MODULE_NAME}}_Funcs.c
    ../{{MODULE_NAME}}/{{MODULE_NAME}}_Util.c
    ../{{MODULE_NAME}}Api/{{MODULE_NAME}}ApiUtil.cpp
    ../{{MODULE_NAME}}Api/{{MODULE_NAME}}ApiTypes.cpp
)

# 테스트 소스
set(TEST_SOURCES
    test_funcs.cpp
    test_util.cpp
    test_state_machine.cpp
    test_condition.cpp
    test_api_util.cpp
)

add_executable({{module_name}}_tests
    ${SUT_SOURCES}
    ${TEST_SOURCES}
)

target_include_directories({{module_name}}_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/../include
    ${CMAKE_SOURCE_DIR}/mocks
    ${GTEST_INCLUDE_DIRS}
)

target_compile_definitions({{module_name}}_tests PRIVATE
    UNIT_TEST=1    # 테스트 빌드 식별 매크로
)

target_link_libraries({{module_name}}_tests PRIVATE
    GTest::gtest_main
    GTest::gmock
)

include(GoogleTest)
gtest_discover_tests({{module_name}}_tests)
```

---

## TDD 워크플로우

```
1. RED    — 실패하는 테스트 먼저 작성
            wmx3-test-writer 에이전트가 테스트 코드 생성
            cd test && cmake -B build && cmake --build build → FAIL 확인

2. GREEN  — 테스트를 통과하는 최소한의 코드 구현
            핸들러 로직 수정 → cmake --build build → PASS 확인

3. REFACTOR — 테스트 통과 상태에서 코드 개선
              리팩토링 → cmake --build build → 여전히 PASS 확인

4. RT 빌드  — 테스트 통과 후 실제 모듈 빌드
              cd .. && cmake --preset linux-release
              cmake --build --preset linux-release
```

---

## wmx3-module-add-api 스킬과의 연동

새 API 모드 추가 후 TDD로 검증하는 플로우:

```
"GetStatus API 모드 추가해줘"
  → wmx3-module-add-api 스킬이 6~7개 파일 수정
  → "GetStatus 테스트 작성해줘"
  → wmx3-tdd 스킬 트리거
  → wmx3-test-writer 에이전트가 gtest 코드 생성
  → "테스트 실행해줘"
  → cd test && cmake -B build && cmake --build build && ./build/wmx3_tests
```

또는 처음부터 TDD로 진행:

```
"TDD로 GetStatus API 모드 만들어줘"
  → wmx3-test-writer 에이전트가 실패하는 테스트 먼저 작성
  → wmx3-module-add-api 스킬이 최소 구현
  → 테스트 실행 → PASS 확인
  → 다음 기능 반복
```

$ARGUMENTS
