/*******************************************************************************
*
* {{MODULE_NAME}}_Funcs.c
*
* API 모드 핸들러 디스패처
* 각 API 함수 호출 시 실행되는 핸들러 함수 정의
*
*******************************************************************************/

#include "stdlib.h"
#include <stdio.h>
#include "WMX3OslIMDef.h"
#include "Osl.h"
#include "IMLib.h"
#include "{{MODULE_NAME}}.h"
#include "WMX3EngineDef.h"
#include "{{MODULE_NAME}}_Util.h"
#include "WMX3ApiDef.h"

/* API 핸들러 함수 시그니처 매크로 */
#define WMX3_API_PARAM void* lParam, void* mParam, IM_API_CMD_HEADER* pApiCmd, IM_API_RESP_HEADER* pApiResp, void* pData

/* API 오류 반환 매크로 */
#define WMX3_API_RETURN_ERROR(argErr, argSize) \
    pApiResp->res = IM_API_RESP_FAILED; \
    pApiResp->size = argSize; \
    pApiResp->err = argErr; \
    return pApiResp->err;

/* API 성공 반환 매크로 */
#define WMX3_API_RETURN_SUCCESS(argSize) \
    pApiResp->res = IM_API_RESP_SUCCESS; \
    pApiResp->size = argSize; \
    return 0;

/*------------------------------------------------------------------------------
 버전 조회 핸들러
------------------------------------------------------------------------------*/
int IM_API {{module_name_snake}}ApiGetVersion(WMX3_API_PARAM) {
    unsigned char *pData_buf = (unsigned char *)pData;

    int *pMajorVersion    = (int*)&pData_buf[0];
    int *pMinorVersion    = (int*)&pData_buf[sizeof(int)];
    int *pRevisionVersion = (int*)&pData_buf[sizeof(int) + sizeof(int)];
    int *pFixVersion      = (int*)&pData_buf[sizeof(int) + sizeof(int) + sizeof(int)];

    *pMajorVersion    = WMX3_ENGINE_MAJOR_VERSION;
    *pMinorVersion    = WMX3_ENGINE_MINOR_VERSION;
    *pRevisionVersion = {{MODULE_NAME_UPPER}}_REVISION_VERSION;
    *pFixVersion      = {{MODULE_NAME_UPPER}}_FIX_VERSION;

    WMX3_API_RETURN_SUCCESS(sizeof(int) + sizeof(int) + sizeof(int) + sizeof(int));
}

/*
 * 여기에 모듈 고유 API 핸들러 함수 구현
 *
 * 패턴 예시:
 *
 * int IM_API {{module_name_snake}}ApiDoSomething(WMX3_API_PARAM) {
 *     PIM_LIB_MPARAM lmParam = (PIM_LIB_MPARAM)mParam;
 *     P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = (P{{MODULE_NAME_UPPER}}_DATA)lmParam->mParam;
 *     int* pInputParam = (int*)pData;
 *     int ret;
 *
 *     // 여기에 처리 로직 구현
 *     ret = Do{{MODULE_NAME}}Something(p{{MODULE_NAME}}Data, *pInputParam);
 *     if (ret) {
 *         WMX3_API_RETURN_ERROR(ret, 0);
 *     }
 *
 *     WMX3_API_RETURN_SUCCESS(0);
 * }
 */

/*------------------------------------------------------------------------------
 상태 업데이트 타입 반환
 - 메인 인터럽트(id==0)에서만 업데이트, 나머지는 스킵
------------------------------------------------------------------------------*/
IM_LIB_STATUS_UPDATE_TYPE IM_API {{module_name_snake}}ApiStatusUpdateType(void* lParam, void* sParam) {
    PWMX3_STATUS_FUNC_LPARAM pslParam = (PWMX3_STATUS_FUNC_LPARAM)lParam;

    if (pslParam->pMpData->id == 0) {
        return IM_LIB_STATUS_UPDATE_TYPE_SINGLE;
    }

    return IM_LIB_STATUS_UPDATE_TYPE_SKIP;
}

/*------------------------------------------------------------------------------
 상태 업데이트 핸들러
------------------------------------------------------------------------------*/
int IM_API {{module_name_snake}}ApiUpdateStatus(void* lParam, void* sParam, void* pData) {
    PWMX3_STATUS_FUNC_LPARAM slParam     = (PWMX3_STATUS_FUNC_LPARAM)lParam;
    PWMX3_MP_ALL_AXIS_IO_DATA pAiData    = (PWMX3_MP_ALL_AXIS_IO_DATA)slParam->allAxisIoData;
    PWMX3_MP_DATA pMpData                = slParam->pMpData;
    P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = (P{{MODULE_NAME_UPPER}}_DATA)sParam;
    P{{MODULE_NAME_UPPER}}_STATUS_DATA pStatus = (P{{MODULE_NAME_UPPER}}_STATUS_DATA)pData;

    /*
     * 여기에 상태 업데이트 로직 구현
     * pStatus 필드를 p{{MODULE_NAME}}Data의 현재 상태로 채움
     */

    return 0;
}

#undef WMX3_API_PARAM
#undef WMX3_API_RETURN_ERROR
#undef WMX3_API_RETURN_SUCCESS
