# STM32F4 Firmware Skill & Agent 사용 가이드 (v1.1.0)

## 1. 개요

이 플러그인은 STM32F4 시리즈 MCU(F401/F407/F411/F429/F446) 펌웨어를 **4개 스킬 + 4개 에이전트**로 개발한다.

```
스킬 4개 (절차서)                    에이전트 4명 (전문가)
──────────────                      ─────────────────
stm32f4-firmware  5단계 파이프라인    kicad-stm32-checker    회로도 검증
kicad-stm32-review  회로도 체크리스트  stm32f4-test-writer    테스트 작성
stm32f4-tdd       호스트 기반 TDD    stm32f4-code-reviewer  코드 리뷰
stm32f4-setup     환경 초기 설정     stm32f4-qa             QA 최종검수
```

## 2. 설치

```bash
# 1. 마켓플레이스 추가 (한 번만)
/plugin marketplace add pjy4617/pjy-claude-skill

# 2. STM32F4 플러그인 설치 → 4개 스킬 활성화
/plugin install stm32f4@pjy-skills

# 3. 에이전트 + CLAUDE.md + 디렉토리 설치 (최초 1회)
/stm32f4-setup
```

셋업 시 프로젝트 경로를 질문합니다:
```
> STM32F4 프로젝트를 설치할 경로를 알려주세요.
> (엔터만 누르면 현재 디렉토리에 설치합니다)
```

지정한 경로에 에이전트, CLAUDE.md, 디렉토리 구조(`Core/`, `Drivers/`, `Middlewares/`, `Startup/`, `Linker/`, `build/`)가 생성됩니다.

## 3. 플러그인 구조

```
plugins/stm32f4/
├── skills/
│   ├── stm32f4-firmware/              # 5단계 에이전트 파이프라인
│   │   ├── SKILL.md
│   │   ├── references/ (7개)
│   │   │   ├── peripheral-patterns.md # SPI, I2C, UART, USB, DMA, TIM, ADC 등
│   │   │   ├── coding-rules.md        # 네이밍, HAL 가이드, 크리티컬 섹션
│   │   │   ├── architecture-patterns.md # 레이어, FSM, RTOS 패턴
│   │   │   ├── pin-validation.md      # 7단계 핀 검증 체크리스트
│   │   │   ├── mcu-selection.md       # MCU 비교, 클럭 패턴
│   │   │   ├── production-checklist.md # Watchdog, BOR, RDP, 부트로더
│   │   │   └── debugging-guide.md     # HardFault, SWO, GDB
│   │   └── assets/templates/ (8개)
│   │       ├── CMakeLists.txt.template
│   │       ├── CMakePresets.json.template
│   │       ├── cmake/gcc-arm-none-eabi.cmake.template
│   │       ├── Makefile.template
│   │       ├── linker_script.ld.template
│   │       ├── openocd.cfg.template
│   │       └── vscode/launch.json.template, tasks.json.template
│   ├── kicad-stm32-review/           # 회로도 검증 체크리스트 (42항목)
│   │   └── SKILL.md
│   ├── stm32f4-tdd/                  # 호스트 기반 TDD (Unity + FFF)
│   │   └── SKILL.md
│   └── stm32f4-setup/                # 환경 초기 설정
│       └── SKILL.md
├── agents/
│   ├── kicad-stm32-checker.md         # 회로도 검증 전문가
│   ├── stm32f4-test-writer.md         # 테스트 코드 작성 전문가
│   ├── stm32f4-code-reviewer.md       # 소스코드 리뷰 전문가
│   └── stm32f4-qa.md                  # QA 최종검수 전문가
├── claude-md/
│   └── CLAUDE.md                      # 프로젝트 설정 템플릿
└── docs/
    └── USAGE_GUIDE.md                 # 이 파일
```

## 4. 에이전트 파이프라인 (stm32f4-firmware)

