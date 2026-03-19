/**
 * test_{{MODULE_NAME}}_Funcs.cpp
 *
 * {{MODULE_NAME}} 모듈 API 핸들러 단위 테스트
 *
 * 테스트 대상:
 *   - {{MODULE_NAME}}_Funcs.c  : API 모드별 핸들러 함수
 *   - {{MODULE_NAME}}_Util.c   : 유틸리티 / 조건 판단 함수
 *   - {{MODULE_NAME}}_PubFuncs.c : 공개 함수 (옵션)
 *
 * 테스트 불가 항목 (RT 의존 — 제외):
 *   - {{MODULE_NAME}}_Motion.c  : Motion_Process (RT 주기 처리)
 *   - {{MODULE_NAME}}_Event.c   : 인터럽트 컨텍스트 핸들러
 *
 * 빌드:
 *   cmake -B build/test -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Debug .
 *   cmake --build build/test -j$(nproc)
 *   cd build/test && ctest --output-on-failure
 */

#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <cstring>

// C 모듈을 C++ 테스트에서 링크할 때 반드시 extern "C" 블록 사용
extern "C" {
    #include "{{MODULE_NAME}}.h"
    #include "{{MODULE_NAME}}_Funcs.h"
    #include "{{MODULE_NAME}}_Util.h"
}

#include "mock_{{MODULE_NAME}}.h"

using ::testing::Return;
using ::testing::_;
using ::testing::NiceMock;

// =============================================================================
// 테스트 픽스처: {{MODULE_NAME}} API 핸들러 테스트
// =============================================================================
class {{MODULE_NAME}}Suite : public ::testing::Test {
protected:
    void SetUp() override {
        // 테스트 시작 전 모듈 데이터 구조체 초기화
        std::memset(&moduleData_, 0, sizeof(moduleData_));
    }

    void TearDown() override {
        // 각 테스트 종료 후 정리 (필요 시 구현)
    }

    // 테스트용 모듈 데이터 구조체 ({{MODULE_NAME}}.h 에 정의된 타입으로 교체)
    // 예시: {{MODULE_NAME}}_DATA moduleData_;
    // 실제 구조체 타입으로 교체하세요.
    struct { int dummy; } moduleData_;
};

// =============================================================================
// 테스트 케이스 1: Execute 핸들러 — 정상 동작
// TEST 이름 규칙: {스위트명}.{핸들러명}_{조건}_{기댓값}
// =============================================================================
TEST_F({{MODULE_NAME}}Suite, Execute_ValidParam_ReturnsSuccess) {
    // Arrange — 유효한 실행 파라미터 설정
    // (실제 파라미터 구조체 타입으로 교체하세요)
    // {{MODULE_NAME}}_EXECUTE_PARAM param = {};
    // param.channel = 0;

    // Act — API 핸들러 직접 호출 (mParam에 파라미터 포인터 전달)
    // int result = mmApiExecute(&moduleData_, 0, &param, NULL);
    int result = 0; // TODO: 실제 핸들러 호출로 교체

    // Assert — 성공 반환값 확인
    EXPECT_EQ(0, result);
}

// =============================================================================
// 테스트 케이스 2: Execute 핸들러 — NULL 파라미터 방어
// =============================================================================
TEST_F({{MODULE_NAME}}Suite, Execute_NullParam_ReturnsError) {
    // Arrange — 파라미터 없음 (NULL)

    // Act — NULL mParam 전달 시 에러 반환 확인
    // int result = mmApiExecute(&moduleData_, 0, NULL, NULL);
    int result = -1; // TODO: 실제 핸들러 호출로 교체

    // Assert — 에러 반환 (0이 아닌 값)
    EXPECT_NE(0, result);
}

// =============================================================================
// 테스트 케이스 3: Execute 핸들러 — 채널 범위 초과
// =============================================================================
TEST_F({{MODULE_NAME}}Suite, Execute_InvalidChannel_ReturnsError) {
    // Arrange — 유효한 파라미터이나 채널 번호 범위 초과
    // {{MODULE_NAME}}_EXECUTE_PARAM param = {};

    // Act — 최대 채널 수 이상의 채널 번호 전달
    // int result = mmApiExecute(&moduleData_, MAX_{{MODULE_NAME}}_CHANNEL, &param, NULL);
    int result = -1; // TODO: 실제 핸들러 호출로 교체

    // Assert — 에러 반환
    EXPECT_NE(0, result);
}

// =============================================================================
// 테스트 픽스처: {{MODULE_NAME}} 유틸리티 함수 테스트
// =============================================================================
class {{MODULE_NAME}}UtilSuite : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
};

// =============================================================================
// 테스트 케이스 4: 조건 판단 함수 — AlwaysTrue 조건
// =============================================================================
TEST_F({{MODULE_NAME}}UtilSuite, ConditionJudgment_AlwaysTrue_ReturnsTrue) {
    // Arrange — AlwaysTrue 조건 설정
    // {{MODULE_NAME}}_CONDITION cond = {};
    // cond.type = CONDITION_ALWAYS_TRUE;

    // Act — 조건 판단 함수 호출
    // int result = mmEvaluateCondition(&cond, NULL);
    int result = 1; // TODO: 실제 함수 호출로 교체

    // Assert — AlwaysTrue는 항상 1 반환
    EXPECT_EQ(1, result);
}

// =============================================================================
// 테스트 케이스 5: 조건 판단 함수 — NeverTrue 조건
// =============================================================================
TEST_F({{MODULE_NAME}}UtilSuite, ConditionJudgment_NeverTrue_ReturnsFalse) {
    // Arrange — NeverTrue 조건 설정
    // {{MODULE_NAME}}_CONDITION cond = {};
    // cond.type = CONDITION_NEVER_TRUE;

    // Act — 조건 판단 함수 호출
    // int result = mmEvaluateCondition(&cond, NULL);
    int result = 0; // TODO: 실제 함수 호출로 교체

    // Assert — NeverTrue는 항상 0 반환
    EXPECT_EQ(0, result);
}

// =============================================================================
// 테스트 케이스 6: Mock 사용 예시 — IMLib SendCommand 호출 검증
// gmock EXPECT_CALL로 의존성 호출 횟수 및 인자 검증
// =============================================================================
TEST_F({{MODULE_NAME}}Suite, Execute_CallsImLibOnce_WhenValid) {
    // Arrange — Mock 객체 생성 및 기대 동작 설정
    NiceMock<MockImLib> mockImLib;

    // SendCommand가 정확히 1회, 임의 인자로 호출되면 0(성공) 반환
    EXPECT_CALL(mockImLib, SendCommand(_, _, _))
        .Times(1)
        .WillOnce(Return(0));

    // Act — Mock을 주입한 핸들러 호출
    // (함수 포인터 또는 의존성 주입 방식으로 mock 연결)
    // int result = mmApiExecuteWithImLib(&moduleData_, 0, &param, &mockImLib);

    // Assert — 현재는 플레이스홀더; 실제 구현 후 교체
    SUCCEED(); // TODO: 실제 검증으로 교체
}
