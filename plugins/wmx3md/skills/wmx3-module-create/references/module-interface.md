# WMX3 모듈 엔트리포인트 인터페이스 규격

WMX3 엔진은 공유 라이브러리(RTDLL/SO)를 `dlopen`으로 로딩하고, 아래에 정의된 표준 진입점 함수를 통해 모듈과 상호작용합니다.

---

## 1. 필수 진입점 (6개)

모든 WMX3 모듈은 반드시 아래 6개 함수를 구현해야 합니다. `export` 파일에 `global:` 섹션으로 명시합니다.

### 1.1 Motion_ModuleId

```c
Motion_API Motion_ModuleId(char licCode[WMX3_RTDLL_SDK_LIC_CODE_SIZE]);
```

| 항목 | 설명 |
|------|------|
| 역할 | 모듈 고유 ID와 라이선스 코드를 반환 |
| 반환값 | `WMX3_MODULE_ID_*` 상수 (예: `WMX3_MODULE_ID_APIBUFFER`) |
| 호출 시점 | 엔진이 라이브러리를 로딩한 직후 |

**구현 예시:**
```c
Motion_API Motion_ModuleId(char licCode[WMX3_RTDLL_SDK_LIC_CODE_SIZE]) {
    snprintfs(licCode, WMX3_RTDLL_SDK_LIC_CODE_SIZE, "{{LICENSE_CODE}}");
    return WMX3_MODULE_ID_{{MODULE_ID_CONSTANT}};
}
```

- `licCode`는 Soft Servo Systems로부터 발급받은 24자 라이선스 문자열
- 모듈 ID는 `WMX3EngineDef.h`에 정의된 `WMX3_MODULE_ID_*` 열거값

---

### 1.2 Motion_ModuleInfo

```c
Motion_API Motion_ModuleInfo(WMX3_MODULE_INFO* pInfo);
```

| 항목 | 설명 |
|------|------|
| 역할 | 버전 정보, 메모리 요구량, 모듈 이름/설명 설정 |
| 반환값 | 0 (성공) |
| 호출 시점 | `Motion_ModuleId` 직후 |

**구현 예시:**
```c
Motion_API Motion_ModuleInfo(WMX3_MODULE_INFO* pInfo) {
    pInfo->majorVersion    = WMX3_ENGINE_MAJOR_VERSION;
    pInfo->minorVersion    = WMX3_ENGINE_MINOR_VERSION;
    pInfo->revisionVersion = {{MODULE}}_REVISION_VERSION;
    pInfo->fixVersion      = {{MODULE}}_FIX_VERSION;

    pInfo->memory = sizeof({{MODULE}}_DATA);  // 모듈 데이터 구조체 크기

    stprintfs(pInfo->moduleName, OSL_CountOf(pInfo->moduleName), _OSL_T("{{ModuleName}}"));
    stprintfs(pInfo->moduleDesc, OSL_CountOf(pInfo->moduleDesc), _OSL_T("{{Module description}}"));
    return 0;
}
```

- `pInfo->memory`: 엔진이 해당 크기만큼 공유 메모리를 할당하므로 반드시 정확한 크기 지정

---

### 1.3 Motion_Setup

```c
Motion_API Motion_Setup(
    IM_LIB_MODULE_FUNCS*  pModuleFunc,
    IM_LIB_STATUS_FUNCS*  pStatusFunc,
    WMX3_MODULE_SETTING*  pSetting,
    WMX3_MODULE_CONFIG*   pConfig
);
```

| 항목 | 설명 |
|------|------|
| 역할 | API 함수 테이블 등록, 상태 함수 등록, 공유 메모리 포인터 설정, PubData 초기화 |
| 반환값 | 0 (성공) |
| 호출 시점 | `Motion_ModuleInfo` 직후, `Motion_Init` 이전 |

