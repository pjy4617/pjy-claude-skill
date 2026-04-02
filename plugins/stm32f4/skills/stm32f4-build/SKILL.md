---
name: stm32f4-build
description: "STM32F4 펌웨어 빌드 실행. CubeMX/CubeIDE 프로젝트를 CMake+Ninja로 변환하여 빌드합니다. STM32CubeIDE 번들 툴체인(gnu-tools-for-stm32)을 자동 탐지하여 VS Code 환경에서 빌드합니다. '빌드해줘', '컴파일해줘', 'build', 'make', '펌웨어 빌드', 'cmake 빌드', '빌드 실행', 'STM32 빌드' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[debug|release] [--flash] [--clean]"
---

# STM32F4 펌웨어 빌드

## Overview

STM32F4 프로젝트를 CMake + Ninja로 빌드한다.
CubeMX/CubeIDE 프로젝트를 자동 감지하여 CMakeLists.txt를 생성하고, STM32CubeIDE 번들 툴체인으로 크로스 컴파일한다.

## 전제 조건

- **STM32CubeIDE 설치** (번들 툴체인 사용: cmake, ninja, arm-none-eabi-gcc)
- **VS Code** 에서 개발 (STM32CubeIDE는 툴체인 제공 용도)

---

## Phase 0: 환경 확인

### 0-1. STM32CubeIDE 번들 툴체인 탐지

아래 경로를 순서대로 탐색하여 STM32CubeIDE 번들 도구를 찾는다.

```bash
# Linux 기본 설치 경로
CUBE_IDE_PATHS=(
    "$HOME/st/stm32cubeide_*"
    "/opt/st/stm32cubeide_*"
    "/usr/local/st/stm32cubeide_*"
)
```

번들 내부 구조:
```
stm32cubeide_<version>/
├── plugins/
│   ├── com.st.stm32cube.ide.mcu.externaltools.cmake.linux64_*/tools/bin/cmake
│   ├── com.st.stm32cube.ide.mcu.externaltools.ninja.linux64_*/tools/bin/ninja
│   └── com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.*/tools/bin/arm-none-eabi-gcc
```

탐지 방법:
```bash
# cmake
CUBE_CMAKE=$(find "${CUBE_IDE_BASE}/plugins" -path "*/cmake.linux64_*/tools/bin/cmake" -type f 2>/dev/null | sort -V | tail -1)

# ninja
CUBE_NINJA=$(find "${CUBE_IDE_BASE}/plugins" -path "*/ninja.linux64_*/tools/bin/ninja" -type f 2>/dev/null | sort -V | tail -1)

# arm-none-eabi-gcc
CUBE_GCC=$(find "${CUBE_IDE_BASE}/plugins" -path "*/gnu-tools-for-stm32.*/tools/bin/arm-none-eabi-gcc" -type f 2>/dev/null | sort -V | tail -1)
```

찾은 경로를 환경변수로 설정:
```bash
export PATH="$(dirname $CUBE_CMAKE):$(dirname $CUBE_NINJA):$(dirname $CUBE_GCC):$PATH"
```

### 0-2. 폴백: 시스템 PATH

STM32CubeIDE가 없으면 시스템 PATH에서 찾는다:
```bash
which cmake && which ninja && which arm-none-eabi-gcc
```

### 0-3. 버전 확인 및 보고

```bash
cmake --version
ninja --version
arm-none-eabi-gcc --version | head -1
```

모든 도구가 없으면 **중단**하고 설치 안내:
```
❌ 빌드 도구를 찾을 수 없습니다.

필요한 도구:
  - arm-none-eabi-gcc (10.3+)
  - cmake (3.22+)
  - ninja (1.10+)

설치 방법:
  1. STM32CubeIDE 설치 (권장 — 모든 도구 번들)
     https://www.st.com/en/development-tools/stm32cubeide.html
  2. 또는 개별 설치:
     sudo apt install cmake ninja-build gcc-arm-none-eabi
```

---

## Phase 1: 프로젝트 감지 및 CMakeLists.txt 생성

프로젝트 루트에서 아래 순서로 빌드 시스템을 감지한다.

### 판별 로직

```
CMakeLists.txt 존재?
  ├─ YES → Phase 2로 진행 (기존 CMake 프로젝트)
  └─ NO → .cproject 존재?
       ├─ YES → 1-A: .cproject에서 CMakeLists.txt 생성
       └─ NO → Makefile 존재? (CubeMX 생성)
            ├─ YES → 1-B: Makefile에서 CMakeLists.txt 생성
            └─ NO → ❌ "빌드 가능한 프로젝트를 찾을 수 없습니다"
```

### 1-A: .cproject → CMakeLists.txt 변환

STM32CubeIDE 프로젝트(.cproject)에서 빌드 정보를 추출한다.

