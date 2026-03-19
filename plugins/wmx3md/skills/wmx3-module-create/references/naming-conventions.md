# WMX3 모듈 네이밍 규칙

---

## 1. 파일명 패턴

| 파일 | 역할 | 예시 (ApiBuffer 기준) |
|------|------|----------------------|
| `{{MODULE}}_Motion.c` | 모듈 생명주기 진입점 | `ApiBuffer_Motion.c` |
| `{{MODULE}}_Funcs.c/h` | API 모드 핸들러 함수 | `ApiBuffer_Funcs.c/h` |
| `{{MODULE}}_Util.c/h` | 내부 유틸리티 함수 | `ApiBuffer_Util.c/h` |
| `{{MODULE}}_PubFuncs.c/h` | 다른 RTDLL 모듈용 공개 함수 | `ApiBuffer_PubFuncs.c/h` |
| `{{MODULE}}_Event.c/h` | Event 모듈 통합 | `ApiBuffer_Event.c/h` |
| `{{MODULE}}.h` | 모듈 내부 메인 헤더 (모듈 데이터 구조체) | `ApiBuffer.h` |
| `{{MODULE}}.c` | Windows DllMain 진입점 (Windows 전용) | `ApiBuffer.c` |

---

## 2. 접두어 규칙

### 2.1 내부 상수·열거형·구조체 (AB_ 접두어)

모듈 내부에서만 사용하는 심볼에는 모듈 약어 + 언더스코어를 붙입니다.

```c
// ApiBuffer 예시
typedef enum { AB_API_MODE_EXECUTE, ... } AB_API_MODE;
typedef enum { AB_API_BUFFER_STATE_IDLE, ... } AB_API_BUFFER_STATE;
typedef struct { ... } AB_BUFF_DATA, *PAB_BUFF_DATA;
typedef struct { ... } AB_MULTI_CONDITION, *PAB_MULTI_CONDITION;
```

- 포인터 타입은 `P` 접두어 추가: `PAB_BUFF_DATA`, `PAB_MULTI_CONDITION`
- 새 모듈의 접두어는 모듈 약어로 결정 (예: CoreMotion → `CM_`, IO → `IO_`)

### 2.2 공개 상수·매크로 (WMX3_AB_ 접두어)

외부에서 참조 가능한 상수·매크로는 `WMX3_` 접두어를 추가합니다.

```c
// ApiBufferApiDef.h
#define WMX3_AB_MAX_API_BUFFER_CHANNEL  255
#define WMX3_AB_MAX_API_BUFFER_ERROR_LOG 10
#define WMX3_AB_MAX_DEFAULT_API_BUFFER_SIZE 524288
#define WMX3_AB_MAX_CONDITION_TREE_NODE  10
#define WMX3_AB_MAX_CONDITION_TREE_CHILDREN 3
```

패턴: `WMX3_{{MODULE_ABBREV}}_{{CONSTANT_NAME}}`

### 2.3 API 핸들러 함수 (buf 접두어)

`ApiBuffer_Funcs.c`의 핸들러 함수는 소문자 모듈 약어로 시작합니다.

```c
int IM_API bufApiExecute(WMX3_API_PARAM);
int IM_API bufApiHalt(WMX3_API_PARAM);
int IM_API bufApiClear(WMX3_API_PARAM);
int IM_API bufApiRewind(WMX3_API_PARAM);
int IM_API bufApiSleep(WMX3_API_PARAM);
int IM_API bufApiWait(WMX3_API_PARAM);
int IM_API bufApiIf(WMX3_API_PARAM);
```

패턴: `{{moduleAbbrev}}Api{{FunctionName}}`
예시:
- ApiBuffer → `bufApi`
- CoreMotion → `cmApi`
- IO → `ioApi`

### 2.4 공개 함수 구현 ({{Module}}Func 접두어)

`ApiBufferApiPub.h`에서 선언되고 `ApiBuffer_PubFuncs.c`에서 구현되는 함수:

```c
int __stdcall ApiBufferExecFunc(int channel);
int __stdcall ApiBufferHaltFunc(int channel);
int __stdcall ApiBufferClearFunc(int channel);
int __stdcall ApiBufferRewindFunc(int channel);
```

패턴: `{{ModuleName}}{{FunctionName}}Func`

---

## 3. 열거형 네이밍

### API 모드 열거형