```
[Agent 1] → [Agent 2] → [Agent 3] → [Agent 4] → [Agent 5]
 요구사항     아키텍처     코드생성     빌드구성     검토
    ▲            ▲           ▲            ▲          │
    └──────── ERROR 시 해당 에이전트로 되돌아감 ──────┘
```

### Agent 1: Requirements Analyzer
- 사용자 요청에서 MCU, 주변장치, 클럭, 메모리, 외부 디바이스를 추출
- **질문 프로토콜**: 정보 부족 시 우선순위대로 질문
  (MCU → HSE → 외부IC → 핀 제약 → 전압 → **빌드 시스템** → **디버그 프로브**)
- MCU 자동 선정: `references/mcu-selection.md` 기반

### Agent 2: Architecture Designer
- Bare-metal vs RTOS 판단 (동시 작업 수, 실시간 제약 차이 기준)
- 레이어 구조, 모듈 분할, 데이터 흐름, 인터럽트 맵, 상태 머신 설계

### Agent 3: Code Generator
- 아키텍처 기반 전체 소스코드 생성 (.c/.h)
- 참조: `peripheral-patterns.md`, `coding-rules.md`

### Agent 4: Build System Generator
- **CMake** (기본, ST 공식 권장) 또는 **Makefile** (대안)
- 링커 스크립트, OpenOCD, VS Code 설정 (cortex-debug + ST 공식 확장)
- 디버그 프로브별 transport 자동 설정 (ST-Link v2/v3, J-Link, CMSIS-DAP)
- 최적화: Debug `-O0 -g3`, Release `-Os -g0`

### Agent 5: Code Reviewer
- **7개 검증 카테고리** 수행 (5-A ~ 5-G)
- 5-A 핀 검증이 최우선 (7단계 체크리스트)
- 5-G 단위 테스트 확인 (test/ 존재 시 실행)
- 검토 결과: OK / WARN / ERROR → ERROR 시 피드백 루프 (최대 3회)

## 5. 전체 워크플로우

```
[환경 설정]
  /stm32f4-setup → 에이전트 + CLAUDE.md 설치

[KiCad 회로도 검증] (선택, KiCad 회로도가 있을 때)
  "KiCad STM32 검토해줘"
    → kicad-stm32-review 스킬 (42항목 체크리스트)
    → kicad-stm32-checker 에이전트가 검증 수행
    → ERROR=0 확인

[펌웨어 생성]
  "STM32F407로 SPI 코덱 펌웨어 만들어줘"
    → stm32f4-firmware 스킬 (Agent 1→2→3→4→5)
    → 코드 + 빌드 시스템 + VS Code 설정 생성

[테스트 추가]
  "테스트 추가해줘" 또는 "TDD로 드라이버 만들어줘"
    → stm32f4-tdd 스킬
    → stm32f4-test-writer 에이전트가 Unity+FFF 테스트 생성
    → cd test && make → PASS 확인

[코드 리뷰]
  "코드 리뷰해줘"
    → stm32f4-code-reviewer 에이전트가 34항목 체크리스트 검증
    → 6카테고리: HAL 안전성, 인터럽트 안전성, 아키텍처 규칙, 네이밍, 메모리 안전성, 양산 준비도
    → 항목별 OK / WARN / ERROR 판정

[QA 최종검수]
  "릴리스 확인" 또는 "QA 검수해줘"
    → stm32f4-qa 에이전트가 최종검수 수행
    → 필수 게이트 6개 + 권고 5개 검증
    → PASS / CONDITIONAL / REJECT 3단계 판정

[빌드 & 플래싱]
  cmake --preset debug && cmake --build --preset debug
  make flash
```

## 6. 사용 예시

### 기본 사용 (한 번에 전체 생성)
```
"STM32F407VGT6으로 SPI1에 VS1053B 오디오 코덱을 연결하고,
 USB OTG FS로 WAV 파일을 받아 내부 Flash에 저장 후 재생하는 펌웨어"
```
→ 5단계 에이전트 순차 실행 → Agent 5에서 핀 검증 → 문제 발견 시 자동 수정

