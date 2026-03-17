---
name: stm32f4-firmware
description: "STM32F4 시리즈 마이크로컨트롤러 펌웨어 개발 스킬. STM32F4 기반 임베디드 시스템 설계, HAL/LL 드라이버 코드 생성, 주변장치(GPIO, SPI, I2C, UART, USB, DMA, TIM, ADC, DAC, SDIO, CAN, Watchdog 등) 구성, CMake/Makefile 빌드 시스템, 링커 스크립트, 인터럽트/DMA 설정, 클럭 트리 구성, 메모리 맵 설계를 포함한 전체 펌웨어 프로젝트를 생성한다. 'STM32', 'stm32f4', 'cortex-m4', 'arm firmware', 'HAL 드라이버', 'embedded C', '마이크로컨트롤러 펌웨어', 'MCU 개발' 등의 키워드가 포함된 요청에 반드시 이 스킬을 사용할 것. SPI 코덱, USB 디바이스, 모터 제어, 센서 인터페이스 등 STM32 기반 하드웨어 프로젝트 요청에도 트리거된다. STM32F1/F7/H7 등 다른 시리즈 요청에는 사용하지 않되, 참고용으로 안내할 수는 있다."
---

# STM32F4 Firmware Development Skill

## Overview

이 스킬은 STM32F4 시리즈 MCU(F401, F407, F411, F429, F446 등)를 위한 완전한 펌웨어 프로젝트를 생성한다. HAL 기반 코드를 기본으로 하되, 성능이 중요한 부분에서는 LL 드라이버나 레지스터 직접 접근을 병행한다.

## Agent Workflow (에이전트 워크플로우)

5단계 에이전트 파이프라인으로 진행한다. **Agent 5(Review)에서 에러가 발견되면 해당 에이전트로 되돌아가 수정한 뒤 재검토한다.**

```
[1.Requirements] → [2.Architecture] → [3.CodeGen] → [4.Build] → [5.Review]
     분석              설계              코드생성        빌드구성      검토
                         ▲                  ▲               ▲          │
                         └──── ERROR 시 ────┴───────────────┴──────────┘
```

### Review Feedback Rules (검토 피드백 규칙)
Agent 5 검토 결과에 따른 분기:
- **ERROR** (핀 누락, 클럭 계산 오류, AF 매핑 오류 등): 해당 에이전트로 돌아가 수정 후 Agent 5 재실행. 수정 사유를 코드 주석에 기록.
- **WARN** (겸용 핀 간섭 가능성, 전류 제한 등): README에 문서화하고 진행.
- **OK**: 최종 출력.

최대 3회 반복 후에도 ERROR가 남으면, 해결 불가 사유를 README에 명시하고 사용자에게 판단을 위임한다.

---

### Agent 1: Requirements Analyzer (요구사항 분석)

사용자 요청에서 다음을 추출한다:
- **타겟 MCU**: 정확한 파트넘버. MCU 선정이 불명확하면 `references/mcu-selection.md`를 참조하여 추천
- **주변장치 목록**: 사용할 페리페럴과 핀 매핑
- **클럭 요구사항**: HSE/HSI, PLL 설정, 시스템 클럭 목표
- **메모리 요구사항**: Flash/SRAM 사용 계획, 섹터 레이아웃
- **외부 디바이스**: 연결할 외부 IC와 통신 프로토콜
- **타이밍 제약**: 실시간 요구사항, 인터럽트 우선순위

#### Clarification Protocol (질문 프로토콜)
정보가 불충분할 때 Agent 1은 다음 우선순위로 사용자에게 질문한다. 사용자가 답하지 않으면 괄호 안의 기본값을 사용하되, 기본값을 사용했음을 Requirements Summary에 명시한다.

1. **MCU 파트넘버 미지정** — "어떤 STM32F4 칩을 사용하시나요?" (기본: 요구 페리페럴 수에 따라 `references/mcu-selection.md` 기준으로 선정)
2. **HSE 주파수 미지정** — "보드의 외부 크리스탈 주파수가 몇 MHz인가요?" (기본: 8MHz)
3. **외부 디바이스 모델 미지정** — "연결할 IC의 정확한 모델명이 무엇인가요?" (기본: 질문 필수, 기본값 없음 — 칩마다 프로토콜이 다르므로)
4. **핀 배치 제약** — "사용할 수 없는 핀이 있나요?" (기본: 제약 없음)
5. **전원 전압** — "보드 전압이 3.3V인가요?" (기본: 3.3V)
6. **빌드 시스템** — "CMake와 Makefile 중 어떤 빌드 시스템을 사용하시나요?" (기본: CMake)
7. **디버그 프로브** — "어떤 디버그 프로브를 사용하시나요? (ST-Link v2/v3, J-Link, CMSIS-DAP)" (기본: ST-Link v2)

