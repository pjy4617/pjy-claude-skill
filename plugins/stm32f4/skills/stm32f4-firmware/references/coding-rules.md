# STM32F4 Coding Rules & Conventions

## Naming Conventions

| 항목 | 규칙 | 예시 |
|------|------|------|
| 파일명 | 소문자_스네이크 | `audio_codec.c`, `flash_storage.h` |
| 함수명 | 모듈_동사_대상 PascalCase | `AudioCodec_Init()`, `Flash_WriteSector()` |
| 전역 변수 | g_ 접두사 | `g_audioState`, `g_usbConnected` |
| 정적 변수 | s_ 접두사 | `static uint8_t s_buffer[512]` |
| 매크로 | 대문자_스네이크 | `AUDIO_SAMPLE_RATE`, `FLASH_SECTOR_SIZE` |
| typedef 구조체 | 모듈_TypeDef | `AudioCodec_HandleTypeDef` |
| typedef 열거형 | 모듈_상태 | `AudioState_t` |
| HAL 핸들 | h + 페리페럴 | `hspi1`, `huart2`, `htim3` |

## Header File Template

```c
/**
 * @file    module_name.h
 * @brief   모듈 설명
 * @author  프로젝트명
 * @date    YYYY-MM-DD
 */
#ifndef __MODULE_NAME_H
#define __MODULE_NAME_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ----------------------------------------------------------*/
#include "stm32f4xx_hal.h"

/* Exported types ----------------------------------------------------*/
typedef enum {
    MODULE_STATE_IDLE = 0,
    MODULE_STATE_BUSY,
    MODULE_STATE_ERROR,
} ModuleState_t;

typedef struct {
    ModuleState_t state;
    // ...
} Module_HandleTypeDef;

/* Exported constants ------------------------------------------------*/
#define MODULE_BUFFER_SIZE    512

/* Exported functions ------------------------------------------------*/
HAL_StatusTypeDef Module_Init(Module_HandleTypeDef *handle);
HAL_StatusTypeDef Module_DeInit(Module_HandleTypeDef *handle);
HAL_StatusTypeDef Module_Process(Module_HandleTypeDef *handle);

#ifdef __cplusplus
}
#endif
#endif /* __MODULE_NAME_H */
```

## Source File Template

```c
/**
 * @file    module_name.c
 * @brief   모듈 구현
 */
#include "module_name.h"

/* Private defines ---------------------------------------------------*/
/* Private variables -------------------------------------------------*/
/* Private function prototypes ---------------------------------------*/
static void Module_InternalHelper(void);

/* Exported functions ------------------------------------------------*/
HAL_StatusTypeDef Module_Init(Module_HandleTypeDef *handle)
{
    if (handle == NULL) return HAL_ERROR;
    handle->state = MODULE_STATE_IDLE;
    return HAL_OK;
}

/* Private functions -------------------------------------------------*/
static void Module_InternalHelper(void)
{
    // ...
}
```

## HAL Usage Guidelines

1. **HAL 반환값은 항상 체크한다**
   ```c
   // 좋음
   if (HAL_SPI_Transmit(&hspi1, data, len, 100) != HAL_OK) {
       return HAL_ERROR;
   }
   // 나쁨 - 에러 무시
   HAL_SPI_Transmit(&hspi1, data, len, 100);
   ```

2. **타임아웃 값을 적절히 설정한다** — HAL_MAX_DELAY는 개발 중에만 사용
   ```c
   // 개발 중
   HAL_SPI_Transmit(&hspi1, data, len, HAL_MAX_DELAY);
   // 프로덕션
   HAL_SPI_Transmit(&hspi1, data, len, 100); // 100ms 타임아웃
   ```

3. **volatile 키워드**: ISR과 메인 루프가 공유하는 변수는 반드시 volatile
   ```c
   volatile uint8_t g_usbDataReady = 0;
   ```

4. **인터럽트 핸들러는 짧게 유지**: 플래그만 세팅하고 메인 루프에서 처리
   ```c
   void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi) {
       g_spiTxComplete = 1;  // 플래그만 세팅
   }
   ```

