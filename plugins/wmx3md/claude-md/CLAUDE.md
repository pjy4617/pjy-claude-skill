## WMX3 Motion Control Module Project

### 최소 요구 버전
- GCC/G++: 9.0 이상 (C99 + C++11 지원)
- CMake: 3.16 이상
- Ninja: 1.10 이상
- WMX3 SDK (`LMX_INSTALLER_ROOT` 환경변수 설정 필요)
- GoogleTest: v1.14.0 (FetchContent로 자동 다운로드)

### 환경
- OS: Linux (RT 커널 / Xenomai) 또는 Windows (RTX64 4.x / Standard)
- Language: C99 (Layer 1 Core RTDLL), C++11 (Layer 2 API), C++/CLI (Layer 3 CLR — Windows 전용)
- 빌드 시스템: CMake + Ninja
- 테스트: GoogleTest (gtest) + GoogleMock (gmock)

### 3계층 아키텍처

```
사용자 애플리케이션 (C++ / C# / VB.NET)
        ↓ C++ 링크                    ↓ .NET 참조
Layer 2: <ModuleName>Api             Layer 3: <ModuleName>Api_CLRLib
(C++11 정적 라이브러리, wmx3Api)       (C++/CLI .NET 래퍼, Windows 전용)
        ↓ IPC 통신 (IMDll 경유, 공유 메모리 / 명령 큐)
═════════════════ 실시간 경계 ═════════════════
        ↓
Layer 1: <ModuleName> (Core RTDLL/SO, C99)
  WMX3 엔진이 dlopen으로 로딩.
  매 제어 사이클마다 Motion_Process() 호출.
        ↓
IMLib / OSL / CoreMotion / Event / IO / UserMemory
```

**핵심 규칙**: Layer 1 ↔ Layer 2는 직접 링크하지 않는다. `include/` 공유 헤더와 IMDll IPC로만 통신한다.

### 디렉토리 규칙

```
<ModuleName>/                    — Layer 1 소스 (C99 RTDLL/SO)
  <ModuleName>_Motion.c          — 모듈 생명주기 + 주기 처리
  <ModuleName>_Funcs.c           — API 모드 핸들러 구현
  <ModuleName>_Util.c            — 내부 유틸리티 함수

<ModuleName>Api/                 — Layer 2 소스 (C++11 정적 라이브러리)
  <ModuleName>Api.cpp            — wmx3Api::<ModuleName> 클래스 구현
  <ModuleName>ApiTypes.cpp       — 데이터 타입 생성자 (기본값 초기화)

<ModuleName>Api_CLRLib/          — Layer 3 (C++/CLI, Windows 전용)
  <ModuleName>ApiCSharp.h/.cpp   — WMX3ApiCLR 관리형 클래스

include/                         — Layer 1 ↔ Layer 2 공유 헤더
  <ModuleName>Api.h              — C++ 공개 API (wmx3Api 네임스페이스)
  <ModuleName>ApiLocal.h         — 공유 구조체 (입출력 데이터 타입)
  <ModuleName>.h                 — Layer 1 내부 데이터 구조

test/                            — 단위 테스트 (gtest + gmock)
  test_<module>_funcs.cpp
  test_<module>_util.cpp
  mocks/                         — Mock 클래스 (IImLib, IOsl 등)
  CMakeLists.txt

build/                           — 빌드 출력 (git에 포함하지 않음)
CMakeLists.txt                   — 크로스플랫폼 빌드 설정
```

### WMX3 모듈 표준 진입점

모든 WMX3 모듈 플러그인은 다음 6개 심볼을 export해야 한다:

```c
Motion_API Motion_ModuleId(char licCode[WMX3_RTDLL_SDK_LIC_CODE_SIZE]);
Motion_API Motion_ModuleInfo(WMX3_MODULE_INFO* pInfo);
Motion_API Motion_Setup(IM_LIB_MODULE_FUNCS* pModuleFunc,
                        IM_LIB_STATUS_FUNCS* pStatusFunc,
                        WMX3_MODULE_SETTING* pSetting,
                        WMX3_MODULE_CONFIG* pConfig);
Motion_API Motion_Init(void* mParam);
Motion_API Motion_Cleanup(void* mParam);
Motion_API Motion_Process(void* mParam);
```

