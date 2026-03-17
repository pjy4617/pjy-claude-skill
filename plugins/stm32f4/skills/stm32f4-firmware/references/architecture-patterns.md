# STM32F4 Architecture Patterns

## Layered Architecture

STM32F4 펌웨어는 4계층 아키텍처를 사용한다:

```
┌─────────────────────────────┐
│       Application           │  main.c, app_audio.c, app_usb.c
├─────────────────────────────┤
│       Middleware             │  USB Stack, FatFS, Audio Pipeline
├─────────────────────────────┤
│     BSP / Device Drivers    │  codec_driver.c, flash_storage.c
├─────────────────────────────┤
│     HAL / LL Drivers        │  stm32f4xx_hal_spi.c, ...
├─────────────────────────────┤
│       Hardware              │  STM32F4 MCU + External ICs
└─────────────────────────────┘
```

### 계층 간 규칙
- 상위 계층만 하위 계층을 호출할 수 있다 (역방향 호출 금지)
- 하위→상위 통신은 콜백 함수 포인터 또는 이벤트 플래그 사용
- 동일 계층 간 직접 호출은 최소화

## State Machine Pattern

메인 루프 기반 상태 머신 (RTOS 미사용):

```c
typedef enum {
    APP_STATE_IDLE,
    APP_STATE_USB_CONNECTED,
    APP_STATE_RECEIVING,
    APP_STATE_STORING,
    APP_STATE_PLAYING,
    APP_STATE_PAUSED,
    APP_STATE_ERROR,
} AppState_t;

static AppState_t s_appState = APP_STATE_IDLE;

void App_Process(void)
{
    switch (s_appState) {
    case APP_STATE_IDLE:
        if (USB_IsConnected()) {
            s_appState = APP_STATE_USB_CONNECTED;
        }
        break;
    case APP_STATE_USB_CONNECTED:
        if (USB_HasNewFile()) {
            s_appState = APP_STATE_RECEIVING;
        }
        break;
    case APP_STATE_RECEIVING:
        App_ReceiveAndStore();
        if (App_IsTransferComplete()) {
            s_appState = APP_STATE_IDLE;
        }
        break;
    case APP_STATE_PLAYING:
        AudioCodec_FeedData();
        if (AudioCodec_IsFinished()) {
            s_appState = APP_STATE_IDLE;
        }
        break;
    // ...
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    // ... 초기화
    while (1) {
        App_Process();
    }
}
```

## Double Buffer Pattern

오디오 스트리밍이나 연속 데이터 처리에 사용:

```c
#define BUF_SIZE 512

static uint8_t s_buf[2][BUF_SIZE];
static volatile uint8_t s_activeBuf = 0;
static volatile uint8_t s_bufReady = 0;

// ISR/DMA 콜백: 버퍼 전환
void DMA_TransferComplete(void)
{
    s_activeBuf ^= 1;  // 0↔1 토글
    s_bufReady = 1;
    // 다음 DMA 전송 시작 (새 활성 버퍼로)
    HAL_SPI_Transmit_DMA(&hspi1, s_buf[s_activeBuf], BUF_SIZE);
}

// 메인 루프: 비활성 버퍼에 데이터 준비
void App_FillBuffer(void)
{
    if (s_bufReady) {
        uint8_t fillBuf = s_activeBuf ^ 1;  // 비활성 버퍼
        // fillBuf에 새 데이터 로드
        Flash_Read(nextAddr, s_buf[fillBuf], BUF_SIZE);
        s_bufReady = 0;
    }
}
```

## Ring Buffer Pattern

UART/USB 수신 등 비동기 데이터 수집:

```c
typedef struct {
    uint8_t *buffer;
    uint32_t size;
    volatile uint32_t head;  // 쓰기 위치 (ISR)
    volatile uint32_t tail;  // 읽기 위치 (메인)
} RingBuffer_t;

static inline uint32_t RingBuffer_Available(RingBuffer_t *rb) {
    return (rb->head - rb->tail) & (rb->size - 1);
    // size는 2의 거듭제곱이어야 함
}
```

## Module Interface Pattern

외부 디바이스 드라이버의 인터페이스 설계:

```c
// codec_driver.h — 모든 제어 핀을 Init 구조체에 포함
typedef struct {
    SPI_HandleTypeDef *hspi;
    GPIO_TypeDef *cs_port;     // XCS — SCI 명령 CS
    uint16_t cs_pin;
    GPIO_TypeDef *dcs_port;    // XDCS — SDI 데이터 CS (VS1053B 등)
    uint16_t dcs_pin;
    GPIO_TypeDef *dreq_port;   // Data Request 핀
    uint16_t dreq_pin;
    GPIO_TypeDef *reset_port;
    uint16_t reset_pin;
} Codec_InitTypeDef;

typedef struct {
    Codec_InitTypeDef init;
    volatile uint8_t playing;
    uint32_t sampleRate;
    uint8_t volume;
} Codec_HandleTypeDef;

// 공개 API만 노출
HAL_StatusTypeDef Codec_Init(Codec_HandleTypeDef *hcodec, Codec_InitTypeDef *init);
HAL_StatusTypeDef Codec_Reset(Codec_HandleTypeDef *hcodec);
HAL_StatusTypeDef Codec_SetVolume(Codec_HandleTypeDef *hcodec, uint8_t vol);
HAL_StatusTypeDef Codec_PlayStart(Codec_HandleTypeDef *hcodec);
HAL_StatusTypeDef Codec_PlayStop(Codec_HandleTypeDef *hcodec);
HAL_StatusTypeDef Codec_FeedData(Codec_HandleTypeDef *hcodec, uint8_t *data, uint32_t len);
uint8_t Codec_NeedsData(Codec_HandleTypeDef *hcodec);
```

핵심: 외부 디바이스 데이터시트의 "모든" MCU 연결 핀을 Init 구조체에 포함한다.
누락하기 쉬운 핀은 `references/pin-validation.md` Step 4 참조.

## Data Flow Design

데이터 흐름을 파이프라인으로 설계:

```
[USB Host] → [USB MSC] → [Buffer] → [Flash Write]  (저장 경로)
[Flash Read] → [Buffer] → [SPI DMA] → [Codec IC]   (재생 경로)
```

각 단계는 독립적으로 동작하며, 버퍼를 통해 속도 차이를 흡수한다.

## FreeRTOS Task Pattern

Bare-metal에서 태스크가 3개 이상이거나 실시간 제약이 서로 다른 경우 RTOS를 사용한다.

### 태스크 분할 예시 (오디오 플레이어)
```c
// 높은 우선순위: 오디오 스트리밍 (지연 민감)
void AudioTask(void *arg) {
    for (;;) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);  // DMA 완료 대기
        AudioCodec_FeedNextBuffer();
    }
}

// 중간 우선순위: USB 처리
void USBTask(void *arg) {
    for (;;) {
        MX_USB_DEVICE_Process();
        osDelay(1);
    }
}

// 낮은 우선순위: UI / LED
void UITask(void *arg) {
    for (;;) {
        LED_Update();
        Button_Scan();
        osDelay(50);
    }
}
```

### RTOS + HAL 주의사항
- `HAL_Delay()`는 SysTick 기반이므로 RTOS에서는 `osDelay()` 사용
- HAL timebase를 TIM으로 변경 필요 (SysTick은 RTOS 스케줄러가 사용)
- ISR에서 FreeRTOS API 호출 시 반드시 `FromISR` 접미사 버전 사용
- Heap 설정: `configTOTAL_HEAP_SIZE`를 SRAM 여유에 맞게 조정

## Multi-Device SPI Bus Sharing Pattern

SPI 버스에 여러 디바이스(코덱 + SD카드 + 센서 등)를 연결할 때:

### CS 관리 규칙
```c
// 모든 CS를 HIGH(비활성)로 초기화한 뒤, 각 트랜잭션마다 하나만 LOW
#define CODEC_CS_LOW()   do { HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET); } while(0)
#define CODEC_CS_HIGH()  do { HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET); } while(0)
#define SD_CS_LOW()      do { HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_RESET); } while(0)
#define SD_CS_HIGH()     do { HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_SET); } while(0)
```

### 속도 전환
디바이스마다 최대 SPI 클럭이 다르므로, 전환 시 프리스케일러를 변경:
```c
static void SPI_SetSpeed(SPI_HandleTypeDef *hspi, uint32_t prescaler)
{
    __HAL_SPI_DISABLE(hspi);
    MODIFY_REG(hspi->Instance->CR1, SPI_CR1_BR_Msk, prescaler);
    __HAL_SPI_ENABLE(hspi);
}

// 사용 예: 코덱 SCI는 느리게, SD카드는 빠르게
SPI_SetSpeed(&hspi1, SPI_BAUDRATEPRESCALER_32);  // 2.6MHz for codec SCI
CODEC_CS_LOW();
// ... codec SCI transaction ...
CODEC_CS_HIGH();

SPI_SetSpeed(&hspi1, SPI_BAUDRATEPRESCALER_4);   // 21MHz for SD card
SD_CS_LOW();
// ... SD card transaction ...
SD_CS_HIGH();
```

### RTOS 환경에서 버스 잠금
```c
static SemaphoreHandle_t s_spiMutex;

HAL_StatusTypeDef SPI_BusAcquire(uint32_t timeout_ms) {
    return (xSemaphoreTake(s_spiMutex, pdMS_TO_TICKS(timeout_ms)) == pdTRUE)
           ? HAL_OK : HAL_TIMEOUT;
}
void SPI_BusRelease(void) {
    xSemaphoreGive(s_spiMutex);
}
```
