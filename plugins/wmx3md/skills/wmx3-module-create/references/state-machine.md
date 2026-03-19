# WMX3 모듈 상태 머신 설계 패턴

---

## 1. ApiBuffer 버퍼 채널 상태 (AB_API_BUFFER_STATE)

`ApiBufferApiDef.h`에 정의된 4개 상태:

```c
typedef enum {
    AB_API_BUFFER_STATE_IDLE,   // 대기: 버퍼 비어있거나 정지 후 완료
    AB_API_BUFFER_STATE_ACTIVE, // 실행 중: 명령 순차 실행 중
    AB_API_BUFFER_STATE_STOP,   // 정지: Halt 호출로 중단 (재개 가능)
    AB_API_BUFFER_STATE_DELAY   // 지연: Sleep/Wait 중 (조건 충족 시 재개)
} AB_API_BUFFER_STATE;
```

내부 큐 상태(`IM_LIB_QUEUE_STATE`)와의 매핑:

```c
// bufApiUpdateStatus에서의 매핑
switch (pAllQueueCtrl->ctrls[loop+1]->status.state) {
    case IM_LIB_QUEUE_STATE_IDLE:   → AB_API_BUFFER_STATE_IDLE
    case IM_LIB_QUEUE_STATE_ACTIVE: → AB_API_BUFFER_STATE_ACTIVE
    case IM_LIB_QUEUE_STATE_STOP:   → AB_API_BUFFER_STATE_STOP
    case IM_LIB_QUEUE_STATE_DELAY:  → AB_API_BUFFER_STATE_DELAY
}
```

---

## 2. 상태 전이 다이어그램

```
                    Execute() 호출
                   ┌─────────────────────────────────────────────────────┐
                   │                                                     │
                   ▼                                                     │
┌──────────────────────────┐     Execute() 호출      ┌──────────────────────────┐
│                          │ ──────────────────────► │                          │
│         IDLE             │                         │         ACTIVE           │
│  (대기 / 초기 상태)        │ ◄────────────────────── │    (명령 순차 실행 중)     │
│                          │   Clear() 또는           │                          │
└──────────────────────────┘   모든 명령 완료          └──────────┬───────────────┘
         ▲                                                        │
         │                                              Sleep()/Wait() 호출
         │ Clear() 호출                                           │
         │                                                        ▼
┌──────────────────────────┐                         ┌──────────────────────────┐
│                          │   Halt() 호출            │                          │
│          STOP            │ ◄────────────────────── │         DELAY            │
│  (정지, 재개 가능)         │                         │  (Sleep/Wait 대기 중)     │
│                          │                         │                          │
└──────────────────────────┘                         └──────────────────────────┘
         │                                                        │
         │ Execute() 호출                               조건 충족 또는 Halt()
         │ (재개)                                                  │
         └────────────────────────────────────────────────────────┘
                             ACTIVE로 전환
```

### 상태 전이 규칙 요약

| 현재 상태 | 이벤트 | 다음 상태 |
|-----------|--------|-----------|
| IDLE | Execute() | ACTIVE |
| ACTIVE | 모든 명령 완료 | IDLE |
| ACTIVE | Halt() | STOP |
| ACTIVE | Sleep(ms) | DELAY |
| ACTIVE | Wait(condition) | DELAY |
| ACTIVE | If(condition) 평가 | ACTIVE (조건 true) / DELAY→ACTIVE (wait 후) |
| DELAY | 시간 경과 (Sleep) | ACTIVE |
| DELAY | 조건 충족 (Wait) | ACTIVE |
| DELAY | Halt() | STOP |
| STOP | Execute() | ACTIVE (재개) |
| STOP | Clear() | IDLE |
| IDLE/STOP/ACTIVE | Clear() | IDLE |
| STOP | Rewind() | STOP (실행 위치 처음으로) |

---

## 3. RT 안전한 상태 머신 구현 규칙

### 규칙 1: 상태 전이는 원자적으로

```c
// 올바른 패턴: 단일 대입으로 상태 변경
lmParam->queCtrl->status.state = IM_LIB_QUEUE_STATE_DELAY;

// 잘못된 패턴: 조건 검사 후 변경 (경쟁 조건 위험)
if (state != DELAY) {
    state = DELAY;  // ← TOCTOU 취약점
}
```

### 규칙 2: 상태 확인은 Motion_Process에서만

```c
// ApiBuffer_Motion.c - Motion_Process
Motion_API Motion_Process(WMX3_MP_DATA* pMP) {
    for (int buffLoop = 1; buffLoop < OSL_CountOf(pApiBufferData->buff); buffLoop++) {
        // IDLE이 아닌 채널만 처리 (불필요한 검사 회피)
        if (pApiBufferData->pAllQueueCtrl->ctrls[buffLoop]->status.state
            != IM_LIB_QUEUE_STATE_IDLE
            && pApiBufferData->buff[buffLoop].interruptId == pMP->id)
        {
            // 대기 조건 평가
            if (pApiBufferData->buff[buffLoop].waitingFlag) {
                // 조건 충족 시 이벤트 시그널
            }
            // Watch 처리
        }
    }
}
```

