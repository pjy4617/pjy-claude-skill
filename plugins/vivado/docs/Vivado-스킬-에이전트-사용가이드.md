# Vivado 스킬 & 에이전트 사용 가이드

> ZedBoard OLED 데모 프로젝트를 예시로 배우는 Claude Code 활용법
> 
> 이 가이드의 목적은 OLED을 구현하는 것이 아닙니다.
> **13개 스킬과 6개 에이전트를 실전에서 어떻게 사용하는지** 배우는 것입니다.
> OLED 데모는 그 예시일 뿐입니다.

---

## 목차

1. [이 가이드의 목적](#1-이-가이드의-목적)
2. [스킬과 에이전트, 뭐가 다른가요?](#2-스킬과-에이전트-뭐가-다른가요)
3. [사전 준비](#3-사전-준비)
4. [실습: 대화 예시로 배우는 전체 플로우](#4-실습-대화-예시로-배우는-전체-플로우)
5. [핵심 패턴: 이렇게 말하면 이렇게 동작합니다](#5-핵심-패턴-이렇게-말하면-이렇게-동작합니다)
6. [FAIL이 나왔을 때 대응법](#6-fail이-나왔을-때-대응법)
7. [자주 묻는 질문](#7-자주-묻는-질문)
8. [부록: 전체 스킬/에이전트 카탈로그](#8-부록-전체-스킬에이전트-카탈로그)

---

## 1. 이 가이드의 목적

### 이 가이드가 다루는 것

- Claude Code에서 **뭐라고 말하면** 어떤 스킬/에이전트가 동작하는지
- 결과가 나오면 **어떻게 해석하고** 다음에 **뭘 말해야 하는지**
- FAIL이 나오면 **어떻게 수정을 요청하는지**
- 스킬이 동작하는 것과 에이전트가 동작하는 것을 **어떻게 구분하는지**

### 이 가이드가 다루지 않는 것

- Verilog 문법 설명
- Vivado TCL 명령 상세
- XDC 제약 파일 작성법
- OLED SSD1306 프로토콜

이런 것들은 **스킬과 에이전트가 알아서 처리**합니다.
당신은 "뭘 원하는지"만 말하면 됩니다.

---

## 2. 스킬과 에이전트, 뭐가 다른가요?

### 한 줄 요약

- **스킬** = 작업 절차서. "이 작업은 이 순서로 해라."
- **에이전트** = 전문가. "이 사람이 별도로 작업해서 결과만 보내줘."

### 체감 차이

| | 스킬 | 에이전트 |
|---|---|---|
| **비유** | 요리 레시피 | 전문 셰프 |
| **동작 방식** | Claude가 레시피를 보고 작업 | 별도 전문가가 따로 작업 후 결과만 전달 |
| **대화 영향** | 메인 대화에서 바로 실행 | 메인 대화를 오염시키지 않음 |
| **언제 쓰나** | 정해진 절차가 있을 때 | 전문적 판단이 필요할 때 |
| **호출 방법** | 자동 또는 `/스킬명` | 자동 위임 또는 "~에게 맡겨줘" |

### 이 프로젝트의 구성

```
스킬 13개 (절차서)                   에이전트 6명 (전문가)
──────────────                     ─────────────────
vivado-setup    에이전트/환경 설치     rtl-designer   설계 전문가
vivado-project  프로젝트/보드 관리    rtl-reviewer   RTL 검증자
vivado-sim      시뮬레이션            tb-reviewer    TB 검증자
vivado-synth    합성                  pin-reviewer   핀 배치 검증자
vivado-impl     배치/라우팅           timing-analyst 타이밍 분석 및 최적화 제안
vivado-bitstream 비트스트림           kicad-xdc-gen  KiCad→XDC 생성
vivado-build-all 전체 빌드 플로우
vivado-gui      GUI 전환
rtl-review      RTL 체크리스트
tb-review       TB 체크리스트
pin-review      핀 배치 체크리스트
kicad-xdc       KiCad→XDC 변환
kicad-review    KiCad 회로 리뷰
```

### 어떻게 구분하나요?

사용할 때는 구분할 필요 없습니다. 당신이 말하면 Claude Code가 알아서 판단합니다.

- "합성해줘" → Claude가 "이건 정해진 절차네" → **vivado-synth 스킬** 로드
- "모듈 만들어줘" → Claude가 "이건 전문가가 별도로 작업해야 하네" → **rtl-designer 에이전트**에 위임
- "리뷰해줘" → Claude가 "이건 3명의 전문가가 동시에 봐야 하네" → **3개 에이전트** 병렬 위임
- "KiCad에서 XDC 만들어줘" → Claude가 "넷리스트 추출하고 변환해야 하네" → **kicad-xdc-gen 에이전트**에 위임

---

## 3. 사전 준비

### 필요한 것

- AMD Vivado가 설치된 Linux 환경 (WSL 포함)
- Claude Code (터미널에서 실행)
- FPGA 보드 (이 예시에서는 ZedBoard, 보드 없이 시뮬레이션까지만도 가능)
- KiCad 8.0+ (KiCad→XDC 자동 생성 기능 사용 시, 선택 사항)

### 스킬 설치 (1분)

```bash
# 1. 마켓플레이스 추가 (한 번만)
/plugin marketplace add pjy4617/pjy-claude-skill

# 2. Vivado 플러그인 설치
/plugin install vivado@pjy-skills

# 3. 에이전트 + CLAUDE.md + 디렉토리 설치 (최초 1회)
/vivado-setup
```

셋업 시 프로젝트 경로를 질문합니다:
```
> Vivado 프로젝트를 설치할 경로를 알려주세요.
> (엔터만 누르면 현재 디렉토리에 설치합니다)
```

지정한 경로에 에이전트, CLAUDE.md, 디렉토리 구조(`rtl/`, `tb/`, `constraints/`, `scripts/`, `build/`)가 생성됩니다.

설치 확인:

```bash
ls <프로젝트경로>/.claude/agents/
# kicad-xdc-gen.md  pin-reviewer.md  rtl-designer.md
# rtl-reviewer.md   tb-reviewer.md   timing-analyst.md
```

해당 폴더 안에서 Claude Code를 실행하면, 모든 스킬과 에이전트가 자동으로 인식됩니다.

---

## 4. 실습: 대화 예시로 배우는 전체 플로우

> 이 섹션이 가이드의 핵심입니다.
> 각 단계를 **"당신이 입력하는 말 → 내부에서 벌어지는 일 → 당신이 받는 결과 → 다음에 할 말"** 패턴으로 설명합니다.

---

### 4.1 프로젝트 생성

#### 당신이 입력하는 말

```
> ZedBoard용 OLED 디스플레이 제어 프로젝트 만들어줘
```

#### 내부에서 벌어지는 일

```
🔧 vivado-project 스킬이 동작합니다 (에이전트가 아님)
   ↓
   boards.json에서 ZedBoard 정보를 찾음
     part: xc7z020clg484-1
     clock: 100MHz, 핀 Y9
   ↓
   디렉터리 구조 생성 (rtl/, tb/, constraints/, scripts/, build/)
   ↓
   XDC 파일 생성, TCL 스크립트 템플릿 생성
```

#### 당신이 받는 결과

```
ZedBoard 프로젝트를 생성했습니다.
- 타겟: xc7z020clg484-1 (Zynq-7000)
- 클럭: 100MHz (Y9)
- XDC: constraints/zedboard.xdc
- 디렉터리: rtl/, tb/, constraints/, scripts/, build/
```

#### 다음에 할 말

```
> OLED 디스플레이를 SPI로 제어하는 Verilog 모듈을 만들어줘
```

#### 💡 초보자 팁

- "ZedBoard" 대신 "Arty A7" 이라고 하면, 같은 스킬이 boards.json에서 다른 보드 정보를 찾아 설정합니다.
- `/vivado-project` 로 직접 스킬을 호출할 수도 있습니다.

---

### 4.1b KiCad 회로도에서 XDC 자동 생성 (선택 사항)

> KiCad로 회로를 설계했다면, XDC를 수동으로 작성할 필요 없이 회로도에서 자동 생성할 수 있습니다.
> KiCad 회로도가 없으면 이 단계를 건너뛰세요.

#### 당신이 입력하는 말

```
> KiCad 회로도에서 ZedBoard용 XDC 만들어줘
```

#### 내부에서 벌어지는 일

```
👤 kicad-xdc-gen 에이전트가 동작합니다 (별도 컨텍스트)
   ↓
   ① kicad-cli로 넷리스트 추출
      kicad-cli sch export netlist → build/netlist.xml
   ↓
   ② FPGA 심볼 자동 탐지
      netlist.xml에서 "xc7z020" 패턴 → U1 찾음
   ↓
   ③ 핀 ↔ 네트 매핑 추출 (예: Y9 → CLK_100MHZ)
      핀 번호 = PACKAGE_PIN
      네트 이름 → 포트 이름으로 변환
   ↓
   ④ 뱅크/IOSTANDARD 자동 결정
      boards.json의 bank_vcco 참조
      핀 이름에서 뱅크 추출 (IO_L12P_T1_MRCC_33 → Bank 33)
      Bank 33 → 3.3V → LVCMOS33
   ↓
   ⑤ 네트 이름 패턴 자동 인식
      net_patterns.json 참조
      CLK_100MHZ → create_clock 생성
      CPU_RESET_N → set_false_path 생성
      OLED_SDIN → SPI 그룹 주석
   ↓
   ⑥ constraints/zedboard.xdc 자동 생성
```

#### 당신이 받는 결과

```
XDC 생성 완료 → constraints/zedboard.xdc
  FPGA: U1 (xc7z020clg484)
  Total pins: 52
  Excluded (power/GND/config): 96
  TODO (IOSTANDARD 불명): 3

⚠️ 자동 생성 파일입니다.
   "핀 배치 확인해줘" 로 pin-reviewer 검증을 권장합니다.
```

#### 다음에 할 말

```
> 핀 배치 확인해줘
```

pin-reviewer가 자동 생성된 XDC를 검증합니다.
TODO 항목이 있으면 수동으로 확인이 필요합니다.

#### 💡 초보자 팁

- KiCad 회로도가 있으면 XDC를 수동으로 작성할 필요가 없습니다. **회로도가 핀 배치의 원본(single source of truth)**이 됩니다.
- FPGA 심볼이 여러 개면: `"U2 FPGA의 XDC 만들어줘"` 처럼 레퍼런스를 지정하세요.
- `kicad-cli`가 없으면 에이전트가 `.kicad_sch` 파일을 직접 파싱하지만, 정확도가 떨어집니다. KiCad 설치를 권장합니다.
- 자동 생성이어도 **pin-reviewer 검증은 필수**입니다. 자동 ≠ 정확하다는 보장이 아닙니다.

---

### 4.1c KiCad 회로 리뷰 (선택 사항)

> KiCad 회로도 자체의 품질을 검토하고 싶을 때 사용합니다.

#### 당신이 입력하는 말

```
> KiCad 회로도 리뷰해줘
```

#### 내부에서 벌어지는 일

```
🔧 kicad-review 스킬이 동작합니다
   ↓
   ① kicad-cli로 ERC(전기 규칙 검사) 실행
   ② .kicad_sch S-expression 직접 파싱 (부품 분류, 전원 네트, 디커플링 캡)
   ③ 넷리스트 기반 연결성 검증
   ④ BOM 추출 및 검토
   ⑤ PCB DRC (PCB 파일 존재 시)
   ⑥ 종합 보고서 (전원부, MCU, 통신, 보호회로 체크)
```

#### 당신이 받는 결과

```
KiCad 회로 리뷰 리포트
  전원부: PASS (디커플링 캡 OK, PWR_FLAG OK)
  통신: WARN (I2C 풀업 저항 누락)
  보호회로: FAIL (ESD 보호 없음)
  일반: PASS (풋프린트 할당 완료)
```

#### 💡 초보자 팁

- 이 스킬은 Vivado가 아닌 **KiCad 회로 설계 품질**을 검토합니다.
- XDC 생성 전에 회로도를 먼저 리뷰하면, 잘못된 핀 연결이 XDC까지 전파되는 것을 방지합니다.

---

### 4.2 RTL 설계

#### 당신이 입력하는 말

```
> OLED 디스플레이를 SPI로 제어하는 Verilog 모듈을 만들어줘.
> D-Pad 버튼 4개로 조작하고 LED0으로 상태를 표시해.
```

#### 내부에서 벌어지는 일

```
👤 rtl-designer 에이전트가 동작합니다 (스킬이 아님)
   ↓
   ⚡ 별도 컨텍스트에서 독립 작업 시작
   ↓
   CLAUDE.md의 코딩 규칙 참조
   자신의 시스템 프롬프트에 따라:
     - snake_case 모듈명
     - 3-process FSM
     - 동기식 리셋
     - 합성 가능성 체크리스트 검증
   ↓
   RTL 파일들 생성 (rtl/*.v)
   테스트벤치 생성 (tb/tb_*.v)
   ↓
   결과만 메인 대화로 반환
```

#### 당신이 받는 결과

```
다음 모듈을 생성했습니다:
  rtl/top.v          — 최상위 모듈
  rtl/oled_ctrl.v    — OLED 제어 FSM
  rtl/spi_ctrl.v     — SPI 마스터
  rtl/delay_counter.v — 딜레이 카운터
  rtl/char_lib.v     — 문자 폰트 ROM
  tb/tb_spi_ctrl.v   — SPI 테스트벤치
  tb/tb_oled_ctrl.v  — OLED 제어 테스트벤치
```

#### 다음에 할 말

```
> 전체 리뷰해줘
```

#### 💡 초보자 팁

- rtl-designer는 **에이전트**이므로 별도 컨텍스트에서 작업합니다. 메인 대화에 코드가 쏟아지지 않고, 생성된 파일 목록만 보입니다.
- 요청이 구체적일수록 좋습니다. "SPI", "D-Pad 버튼 4개" 같은 키워드가 설계 품질을 높입니다.
- 추가 요청도 가능합니다: "uart_tx 모듈도 추가해줘"

---

### 4.3 코드 리뷰 (빌드 전 품질 게이트)

> **이 단계가 가장 중요합니다.**
> 리뷰를 건너뛰고 바로 합성해도 되지만, 
> 리뷰를 거치면 합성 에러, 시뮬레이션 실패, 보드 손상을 **사전에** 방지합니다.

#### 당신이 입력하는 말

```
> 전체 리뷰해줘
```

#### 내부에서 벌어지는 일

```
👤👤👤 3개 에이전트가 동시에 동작합니다 (각각 별도 컨텍스트)

┌─ rtl-reviewer (RTL 검증자)
│    rtl-review 스킬의 체크리스트 32항목 적용
│    모든 .v 파일을 읽고 교차 검증
│    "합성 가능한가? 포트가 맞는가?"
│
├─ tb-reviewer (TB 검증자)
│    tb-review 스킬의 체크리스트 28항목 적용
│    테스트벤치 파일의 구조/커버리지/자동검증을 분석
│    (DUT 로직 자체의 정확성은 rtl-reviewer가 담당)
│    "검증이 충분한가? 커버리지는?"
│
└─ pin-reviewer (핀 배치 검증자)
     pin-review 스킬의 체크리스트 28항목 적용
     top.v + XDC + boards.json 교차 검증
     "핀 배치가 안전한가? 전압은 맞는가?"

각 에이전트가 결과만 메인 대화로 반환
```

#### 당신이 받는 결과

```
═══════════════════════════════════════
  코드 리뷰 종합 리포트
═══════════════════════════════════════

RTL 리뷰:  PASS 28 / WARN 3 / FAIL 0  ✅
TB 리뷰:   PASS 22 / WARN 4 / FAIL 2  ❌
Pin 리뷰:  PASS 25 / WARN 2 / FAIL 1  ❌

[TB FAIL]
  ❌ SC1 — tb/tb_oled_ctrl.v
     자동 PASS/FAIL 판정 없음. 파형 수동 확인에 의존.
  ❌ DM1 — tb/tb_spi_ctrl.v
     DUT 출력 'busy' 포트가 TB에서 미연결

[Pin FAIL]
  🔴 IO2 — oled_dc(U10)은 Bank 34(VCCO=1.8V)
     LVCMOS33 설정은 전압 불일치 → FPGA 손상 위험!

[WARN 항목 — 지금 안 고쳐도 되지만 권장]
  ⚠️ CV6 — FSM 상태 3/5만 커버
  ⚠️ C6 — spi_ctrl.v에 매직 넘버 50
  ...
```

#### 이 결과를 어떻게 읽나요?

- **PASS** = 이상 없습니다.
- **WARN** = 지금 안 고쳐도 동작은 하지만, 나중에 문제가 될 수 있습니다.
- **FAIL** = 반드시 고쳐야 합니다. 안 고치면 합성 실패하거나 보드가 손상됩니다.
- **🔴 CRITICAL** = FAIL 중에서도 최고 심각도. IOSTANDARD 전압 불일치, 전용 핀 오용 등 **FPGA 또는 보드 하드웨어가 물리적으로 손상**될 수 있는 항목입니다. 발견 즉시 최우선으로 수정해야 합니다.

#### 다음에 할 말

FAIL이 있으므로 수정을 요청합니다:

```
> FAIL 항목 전부 수정해줘
```

그러면 rtl-designer 에이전트가 수정하고, 다시 리뷰를 요청합니다:

```
> 다시 리뷰해줘
```

**3개 리뷰 모두 FAIL=0이 될 때까지 반복합니다.**

```
RTL 리뷰:  PASS 30 / WARN 2 / FAIL 0  ✅
TB 리뷰:   PASS 26 / WARN 2 / FAIL 0  ✅
Pin 리뷰:  PASS 27 / WARN 1 / FAIL 0  ✅
→ 빌드 진행 가능!
```

#### 💡 초보자 팁

- "전체 리뷰해줘" 한마디로 3개 리뷰어가 88개 항목을 검사합니다.
- 특정 부분만 리뷰할 수도 있습니다:
  - `"RTL만 리뷰해줘"` → rtl-reviewer만 동작
  - `"핀 배치 확인해줘"` → pin-reviewer만 동작
  - `"spi_ctrl.v만 리뷰해줘"` → 특정 파일만 검사
- WARN은 무시해도 빌드에 영향 없습니다. 하지만 고치면 코드 품질이 올라갑니다.

---

### 4.4 시뮬레이션

#### 당신이 입력하는 말

```
> 시뮬레이션 돌려줘
```

#### 내부에서 벌어지는 일

```
🔧 vivado-sim 스킬이 동작합니다 (에이전트가 아님)
   ↓
   스킬에 정의된 3단계 파이프라인을 순서대로 실행:
     ① xvlog (컴파일)
     ② xelab (엘라보레이션)
     ③ xsim (시뮬레이션 실행)
   ↓
   자동으로 결과 확인:
     grep -E "(PASS|FAIL|ERROR)" xsim.log
```

#### 당신이 받는 결과

```
시뮬레이션 완료.

--- Test 1: Single byte transfer ---
PASS: SPI byte 0x55 transferred correctly
--- Test 2: Boundary values ---
PASS: 0x00 transferred correctly
PASS: 0xFF transferred correctly
========================================
PASS: All 5 tests passed
========================================
```

#### 다음에 할 말

- **전부 PASS** → 합성으로: `"합성해줘"`
- **FAIL 있음** → 원인 추적: `"시뮬레이션 FAIL 원인 찾아줘"`
- **파형을 눈으로 보고 싶음** → `"파형 보여줘"`

#### 💡 초보자 팁

- 시뮬레이션은 **스킬**입니다. 정해진 절차(xvlog→xelab→xsim)를 실행할 뿐입니다.
- 이전 단계에서 리뷰를 거쳐 TB가 이미 검증되었으므로, FAIL이 나오면 DUT(설계) 문제일 가능성이 높습니다.
- 특정 모듈만 시뮬레이션: `"spi_ctrl만 시뮬레이션 돌려줘"`

---

### 4.5 합성 → Implementation → Bitstream

> 이 3단계는 패턴이 동일합니다. 한꺼번에 설명합니다.

#### 당신이 입력하는 말

```
> 합성해줘
```

합성이 끝나면:

```
> Implementation 돌려줘
```

Implementation이 끝나면:

```
> 비트스트림 만들어줘
```

#### 내부에서 벌어지는 일

```
🔧 vivado-synth 스킬 → 🔧 vivado-impl 스킬 → 🔧 vivado-bitstream 스킬
   (3개 모두 스킬 — 정해진 TCL 절차를 batch로 실행)
   
   각 단계마다:
   ① TCL 스크립트 실행 (vivado -mode batch)
   ② 결과 리포트 확인 (WNS, 리소스, DRC 등)
   ③ 문제 없으면 다음 단계, 문제 있으면 알려줌
```

#### 당신이 받는 결과 (각 단계별)

합성:
```
합성 완료.
  WNS: 3.245ns ✅ (타이밍 충족)
  LUT 사용: 342/53200 (0.6%)
  에러: 0, 경고: 2
```

Implementation:
```
Implementation 완료.
  WNS: 2.891ns ✅
  DRC 위반: 0 ✅
  전력: 0.18W
```

Bitstream:
```
Bitstream 생성 완료.
  파일: build/output/top.bit (4.0MB)
```

#### 중간에 문제가 생기면?

WNS가 음수(타이밍 위반)이면 Claude가 알려줍니다:

```
합성 완료. 단, 타이밍 위반이 있습니다.
  WNS: -1.2ns ❌
```

이때 이렇게 말하면:

```
> 타이밍 분석해줘
```

```
👤 timing-analyst 에이전트가 동작합니다
   ↓
   별도 컨텍스트에서 타이밍 리포트 전체를 읽고 분석
   ↓
   원인 분석 및 최적화 제안을 메인 대화로 반환:
   "원인: oled_ctrl의 FSM 출력 로직이 8단 조합 경로
    최적화 제안: 파이프라인 1단 추가"
```

#### 💡 초보자 팁

- 합성/Impl/Bitstream은 모두 **스킬**입니다. 정해진 TCL 스크립트를 실행합니다.
- timing-analyst는 **에이전트**입니다. 타이밍 위반이라는 "전문적 판단"이 필요하기 때문입니다.
- 3단계를 한꺼번에 요청할 수도 있습니다: `"합성부터 비트스트림까지 전부 돌려줘"`

---

### 4.6 GUI로 확인하기

> CLI에서 빌드한 결과를 GUI에서 **보기만** 하는 것입니다.
> GUI에서 수정하지 않습니다.

#### 당신이 입력하는 말

상황에 따라 다릅니다:

| 보고 싶은 것 | 이렇게 말하세요 |
|-------------|---------------|
| 시뮬레이션 파형 | `"파형 보여줘"` 또는 `"waveform 열어"` |
| 합성된 회로도 | `"스키매틱 보여줘"` |
| 칩 위 배치 | `"Device View 보여줘"` 또는 `"배치 결과 보여줘"` |
| 타이밍 경로 | `"라우팅 결과 보여줘"` |
| FPGA 프로그래밍 (GUI) | `"Hardware Manager 열어줘"` |

#### 내부에서 벌어지는 일

```
🔧 vivado-gui 스킬이 동작합니다
   ↓
   해당 체크포인트(.dcp) 또는 파형 파일(.wdb)을 GUI로 엶:
     vivado build/checkpoints/post_route.dcp &
   ↓
   또는 헬퍼 스크립트 실행:
     ./scripts/open_gui.sh route
```

#### 💡 초보자 팁

- GUI는 **보는 용도로만** 사용합니다. 수정은 항상 RTL/XDC에서 합니다.
- GUI 없이도 전체 플로우가 가능합니다. GUI는 선택 사항입니다.
- WSL에서 GUI가 안 열리면 X11 설정이 필요할 수 있습니다.

---

### 4.7 FPGA에 다운로드하기

#### 당신이 입력하는 말

```
> FPGA에 다운로드해줘
```

#### 내부에서 벌어지는 일

```
🔧 vivado-bitstream 스킬이 동작합니다
   ↓
   전제 조건 확인:
     ✅ top.bit 존재, ✅ WNS ≥ 0, ✅ DRC 위반 없음
   ↓
   program_fpga.tcl 실행
   ↓
   "Programming Complete" 출력
```

#### 당신이 받는 결과

```
FPGA 프로그래밍 완료.
보드에서 OLED 디스플레이가 자동으로 초기화됩니다.
D-Pad 버튼으로 조작하세요.

⚠️ 보드 전원 끄기 전: BTNR로 OLED OFF → 3.5초 대기 → 전원 OFF
```

#### 💡 초보자 팁

- GUI로 프로그래밍하고 싶으면: `"Hardware Manager 열어줘"` → GUI에서 Program Device
- 보드가 연결되지 않으면 `"No hardware target"` 에러가 나옵니다. USB 확인하세요.

---

## 5. 핵심 패턴: 이렇게 말하면 이렇게 동작합니다

### 스킬이 동작하는 경우 (정해진 절차 실행)

| 당신이 말하면 | 동작하는 스킬 | 하는 일 |
|-------------|-------------|--------|
| "프로젝트 만들어" | vivado-project | 보드 설정, 디렉터리 생성 |
| "시뮬레이션 돌려" | vivado-sim | xvlog→xelab→xsim |
| "합성해줘" | vivado-synth | synth_design batch 실행 |
| "Implementation 돌려" | vivado-impl | place→route batch 실행 |
| "비트스트림 만들어" | vivado-bitstream | write_bitstream 실행 |
| "전체 빌드 돌려" | vivado-build-all | 합성→Impl→Bitstream 일괄 실행 |
| "파형 보여줘" | vivado-gui | GUI로 파형 열기 |
| "스키매틱 보여줘" | vivado-gui | GUI로 체크포인트 열기 |
| "KiCad 회로도 리뷰해줘" | kicad-review | ERC, 넷리스트, BOM 종합 검토 |

### 에이전트가 동작하는 경우 (전문가가 별도 작업)

| 당신이 말하면 | 동작하는 에이전트 | 하는 일 |
|-------------|-----------------|--------|
| "모듈 만들어줘" | rtl-designer | Verilog 코드 설계 전문 (별도 컨텍스트, 리뷰는 rtl-reviewer가 담당) |
| "리뷰해줘" | rtl-reviewer + tb-reviewer + pin-reviewer | 3인 병렬 리뷰 (각각 별도 컨텍스트) |
| "RTL만 리뷰해줘" | rtl-reviewer | RTL 체크리스트 32항목 검사 |
| "테스트벤치 리뷰해줘" | tb-reviewer | TB 체크리스트 28항목 검사 |
| "핀 배치 확인해줘" | pin-reviewer | 핀 체크리스트 28항목 검사 |
| "타이밍 분석해줘" | timing-analyst | 타이밍 리포트 분석 및 최적화 제안 (별도 컨텍스트) |
| "KiCad에서 XDC 만들어줘" | kicad-xdc-gen | 넷리스트에서 XDC 자동 생성 (별도 컨텍스트) |

### 에이전트 + 스킬이 함께 동작하는 경우

| 상황 | 에이전트 | 참조하는 스킬 |
|------|---------|-------------|
| "RTL 리뷰해줘" | rtl-reviewer | rtl-review 스킬의 체크리스트 |
| "TB 리뷰해줘" | tb-reviewer | tb-review 스킬의 체크리스트 |
| "핀 확인해줘" | pin-reviewer | pin-review 스킬의 체크리스트 |
| "KiCad에서 XDC" | kicad-xdc-gen | kicad-xdc 스킬의 변환 규칙 + net_patterns.json |

에이전트가 "무엇을 검사할지"를 스킬에서 참조하는 구조입니다.
이 체크리스트를 프로젝트에 맞게 수정할 수 있습니다.

---

## 6. FAIL이 나왔을 때 대응법

### 리뷰 FAIL

| 리뷰 리포트에서 | 이렇게 말하세요 | 누가 고치나요 |
|---------------|---------------|-------------|
| `❌ S1 — 래치 추론` | "래치 문제 수정해줘" | rtl-designer |
| `❌ SC1 — 자동 검증 없음` | "테스트벤치에 자동 검증 추가해줘" | rtl-designer |
| `🔴 IO2 — 전압 불일치` | "IOSTANDARD 수정해줘" | rtl-designer |
| `❌ DM1 — 포트 미연결` | "TB 포트 연결 수정해줘" | rtl-designer |

수정 후 반드시: `"다시 리뷰해줘"`

### 시뮬레이션 FAIL

시뮬레이션이 실패하면 원인을 3단계로 추적합니다:

```
당신: "시뮬레이션 FAIL 원인 찾아줘"

① tb-reviewer → "TB 자체에 버그가 있나?"
   결과: "TB는 정상입니다"

② rtl-reviewer → "RTL에 합성 가능성 문제가 있나?"
   결과: "RTL 구조는 정상입니다"

③ 둘 다 PASS → DUT 로직 버그
   당신: "oled_ctrl.v의 FSM 로직에 버그가 있는 것 같아. 수정해줘"
   → rtl-designer가 수정
```

### 합성/Implementation FAIL

| 에러 | 이렇게 말하세요 |
|------|---------------|
| WNS < 0 (타이밍 위반) | "타이밍 분석해줘" → timing-analyst 에이전트 |
| Inferred latch | "래치 경고 수정해줘" → rtl-designer |
| Black box module | "run_synth.tcl에 소스 파일 추가해줘" |
| DRC VIOLATION | "DRC 위반 확인해줘" |

### 보드에서 동작 안 함

| 증상 | 이렇게 말하세요 |
|------|---------------|
| OLED 안 켜짐 | "핀 배치 다시 확인해줘" → pin-reviewer |
| FPGA에 연결 안 됨 | "Hardware Manager 열어줘" → vivado-gui |
| FPGA가 뜨거움 | 🔴 즉시 전원 차단! → "IOSTANDARD 전압 확인해줘" → pin-reviewer |

---

## 7. 자주 묻는 질문

### Q: 리뷰를 건너뛰고 바로 합성해도 되나요?

됩니다. `"합성해줘"` 라고 하면 스킬이 바로 실행됩니다.
하지만 리뷰를 거치면 다음을 사전에 방지할 수 있습니다:
- 합성 에러 (래치, 블랙박스 등)
- 시뮬레이션 실패 (TB 버그)
- 보드 손상 (IOSTANDARD 전압 불일치)

### Q: 스킬의 체크리스트를 수정할 수 있나요?

네. `.claude/skills/rtl-review/SKILL.md` 등의 마크다운 파일을 직접 편집하면 됩니다.
예를 들어 EtherCAT 프로젝트면 "EtherCAT 타이밍 체크" 항목을 추가할 수 있습니다.

### Q: 에이전트를 추가할 수 있나요?

네. `.claude/agents/` 폴더에 새 마크다운 파일을 만들면 됩니다.
예를 들어 `power-analyst.md` 를 만들어 전력 분석 전문가를 추가할 수 있습니다.

### Q: 보드를 바꾸면 뭘 해야 하나요?

1. `"보드를 Arty A7으로 바꿔줘"` → vivado-project 스킬이 boards.json 참조
2. `"핀 배치 확인해줘"` → pin-reviewer가 새 보드와 XDC 교차 검증
3. 이전 보드의 핀이 남아있으면 FAIL로 잡아냅니다.

### Q: GUI 없이도 전부 가능한가요?

네. 전체 플로우가 CLI에서 동작합니다.
GUI는 파형 디버깅, Device View 확인 등 "시각적으로 봐야 할 때"만 사용합니다.

### Q: WARN은 꼭 고쳐야 하나요?

아니요. WARN은 권장 사항입니다.
FAIL만 고치면 빌드가 가능합니다.
하지만 WARN을 고치면 코드 품질, 커버리지, 유지보수성이 올라갑니다.

### Q: KiCad 없이도 XDC를 만들 수 있나요?

네. KiCad→XDC 자동 생성은 선택 사항입니다.
KiCad가 없으면 rtl-designer 에이전트에게 `"XDC 파일도 만들어줘"`라고 하면 수동으로 작성해줍니다.
KiCad가 있으면 회로도를 원본으로 하여 XDC를 자동 생성하므로 핀 번호 오타 같은 실수를 원천 차단할 수 있습니다.

### Q: KiCad에서 XDC 생성 후 TODO가 남아있으면?

TODO는 뱅크 전압을 자동으로 결정할 수 없는 핀입니다.
두 가지 방법으로 해결합니다:
1. boards.json의 `bank_vcco`에 해당 뱅크 정보를 추가한 후 다시 생성
2. 패키지 핀아웃 파일에서 뱅크를 확인하고 XDC를 수동 수정

### Q: KiCad 회로도가 변경되면 XDC도 다시 만들어야 하나요?

네. `"KiCad에서 XDC 다시 만들어줘"` 하면 됩니다.
회로도가 핀 배치의 원본이므로, 회로도가 변경되면 XDC를 재생성하는 것이 안전합니다.

---

## 8. 부록: 전체 스킬/에이전트 카탈로그

### 에이전트 (6명) — 전문가

| 이름 | 핵심 질문 | 트리거 키워드 |
|------|----------|-------------|
| rtl-designer | "어떻게 설계할까?" | "모듈 만들어", "코드 작성" |
| rtl-reviewer | "합성 가능한가?" | "RTL 리뷰", "코드 리뷰", "린트" |
| tb-reviewer | "검증 충분한가?" (테스트벤치만 검토, DUT 로직은 rtl-reviewer 담당) | "TB 리뷰", "테스트벤치 리뷰", "커버리지" |
| pin-reviewer | "핀 배치 안전한가?" | "핀 확인", "XDC 리뷰", "IOSTANDARD" |
| timing-analyst | "타이밍 괜찮은가? 어떻게 개선할까?" | "타이밍 분석", "WNS", "타이밍 위반", "타이밍 최적화" |
| kicad-xdc-gen | "회로도에서 XDC 뽑을 수 있나?" | "KiCad XDC", "회로도에서 핀 배치", "넷리스트에서 XDC" |

### 스킬 (13개) — 절차서

| 이름 | 역할 | 트리거 키워드 |
|------|------|-------------|
| vivado-setup | 에이전트/환경 설치 | "vivado 설치", "vivado-setup", `/vivado-setup` |
| vivado-project | 프로젝트/보드 관리 | "프로젝트 만들어", "보드 바꿔" |
| vivado-sim | 시뮬레이션 | "시뮬레이션", "시뮬", "xsim" |
| vivado-synth | 합성 | "합성", "synth" |
| vivado-impl | Place & Route | "Implementation", "impl", "배치" |
| vivado-bitstream | Bitstream + 프로그래밍 | "비트스트림", "다운로드", "프로그래밍" |
| vivado-build-all | 전체 빌드 플로우 (합성→Impl→Bitstream) | "전체 빌드", "빌드 전부", "합성부터 비트스트림까지" |
| vivado-gui | GUI 전환 | "GUI 열어", "파형", "스키매틱", "Device View" |
| rtl-review | RTL 체크리스트 (32항목) | rtl-reviewer 에이전트가 참조 |
| tb-review | TB 체크리스트 (28항목) | tb-reviewer 에이전트가 참조 |
| pin-review | 핀 배치 체크리스트 (28항목) | pin-reviewer 에이전트가 참조 |
| kicad-xdc | KiCad→XDC 변환 규칙 | kicad-xdc-gen 에이전트가 참조 |
| kicad-review | KiCad 회로 종합 리뷰 | "KiCad 회로도 리뷰", "ERC" |

### 전체 플로우

```
[프로젝트 생성]  "프로젝트 만들어줘"
    │ 🔧 vivado-project 스킬
    ▼
[KiCad→XDC]  "KiCad에서 XDC 만들어줘" (선택)
    │ 👤 kicad-xdc-gen 에이전트
    │ KiCad 없으면 건너뛰기 — rtl-designer가 XDC 수동 작성
    ▼
[KiCad 회로 리뷰]  "KiCad 회로도 리뷰해줘" (선택)
    │ 🔧 kicad-review 스킬
    ▼
[RTL 설계]  "모듈 만들어줘"
    │ 👤 rtl-designer 에이전트
    ▼
[코드 리뷰]  "전체 리뷰해줘"
    │ 👤👤👤 rtl-reviewer + tb-reviewer + pin-reviewer (병렬)
    │ FAIL? → "수정해줘" → "다시 리뷰해줘"
    ▼ 모두 FAIL=0
[시뮬레이션]  "시뮬레이션 돌려줘"
    │ 🔧 vivado-sim 스킬
    │ FAIL? → "원인 찾아줘" → tb-reviewer → rtl-reviewer → rtl-designer
    ▼ PASS
[합성]  "합성해줘"
    │ 🔧 vivado-synth 스킬
    │ WNS < 0? → "타이밍 분석해줘" → 👤 timing-analyst
    ▼ WNS ≥ 0
[Implementation]  "impl 돌려줘"
    │ 🔧 vivado-impl 스킬
    ▼
[Bitstream]  "비트스트림 만들어줘"
    │ 🔧 vivado-bitstream 스킬
    ▼
[다운로드]  "FPGA에 다운로드해줘"
    │ 🔧 vivado-bitstream 스킬
    ▼
[동작 확인]

[GUI]  "파형 보여줘" / "스키매틱 보여줘" / ...
    🔧 vivado-gui 스킬 — 어느 단계에서든 사용 가능

🔧 = 스킬 (정해진 절차 실행)
👤 = 에이전트 (별도 컨텍스트에서 전문가 작업)
```

---

> **이 가이드는 Vivado + KiCad 스킬 패키지 v1.1.0 (6 에이전트 + 13 스킬)의 사용법을 설명합니다.**
> OLED 데모는 예시일 뿐이며, 같은 스킬/에이전트를 UART, SPI, I2C 등 
> 어떤 Verilog 프로젝트에든 동일하게 적용할 수 있습니다.
> KiCad 연동은 선택 사항이며, KiCad 없이도 전체 플로우가 동작합니다.
> 
> 체크리스트와 에이전트는 프로젝트 특성에 맞게 수정/추가할 수 있습니다.
> 상세 내용: `.claude/skills/스킬명/SKILL.md`, `.claude/agents/에이전트명.md`