추출 결과 형식:
```
## Requirements Summary
- MCU: STM32F407VGT6 (사용자 지정 / 자동 선정 — 사유: USB+SPI+1MB Flash 필요)
- Clock: HSE 8MHz → PLL → 168MHz SYSCLK (기본값 사용)
- Peripherals: USB_OTG_FS(Device), SPI1(Full-Duplex Master), ...
- Memory: Flash Sector 4-7 for data storage (256KB)
- External: VS1053B — 핀 요구: XCS, XDCS, DREQ, XRESET (데이터시트 대조 완료)
- Constraints: Audio playback latency < 10ms
- Defaults Used: HSE=8MHz (사용자 미지정)
```

### Agent 2: Architecture Designer (아키텍처 설계)

요구사항을 기반으로 소프트웨어 아키텍처를 설계한다:
- **실행 모델 결정**: Bare-metal 슈퍼루프 vs RTOS — 아래 판단 기준 참조
- **레이어 구조**: BSP → Driver → Middleware → Application
- **모듈 분할**: 각 기능별 .c/.h 파일 매핑
- **데이터 흐름**: 모듈 간 데이터 전달 경로 (파이프라인 다이어그램)
- **인터럽트 맵**: IRQ 핸들러 → 콜백 → 애플리케이션 매핑
- **상태 머신 또는 태스크 설계**
- **메모리 레이아웃**: Flash 섹터 할당, SRAM 영역 구분

#### Bare-metal vs RTOS 판단 기준
| 조건 | Bare-metal | RTOS |
|------|-----------|------|
| 동시 독립 작업 수 | ≤ 2 | ≥ 3 |
| 작업별 실시간 제약 차이 | 작음 | 크게 다름 (예: 1ms 모터 + 100ms UI) |
| 블로킹 I/O 필요 | 없음 | 있음 (예: TCP/IP 스택) |
| 우선순위 역전 위험 | 낮음 | 높음 (mutex 필요) |
| 코드 복잡도 관리 | 단순 | 모듈별 태스크 분리가 유리 |

RTOS 선택 시 FreeRTOS 기본, 태스크 분할과 우선순위는 `references/architecture-patterns.md`의 RTOS 섹션 참조.

참고 파일: `references/architecture-patterns.md`

### Agent 3: Code Generator (코드 생성)

아키텍처를 기반으로 실제 코드를 생성한다:
- **시스템 초기화**: SystemClock_Config, HAL_Init, GPIO_Init 등
- **주변장치 드라이버**: 각 페리페럴 초기화 및 운용 코드
- **미들웨어**: USB 스택, 파일 시스템, 오디오 코덱 드라이버 등
- **애플리케이션**: main.c와 애플리케이션 로직
- **인터럽트 핸들러**: stm32f4xx_it.c

코드 생성 규칙 — `references/coding-rules.md` 참조

### Agent 4: Build System Generator (빌드 시스템 구성)

프로젝트 빌드에 필요한 파일을 생성한다:

#### 빌드 시스템 선택
사용자에게 빌드 시스템을 확인한다. 미지정 시 CMake를 기본으로 한다.
- **CMake** (기본, ST 공식 권장): CMakeLists.txt + CMakePresets.json + gcc-arm-none-eabi.cmake 툴체인
- **Makefile** (대안): arm-none-eabi-gcc 기반 전통적 빌드

#### 생성 파일 목록
- **빌드 설정**: CMakeLists.txt + CMakePresets.json (또는 Makefile)
- **CMake 툴체인**: cmake/gcc-arm-none-eabi.cmake (CMake 선택 시)
- **링커 스크립트**: MCU별 메모리 레이아웃 (.ld)
- **시작 코드**: startup_stm32f4xx.s (벡터 테이블)
- **OpenOCD 설정**: 디버깅/플래싱 설정 — 프로브에 맞는 transport 선택
- **VS Code 설정**: launch.json (디버그), tasks.json (빌드/플래싱)

#### 디버그 프로브 선택
사용자 보드에 따라 프로브와 transport를 설정한다:
| 프로브 | interface | transport | 속도 |
|--------|-----------|-----------|------|
| ST-Link v2 (Nucleo/Discovery 구형) | stlink | hla_swd | 4000kHz |
| ST-Link v3 (최신 Nucleo, STLINK-V3SET) | stlink | dapdirect_swd | 8000kHz |
| J-Link | jlink | swd | 4000kHz |
| CMSIS-DAP | cmsis-dap | swd | 4000kHz |

