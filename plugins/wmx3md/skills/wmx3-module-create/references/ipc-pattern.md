# WMX3 IPC 통신 패턴

WMX3 모듈의 IPC(프로세스간 통신)는 IMDll/IMLib 프레임워크를 통해 이루어집니다. 사용자 공간의 C++ API가 실시간 경계를 넘어 RTDLL 내의 핸들러 함수를 호출하는 전체 흐름을 설명합니다.

---

## 1. 전체 흐름

```
[사용자 앱]
  apiBuffer.Execute(0)
       │
       ▼
[ApiBufferApi.cpp - wmx3Api 레이어]
  C++ 구조체 → C 구조체 변환
  imdll_SendAndReceive(dev, moduleId=APIBUFFER, mode=EXECUTE, data, ...)
       │
       ▼
[IMDll - 공유 라이브러리 IPC 계층]
  공유 메모리 / 명령 큐를 통해 RTDLL로 전달
       │
  ══════════════ 실시간 경계 ══════════════
       │
       ▼
[ApiBuffer_Funcs.c - RTDLL 핸들러]
  bufApiExecute(lParam, mParam, pApiCmd, pApiResp, pData)
       │
       ▼
[ApiBuffer_Util.c - 실제 로직]
  ExecuteApiBuffer(pApiBufferData, pChannelSelection, interruptId)
       │
       ▼
[반환값 역방향 전파]
  에러 코드 → IPC → C++ API → int 반환값
```

---

## 2. API 모드 디스패처 구조

### 2.1 핸들러 함수 시그니처

```c
// ApiBuffer_Funcs.h
#define WMX3_API_PARAM \
    void* lParam, void* mParam, \
    IM_API_CMD_HEADER* pApiCmd, IM_API_RESP_HEADER* pApiResp, \
    void* pData

int IM_API bufApiExecute(WMX3_API_PARAM);
int IM_API bufApiHalt(WMX3_API_PARAM);
int IM_API bufApiSleep(WMX3_API_PARAM);
int IM_API bufApiWait(WMX3_API_PARAM);
// ...
```

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `lParam` | `void*` | IMLib이 전달하는 내부 파라미터 |
| `mParam` | `void*` | `PIM_LIB_MPARAM`로 캐스팅 (모듈 파라미터) |
| `pApiCmd` | `IM_API_CMD_HEADER*` | 명령 헤더 (mode, property 포함) |
| `pApiResp` | `IM_API_RESP_HEADER*` | 응답 헤더 (결과 코드, 크기 설정) |
| `pData` | `void*` | 실제 데이터 페이로드 (구조체 포인터) |

### 2.2 mParam에서 모듈 데이터 획득

```c
int IM_API bufApiExecute(WMX3_API_PARAM) {
    // mParam을 PIM_LIB_MPARAM으로 캐스팅
    PIM_LIB_MPARAM lmParam = (PIM_LIB_MPARAM)mParam;

    // Motion_Setup에서 등록한 pApiBufferData 획득
    PAPIBUFFER_DATA pApiBufferData = (PAPIBUFFER_DATA)lmParam->mParam;

    // 큐 제어기 포인터 (QUEUE_CTRL 옵션 사용 시)
    // lmParam->queCtrl → 현재 큐 상태 접근 가능

    // 데이터 페이로드
    PAB_CHANNEL_SELECTION pChannelSelection = (PAB_CHANNEL_SELECTION)pData;

    int ret = ExecuteApiBuffer(pApiBufferData, pChannelSelection,
                               pApiCmd->property[WMX3_API_CMD_PROPERTY_INTERRUPT_ID]);
    if (ret) {
        WMX3_API_RETURN_ERROR(ret, 0);
    }
    WMX3_API_RETURN_SUCCESS(0);
}
```

### 2.3 응답 매크로

