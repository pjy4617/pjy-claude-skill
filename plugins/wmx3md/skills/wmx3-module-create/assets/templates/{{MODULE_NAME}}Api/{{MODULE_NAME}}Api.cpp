/*******************************************************************************
*
* {{MODULE_NAME}}Api.cpp
*
* C++ API 클래스 구현
* wmx3Api::{{MODULE_NAME}} 클래스의 멤버 함수 정의
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
#include "WMX3ApiDef.h"

namespace wmx3Api {
    /* 모듈 버전 정보 */
    IM_VERSION_INFO {{module_name}}Version = {
        WMX3_ENGINE_MAJOR_VERSION,
        WMX3_ENGINE_MINOR_VERSION,
        {{MODULE_NAME_UPPER}}_REVISION_VERSION
    };

    extern char wmx3LibVerFile[];
}

/*------------------------------------------------------------------------------
 내부 초기화 / 종료
------------------------------------------------------------------------------*/

void wmx3Api::{{MODULE_NAME}}::init(WMX3Api *f) {
    wmx3Api = f;
    statChnlId = -1;

    if (wmx3Api != NULL) {
        /* 상태 채널 요청 */
        imdll_RequestStatusChannel(
            wmx3Api->dev,
            WMX3_MODULE_ID_{{MODULE_NAME_UPPER}},    /* 실제 모듈 ID로 교체 필요 */
            {{MODULE_NAME_UPPER}}_STATUS_CHANNEL_MAIN_STATUS,
            sizeof({{MODULE_NAME_UPPER}}_STATUS_DATA),
            WMX3_STATUS_COPY_SIZE,
            1,
            &statChnlId,
            &{{module_name}}Version
        );
    }

    WMX3Api::PrintToFileIfExist(wmx3LibVerFile, "{{MODULE_NAME}}Api: v%d.%d.%d.%d\n",
        WMX3_ENGINE_MAJOR_VERSION,
        WMX3_ENGINE_MINOR_VERSION,
        {{MODULE_NAME_UPPER}}_REVISION_VERSION,
        {{MODULE_NAME_UPPER}}_FIX_VERSION);
}

void wmx3Api::{{MODULE_NAME}}::close() {
    if (isSelfDev && wmx3Api != NULL) {
        imdll_FreeStatusChannelEx(wmx3Api->dev, statChnlId, 1);
        statChnlId = -1;
        wmx3Api->CloseDevice();
    }
}

/*------------------------------------------------------------------------------
 생성자 / 소멸자
------------------------------------------------------------------------------*/

wmx3Api::{{MODULE_NAME}}::{{MODULE_NAME}}(WMX3Api *f) {
    isSelfDev = false;
    init(f);
}

wmx3Api::{{MODULE_NAME}}::{{MODULE_NAME}}(const {{MODULE_NAME}}& src) {
    isSelfDev = false;
    init(src.wmx3Api);
}

wmx3Api::{{MODULE_NAME}}& wmx3Api::{{MODULE_NAME}}::operator=(const {{MODULE_NAME}}& src) {
    if (this != &src) {
        close();
        isSelfDev = false;
        init(src.wmx3Api);
    }
    return *this;
}

wmx3Api::{{MODULE_NAME}}::{{MODULE_NAME}}() {
    isSelfDev = true;
    WMX3Api *newApi = new WMX3Api();
    init(newApi);
}

wmx3Api::{{MODULE_NAME}}::~{{MODULE_NAME}}() {
    close();
}

/*------------------------------------------------------------------------------
 정적 유틸리티 함수
------------------------------------------------------------------------------*/

bool wmx3Api::{{MODULE_NAME}}::IsDeviceValid() {
    return wmx3Api != NULL && wmx3Api->IsDeviceValid();
}

WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::ErrorToString(int errCode, char *pString, unsigned int size) {
    /* 여기에 오류 코드 → 문자열 변환 로직 구현 */
    return ErrorCode::None;
}

WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::ErrorToString(int errCode, wchar_t *pString, unsigned int size) {
    /* 여기에 오류 코드 → 와이드 문자열 변환 로직 구현 */
    return ErrorCode::None;
}

WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::ApiLogToString(unsigned char* pLogData, unsigned int logDataSize, char *pString, unsigned int size) {
    /* 여기에 API 로그 → 문자열 변환 로직 구현 */
    return ErrorCode::None;
}

WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::ApiLogToString(unsigned char* pLogData, unsigned int logDataSize, wchar_t *pString, unsigned int size) {
    /* 여기에 API 로그 → 와이드 문자열 변환 로직 구현 */
    return ErrorCode::None;
}

WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::GetLibVersion(int *pMajorVersion, int *pMinorVersion, int *pRevisionVersion, int *pFixVersion) {
    if (pMajorVersion)    *pMajorVersion    = WMX3_ENGINE_MAJOR_VERSION;
    if (pMinorVersion)    *pMinorVersion    = WMX3_ENGINE_MINOR_VERSION;
    if (pRevisionVersion) *pRevisionVersion = {{MODULE_NAME_UPPER}}_REVISION_VERSION;
    if (pFixVersion)      *pFixVersion      = {{MODULE_NAME_UPPER}}_FIX_VERSION;
    return ErrorCode::None;
}

/*------------------------------------------------------------------------------
 API 함수 구현
------------------------------------------------------------------------------*/

WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::GetVersion(int *pMajorVersion, int *pMinorVersion, int *pRevisionVersion, int *pFixVersion) {
    unsigned char sendBuf[sizeof(int) * 4];
    unsigned char recvBuf[sizeof(int) * 4];
    int recvSize;
    int ret;

    if (!IsDeviceValid()) return ErrorCode::DeviceIsInvalid;

    ret = imdll_SendAndRecv(
        wmx3Api->dev,
        WMX3_MODULE_ID_{{MODULE_NAME_UPPER}},   /* 실제 모듈 ID로 교체 필요 */
        {{MODULE_NAME_UPPER}}_API_MODE_GET_VERSION,
        sendBuf, 0,
        recvBuf, sizeof(recvBuf), &recvSize,
        &{{module_name}}Version
    );

    if (ret) return convert{{MODULE_NAME}}ErrorCode(ret);

    if (pMajorVersion)    *pMajorVersion    = *(int*)&recvBuf[0];
    if (pMinorVersion)    *pMinorVersion    = *(int*)&recvBuf[sizeof(int)];
    if (pRevisionVersion) *pRevisionVersion = *(int*)&recvBuf[sizeof(int) * 2];
    if (pFixVersion)      *pFixVersion      = *(int*)&recvBuf[sizeof(int) * 3];

    return ErrorCode::None;
}

WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::GetStatus({{MODULE_NAME}}Status* pStatus) {
    {{MODULE_NAME_UPPER}}_STATUS_DATA statusData;
    int ret;

    if (!IsDeviceValid()) return ErrorCode::DeviceIsInvalid;
    if (pStatus == NULL)  return ErrorCode::ArgumentIsNull;

    ret = imdll_GetStatus(wmx3Api->dev, statChnlId, &statusData, sizeof(statusData));
    if (ret) return convert{{MODULE_NAME}}ErrorCode(ret);

    /*
     * 여기에 C 구조체 → C++ 클래스 변환 로직 구현
     * 예:
     *   pStatus->state = ({{MODULE_NAME}}State::T)statusData.status.state;
     */

    return ErrorCode::None;
}

/*
 * 여기에 추가 API 함수 구현
 *
 * 패턴 예시 (단순 명령 전송):
 *
 * WMX3APIFUNC wmx3Api::{{MODULE_NAME}}::DoSomething(int param) {
 *     unsigned char sendBuf[sizeof(int)];
 *     unsigned char recvBuf[1];
 *     int recvSize;
 *     int ret;
 *
 *     if (!IsDeviceValid()) return ErrorCode::DeviceIsInvalid;
 *
 *     *(int*)sendBuf = param;
 *
 *     ret = imdll_SendAndRecv(
 *         wmx3Api->dev,
 *         WMX3_MODULE_ID_{{MODULE_NAME_UPPER}},
 *         {{MODULE_NAME_UPPER}}_API_MODE_DO_SOMETHING,
 *         sendBuf, sizeof(sendBuf),
 *         recvBuf, sizeof(recvBuf), &recvSize,
 *         &{{module_name}}Version
 *     );
 *
 *     return convert{{MODULE_NAME}}ErrorCode(ret);
 * }
 */