**apiFuncs[] 등록 패턴:**
```c
Motion_API Motion_Setup(IM_LIB_MODULE_FUNCS* pModuleFunc,
                        IM_LIB_STATUS_FUNCS* pStatusFunc,
                        WMX3_MODULE_SETTING* pSetting,
                        WMX3_MODULE_CONFIG*  pConfig)
{
    P{{MODULE}}_DATA p{{Module}}Data = &__{{Module}}Data__;

    if (pModuleFunc != NULL) {
        // API 모드 번호를 인덱스로 핸들러 함수 등록
        pModuleFunc->apiFuncs[{{MODULE}}_API_MODE_{{FUNCTION}}] = {{prefix}}Api{{Function}};
        // ... 추가 API 모드 등록 ...

        pModuleFunc->apiFuncNum = {{MODULE}}_API_MODE_SIZE;  // 총 API 모드 수
        pModuleFunc->mParam     = p{{Module}}Data;           // 모듈 데이터 포인터
        pModuleFunc->option     = IM_LIB_MODULE_PARAM_OPTION_QUEUE_CTRL;  // 큐 제어 옵션

        // 큐 제어기 포인터 획득 (QUEUE_CTRL 옵션 사용 시)
        p{{Module}}Data->pAllQueueCtrl =
            (PIM_LIB_ALL_QUEUE_CTRL)pModuleFunc->optParam[0].mParam;
    }

    if (pStatusFunc != NULL) {
        pStatusFunc->func[{{MODULE}}_STATUS_CHANNEL_{{STATUS}}].utFunc = {{prefix}}ApiStatusUpdateType;
        pStatusFunc->func[{{MODULE}}_STATUS_CHANNEL_{{STATUS}}].sFuncs = {{prefix}}ApiUpdateStatus;
        pStatusFunc->func[{{MODULE}}_STATUS_CHANNEL_{{STATUS}}].sParam = p{{Module}}Data;
        pStatusFunc->numOfFunc = {{MODULE}}_STATUS_CHANNEL_SIZE;
    }

    if (pConfig != NULL) {
        OslSetProperty(pConfig->hOslProperty);
        OslSetStdOut(pConfig->stdoutType);
        pConfig->sharedMemory = &p{{Module}}Data->pubData;  // PubData를 공유 메모리로 노출
    }

    // PubData 함수 포인터 초기화 (다른 모듈이 직접 호출 가능한 함수)
    p{{Module}}Data->pubData.execFunc  = {{Module}}ExecFunc;
    p{{Module}}Data->pubData.haltFunc  = {{Module}}HaltFunc;

    return 0;
}
```

- `pConfig->sharedMemory = &pubData`: 이 포인터가 다른 모듈의 `pAllAxisIoData->userMemory[MODULE_ID]`로 접근됨
- `apiFuncNum`은 반드시 실제 등록한 API 모드 수(열거형 `_SIZE` 값)와 일치해야 함

---

### 1.4 Motion_Init

```c
Motion_API Motion_Init(
    WMX3_MP_ALL_AXIS_IO_DATA* pAllAxisIoData,
    WMX3_MODULE_INIT_DATA*    pInitData
);
```

| 항목 | 설명 |
|------|------|
| 역할 | 모듈 초기화: 이벤트 핸들 생성, 의존 모듈 포인터 획득, 보안 코드 검증 |
| 반환값 | 0 (성공), 비0 (에러 코드) |
| 호출 시점 | 엔진 통신 시작 직전, 모든 모듈의 `Motion_Setup` 완료 후 |

**구현 예시:**
```c
Motion_API Motion_Init(WMX3_MP_ALL_AXIS_IO_DATA* pAllAxisIoData,
                       WMX3_MODULE_INIT_DATA*    pInitData)
{
    P{{MODULE}}_DATA p{{Module}}Data = &__{{Module}}Data__;

    // 보안 코드 검증 (필수)
    if (!IM_UtilVerifySecurityCode(WMX3_MODULE_ID_{{MODULE_ID}}, pInitData->securityCode)) {
        return {{MODULE}}_ERROR_INVALID_SECURITY_CODE;
    }

    // OS 이벤트 핸들 생성 (Wait 기능 사용 시)
    for (int i = 0; i < OSL_CountOf(p{{Module}}Data->buff); i++) {
        p{{Module}}Data->buff[i].eventHandle = OslCreateEvent(NULL, OSL_TRUE, OSL_FALSE, name);
        if (p{{Module}}Data->buff[i].eventHandle == NULL) {
            return {{MODULE}}_ERROR_INIT_FAILED;
        }
    }

    // 의존 모듈의 PubData 포인터 획득
    p{{Module}}Data->pCmPubData =
        (PCORE_MOTION_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_CORE_MOTION];
    p{{Module}}Data->pEvPubData =
        (PEVENT_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_EVENT];
    p{{Module}}Data->pIoPubData =
        (PIO_CONTROL_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_IO];
    p{{Module}}Data->pUmPubData =
        (PUSER_MEMORY_CONTROL_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_USER_MEMORY];

    // 전체 IO 데이터 포인터 보관
    p{{Module}}Data->pMpAiData = pAllAxisIoData;

    return 0;
}
```

