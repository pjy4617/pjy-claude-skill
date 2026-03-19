/*******************************************************************************
*
* {{MODULE_NAME}}_Motion.c
*
* WMX3 RT 모듈 필수 진입점 6개 + 선택적 진입점 스텁
*
* 필수 진입점:
*   Motion_ModuleId    - 모듈 ID 및 라이선스 코드 반환
*   Motion_ModuleInfo  - 모듈 정보 반환
*   Motion_Setup       - API 핸들러 및 상태 함수 등록
*   Motion_Init        - 모듈 초기화
*   Motion_Cleanup     - 모듈 정리
*   Motion_Process     - 주기적 처리 (매 제어 주기 호출)
*
*******************************************************************************/

#include "stdio.h"
#include "WMX3EngineDef.h"
#include "WMX3Motion.h"
#include "IMLib.h"
#include "{{MODULE_NAME}}.h"
#include "{{MODULE_NAME}}ApiLocal.h"
#include "{{MODULE_NAME}}_Funcs.h"
#include "{{MODULE_NAME}}_Util.h"
#include "{{MODULE_NAME}}_PubFuncs.h"
#include "{{MODULE_NAME}}_Event.h"

/* 모듈 전역 데이터 인스턴스 */
{{MODULE_NAME_UPPER}}_DATA __{{MODULE_NAME}}Data__;

/*==============================================================================
 초기화 및 종료 루틴
==============================================================================*/

/* 모듈 ID와 라이선스 코드를 반환 */
Motion_API Motion_ModuleId(char licCode[WMX3_RTDLL_SDK_LIC_CODE_SIZE]) {
    /* 여기에 라이선스 코드 설정 (SoftServo Systems에서 발급) */
    snprintfs(licCode, WMX3_RTDLL_SDK_LIC_CODE_SIZE, "XXXXXXXXXXXXXXXXXXXXXXXX");
    /* 여기에 할당받은 모듈 ID 반환 */
    /* return WMX3_MODULE_ID_{{MODULE_NAME_UPPER}}; */
    return 0; /* 임시값: 실제 모듈 ID로 교체 필요 */
}

/* 모듈 정보를 반환 */
Motion_API Motion_ModuleInfo(WMX3_MODULE_INFO* pInfo) {
    pInfo->majorVersion    = WMX3_ENGINE_MAJOR_VERSION;
    pInfo->minorVersion    = WMX3_ENGINE_MINOR_VERSION;
    pInfo->revisionVersion = {{MODULE_NAME_UPPER}}_REVISION_VERSION;
    pInfo->fixVersion      = {{MODULE_NAME_UPPER}}_FIX_VERSION;

    pInfo->memory = sizeof({{MODULE_NAME_UPPER}}_DATA);

    stprintfs(pInfo->moduleName, OSL_CountOf(pInfo->moduleName), _OSL_T("{{MODULE_NAME}}"));
    stprintfs(pInfo->moduleDesc, OSL_CountOf(pInfo->moduleDesc), _OSL_T("{{MODULE_NAME}} 모듈"));

    return 0;
}

/* API 핸들러 함수 및 상태 업데이트 함수 등록 */
Motion_API Motion_Setup(IM_LIB_MODULE_FUNCS* pModuleFunc, IM_LIB_STATUS_FUNCS* pStatusFunc, WMX3_MODULE_SETTING* pSetting, WMX3_MODULE_CONFIG* pConfig) {
    P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = &__{{MODULE_NAME}}Data__;

    if (pModuleFunc != NULL) {
        /* 버전 조회 핸들러 등록 */
        pModuleFunc->apiFuncs[{{MODULE_NAME_UPPER}}_API_MODE_GET_VERSION] = {{module_name_snake}}ApiGetVersion;

        /*
         * 여기에 모듈 고유 API 핸들러 등록
         * 예:
         *   pModuleFunc->apiFuncs[{{MODULE_NAME_UPPER}}_API_MODE_DO_SOMETHING] = {{module_name_snake}}ApiDoSomething;
         */

        pModuleFunc->apiFuncNum = {{MODULE_NAME_UPPER}}_API_MODE_SIZE;
        pModuleFunc->mParam     = p{{MODULE_NAME}}Data;
    }

    if (pStatusFunc != NULL) {
        /* 상태 업데이트 함수 등록 */
        pStatusFunc->func[{{MODULE_NAME_UPPER}}_STATUS_CHANNEL_MAIN_STATUS].utFunc = {{module_name_snake}}ApiStatusUpdateType;
        pStatusFunc->func[{{MODULE_NAME_UPPER}}_STATUS_CHANNEL_MAIN_STATUS].sFuncs = {{module_name_snake}}ApiUpdateStatus;
        pStatusFunc->func[{{MODULE_NAME_UPPER}}_STATUS_CHANNEL_MAIN_STATUS].sParam = p{{MODULE_NAME}}Data;
        pStatusFunc->numOfFunc = {{MODULE_NAME_UPPER}}_STATUS_CHANNEL_SIZE;
    }

    if (pConfig != NULL) {
        OslSetProperty(pConfig->hOslProperty);
        OslSetStdOut(pConfig->stdoutType);
        pConfig->sharedMemory = &p{{MODULE_NAME}}Data->pubData;
    }

    /*
     * 여기에 퍼블릭 함수 포인터 초기화
     * 예:
     *   p{{MODULE_NAME}}Data->pubData.doSomething = {{MODULE_NAME}}DoSomethingFunc;
     */

    return 0;
}

