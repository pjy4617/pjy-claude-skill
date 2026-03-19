# WMX3 의존 모듈 인터페이스

ApiBuffer 모듈은 런타임에 CoreMotion, Event, IO, UserMemory 4개 모듈의 PubData에 의존합니다. 이 문서는 의존성 획득 방법과 각 모듈 인터페이스 접근 패턴을 설명합니다.

---

## 1. 의존성 획득 방법

### 1.1 Motion_Init에서 포인터 획득

```c
Motion_API Motion_Init(WMX3_MP_ALL_AXIS_IO_DATA* pAllAxisIoData,
                       WMX3_MODULE_INIT_DATA*    pInitData)
{
    PAPIBUFFER_DATA pApiBufferData = &__ApiBufferData__;

    // 각 모듈 ID로 인덱싱하여 PubData 획득
    pApiBufferData->pCmPubData =
        (PCORE_MOTION_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_CORE_MOTION];

    pApiBufferData->pEvPubData =
        (PEVENT_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_EVENT];

    pApiBufferData->pIoPubData =
        (PIO_CONTROL_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_IO];

    pApiBufferData->pUmPubData =
        (PUSER_MEMORY_CONTROL_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_USER_MEMORY];

    return 0;
}
```

- `pAllAxisIoData->userMemory[MODULE_ID]`는 각 모듈이 `Motion_Setup`에서
  `pConfig->sharedMemory`로 등록한 PubData 포인터
- 반환값 타입은 해당 모듈의 `*ApiPub.h` 헤더에 정의된 구조체로 캐스팅
- 모듈이 로드되지 않았을 경우 `NULL`이 될 수 있으므로 반드시 NULL 체크 필요

### 1.2 NULL 체크 패턴

```c
// Motion_Process 등에서 사용 시
if (pApiBufferData->pCmPubData != NULL) {
    // CoreMotion PubData 사용
}
```

---

## 2. 의존 모듈별 인터페이스

### 2.1 CoreMotion (PCORE_MOTION_PUB_DATA)

헤더: `CoreMotionApiPub.h`
모듈 ID: `WMX3_MODULE_ID_CORE_MOTION`
용도: 축 상태 조회, 모션 조건 평가 (InPos, PosSET, RemainingTime 등)

```c
// ApiBuffer.h 에서의 선언
PCORE_MOTION_PUB_DATA pCmPubData;
```

주요 사용 패턴 (조건 평가 시):
```c
// ApiBuffer_Util.c의 조건 판단 함수에서 CoreMotion PubData 사용
// 축 상태, 위치, 속도 등을 조회하여 Wait/If 조건을 평가
if (pApiBufferData->pCmPubData != NULL) {
    // pCmPubData를 통해 축 상태 조회
}
```

### 2.2 Event (PEVENT_PUB_DATA)

헤더: `EventApiPub.h`
모듈 ID: `WMX3_MODULE_ID_EVENT`
용도: 커스텀 이벤트 등록, 이벤트 조건 평가

```c
// ApiBuffer.h 에서의 선언
PEVENT_PUB_DATA pEvPubData;
```

**Motion_Init에서 커스텀 이벤트 등록 패턴:**
```c
PEVENT_PUB_DATA pEvPub =
    (PEVENT_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_EVENT];

if (pEvPub != NULL) {
    EV_CUSTOM_EVENT_PUB ab_event;
    AbEventSetCustomEvent(pApiBufferData, &ab_event);  // 이벤트 데이터 설정
    pEvPub->registerCustomEvent(WMX3_MODULE_ID_APIBUFFER, &ab_event);  // 등록
}
```

### 2.3 IO (PIO_CONTROL_PUB_DATA)

헤더: `IOApiPub.h`
모듈 ID: `WMX3_MODULE_ID_IO`
용도: IO 입출력 비트 조건 평가 (Wait/If의 IOInput, IOOutput 조건 타입)

```c
// ApiBuffer.h 에서의 선언
PIO_CONTROL_PUB_DATA pIoPubData;
```

IO 조건 구조체 (`ApiBufferApiLocal.h` 참조):
```c
struct {
    unsigned int  byteAddress;  // IO 입력 바이트 주소
    unsigned char bitAddress;   // IO 입력 비트 주소 (0~7)
    unsigned char invert;       // 1: 입력 반전, 0: 그대로
} ioInput;

struct {
    unsigned int  byteAddress;  // IO 출력 바이트 주소
    unsigned char bitAddress;   // IO 출력 비트 주소 (0~7)
    unsigned char invert;       // 1: 출력 반전, 0: 그대로
} ioOutput;
```

### 2.4 UserMemory (PUSER_MEMORY_CONTROL_PUB_DATA)

헤더: `UserMemoryApiPub.h`
모듈 ID: `WMX3_MODULE_ID_USER_MEMORY`
용도: 사용자 메모리 비트 조건 평가