#### VS Code 디버거 선택
launch.json에 두 가지 디버거 설정을 모두 포함한다:
- **cortex-debug** (marus25): OpenOCD 기반, 모든 프로브 지원, 커뮤니티 표준
- **stlinkgdbtarget** (ST 공식): STM32 VS Code Extension, ST-LINK/J-Link 전용

#### 최적화 플래그 (ST 공식 기준)
- **Debug**: `-O0 -g3` (최적화 없음, 디버거에서 변수 완전 추적)
- **Release**: `-Os -g0` (사이즈 최적화, 디버그 심볼 제거)

템플릿: `assets/templates/` 디렉토리 참조

### Agent 5: Code Reviewer (코드 검토)

생성된 전체 코드를 검토한다. 특히 **핀 검증은 7단계 체크리스트**를 반드시 수행한다.
검토 결과를 OK/WARN/ERROR로 분류하고, ERROR가 있으면 피드백 규칙에 따라 해당 에이전트로 되돌린다.

#### 5-A. 핀 할당 검증 (최우선)
핀 할당 오류는 하드웨어 손상을 초래하므로 가장 먼저 검증한다.
상세 체크리스트: `references/pin-validation.md` — 7단계를 모두 수행할 것.

1. **AF 매핑 정확성**: 데이터시트 Table 9 대조
2. **핀 충돌 검사**: 다중 AF/기능 + 겸용 핀 (WKUP, BOOT, SWD) 간섭
3. **전기적 특성**: GPIO Speed/Pull, 5V 톨러런트
4. **외부 디바이스 핀 완전성**: 외부 IC의 모든 MCU 연결 핀이 할당되었는지
5. **DMA 스트림/채널 충돌**
6. **EXTI 라인 충돌**: 같은 핀 번호의 EXTI 공유 (PA0과 PB0 동시 EXTI 불가)
7. **부트 핀 간섭**: BOOT0/BOOT1(PB2) 상태

#### 5-B. 클럭 설정 검증
- PLL: VCO입력(1~2MHz), VCO출력(100~432MHz), SYSCLK(≤MCU max)
- USB 48MHz, APB1 ≤ 42MHz, APB2 ≤ 84MHz
- MCU별 SYSCLK 상한: F401=84, F411=100, F407/F429=168, F446=180

#### 5-C. 인터럽트 우선순위
- NVIC 우선순위 그룹 일관성, 우선순위 역전 없는지
- SysTick은 HAL에서 우선순위 15(최저)로 설정됨 — DMA보다 낮아야 정상 동작

#### 5-D. 메모리
- 링커 스크립트 메모리 크기가 실제 MCU와 일치
- 스택/힙이 사용 패턴에 충분한지 (USB 사용 시 최소 스택 2KB 권장)
- DMA 버퍼가 CCM(0x1000_0000)에 없는지

#### 5-E. 하드웨어 타이밍
- SPI/I2C 클럭이 외부 디바이스 최대 허용 범위 이내
- UART 보레이트 오차율 (APB 클럭에 따른 실제 보레이트 계산)

#### 5-F. 에러 처리 및 안전성
- 모든 HAL 호출의 리턴값 검사
- 타임아웃 값의 적절성 (HAL_MAX_DELAY 사용 금지 in production)
- Watchdog 설정 여부 (프로덕션 빌드에서 IWDG 권장)
- Flash 쓰기 중 같은 뱅크 코드 실행 문제 (버스 스톨) 확인

#### 5-G. 단위 테스트 확인 (test/ 디렉토리 존재 시)
- `test/` 디렉토리가 존재하면 호스트 테스트를 실행한다: `cd test && make`
- 테스트 결과가 PASS인지 확인. FAIL이 있으면 ERROR로 분류하고 Agent 3으로 되돌린다.
- 테스트가 없으면 WARN: "단위 테스트 미작성 — `/stm32f4-tdd`로 추가 권장"
- 테스트 커버리지(테스트된 함수 수 / 테스트 가능한 함수 수) 보고

---

## Project Structure

```
project-name/
├── Core/
│   ├── Inc/                    # main.h, hal_conf.h, it.h
│   └── Src/                    # main.c, hal_msp.c, it.c, system.c
├── Drivers/
│   ├── BSP/Inc/ BSP/Src/       # 보드 지원 패키지
│   └── Device/Inc/ Device/Src/ # 외부 디바이스 드라이버
├── Middlewares/Inc/ Src/        # USB, FatFS 등
├── Startup/                    # startup_stm32f4xxxx.s
├── Linker/                     # .ld 링커 스크립트
├── cmake/                      # CMake 사용 시
│   └── gcc-arm-none-eabi.cmake # 툴체인 파일
├── .vscode/
│   ├── launch.json             # 디버그 설정 (cortex-debug + ST 확장)
│   └── tasks.json              # 빌드/플래싱 태스크
├── CMakeLists.txt              # CMake 빌드 (기본)
├── CMakePresets.json           # 빌드 프리셋 (Debug/Release)
├── Makefile                    # Makefile 빌드 (대안)
├── openocd.cfg
└── README.md
```

