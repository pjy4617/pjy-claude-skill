/*******************************************************************************
*
* {{MODULE_NAME}}_Event.c
*
* 이벤트 통합 구현
* Event 모듈과의 커스텀 이벤트 인터페이스
*
*******************************************************************************/

#include "{{MODULE_NAME}}_Event.h"

/* 커스텀 이벤트 구조체 초기화 - Motion_Init에서 호출 */
void {{MODULE_NAME}}EventSetCustomEvent(P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data, PEV_CUSTOM_EVENT_PUB event)
{
    event->setEvtDataFunc    = NULL;
    event->removedFunc       = NULL;
    event->setInputDataFunc  = NULL;
    event->setOutputDataFunc = {{MODULE_NAME}}EventSetOutputData;
    event->getInputDataFunc  = NULL;
    event->getOutputDataFunc = {{MODULE_NAME}}EventGetOutputData;
    event->triggerConditionFunc = NULL;
    event->triggeredOutputFunc  = {{MODULE_NAME}}EventTriggeredOutput;
    event->timing   = EV_CUSTOM_EVENT_TIMING_POST_CMD;
    event->context  = p{{MODULE_NAME}}Data;
}

/* 이벤트 출력 데이터 설정 */
int __stdcall {{MODULE_NAME}}EventSetOutputData(void* context,
                                                unsigned char* outputData,
                                                int outputDataSize,
                                                unsigned char* innerOutputData,
                                                int* innerOutputDataSize)
{
    P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = (P{{MODULE_NAME_UPPER}}_DATA)context;

    *innerOutputDataSize = 0;

    /*
     * 여기에 출력 데이터 유효성 검사 및 설정 로직 구현
     *
     * 패턴 예시:
     *   if (outputDataSize != sizeof(출력_데이터_타입)) {
     *       return WMX3_API_ERROR_ARGUMENT_OUT_OF_RANGE;
     *   }
     *   // 출력 데이터 복사
     *   memcpy(innerOutputData, outputData, outputDataSize);
     *   *innerOutputDataSize = outputDataSize;
     */

    return 0;
}

/* 이벤트 출력 데이터 조회 */
int __stdcall {{MODULE_NAME}}EventGetOutputData(void* context,
                                                unsigned char* innerOutputData,
                                                int innerOutputDataSize,
                                                unsigned char* outputData,
                                                int* outputDataSize)
{
    P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = (P{{MODULE_NAME_UPPER}}_DATA)context;

    *outputDataSize = 0;

    /*
     * 여기에 출력 데이터 조회 로직 구현
     *
     * 패턴 예시:
     *   if (innerOutputDataSize != sizeof(출력_데이터_타입)) {
     *       return WMX3_API_ERROR_ARGUMENT_OUT_OF_RANGE;
     *   }
     *   memcpy(outputData, innerOutputData, innerOutputDataSize);
     *   *outputDataSize = innerOutputDataSize;
     */

    return 0;
}

/* 이벤트 트리거 출력 실행 */
int __stdcall {{MODULE_NAME}}EventTriggeredOutput(void* context,
                                                  unsigned char* innerOutputData,
                                                  int innerOutputDataSize,
                                                  unsigned char rise,
                                                  EV_CUSTOM_EVENT_TIMING timing,
                                                  int interruptId)
{
    P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = (P{{MODULE_NAME_UPPER}}_DATA)context;

    if (p{{MODULE_NAME}}Data == NULL || innerOutputData == NULL) {
        return EV_TRIGGER_OUTPUT_ERROR;
    }

    /*
     * 여기에 트리거 출력 로직 구현
     * rise > 0: 이벤트 조건이 참으로 평가됨
     * rise == 0: 이벤트 조건이 거짓으로 평가됨
     *
     * 패턴 예시:
     *   if (rise) {
     *       int ret = p{{MODULE_NAME}}Data->pubData.doSomething(channel);
     *       if (ret != {{MODULE_NAME_UPPER}}_PUB_ERROR_NONE) {
     *           return EV_TRIGGER_OUTPUT_RETRY;  // 다음 주기에 재시도
     *       }
     *   }
     */

    return 0;
}
