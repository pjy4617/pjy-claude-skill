## STM32F4 Firmware Project

### 빌드 환경 (기본)
- **STM32CubeIDE for VS Code** (ST 공식 VS Code 확장) — 기본 빌드 환경
  - STM32CubeIDE 번들 툴체인 자동 사용 (cmake, ninja, arm-none-eabi-gcc)
  - STM32CubeProgrammer 번들 포함 (플래싱)
  - 설치: VS Code Extensions에서 "STM32 VS Code Extension" 검색

### 최소 요구 버전
- STM32CubeIDE: 1.13 이상 (번들 툴체인 제공)
- Python: 3.6 이상 (KiCad XDC 생성 스크립트용)
- KiCad: 8.0 이상 (회로도 검증 사용 시, 선택 사항)
- Unity/FFF: 테스트 실행 시 자동 다운로드

### 환경
- IDE: VS Code + STM32CubeIDE for VS Code 확장 (기본)
- OS: Linux (Ubuntu/WSL)
- Language: C (C11)
- MCU: STM32F4 시리즈 (F401, F407, F411, F429, F446)
- 컴파일러: arm-none-eabi-gcc (STM32CubeIDE 번들)
- 빌드 시스템: CMake + Ninja (STM32CubeIDE 번들)
- 디버거: ST 공식 확장 (stlinkgdbtarget) 또는 cortex-debug + OpenOCD

### 디렉토리 규칙
- `Core/Inc/` `Core/Src/` — main, HAL 설정, 인터럽트 핸들러
- `Drivers/BSP/` — 보드 지원 패키지
- `Drivers/Device/` — 외부 디바이스 드라이버
- `Middlewares/` — USB, FatFS 등 미들웨어
- `Startup/` — 스타트업 어셈블리 (.s)
- `Linker/` — 링커 스크립트 (.ld)
- `cmake/` — CMake 툴체인 파일
- `test/` — 호스트 기반 단위 테스트 (Unity + FFF)
- `build/` — 빌드 출력 (git에 포함하지 않음)
- `.vscode/` — VS Code 디버그/빌드 설정

### 코딩 규칙
- 파일명: 소문자_스네이크 (예: `audio_codec.c`)
- 함수명: 모듈_동사_대상 PascalCase (예: `Codec_Init()`)
- 전역 변수: `g_` 접두사, 정적 변수: `s_` 접두사
- HAL 핸들: `h` + 페리페럴 (예: `hspi1`, `huart2`)
- HAL 반환값은 항상 검사
- 인터럽트 핸들러는 짧게 유지 (플래그만 세팅)
- 매직 넘버 금지 — 모든 상수는 `#define` 또는 `enum`

### 빌드 방법
```bash
# STM32CubeIDE for VS Code 환경 (기본)
# VS Code Tasks 또는 stm32f4-build 스킬 사용 권장
cmake --preset debug && cmake --build --preset debug

# 플래싱 (STM32CubeProgrammer CLI)
STM32_Programmer_CLI -c port=SWD -d build/Debug/project.bin 0x08000000 -v -rst

# 플래싱 (OpenOCD 폴백)
openocd -f openocd.cfg -c "program build/Debug/project.bin verify reset exit 0x08000000"

# 테스트 (호스트 기반)
cd test && make
```

### 에이전트/스킬 구성 (5 스킬 + 4 에이전트)
- 스킬: stm32f4-firmware, kicad-stm32-review, stm32f4-tdd, stm32f4-build, stm32f4-setup
- 에이전트: kicad-stm32-checker, stm32f4-test-writer, stm32f4-code-reviewer, stm32f4-qa

### 빌드 실행 (stm32f4-build 스킬)
- 프로젝트 자동 감지: .cproject (STM32CubeIDE) / Makefile (CubeMX) → CMakeLists.txt 자동 생성
- STM32CubeIDE 번들 툴체인 자동 탐지 (cmake, ninja, arm-none-eabi-gcc)
- 빌드: `cmake --preset debug && cmake --build --preset debug`
- 플래싱: STM32CubeProgrammer CLI 또는 OpenOCD
