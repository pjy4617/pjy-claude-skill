---
name: kicad-stm32-review
description: "KiCad 회로도에서 STM32F4 칩의 핀 할당, 페리페럴 설정, 전원 설계를 검증합니다. 'KiCad STM32 검토', 'KiCad 핀 확인', '회로도 핀 검증', 'STM32 회로 리뷰', '회로도에서 핀 맞는지', 'KiCad AF 확인', '회로도 페리페럴 검토' 등의 요청에 자동 적용. 펌웨어 생성 전에 회로도 단계에서 하드웨어 오류를 사전에 잡아내는 용도."
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# KiCad × STM32F4 회로도 검증 체크리스트

> 이 스킬은 체크리스트를 정의합니다.
> 실제 검증 작업은 **kicad-stm32-checker 에이전트**에게 위임됩니다.
> 에이전트는 별도 컨텍스트에서 KiCad 파일을 파싱하고 이 체크리스트를 적용합니다.

## 목적

KiCad 회로도에서 STM32F4 MCU의 핀 할당과 페리페럴 설정이 **데이터시트와 일치하는지** 검증한다.
펌웨어 코드를 생성하기 **전에** 하드웨어 설계 오류를 잡아낸다.

## 검증 결과 형식

모든 항목을 **OK / WARN / ERROR** 로 분류한다:
- **ERROR**: 하드웨어 손상 또는 동작 불가. 반드시 수정.
- **WARN**: 동작은 하지만 잠재적 문제. README에 문서화.
- **OK**: 이상 없음.

---

## 체크리스트 (8개 카테고리, 42항목)

### A. MCU 식별 및 기본 확인 (4항목)

| ID | 항목 | ERROR 조건 |
|----|------|-----------|
| A1 | MCU 파트넘버가 회로도 심볼에 명시되어 있는가 | 파트넘버 불명 |
| A2 | 패키지(LQFP64/100/144 등)가 풋프린트와 일치하는가 | 불일치 |
| A3 | 데이터시트 핀아웃과 심볼의 핀 번호가 일치하는가 | 핀 번호 오류 |
| A4 | 모든 VDD/VSS 핀이 연결되어 있는가 (NC 핀 없이) | 전원 핀 미연결 |

### B. 전원 설계 (6항목)

| ID | 항목 | ERROR 조건 |
|----|------|-----------|
| B1 | 각 VDD 핀에 100nF 디커플링 캡이 있는가 | 디커플링 캡 누락 |
| B2 | VCAP1/VCAP2 핀에 2.2μF 캡이 연결되었는가 (해당 패키지만) | VCAP 미처리 |
| B3 | VDDA에 1μF + 100nF 필터가 있는가 | VDDA 필터 누락 |
| B4 | VBAT 핀이 VDD 또는 배터리에 연결되었는가 | VBAT 플로팅 |
| B5 | 전원 전압이 MCU 허용 범위(1.7~3.6V)인가 | 전압 초과 |
| B6 | PWR_FLAG가 전원 네트에 있는가 (KiCad ERC 통과용) | WARN만 |

### C. 클럭 회로 (4항목)

| ID | 항목 | ERROR 조건 |
|----|------|-----------|
| C1 | HSE 크리스탈이 OSC_IN(PH0)/OSC_OUT(PH1)에 연결되었는가 | 핀 오류 |
| C2 | HSE 로드 캡 값이 크리스탈 데이터시트와 일치하는가 | WARN: 불일치 |
| C3 | HSE 배선이 MCU에 가까운가 (PCB 존재 시) | WARN만 |
| C4 | LSE 사용 시 PC14/PC15에 32.768kHz 연결되었는가 | 핀 오류 |

### D. 리셋 및 부트 (4항목)

| ID | 항목 | ERROR 조건 |
|----|------|-----------|
| D1 | NRST 핀에 100nF 캡 + 10kΩ 풀업이 있는가 | 리셋 회로 누락 |
| D2 | BOOT0이 GND로 풀다운되어 있는가 (Flash 부팅) | BOOT0 플로팅 |
| D3 | PB2(BOOT1)를 GPIO로 사용 시 외부 풀다운이 있는가 | WARN: 부트 간섭 가능 |
| D4 | 외부 리셋 버튼이 있다면 디바운스 회로가 있는가 | WARN만 |

