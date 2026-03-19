# WMX3 모듈 TDD 패턴

WMX3 RTDLL 모듈의 테스트 전략과 gtest/gmock 기반 구현 패턴을 설명합니다.

---

## 1. 테스트 가능/불가능 범위

### 테스트 가능한 영역

| 대상 | 설명 |
|------|------|
| 순수 로직 함수 | 조건 평가, 상태 머신 전이, 데이터 변환 |
| API 모드 핸들러 | `bufApiExecute`, `bufApiSleep` 등 (의존성 Mock 처리) |
| 에러 코드 반환 | 유효하지 않은 파라미터 → 올바른 에러 코드 |
| 구조체 변환 유틸리티 | C++ ↔ C 구조체 변환 (`ApiBufferApiUtil.cpp`) |
| 다중 조건 트리 평가 | `ApiBufferMultiConditionJudgment` 로직 |

### 테스트 어려운 영역

| 대상 | 이유 |
|------|------|
| `Motion_Process` 실시간 동작 | RT 환경(RTX64/Xenomai) 의존 |
| `OslCreateEvent`, `OslWaitForSingleObject` | OSL 런타임 의존 |
| `imdll_SendAndReceive` | IMDll 공유 라이브러리 의존 |
| 실제 축 모션 결과 | WMX3 엔진 구동 환경 필요 |

---

## 2. CMake FetchContent로 gtest 설정

```cmake
# tests/CMakeLists.txt
cmake_minimum_required(VERSION 3.14)
project({{Module}}Tests)

include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/v1.14.0.zip
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
# Windows: gtest가 공유 런타임을 사용하지 않도록
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

add_executable({{Module}}Test
    test_{{module}}_funcs.cpp
    test_{{module}}_util.cpp
    # Mock 구현 파일
    mocks/MockOsl.cpp
    mocks/MockImLib.cpp
)

target_link_libraries({{Module}}Test
    GTest::gtest_main
    GTest::gmock_main
    {{Module}}TestLib       # 테스트 대상 라이브러리 (정적)
)

target_include_directories({{Module}}Test PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/{{Module}}
    ${CMAKE_SOURCE_DIR}/tests/mocks
)

include(GoogleTest)
gtest_discover_tests({{Module}}Test)
```

---

## 3. IMLib/OSL 의존성 모킹 전략

### 3.1 인터페이스 추상화 (래퍼 헤더)

테스트에서는 실제 OSL/IMLib 함수를 Mock으로 대체합니다.

```c
// tests/mocks/MockOsl.h
#ifdef WMX3_TEST_MODE
    // 테스트 모드: Mock 함수로 대체
    #define OslSleep(ms)              MockOslSleep(ms)
    #define OslCreateEvent(a,b,c,d)   MockOslCreateEvent(a,b,c,d)
    #define OslSetEvent(h)            MockOslSetEvent(h)
    #define OslCloseHandle(h)         MockOslCloseHandle(h)
    #define OslWaitForSingleObject(h,t) MockOslWaitForSingleObject(h,t)

    // Mock 함수 선언
    #ifdef __cplusplus
    extern "C" {
    #endif
    void MockOslSleep(unsigned int ms);
    void* MockOslCreateEvent(void* a, int b, int c, const char* name);
    void MockOslSetEvent(void* handle);
    void MockOslCloseHandle(void* handle);
    int MockOslWaitForSingleObject(void* handle, unsigned int timeout);
    #ifdef __cplusplus
    }
    #endif
#endif
```

### 3.2 gmock 기반 Mock 클래스

```cpp
// tests/mocks/MockOsl.cpp
#include "gtest/gtest.h"
#include "gmock/gmock.h"

class MockOslInterface {
public:
    MOCK_METHOD(void, Sleep, (unsigned int ms));
    MOCK_METHOD(void*, CreateEvent, (void* a, int b, int c, const char* name));
    MOCK_METHOD(void, SetEvent, (void* handle));
};

// 전역 Mock 객체 (C 링크 함수에서 참조)
MockOslInterface* g_mockOsl = nullptr;

extern "C" void MockOslSleep(unsigned int ms) {
    if (g_mockOsl) g_mockOsl->Sleep(ms);
}
extern "C" void* MockOslCreateEvent(void* a, int b, int c, const char* name) {
    return g_mockOsl ? g_mockOsl->CreateEvent(a, b, c, name) : (void*)1;
}
```

---

## 4. extern "C" 링크 패턴

C로 작성된 RTDLL 함수를 C++ 테스트 파일에서 호출할 때 필요합니다.