- `pAllAxisIoData->userMemory[MODULE_ID]`는 각 모듈의 `pConfig->sharedMemory`가 등록한 PubData
- 포인터가 NULL일 수 있음 (해당 모듈이 로드되지 않은 경우) → 반드시 NULL 체크 후 사용

---

### 1.5 Motion_Cleanup

```c
Motion_API Motion_Cleanup(void);
```

| 항목 | 설명 |
|------|------|
| 역할 | 모듈 자원 해제: 이벤트 핸들 해제, 표준 출력 해제 |
| 반환값 | 0 (성공) |
| 호출 시점 | 엔진 종료 시, `Motion_Init`과 쌍으로 호출 |

**구현 예시:**
```c
Motion_API Motion_Cleanup(void) {
    P{{MODULE}}_DATA p{{Module}}Data = &__{{Module}}Data__;

    for (int i = 0; i < OSL_CountOf(p{{Module}}Data->buff); i++) {
        if (p{{Module}}Data->buff[i].eventHandle != NULL) {
            OslSetEvent(p{{Module}}Data->buff[i].eventHandle);    // 대기 중인 스레드 해제
            OslCloseHandle(p{{Module}}Data->buff[i].eventHandle);
            p{{Module}}Data->buff[i].eventHandle = NULL;
        }
    }

    OslReleaseStdOut();
    return 0;
}
```

---

### 1.6 Motion_Process

```c
Motion_API Motion_Process(WMX3_MP_DATA* pMP);
```

| 항목 | 설명 |
|------|------|
| 역할 | 매 제어 사이클마다 호출되는 주기적 처리 함수 |
| 반환값 | 0 (성공) |
| 호출 시점 | 엔진 제어 루프마다 (수백 µs ~ 수 ms 주기) |
| 주의 | RT 안전성 필수: malloc/free 금지, 재귀 금지, 블로킹 금지 |

**구현 예시 (ApiBuffer 패턴):**
```c
Motion_API Motion_Process(WMX3_MP_DATA* pMP) {
    P{{MODULE}}_DATA p{{Module}}Data = &__{{Module}}Data__;

    for (int i = 1; i < OSL_CountOf(p{{Module}}Data->buff); i++) {
        // 해당 인터럽트 ID에 속하는 채널만 처리
        if (p{{Module}}Data->pAllQueueCtrl->ctrls[i]->status.state != IM_LIB_QUEUE_STATE_IDLE
            && p{{Module}}Data->buff[i].interruptId == pMP->id)
        {
            // 대기 조건 평가
            if (p{{Module}}Data->buff[i].waitingFlag) {
                if (ConditionJudgment(p{{Module}}Data, i)) {
                    OslSetEvent(p{{Module}}Data->buff[i].eventHandle);
                }
            }
            // 감시 처리
            ProcessWatch(p{{Module}}Data, i);
        }
    }
    return 0;
}
```

- `pMP->id`: 현재 모션 프로세서 ID (멀티-MP 환경에서 채널 분리에 사용)

---

## 2. 선택적 진입점

CoreMotion의 `export` 파일을 기준으로 추가로 지원 가능한 진입점 목록입니다. 필요한 경우에만 구현하며, 구현하지 않는 함수는 주석 처리합니다.

