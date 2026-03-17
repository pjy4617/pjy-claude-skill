# STM32F4 Pin Assignment Validation Guide

이 문서는 Agent 5 (Code Reviewer)가 핀 할당을 검증할 때 사용하는 체크리스트이다.
단순 충돌 검사를 넘어, 데이터시트 대조까지 수행해야 한다.

## Pin Validation Checklist

Agent 5는 모든 핀 할당에 대해 다음 7단계 검증을 수행한다:

### Step 1: AF 매핑 정확성 (Alternate Function)
- 핀별 AF 번호가 데이터시트의 AF 매핑 테이블과 일치하는지 확인
- **반드시 타겟 MCU에 맞는 af-tables JSON 파일을 로드하여 검증할 것**:
  - `references/af-tables/stm32f401.json` (F401, DS9716)
  - `references/af-tables/stm32f407.json` (F407, DS8626)
  - `references/af-tables/stm32f411.json` (F411, DS10314)
  - `references/af-tables/stm32f429.json` (F429, DS8597)
  - `references/af-tables/stm32f446.json` (F446, DS10693)
- JSON의 `peripherals` 섹션에서 해당 페리페럴의 핀 옵션을 확인
- JSON의 `pin_conflicts` 섹션에서 충돌 가능성 자동 검출
- JSON의 `five_volt_tolerant` / `not_five_volt_tolerant`로 FT 핀 확인
- **MCU마다 AF 매핑이 다르므로 F407 기준으로 다른 MCU를 검증하면 안 됨**
- STM32F407 주요 AF 매핑 (참고용, 정확한 검증은 JSON 사용):
  | AF# | 기능 |
  |-----|------|
  | AF0 | SYS (JTAG/SWD, RTC) |
  | AF1 | TIM1, TIM2 |
  | AF2 | TIM3, TIM4, TIM5 |
  | AF3 | TIM8, TIM9, TIM10, TIM11 |
  | AF4 | I2C1, I2C2, I2C3 |
  | AF5 | SPI1, SPI2 |
  | AF6 | SPI3 |
  | AF7 | USART1, USART2, USART3 |
  | AF8 | UART4, UART5, USART6 |
  | AF9 | CAN1, CAN2, TIM12, TIM13, TIM14 |
  | AF10 | OTG_FS, OTG_HS |
  | AF11 | ETH |
  | AF12 | FSMC, SDIO, OTG_HS_FS |
  | AF13 | DCMI |
  | AF14 | (reserved) |
  | AF15 | EVENTOUT |

- **검증 방법**: 각 핀의 AF 할당을 데이터시트 Table 9 "Alternate function mapping"과 대조
- 모든 핀이 해당 AF에서 해당 기능을 지원하는지 확인
- 예: SPI1_SCK는 PA5(AF5) 또는 PB3(AF5)만 가능. PB5(AF5)에 할당하면 오류

### Step 2: 핀 충돌 검사
- 동일 핀에 2개 이상의 기능이 할당되지 않았는지 확인
- GPIO로 사용하는 핀이 다른 페리페럴의 AF와 겹치는 경우:
  - 해당 페리페럴이 비활성 상태인지 확인
  - HAL_conf.h에서 해당 모듈이 꺼져 있는지 확인
- **특히 주의할 겸용 핀**:
  | 핀 | 겸용 기능 | 주의사항 |
  |-----|----------|---------|
  | PA0 | WKUP | 저전력 모드에서 의도치 않은 Wake-Up |
  | PA4 | SPI1_NSS / DAC1_OUT | 소프트웨어 NSS 사용 시에도 HAL이 개입할 수 있음 |
  | PA5 | SPI1_SCK / DAC2_OUT | DAC 사용 시 SPI1_SCK를 PB3(AF5)로 이동 필요 |
  | **PA11/PA12** | **USB_DM/DP (AF10) / CAN1_RX/TX (AF9)** | **USB와 CAN1 동시 사용 불가! CAN1은 PB8/PB9 또는 PD0/PD1로 이동** |
  | PA13/14 | SWDIO/SWCLK | 디버거 연결 필수 핀, GPIO로 전환하면 디버깅 불가 |
  | PB2 | BOOT1 | GPIO로 사용 시 외부 풀다운 필요, 없으면 시스템 메모리 부팅 가능 |
  | PB3 | SWO (trace) | JTAG 트레이스 출력, GPIO로 쓸 때 JTAG 비활성화 필요 |
  | PC13~15 | RTC_AF1/TAMP/OUT | 전류 구동 제한, source/sink 2~3mA only |
  | PH0/PH1 | OSC_IN/OUT | HSE 크리스탈 연결 핀, GPIO 사용 불가 |

### Step 3: 전기적 특성 검증
- 출력 핀의 Speed 설정이 적절한지:
  | 주파수 | 권장 Speed |
  |--------|-----------|
  | < 2MHz | LOW |
  | 2~25MHz | MEDIUM |
  | 25~50MHz | HIGH |
  | 50~100MHz | VERY_HIGH |
  - 불필요하게 높은 Speed는 EMI 증가 → 최소 필요 Speed 사용
