# pjy-claude-skill

Claude Code 플러그인 마켓플레이스 — 하드웨어 개발을 위한 스킬 & 에이전트 모음

> **"말하면 만들어 준다"** — FPGA 설계부터 MCU 펌웨어까지, Claude Code에서 자연어로 하드웨어 프로젝트를 개발합니다.

---

## 포함된 플러그인

<table>
<tr>
<td align="center" width="50%">
<img src="assets/mascot-vivado.png" width="280" alt="Vivado Mascot"><br>
<b>Vivado FPGA</b><br>
RTL 설계 → 시뮬레이션 → 합성 → Bitstream<br>
12 스킬 + 6 에이전트
</td>
<td align="center" width="50%">
<img src="assets/mascot-stm32f4.png" width="280" alt="STM32F4 Mascot"><br>
<b>STM32F4 Firmware</b><br>
5단계 파이프라인 + KiCad 검증 + TDD<br>
4 스킬 + 2 에이전트
</td>
</tr>
</table>

---

## 스킬과 에이전트란?

Claude Code를 처음 사용한다면, 먼저 이 개념을 이해하세요.

### 스킬 = 작업 절차서

스킬은 Claude에게 **"이 작업은 이 순서로 해라"**라고 알려주는 레시피입니다.
사용자가 `/스킬명` 으로 직접 호출하거나, 대화 내용에 따라 자동으로 트리거됩니다.

```
사용자: "합성해줘"
Claude: (vivado-synth 스킬을 로드하고 정해진 TCL 절차를 실행)
```

### 에이전트 = 전문가

에이전트는 **별도 컨텍스트에서 독립적으로 작업하는 전문가**입니다.
메인 대화를 오염시키지 않고, 결과만 돌려줍니다.

```
사용자: "전체 리뷰해줘"
Claude: (RTL 리뷰어 + TB 리뷰어 + 핀 리뷰어 3명이 병렬로 작업 → 결과만 반환)
```

### 차이 한눈에 보기

| | 스킬 | 에이전트 |
|---|---|---|
| **비유** | 요리 레시피 | 전문 셰프 |
| **동작** | Claude가 레시피 보고 직접 실행 | 별도 전문가가 독립 작업 후 결과만 전달 |
| **언제 사용** | 정해진 절차가 있을 때 | 전문적 판단이 필요할 때 |

**사용할 때 구분할 필요 없습니다.** 원하는 것을 말하면 Claude가 알아서 판단합니다.

---

## 사전 준비

### 필수