#### 추출 대상 (XML 파싱)

| 정보 | .cproject 내 위치 | 예시 |
|------|-------------------|------|
| MCU 디바이스 | `<option id="...mcu"` `value=` | `STM32F407VGTx` |
| MCU define | 디바이스명에서 도출 | `STM32F407xx` |
| 소스 디렉토리 | `<sourceEntries>` `<entry name=` | `Core`, `Drivers` |
| 인클루드 경로 | `<option>` `superClass="...include.paths"` | `Core/Inc`, `Drivers/...` |
| 전처리기 매크로 | `<option>` `superClass="...c.compiler.defs"` | `USE_HAL_DRIVER`, `STM32F407xx` |
| 링커 스크립트 | `<option>` `superClass="...linker.script"` | `STM32F407VGTX_FLASH.ld` |
| HAL 소스 경로 | 인클루드에서 추론 | `Drivers/STM32F4xx_HAL_Driver` |

#### 추출 방법 (grep 기반 — XML 파서 불필요)

```bash
# MCU 디바이스
MCU_DEVICE=$(grep -oP 'com\.st\.stm32cube\.ide\.mcu\.gnu\.managedbuild\.option\.target_mcu" value="\K[^"]+' .cproject)

# MCU define 도출: STM32F407VGTx → STM32F407xx
MCU_DEFINE=$(echo "$MCU_DEVICE" | sed -E 's/([A-Z0-9]+[0-9]{3})[A-Z0-9]+x?/\1xx/')

# 인클루드 경로 (../ 제거하여 상대경로로)
INCLUDES=$(grep -oP 'include\.paths.*?<listOptionValue.*?value="\K[^"]+' .cproject | sed 's|^\.\./||')

# 전처리기 매크로
DEFINES=$(grep -oP 'c\.compiler\.defs.*?<listOptionValue.*?value="\K[^"]+' .cproject)

# 링커 스크립트
LINKER_SCRIPT=$(grep -oP 'linker\.script" value="\K[^"]+' .cproject)
```

#### 소스 파일 수집

.cproject의 `<sourceEntries>`에서 소스 디렉토리를 파악하고, 실제 파일을 glob:
```bash
# C 소스
C_SOURCES=$(find Core/Src Drivers/ -name "*.c" 2>/dev/null)

# 스타트업 어셈블리
STARTUP=$(find . -name "startup_stm32f4*.s" 2>/dev/null | head -1)
```

#### CMakeLists.txt 생성

추출한 정보로 CMakeLists.txt를 생성한다. `stm32f4-firmware`의 `assets/templates/CMakeLists.txt.template`를 기반으로 플레이스홀더를 치환:

```
{{PROJECT_NAME}}   ← 프로젝트 디렉토리 이름
{{MCU_DEFINE}}     ← 추출한 MCU define
{{LINKER_SCRIPT}}  ← 추출한 링커 스크립트 경로
{{HAL_DRIVER_PATH}} ← 추출한 HAL 경로
{{STARTUP_FILE}}   ← 추출한 스타트업 파일
```

동시에 생성하는 파일:
- `cmake/gcc-arm-none-eabi.cmake` — 툴체인 파일
- `CMakePresets.json` — Ninja 기반 Debug/Release 프리셋

### 1-B: Makefile (CubeMX) → CMakeLists.txt 변환

CubeMX가 생성한 Makefile에서 빌드 정보를 추출한다.

#### CubeMX Makefile 구조

CubeMX Makefile은 정형화되어 있어 grep으로 파싱 가능:
```makefile
TARGET = project_name
C_SOURCES = Core/Src/main.c Core/Src/...
ASM_SOURCES = startup_stm32f407xx.s
C_DEFS = -DUSE_HAL_DRIVER -DSTM32F407xx
C_INCLUDES = -ICore/Inc -IDrivers/...
LDSCRIPT = STM32F407VGTx_FLASH.ld
```

#### 추출 방법

```bash
# 프로젝트 이름
TARGET=$(grep -m1 '^TARGET' Makefile | awk -F'= ' '{print $2}' | tr -d ' ')

# C 소스 (여러 줄에 걸쳐 \ 연결)
C_SOURCES=$(sed -n '/^C_SOURCES/,/^[^\\]/p' Makefile | grep -v '^C_SOURCES' | tr -d '\\' | tr '\n' ' ')

# ASM 소스
ASM_SOURCES=$(sed -n '/^ASM_SOURCES/,/^[^\\]/p' Makefile | grep -v '^ASM_SOURCES' | tr -d '\\' | tr '\n' ' ')

# 전처리기 매크로 (-D 제거)
C_DEFS=$(sed -n '/^C_DEFS/,/^[^\\]/p' Makefile | grep -oP '\-D\K\S+')

# 인클루드 경로 (-I 제거)
C_INCLUDES=$(sed -n '/^C_INCLUDES/,/^[^\\]/p' Makefile | grep -oP '\-I\K\S+')

# 링커 스크립트
LDSCRIPT=$(grep -m1 '^LDSCRIPT' Makefile | awk -F'= ' '{print $2}' | tr -d ' ')

# MCU define 추출
MCU_DEFINE=$(echo "$C_DEFS" | grep -oP 'STM32F4\w+')
```