### MCU 미지정 시
```
"SPI 센서 3개와 UART 디버그를 사용하는 데이터 수집 펌웨어"
```
→ Agent 1이 mcu-selection.md 참조 → "F411 추천" → 사용자 확인 요청

### KiCad 회로도 검증 후 펌웨어 생성
```
"KiCad 회로도 핀 확인해줘"
→ 42항목 검증 → ERROR=0
"이 회로도 기반으로 펌웨어 만들어줘"
→ 회로도의 핀 할당을 그대로 사용하여 코드 생성
```

### TDD로 드라이버 개발
```
"TDD로 SPI 코덱 드라이버 만들어줘"
→ 실패하는 테스트 먼저 작성 (Red)
→ 최소 구현 (Green)
→ 리팩토링 (Refactor)
```

### 코드 리뷰
```
"코드 리뷰해줘"
→ stm32f4-code-reviewer 에이전트가 34항목 체크리스트 검증
→ HAL 안전성, 인터럽트 안전성, 아키텍처 규칙, 네이밍, 메모리 안전성, 양산 준비도
→ 항목별 OK / WARN / ERROR 판정 + 수정 제안
```

### QA 최종검수 (릴리스 전)
```
"릴리스 확인" 또는 "QA 검수해줘"
→ stm32f4-qa 에이전트가 필수 게이트 6개 + 권고 5개 검증
→ PASS: 릴리스 가능 / CONDITIONAL: 조건부 승인 / REJECT: 릴리스 불가
```

## 7. 참조 문서 활용표

| 에이전트/스킬 | 참조 문서 | 언제 읽는가 |
|--------------|-----------|------------|
| Agent 1 | mcu-selection.md | MCU 미지정 또는 칩 비교 필요 시 |
| Agent 2 | architecture-patterns.md | 항상 (RTOS 판단, 레이어, 패턴) |
| Agent 3 | peripheral-patterns.md | 주변장치 코드 생성 시 |
| Agent 3 | coding-rules.md | 항상 (네이밍, 에러 처리, 크리티컬 섹션) |
| Agent 4 | assets/templates/ | 항상 (CMake, Makefile, 링커, OpenOCD, VS Code) |
| Agent 5 | pin-validation.md | 항상 (7단계 핀 검증 필수) |
| Agent 5 | production-checklist.md | 프로덕션 빌드 검토 시 |
| kicad-stm32-review | pin-validation.md | 회로도 검증 시 |
| stm32f4-tdd | coding-rules.md | 테스트 코드 네이밍 시 |
| stm32f4-code-reviewer | coding-rules.md, architecture-patterns.md, production-checklist.md | 코드 리뷰 시 (34항목 6카테고리) |
| stm32f4-qa | production-checklist.md, pin-validation.md | QA 최종검수 시 (필수 게이트 6개 + 권고 5개) |
| 개발자 | debugging-guide.md | HardFault, 디버깅 문제 시 |

## 8. 제한사항

- STM32 HAL 라이브러리 소스는 포함하지 않음 — STM32CubeF4 패키지 별도 필요
- USB/FatFS 미들웨어도 CubeF4에서 복사 필요
- 이 스킬은 코드 생성에 초점 — 실제 컴파일은 arm-none-eabi-gcc + CMake/Ninja 환경 필요
- RTOS 태스크 설계는 가이드라인 제공 수준 — FreeRTOS 커널 소스는 미포함
- 호스트 기반 테스트는 로직만 검증 — 하드웨어 타이밍/인터럽트는 실제 MCU에서 확인 필요
- KiCad 회로도 검증은 kicad-cli 설치 시 정확도가 높음 (없으면 직접 파싱, 정확도 제한)
