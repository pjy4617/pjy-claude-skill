---
name: pin-review
description: 핀 배치 리뷰 체크리스트 정의. pin-reviewer 에이전트가 참조하는 기준 문서입니다. 사용자가 "핀 배치 확인", "XDC 리뷰", "IOSTANDARD 확인" 등을 요청하면 pin-reviewer 에이전트에게 위임됩니다.
---

# 핀 배치 & 제약 파일 리뷰 체크리스트

> 이 스킬은 체크리스트를 정의합니다.
> 실제 리뷰 작업은 pin-reviewer 에이전트에게 위임됩니다.
>
> XDC 핀 배치 오류의 특성:
>   - 합성/Implementation은 **정상 통과**합니다
>   - 보드에서 **동작하지 않거나, 하드웨어가 손상**될 수 있습니다
>   - Vivado가 잡아주지 않으므로 사람(또는 리뷰어)이 잡아야 합니다

## 리뷰 범위

리뷰 요청 시 아래 7개 카테고리를 **모두** 검사합니다.
각 항목은 PASS / WARN / FAIL로 판정합니다.

---

## 카테고리 1: 포트 매칭 (Port Matching)

Top 모듈의 포트와 XDC의 `get_ports`가 1:1 대응하는지.

| # | 체크 항목 | FAIL 조건 |
|---|----------|-----------|
| PM1 | XDC에 정의된 모든 포트가 top.v에 존재 | XDC에 `get_ports oled_sdin` → top.v에 `oled_sdin` 포트 없음 |
| PM2 | top.v의 모든 I/O 포트가 XDC에 정의됨 | top.v에 `output led0` → XDC에 핀 할당 없음 |
| PM3 | 포트 이름 철자 일치 | XDC: `oled_sdin` vs top.v: `oled_sdi` (오타) |
| PM4 | 버스 포트 인덱스 일치 | top.v: `output [7:0] led` → XDC에 `led[0]`~`led[7]` 모두 있는지 |
| PM5 | 포트 방향과 핀 용도 일치 | `input` 포트가 출력 전용 핀에 할당되지 않았는지 |

## 카테고리 2: 핀 번호 정확성 (Pin Assignment)

PACKAGE_PIN이 실제 보드 회로도와 일치하는지.

| # | 체크 항목 | FAIL 조건 |
|---|----------|-----------|
| PA1 | 핀 번호가 보드 회로도/데이터시트와 일치 | 회로도: OLED_SDIN = AB12, XDC: AB13 (오류) |
| PA2 | 클럭 핀이 MRCC/SRCC 전용 핀에 할당 | 100MHz 클럭을 일반 I/O 핀에 할당 |
| PA3 | 같은 핀에 중복 할당 없음 | 두 개의 서로 다른 포트가 같은 PACKAGE_PIN 사용 |
| PA4 | 핀이 해당 FPGA 패키지에 실제로 존재 | xc7z020clg484에 없는 핀 번호 사용 |
| PA5 | 보드 변경 시 핀 번호 업데이트 | boards.json에서 보드를 바꿨는데 XDC는 이전 보드 핀 그대로 |

## 카테고리 3: IOSTANDARD (전압 레벨)

핀의 전압 표준이 보드 뱅크 전압과 일치하는지.
**불일치 시 FPGA 또는 외부 디바이스가 물리적으로 손상될 수 있음.**

| # | 체크 항목 | FAIL 조건 |
|---|----------|-----------|
| IO1 | IOSTANDARD 명시 | IOSTANDARD 미지정 (Vivado 기본값에 의존) |
| IO2 | 뱅크 전압과 IOSTANDARD 일치 | VCCO=3.3V 뱅크에 LVCMOS18 설정 |
| IO3 | 같은 뱅크 내 IOSTANDARD 통일 | 같은 뱅크에 LVCMOS33과 LVCMOS25 혼재 |
| IO4 | 외부 디바이스 전압 호환 | OLED SSD1306은 3.3V → LVCMOS33 필수 |
| IO5 | 차동 신호 페어 IOSTANDARD | LVDS 사용 시 P/N 페어가 올바른지 |

### ZedBoard 뱅크 전압 참조
```
Bank 13 (MIO)  : 3.3V — PS I/O
Bank 33        : 3.3V — Pmod, OLED, 버튼, LED
Bank 34        : 1.8V — HDMI, Audio
Bank 35        : 3.3V — FMC LPC (LA00-LA16)
Bank 0         : 설정용 (CFGBVS)
```

## 카테고리 4: 타이밍 제약 (Timing Constraints)

클럭 정의 및 타이밍 관련 제약이 올바른지.

| # | 체크 항목 | FAIL 조건 |
|---|----------|-----------|
| TC1 | 기본 클럭 `create_clock` 정의 | 클럭 포트에 `create_clock` 없음 |
| TC2 | 클럭 주기 정확성 | 100MHz → `period 10.000`, 실수로 `period 100.000` |
| TC3 | 클럭 핀과 `create_clock` 포트 일치 | XDC: `get_ports clk` vs 실제 포트명 불일치 |
| TC4 | 생성 클럭 정의 | PLL/MMCM 사용 시 `create_generated_clock` 누락 |
| TC5 | 비동기 경로 `set_false_path` | 리셋, 버튼 등 비동기 입력에 false_path 미설정 |
| TC6 | I/O 딜레이 | 외부 인터페이스에 `set_input_delay`/`set_output_delay` 미설정 |

## 카테고리 5: 기능별 핀 검증 (Functional Pin Check)

신호의 논리적 기능과 물리적 핀의 용도가 맞는지.

