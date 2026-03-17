# STM32F4 Production Checklist & Bootloader Patterns

양산 전 반드시 확인해야 할 항목과 펌웨어 업데이트 구조.

## Production Readiness Checklist

### 1. Watchdog 설정
```c
// IWDG (Independent Watchdog) — LSI 32kHz 기반, 가장 신뢰성 높음
IWDG_HandleTypeDef hiwdg;
hiwdg.Instance = IWDG;
hiwdg.Init.Prescaler = IWDG_PRESCALER_64;  // 32kHz/64 = 500Hz
hiwdg.Init.Reload = 2000;                   // 2000/500 = 4초 타임아웃
HAL_IWDG_Init(&hiwdg);
// 메인 루프에서 주기적으로:
HAL_IWDG_Refresh(&hiwdg);
```
Error_Handler()에서 무한루프 대신 Watchdog 리셋을 기대하거나, 안전 상태로 전환.

### 2. Brown-Out Reset (BOR) 레벨
```c
// Option Bytes에서 BOR 레벨 설정
// BOR_LEVEL3: 2.70~3.60V (3.3V 시스템 권장)
FLASH_OBProgramInitTypeDef obInit;
HAL_FLASHEx_OBGetConfig(&obInit);
obInit.OptionType = OPTIONBYTE_BOR;
obInit.BORLevel = OB_BOR_LEVEL3;
HAL_FLASH_Unlock();
HAL_FLASH_OB_Unlock();
HAL_FLASHEx_OBProgram(&obInit);
HAL_FLASH_OB_Lock();
HAL_FLASH_Lock();
```

### 3. Read Protection (RDP)
- Level 0: 보호 없음 (개발 중)
- Level 1: Flash 읽기 보호 (디버거로 읽기 차단, 해제 시 Flash 전체 삭제)
- Level 2: 영구 보호 (**되돌릴 수 없음! 디버거 연결 불가**)
양산 시 최소 Level 1 설정 권장.

### 4. 미사용 핀 처리
플로팅 핀은 소비전력 증가와 EMI 원인. 미사용 핀은:
```c
// Analog Input 모드 (최소 소비전력)
GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
GPIO_InitStruct.Pull = GPIO_NOPULL;
```

### 5. 클럭 안전 시스템 (CSS)
HSE 크리스탈 고장 시 자동으로 HSI로 전환:
```c
HAL_RCC_EnableCSS();
// NMI_Handler에서 클럭 전환 처리
void NMI_Handler(void) {
    if (__HAL_RCC_GET_IT(RCC_IT_CSS)) {
        __HAL_RCC_CLEAR_IT(RCC_IT_CSS);
        // HSI로 전환된 상태 — 안전 모드 진입
    }
}
```

### 6. Flash Prefetch / Cache
```c
__HAL_FLASH_PREFETCH_BUFFER_ENABLE();
__HAL_FLASH_INSTRUCTION_CACHE_ENABLE();
__HAL_FLASH_DATA_CACHE_ENABLE();
```
이미 SystemClock_Config에서 Flash Latency 설정 시 활성화되지만, 명시적으로 확인.

### 7. SWD 핀 유지
PA13(SWDIO), PA14(SWCLK)을 GPIO로 사용하지 않았는지 최종 확인. 양산 후 디버깅 불가.

### 8. 전원 인가 시퀀스
- 외부 디바이스의 리셋 타이밍 확인 (MCU 부팅 후 충분한 딜레이)
- 전원 안정화 후 HSE 기동 (HAL_RCC_OscConfig가 타임아웃 처리)

---

## Bootloader / OTA Pattern

### 메모리 레이아웃 (듀얼 이미지)
```
0x0800_0000 ┌─────────────────┐
            │ Bootloader      │ Sector 0-1 (32KB)
0x0800_8000 ├─────────────────┤
            │ App Image       │ Sector 2 ~ 7
0x0806_0000 ├─────────────────┤
            │ Update Image    │ Sector 8 ~ 11 (또는 외부 Flash)
            └─────────────────┘
```

### 부트로더 → 앱 점프
```c
typedef void (*AppEntry_t)(void);

void Bootloader_JumpToApp(uint32_t appAddr)
{
    uint32_t appStack = *(volatile uint32_t *)appAddr;
    uint32_t appEntry = *(volatile uint32_t *)(appAddr + 4);

    // 스택 포인터가 SRAM 범위인지 검증
    if ((appStack & 0x2FFE0000) != 0x20000000) return;

    HAL_RCC_DeInit();       // 클럭을 기본 상태로
    HAL_DeInit();           // HAL 디초기화
    SysTick->CTRL = 0;     // SysTick 비활성화
    __disable_irq();

    // 벡터 테이블 재배치
    SCB->VTOR = appAddr;

    __set_MSP(appStack);
    AppEntry_t appEntryFunc = (AppEntry_t)appEntry;
    appEntryFunc();
}
```

### 앱 측 링커 스크립트 수정
```
MEMORY
{
    FLASH (rx) : ORIGIN = 0x08008000, LENGTH = 352K  /* Sector 2부터 시작 */
    RAM (xrw)  : ORIGIN = 0x20000000, LENGTH = 128K
}
```

### 앱 측 system_stm32f4xx.c 수정
```c
#define VECT_TAB_OFFSET  0x8000  /* 앱 시작 오프셋 */
```