```c
// 성공 반환: 응답 크기(바이트)를 지정
#define WMX3_API_RETURN_SUCCESS(argSize) \
    pApiResp->res = IM_API_RESP_SUCCESS; \
    pApiResp->size = argSize; \
    return 0;

// 실패 반환: 에러 코드와 응답 크기 지정
#define WMX3_API_RETURN_ERROR(argErr, argSize) \
    pApiResp->res = IM_API_RESP_FAILED; \
    pApiResp->size = argSize; \
    pApiResp->err = argErr; \
    return pApiResp->err;
```

---

## 3. ApiLocal.h의 IPC 데이터 구조

`ApiBufferApiLocal.h`는 C++ API와 RTDLL이 공유하는 IPC 전송 구조체를 정의합니다.

### 3.1 API 모드 열거형 (핸들러 디스패치 인덱스)

```c
// ApiBufferApiLocal.h
typedef enum {
    AB_API_MODE_GET_VERSION,      // 인덱스 0
    AB_API_MODE_EXECUTE,          // 인덱스 1
    AB_API_MODE_HALT,             // 인덱스 2
    AB_API_MODE_CLEAR,            // 인덱스 3
    AB_API_MODE_REWIND,           // 인덱스 4
    AB_API_MODE_GET_BLOCK_COUNT,  // 인덱스 5
    AB_API_MODE_IF,               // 인덱스 6
    AB_API_MODE_ELSEIF,           // 인덱스 7
    AB_API_MODE_ELSE,             // 인덱스 8
    AB_API_MODE_ENDIF,            // 인덱스 9
    AB_API_MODE_SLEEP,            // 인덱스 10
    AB_API_MODE_USLEEP,           // 인덱스 11
    AB_API_MODE_WAIT,             // 인덱스 12
    AB_API_MODE_AWAKE_QUEUE,      // 인덱스 13
    AB_API_MODE_SET_WATCH,        // 인덱스 14
    AB_API_MODE_GET_WATCH,        // 인덱스 15
    AB_API_MODE_REGISTER_INTERRUPT_ID, // 인덱스 16
    AB_API_MODE_SIZE              // = 17 → apiFuncNum에 할당
} AB_API_MODE;
```

### 3.2 채널 선택 구조체

```c
// C 레이어 (ApiBufferApiLocal.h)
typedef struct {
    unsigned int channelCount;
    unsigned int channel[WMX3_AB_MAX_API_BUFFER_CHANNEL];
} AB_CHANNEL_SELECTION, *PAB_CHANNEL_SELECTION;
```

### 3.3 Watch 설정 구조체

```c
typedef struct {
    unsigned int  channel;                    // API 버퍼 채널 번호
    unsigned char enableWatch;                // 1: Watch 활성화
    AB_AXIS_SELECTION watchAxes;              // 감시할 축 목록
    unsigned char enableWatchTriggerRoutine;  // 1: 트리거 루틴 실행
    int watchTriggerRoutineChannel;           // 트리거 루틴 채널
} AB_SET_WATCH_DATA, *PAB_SET_WATCH_DATA;
```

---

## 4. 큐 기반 명령 전달 메커니즘

### 4.1 큐 상태 (IM_LIB_QUEUE_STATE)

```
IM_LIB_QUEUE_STATE_IDLE   → AB_API_BUFFER_STATE_IDLE   (대기)
IM_LIB_QUEUE_STATE_ACTIVE → AB_API_BUFFER_STATE_ACTIVE (실행 중)
IM_LIB_QUEUE_STATE_STOP   → AB_API_BUFFER_STATE_STOP   (정지, 재개 가능)
IM_LIB_QUEUE_STATE_DELAY  → AB_API_BUFFER_STATE_DELAY  (대기 후 재개)
```

### 4.2 QUEUE_CTRL 옵션 설정

```c
// Motion_Setup에서 큐 제어 옵션 활성화
pModuleFunc->option = IM_LIB_MODULE_PARAM_OPTION_QUEUE_CTRL;

// 옵션 파라미터에서 큐 제어기 획득
pApiBufferData->pAllQueueCtrl =
    (PIM_LIB_ALL_QUEUE_CTRL)pModuleFunc->optParam[0].mParam;
```

