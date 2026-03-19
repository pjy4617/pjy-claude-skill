/*******************************************************************************
*
* {{MODULE_NAME}}Api_ApiLog.cpp
*
* API 로그 변환 구현
* API 호출 로그 데이터를 사람이 읽을 수 있는 문자열로 변환
*
*******************************************************************************/

#include "stdio.h"
#include "WMX3OslIMDef.h"
#include "IMDll.h"
#include "WMX3EngineDef.h"
#include "{{MODULE_NAME}}Api.h"
#include "{{MODULE_NAME}}ApiLocal.h"
#include "{{MODULE_NAME}}ApiPub.h"
#include "{{MODULE_NAME}}ApiUtil.h"
#include "WMX3ApiUtil.h"
#include "WMX3Api_ApiLogUtil.h"
#include "WMX3ApiDef.h"

namespace wmx3Api {
    extern IM_VERSION_INFO {{module_name}}Version;
}

/*------------------------------------------------------------------------------
 내부 로그 → 문자열 변환 (native TCHAR)
------------------------------------------------------------------------------*/
static WMX3APIFUNC ApiLogToStringNative(
    unsigned char* pLogData,
    unsigned int logDataSize,
    IM_TCHAR *pString,
    unsigned int size)
{
    PIM_API_LOG_INFO pApiLogInfo = (PIM_API_LOG_INFO)pLogData;
    bool printNoErrMsg = false;
    unsigned char* pData;
    int cur = 0;
    int strSize = (int)size;

    if (pLogData == NULL || pString == NULL) {
        return wmx3Api::ErrorCode::ArgumentIsNull;
    }

    if (logDataSize < sizeof(IM_API_LOG_INFO)
        || pApiLogInfo->dataLen + sizeof(IM_API_LOG_INFO) > logDataSize
        || strSize <= 0) {
        return wmx3Api::ErrorCode::ArgumentOutOfRange;
    }

    if (pApiLogInfo->majorVer != wmx3Api::{{module_name}}Version.major
        || pApiLogInfo->minorVer != wmx3Api::{{module_name}}Version.minor
        || pApiLogInfo->revision != wmx3Api::{{module_name}}Version.revision) {
        return wmx3Api::ErrorCode::ModuleVersionMismatch;
    }

    /* 여기에 모듈 ID 검증 추가 */
    /* if (pApiLogInfo->moduleId != WMX3_MODULE_ID_{{MODULE_NAME_UPPER}}) { */
    /*     return wmx3Api::ErrorCode::InvalidModuleId; */
    /* } */

    pData = (unsigned char*)(pApiLogInfo + 1);

    switch (pApiLogInfo->mode) {
    case {{MODULE_NAME_UPPER}}_API_MODE_GET_VERSION:
        {
            if (pApiLogInfo->type == 0) {
                cur = wmx3Api::appendString(pString, strSize, cur, _IM_T("GetVersion"));
            } else {
                int* pMajVer = (int*)&pData[0];
                int* pMinVer = (int*)&pData[sizeof(int)];
                int* pRevVer = (int*)&pData[sizeof(int) * 2];
                int* pFixVer = (int*)&pData[sizeof(int) * 3];

                cur = wmx3Api::appendString(pString, strSize, cur, _IM_T("GetVersion: "));
                if (pApiLogInfo->resp.err == 0) {
                    cur = wmx3Api::appendString(pString, size, cur,
                        _IM_T("v%d.%d.%d.%d"), *pMajVer, *pMinVer, *pRevVer, *pFixVer);
                }
            }
            break;
        }

    /*
     * 여기에 모듈 고유 API 모드별 로그 변환 추가
     *
     * 패턴 예시:
     * case {{MODULE_NAME_UPPER}}_API_MODE_DO_SOMETHING:
     *     {
     *         cur = wmx3Api::appendString(pString, strSize, cur, _IM_T("DoSomething: "));
     *         if (pApiLogInfo->type == 0) {
     *             int param = *(int*)pData;
     *             cur = wmx3Api::appendString(pString, strSize, cur, _IM_T("param: %d"), param);
     *         } else {
     *             printNoErrMsg = true;
     *         }
     *         break;
     *     }
     */

    default:
        if (pApiLogInfo->type == 0) {
            cur = wmx3Api::appendString(pString, strSize, cur,
                _IM_T("{{MODULE_NAME}} 알 수 없는 API(%d)"), pApiLogInfo->mode);
        } else {
            cur = wmx3Api::appendString(pString, strSize, cur,
                _IM_T("{{MODULE_NAME}} 알 수 없는 API(%d): "), pApiLogInfo->mode);
            printNoErrMsg = true;
        }
        break;
    }

    if (cur == -1) {
        return wmx3Api::ErrorCode::BufferTooSmall;
    }

    if (pApiLogInfo->type == 1
        && (pApiLogInfo->resp.err != 0 || printNoErrMsg)
        && cur >= 0 && cur < strSize) {
        wmx3Api::{{MODULE_NAME}}::ErrorToString(
            wmx3Api::convert{{MODULE_NAME}}ErrorCode(pApiLogInfo->resp.err),
            &pString[cur], strSize - cur);
    }

    return wmx3Api::ErrorCode::None;
}

/*------------------------------------------------------------------------------
 공개 API: char 버전
------------------------------------------------------------------------------*/
WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::ApiLogToString(
    unsigned char* pLogData,
    unsigned int logDataSize,
    char *pString,
    unsigned int size)
{
    char charBuf[1024];
    char* pcharBuf;
    IM_TCHAR tcharBuf[1024];
    size_t convChars;
    int ret;

    ret = ApiLogToStringNative(pLogData, logDataSize, tcharBuf, IM_CountOf(tcharBuf));
    if (ret != ErrorCode::None) return ret;

    pcharBuf = tchar2char(&convChars, charBuf, IM_CountOf(charBuf), tcharBuf);
    if (pcharBuf == NULL) return ErrorCode::StringConversionError;

    size = IM_MIN(size, sizeof(charBuf));
    ret = snprintfs(pString, size, "%s", pcharBuf);
    if (ret == -1) return ErrorCode::BufferTooSmall;

    return ErrorCode::None;
}

/*------------------------------------------------------------------------------
 공개 API: wchar_t 버전
------------------------------------------------------------------------------*/
WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::ApiLogToString(
    unsigned char* pLogData,
    unsigned int logDataSize,
    wchar_t *pString,
    unsigned int size)
{
    wchar_t wcharBuf[1024];
    wchar_t* pwcharBuf;
    IM_TCHAR tcharBuf[1024];
    size_t convChars;
    int ret;

    ret = ApiLogToStringNative(pLogData, logDataSize, tcharBuf, IM_CountOf(tcharBuf));
    if (ret != ErrorCode::None) return ret;

    pwcharBuf = tchar2wchar(&convChars, wcharBuf, IM_CountOf(wcharBuf), tcharBuf);
    if (pwcharBuf == NULL) return ErrorCode::StringConversionError;

    size = IM_MIN(size, IM_CountOf(wcharBuf));
    ret = swprintfs(pString, size, L"%ls", pwcharBuf);
    if (ret == -1) return ErrorCode::BufferTooSmall;

    return ErrorCode::None;
}