```c
// ApiBuffer.h 에서의 선언
PUSER_MEMORY_CONTROL_PUB_DATA pUmPubData;
```

UserMemory 조건 구조체:
```c
struct {
    unsigned int  byteAddress;  // 사용자 메모리 바이트 주소
    unsigned char bitAddress;   // 사용자 메모리 비트 주소 (0~7)
    unsigned char invert;       // 1: 반전, 0: 그대로
} userMemory;
```

---

## 3. PubData 구조체 패턴 (함수 포인터 주입)

다른 RTDLL 모듈이 ApiBuffer를 직접 호출할 수 있도록 함수 포인터를 PubData에 등록합니다.

### 3.1 ApiBufferApiPub.h 구조

```c
// 함수 포인터 타입 정의
typedef int (__stdcall *ApiBufferExec)(int channel);
typedef int (__stdcall *ApiBufferHalt)(int channel);
typedef int (__stdcall *ApiBufferClear)(int channel);
typedef int (__stdcall *ApiBufferRewind)(int channel);

// PubData 구조체: 함수 포인터 테이블
typedef struct {
    ApiBufferExec   execApiBuff;   // 버퍼 실행 함수 포인터
    ApiBufferHalt   haltApiBuff;   // 버퍼 정지 함수 포인터
    ApiBufferClear  clearApiBuff;  // 버퍼 초기화 함수 포인터
    ApiBufferRewind rewindApiBuff; // 버퍼 되감기 함수 포인터
} APIBUFFER_PUB_DATA, *PAPIBUFFER_PUB_DATA;
```

### 3.2 Motion_Setup에서 PubData 초기화

```c
// ApiBuffer_Motion.c - Motion_Setup 내부
pApiBufferData->pubData.execApiBuff   = ApiBufferExecFunc;
pApiBufferData->pubData.haltApiBuff   = ApiBufferHaltFunc;
pApiBufferData->pubData.clearApiBuff  = ApiBufferClearFunc;
pApiBufferData->pubData.rewindApiBuff = ApiBufferRewindFunc;

// 공유 메모리로 노출 (다른 모듈이 pAllAxisIoData->userMemory[APIBUFFER]로 접근)
pConfig->sharedMemory = &pApiBufferData->pubData;
```

### 3.3 다른 모듈에서 ApiBuffer PubData 사용

```c
// 다른 RTDLL 모듈 (예: Event 모듈)에서
PAPIBUFFER_PUB_DATA pAbPubData =
    (PAPIBUFFER_PUB_DATA)pAllAxisIoData->userMemory[WMX3_MODULE_ID_APIBUFFER];

if (pAbPubData != NULL && pAbPubData->execApiBuff != NULL) {
    int ret = pAbPubData->execApiBuff(channel);
}
```

---

## 4. 새 모듈의 PubData 설계 원칙

| 원칙 | 설명 |
|------|------|
| 함수 포인터만 노출 | 내부 데이터 구조체는 노출하지 않음 |
| `__stdcall` 호환 | Windows/Linux 크로스 플랫폼 ABI 일치 (`ApiBufferApiDef.h`에서 Linux용 빈 매크로 정의) |
| NULL 초기화 | 구조체 전체를 0으로 초기화 후 함수 포인터 설정 |
| `*ApiPub.h` 분리 | PubData 정의는 별도 헤더에 분리하여 다른 모듈이 내부 헤더 없이 참조 가능 |

### Linux에서 __stdcall 처리

```c
// ApiBufferApiDef.h
#ifndef _WIN32
#ifndef __stdcall
#define __stdcall   // Linux에서는 빈 매크로로 정의
#endif
#endif
```

---

## 5. 모듈 데이터 구조체에서의 의존성 선언

```c
// ApiBuffer.h - APIBUFFER_DATA 구조체
typedef struct {
    // 공통 데이터
    PWMX3_MP_ALL_AXIS_IO_DATA pMpAiData;     // 전체 IO 데이터 포인터

    // PubData (이 모듈이 노출하는 공개 인터페이스)
    APIBUFFER_PUB_DATA pubData;

    // 의존 모듈 PubData 포인터 (Motion_Init에서 획득)
    PCORE_MOTION_PUB_DATA         pCmPubData;
    PEVENT_PUB_DATA               pEvPubData;
    PIO_CONTROL_PUB_DATA          pIoPubData;
    PUSER_MEMORY_CONTROL_PUB_DATA pUmPubData;

    // 내부 전용 데이터
    AB_BUFF_DATA         buff[IM_MAX_CMD_QUEUE_SIZE];
    PIM_LIB_ALL_QUEUE_CTRL pAllQueueCtrl;
} APIBUFFER_DATA, *PAPIBUFFER_DATA;
```

새 모듈 작성 시 필요한 의존 모듈만 포인터를 선언하고, 불필요한 의존성은 추가하지 않습니다.