```cpp
// tests/test_apibuffer_funcs.cpp
extern "C" {
    // ApiBuffer 내부 함수 선언 (테스트 대상)
    #include "ApiBuffer.h"
    #include "ApiBuffer_Funcs.h"
    #include "ApiBuffer_Util.h"
}

#include "gtest/gtest.h"
#include "gmock/gmock.h"
```

전역 데이터도 extern으로 접근:
```cpp
extern "C" {
    extern APIBUFFER_DATA __ApiBufferData__;
}
```

---

## 5. 테스트 구조: Arrange → Act → Assert

```cpp
// tests/test_apibuffer_util.cpp
#include "gtest/gtest.h"

extern "C" {
    #include "ApiBuffer.h"
    #include "ApiBuffer_Util.h"
}

class ApiBufferUtilTest : public ::testing::Test {
protected:
    APIBUFFER_DATA testData;

    void SetUp() override {
        // Arrange: 테스트 데이터 초기화
        memset(&testData, 0, sizeof(testData));
    }

    void TearDown() override {
        // 정리 작업
    }
};

TEST_F(ApiBufferUtilTest, ExecuteApiBuffer_ValidChannel_ReturnsSuccess) {
    // Arrange
    AB_CHANNEL_SELECTION channelSel;
    channelSel.channelCount = 1;
    channelSel.channel[0] = 0;

    // 큐 컨트롤러 Mock 설정
    // ...

    // Act
    int ret = ExecuteApiBuffer(&testData, &channelSel, 0);

    // Assert
    EXPECT_EQ(ret, WMX3_API_ERROR_NONE);
}
```

---

## 6. API 모드 핸들러 테스트 패턴

```cpp
// tests/test_apibuffer_funcs.cpp
#include "gtest/gtest.h"

extern "C" {
    #include "ApiBuffer.h"
    #include "ApiBuffer_Funcs.h"
    #include "IMLib.h"
}

// 테스트용 mParam 구조체 빌더
static PIM_LIB_MPARAM BuildMParam(PAPIBUFFER_DATA pData) {
    static IM_LIB_MPARAM mparam;
    memset(&mparam, 0, sizeof(mparam));
    mparam.mParam = pData;
    return &mparam;
}

TEST(ApiBufferFuncsTest, bufApiGetBlockCount_NullQueueCtrl_ReturnsError) {
    // Arrange
    APIBUFFER_DATA data;
    memset(&data, 0, sizeof(data));
    data.pAllQueueCtrl = NULL;  // 의도적으로 NULL 설정

    IM_LIB_MPARAM mparam;
    mparam.mParam = &data;

    IM_API_CMD_HEADER cmdHeader = {};
    IM_API_RESP_HEADER respHeader = {};

    unsigned int channel = 0;

    // Act
    int ret = bufApiGetBlockCount(NULL, &mparam, &cmdHeader, &respHeader, &channel);

    // Assert
    EXPECT_EQ(ret, AB_API_ERROR_INVALID_BUFF_CTRL);
    EXPECT_EQ(respHeader.res, IM_API_RESP_FAILED);
}

TEST(ApiBufferFuncsTest, bufApiSleep_ZeroTime_ReturnsSuccessImmediately) {
    // Arrange
    APIBUFFER_DATA data;
    memset(&data, 0, sizeof(data));

    IM_LIB_QUEUE_CTRL queueCtrl = {};
    queueCtrl.curQueueId = 1;

    IM_LIB_MPARAM mparam;
    mparam.mParam = &data;
    mparam.queCtrl = &queueCtrl;

    IM_API_CMD_HEADER cmdHeader = {};
    IM_API_RESP_HEADER respHeader = {};

    unsigned int sleepTime = 0;

    // Act
    int ret = bufApiSleep(NULL, &mparam, &cmdHeader, &respHeader, &sleepTime);

    // Assert
    EXPECT_EQ(ret, 0);
    EXPECT_EQ(respHeader.res, IM_API_RESP_SUCCESS);
}
```

---

## 7. 조건 평가 로직 테스트 패턴

