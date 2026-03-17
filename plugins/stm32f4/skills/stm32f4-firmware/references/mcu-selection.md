# STM32F4 MCU Selection Guide

Agent 1이 사용자의 요구사항에 맞는 MCU를 선정할 때 참조한다.

## MCU Comparison Table

| 항목 | F401 | F411 | F407 | F429 | F446 |
|------|------|------|------|------|------|
| Max SYSCLK | 84MHz | 100MHz | 168MHz | 168MHz | 180MHz |
| Flash | 256KB | 512KB | 1MB | 2MB | 512KB |
| SRAM | 64KB | 128KB | 192KB(+64CCM) | 256KB(+64CCM) | 128KB |
| USB OTG FS | ✓ | ✓ | ✓ | ✓ | ✓ |
| USB OTG HS | — | — | ✓ | ✓ | ✓ |
| Ethernet | — | — | ✓ | ✓ | — |
| SDIO | — | ✓ | ✓ | ✓ | ✓ |
| CAN | — | — | 2× | 2× | 2× |
| DAC | — | — | 2ch | 2ch | 2ch |
| Camera (DCMI) | — | — | ✓ | ✓ | ✓ |
| LCD (LTDC) | — | — | — | ✓ | — |
| FMC/FSMC | — | — | FSMC | FMC | FMC |
| FPU | ✓ | ✓ | ✓ | ✓ | ✓ |
| 대표 패키지 | UFQFPN48 | UFQFPN48 | LQFP100/144 | LQFP144/176 | LQFP64/100 |
| 가격대 | 최저 | 저가 | 중가 | 고가 | 중가 |

## MCU Selection Flowchart

```
USB 필요?
├─ NO → F401 (최소 비용, 84MHz, 256KB Flash)
└─ YES
   ├─ Flash > 512KB 필요? → F407 (1MB) 또는 F429 (2MB)
   ├─ Ethernet 필요? → F407 또는 F429
   ├─ LCD 직결 (LTDC)? → F429
   ├─ CAN 필요? → F407, F429, F446
   ├─ 180MHz 필요? → F446
   └─ 저가+USB → F411 (100MHz, 512KB)
```

## Clock Configuration Per MCU

### STM32F401 (84MHz, HSE 25MHz 보편적)
```c
.PLLM = 25, .PLLN = 336, .PLLP = 4, .PLLQ = 7
// SYSCLK = 84MHz, USB = 48MHz
// APB1 = 42MHz (/2), APB2 = 84MHz (/1)
// Flash Latency = 2WS
```

### STM32F411 (100MHz, HSE 25MHz)
```c
.PLLM = 25, .PLLN = 200, .PLLP = 2, .PLLQ = — (USB 별도 계산 필요)
// SYSCLK = 100MHz
// APB1 = 50MHz (/2), APB2 = 100MHz (/1)
// Flash Latency = 3WS
// ⚠ USB 48MHz: PLLN=192, PLLP=4 → SYSCLK=48MHz 또는 96MHz 타협 필요
```

USB와 SYSCLK을 동시 최적화하기 어려운 칩이다. USB 사용 시:
```c
// USB 우선: PLLM=25, PLLN=192, PLLP=2, PLLQ=4 → SYSCLK=96MHz, USB=48MHz
// 속도 우선: PLLM=25, PLLN=200, PLLP=2 → SYSCLK=100MHz, USB=50MHz(오차!)
```

### STM32F407 (168MHz, HSE 8MHz)
```c
.PLLM = 8, .PLLN = 336, .PLLP = 2, .PLLQ = 7
// SYSCLK = 168MHz, USB = 48MHz
// APB1 = 42MHz (/4), APB2 = 84MHz (/2)
// Flash Latency = 5WS
```

### STM32F429 (168MHz, HSE 8MHz — F407과 동일 PLL)
```c
.PLLM = 8, .PLLN = 336, .PLLP = 2, .PLLQ = 7
// F407과 동일. LTDC 클럭은 PLLSAI로 별도 설정.
```

### STM32F446 (180MHz, HSE 8MHz)
```c
.PLLM = 4, .PLLN = 180, .PLLP = 2, .PLLQ = — 
// SYSCLK = 180MHz (Over-Drive 모드 필요)
// APB1 = 45MHz (/4), APB2 = 90MHz (/2)
// Flash Latency = 5WS
// ⚠ Over-Drive: HAL_PWREx_EnableOverDrive() 호출 필수
// ⚠ USB: PLLM=4, PLLN=168, PLLP=2, PLLQ=7 → SYSCLK=168MHz, USB=48MHz (180MHz 포기)
// 또는 PLLSAI를 USB 48MHz 소스로 사용 (F446 고유 기능)
```

## Memory Layout Per MCU

### F401 (256KB Flash)
Sector 0-3: 16KB×4, Sector 4: 64KB, Sector 5: 128KB — 총 256KB
데이터 저장에 사용할 여유 Flash가 매우 적음. 외부 Flash/EEPROM 권장.

### F411 (512KB Flash)
Sector 0-3: 16KB×4, Sector 4: 64KB, Sector 5-7: 128KB×3 — 총 512KB

### F407 (1MB Flash)
Sector 0-3: 16KB×4, Sector 4: 64KB, Sector 5-11: 128KB×7 — 총 1MB

### F429 (2MB Flash, Dual Bank)
Bank 1: Sector 0-11 (1MB), Bank 2: Sector 12-23 (1MB)
Dual Bank 모드에서 한쪽 뱅크에 쓰기하면서 다른 뱅크에서 코드 실행 가능.

### F446 (512KB Flash)
F411과 동일한 섹터 구조.

## APB Bus Clock Limits

| MCU | APB1 max | APB2 max | SPI1 클럭(APB2) | SPI2/3 클럭(APB1) |
|-----|----------|----------|----------------|-------------------|
| F401 | 42MHz | 84MHz | 84MHz | 42MHz |
| F411 | 50MHz | 100MHz | 100MHz | 50MHz |
| F407 | 42MHz | 84MHz | 84MHz | 42MHz |
| F429 | 42MHz | 84MHz | 84MHz | 42MHz |
| F446 | 45MHz | 90MHz | 90MHz | 45MHz |

SPI 프리스케일러 계산 시 반드시 해당 MCU의 APB 클럭을 기준으로 해야 한다.