/* 모듈 초기화 - 보안 코드 검증, 리소스 할당, 다른 모듈 참조 설정 */
Motion_API Motion_Init(WMX3_MP_ALL_AXIS_IO_DATA* pAllAxisIoData, WMX3_MODULE_INIT_DATA* pInitData) {
    P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = &__{{MODULE_NAME}}Data__;

    /* 보안 코드 검증 */
    /* if (!IM_UtilVerifySecurityCode(WMX3_MODULE_ID_{{MODULE_NAME_UPPER}}, pInitData->securityCode)) { */
    /*     return {{MODULE_NAME_UPPER}}_ERROR_INVALID_SECURITY_CODE; */
    /* } */

    /* 다른 모듈의 퍼블릭 데이터 포인터 획득 */
    /* 예:
     *   p{{MODULE_NAME}}Data->pCmPubData = (PCORE_MOTION_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_CORE_MOTION];
     *   p{{MODULE_NAME}}Data->pEvPubData = (PEVENT_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_EVENT];
     */

    /* MP/Axis/IO 데이터 포인터 저장 */
    p{{MODULE_NAME}}Data->pMpAiData = pAllAxisIoData;

    /*
     * 여기에 모듈 초기화 로직 구현
     * - 이벤트 핸들 생성
     * - 내부 상태 초기화
     * - 이벤트 모듈에 커스텀 이벤트 등록 등
     */

    return 0;
}

/* 모듈 정리 - Motion_Init에서 할당한 리소스 해제 */
Motion_API Motion_Cleanup() {
    P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = &__{{MODULE_NAME}}Data__;

    /*
     * 여기에 리소스 해제 로직 구현
     * - 이벤트 핸들 닫기
     * - 동적 할당 메모리 해제 등
     */

    OslReleaseStdOut();

    return 0;
}

/* 주기적 처리 루틴 - 매 제어 주기마다 호출됨 */
Motion_API Motion_Process(WMX3_MP_DATA* pMP) {
    P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = &__{{MODULE_NAME}}Data__;

    /*
     * 여기에 주기적 처리 로직 구현
     * - 조건 판정
     * - 상태 업데이트
     * - 이벤트 처리 등
     */

    return 0;
}

/*==============================================================================
 선택적 진입점 (필요 시 주석 해제하여 구현)
 CoreMotion 등의 참조 모듈과 동일한 패턴
==============================================================================*/

/* 통신 시작/종료 루틴 */
//Motion_API Motion_PreStartCommProc(WMX3_MP_DATA* pMP, WMX3_MODULE_CONFIG* pConfig) {
//    /* 여기에 통신 시작 전 처리 구현 */
//    return 0;
//}

//Motion_API Motion_PostStartCommProc(WMX3_MP_DATA* pMP, WMX3_MODULE_CONFIG* pConfig) {
//    /* 여기에 통신 시작 후 처리 구현 */
//    return 0;
//}

//Motion_API Motion_PreStopCommProc(WMX3_MP_DATA* pMP) {
//    /* 여기에 통신 종료 전 처리 구현 */
//    return 0;
//}

//Motion_API Motion_PostStopCommProc(WMX3_MP_DATA* pMP) {
//    /* 여기에 통신 종료 후 처리 구현 */
//    return 0;
//}

/* 종료 루틴 (Cleanup 이전) */
//Motion_API Motion_Closing() {
//    /* 여기에 종료 직전 처리 구현 */
//    return 0;
//}

/* 주기적 처리 세분화 루틴 */
//Motion_API Motion_PreCommunicate(WMX3_MP_DATA* pMP) {
//    /* 여기에 통신 전 주기 처리 구현 */
//    return 0;
//}

//Motion_API Motion_PostCommunicate(WMX3_MP_DATA* pMP) {
//    /* 여기에 통신 후 주기 처리 구현 */
//    return 0;
//}

//Motion_API Motion_PreFeedbackProc(WMX3_MP_DATA* pMP) {
//    /* 여기에 피드백 처리 전 구현 */
//    return 0;
//}

//Motion_API Motion_PostFeedbackProc(WMX3_MP_DATA* pMP) {
//    /* 여기에 피드백 처리 후 구현 */
//    return 0;
//}

//Motion_API Motion_PreProcess(WMX3_MP_DATA* pMP) {
//    /* 여기에 Process 이전 주기 처리 구현 */
//    return 0;
//}

//Motion_API Motion_PostProcess(WMX3_MP_DATA* pMP) {
//    /* 여기에 Process 이후 주기 처리 구현 */
//    return 0;
//}

//Motion_API Motion_PreCommandProc(WMX3_MP_DATA* pMP) {
//    /* 여기에 커맨드 처리 전 구현 */
//    return 0;
//}

//Motion_API Motion_PostCommandProc(WMX3_MP_DATA* pMP) {
//    /* 여기에 커맨드 처리 후 구현 */
//    return 0;
//}
