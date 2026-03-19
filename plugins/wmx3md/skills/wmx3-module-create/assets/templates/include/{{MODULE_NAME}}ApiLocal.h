/*******************************************************************************
*
* {{MODULE_NAME}}ApiLocal.h
*
* IPC 데이터 구조 - API 모드 열거형, 상태/오류 구조체
* C++ API 라이브러리와 RTDLL 간 데이터 전송에 사용
*
* 이 헤더는 {{MODULE_NAME}}Api 및 {{MODULE_NAME}} 프로젝트에서만 포함해야 함
*
*******************************************************************************/

#ifndef WMX3_{{MODULE_NAME_UPPER}}_API_LOCAL_H
#define WMX3_{{MODULE_NAME_UPPER}}_API_LOCAL_H

#include "WMX3ApiDef.h"
#include "{{MODULE_NAME}}ApiDef.h"

/*
 * {{MODULE_NAME}} API 함수 식별 코드 (API 모드)
 * C++ API 함수와 RTDLL 핸들러를 연결하는 열거형
 */
typedef enum {
    {{MODULE_NAME_UPPER}}_API_MODE_GET_VERSION,     /* 버전 조회 */

    /*
     * 여기에 모듈 고유 API 모드 추가
     * 예:
     *   {{MODULE_NAME_UPPER}}_API_MODE_DO_SOMETHING,
     *   {{MODULE_NAME_UPPER}}_API_MODE_GET_DATA,
     */

    {{MODULE_NAME_UPPER}}_API_MODE_SIZE             /* 이 열거형의 크기 */
} {{MODULE_NAME_UPPER}}_API_MODE, *P{{MODULE_NAME_UPPER}}_API_MODE;

/*
 * {{MODULE_NAME}} 단일 채널 상태 구조체
 */
typedef struct {
    {{MODULE_NAME_UPPER}}_STATE state;  /* 모듈 상태 */

    /*
     * 여기에 상태 필드 추가
     * 예:
     *   int someValue;
     *   unsigned char errorFlag;
     */
} {{MODULE_NAME_UPPER}}_STATUS, *P{{MODULE_NAME_UPPER}}_STATUS;

/*
 * {{MODULE_NAME}} 전체 상태 데이터 구조체
 */
typedef struct {
    {{MODULE_NAME_UPPER}}_STATUS status;    /* 모듈 상태 */

    /*
     * 여기에 추가 상태 필드 정의
     */
} {{MODULE_NAME_UPPER}}_STATUS_DATA, *P{{MODULE_NAME_UPPER}}_STATUS_DATA;

/*
 * 여기에 추가 IPC 데이터 구조체 정의
 * API 모드별 입출력 데이터 구조체 등
 */

#endif