#### CMakeLists.txt 생성

Makefile에서 추출한 C_SOURCES를 **명시적으로 나열** (GLOB 대신):
```cmake
set(C_SOURCES
    Core/Src/main.c
    Core/Src/stm32f4xx_it.c
    Core/Src/stm32f4xx_hal_msp.c
    # ... CubeMX Makefile에서 추출한 전체 목록
)
```

이유: CubeMX가 Makefile에 필요한 HAL 소스만 정확히 나열하므로, 이를 그대로 사용하는 것이 GLOB보다 정확하다.

동시에 생성하는 파일:
- `cmake/gcc-arm-none-eabi.cmake` — 툴체인 파일
- `CMakePresets.json` — Ninja 기반 Debug/Release 프리셋

### 1-C: 공통 — 생성 결과 보고

```
✅ CMakeLists.txt 생성 완료

소스: .cproject (STM32CubeIDE 프로젝트) | Makefile (CubeMX 프로젝트)
MCU: STM32F407VGTx (STM32F407xx)
링커: STM32F407VGTx_FLASH.ld
C 소스: 42개 파일
인클루드: 8개 경로

생성된 파일:
  ✅ CMakeLists.txt
  ✅ cmake/gcc-arm-none-eabi.cmake
  ✅ CMakePresets.json
```

---

## Phase 2: 빌드 실행

### 2-1. 빌드 타입 결정

| 인자 | 동작 |
|------|------|
| (없음) / `debug` | Debug 빌드 (-O0 -g3) |
| `release` | Release 빌드 (-Os -g0) |
| `--clean` | 빌드 디렉토리 삭제 후 재빌드 |
| `--flash` | 빌드 후 플래싱까지 실행 |

### 2-2. Clean (선택)

```bash
# --clean 옵션 시
rm -rf build/Debug   # 또는 build/Release
```

### 2-3. CMake Configure

```bash
cmake --preset debug    # 또는 release
```

에러 발생 시 로그를 분석하고 원인 보고:
- 툴체인 못 찾음 → Phase 0 재실행 안내
- 링커 스크립트 없음 → 경로 확인
- 소스 파일 없음 → CMakeLists.txt 확인

### 2-4. 빌드 실행

```bash
cmake --build --preset debug -- -j$(nproc)    # 또는 release
```

### 2-5. 빌드 에러 처리

빌드 실패 시 에러 메시지를 분석하여 분류:

| 에러 유형 | 원인 | 조치 |
|----------|------|------|
| `undefined reference` | 소스 누락 또는 링커 설정 | CMakeLists.txt에 소스 추가 |
| `No such file or directory` (헤더) | 인클루드 경로 누락 | CMakeLists.txt에 경로 추가 |
| `implicit declaration` | 헤더 미포함 | #include 추가 |
| `region 'FLASH' overflowed` | Flash 용량 초과 | -Os 최적화 또는 코드 축소 |
| `region 'RAM' overflowed` | SRAM 용량 초과 | 전역 변수 축소, 힙/스택 조정 |

**자동 수정 시도**: 에러가 CMakeLists.txt 설정 문제(소스/인클루드 누락)이면, 프로젝트 구조를 다시 스캔하여 CMakeLists.txt를 업데이트하고 재빌드한다. 최대 2회 재시도.

---

## Phase 3: 결과 리포트

### 3-1. 메모리 사용량 파싱

빌드 성공 시 `arm-none-eabi-size`와 링커의 `--print-memory-usage` 출력을 파싱:

```bash
arm-none-eabi-size build/Debug/*.elf
```

출력 예시:
```
   text    data     bss     dec     hex filename
  15284     120    1568   16972    424c project.elf
```

링커 메모리 사용량:
```
Memory region         Used Size  Region Size  %age Used
           FLASH:       15404 B         1 MB      1.47%
             RAM:        1688 B       128 KB      1.29%
```

### 3-2. 결과 보고서