### RT 안전성 코딩 규칙 (Layer 1 필수 준수)

Layer 1(Core RTDLL)은 실시간 모션 프로세서 컨텍스트에서 실행된다. 다음 규칙을 반드시 준수한다:

**금지 사항**:
- `malloc`, `calloc`, `realloc`, `free` 사용 금지 → 사전 할당된 정적 배열/풀 사용
- 재귀 호출 금지 → 반복문으로 교체
- `printf`, `fprintf`, `sprintf` 금지 → `OslPrintf` 또는 완전 제거
- 타임아웃 없는 대기 금지 (`while(1)`, 무한 루프) → 카운터/타임아웃 기반 루프
- 파일 I/O 금지 (`fopen`, `fclose`, `fread`, `fwrite`)
- C++ 예외 금지 (`throw`, `try`, `catch`)
- POSIX 직접 호출 금지 → OSL(OS 추상화 계층) 함수 사용

**주의 사항**:
- 부동소수점 연산: FPU 없는 타겟에서 고정소수점 사용 권장
- 전역변수 경합: 다중 채널 접근 시 반드시 동기화 필요
- 스택 지역변수: 4KB 이하 유지

### 일반 코딩 규칙

- API 모드 핸들러 함수명: `소문자_접두어Api대문자Action` (예: `mmApiExecute`)
- 데이터 타입: UPPER_SNAKE_CASE (예: `MY_MODULE_DATA`, `PMY_MODULE_DATA`)
- C++ 클래스: `wmx3Api::<ModuleName>` 네임스페이스
- API 모드 enum: `<PREFIX>_API_MODE_<ACTION>`, 마지막은 반드시 `_SIZE`
- 전역 모듈 데이터: `__<ModuleName>Data__` 형식 (예: `__ApiBufferData__`)
- 채널 범위 검사: 모든 핸들러에서 `channel < 0 || channel >= MAX_CHANNEL` 체크
- NULL 체크: `mParam`, `inData`, `outData`는 항상 첫 줄에서 NULL 검사

### 빌드 방법

```bash
# 환경변수 설정 (필수)
export LMX_INSTALLER_ROOT=/opt/wmx3  # WMX3 SDK 설치 경로

# 릴리스 빌드
cmake --preset release && cmake --build --preset release

# 디버그 빌드
cmake --preset debug && cmake --build --preset debug

# 테스트 포함 빌드
cmake -B build/test -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Debug .
cmake --build build/test -j$(nproc)
ctest --test-dir build/test --output-on-failure

# 심볼 확인
nm -D build/debug/lib<module_name>.so | grep "Motion_"
```

### 테스트 (gtest + gmock)

```bash
# 테스트 실행
./build/test/test/wmx3_module_test --gtest_output=xml:/tmp/result.xml

# 특정 테스트만 실행
./build/test/test/wmx3_module_test --gtest_filter="MyModuleSuite.*"
```

**테스트 대상 분류**:
- 순수 로직 함수 (조건 평가, 유틸리티) → 즉시 테스트 가능
- API 모드 핸들러 → IMLib/OSL gmock으로 목킹하여 테스트
- RT 의존 함수 (Motion_Process, 인터럽트) → 테스트 제외

```cpp
// extern "C"로 C 모듈 링크
extern "C" {
    #include "MyModule.h"
    #include "MyModule_Funcs.h"
}

// 테스트명 규칙: TEST(스위트명, 핸들러명_조건_기댓값)
TEST(MyModuleSuite, Execute_ValidParam_ReturnsSuccess) {
    // Arrange
    MY_MODULE_DATA data = {};
    MY_EXECUTE_PARAM param = {.channel = 0, .targetPos = 1000};

    // Act
    int result = mmApiExecute(&data, 0, &param, NULL);

    // Assert
    EXPECT_EQ(0, result);
}
```

### 에이전트/스킬 구성

- 스킬: wmx3-setup, wmx3-module-create, wmx3-build, wmx3-module-add-api, wmx3-tdd, wmx3-code-review, wmx3-docs, wmx3-deploy
- 에이전트: wmx3-module-designer, wmx3-code-generator, wmx3-build-checker, wmx3-test-writer, wmx3-code-reviewer, wmx3-doc-writer
