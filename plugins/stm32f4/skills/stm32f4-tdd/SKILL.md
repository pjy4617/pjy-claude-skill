---
name: stm32f4-tdd
description: "STM32F4 펌웨어의 호스트 기반 단위 테스트 생성 및 실행. Unity + FFF(Fake Function Framework)를 사용하여 PC에서 애플리케이션 로직, 상태 머신, 프로토콜 파서, 드라이버 로직을 테스트합니다. 'STM32 테스트', 'TDD', '단위 테스트 추가', '테스트 코드 작성', 'Unity 테스트', '펌웨어 테스트', '함수 테스트해줘', '로직 검증' 등의 요청에 자동 적용."
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: [모듈명 또는 함수명]
---

# STM32F4 호스트 기반 TDD (Test-Driven Development)

> 이 스킬은 테스트 체계와 패턴을 정의합니다.
> 실제 테스트 코드 작성은 **stm32f4-test-writer 에이전트**에게 위임됩니다.

## 핵심 원칙

1. **호스트 기반 테스트**: PC(x86/x64)에서 실행. MCU 하드웨어 불필요.
2. **HAL을 Fake로 대체**: FFF(Fake Function Framework)로 HAL 함수를 가짜로 치환.
3. **Red → Green → Refactor**: 실패하는 테스트 먼저 → 최소 구현 → 리팩토링.
4. **테스트 가능한 것만 테스트**: 하드웨어 직접 의존 코드는 대상에서 제외.

## 테스트 가능 / 불가능 범위

### 테스트 가능 (호스트에서 실행)
| 대상 | 예시 | 가치 |
|------|------|------|
| 상태 머신 로직 | OLED FSM, 모터 제어 FSM | 높음 |
| 프로토콜 파서 | SPI 명령 해석, UART 패킷 파싱 | 높음 |
| 수학/계산 함수 | CRC, PID 제어, 필터, 클럭 계산 | 높음 |
| 링 버퍼 / FIFO | 데이터 큐, 로그 버퍼 | 중간 |
| 설정값 검증 | 핀 설정 범위, 클럭 분주비 | 중간 |
| 디바이스 드라이버 (HAL Mock) | SPI 전송 시퀀스, I2C 레지스터 읽기 | 중간 |
| 애플리케이션 로직 | 버튼 디바운스, LED 패턴, 메뉴 시스템 | 높음 |

### 테스트 불가 (하드웨어 필요)
- HAL 레지스터 직접 접근, 인터럽트 래이턴시, DMA 전송 타이밍
- 실제 SPI/I2C 버스 통신, GPIO 전기적 동작
- 실시간 스케줄링 (RTOS 태스크 전환 타이밍)

---

## 테스트 프로젝트 구조

기존 프로젝트에 `test/` 디렉토리를 추가:

```
project-name/
├── Core/Src/Inc/                # 기존 소스
├── Drivers/                     # 기존 드라이버
├── test/                        # 🆕 테스트 루트
│   ├── Makefile                 # 호스트 빌드 (gcc, NOT arm-none-eabi-gcc)
│   ├── unity/                   # Unity 프레임워크 소스
│   │   ├── unity.c
│   │   ├── unity.h
│   │   └── unity_internals.h
│   ├── fff/                     # FFF (Fake Function Framework)
│   │   └── fff.h
│   ├── fakes/                   # HAL Fake 구현
│   │   ├── fake_stm32f4xx_hal.h # HAL 타입 정의 (최소)
│   │   ├── fake_hal_spi.h       # SPI HAL Fake
│   │   ├── fake_hal_gpio.h      # GPIO HAL Fake
│   │   ├── fake_hal_uart.h      # UART HAL Fake
│   │   └── fake_hal_i2c.h       # I2C HAL Fake
│   ├── test_app_logic.c         # 애플리케이션 로직 테스트
│   ├── test_state_machine.c     # 상태 머신 테스트
│   ├── test_protocol_parser.c   # 프로토콜 파서 테스트
│   ├── test_device_driver.c     # 디바이스 드라이버 테스트 (HAL Mock)
│   ├── test_ring_buffer.c       # 링 버퍼 테스트
│   └── test_runner.c            # 메인 테스트 러너
├── CMakeLists.txt               # 타겟 빌드 (arm)
└── Makefile                     # 타겟 빌드 (arm)
```