### E. 디버그 인터페이스 (3항목)

| ID | 항목 | ERROR 조건 |
|----|------|-----------|
| E1 | SWD 핀(PA13=SWDIO, PA14=SWCLK)이 디버그 커넥터에 연결되었는가 | 디버그 불가 |
| E2 | SWO(PB3) 사용 시 디버그 커넥터에 연결되었는가 | WARN: ITM 불가 |
| E3 | PA13/PA14를 GPIO로 전용하면 디버거 연결 불가 경고 | ERROR: 디버깅 불가 |

### F. 핀-AF 매핑 검증 (9항목) — 가장 중요

| ID | 항목 | ERROR 조건 |
|----|------|-----------|
| F1 | 각 페리페럴 핀의 AF 번호가 데이터시트 Table 9과 일치하는가 | AF 오류 → 동작 안 함 |
| F2 | 동일 핀에 2개 이상의 AF가 할당되지 않았는가 | 핀 충돌 |
| F3 | SPI: SCK, MOSI, MISO, CS 핀이 모두 할당되었는가 | 핀 누락 |
| F4 | I2C: SDA, SCL에 외부 풀업 저항(4.7kΩ)이 있는가 | 풀업 누락 → 통신 불가 |
| F5 | UART: TX↔RX 크로스 연결이 올바른가 | 크로스 오류 |
| F6 | USB: DP(PA12)/DM(PA11)에 1.5kΩ 풀업이 있는가 (Full-Speed) | WARN: 호스트가 인식 못할 수 있음 |
| F7 | CAN: TX/RX가 CAN 트랜시버에 연결되었는가 (직결 금지) | 트랜시버 누락 |
| F8 | ADC 입력 핀이 실제 아날로그 가능 핀인가 (PA0~PA7, PB0~PB1, PC0~PC5 등) | 비ADC 핀 사용 |
| F9 | DAC 출력(PA4/PA5)이 다른 AF와 충돌하지 않는가 | 핀 충돌 |

### G. 외부 디바이스 연결 (6항목)

| ID | 항목 | ERROR 조건 |
|----|------|-----------|
| G1 | 외부 IC의 데이터시트 Application Circuit와 대조했는가 | 미대조 |
| G2 | 외부 IC의 모든 제어 핀(CS, RESET, INT, DREQ 등)이 MCU에 연결되었는가 | 핀 누락 |
| G3 | 5V 디바이스를 연결한 핀이 5V 톨러런트(FT)인가 | 비FT 핀 → MCU 손상 |
| G4 | 레벨 시프터가 필요한 경우 배치되었는가 (1.8V↔3.3V, 3.3V↔5V) | 전압 불일치 |
| G5 | SPI 디바이스별 CS가 개별 GPIO로 할당되었는가 (공유 금지) | CS 공유 |
| G6 | 외부 IC 전원 핀에 디커플링 캡이 있는가 | WARN: 노이즈 |

### H. DMA/EXTI/특수 핀 (6항목)

| ID | 항목 | ERROR 조건 |
|----|------|-----------|
| H1 | DMA를 사용할 페리페럴의 DMA 스트림/채널이 충돌하지 않는가 | DMA 충돌 |
| H2 | EXTI 인터럽트 핀이 같은 번호(PA0과 PB0 등)로 충돌하지 않는가 | EXTI 충돌 |
| H3 | PC13~PC15를 LED/출력으로 사용 시 전류 제한(2~3mA) 인지 | WARN: 구동 부족 |
| H4 | PA0(WKUP)을 사용 시 저전력 모드에서 의도치 않은 Wake-Up 가능성 | WARN |
| H5 | 미사용 GPIO가 아날로그 모드 또는 출력 LOW로 처리 가능한가 | WARN: 플로팅 |
| H6 | PA4(DAC1/SPI1_NSS)처럼 겸용 핀의 간섭 가능성을 확인했는가 | WARN |

---

## 검증 보고서 템플릿

