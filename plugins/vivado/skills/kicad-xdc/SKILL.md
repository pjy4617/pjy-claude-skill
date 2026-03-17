---
name: kicad-xdc
description: KiCad 회로도에서 Vivado XDC 제약 파일을 자동 생성합니다. "KiCad에서 XDC 만들어", "회로도에서 핀 배치 생성", "kicad xdc", "넷리스트에서 constraints", "스키매틱에서 XDC" 등의 요청에 자동 적용.
---

# KiCad → Vivado XDC 자동 생성

> 이 스킬은 XDC 생성 절차와 매핑 규칙을 정의합니다.
> 실제 작업은 kicad-xdc-gen 에이전트에게 위임됩니다.
> 생성된 XDC는 pin-reviewer 에이전트가 검증합니다.

## 파이프라인

```
KiCad 회로도 (.kicad_sch)
    │  kicad-cli → netlist.xml
    ▼
FPGA 핀 ↔ 네트 매핑 추출
    │  핀 번호 = PACKAGE_PIN
    │  네트 이름 = 포트 이름
    ▼
뱅크/IOSTANDARD 자동 결정
    │  boards.json → bank_vcco 참조
    │  핀 → 뱅크 → VCCO → IOSTANDARD
    ▼
타이밍 제약 자동 생성
    │  클럭 네트 → create_clock
    │  리셋/버튼 → set_false_path
    ▼
constraints/보드명.xdc 출력
    ▼
pin-reviewer 검증 (기존 에이전트)
```

## 전제 조건

- `kicad-cli` 가 설치되어 있어야 함 (KiCad 8.0+ 필수, 9.0 권장)
- Python 3.6+ (gen_xdc_from_netlist.py 실행용)
- KiCad 회로도에 FPGA 심볼이 있어야 함
- FPGA 심볼의 핀 번호가 패키지 핀 번호와 일치해야 함 (KiCad 공식 라이브러리 사용 시 자동)
- boards.json에 타겟 보드의 bank_vcco 정보가 있어야 함

## Step 1: 넷리스트 추출

```bash
kicad-cli sch export netlist \
  --output build/netlist.xml \
  --format kicadxml \
  프로젝트.kicad_sch
```

## Step 2: FPGA 심볼 식별 및 핀 추출

netlist.xml에서 FPGA 컴포넌트를 찾는 방법:

### 자동 식별 기준 (우선순위 순)
1. **value 필드**: `xc7z020`, `xc7a35t`, `xc7a100t` 등 Xilinx 파트 넘버 포함
2. **footprint 필드**: `Xilinx` 또는 패키지명 (`CLG484`, `CSG324` 등) 포함
3. **핀 수**: 100개 이상 핀을 가진 컴포넌트
4. **사용자 지정**: `$ARGUMENTS`로 레퍼런스 지정 (예: `U1`)

### XML에서 추출하는 정보
```xml
<comp ref="U1">
  <value>xc7z020clg484</value>
  <pin num="Y9"   name="IO_L12P_T1_MRCC_33"  net="CLK_100MHZ"/>
  <pin num="AB12" name="IO_L4P_T0_33"         net="OLED_SDIN"/>
  <pin num="T18"  name="IO_L7N_T1_33"         net="CPU_RESET_N"/>
  ...
</comp>
```

각 핀에서:
- `num` (Y9) → PACKAGE_PIN
- `net` (CLK_100MHZ) → XDC 포트 이름 + Verilog 포트 이름
- `name` (IO_L12P_T1_MRCC_33) → 뱅크 번호 추출 (끝 숫자 `_33`)

## Step 3: 뱅크/IOSTANDARD 결정

### 핀 이름에서 뱅크 추출
Xilinx 핀 이름의 마지막 숫자가 뱅크 번호:
```
IO_L12P_T1_MRCC_33  → Bank 33
IO_L4P_T0_34        → Bank 34
IO_0_35             → Bank 35
```

### 뱅크 → IOSTANDARD 매핑
boards.json의 `bank_vcco` 참조:
```json
"33": { "voltage": 3.3, "iostandard": "LVCMOS33" }
"34": { "voltage": 1.8, "iostandard": "LVCMOS18" }
```

### 매핑 불가 시 (뱅크 불명)
- XDC에 `## TODO: IOSTANDARD 확인 필요` 주석 추가
- pin-reviewer가 WARN으로 보고