## 테스트 프레임워크

### Unity (C 단위 테스트)
경량 C 테스트 프레임워크. 임베디드에 최적화.

```c
#include "unity.h"
#include "app_logic.h"

void setUp(void) { /* 각 테스트 전 초기화 */ }
void tearDown(void) { /* 각 테스트 후 정리 */ }

void test_temperature_conversion(void) {
    // ADC 원시값 → 온도 변환 검증
    TEST_ASSERT_EQUAL_FLOAT(25.0f, ADC_ToTemperature(2048));
    TEST_ASSERT_EQUAL_FLOAT(0.0f, ADC_ToTemperature(0));
    TEST_ASSERT_EQUAL_FLOAT(100.0f, ADC_ToTemperature(4095));
}

void test_temperature_out_of_range(void) {
    // 경계값 테스트
    TEST_ASSERT_EQUAL_FLOAT(-40.0f, ADC_ToTemperature(-1));  // 언더플로우
}
```

### FFF (Fake Function Framework)
HAL 함수를 Fake로 대체. Mock보다 가볍고 설정이 간단.

```c
#include "fff.h"
DEFINE_FFF_GLOBALS;

// HAL_SPI_Transmit을 Fake로 선언
FAKE_VALUE_FUNC(HAL_StatusTypeDef, HAL_SPI_Transmit,
    SPI_HandleTypeDef*, uint8_t*, uint16_t, uint32_t);

// HAL_GPIO_WritePin을 Fake로 선언
FAKE_VOID_FUNC(HAL_GPIO_WritePin,
    GPIO_TypeDef*, uint16_t, GPIO_PinState);

void setUp(void) {
    RESET_FAKE(HAL_SPI_Transmit);
    RESET_FAKE(HAL_GPIO_WritePin);
    FFF_RESET_HISTORY();
}

void test_codec_send_command(void) {
    // SPI 전송이 성공하도록 Fake 설정
    HAL_SPI_Transmit_fake.return_val = HAL_OK;

    // 테스트 대상 함수 호출
    HAL_StatusTypeDef result = Codec_SendCommand(0x0B, 0x0000);

    // 검증: SPI가 호출되었는가?
    TEST_ASSERT_EQUAL(1, HAL_SPI_Transmit_fake.call_count);
    // 검증: CS 핀이 LOW → HIGH로 토글되었는가?
    TEST_ASSERT_EQUAL(2, HAL_GPIO_WritePin_fake.call_count);
    // 검증: 결과가 OK인가?
    TEST_ASSERT_EQUAL(HAL_OK, result);
}

void test_codec_send_command_spi_fail(void) {
    // SPI 전송 실패 시나리오
    HAL_SPI_Transmit_fake.return_val = HAL_ERROR;

    HAL_StatusTypeDef result = Codec_SendCommand(0x0B, 0x0000);

    TEST_ASSERT_EQUAL(HAL_ERROR, result);
}
```

## HAL Fake 최소 타입 정의

테스트 코드가 컴파일되려면 HAL 타입이 필요하지만, 실제 HAL 헤더 전체를 포함하면 하드웨어 의존성이 따라옴. 최소한의 타입만 정의:

```c
// fake_stm32f4xx_hal.h — 테스트용 최소 HAL 타입
#ifndef FAKE_STM32F4XX_HAL_H
#define FAKE_STM32F4XX_HAL_H

#include <stdint.h>

// 상태 열거형
typedef enum {
    HAL_OK       = 0x00,
    HAL_ERROR    = 0x01,
    HAL_BUSY     = 0x02,
    HAL_TIMEOUT  = 0x03
} HAL_StatusTypeDef;

// GPIO
typedef struct { uint32_t dummy; } GPIO_TypeDef;
typedef enum { GPIO_PIN_RESET = 0, GPIO_PIN_SET = 1 } GPIO_PinState;

// SPI
typedef struct {
    uint32_t dummy;
} SPI_HandleTypeDef;

// I2C
typedef struct {
    uint32_t dummy;
} I2C_HandleTypeDef;

// UART
typedef struct {
    uint32_t dummy;
} UART_HandleTypeDef;

// 타이머
typedef struct {
    uint32_t dummy;
} TIM_HandleTypeDef;

// GPIO 핀 정의 (비트마스크)
#define GPIO_PIN_0  ((uint16_t)0x0001)
#define GPIO_PIN_1  ((uint16_t)0x0002)
#define GPIO_PIN_2  ((uint16_t)0x0004)
#define GPIO_PIN_3  ((uint16_t)0x0008)
#define GPIO_PIN_4  ((uint16_t)0x0010)
#define GPIO_PIN_5  ((uint16_t)0x0020)
// ... 필요한 만큼 추가

// GPIO 포트 (더미)
extern GPIO_TypeDef fake_GPIOA, fake_GPIOB, fake_GPIOC, fake_GPIOD;
#define GPIOA (&fake_GPIOA)
#define GPIOB (&fake_GPIOB)
#define GPIOC (&fake_GPIOC)
#define GPIOD (&fake_GPIOD)

// HAL_MAX_DELAY
#define HAL_MAX_DELAY 0xFFFFFFFF

#endif
```

## 테스트 빌드 (호스트용 Makefile)

```makefile
# test/Makefile — 호스트(PC)에서 실행하는 테스트 빌드
CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -g -O0
CFLAGS += -DUNIT_TEST  # 테스트 빌드 식별 매크로

# 인클루드 경로
CFLAGS += -I.
CFLAGS += -Iunity
CFLAGS += -Ifff
CFLAGS += -Ifakes
CFLAGS += -I../Core/Inc
CFLAGS += -I../Drivers/BSP/Inc
CFLAGS += -I../Drivers/Device/Inc

# 소스 파일
TEST_SOURCES = $(wildcard test_*.c) test_runner.c
UNITY_SOURCE = unity/unity.c
# 테스트 대상 소스 (HAL 미의존 모듈만)
SUT_SOURCES = \
    ../Core/Src/app_logic.c \
    ../Drivers/Device/Src/codec_driver.c

SOURCES = $(TEST_SOURCES) $(UNITY_SOURCE) $(SUT_SOURCES)
TARGET = test_runner

all: $(TARGET)
	./$(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $^ -o $@ -lm

clean:
	rm -f $(TARGET)

.PHONY: all clean
```

## 테스트 러너

```c
// test_runner.c
#include "unity.h"

// 각 테스트 파일에서 선언된 테스트 함수를 extern
extern void test_temperature_conversion(void);
extern void test_temperature_out_of_range(void);
extern void test_codec_send_command(void);
extern void test_codec_send_command_spi_fail(void);
extern void test_state_machine_idle_to_active(void);
// ... 추가 테스트

int main(void) {
    UNITY_BEGIN();

    // 애플리케이션 로직
    RUN_TEST(test_temperature_conversion);
    RUN_TEST(test_temperature_out_of_range);

    // 디바이스 드라이버
    RUN_TEST(test_codec_send_command);
    RUN_TEST(test_codec_send_command_spi_fail);

    // 상태 머신
    RUN_TEST(test_state_machine_idle_to_active);

    return UNITY_END();
}
```

## 테스트 가능한 코드 작성 패턴

### 패턴 1: HAL 의존성 분리

