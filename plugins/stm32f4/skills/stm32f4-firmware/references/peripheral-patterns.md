# STM32F4 Peripheral Patterns Reference

이 문서는 STM32F4 HAL 기반 주변장치 초기화 및 운용 패턴을 제공한다.

## Table of Contents
1. [SPI Master](#spi-master)
2. [SPI with DMA](#spi-with-dma)
3. [USB OTG FS Device (MSC)](#usb-otg-fs-device-msc)
4. [Internal Flash Read/Write](#internal-flash-readwrite)
5. [I2C Master](#i2c-master)
6. [UART with DMA](#uart-with-dma)
7. [Timer (PWM)](#timer-pwm)
8. [ADC with DMA](#adc-with-dma)
9. [GPIO](#gpio)
10. [DMA General](#dma-general)
11. [Watchdog (IWDG / WWDG)](#watchdog-iwdg--wwdg)
12. [DAC Output](#dac-output)
13. [CAN Bus](#can-bus)
14. [SDIO (SD Card)](#sdio-sd-card-4-bit-mode)
15. [Low Power Modes](#low-power-modes)

---

## SPI Master

### HAL MSP (stm32f4xx_hal_msp.c)
```c
void HAL_SPI_MspInit(SPI_HandleTypeDef* hspi)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    if (hspi->Instance == SPI1) {
        __HAL_RCC_SPI1_CLK_ENABLE();
        __HAL_RCC_GPIOA_CLK_ENABLE();
        // PA5=SCK, PA6=MISO, PA7=MOSI
        GPIO_InitStruct.Pin = GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7;
        GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
        GPIO_InitStruct.Alternate = GPIO_AF5_SPI1;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    }
}
```

### 초기화 (Polling 모드)
```c
SPI_HandleTypeDef hspi1;

void MX_SPI1_Init(void)
{
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_8;
    // APB2=84MHz, /8 = 10.5MHz
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    if (HAL_SPI_Init(&hspi1) != HAL_OK) {
        Error_Handler();
    }
}
```

### CS(Chip Select) 제어 — 소프트웨어 NSS
```c
#define CODEC_CS_PIN     GPIO_PIN_4
#define CODEC_CS_PORT    GPIOA
#define CODEC_CS_LOW()   HAL_GPIO_WritePin(CODEC_CS_PORT, CODEC_CS_PIN, GPIO_PIN_RESET)
#define CODEC_CS_HIGH()  HAL_GPIO_WritePin(CODEC_CS_PORT, CODEC_CS_PIN, GPIO_PIN_SET)
```

### SPI 전송/수신
```c
// 송신만
HAL_SPI_Transmit(&hspi1, txData, len, HAL_MAX_DELAY);

// 수신만
HAL_SPI_Receive(&hspi1, rxData, len, HAL_MAX_DELAY);

// 양방향 (Full-Duplex)
HAL_SPI_TransmitReceive(&hspi1, txData, rxData, len, HAL_MAX_DELAY);

// CS 포함 트랜잭션
CODEC_CS_LOW();
HAL_SPI_Transmit(&hspi1, cmd, cmdLen, 100);
HAL_SPI_Receive(&hspi1, resp, respLen, 100);
CODEC_CS_HIGH();
```

---

## SPI with DMA

### DMA 설정 (HAL MSP 내)
```c
static DMA_HandleTypeDef hdma_spi1_tx;
static DMA_HandleTypeDef hdma_spi1_rx;

void HAL_SPI_MspInit(SPI_HandleTypeDef* hspi)
{
    if (hspi->Instance == SPI1) {
        __HAL_RCC_SPI1_CLK_ENABLE();
        __HAL_RCC_DMA2_CLK_ENABLE();
        // GPIO init 생략...

        // TX DMA: DMA2 Stream3 Channel3
        hdma_spi1_tx.Instance = DMA2_Stream3;
        hdma_spi1_tx.Init.Channel = DMA_CHANNEL_3;
        hdma_spi1_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
        hdma_spi1_tx.Init.PeriphInc = DMA_PINC_DISABLE;
        hdma_spi1_tx.Init.MemInc = DMA_MINC_ENABLE;
        hdma_spi1_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
        hdma_spi1_tx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
        hdma_spi1_tx.Init.Mode = DMA_NORMAL;
        hdma_spi1_tx.Init.Priority = DMA_PRIORITY_HIGH;
        hdma_spi1_tx.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
        HAL_DMA_Init(&hdma_spi1_tx);
        __HAL_LINKDMA(hspi, hdmatx, hdma_spi1_tx);

        // RX DMA: DMA2 Stream0 Channel3
        hdma_spi1_rx.Instance = DMA2_Stream0;
        hdma_spi1_rx.Init.Channel = DMA_CHANNEL_3;
        hdma_spi1_rx.Init.Direction = DMA_PERIPH_TO_MEMORY;
        // ... 나머지 동일
        HAL_DMA_Init(&hdma_spi1_rx);
        __HAL_LINKDMA(hspi, hdmarx, hdma_spi1_rx);

        // NVIC
        HAL_NVIC_SetPriority(DMA2_Stream3_IRQn, 1, 0);
        HAL_NVIC_EnableIRQ(DMA2_Stream3_IRQn);
        HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 1, 0);
        HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);
        HAL_NVIC_SetPriority(SPI1_IRQn, 1, 0);
        HAL_NVIC_EnableIRQ(SPI1_IRQn);
    }
}
```

### DMA 전송
```c
// DMA 전송 시작 (논블로킹)
HAL_SPI_Transmit_DMA(&hspi1, txBuf, len);

// 완료 콜백
void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi->Instance == SPI1) {
        // 전송 완료 처리
        CODEC_CS_HIGH();
    }
}
```

주의: DMA 버퍼는 CCM(0x1000_0000)에 위치하면 안 됨. SRAM1/SRAM2만 사용.

---

## USB OTG FS Device (MSC)

### USB GPIO 설정
```c
// PA11=USB_DM, PA12=USB_DP (AF10)
void HAL_PCD_MspInit(PCD_HandleTypeDef *hpcd)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    if (hpcd->Instance == USB_OTG_FS) {
        __HAL_RCC_GPIOA_CLK_ENABLE();
        GPIO_InitStruct.Pin = GPIO_PIN_11 | GPIO_PIN_12;
        GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
        GPIO_InitStruct.Alternate = GPIO_AF10_OTG_FS;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

        __HAL_RCC_USB_OTG_FS_CLK_ENABLE();
        HAL_NVIC_SetPriority(OTG_FS_IRQn, 5, 0);
        HAL_NVIC_EnableIRQ(OTG_FS_IRQn);
    }
}
```

### USB MSC (Mass Storage Class) 패턴
USB MSC 구현은 ST의 USB Device Library를 활용한다:
- `usbd_core.c/h` — USB 코어
- `usbd_msc.c/h` — MSC 클래스
- `usbd_msc_bot.c/h` — Bulk-Only Transport
- `usbd_msc_scsi.c/h` — SCSI 명령 처리
- `usbd_storage.c/h` — 스토리지 미디어 인터페이스 (사용자 구현)

스토리지 콜백 구조:
```c
USBD_StorageTypeDef USBD_Storage_Fops = {
    .Init    = STORAGE_Init,
    .GetCapacity  = STORAGE_GetCapacity,
    .IsReady      = STORAGE_IsReady,
    .IsWriteProtected = STORAGE_IsWriteProtected,
    .Read    = STORAGE_Read,     // 호스트→디바이스: LBA 단위 읽기
    .Write   = STORAGE_Write,    // 호스트→디바이스: LBA 단위 쓰기
    .GetMaxLun    = STORAGE_GetMaxLun,
    .InquiryData  = STORAGE_Inquirydata,
};
```

### USB VBUS 감지 (Self-Powered 디바이스)
Bus-Powered(USB 전원 사용) 디바이스는 VBUS 감지가 불필요하지만, Self-Powered(외부 전원) 디바이스에서는 PA9를 VBUS 감지에 사용해야 호스트 연결/해제를 인식할 수 있다:
```c
// PA9 = OTG_FS_VBUS (AF 없이 GPIO Input으로 사용)
GPIO_InitStruct.Pin = GPIO_PIN_9;
GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
GPIO_InitStruct.Pull = GPIO_NOPULL;
HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
```
VBUS 감지를 사용하지 않으면 `usbd_conf.c`에서 VBUS sensing을 비활성화:
```c
hpcd.Init.vbus_sensing_enable = DISABLE;
```

---

## Internal Flash Read/Write

### Flash 읽기 (직접 메모리 접근)
```c
// Flash는 메모리 매핑되어 있으므로 직접 읽기 가능
uint32_t data = *(volatile uint32_t*)0x08060000;

// 블록 복사
memcpy(buffer, (void*)FLASH_DATA_START_ADDR, size);
```

### Flash 쓰기
```c
HAL_StatusTypeDef Flash_Write(uint32_t addr, uint8_t *data, uint32_t len)
{
    HAL_FLASH_Unlock();
    __HAL_FLASH_CLEAR_FLAG(FLASH_FLAG_EOP | FLASH_FLAG_OPERR |
                           FLASH_FLAG_WRPERR | FLASH_FLAG_PGAERR |
                           FLASH_FLAG_PGPERR | FLASH_FLAG_PGSERR);

    // 바이트 단위 쓰기 (FLASH_TYPEPROGRAM_BYTE)
    for (uint32_t i = 0; i < len; i++) {
        if (HAL_FLASH_Program(FLASH_TYPEPROGRAM_BYTE,
                              addr + i, data[i]) != HAL_OK) {
            HAL_FLASH_Lock();
            return HAL_ERROR;
        }
    }
    HAL_FLASH_Lock();
    return HAL_OK;
}
```

### Flash 섹터 Erase
```c
HAL_StatusTypeDef Flash_EraseSector(uint32_t sector)
{
    FLASH_EraseInitTypeDef eraseInit;
    uint32_t sectorError;

    HAL_FLASH_Unlock();
    eraseInit.TypeErase = FLASH_TYPEERASE_SECTORS;
    eraseInit.Sector = sector;          // FLASH_SECTOR_4 등
    eraseInit.NbSectors = 1;
    eraseInit.VoltageRange = FLASH_VOLTAGE_RANGE_3; // 2.7~3.6V

    HAL_StatusTypeDef status = HAL_FLASHEx_Erase(&eraseInit, &sectorError);
    HAL_FLASH_Lock();
    return status;
}
```

### ⚠ Flash 쓰기 중 코드 실행 주의 (Bus Stall)
STM32F4 Single Bank Flash에서 Erase/Write 중에는 **같은 Flash에서 코드를 읽을 수 없다**. 모든 인터럽트 핸들러, DMA 콜백, 심지어 SysTick도 Flash에서 실행되므로, Flash 쓰기 중에는 시스템 전체가 멈춘다 (수십 ms ~ 수 초).

대응 방법:
1. **인터럽트 비활성화 후 쓰기**: `__disable_irq()` → Flash 쓰기 → `__enable_irq()`. 단순하지만 실시간성 상실.
2. **RAM에서 Flash 쓰기 함수 실행**:
   ```c
   __attribute__((section(".RamFunc"))) void Flash_WriteFromRAM(uint32_t addr, uint32_t data) {
       HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, addr, data);
   }
   ```
   링커 스크립트에 `.RamFunc` 섹션 추가 필요.
3. **F429 Dual Bank 모드**: Bank 1에서 코드 실행, Bank 2에 데이터 쓰기 → 스톨 없음.

---

## I2C Master

```c
I2C_HandleTypeDef hi2c1;

void MX_I2C1_Init(void)
{
    hi2c1.Instance = I2C1;
    hi2c1.Init.ClockSpeed = 400000;         // 400kHz Fast Mode
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
    HAL_I2C_Init(&hi2c1);
}

// 레지스터 쓰기
HAL_I2C_Mem_Write(&hi2c1, devAddr << 1, regAddr, I2C_MEMADD_SIZE_8BIT,
                  &data, 1, 100);
// 레지스터 읽기
HAL_I2C_Mem_Read(&hi2c1, devAddr << 1, regAddr, I2C_MEMADD_SIZE_8BIT,
                 buffer, len, 100);
```

---

## UART with DMA

```c
UART_HandleTypeDef huart2;

void MX_USART2_Init(void)
{
    huart2.Instance = USART2;
    huart2.Init.BaudRate = 115200;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart2);
}

// DMA 수신 (링 버퍼 패턴)
uint8_t dma_rx_buf[256];
HAL_UART_Receive_DMA(&huart2, dma_rx_buf, sizeof(dma_rx_buf));
// DMA Circular 모드 사용 시 hdma_usart2_rx.Init.Mode = DMA_CIRCULAR;
```

---

## Timer (PWM)

```c
TIM_HandleTypeDef htim3;

void MX_TIM3_Init(void)
{
    TIM_OC_InitTypeDef sConfigOC = {0};

    htim3.Instance = TIM3;
    htim3.Init.Prescaler = 83;          // 84MHz/84 = 1MHz
    htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim3.Init.Period = 999;            // 1MHz/1000 = 1kHz PWM
    htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    HAL_TIM_PWM_Init(&htim3);

    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 500;              // 50% duty
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
}
```

---

## ADC with DMA

```c
ADC_HandleTypeDef hadc1;
uint16_t adc_buf[4]; // 4채널 DMA 변환

void MX_ADC1_Init(void)
{
    ADC_ChannelConfTypeDef sConfig = {0};

    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = ENABLE;
    hadc1.Init.ContinuousConvMode = ENABLE;
    hadc1.Init.NbrOfConversion = 4;
    hadc1.Init.DMAContinuousRequests = ENABLE;
    HAL_ADC_Init(&hadc1);

    sConfig.Channel = ADC_CHANNEL_0;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_84CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
    // 채널 1,2,3 도 동일하게 Rank 2,3,4로 설정

    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buf, 4);
}
```

---

## GPIO

```c
// 출력
GPIO_InitStruct.Pin = GPIO_PIN_13;
GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
GPIO_InitStruct.Pull = GPIO_NOPULL;
GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);

// 입력 (외부 인터럽트)
GPIO_InitStruct.Pin = GPIO_PIN_0;
GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
GPIO_InitStruct.Pull = GPIO_PULLDOWN;
HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
HAL_NVIC_EnableIRQ(EXTI0_IRQn);
```

---

## DMA General

DMA 스트림/채널 매핑은 레퍼런스 매뉴얼의 DMA request mapping 테이블 참조.

주요 규칙:
- DMA1: APB1 페리페럴 (USART2/3, SPI2/3, I2C1/2/3, TIM2-7)
- DMA2: APB2 페리페럴 (USART1/6, SPI1, ADC, SDIO, TIM1/8) + Memory-to-Memory
- CCM SRAM(0x1000_0000)은 DMA가 접근할 수 없음
- DMA 버퍼는 반드시 SRAM1/SRAM2에 배치
- 캐시가 없는 STM32F4에서는 DMA 일관성 문제 없음 (F7/H7과 다름)

---

## Watchdog (IWDG / WWDG)

### IWDG (Independent Watchdog) — 프로덕션 권장
LSI(32kHz) 기반, 독립 클럭이므로 메인 클럭 고장 시에도 동작:
```c
IWDG_HandleTypeDef hiwdg;

void MX_IWDG_Init(void)
{
    hiwdg.Instance = IWDG;
    hiwdg.Init.Prescaler = IWDG_PRESCALER_64;  // 32kHz/64 = 500Hz
    hiwdg.Init.Reload = 2000;                   // 2000/500Hz = 4초 타임아웃
    HAL_IWDG_Init(&hiwdg);
    // 시작 즉시 카운트 다운 시작 — 비활성화 불가!
}

// 메인 루프에서 반드시 주기적으로:
HAL_IWDG_Refresh(&hiwdg);
```

### WWDG (Window Watchdog) — 정밀 타이밍 필요 시
APB1 클럭 기반. 지정 윈도우 내에서만 리프레시 가능:
```c
WWDG_HandleTypeDef hwwdg;
hwwdg.Instance = WWDG;
hwwdg.Init.Prescaler = WWDG_PRESCALER_8;
hwwdg.Init.Window = 80;     // 리프레시 가능 상한
hwwdg.Init.Counter = 127;   // 시작 카운터 (63 이하가 되면 리셋)
hwwdg.Init.EWIMode = WWDG_EWI_ENABLE;  // Early Warning 인터럽트
HAL_WWDG_Init(&hwwdg);
```

---

## DAC Output

F407/F429/F446에서 사용 가능 (F401/F411에는 없음):
```c
DAC_HandleTypeDef hdac;
DAC_ChannelConfTypeDef sConfig = {0};

void MX_DAC_Init(void)
{
    __HAL_RCC_DAC_CLK_ENABLE();
    hdac.Instance = DAC;
    HAL_DAC_Init(&hdac);

    sConfig.DAC_Trigger = DAC_TRIGGER_NONE;       // 소프트웨어 트리거
    sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
    HAL_DAC_ConfigChannel(&hdac, &sConfig, DAC_CHANNEL_1);

    HAL_DAC_Start(&hdac, DAC_CHANNEL_1);
    HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_12B_R, 2048); // 중간값
}
// PA4 = DAC_OUT1, PA5 = DAC_OUT2 (⚠ SPI1_SCK와 충돌 가능!)
```
PA5를 DAC으로 사용하면 SPI1_SCK를 다른 핀(PB3)으로 이동해야 한다.

---

## CAN Bus

F407/F429/F446에서 사용 가능:
```c
CAN_HandleTypeDef hcan1;

void MX_CAN1_Init(void)
{
    __HAL_RCC_CAN1_CLK_ENABLE();
    hcan1.Instance = CAN1;
    hcan1.Init.Prescaler = 6;        // APB1=42MHz → 42/6=7MHz Time Quantum
    hcan1.Init.Mode = CAN_MODE_NORMAL;
    hcan1.Init.SyncJumpWidth = CAN_SJW_1TQ;
    hcan1.Init.TimeSeg1 = CAN_BS1_5TQ;   // 5 TQ
    hcan1.Init.TimeSeg2 = CAN_BS2_1TQ;   // 1 TQ
    // Baud = 7MHz / (1+5+1) = 1Mbps
    hcan1.Init.AutoBusOff = ENABLE;
    hcan1.Init.AutoRetransmission = ENABLE;
    HAL_CAN_Init(&hcan1);
}
// CAN1: PA11(RX)/PA12(TX) AF9 또는 PB8(RX)/PB9(TX) AF9 또는 PD0(RX)/PD1(TX) AF9
// ⚠ PA11/PA12는 USB와 공유 — CAN과 USB를 동시에 사용할 수 없음!
```

---

## SDIO (SD Card, 4-bit mode)

F407/F411/F429/F446에서 사용 가능:
```c
SD_HandleTypeDef hsd;

void MX_SDIO_Init(void)
{
    hsd.Instance = SDIO;
    hsd.Init.ClockEdge = SDIO_CLOCK_EDGE_RISING;
    hsd.Init.ClockBypass = SDIO_CLOCK_BYPASS_DISABLE;
    hsd.Init.ClockPowerSave = SDIO_CLOCK_POWER_SAVE_DISABLE;
    hsd.Init.BusWide = SDIO_BUS_WIDE_1B;  // 초기화는 1비트로
    hsd.Init.HardwareFlowControl = SDIO_HARDWARE_FLOW_CONTROL_DISABLE;
    hsd.Init.ClockDiv = 4;  // 48MHz / (4+2) = 8MHz
    HAL_SD_Init(&hsd);

    // 초기화 후 4비트 모드 전환
    HAL_SD_ConfigWideBusOperation(&hsd, SDIO_BUS_WIDE_4B);
}
// SDIO 핀 (AF12): PC8(D0), PC9(D1), PC10(D2), PC11(D3), PC12(CLK), PD2(CMD)
// DMA2 Stream3 Channel4 또는 Stream6 Channel4 사용
```

---

## Low Power Modes

### Sleep Mode (가장 얕음, 복귀 빠름)
CPU만 정지, 모든 페리페럴 동작:
```c
HAL_SuspendTick();       // SysTick이 깨우지 않도록
HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
HAL_ResumeTick();
// 아무 인터럽트로 복귀
```

### Stop Mode (중간, 복귀 수 us)
1.2V 레귤레이터 저전력 모드, SRAM/레지스터 유지, HSE/PLL 정지:
```c
HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
// 복귀 후 클럭이 HSI(16MHz)로 리셋됨 — SystemClock_Config() 재호출 필요!
SystemClock_Config();
// EXTI, RTC Alarm, USB 등으로 복귀
```

### Standby Mode (가장 깊음, 최소 전력)
SRAM 내용 소실, Wakeup 핀/RTC/IWDG로만 복귀, 리셋과 유사:
```c
HAL_PWR_EnterSTANDBYMode();
// PA0(WKUP)을 HIGH로 하면 복귀 → 리셋부터 재시작
```
