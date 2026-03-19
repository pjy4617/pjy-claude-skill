# WMX3 에러 코드 체계

---

## 1. 에러 코드 범위 구조

WMX3는 모듈별로 에러 코드 범위를 분리합니다. 각 모듈은 고유한 기준 오프셋을 가집니다.

### 공통 에러 코드 (WMX3ApiDef.h)

```c
// 성공
WMX3_API_ERROR_NONE = 0

// 공통 에러 범위: 0x00000001 ~ 0x00001FFF
WMX3_API_ERROR_CHANNEL_OUT_OF_RANGE
WMX3_API_ERROR_AXIS_OUT_OF_RANGE
WMX3_API_ERROR_AXIS_COUNT_OUT_OF_RANGE
WMX3_API_ERROR_ARGUMENT_OUT_OF_RANGE
WMX3_API_ERROR_PREVIOUS_SETTINGS_BEING_APPLIED
WMX3_API_ERROR_INVALID_SECURITY_CODE
// ...
```

### ApiBuffer 에러 코드 (ApiBufferApiDef.h)

```c
typedef enum {
    // ApiBuffer 전용 범위: 0x00012000 ~
    AB_API_ERROR_OVER_MAX_LEVEL = 0x00012000,
    AB_API_ERROR_INVALID_LEVEL,
    AB_API_ERROR_INVALID_BUFF_CTRL,
    AB_API_ERROR_INVALID_WATCH_TRIGGER_ROUTINE_CHANNEL,
    AB_API_ERROR_WATCH_TRIGGER_ROUTINE_CHANNEL_SAME_AS_EXEC_CHANNEL,
    AB_API_ERROR_REWIND_FAILED_FIRST_COMMAND_OVERWRITTEN,
    AB_API_ERROR_ALREADY_RECORDING_FOR_SPECIFIED_CHANNEL,
    AB_API_ERROR_NOT_RECORDING,
    AB_API_ERROR_REQUEST_MODE_CHANGE_TIMEOUT,
    AB_API_ERROR_API_BUFFER_NOT_OPENED,
    AB_API_ERROR_GATE_NODE_HAS_NO_CHILD,
    AB_API_ERROR_NOT_GATE_NODE_INVALID_CHILD_COUNT,
    AB_API_ERROR_LEAF_NODE_HAS_CHILD,
    AB_API_ERROR_INVALID_MULTI_CONDITION,
    AB_API_ERROR_XOR_GATE_NODE_INVALID_CHILD_COUNT,
    AB_API_ERROR_INVALID_CONDITION_TYPE,

    AB_API_ERROR_SIZE
} AB_API_ERROR_CODE;
```

---

## 2. 모듈별 에러 코드 범위 할당 규칙

새 모듈 추가 시 기존 모듈과 겹치지 않는 범위를 선택합니다.

| 모듈 | 범위 시작 | 예시 |
|------|-----------|------|
| 공통 (WMX3Api) | `0x00000001` | `WMX3_API_ERROR_CHANNEL_OUT_OF_RANGE` |
| CoreMotion | `0x00010000` | (CoreMotion 전용 에러) |
| ApiBuffer | `0x00012000` | `AB_API_ERROR_OVER_MAX_LEVEL = 0x00012000` |
| 새 모듈 예시 | `0x00013000` | `{{MODULE}}_API_ERROR_xxx = 0x00013000` |

**범위 선택 원칙:**
- 모듈당 최대 0x1000(4096)개 에러 코드 할당
- 새 모듈은 기존 최대값 + 0x1000에서 시작
- `WMX3EngineDef.h` 또는 프로젝트 내 `MODULE_ERROR_RANGES.md`에서 현재 할당 범위 확인

---

## 3. 에러 코드 매크로 정의 패턴

### 헤더 분리 원칙

```c
// {{MODULE}}ApiDef.h: 사용자에게 공개되는 에러 코드
typedef enum {
    {{MODULE}}_API_ERROR_{{NAME}} = 0x000XX000,  // 범위 기준값
    {{MODULE}}_API_ERROR_{{NAME2}},
    // ...
    {{MODULE}}_API_ERROR_SIZE
} {{MODULE}}_API_ERROR_CODE, *P{{MODULE}}_API_ERROR_CODE;

// {{MODULE}}.h: 모듈 내부 전용 에러 코드 (RTDLL 내부만 사용)
typedef enum {
    {{MODULE}}_ERROR_NONE = 0,
    {{MODULE}}_ERROR_INIT_FAILED,
    {{MODULE}}_ERROR_INVALID_SECURITY_CODE,
    {{MODULE}}_ERROR_CODE_SIZE
} {{MODULE}}_ERROR_CODE, *P{{MODULE}}_ERROR_CODE;

// ApiBufferApiPub.h: 다른 RTDLL 모듈이 PubFuncs 호출 시 받는 에러
typedef enum {
    APIBUFFER_PUB_ERROR_NONE,
    APIBUFFER_PUB_ERROR_INVALID_BUFF_DATA,
    APIBUFFER_PUB_ERROR_INVALID_CHANNEL,
    APIBUFFER_PUB_ERROR_INVALID_BUFF_CTRL,
    APIBUFFER_PUB_ERROR_FIRST_COMMAND_OVERWRITTEN,
    APIBUFFER_PUB_ERROR_PREVIOUS_SETTINGS_BEING_APPLIED,
    APIBUFFER_PUB_ERROR_SIZE
} APIBUFFER_PUB_ERROR_CODE;
```