### 4.3 Sleep/Wait 핸들러의 큐 상태 변경 패턴

```c
int IM_API bufApiSleep(WMX3_API_PARAM) {
    PIM_LIB_MPARAM lmParam = (PIM_LIB_MPARAM)mParam;
    PAPIBUFFER_DATA pApiBufferData = (PAPIBUFFER_DATA)lmParam->mParam;
    unsigned int sleepTime = *(unsigned int*)pData;
    int queueId;

    if (lmParam->queCtrl == NULL) {
        WMX3_API_RETURN_ERROR(AB_API_ERROR_INVALID_BUFF_CTRL, 0);
    }

    // 큐 상태를 DELAY로 변경 (실행 일시 정지)
    lmParam->queCtrl->status.state = IM_LIB_QUEUE_STATE_DELAY;
    queueId = lmParam->queCtrl->curQueueId;

    pApiBufferData->buff[queueId].sleepFlag = 1;
    while (sleepTime > 0 && pApiBufferData->buff[queueId].sleepFlag) {
        OslSleep(1);   // 1ms 대기
        sleepTime--;
    }
    pApiBufferData->buff[queueId].sleepFlag = 0;

    WMX3_API_RETURN_SUCCESS(0);
}
```

### 4.4 Wait 핸들러의 이벤트 기반 대기 패턴

```c
int IM_API bufApiWait(WMX3_API_PARAM) {
    PIM_LIB_MPARAM lmParam = (PIM_LIB_MPARAM)mParam;
    PAPIBUFFER_DATA pApiBufferData = (PAPIBUFFER_DATA)lmParam->mParam;
    PAB_MULTI_CONDITION pWaitMultiCondition = (PAB_MULTI_CONDITION)pData;

    lmParam->queCtrl->status.state = IM_LIB_QUEUE_STATE_DELAY;

    if (pApiBufferData->buff[lmParam->queCtrl->curQueueId].waitEventHandle != NULL) {
        // 조건 복사 (RT 컨텍스트의 Motion_Process에서 평가)
        memcpy(&pApiBufferData->buff[lmParam->queCtrl->curQueueId].waitMultiCondition,
               pWaitMultiCondition, sizeof(AB_MULTI_CONDITION));
        pApiBufferData->buff[lmParam->queCtrl->curQueueId].waitingFlag = 1;

        // 이벤트 리셋 후 대기 (Motion_Process에서 OslSetEvent 호출 시까지)
        OslResetEvent(pApiBufferData->buff[lmParam->queCtrl->curQueueId].waitEventHandle);
        OslWaitForSingleObject(pApiBufferData->buff[lmParam->queCtrl->curQueueId].waitEventHandle,
                               OSL_INFINITE);

        pApiBufferData->buff[lmParam->queCtrl->curQueueId].waitingFlag = 0;
    }
    WMX3_API_RETURN_SUCCESS(0);
}
```

`Motion_Process`에서 조건이 충족되면 `OslSetEvent`를 호출하여 Wait 핸들러를 깨웁니다:
```c
Motion_API Motion_Process(WMX3_MP_DATA* pMP) {
    // ...
    if (pApiBufferData->buff[buffLoop].waitingFlag) {
        if (ApiBufferMultiConditionJudgment(pApiBufferData,
            &pApiBufferData->buff[buffLoop].waitMultiCondition, &err)
            || err != WMX3_API_ERROR_NONE)
        {
            pApiBufferData->buff[buffLoop].waitErr = err;
            OslSetEvent(pApiBufferData->buff[buffLoop].waitEventHandle);
        }
    }
    // ...
}
```

---

## 5. If/ElseIf 분기의 큐 스킵 메커니즘

