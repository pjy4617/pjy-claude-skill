/*******************************************************************************
*
* {{MODULE_NAME}}ApiDef.h
*
* 공유 상수, 열거형, 구조체 정의
* C++ API 라이브러리와 RTDLL 간 데이터 전송에 사용
*
* 이 헤더는 {{MODULE_NAME}}Api, {{MODULE_NAME}}, 기타 모듈 RTDLL 프로젝트에서만 포함해야 함
*
*******************************************************************************/

#ifndef WMX3_{{MODULE_NAME_UPPER}}_API_DEF_H
#define WMX3_{{MODULE_NAME_UPPER}}_API_DEF_H

/* Linux에서 __stdcall 정의 */
#ifndef _WIN32
#ifndef __stdcall
#define __stdcall
#endif
#endif

/* 모듈 버전 정의 */
#define {{MODULE_NAME_UPPER}}_REVISION_VERSION  0   /* 리비전 버전 */
#define {{MODULE_NAME_UPPER}}_FIX_VERSION       0   /* 픽스 버전 */

/*
 * 여기에 모듈 공유 상수 정의
 * 예:
 *   #ifndef WMX3_{{MODULE_PREFIX}}_MAX_CHANNEL
 *   #define WMX3_{{MODULE_PREFIX}}_MAX_CHANNEL 255
 *   #endif
 */

/*
 * {{MODULE_NAME}} API 함수 오류 코드
 * 오류 코드 베이스 값은 다른 모듈과 충돌하지 않도록 할당받아야 함
 */
typedef enum {
    /* 여기에 모듈 고유 오류 코드 열거형 정의 */
    /* 예: {{MODULE_NAME_UPPER}}_API_ERROR_SOME_ERROR = 0x000XX000, */

    {{MODULE_NAME_UPPER}}_API_ERROR_SIZE    /* 이 열거형의 크기 */
} {{MODULE_NAME_UPPER}}_API_ERROR_CODE, *P{{MODULE_NAME_UPPER}}_API_ERROR_CODE;

/*
 * {{MODULE_NAME}} API 상태 코드
 */
typedef enum {
    /* 여기에 모듈 상태 열거형 정의 */
    /* 예: {{MODULE_NAME_UPPER}}_STATE_IDLE, */
    /* 예: {{MODULE_NAME_UPPER}}_STATE_ACTIVE, */

    {{MODULE_NAME_UPPER}}_STATE_SIZE        /* 이 열거형의 크기 */
} {{MODULE_NAME_UPPER}}_STATE, *P{{MODULE_NAME_UPPER}}_STATE;

/*
 * {{MODULE_NAME}} API 상태 채널
 */
typedef enum {
    {{MODULE_NAME_UPPER}}_STATUS_CHANNEL_MAIN_STATUS,   /* 메인 상태 채널 */

    {{MODULE_NAME_UPPER}}_STATUS_CHANNEL_SIZE
} {{MODULE_NAME_UPPER}}_STATUS_CHANNEL, *P{{MODULE_NAME_UPPER}}_STATUS_CHANNEL;

/*
 * 여기에 추가 열거형 및 구조체 정의
 * 예: 이벤트 출력 함수 열거형, 조건 타입 등
 */

#endif
