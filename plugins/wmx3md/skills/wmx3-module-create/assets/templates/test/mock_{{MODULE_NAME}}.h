#pragma once
/**
 * mock_{{MODULE_NAME}}.h
 *
 * {{MODULE_NAME}} 모듈 단위 테스트용 Mock 클래스 정의
 *
 * 포함 내용:
 *   - IImLib   : IMLib 인터페이스 (SendCommand, GetStatus, FlushQueue 등)
 *   - IOslLib  : OSL 인터페이스 (뮤텍스, 이벤트, 시간)
 *   - MockImLib  : IImLib의 gmock 구현
 *   - MockOslLib : IOslLib의 gmock 구현
 *
 * 사용법:
 *   #include "mock_{{MODULE_NAME}}.h"
 *
 *   NiceMock<MockImLib> mockImLib;
 *   EXPECT_CALL(mockImLib, SendCommand(_, _, _)).WillOnce(Return(0));
 *
 * 주의:
 *   - Mock은 테스트 대상 함수가 실제로 사용하는 의존성만 정의하세요.
 *   - 사용하지 않는 Mock 메서드 호출은 NiceMock으로 경고 억제 가능합니다.
 *   - UNIT_TEST 가드로 프로덕션 빌드에서 이 헤더가 포함되지 않도록 하세요.
 */

#ifndef UNIT_TEST
#error "mock_{{MODULE_NAME}}.h 는 단위 테스트 빌드에서만 포함해야 합니다 (UNIT_TEST 정의 필요)."
#endif

#include <gmock/gmock.h>

// =============================================================================
// IImLib 인터페이스
// WMX3 IMLib의 모듈 간 통신 함수를 추상화합니다.
// 테스트 대상 코드가 사용하는 IMLib 함수를 이 인터페이스에 추가하세요.
// =============================================================================
class IImLib {
public:
    virtual ~IImLib() = default;

    /**
     * @brief 다른 모듈에 커맨드를 전송합니다.
     * @param moduleId   대상 모듈 ID
     * @param apiMode    API 모드 번호 (ApiLocal.h 열거형 값)
     * @param pInData    입력 데이터 포인터 (void*)
     * @return 0: 성공, 비0: 에러 코드
     */
    virtual int SendCommand(int moduleId, int apiMode, void* pInData) = 0;

    /**
     * @brief 모듈 상태를 조회합니다.
     * @param moduleId  대상 모듈 ID
     * @param pOutData  출력 데이터 포인터 (void*)
     * @return 0: 성공, 비0: 에러 코드
     */
    virtual int GetStatus(int moduleId, void* pOutData) = 0;

    /**
     * @brief API 큐를 비웁니다.
     * @param moduleId  대상 모듈 ID
     * @param channel   대상 채널 번호
     * @return 0: 성공, 비0: 에러 코드
     */
    virtual int FlushQueue(int moduleId, int channel) = 0;

    /**
     * @brief 큐에 API 블록을 추가합니다.
     * @param moduleId  대상 모듈 ID
     * @param channel   대상 채널 번호
     * @param apiMode   API 모드 번호
     * @param pData     블록 데이터 포인터
     * @param dataSize  블록 데이터 크기 (바이트)
     * @return 0: 성공, 비0: 에러 코드 (큐 꽉 참 등)
     */
    virtual int EnqueueApiBlock(int moduleId, int channel,
                                int apiMode, void* pData, int dataSize) = 0;
};

// =============================================================================
// MockImLib — IImLib의 gmock 구현
// =============================================================================
class MockImLib : public IImLib {
public:
    // MOCK_METHOD(반환타입, 함수명, (인자목록), (한정자))
    MOCK_METHOD(int, SendCommand,
                (int moduleId, int apiMode, void* pInData),
                (override));

    MOCK_METHOD(int, GetStatus,
                (int moduleId, void* pOutData),
                (override));

    MOCK_METHOD(int, FlushQueue,
                (int moduleId, int channel),
                (override));

    MOCK_METHOD(int, EnqueueApiBlock,
                (int moduleId, int channel, int apiMode,
                 void* pData, int dataSize),
                (override));
};

// =============================================================================
// IOslLib 인터페이스
// WMX3 OSL(OS Abstraction Layer)의 동기화 및 시간 함수를 추상화합니다.
// RT 컨텍스트 외부(단위 테스트 환경)에서 호출 가능한 함수만 포함합니다.
// =============================================================================
class IOslLib {
public:
    virtual ~IOslLib() = default;

    /**
     * @brief 뮤텍스를 잠급니다.
     * @param mutexId  뮤텍스 ID
     * @return 0: 성공, 비0: 에러
     */
    virtual int MutexLock(int mutexId) = 0;

    /**
     * @brief 뮤텍스를 해제합니다.
     * @param mutexId  뮤텍스 ID
     * @return 0: 성공, 비0: 에러
     */
    virtual int MutexUnlock(int mutexId) = 0;

    /**
     * @brief 이벤트를 설정합니다(신호 전달).
     * @param eventId  이벤트 ID
     * @return 0: 성공, 비0: 에러
     */
    virtual int EventSet(int eventId) = 0;

    /**
     * @brief 이벤트를 지정 시간 대기합니다.
     * @param eventId      이벤트 ID
     * @param timeoutMsec  타임아웃 (밀리초), 0이면 무한 대기
     * @return 0: 이벤트 수신, 1: 타임아웃, 비0: 에러
     */
    virtual int EventWait(int eventId, unsigned int timeoutMsec) = 0;

    /**
     * @brief 현재 시각을 밀리초 단위로 반환합니다.
     * @return 현재 시각 (밀리초)
     */
    virtual unsigned long long GetCurrentTimeMsec() = 0;
};

// =============================================================================
// MockOslLib — IOslLib의 gmock 구현
// =============================================================================
class MockOslLib : public IOslLib {
public:
    MOCK_METHOD(int, MutexLock,
                (int mutexId),
                (override));

    MOCK_METHOD(int, MutexUnlock,
                (int mutexId),
                (override));

    MOCK_METHOD(int, EventSet,
                (int eventId),
                (override));

    MOCK_METHOD(int, EventWait,
                (int eventId, unsigned int timeoutMsec),
                (override));

    MOCK_METHOD(unsigned long long, GetCurrentTimeMsec,
                (),
                (override));
};