```c
// ApiBufferApiLocal.h
typedef enum {
    AB_API_MODE_GET_VERSION,
    AB_API_MODE_EXECUTE,
    AB_API_MODE_HALT,
    // ...
    AB_API_MODE_SIZE    // ← 반드시 마지막에 SIZE 추가
} AB_API_MODE, *PAB_API_MODE;
```

패턴: `{{MODULE_ABBREV}}_API_MODE_{{FUNCTION_NAME}}`

마지막 항목 `_SIZE`는 `apiFuncNum`에 할당되며, 핸들러 배열 크기를 결정합니다.

### 에러 코드 열거형

```c
// ApiBufferApiDef.h
typedef enum {
    AB_API_ERROR_OVER_MAX_LEVEL = 0x00012000,  // 모듈별 기준 오프셋
    AB_API_ERROR_INVALID_LEVEL,
    // ...
    AB_API_ERROR_SIZE
} AB_API_ERROR_CODE, *PAB_API_ERROR_CODE;
```

패턴: `{{MODULE_ABBREV}}_API_ERROR_{{ERROR_NAME}}`

---

## 4. 헤더 가시성 계층

4개 헤더는 포함 범위가 다릅니다. 반드시 올바른 헤더만 포함해야 합니다.

```
가시성 좁음 ──────────────────────────────────── 넓음

ApiBufferApiLocal.h   ApiBufferApiPub.h   ApiBufferApiDef.h   ApiBufferApi.h
(내부 IPC 전용)        (모듈간 공유)        (모든 C/C++ 코드)    (사용자 앱 전용)
```

| 헤더 파일 | 포함 대상 | 포함 금지 대상 |
|-----------|-----------|----------------|
| `{{MODULE}}ApiLocal.h` | ApiBuffer RTDLL, ApiBufferApi C++ 라이브러리 | 외부 모듈, 사용자 앱 |
| `{{MODULE}}ApiPub.h` | ApiBuffer RTDLL, 다른 RTDLL 모듈 | 사용자 앱 |
| `{{MODULE}}ApiDef.h` | 모든 모듈 + 사용자 앱 | 없음 |
| `{{MODULE}}Api.h` | 사용자 C++ 앱 전용 | RTDLL 내부 |

**헤더 가드 패턴:**
```c
#ifndef WMX3_{{MODULE}}_API_LOCAL_H
#define WMX3_{{MODULE}}_API_LOCAL_H
// ...
#endif
```

---

## 5. C++ 네임스페이스 (ApiBufferApi 레이어)

```cpp
// wmx3Api:: 네임스페이스 (공통 WMX3 API 네임스페이스)
namespace wmx3Api {
    class ApiBuffer { ... };
    class ApiBufferCondition { ... };
    class ApiBufferMultiCondition { ... };
    class ApiBufferStatus { ... };
    class ApiBufferState { ... };
    class ApiBufferErrorCode : public ErrorCode { ... };
}
```

### .NET CLR 래퍼 네임스페이스

```cpp
// WMX3ApiCLR:: 네임스페이스 (C++/CLI .NET 래퍼)
namespace WMX3ApiCLR {
    public ref class ApiBuffer { ... };
}
```

---

## 6. 모듈 데이터 구조체 네이밍

```c
// 모듈 메인 데이터 구조체
typedef struct {
    // 공통 데이터
    PWMX3_MP_ALL_AXIS_IO_DATA pMpAiData;

    // PubData (다른 모듈이 접근)
    {{MODULE}}_PUB_DATA pubData;

    // 의존 모듈 PubData 포인터
    PCORE_MOTION_PUB_DATA pCmPubData;
    PEVENT_PUB_DATA       pEvPubData;

    // 내부 전용 데이터
    // ...
} {{MODULE}}_DATA, *P{{MODULE}}_DATA;
```

전역 변수명: `__{{Module}}Data__` (언더스코어로 감쌈)

---

## 7. 상태 채널 열거형

```c
typedef enum {
    {{MODULE}}_STATUS_CHANNEL_{{STATUS_NAME}},  // 예: AB_STATUS_CHANNEL_BUFF_STATUS
    // ...
    {{MODULE}}_STATUS_CHANNEL_SIZE
} {{MODULE}}_STATUS_CHANNEL, *P{{MODULE}}_STATUS_CHANNEL;
```

---

## 8. 버전 상수 패턴

```c
// {{MODULE}}ApiDef.h
#define {{MODULE}}_REVISION_VERSION  0  // 예: API_BUFFER_REVISION_VERSION
#define {{MODULE}}_FIX_VERSION       0  // 예: API_BUFFER_FIX_VERSION
```