```c
// ❌ 나쁨 — HAL 직접 호출, 테스트 불가
void LED_Toggle(void) {
    HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
}

// ✅ 좋음 — 로직과 HAL 분리
typedef struct {
    GPIO_TypeDef *port;
    uint16_t pin;
    uint8_t state;
} LED_Handle_t;

void LED_Toggle(LED_Handle_t *led) {
    led->state = !led->state;
    HAL_GPIO_WritePin(led->port, led->pin,
        led->state ? GPIO_PIN_SET : GPIO_PIN_RESET);
}
// 테스트에서는 HAL_GPIO_WritePin을 FFF로 Fake하고,
// led->state만 검증하면 된다.
```

### 패턴 2: 순수 함수 추출

```c
// ❌ 나쁨 — ADC 읽기 + 변환이 결합
float ReadTemperature(void) {
    uint32_t raw = HAL_ADC_GetValue(&hadc1);
    return (float)raw * 3.3f / 4095.0f * 100.0f;
}

// ✅ 좋음 — 변환 로직을 순수 함수로 분리
float ADC_ToTemperature(uint32_t raw_value) {
    return (float)raw_value * 3.3f / 4095.0f * 100.0f;
}
// ADC_ToTemperature는 HAL 의존성 없이 단독 테스트 가능
```

### 패턴 3: 상태 머신 테스트

```c
// 상태 머신이 테스트 가능하려면 입력/출력이 명확해야 한다
typedef enum { STATE_IDLE, STATE_ACTIVE, STATE_ERROR } AppState_t;
typedef struct {
    AppState_t state;
    uint32_t error_count;
    uint8_t output_enabled;
} AppFSM_t;

// 순수 상태 전이 함수 — 테스트 최적
AppState_t FSM_HandleEvent(AppFSM_t *fsm, uint8_t event) {
    switch (fsm->state) {
        case STATE_IDLE:
            if (event == EVT_START) {
                fsm->output_enabled = 1;
                return STATE_ACTIVE;
            }
            break;
        case STATE_ACTIVE:
            if (event == EVT_ERROR) {
                fsm->error_count++;
                fsm->output_enabled = 0;
                return STATE_ERROR;
            }
            break;
        // ...
    }
    return fsm->state;
}
```

### 패턴 4: #ifdef UNIT_TEST 가드

```c
// 프로덕션과 테스트 빌드에서 다른 헤더 사용
#ifdef UNIT_TEST
    #include "fake_stm32f4xx_hal.h"
#else
    #include "stm32f4xx_hal.h"
#endif
```

## TDD 워크플로우

```
1. RED   — 실패하는 테스트 먼저 작성
           cd test && make → FAIL 확인

2. GREEN — 테스트를 통과하는 최소한의 코드 구현
           코드 수정 → cd test && make → PASS 확인

3. REFACTOR — 테스트 통과 상태에서 코드 개선
              리팩토링 → cd test && make → 여전히 PASS 확인

4. 타겟 빌드 — 테스트 통과 후 MCU 빌드
              cd .. && make (또는 cmake --build --preset debug)
```

## stm32f4-firmware 스킬과의 연동

펌웨어 생성 후 테스트를 추가하는 플로우:

```
"STM32F407 펌웨어 만들어줘"
  → stm32f4-firmware 스킬이 코드 생성
  → "테스트 추가해줘"
  → stm32f4-tdd 스킬 트리거
  → stm32f4-test-writer 에이전트가 테스트 코드 생성
  → "테스트 실행해줘"
  → cd test && make → 결과 확인
```

또는 처음부터 TDD로 진행:

```
"TDD로 STM32F407 SPI 코덱 드라이버 만들어줘"
  → stm32f4-test-writer 에이전트가 실패하는 테스트 먼저 작성
  → stm32f4-firmware의 Agent 3이 최소 구현
  → 테스트 실행 → PASS 확인
  → 다음 기능 반복
```

$ARGUMENTS