| # | 체크 항목 | FAIL 조건 |
|---|----------|-----------|
| FP1 | SPI 신호 핀 검증 | SCLK/MOSI/MISO/CS가 보드의 SPI 헤더와 일치 |
| FP2 | 버튼 핀 풀업/풀다운 | 버튼이 active-high인데 RTL에서 active-low로 처리 (또는 반대) |
| FP3 | LED 핀 극성 | active-high LED에 1 출력 시 점등되는지 |
| FP4 | 전원 제어 핀 극성 | OLED VDD/VBAT 핀의 active-high/low가 RTL과 일치 |
| FP5 | 리셋 핀 극성 | 보드의 리셋 버튼이 active-low인데 RTL에서 active-high로 처리 |
| FP6 | 미사용 핀 처리 | 미사용 핀이 내부 풀업/풀다운으로 적절히 처리되었는지 |

## 카테고리 6: 보드 호환성 (Board Compatibility)

boards.json과 XDC의 일관성, 보드 변경 시 문제 예방.

| # | 체크 항목 | WARN 조건 |
|---|----------|-----------|
| BC1 | boards.json의 part와 XDC 타겟 일치 | boards.json: xc7z020clg484-1 vs TCL의 set PART 불일치 |
| BC2 | boards.json의 clock_pin과 XDC 일치 | boards.json: Y9 vs XDC의 clk PACKAGE_PIN 불일치 |
| BC3 | boards.json의 xdc 경로 유효 | boards.json이 가리키는 XDC 파일이 실제로 존재하는지 |
| BC4 | 보드 전용 기능 확인 | ZedBoard 전용 OLED 핀을 다른 보드 XDC에 사용 |
| BC5 | Digilent 마스터 XDC 참조 | 핀 번호를 Digilent 공식 XDC와 대조했는지 |

## 카테고리 7: 안전성 (Safety)

하드웨어 손상을 방지하는 검사.

| # | 체크 항목 | FAIL 조건 |
|---|----------|-----------|
| SF1 | 출력 드라이브 강도 | 고전류 부하에 약한 드라이브 강도 설정 |
| SF2 | 슬루 레이트 | 고속 신호에 SLOW 설정 (또는 반대) |
| SF3 | 전원 시퀀싱 핀 초기값 | OLED VDD/VBAT 같은 전원 제어 핀의 초기 상태가 안전한지 (OFF) |
| SF4 | 양방향 핀 충돌 | inout 포트의 방향 제어가 올바른지 |
| SF5 | 핀 과부하 | 한 FPGA 출력에 너무 많은 팬아웃 (PCB 레벨) |

---

## 리포트 형식

```
═══════════════════════════════════════
  핀 배치 & 제약 리뷰 리포트
  보드: ZedBoard (xc7z020clg484-1)
  XDC: constraints/zedboard.xdc
  Top: rtl/top.v
═══════════════════════════════════════

[요약]
  PASS: 25 / WARN: 2 / FAIL: 1 / TOTAL: 28

[FAIL 항목] ⚡ 하드웨어 손상 위험 포함
  ❌ IO2 — constraints/zedboard.xdc:15
     oled_dc 핀(U10)은 Bank 34 (VCCO=1.8V)
     LVCMOS33 설정은 전압 불일치 → FPGA 손상 위험
     수정: IOSTANDARD를 LVCMOS18로 변경, 또는
           1.8V→3.3V 레벨 시프터 필요 여부 회로도 확인

[WARN 항목]
  ⚠️ TC6 — SPI 출력(oled_sclk, oled_sdin)에
     set_output_delay 미설정
     10MHz SPI에서는 문제없으나, 고속화 시 필요
  ⚠️ FP6 — 미사용 Pmod 핀 처리 없음
     PULLDOWN 또는 PULLUP 설정 권장

[포트 매칭 검증]
  top.v 포트 (12개) ↔ XDC 핀 할당 (12개) → ✅ 1:1 대응
  
  포트명         방향     PACKAGE_PIN  IOSTANDARD  Bank  뱅크전압  일치?
  ──────────    ──────   ───────────  ──────────  ────  ────────  ─────
  clk           input    Y9           LVCMOS33    33    3.3V      ✅
  rst_n         input    T18          LVCMOS33    33    3.3V      ✅
  btnr          input    R18          LVCMOS33    33    3.3V      ✅
  btnu          input    T22          LVCMOS33    33    3.3V      ✅
  btnc          input    P16          LVCMOS33    33    3.3V      ✅
  btnd          input    R16          LVCMOS33    33    3.3V      ✅
  led0          output   T22          LVCMOS33    33    3.3V      ✅
  oled_sdin     output   AB12         LVCMOS33    33    3.3V      ✅
  oled_sclk     output   AA12         LVCMOS33    33    3.3V      ✅
  oled_dc       output   U10          LVCMOS33    34    1.8V      ❌
  oled_res      output   U9           LVCMOS33    33    3.3V      ✅
  oled_vbat     output   U11          LVCMOS33    33    3.3V      ✅
```

## 보드별 참조 데이터 소스

| 보드 | 공식 XDC 소스 |
|------|-------------|
| ZedBoard | github.com/Digilent/digilent-xdc/Zedboard-Master.xdc |
| Arty A7 | github.com/Digilent/digilent-xdc/Arty-A7-35-Master.xdc |
| Nexys 4 DDR | github.com/Digilent/digilent-xdc/Nexys-4-DDR-Master.xdc |
| Zybo Z7 | github.com/Digilent/digilent-xdc/Zybo-Z7-Master.xdc |

리뷰 시 반드시 공식 마스터 XDC와 대조합니다.
