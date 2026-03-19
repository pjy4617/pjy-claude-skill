/*******************************************************************************
*
* {{MODULE_NAME}}_Funcs.h
*
* API 모드 핸들러 함수 선언
*
*******************************************************************************/

#ifndef WMX3_{{MODULE_NAME_UPPER}}_FUNCS_H
#define WMX3_{{MODULE_NAME_UPPER}}_FUNCS_H
#include "IMLib.h"

/* API 핸들러 함수 시그니처 매크로 */
#define WMX3_API_PARAM void* lParam, void* mParam, IM_API_CMD_HEADER* pApiCmd, IM_API_RESP_HEADER* pApiResp, void* pData

/* 버전 조회 핸들러 */
int IM_API {{module_name_snake}}ApiGetVersion(WMX3_API_PARAM);

/*
 * 여기에 모듈 고유 API 핸들러 함수 선언 추가
 * 예:
 *   int IM_API {{module_name_snake}}ApiDoSomething(WMX3_API_PARAM);
 *   int IM_API {{module_name_snake}}ApiGetData(WMX3_API_PARAM);
 */

/* 상태 업데이트 타입 핸들러 */
IM_LIB_STATUS_UPDATE_TYPE IM_API {{module_name_snake}}ApiStatusUpdateType(void* lParam, void* sParam);

/* 상태 업데이트 핸들러 */
int IM_API {{module_name_snake}}ApiUpdateStatus(void* lParam, void* sParam, void* pData);

#undef WMX3_API_PARAM


#endif