```cpp
// tests/test_multi_condition.cpp
#include "gtest/gtest.h"

extern "C" {
    #include "ApiBuffer.h"
    #include "ApiBuffer_Util.h"
}

TEST(MultiConditionTest, AlwaysTrue_ReturnsTrue) {
    // Arrange
    APIBUFFER_DATA data;
    memset(&data, 0, sizeof(data));

    AB_MULTI_CONDITION condition;
    memset(&condition, 0, sizeof(condition));

    // AlwaysTrue 단일 리프 노드 설정
    condition.rootIdx = 0;
    condition.nodeCount = 1;
    condition.nodes[0].type = AB_CONDITION_NODE_TYPE_LEAF;
    condition.nodes[0].condition.type = AB_CONDITION_TYPE_ALWAYS_TRUE;
    condition.nodes[0].parent = -1;
    condition.nodes[0].childCount = 0;

    // Act
    int err = WMX3_API_ERROR_NONE;
    int result = ApiBufferMultiConditionJudgment(&data, &condition, &err);

    // Assert
    EXPECT_TRUE(result);
    EXPECT_EQ(err, WMX3_API_ERROR_NONE);
}

TEST(MultiConditionTest, NeverTrue_ReturnsFalse) {
    // Arrange
    APIBUFFER_DATA data;
    memset(&data, 0, sizeof(data));

    AB_MULTI_CONDITION condition;
    memset(&condition, 0, sizeof(condition));

    condition.rootIdx = 0;
    condition.nodeCount = 1;
    condition.nodes[0].type = AB_CONDITION_NODE_TYPE_LEAF;
    condition.nodes[0].condition.type = AB_CONDITION_TYPE_NEVER_TRUE;
    condition.nodes[0].parent = -1;

    // Act
    int err = WMX3_API_ERROR_NONE;
    int result = ApiBufferMultiConditionJudgment(&data, &condition, &err);

    // Assert
    EXPECT_FALSE(result);
    EXPECT_EQ(err, WMX3_API_ERROR_NONE);
}

TEST(MultiConditionTest, InvalidTree_GateNodeNoChild_ReturnsError) {
    // Arrange
    APIBUFFER_DATA data;
    memset(&data, 0, sizeof(data));

    AB_MULTI_CONDITION condition;
    memset(&condition, 0, sizeof(condition));

    // AND 게이트이지만 자식이 없는 잘못된 트리
    condition.rootIdx = 0;
    condition.nodeCount = 1;
    condition.nodes[0].type = AB_CONDITION_NODE_TYPE_AND;
    condition.nodes[0].childCount = 0;  // 오류: AND 게이트에 자식 없음
    condition.nodes[0].parent = -1;

    // Act
    int err = WMX3_API_ERROR_NONE;
    ApiBufferMultiConditionJudgment(&data, &condition, &err);

    // Assert
    EXPECT_EQ(err, AB_API_ERROR_GATE_NODE_HAS_NO_CHILD);
}
```

---

## 8. 상태 머신 전이 테스트 패턴

```cpp
// tests/test_state_machine.cpp
#include "gtest/gtest.h"

extern "C" {
    #include "ApiBuffer.h"
    #include "ApiBuffer_Util.h"
    // 내부 상태 머신 함수
}

TEST(ApiBufferStateMachine, IfLevel_Increment_OnIfEntry) {
    // Arrange
    APIBUFFER_DATA data;
    memset(&data, 0, sizeof(data));

    int buffIdx = 1;
    EXPECT_EQ(data.buff[buffIdx].curIfLevel, 0);

    // Act: If 블록 진입 시 레벨 증가 시뮬레이션
    data.buff[buffIdx].curIfLevel++;

    // Assert
    EXPECT_EQ(data.buff[buffIdx].curIfLevel, 1);
}

TEST(ApiBufferStateMachine, SkipLevel_SetOnFalseCondition) {
    // Arrange
    APIBUFFER_DATA data;
    memset(&data, 0, sizeof(data));

    int buffIdx = 1;
    data.buff[buffIdx].curIfLevel = 1;

    // Act: 조건이 거짓일 때 skipLevel 설정
    data.buff[buffIdx].skipLevel = data.buff[buffIdx].curIfLevel;

    // Assert
    EXPECT_EQ(data.buff[buffIdx].skipLevel, 1);
}
```

---

## 9. 테스트 불가 영역 처리 원칙

| 원칙 | 설명 |
|------|------|
| RT 의존성 격리 | `OslSleep`, `OslCreateEvent` 등은 Mock으로 교체 |
| 통합 테스트 분리 | RT 환경이 필요한 테스트는 별도 통합 테스트 스위트로 분리 |
| 경계값 우선 | 채널 범위(0, 254, 255), 에러 코드, NULL 포인터 등 경계값 집중 테스트 |
| 순수 로직 추출 | RT 의존성이 있는 함수에서 순수 로직을 별도 함수로 분리하여 테스트 |

---

## 10. 프로젝트 구조 예시

```
wmx3_module_{{module}}/
├── {{Module}}/              ← 프로덕션 코드 (C99)
├── {{Module}}Api/           ← 프로덕션 코드 (C++11)
└── tests/
    ├── CMakeLists.txt
    ├── mocks/
    │   ├── MockOsl.h/cpp    ← OSL 함수 Mock
    │   └── MockImLib.h/cpp  ← IMLib 함수 Mock
    ├── test_{{module}}_funcs.cpp
    ├── test_{{module}}_util.cpp
    └── test_multi_condition.cpp
```
