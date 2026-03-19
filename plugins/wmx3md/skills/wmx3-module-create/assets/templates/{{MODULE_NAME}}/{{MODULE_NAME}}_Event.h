/*******************************************************************************
*
* {{MODULE_NAME}}_Event.h
*
* 이벤트 통합 함수 선언
*
*******************************************************************************/

#ifndef WMX3_{{MODULE_NAME_UPPER}}_EVENT_H
#define WMX3_{{MODULE_NAME_UPPER}}_EVENT_H

#include "EventApiPub.h"
#include "{{MODULE_NAME}}.h"

/*
 * 커스텀 이벤트 구조체 초기화
 * 함수 포인터, 데이터 포인터, 옵션을 EV_CUSTOM_EVENT_PUB에 설정
 * 설정 후 Event 모듈의 registerCustomEvent 퍼블릭 함수로 등록
 *
 * @param[in,out] p{{MODULE_NAME}}Data  {{MODULE_NAME}} 모듈 데이터 포인터
 * @param[out]    event                 이벤트 구조체 포인터
 */
void {{MODULE_NAME}}EventSetCustomEvent(P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data, PEV_CUSTOM_EVENT_PUB event);

/*
 * 이벤트 출력 데이터 설정
 * EV_CUSTOM_EVENT_PUB의 setOutputDataFunc에 등록
 */
int __stdcall {{MODULE_NAME}}EventSetOutputData(void* context,
                                                unsigned char* outputData,
                                                int outputDataSize,
                                                unsigned char* innerOutputData,
                                                int* innerOutputDataSize);

/*
 * 이벤트 출력 데이터 조회
 * EV_CUSTOM_EVENT_PUB의 getOutputDataFunc에 등록
 */
int __stdcall {{MODULE_NAME}}EventGetOutputData(void* context,
                                                unsigned char* innerOutputData,
                                                int innerOutputDataSize,
                                                unsigned char* outputData,
                                                int* outputDataSize);

/*
 * 이벤트 트리거 출력 실행
 * EV_CUSTOM_EVENT_PUB의 triggeredOutputFunc에 등록
 *
 * @returns 0                       성공
 * @returns EV_TRIGGER_OUTPUT_RETRY 다음 주기에 재시도
 * @returns EV_TRIGGER_OUTPUT_ERROR 오류
 */
int __stdcall {{MODULE_NAME}}EventTriggeredOutput(void* context,
                                                  unsigned char* innerOutputData,
                                                  int innerOutputDataSize,
                                                  unsigned char rise,
                                                  EV_CUSTOM_EVENT_TIMING timing,
                                                  int interruptId);

#endif
