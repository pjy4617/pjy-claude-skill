---
name: wmx3-build
description: "WMX3 모듈 CMake 빌드 실행 및 결과 확인. OS 자동 감지 후 적절한 프리셋으로 빌드한다. '빌드', 'build', '컴파일', 'cmake', 'make', 'wmx3 빌드해줘', '빌드 실행', 'cmake 빌드' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
argument-hint: "[프리셋명]"
---

# WMX3 모듈 CMake 빌드

> 이 스킬은 CMake 프리셋 기반 빌드를 실행합니다.
> 빌드 에러 발생 시 **wmx3-build-checker 에이전트**에게 분석을 위임합니다.

## CMakePresets.json 프리셋 목록

| 프리셋명 | 설명 | OS | 빌드 디렉토리 |
|---------|------|-----|--------------|
| `linux-release` | Linux GCC Release | Linux | `build-linux-release/` |
| `linux-debug` | Linux GCC Debug (디버그 심볼 포함) | Linux | `build-linux-debug/` |
| `linux-relwithdebinfo` | Linux GCC RelWithDebInfo | Linux | `build-linux-relwithdebinfo/` |
| `linux-xenomai` | Linux Xenomai RTOS Release | Linux | `build-linux-xenomai/` |
| `windows` | Windows VS2022 (v110 toolset, RTX64 4.x) | Windows | `build-windows/` |

> **참고**: `windows` 프리셋은 `hostSystemName == Windows` 조건에서만 활성화됩니다.
> Claude Code는 Linux 환경에서 실행되므로 Windows 빌드는 직접 실행 불가합니다.

---

## 워크플로우

### 1단계: OS 자동 감지

```bash
uname -s
```

- `Linux` → Linux 빌드 직접 실행
- `Windows_NT` (또는 Windows) → 빌드 명령 안내만 제공

### 2단계-A: Linux 빌드 실행

인수로 프리셋명이 주어지지 않으면 `linux-release`를 기본값으로 사용합니다.

```bash
# 환경변수 설정 확인
echo "LMX_INSTALLER_ROOT=${LMX_INSTALLER_ROOT}"

# CMake 구성
cmake --preset linux-release

# 빌드 실행 (병렬 빌드)
cmake --build --preset linux-release --parallel
```

빌드 성공 확인:
```bash
# 공유 라이브러리 (.so) 확인
find build-linux-release -name "*.so" -type f

# 정적 라이브러리 (.a) 확인
find build-linux-release -name "*.a" -type f
```

### 2단계-B: Windows 빌드 안내

Claude Code는 Linux 환경에서 실행되므로, Windows 빌드는 Windows 머신에서 직접 실행해야 합니다.

```powershell
# Windows PowerShell / VS Developer Command Prompt
cmake --preset windows
cmake --build --preset windows-release
```

또는 Visual Studio 솔루션 파일을 직접 열어서 빌드합니다:
```
build-windows/모듈명.sln
```

### 3단계: 빌드 에러 처리

빌드 중 에러가 발생하면 **wmx3-build-checker 에이전트**에게 위임합니다:
- 전체 빌드 로그 전달
- 에러 메시지 + 소스 파일 위치 전달
- 수정 방안 제안 수신 후 적용

### 4단계: 빌드 결과 보고

```
빌드 완료!

프리셋: linux-release
빌드 디렉토리: build-linux-release/

생성된 파일:
  ✅ build-linux-release/libapibuffer.so      (Core RTDLL)
  ✅ build-linux-release/libapibufferapi.a    (C++ API)

빌드 시간: N초
경고 수: N개
```

---

## 환경변수 설정 가이드

WMX3 모듈 빌드에 필요한 환경변수:

```bash
# WMX3/IMLib 설치 루트 (필수)
export LMX_INSTALLER_ROOT=/opt/lmx

# OSL 타입 (rt: 실시간, xeno: Xenomai) — CMakePresets.json에서 자동 설정
# export OSL_TYPE=rt

# 빌드 후 환경변수 확인
echo "LMX_INSTALLER_ROOT=${LMX_INSTALLER_ROOT}"
```

`LMX_INSTALLER_ROOT`가 미설정된 경우 빌드 전에 경고를 표시하고 설정 방법을 안내합니다.

---

## 자주 사용하는 빌드 명령

```bash
# Release 빌드 (기본)
cmake --preset linux-release && cmake --build --preset linux-release

# Debug 빌드 (gdb 디버깅용)
cmake --preset linux-debug && cmake --build --preset linux-debug

# 특정 타겟만 빌드
cmake --build --preset linux-release --target ApiBuffer

# 빌드 디렉토리 초기화 후 재빌드
rm -rf build-linux-release && cmake --preset linux-release && cmake --build --preset linux-release

# Xenomai RTOS용 빌드
cmake --preset linux-xenomai && cmake --build --preset linux-xenomai
```

$ARGUMENTS
