/*******************************************************************************
*
* {{MODULE_NAME}}_Util.c
*
* 유틸리티 함수 구현
* {{MODULE_NAME}} 모듈 내부에서 사용하는 헬퍼 함수들
*
*******************************************************************************/

#include "Osl.h"
#include <stdio.h>
#include <string.h>
#include "WMX3OslIMDef.h"
#include "{{MODULE_NAME}}ApiLocal.h"
#include "{{MODULE_NAME}}.h"
#include "{{MODULE_NAME}}_Util.h"
#include "{{MODULE_NAME}}ApiPub.h"
#include "WMX3ApiDef.h"

/*
 * 여기에 유틸리티 함수 구현
 *
 * 일반적인 유틸리티 함수 패턴:
 *
 * 1. 파라미터 유효성 검사 함수
 *    int {{MODULE_NAME}}CheckParam(P{{MODULE_NAME_UPPER}}_DATA pData, int param) {
 *        if (pData == NULL) return {{MODULE_NAME_UPPER}}_API_ERROR_INVALID_DATA;
 *        if (param < 0 || param >= MAX_VALUE) return WMX3_API_ERROR_ARGUMENT_OUT_OF_RANGE;
 *        return WMX3_API_ERROR_NONE;
 *    }
 *
 * 2. 오류 코드 변환 함수
 *    int Convert{{MODULE_NAME}}PubErrorCode({{MODULE_NAME_UPPER}}_PUB_ERROR_CODE pubErrCode) {
 *        switch (pubErrCode) {
 *        case {{MODULE_NAME_UPPER}}_PUB_ERROR_INVALID_DATA:
 *            return {{MODULE_NAME_UPPER}}_API_ERROR_INVALID_DATA;
 *        default:
 *            return 0;
 *        }
 *    }
 *
 * 3. 모드 변경 대기 함수
 *    int {{MODULE_NAME}}_WaitForModeChange(P{{MODULE_NAME_UPPER}}_DATA pData, int timeoutMs) {
 *        int timeout = 0;
 *        while (timeout++ < timeoutMs) {
 *            OslSleep(1);
 *            // 여기에 완료 조건 판정
 *            if (완료_조건) return 0;
 *        }
 *        return {{MODULE_NAME_UPPER}}_API_ERROR_TIMEOUT;
 *    }
 */