```
═══════════════════════════════════════
  KiCad × STM32F4 회로도 검증 리포트
═══════════════════════════════════════

MCU: STM32F407VGT6 (LQFP100)
회로도: project.kicad_sch
검증일: YYYY-MM-DD

카테고리별 결과:
  A. MCU 식별:       OK 4 / WARN 0 / ERROR 0  ✅
  B. 전원 설계:       OK 5 / WARN 1 / ERROR 0  ✅
  C. 클럭 회로:       OK 3 / WARN 1 / ERROR 0  ✅
  D. 리셋/부트:       OK 3 / WARN 1 / ERROR 0  ✅
  E. 디버그:          OK 2 / WARN 1 / ERROR 0  ✅
  F. 핀-AF 매핑:     OK 7 / WARN 0 / ERROR 2  ❌
  G. 외부 디바이스:   OK 5 / WARN 0 / ERROR 1  ❌
  H. DMA/EXTI/특수:  OK 5 / WARN 1 / ERROR 0  ✅

종합: OK 34 / WARN 5 / ERROR 3

[ERROR 항목]
  🔴 F1 — PA5에 SPI1_SCK(AF5) 할당했으나,
          데이터시트에서 PA5의 AF5는 SPI1_SCK ✓ (OK)
          PB5에 SPI1_MOSI(AF5) 할당했으나,
          데이터시트에서 PB5의 AF5는 SPI3_MOSI ✗ → SPI1_MOSI는 PA7(AF5)
  🔴 F4 — I2C1 SDA(PB7)/SCL(PB6)에 외부 풀업 저항 없음
  🔴 G2 — VS1053B XDCS 핀이 MCU에 미연결 (XCS만 연결됨)

[WARN 항목]
  ⚠️ B6 — +3V3 네트에 PWR_FLAG 없음 (ERC 경고 발생)
  ⚠️ C2 — HSE 8MHz 로드 캡 20pF, 크리스탈 권장 18pF (2pF 차이)
  ⚠️ D3 — PB2(BOOT1)를 GPIO 출력으로 사용, 외부 풀다운 없음
  ⚠️ E2 — SWO(PB3) 미연결, ITM printf 사용 불가
  ⚠️ H4 — PA0를 버튼 EXTI로 사용, WKUP 간섭 가능

[핀 할당 테이블]
  Pin  | Net Name     | AF  | Function     | DS Check | Status
  PA5  | SPI1_SCK     | AF5 | SPI1_SCK     | Table 9 ✓ | OK
  PA7  | SPI1_MOSI    | AF5 | SPI1_MOSI    | Table 9 ✓ | OK
  PB5  | SPI1_MOSI_ERR| AF5 | SPI3_MOSI!   | Table 9 ✗ | ERROR
  PB6  | I2C1_SCL     | AF4 | I2C1_SCL     | Table 9 ✓ | OK (풀업 누락)
  ...

[외부 디바이스 핀 체크리스트]
  VS1053B:
    [✓] XCS      — PB0 (GPIO Output)
    [✗] XDCS     — 미할당!
    [✓] DREQ     — PA0 (GPIO Input / EXTI)
    [✓] XRESET   — PC4 (GPIO Output)

[권장 조치]
  1. [ERROR] PB5 → PA7로 변경하거나, SPI3 사용으로 전환
  2. [ERROR] PB6/PB7에 4.7kΩ 풀업 저항 추가
  3. [ERROR] VS1053B XDCS 핀을 MCU GPIO에 할당 (예: PB1)
```

---

## 펌웨어 스킬(stm32f4-firmware)과의 연동

이 검증을 먼저 통과한 후 펌웨어 생성을 진행하면:
1. **Agent 1(Requirements)** 이 회로도에서 핀 매핑을 직접 가져올 수 있음
2. **Agent 3(CodeGen)** 이 검증된 핀 할당으로 코드를 생성하므로 불일치 원천 차단
3. **Agent 5(Review)** 가 회로도 검증 결과를 참조하여 교차 검증

권장 워크플로우:
```
KiCad 회로도 완성
  → /kicad-stm32-review  (이 스킬)
  → ERROR=0 확인
  → "이 회로도 기반으로 펌웨어 만들어줘"
  → stm32f4-firmware 스킬이 회로도의 핀 할당을 그대로 사용
```

$ARGUMENTS