### 규칙 3: 재귀 없는 반복적 평가

다중 조건 트리(`ApiBuffer_Util_MultiCondition.c`)는 스택 기반 반복 알고리즘으로 구현:

```c
// 스택 기반 트리 순회 (재귀 없음 - RT 안전)
int ApiBufferMultiConditionJudgment(PAPIBUFFER_DATA pData,
                                     PAB_MULTI_CONDITION pCondition,
                                     int* pErr)
{
    // 최대 WMX3_AB_MAX_CONDITION_TREE_NODE 크기의 스택 사용
    // (동적 할당 없음 - 고정 크기 배열)
    int stack[WMX3_AB_MAX_CONDITION_TREE_NODE];
    int stackTop = 0;
    // ...스택 기반 후위 순회...
}
```

### 규칙 4: 플래그 기반 상태 관리

복잡한 상태는 플래그 조합으로 표현:

```c
// AB_BUFF_DATA (ApiBuffer.h)
typedef struct {
    unsigned char waitingFlag;    // Wait 명령 대기 중
    unsigned char sleepFlag;      // Sleep 명령 실행 중
    unsigned char updateWatch;    // Watch 설정 갱신 대기
    unsigned char executeTriggerRoutineFlag; // 트리거 루틴 실행 예약
    unsigned char watchErr;       // Watch 에러 발생 여부

    int skipLevel;                // If 블록 스킵 레벨 (0=스킵 없음)
    int curIfLevel;               // 현재 If 중첩 깊이
    unsigned char ifState[WMX3_AB_APIBUFFER_MAX_IF_LEVEL]; // If 분기 실행 여부
} AB_BUFF_DATA;
```

---

## 4. If/ElseIf/Else/EndIf 상태 관리

중첩 If 블록은 `curIfLevel`과 `ifState[]`로 관리합니다.

```
If(조건A)           → curIfLevel: 0→1, 조건A=true: ifState[0]=1, skipLevel=0
                                        조건A=false: ifState[0]=0, skipLevel=1
    ...실행 코드...
ElseIf(조건B)       → curIfLevel: 1 (불변), ifState[0]==0이면 조건B 평가
                                              ifState[0]==1이면 skipLevel=1
    ...실행 코드...
Else                → curIfLevel: 1 (불변), ifState[0]==0이면 실행
                                             ifState[0]==1이면 skipLevel=1
    ...실행 코드...
EndIf               → curIfLevel: 1→0, ifState[0]=0 초기화
```

상태 전이 코드:
```c
// If 진입
pApiBufferData->buff[queueId].curIfLevel++;
// 조건 true
pApiBufferData->buff[queueId].ifState[curLevel] = 1;
pApiBufferData->buff[queueId].skipLevel = 0;
// 조건 false
pApiBufferData->buff[queueId].skipLevel = curLevel + 1;
// NextIfElseCommand로 스킵

// EndIf
pApiBufferData->buff[queueId].curIfLevel--;
pApiBufferData->buff[queueId].ifState[curLevel] = 0;  // 초기화
```

최대 중첩 깊이: `WMX3_AB_APIBUFFER_MAX_IF_LEVEL = 100`

---

## 5. Watch 상태 머신

Watch는 실행 중인 채널에서 지정한 축에 에러가 발생하면 자동 Halt + 트리거 루틴 실행합니다.

```
Watch 비활성화 상태 (watchFlag=0)
    │
    │ SetWatch(enableWatch=true)
    ▼
Watch 활성화 상태 (watchFlag=1)
    │
    │ Motion_Process에서 매 사이클 축 에러 감시
    │
    ├─── 에러 없음: 계속 감시
    │
    └─── 에러 감지:
             │
             ▼
         watchErr=1, watchErrCode=에러코드, watchErrAxis=축번호
             │
             ├── enableTriggerRoutine=true → 트리거 루틴 채널 Execute
             │
             └── 현재 채널 Halt
```

```c
// AB_WATCH_DATA (ApiBuffer.h)
typedef struct {
    unsigned char watchFlag;                // Watch 활성화 여부
    unsigned char watchTriggerRoutineFlag;  // 트리거 루틴 실행 여부
    AB_AXIS_SELECTION watchAxes;            // 감시 대상 축
    int watchTriggerRoutineChannel;         // 트리거 루틴 채널
} AB_WATCH_DATA;
```

---

## 6. 새 모듈에서 상태 머신 설계 원칙

| 원칙 | 설명 |
|------|------|
| 상태 수 최소화 | 필요한 최소한의 상태만 정의 (복잡도 감소) |
| 플래그는 atomic | `unsigned char` 또는 `int` 단일 필드로 상태 표현 |
| 전이 함수 분리 | 상태 전이 로직을 별도 유틸리티 함수로 분리 |
| 재귀 금지 | 상태 평가 시 재귀 호출 절대 금지 (RT 스택 오버플로우) |
| 고정 배열 | 상태 데이터는 컴파일 타임에 크기가 결정된 배열만 사용 |
| 멱등성 보장 | 같은 상태에서 같은 전이 함수를 두 번 호출해도 안전해야 함 |
