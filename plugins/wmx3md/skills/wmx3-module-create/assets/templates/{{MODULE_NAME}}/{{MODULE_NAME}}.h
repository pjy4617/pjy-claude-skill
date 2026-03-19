/*******************************************************************************
*
* {{MODULE_NAME}}.h
*
* 내부 메인 헤더 - 모듈 데이터 구조체 정의
* {{MODULE_NAME}} RTDLL 내부에서만 사용
*
*******************************************************************************/

#ifndef WMX3_{{MODULE_NAME_UPPER}}_RTDLL_H
#define WMX3_{{MODULE_NAME_UPPER}}_RTDLL_H

#define _USE_MATH_DEFINES
#include <math.h>
#include "WMX3OslIMDef.h"
#include "Osl.h"
#include "IMDef.h"
#include "IMLib.h"
#include "{{MODULE_NAME}}ApiLocal.h"
#include "{{MODULE_NAME}}ApiPub.h"
#include "WMX3ApiDef.h"
#include "WMX3MPInterface.h"

/*
 * 여기에 모듈 내부 상수 정의
 * 예:
 *   #define WMX3_{{MODULE_PREFIX}}_SOME_CONSTANT  100
 *   #define WMX3_{{MODULE_PREFIX}}_WAIT_EVENT_NAME _OSL_T("WMX3_{{MODULE_PREFIX}}_WaitEvt")
 */

/*
 * {{MODULE_NAME}} 모듈 내부 오류 코드
 */
typedef enum {
    {{MODULE_NAME_UPPER}}_ERROR_NONE = 0,

    {{MODULE_NAME_UPPER}}_ERROR_INIT_FAILED,
    {{MODULE_NAME_UPPER}}_ERROR_INVALID_SECURITY_CODE,

    {{MODULE_NAME_UPPER}}_ERROR_CODE_SIZE
} {{MODULE_NAME_UPPER}}_ERROR_CODE, *P{{MODULE_NAME_UPPER}}_ERROR_CODE;

/*
 * 여기에 모듈 내부 데이터 구조체 정의
 * 필요에 따라 채널별 데이터, 내부 상태 등을 추가
 *
 * 예:
 *   typedef struct {
 *       OSL_HANDLE someEventHandle;
 *       unsigned char someFlag;
 *       int someValue;
 *   } {{MODULE_NAME_UPPER}}_CHANNEL_DATA, *P{{MODULE_NAME_UPPER}}_CHANNEL_DATA;
 */

/*
 * {{MODULE_NAME}} 모듈 메인 데이터 구조체
 */
typedef struct {

    /*---------------------------------------------------------------------------
     공통 데이터
    ---------------------------------------------------------------------------*/
    PWMX3_MP_ALL_AXIS_IO_DATA pMpAiData;    /* MP, Axis, IO 데이터 포인터 */

    /*---------------------------------------------------------------------------
     퍼블릭 데이터
    ---------------------------------------------------------------------------*/
    {{MODULE_NAME_UPPER}}_PUB_DATA pubData;  /* 외부 모듈이 접근 가능한 퍼블릭 데이터 */

    /*---------------------------------------------------------------------------
     프라이빗 데이터
    ---------------------------------------------------------------------------*/
    /*
     * 여기에 모듈 고유 프라이빗 데이터 필드 추가
     * 예:
     *   {{MODULE_NAME_UPPER}}_CHANNEL_DATA channelData[MAX_CHANNEL];
     *   int someInternalState;
     */

} {{MODULE_NAME_UPPER}}_DATA, *P{{MODULE_NAME_UPPER}}_DATA;

#endif