조건이 거짓인 If 블록은 `NextIfElseCommand` 함수를 이용하여 큐를 스킵합니다.

```c
// NextIfElseCommand: If/ElseIf/Else/EndIf 명령까지 큐를 건너뜀
int IM_API NextIfElseCommand(int moduleId, IM_API_CMD_HEADER* pCmdHeader, void* param) {
    if (moduleId == WMX3_MODULE_ID_APIBUFFER &&
        (pCmdHeader->mode == AB_API_MODE_IF    ||
         pCmdHeader->mode == AB_API_MODE_ELSEIF ||
         pCmdHeader->mode == AB_API_MODE_ELSE  ||
         pCmdHeader->mode == AB_API_MODE_ENDIF))
    {
        return OSL_TRUE;  // 이 명령에서 멈춤
    }
    return OSL_FALSE;     // 계속 스킵
}

// 조건이 거짓인 경우 스킵 설정
lmParam->queCtrl->Func    = NextIfElseCommand;
lmParam->queCtrl->subMode = IM_LIB_QUEUE_CTRL_SUB_MODE_NEXT_CMD_FUNC;
lmParam->queCtrl->param   = NULL;
```

---

## 6. 채널 인덱스 오프셋 (+1)

사용자 채널 번호(0-base)와 내부 큐 인덱스(1-base) 사이에 +1 오프셋이 있습니다.

```c
// 사용자 채널 0 → 내부 큐 인덱스 1
// 사용자 채널 254 → 내부 큐 인덱스 255

// 모든 핸들러에서 일관되게 적용
channel += 1;

if (channel <= 0 || channel >= IM_MAX_CMD_QUEUE_SIZE) {
    WMX3_API_RETURN_ERROR(IM_ERROR_INVALID_QUEUE_ID, 0);
}
```

큐 인덱스 0은 시스템 예약 영역으로 사용자가 접근할 수 없습니다.

---

## 7. 상태 업데이트 함수 패턴

```c
// 상태 업데이트 타입 결정 (MP ID 0에서만 업데이트)
IM_LIB_STATUS_UPDATE_TYPE IM_API bufApiStatusUpdateType(void* lParam, void* sParam) {
    PWMX3_STATUS_FUNC_LPARAM pslParam = (PWMX3_STATUS_FUNC_LPARAM)lParam;

    if (pslParam->pMpData->id == 0) {
        return IM_LIB_STATUS_UPDATE_TYPE_SINGLE;  // MP 0에서만 실행
    }
    return IM_LIB_STATUS_UPDATE_TYPE_SKIP;        // 나머지 MP에서는 스킵
}

// 상태 데이터 채우기
int IM_API bufApiUpdateStatus(void* lParam, void* sParam, void* pData) {
    PAPIBUFFER_DATA pApiBufferData = (PAPIBUFFER_DATA)sParam;
    PAB_API_BUFFER_STATUS_DATA pStatus = (PAB_API_BUFFER_STATUS_DATA)pData;

    for (int loop = 0; loop < OSL_CountOf(pStatus->status); loop++) {
        // 큐 상태를 AB_API_BUFFER_STATE로 매핑
        switch (pApiBufferData->pAllQueueCtrl->ctrls[loop+1]->status.state) {
            case IM_LIB_QUEUE_STATE_IDLE:   pStatus->status[loop].state = AB_API_BUFFER_STATE_IDLE;   break;
            case IM_LIB_QUEUE_STATE_ACTIVE: pStatus->status[loop].state = AB_API_BUFFER_STATE_ACTIVE; break;
            case IM_LIB_QUEUE_STATE_STOP:   pStatus->status[loop].state = AB_API_BUFFER_STATE_STOP;   break;
            case IM_LIB_QUEUE_STATE_DELAY:  pStatus->status[loop].state = AB_API_BUFFER_STATE_DELAY;  break;
        }
        // blockCount, freeSize, errorLog 등 채우기
    }
    return 0;
}
```