| 함수명 | 호출 시점 | 용도 |
|--------|-----------|------|
| `Motion_Closing` | 엔진 종료 요청 직전 | 종료 전 정리 작업 |
| `Motion_PreStartCommProc` | 통신 시작 직전 | 통신 전 초기화 |
| `Motion_PostStartCommProc` | 통신 시작 직후 | 통신 후 설정 |
| `Motion_PreStopCommProc` | 통신 중지 직전 | 통신 종료 준비 |
| `Motion_PostStopCommProc` | 통신 중지 직후 | 통신 종료 정리 |
| `Motion_PreCommunicate` | 통신 처리 직전 (매 사이클) | 통신 전 처리 |
| `Motion_PostCommunicate` | 통신 처리 직후 (매 사이클) | 통신 후 처리 |
| `Motion_PreFeedbackProc` | 피드백 처리 직전 (매 사이클) | 피드백 전 처리 |
| `Motion_PostFeedbackProc` | 피드백 처리 직후 (매 사이클) | 피드백 후 처리 |
| `Motion_PreProcess` | `Motion_Process` 직전 (매 사이클) | 프로세스 전 처리 |
| `Motion_PostProcess` | `Motion_Process` 직후 (매 사이클) | 프로세스 후 처리 |
| `Motion_PreCommandProc` | 명령 처리 직전 (매 사이클) | 명령 전 처리 |
| `Motion_PostCommandProc` | 명령 처리 직후 (매 사이클) | 명령 후 처리 |

**선택적 진입점 시그니처:**
```c
Motion_API Motion_Closing(void);
Motion_API Motion_PreStartCommProc(WMX3_MP_DATA* pMP, WMX3_MODULE_CONFIG* pConfig);
Motion_API Motion_PostStartCommProc(WMX3_MP_DATA* pMP, WMX3_MODULE_CONFIG* pConfig);
Motion_API Motion_PreStopCommProc(WMX3_MP_DATA* pMP);
Motion_API Motion_PostStopCommProc(WMX3_MP_DATA* pMP);
Motion_API Motion_PreCommunicate(WMX3_MP_DATA* pMP);
Motion_API Motion_PostCommunicate(WMX3_MP_DATA* pMP);
Motion_API Motion_PreFeedbackProc(WMX3_MP_DATA* pMP);
Motion_API Motion_PostFeedbackProc(WMX3_MP_DATA* pMP);
Motion_API Motion_PreProcess(WMX3_MP_DATA* pMP);
Motion_API Motion_PostProcess(WMX3_MP_DATA* pMP);
Motion_API Motion_PreCommandProc(WMX3_MP_DATA* pMP);
Motion_API Motion_PostCommandProc(WMX3_MP_DATA* pMP);
```

---

## 3. export 파일 규칙

Linux에서 심볼 가시성을 제어하는 버전 스크립트입니다. `ApiBuffer/export` 예시:

```
{
    global:
        Motion_ModuleId;
        Motion_ModuleInfo;
        Motion_Setup;
        Motion_Init;
        Motion_Cleanup;
        Motion_Process;
    local:*;
};
```

- `global:` 섹션에는 구현한 진입점만 나열
- `local:*;`는 나머지 모든 심볼을 숨김 (정보 은닉)
- 선택적 진입점을 구현했으면 반드시 `global:` 섹션에 추가
- CoreMotion처럼 더 많은 진입점을 구현한 경우 해당 함수명을 모두 나열

---

## 4. 전역 데이터 패턴

모듈 데이터는 전역 변수 하나로 관리합니다:

```c
// {{MODULE}}_Motion.c
{{MODULE}}_DATA __{{Module}}Data__;

// 다른 파일에서 참조 시
extern {{MODULE}}_DATA __{{Module}}Data__;
```

- 모든 진입점 함수에서 `&__{{Module}}Data__`를 통해 접근
- API 핸들러 함수는 `mParam` 파라미터로 포인터를 전달받아 사용

---

## 5. Motion_API 매크로

```c
// Windows RTX64: __declspec(dllexport)
// Linux: __attribute__((visibility("default"))) 등 플랫폼별 정의
Motion_API  // WMX3Motion.h에 정의
```