5. **매직 넘버 금지**: 모든 상수는 #define 또는 enum으로 정의

## Critical Section & Atomic Access

ISR과 메인 루프가 공유 변수를 사용할 때, `volatile`만으로는 **멀티바이트 값의 원자성**이 보장되지 않는다.

### 패턴 1: 인터럽트 비활성화 (가장 간단, 짧은 구간에만)
```c
// 32비트보다 큰 데이터 또는 여러 변수를 원자적으로 읽기
__disable_irq();
uint32_t localCount = g_sampleCount;
uint32_t localAddr  = g_playAddress;
__enable_irq();
```
주의: `__disable_irq()`는 모든 인터럽트를 차단하므로 수 마이크로초 이내로 유지. 이 구간 안에서 HAL 함수나 지연 호출 금지.

### 패턴 2: BASEPRI를 이용한 선택적 차단
```c
// 우선순위 4 이하(숫자 ≥4)의 인터럽트만 차단, 0-3은 통과
__set_BASEPRI(4 << (8 - __NVIC_PRIO_BITS));
// ... critical section ...
__set_BASEPRI(0);  // 해제
```

### 패턴 3: 단일 32비트 값은 volatile만으로 충분
Cortex-M4에서 정렬된 32비트 읽기/쓰기는 원자적이다:
```c
volatile uint32_t g_flags;  // ISR에서 설정, 메인에서 읽기 — OK
volatile uint8_t g_byte;    // 8비트도 원자적 — OK
// 하지만 read-modify-write(g_flags |= 0x01)는 원자적이지 않음!
```

### 패턴 4: 원자적 Read-Modify-Write (LDREX/STREX)
```c
static inline void AtomicSetBit(volatile uint32_t *addr, uint32_t bit)
{
    uint32_t val;
    do {
        val = __LDREXW(addr);
        val |= bit;
    } while (__STREXW(val, addr) != 0);
    __DMB();
}
```

### 절대 하지 말 것
```c
// 나쁨: ISR과 메인이 같은 64비트 변수를 공유 (비원자적)
volatile uint64_t g_timestamp;
// ISR에서 쓰기, 메인에서 읽기 → 중간에 인터럽트 발생 시 절반만 갱신된 값을 읽음
// → __disable_irq() 감싸거나, 32비트 2개로 분리하고 순서 보장
```

## Memory Alignment

- DMA 버퍼: 4바이트 정렬 권장
  ```c
  __attribute__((aligned(4))) uint8_t dma_buffer[512];
  ```
- CCM에 배치할 변수:
  ```c
  __attribute__((section(".ccmram"))) uint32_t ccm_data[1024];
  ```

## Interrupt Priority Guidelines

STM32F4 NVIC는 4비트 우선순위 (0-15, 0이 최고):

| 우선순위 | 용도 |
|----------|------|
| 0-1 | 하드웨어 안전 크리티컬 (긴급 정지 등, 일반적으로 미사용) |
| 2-3 | 실시간 페리페럴 (DMA 완료, 고속 통신) |
| 4-5 | USB, 오디오 |
| 6-8 | 일반 통신 (UART, I2C) |
| 9-14 | 저우선순위 (GPIO EXTI, 타이머) |
| 15 | SysTick (**HAL이 기본으로 15를 할당**, 이 값을 변경하지 말 것) |

**SysTick 주의**: HAL은 SysTick을 우선순위 **15(가장 낮음)**로 설정한다. 이는 다른 인터럽트가 SysTick보다 높은 우선순위를 가지도록 보장하기 위함이다. DMA 전송 중에도 SysTick이 HAL_GetTick()을 정상 업데이트하려면 DMA 인터럽트가 SysTick보다 높은 우선순위여야 한다 — 이미 기본값이 그렇게 되어 있다. RTOS 사용 시 SysTick을 RTOS 스케줄러용으로 예약하고, HAL timebase는 별도 TIM을 사용한다.