- [Claude Code](https://claude.ai/code) 설치 및 실행 가능
- 터미널에서 `claude` 명령어 실행 가능

### 플러그인별 추가 요구사항

<details>
<summary><b>Vivado 플러그인</b></summary>

- AMD Vivado 2020.1 이상 (CLI batch 모드 지원)
- Linux 환경 (Ubuntu 20.04+, WSL2 포함)
- FPGA 보드 (시뮬레이션만 하면 보드 없이도 가능)
- KiCad 8.0+ (KiCad→XDC 자동 생성 사용 시, 선택 사항)

</details>

<details>
<summary><b>STM32F4 플러그인</b></summary>

- arm-none-eabi-gcc 10.3 이상
- CMake 3.22 이상 + Ninja 1.10 이상 (CMake 빌드 사용 시)
- OpenOCD 0.11 이상 (또는 ST-LINK GDB Server)
- Linux 환경 (Ubuntu 20.04+, WSL2 포함)
- KiCad 8.0+ (회로도 검증 사용 시, 선택 사항)

</details>

---

## 설치 방법 (초보자 가이드)

### Step 1: 마켓플레이스 추가

Claude Code 터미널에서 다음을 입력합니다. **한 번만 하면 됩니다.**

```
/plugin marketplace add pjy4617/pjy-claude-skill
```

이렇게 하면 이 저장소가 마켓플레이스로 등록됩니다.

### Step 2: 원하는 플러그인 설치

#### Vivado (FPGA 개발) 설치

```
/plugin install vivado@pjy-skills
```

12개 스킬이 한 번에 활성화됩니다. 이후 에이전트를 설치합니다:

```
/vivado-setup
```

이 명령은 6개 에이전트를 `.claude/agents/`에 복사하고, 프로젝트 설정(CLAUDE.md)을 추가합니다.

#### STM32F4 (MCU 펌웨어) 설치

```
/plugin install stm32f4@pjy-skills
```

4개 스킬이 한 번에 활성화됩니다. 이후 에이전트를 설치합니다:

```
/stm32f4-setup
```

이 명령은 2개 에이전트를 `.claude/agents/`에 복사하고, 프로젝트 설정(CLAUDE.md)을 추가합니다.

#### 둘 다 설치

```
/plugin install vivado@pjy-skills
/plugin install stm32f4@pjy-skills
```

각 플러그인은 독립적이므로 원하는 것만 설치할 수 있습니다.

### Step 3: 설치 확인

설치가 잘 되었는지 확인하려면:

```
/plugin list
```

설치된 스킬이 표시되면 성공입니다.

---

## 사용법

### <img src="assets/mascot-vivado.png" width="48" align="center"> Vivado 플러그인 — 이렇게 말하면 됩니다

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|---------------------|
| 프로젝트 생성 | "ZedBoard용 OLED 프로젝트 만들어줘" | vivado-project 스킬 |
| RTL 설계 | "SPI 제어 Verilog 모듈 만들어줘" | rtl-designer 에이전트 |
| 코드 리뷰 | "전체 리뷰해줘" | 3개 에이전트 병렬 (RTL+TB+Pin) |
| 시뮬레이션 | "시뮬레이션 돌려줘" | vivado-sim 스킬 |
| 합성 | "합성해줘" | vivado-synth 스킬 |
| Implementation | "impl 돌려줘" | vivado-impl 스킬 |
| Bitstream | "비트스트림 만들어줘" | vivado-bitstream 스킬 |
| 타이밍 문제 | "타이밍 분석해줘" | timing-analyst 에이전트 |
| GUI 확인 | "파형 보여줘" / "스키매틱 보여줘" | vivado-gui 스킬 |
| KiCad→XDC | "KiCad에서 XDC 만들어줘" | kicad-xdc-gen 에이전트 |
| 전체 빌드 | "합성부터 비트스트림까지 돌려줘" | vivado-build-all 스킬 |

#### Vivado 전체 워크플로우

```
"프로젝트 만들어줘"           ← vivado-project 스킬
    ↓
"모듈 만들어줘"               ← rtl-designer 에이전트
    ↓
"전체 리뷰해줘"               ← 3개 에이전트 병렬 검사
    ↓ (FAIL=0 될 때까지 반복)
"시뮬레이션 돌려줘"           ← vivado-sim 스킬
    ↓
"합성해줘"                    ← vivado-synth 스킬
    ↓
"impl 돌려줘"                 ← vivado-impl 스킬
    ↓
"비트스트림 만들어줘"         ← vivado-bitstream 스킬
    ↓
"FPGA에 다운로드해줘"         ← vivado-bitstream 스킬
```

---

### <img src="assets/mascot-stm32f4.png" width="48" align="center"> STM32F4 플러그인 — 이렇게 말하면 됩니다

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|---------------------|
| 펌웨어 생성 | "STM32F407로 SPI 코덱 펌웨어 만들어줘" | stm32f4-firmware 스킬 (5단계 파이프라인) |
| 회로도 검증 | "KiCad STM32 검토해줘" | kicad-stm32-review 스킬 + checker 에이전트 |
| 테스트 추가 | "테스트 추가해줘" | stm32f4-tdd 스킬 + test-writer 에이전트 |
| TDD 개발 | "TDD로 SPI 드라이버 만들어줘" | test-writer가 Red→Green→Refactor |

#### STM32F4 전체 워크플로우

```
"KiCad STM32 검토해줘"        ← 회로도 핀 검증 (42항목), KiCad가 있을 때
    ↓ (ERROR=0 확인)
"이 회로도 기반으로 펌웨어 만들어줘"
    ↓
  Agent 1: 요구사항 분석      ← MCU, 클럭, 페리페럴, 핀 추출
  Agent 2: 아키텍처 설계      ← Bare-metal vs RTOS 판단
  Agent 3: 코드 생성          ← HAL 기반 소스코드
  Agent 4: 빌드 구성          ← CMake/Makefile + 링커 + OpenOCD + VS Code
  Agent 5: 코드 검토          ← 7개 카테고리 검증 (핀, 클럭, 메모리, 테스트 등)
    ↓ (ERROR → 해당 에이전트로 되돌아가 수정, 최대 3회)
"테스트 추가해줘"             ← Unity + FFF 호스트 기반 단위 테스트
    ↓
  cd test && make             ← PC에서 테스트 실행
```

#### 펌웨어 생성 시 Claude가 물어보는 것들

정보가 부족하면 Claude가 순서대로 질문합니다:

1. **MCU** — "어떤 STM32F4 칩을 사용하시나요?" (미지정 시 자동 추천)
2. **HSE 주파수** — "외부 크리스탈이 몇 MHz인가요?" (기본: 8MHz)
3. **외부 IC** — "연결할 IC의 정확한 모델명은?" (필수 질문)
4. **핀 제약** — "사용할 수 없는 핀이 있나요?" (기본: 없음)
5. **전원 전압** — "3.3V인가요?" (기본: 3.3V)
6. **빌드 시스템** — "CMake? Makefile?" (기본: CMake)
7. **디버그 프로브** — "ST-Link v2? v3? J-Link?" (기본: ST-Link v2)

전부 답하지 않아도 됩니다. 미답변 항목은 기본값을 사용하고, 기본값 사용 사실을 명시합니다.

---

## 리뷰 결과 읽는 법

Vivado와 STM32F4 모두 동일한 3단계 등급을 사용합니다:

| 등급 | 의미 | 조치 |
|------|------|------|
| **ERROR** | 반드시 수정해야 함. 동작 불가 또는 하드웨어 손상 위험 | "FAIL 항목 수정해줘" |
| **WARN** | 동작은 하지만 잠재적 문제. 권장 수정 | 지금 안 고쳐도 됨 |
| **OK** / **PASS** | 이상 없음 | 다음 단계로 진행 |

리뷰에서 ERROR가 나오면:

```
사용자: "FAIL 항목 전부 수정해줘"
(수정 후)
사용자: "다시 리뷰해줘"
(FAIL=0이 될 때까지 반복)
```

---

## 지원하는 MCU / FPGA

### STM32F4 시리즈

| MCU | 최대 클럭 | Flash | 특징 |
|-----|----------|-------|------|
| F401 | 84MHz | 256KB | 최저가, USB, SPI4 |
| F411 | 100MHz | 512KB | 저가+USB, SPI3/4/5, SDIO |
| F407 | 168MHz | 1MB | 기준 MCU, CAN, ETH, DAC |
| F429 | 168MHz | 2MB | LCD(LTDC), FMC, Dual Bank Flash |
| F446 | 180MHz | 512KB | 최고 클럭, QUADSPI, SAI, FMPI2C |

각 MCU별로 **공식 데이터시트 기반 AF 매핑 JSON**이 포함되어 있어, 핀 검증 시 타겟 MCU에 맞는 정확한 검증이 이루어집니다.

### Vivado FPGA

boards.json에 등록된 보드를 지원합니다 (Arty A7, ZedBoard 등). 보드 추가도 가능합니다.

---

## 폴더 구조

```
pjy-claude-skill/
├── .claude-plugin/
│   └── marketplace.json           ← 마켓플레이스 카탈로그
├── plugins/
│   ├── vivado/                    ← Vivado FPGA 플러그인
│   │   ├── plugin.json
│   │   ├── skills/ (12개)         ← 스킬 (SKILL.md + 보조 파일)
│   │   ├── agents/ (6개)          ← 에이전트 (.md)
│   │   ├── claude-md/             ← 프로젝트 CLAUDE.md 템플릿
│   │   ├── templates/             ← 예제 RTL/TB/XDC
│   │   └── docs/                  ← 사용 가이드
│   └── stm32f4/                   ← STM32F4 MCU 플러그인
│       ├── plugin.json
│       ├── skills/ (4개)
│       │   ├── stm32f4-firmware/  ← 5단계 파이프라인
│       │   │   ├── references/    ← 7개 참조 문서
│       │   │   ├── references/af-tables/  ← 5개 MCU AF 매핑 JSON
│       │   │   └── assets/templates/      ← 8개 빌드 템플릿
│       │   ├── kicad-stm32-review/        ← 회로도 검증 (42항목)
│       │   ├── stm32f4-tdd/              ← TDD (Unity+FFF)
│       │   └── stm32f4-setup/            ← 환경 설정
│       ├── agents/ (2개)
│       ├── claude-md/
│       └── docs/
├── CLAUDE.md
├── README.md
└── .gitignore
```

---

## 자주 묻는 질문

### Q: 스킬을 하나만 설치할 수 있나요?

마켓플레이스 단위로 설치됩니다. `vivado` 플러그인을 설치하면 12개 스킬이 모두 활성화됩니다. 개별 스킬만 설치하는 것은 지원하지 않지만, 사용하지 않는 스킬은 트리거되지 않으므로 문제없습니다.

### Q: Vivado와 STM32F4를 동시에 설치해도 되나요?

네. 각 플러그인은 완전히 독립적입니다.

### Q: 스킬/에이전트를 수정할 수 있나요?

네. 설치 후 `.claude/skills/` 또는 `.claude/agents/` 디렉토리의 마크다운 파일을 직접 편집하면 됩니다. 예를 들어 체크리스트에 프로젝트 특화 항목을 추가할 수 있습니다.

### Q: 업데이트는 어떻게 하나요?

```
/plugin marketplace update pjy-skills
```

### Q: Windows에서도 사용할 수 있나요?

WSL2 환경에서 사용할 수 있습니다. 네이티브 Windows는 Vivado CLI와 arm-none-eabi-gcc의 경로 설정이 필요합니다.

### Q: KiCad가 없어도 되나요?

네. KiCad 관련 스킬(회로도 검증, XDC 생성)은 선택 사항입니다. KiCad가 없으면 해당 스킬이 트리거되지 않습니다.

---

## 상세 가이드

각 플러그인의 상세 사용법은 아래 문서를 참고하세요:

- **Vivado**: [`plugins/vivado/docs/Vivado-스킬-에이전트-사용가이드.md`](plugins/vivado/docs/Vivado-스킬-에이전트-사용가이드.md)
- **STM32F4**: [`plugins/stm32f4/docs/USAGE_GUIDE.md`](plugins/stm32f4/docs/USAGE_GUIDE.md)

---

## 라이선스

MIT License