---

## 4. 에러 코드 사용 패턴

### 4.1 핸들러 함수에서 에러 반환

```c
// ApiBuffer_Funcs.c 패턴
int IM_API bufApiSetWatch(WMX3_API_PARAM) {
    // ...
    if (channel < 0 || channel >= WMX3_AB_MAX_API_BUFFER_CHANNEL) {
        WMX3_API_RETURN_ERROR(WMX3_API_ERROR_CHANNEL_OUT_OF_RANGE, 0);
    }
    if (pWatchData->watchAxes.axisCount < 0 || pWatchData->watchAxes.axisCount > WMX3_MAX_AXES) {
        WMX3_API_RETURN_ERROR(WMX3_API_ERROR_AXIS_COUNT_OUT_OF_RANGE, 0);
    }
    // ...
}
```

### 4.2 유틸리티 함수에서 에러 반환

```c
// ApiBuffer_Util.c 패턴
int ExecuteApiBuffer(PAPIBUFFER_DATA pData, PAB_CHANNEL_SELECTION pChannelSel, int intId) {
    if (pData->pAllQueueCtrl == NULL) {
        return AB_API_ERROR_INVALID_BUFF_CTRL;
    }
    // ... 처리 후
    return WMX3_API_ERROR_NONE;  // 성공
}
```

### 4.3 PubFuncs에서 에러 반환

```c
// ApiBuffer_PubFuncs.c 패턴
int __stdcall ApiBufferExecFunc(int channel) {
    if (pApiBufferData->pAllQueueCtrl == NULL) {
        return APIBUFFER_PUB_ERROR_INVALID_BUFF_DATA;
    }
    channel += 1;
    if (channel <= 0 || channel >= IM_MAX_CMD_QUEUE_SIZE) {
        return APIBUFFER_PUB_ERROR_INVALID_CHANNEL;
    }
    // ...
    return APIBUFFER_PUB_ERROR_NONE;
}
```

---

## 5. C++ API에서 에러 코드 클래스

```cpp
// ApiBufferApi.h
namespace wmx3Api {
    class ApiBufferErrorCode : public ErrorCode {
    public:
        enum {
            OverMaxLevel                          = 0x00012000,
            InvalidLevel,
            InvalidBuffControl,
            InvalidWatchTriggerRoutineChannel,
            WatchTriggerRoutineChannelSameAsExecChannel,
            RewindFailedFirstCommandOverwritten,
            AlreadyRecordingForSpecifiedChannel,
            NotRecording,
            RequestModeChangeTimeout,
            ApiBufferNotOpened,
            GateNodeHasNoChild,
            NotGateNodeInvalidChildCount,
            LeafNodeHasChild,
            InvalidMultiCondition,
            XorGateNodeInvalidChildCount,
            InvalidConditionType,
        };
    };
}
```

C 에러 코드와 C++ 에러 코드는 동일한 숫자 값을 공유합니다.

---

## 6. ApiLog 변환 패턴

에러 코드를 사람이 읽을 수 있는 문자열로 변환:

```cpp
// ApiBufferApi_ApiLog.cpp 패턴
// wmx3Api::ApiBuffer::ApiLogToString() 내부 구현

static const char* GetErrorString(int errCode) {
    switch (errCode) {
        case AB_API_ERROR_OVER_MAX_LEVEL:
            return "OverMaxLevel: Maximum nesting level exceeded";
        case AB_API_ERROR_INVALID_LEVEL:
            return "InvalidLevel: Invalid nesting level";
        case AB_API_ERROR_INVALID_BUFF_CTRL:
            return "InvalidBuffControl: API buffer function cannot be used";
        // ... 각 에러 코드에 대한 설명 문자열
        default:
            return "Unknown error";
    }
}
```

새 모듈에서 `ErrorToString` 정적 함수 구현:
```cpp
// {{Module}}Api.cpp
WMX3APIFUNC wmx3Api::{{Module}}::ErrorToString(int errCode, char* pString, unsigned int size) {
    // errCode → 문자열 변환 구현
    // WMX3Api::ErrorToString으로 공통 에러 처리 후 모듈 전용 에러 처리
}
```

---

## 7. 에러 코드 추가 체크리스트

새 모듈에서 에러 코드를 추가할 때:

- [ ] `{{MODULE}}ApiDef.h`의 열거형에 새 에러 코드 추가 (`_SIZE` 이전에)
- [ ] 범위 시작값(`0x000XX000`)이 기존 모듈과 겹치지 않는지 확인
- [ ] `ApiBufferApi_ApiLog.cpp`에 해당하는 `ErrorToString` 케이스 추가
- [ ] C++ API 클래스의 `ErrorCode` 중첩 열거형에 동일 값으로 추가
- [ ] CLRLib(.NET 래퍼)에도 동일 에러 코드 정의 (Windows 전용)