```
═══════════════════════════════════════════
  STM32F4 빌드 결과
═══════════════════════════════════════════

MCU: STM32F407VGTx
빌드: Debug (-O0 -g3)
툴체인: arm-none-eabi-gcc 12.3.1 (STM32CubeIDE 번들)

결과: ✅ SUCCESS

메모리 사용량:
  FLASH:  15,404 / 1,048,576 bytes (1.5%)  ████░░░░░░░░░░░░░░░░
  RAM:     1,688 /   131,072 bytes (1.3%)  ████░░░░░░░░░░░░░░░░

산출물:
  ELF: build/Debug/project.elf (16,972 bytes)
  HEX: build/Debug/project.hex
  BIN: build/Debug/project.bin
  MAP: build/Debug/project.map

경고: 0개
에러: 0개
```

실패 시:
```
═══════════════════════════════════════════
  STM32F4 빌드 결과
═══════════════════════════════════════════

결과: ❌ FAILED

에러 (3개):
  1. Core/Src/main.c:45: undefined reference to 'HAL_SPI_Init'
     → CMakeLists.txt에 stm32f4xx_hal_spi.c 추가 필요
  2. Core/Src/codec.c:12: 'SPI_HandleTypeDef' undeclared
     → #include "stm32f4xx_hal_spi.h" 추가 필요
  3. ...

자동 수정 시도: CMakeLists.txt에 HAL SPI 소스 추가 후 재빌드...
```

---

## Phase 4: 플래싱 (--flash 옵션)

빌드 성공 후 `--flash` 옵션이 지정되면 플래싱을 실행한다.

### 4-1. 플래싱 도구 감지

우선순위:
1. **STM32CubeProgrammer CLI** (`STM32_Programmer_CLI`)
2. **OpenOCD** (`openocd`)

```bash
# STM32CubeProgrammer 탐지
PROGRAMMER=$(find "$HOME/st" "/opt/st" -name "STM32_Programmer_CLI" -type f 2>/dev/null | sort -V | tail -1)
# 없으면 시스템 PATH
[ -z "$PROGRAMMER" ] && PROGRAMMER=$(which STM32_Programmer_CLI 2>/dev/null)
# 없으면 OpenOCD 폴백
[ -z "$PROGRAMMER" ] && PROGRAMMER=$(which openocd 2>/dev/null)
```

### 4-2. 플래싱 실행

**STM32CubeProgrammer 사용 시:**
```bash
STM32_Programmer_CLI -c port=SWD freq=4000 -d build/Debug/project.bin 0x08000000 -v -rst
```

**OpenOCD 사용 시:**
```bash
openocd -f openocd.cfg -c "program build/Debug/project.bin verify reset exit 0x08000000"
```

### 4-3. 플래싱 결과

```
플래싱: ✅ SUCCESS
  도구: STM32CubeProgrammer 2.17.0
  대상: build/Debug/project.bin (15,284 bytes)
  주소: 0x08000000
  검증: PASS
  리셋: 완료
```

---

## 에러 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `cmake: command not found` | 툴체인 미설치 | STM32CubeIDE 설치 또는 `sudo apt install cmake` |
| `ninja: command not found` | Ninja 미설치 | STM32CubeIDE 설치 또는 `sudo apt install ninja-build` |
| `arm-none-eabi-gcc: not found` | 크로스 컴파일러 미설치 | STM32CubeIDE 설치 또는 `sudo apt install gcc-arm-none-eabi` |
| `No targets specified and no makefile found` | CMake configure 미실행 | `cmake --preset debug` 먼저 실행 |
| `FLASH overflowed` | Flash 용량 초과 | Release 빌드(`-Os`) 또는 미사용 코드 제거 |
| `RAM overflowed` | SRAM 부족 | 힙/스택 크기 조정, 전역 변수 축소 |
| `Error: unable to find ST-LINK` | 디버거 미연결 | USB 케이블 확인, `lsusb`로 ST-Link 확인 |
| `Error: init mode failed` | OpenOCD 프로브 설정 오류 | openocd.cfg의 interface/transport 확인 |

---

## stm32f4-firmware 스킬과의 연동

```
"STM32F407 펌웨어 만들어줘"
  → stm32f4-firmware 스킬이 코드 + 빌드 파일 생성 (Agent 1~4)
  → "빌드해줘"
  → stm32f4-build 스킬이 빌드 실행 (이 스킬)
  → "플래싱까지 해줘"
  → stm32f4-build --flash
```

CubeMX 프로젝트 활용:
```
CubeMX에서 .ioc로 프로젝트 생성 (Makefile 출력)
  → "빌드해줘"
  → stm32f4-build가 Makefile 감지 → CMakeLists.txt 자동 생성 → 빌드
```

STM32CubeIDE 프로젝트 활용:
```
STM32CubeIDE에서 .cproject 프로젝트 생성
  → VS Code에서 "빌드해줘"
  → stm32f4-build가 .cproject 감지 → CMakeLists.txt 자동 생성 → 빌드
```

$ARGUMENTS