## Step 4: 네트 이름 패턴 인식

### 자동 인식 패턴 (`net_patterns.json` 참조)

| 패턴 | 인식 결과 | XDC 동작 |
|------|----------|---------|
| `*CLK*`, `*CLOCK*` | 클럭 신호 | `create_clock` 생성 |
| `*RST*`, `*RESET*` | 리셋 신호 | `set_false_path` 생성 |
| `*BTN*`, `*BUTTON*`, `*SW*` | 사용자 입력 | `set_false_path` 생성 |
| `*LED*` | LED 출력 | `set_false_path` (선택) |
| `*_P`, `*_N` | 차동 페어 | 페어로 묶어 처리 |
| `*SPI*`, `*SCLK*`, `*MOSI*`, `*MISO*`, `*CS*` | SPI | 그룹 주석 추가 |
| `*UART*`, `*TX*`, `*RX*` | UART | 그룹 주석 추가 |
| `*I2C*`, `*SDA*`, `*SCL*` | I2C | 그룹 주석 추가 |
| `GND`, `VCC*`, `PWR*` | 전원/그라운드 | XDC에서 제외 (FPGA 내부) |
| `NC`, `DNC`, `NO_CONNECT` | 미연결 | XDC에서 제외 |

## Step 5: XDC 파일 생성

### 출력 형식

```xdc
## ============================================================
## Auto-generated XDC from KiCad schematic
## Board: ZedBoard (xc7z020clg484-1)
## Source: project.kicad_sch
## FPGA: U1 (xc7z020clg484)
## Generated: 2025-03-16
## ============================================================
## ⚠️ 자동 생성 파일입니다. pin-reviewer로 검증해주세요.
## ============================================================

## ---- Clock ----
set_property -dict { PACKAGE_PIN Y9  IOSTANDARD LVCMOS33 } [get_ports clk_100mhz]
create_clock -period 10.000 -name sys_clk [get_ports clk_100mhz]

## ---- Reset ----
set_property -dict { PACKAGE_PIN T18 IOSTANDARD LVCMOS33 } [get_ports cpu_reset_n]
set_false_path -from [get_ports cpu_reset_n]

## ---- Buttons ----
set_property -dict { PACKAGE_PIN R18 IOSTANDARD LVCMOS33 } [get_ports btnr]
set_property -dict { PACKAGE_PIN T22 IOSTANDARD LVCMOS33 } [get_ports btnu]
set_false_path -from [get_ports btn*]

## ---- OLED (SPI) ----
set_property -dict { PACKAGE_PIN AB12 IOSTANDARD LVCMOS33 } [get_ports oled_sdin]
set_property -dict { PACKAGE_PIN AA12 IOSTANDARD LVCMOS33 } [get_ports oled_sclk]
```

### 네트 이름 → 포트 이름 변환 규칙
1. 대문자 → 소문자 변환
2. 하이픈(-) → 언더스코어(_)
3. 공백 → 언더스코어
4. 선행 숫자 → `pin_` 접두사 추가
5. Verilog 예약어 충돌 시 → `_io` 접미사 추가

예: `CLK_100MHZ` → `clk_100mhz`, `OLED-SDIN` → `oled_sdin`

## Step 6: 검증 연계

XDC 생성 후 자동으로 다음을 수행:
1. `"pin-reviewer에게 검증 요청"` — 기존 pin-review 체크리스트 적용
2. top.v 포트와 XDC 포트 이름이 일치하는지 확인
3. 불일치 시 top.v 포트 이름을 XDC에 맞추거나, XDC를 수정

## 한계 및 주의사항

| 한계 | 원인 | 대응 |
|------|------|------|
| 뱅크 경계 핀 (예: ZedBoard U핀) | 핀 이름에서 뱅크 추출이 모호 | 패키지 핀아웃 파일로 이중 확인 |
| 커스텀 KiCad 심볼 | 핀 번호가 패키지 핀과 다를 수 있음 | 공식 라이브러리 사용 권장 |
| 멀티 FPGA 디자인 | 어떤 FPGA에 대한 XDC인지 | `$ARGUMENTS`로 레퍼런스 지정 |
| 전원/GND 핀 | XDC 대상이 아님 | 자동 필터링 |
| 내부 전용 핀 (JTAG, CONFIG) | IOSTANDARD가 특수 | 알려진 핀은 자동 처리, 나머지는 TODO 표시 |