## Clock Configuration Patterns

MCU별 클럭 설정 — `references/mcu-selection.md`에 F401/F407/F411/F446 전체 패턴 수록.

대표 예시 (STM32F407, HSE 8MHz):
```c
// HSE 8MHz → PLL → SYSCLK 168MHz, USB 48MHz
.PLLM = 8, .PLLN = 336, .PLLP = 2, .PLLQ = 7
// APB1 = 42MHz (/4), APB2 = 84MHz (/2), Flash Latency = 5WS
```

## Peripheral Init Order

반드시 이 순서를 준수:
1. 클럭 활성화 → 2. GPIO AF 설정 → 3. 페리페럴 Init → 4. DMA → 5. NVIC → 6. Start

## Memory Layout (STM32F407 기준)

Flash: Sector 0-3(16KB×4) + Sector 4(64KB) + Sector 5-11(128KB×7) = 1MB
SRAM: SRAM1(112KB) + SRAM2(16KB) = 128KB, CCM(64KB, DMA 불가)

다른 MCU 메모리는 `references/mcu-selection.md` 참조.

## Error Handling

```c
static void Error_Handler(void) {
    __disable_irq();
    while (1) { /* Watchdog이 리셋하거나 디버거에서 확인 */ }
}
```

프로덕션 준비 사항은 `references/production-checklist.md` 참조.
디버깅 기법은 `references/debugging-guide.md` 참조.

## Reference Files

| 파일 | 내용 | 주 사용 에이전트 |
|------|------|-----------------|
| `references/peripheral-patterns.md` | SPI, I2C, UART, USB, DMA, TIM, ADC, Flash, **Watchdog, DAC, CAN, SDIO, 저전력** | Agent 3 |
| `references/coding-rules.md` | 네이밍, HAL 가이드, **크리티컬 섹션, 원자적 접근** | Agent 3 |
| `references/architecture-patterns.md` | 레이어, 상태 머신, 더블 버퍼, **RTOS 패턴, 멀티 SPI 공유** | Agent 2 |
| `references/pin-validation.md` | 7단계 핀 검증 체크리스트, 겸용 핀 | Agent 5 |
| `references/af-tables/*.json` | **MCU별 AF 매핑 데이터** (F401/F407/F411/F429/F446 각각) | Agent 5, kicad-stm32-checker |
| `references/mcu-selection.md` | **F401/F407/F411/F429/F446 비교**, 클럭 패턴, 메모리, 페리페럴 차이 | Agent 1 |
| `references/production-checklist.md` | **Watchdog, BOR, RDP, Option Bytes, 양산 체크리스트** | Agent 5 |
| `references/debugging-guide.md` | **HardFault 분석, SWO/ITM, printf 리다이렉션, GDB 팁** | 개발 시 참고 |

## KiCad 회로도 연동 (선택)

KiCad 회로도가 있으면 펌웨어 생성 **전에** 회로도 검증을 권장한다.

### 권장 워크플로우
```
KiCad 회로도 완성
  → /kicad-stm32-review (회로도 검증 — 42항목 체크리스트)
  → kicad-stm32-checker 에이전트가 검증 수행
  → ERROR=0 확인
  → "이 회로도 기반으로 펌웨어 만들어줘"
  → stm32f4-firmware 스킬 (Agent 1이 회로도에서 핀 매핑을 가져옴)
```

### 회로도 검증이 펌웨어 품질을 높이는 이유
- **Agent 1**: 회로도에서 핀 할당을 직접 가져오므로 요구사항 추출이 정확
- **Agent 3**: 검증된 핀 할당으로 코드를 생성하므로 회로도-코드 불일치 원천 차단
- **Agent 5**: 회로도 검증 결과를 참조하여 교차 검증 가능

### 관련 스킬/에이전트
| 이름 | 역할 | 트리거 |
|------|------|--------|
| `kicad-stm32-review` (스킬) | STM32F4 특화 회로도 검증 체크리스트 (42항목) | "KiCad STM32 검토", "회로도 핀 확인" |
| `kicad-stm32-checker` (에이전트) | 체크리스트를 실행하는 전문가 (별도 컨텍스트) | 자동 위임 |
| `stm32f4-tdd` (스킬) | 호스트 기반 단위 테스트 체계 (Unity + FFF) | "테스트 추가", "TDD" |
| `stm32f4-test-writer` (에이전트) | 테스트 코드 생성 전문가 (별도 컨텍스트) | 자동 위임 |