- Pull-up/Pull-down 설정:
  - SPI MISO: 일반적으로 NOPULL (외부 디바이스가 드라이브)
  - I2C SDA/SCL: Open-Drain + 외부 Pull-Up (HAL이 자동 설정)
  - 버튼 입력: PULLUP 또는 PULLDOWN (회로에 따라)
  - 미사용 핀: Analog 모드 또는 Output LOW (floating 방지)

### Step 4: 외부 디바이스 핀 요구사항 대조
- 외부 IC의 데이터시트에서 요구하는 모든 제어 핀이 할당되었는지 확인
- **흔히 누락되는 핀들**:
  | 디바이스 유형 | 빠지기 쉬운 핀 |
  |-------------|--------------|
  | SPI 디바이스 | CS (여러 CS가 필요한 경우), RESET, INT/DREQ |
  | VS1053B 코덱 | **XDCS** (SDI Data CS — XCS와 별도!), DREQ, XRESET |
  | OLED/LCD | DC (Data/Command), RESET, CS |
  | SD 카드 (SPI 모드) | CS, Card Detect |
  | 무선 모듈 (nRF24, ESP) | CE, IRQ, CS |
  | 모터 드라이버 | ENABLE, DIR, STEP, FAULT |

- **핵심 규칙**: 외부 디바이스 데이터시트의 "Pin Description" 또는 "Application Circuit" 섹션에 나오는
  모든 MCU 연결 핀을 하나하나 체크하여 누락된 것이 없는지 확인

### Step 5: DMA 스트림/채널 충돌
- 같은 DMA 스트림을 2개 이상의 페리페럴이 사용하지 않는지 확인
- STM32F4에서 각 DMA 스트림은 한 번에 하나의 채널만 활성화 가능
- DMA1/DMA2의 스트림-채널 매핑은 RM0090 Table 42~43 참조

### Step 6: EXTI 라인 충돌
- 같은 EXTI 라인에 2개 이상의 핀이 할당되지 않았는지 확인
- EXTI0 = PA0 또는 PB0 또는 PC0... (같은 핀 번호끼리 공유)
- 예: PA0(EXTI0)과 PB0을 둘 다 외부 인터럽트로 사용하면 충돌
- **같은 번호의 핀을 동시에 GPIO Input(폴링) + EXTI(인터럽트)로 사용하는 것은 가능**하지만, 나중에 EXTI로 변경할 위험이 있으므로 Requirements Summary에 명시할 것
- **구체적 예**: PA0를 버튼 EXTI로, PB0을 코덱 DREQ로 사용하는 경우 — 현재는 PB0이 GPIO 폴링이므로 충돌하지 않지만, 향후 PB0을 EXTI로 바꾸면 PA0과 EXTI0 라인을 공유하여 충돌한다. 이런 잠재적 충돌은 README에 기록한다.

### Step 7: 부트 핀 간섭
- BOOT0(핀 또는 옵션 바이트)이 0인지 확인 (Flash 부팅)
- BOOT1(PB2)을 GPIO로 사용하는 경우, 외부 풀다운 확인

## Validation Report Template

핀 검증 결과는 다음 형식으로 보고한다:

```
## Pin Validation Report

### Summary
- Total pins: N
- OK: N | WARN: N | ERROR: N

### Pin Table
| Pin  | Function    | AF/Mode | DS Confirmed | Status | Note |
|------|-------------|---------|--------------|--------|------|
| PA5  | SPI1_SCK    | AF5     | Table 9 ✓    | OK     | —    |
| PA4  | Codec XCS   | GPIO-Out| NSS겸용      | WARN   | 소프트웨어 NSS 확인 |
| ???  | Codec XDCS  | —       | 미할당!       | ERROR  | SDI CS 누락 |

### External Device Pin Checklist
- [x] VS1053B XCS (SCI chip select)
- [ ] VS1053B XDCS (SDI data chip select)  ← 누락!
- [x] VS1053B DREQ (data request)
- [x] VS1053B XRESET (hardware reset)

### Actions Required
1. [ERROR] XDCS 핀을 할당하라 (예: PB2)
2. [WARN] PA0 WKUP 간섭 가능성 문서화
```

## Common STM32F4 Pin Mistakes

1. **VS1053B XDCS 누락**: SCI(XCS)와 SDI(XDCS)는 반드시 별도 CS 핀 필요
2. **SPI NSS 핀을 GPIO CS로 사용**: 소프트웨어 NSS 모드에서 NSS 핀은 GPIO로 사용 가능하지만,
   HAL_SPI_Init에서 NSS=SPI_NSS_SOFT를 반드시 설정해야 함
3. **PC13~15 LED 구동**: 전류 제한이 있어 밝은 LED 구동 불가. 버퍼/MOSFET 필요할 수 있음
4. **BOOT0/BOOT1 미처리**: PB2(BOOT1)를 GPIO로 사용할 때 외부 풀다운 없으면
   전원 인가 시 시스템 메모리 부팅 가능
5. **I2C에서 GPIO_MODE_AF_OD 미설정**: I2C는 반드시 Open-Drain + 외부 풀업
6. **USB VBUS 핀 (PA9) 미연결**: Self-powered 디바이스는 PA9를 VBUS 감지에 사용해야 할 수 있음
7. **5V 톨러런트 핀 확인 안 함**: 5V 외부 디바이스 연결 시 FT(Five-volt Tolerant) 핀인지 확인 필요
   (데이터시트 I/O Level 컬럼에 "FT" 표시)
