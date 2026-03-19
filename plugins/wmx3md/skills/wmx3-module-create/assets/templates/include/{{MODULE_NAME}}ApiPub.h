/*******************************************************************************
*
* {{MODULE_NAME}}ApiPub.h
*
* 퍼블릭 함수 포인터 - 다른 RT 모듈에서 참조하는 공개 인터페이스
*
* 이 헤더는 {{MODULE_NAME}} 프로젝트 및 다른 모듈 RTDLL 프로젝트에서 포함 가능
*
*******************************************************************************/

#ifndef WMX3_{{MODULE_NAME_UPPER}}_API_PUB_H
#define WMX3_{{MODULE_NAME_UPPER}}_API_PUB_H

#include "{{MODULE_NAME}}ApiDef.h"

/* 다른 RT 모듈이 접근 가능한 최대 채널 수 */
#define {{MODULE_NAME_UPPER}}_PUB_MAX_CHANNEL   255

/*
 * 퍼블릭 함수에서 사용하는 오류 코드
 */
typedef enum {
    {{MODULE_NAME_UPPER}}_PUB_ERROR_NONE,                           /* 오류 없음 */
    {{MODULE_NAME_UPPER}}_PUB_ERROR_INVALID_DATA,                   /* 유효하지 않은 데이터 */
    {{MODULE_NAME_UPPER}}_PUB_ERROR_INVALID_CHANNEL,                /* 유효하지 않은 채널 */
    {{MODULE_NAME_UPPER}}_PUB_ERROR_PREVIOUS_SETTINGS_BEING_APPLIED, /* 이전 설정 적용 중 */

    {{MODULE_NAME_UPPER}}_PUB_ERROR_SIZE
} {{MODULE_NAME_UPPER}}_PUB_ERROR_CODE, *P{{MODULE_NAME_UPPER}}_PUB_ERROR_CODE;

/*
 * 여기에 퍼블릭 함수 포인터 타입 정의
 * 다른 RT 모듈이 이 모듈의 기능을 직접 호출할 때 사용
 *
 * 예:
 *   typedef int (__stdcall *{{MODULE_NAME}}DoSomething)(int channel);
 *   typedef int (__stdcall *{{MODULE_NAME}}GetState)(int channel, {{MODULE_NAME_UPPER}}_STATE* pState);
 */

/*
 * {{MODULE_NAME}} 모듈의 퍼블릭 데이터 구조체
 * 다른 모듈이 sharedMemory를 통해 접근하는 함수 포인터 집합
 */
typedef struct {
    /*
     * 여기에 퍼블릭 함수 포인터 필드 추가
     * 예:
     *   {{MODULE_NAME}}DoSomething doSomething;
     *   {{MODULE_NAME}}GetState    getState;
     */
} {{MODULE_NAME_UPPER}}_PUB_DATA, *P{{MODULE_NAME_UPPER}}_PUB_DATA;

#endif
