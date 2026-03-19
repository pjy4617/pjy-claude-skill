# WMX3 모듈 코드 리뷰 체크리스트

---

## 1. RT 안전성 (12항목)

실시간 컨텍스트(`Motion_Process` 및 API 핸들러)에서 실행되는 코드에 대한 검사입니다.

| # | 항목 | 확인 방법 |
|---|------|-----------|
| RT-1 | `malloc`/`free`/`calloc`/`realloc` 호출 없음 | 소스 grep: `malloc\|free\|calloc\|realloc` |
| RT-2 | `new`/`delete` 연산자 사용 없음 (C++ 코드) | 소스 grep: `new \|delete ` |
| RT-3 | 재귀 함수 없음 (스택 오버플로우 위험) | 함수 호출 그래프 확인 |
| RT-4 | 무한 루프 없음 (탈출 조건 반드시 존재) | 모든 `while`/`for` 루프 탈출 조건 확인 |
| RT-5 | 무한 대기(`OSL_INFINITE`) 사용 시 반드시 타임아웃 또는 이벤트 시그널 존재 | `OslWaitForSingleObject` 호출 검토 |
| RT-6 | `printf`/`fprintf` 직접 호출 없음 (RT 컨텍스트) | `OslPrintf` 또는 제공된 로깅 API 사용 |
| RT-7 | 부동소수점 연산 최소화 및 일관된 사용 (`double` vs `float` 혼용 금지) | 조건 평가 코드의 부동소수점 타입 확인 |
| RT-8 | 스택 사이즈 초과 위험 없음 (대형 로컬 배열 금지) | 로컬 변수 크기 확인, 대형 구조체는 포인터 사용 |
| RT-9 | `Motion_Process` 반환값 항상 0 | 반환 경로 모두 `return 0` 확인 |
| RT-10 | `OslSleep` 사용 시 큐 상태를 `DELAY`로 변경 | `sleepFlag` 설정 전 `status.state = IM_LIB_QUEUE_STATE_DELAY` |
| RT-11 | 멀티-MP 환경에서 `pMP->id` 기준 채널 분리 | `buff[i].interruptId == pMP->id` 조건 확인 |
| RT-12 | 상태 업데이트 함수가 MP 0에서만 실행 | `pslParam->pMpData->id == 0` 조건 확인 |

---

## 2. IPC 정합성 (8항목)

C++ API 레이어와 RTDLL 핸들러 간의 데이터 구조가 일치해야 합니다.

| # | 항목 | 확인 방법 |
|---|------|-----------|
| IPC-1 | `ApiLocal.h`의 C 구조체 크기 = C++ API의 대응 클래스가 전송하는 데이터 크기 | `sizeof()` 비교, `imdll_SendAndReceive` 호출부의 `dataSize` 검토 |
| IPC-2 | `AB_API_MODE_*` 열거값과 `apiFuncs[]` 인덱스가 일치 | `Motion_Setup`의 `pModuleFunc->apiFuncs[MODE] = handler` 확인 |
| IPC-3 | `apiFuncNum = AB_API_MODE_SIZE` 설정 | `Motion_Setup`에서 반드시 마지막 열거값으로 설정 |
| IPC-4 | 새 API 모드 추가 시 `AB_API_MODE_SIZE` 이전에 추가 (열거값 순서 유지) | `ApiBufferApiLocal.h`의 열거형 순서 검토 |
| IPC-5 | `pData` 캐스팅 타입이 C++ API에서 전송하는 구조체와 일치 | 핸들러의 `(P{{STRUCT}}*)pData` 캐스팅과 `ApiBufferApi.cpp`의 전송 데이터 비교 |
| IPC-6 | `WMX3_API_RETURN_SUCCESS(argSize)`의 `argSize`가 실제 반환 데이터 크기와 일치 | 반환 데이터가 없으면 0, 있으면 `sizeof(구조체)` |
| IPC-7 | `imdll_RequestStatusChannel`의 `sizeof` 인수가 실제 상태 구조체 크기와 일치 | `ApiBufferApi.cpp`의 `init()` 함수 확인 |
| IPC-8 | 채널 번호 오프셋(+1) 적용 일관성 | 사용자 채널을 받는 모든 핸들러에서 `channel += 1` 확인 |

---

## 3. 크로스플랫폼 (6항목)

Windows(RTX64/Standard)와 Linux(RT/Xenomai) 모두에서 동작해야 합니다.

| # | 항목 | 확인 방법 |
|---|------|-----------|
| CP-1 | `#ifdef _WIN32` / `#ifndef _WIN32` 분기가 올바른 플랫폼별 코드를 포함 | 플랫폼 분기 검토 |
| CP-2 | `int` 크기 의존 코드 없음 (32/64비트 이식성) | `int` 대신 `uint32_t` 등 고정 폭 타입 사용 여부 확인 |
| CP-3 | `__stdcall` 매크로가 Linux에서 빈 정의로 제공됨 | `ApiBufferApiDef.h`의 `#ifndef __stdcall` 블록 확인 |
| CP-4 | 파일 경로 구분자 하드코딩 없음 (`\` 대신 `/` 또는 `OSL_PATH_SEPARATOR` 사용) | 경로 관련 코드 검토 |
| CP-5 | 문자열 리터럴에 `_OSL_T()` 매크로 적용 (유니코드/멀티바이트 호환) | `_OSL_T("문자열")` 사용 확인 |
| CP-6 | Windows DllMain(`ApiBuffer.c`)이 `#if WIN32` 조건부 컴파일 | `CMakeLists.txt`의 `if(WIN32)` 소스 추가 확인 |

---

## 4. 네이밍 (5항목)

| # | 항목 | 확인 방법 |
|---|------|-----------|
| NM-1 | 내부 심볼에 모듈 약어 접두어 사용 (예: `AB_`, `CM_`) | 공개되지 않을 열거형/구조체의 접두어 확인 |
| NM-2 | API 핸들러 함수명 패턴 준수: `{{prefix}}Api{{Function}}` | `buf`Api`Execute`, `buf`Api`Sleep` 등 확인 |
| NM-3 | 파일명 패턴 준수: `{{MODULE}}_Motion.c`, `{{MODULE}}_Funcs.c` | 소스 파일명 확인 |
| NM-4 | 헤더 가드 패턴: `WMX3_{{MODULE}}_{{TYPE}}_H` | 헤더 파일의 `#ifndef` 가드 확인 |
| NM-5 | 공개 상수에 `WMX3_{{MODULE_ABBREV}}_` 접두어 사용 | `ApiBufferApiDef.h`의 `#define WMX3_AB_` 패턴 확인 |

---

## 5. 심볼 가시성 (4항목)

Linux에서 불필요한 심볼 노출을 방지하고, Windows에서 올바른 export 설정을 확인합니다.

| # | 항목 | 확인 방법 |
|---|------|-----------|
| SV-1 | `export` 파일의 `global:` 섹션에 구현된 진입점만 포함 | `export` 파일과 실제 구현 함수 목록 비교 |
| SV-2 | 구현했지만 `export` 미등록 진입점 없음 | `export`의 `global:` 목록과 소스 파일의 `Motion_` 함수 비교 |
| SV-3 | 내부 유틸리티 함수가 `export`에 없음 | `bufApi*`, `ExecuteApiBuffer` 등이 `local:*`에 의해 숨겨짐 확인 |
| SV-4 | Windows에서 `WMX3_EXPORTS` 매크로가 올바른 `__declspec(dllexport)` 생성 | CMakeLists.txt의 `target_compile_definitions`에 `WMX3_EXPORTS` 확인 |

---

## 6. 빠른 리뷰 명령어

```bash
# RT-1: malloc/free 검색
grep -rn "malloc\|free\|calloc\|realloc" {{Module}}/ --include="*.c"

# RT-2: new/delete 검색 (C++ 코드)
grep -rn "\bnew\b\|\bdelete\b" {{Module}}Api/ --include="*.cpp"

# RT-3: 재귀 함수 탐지 (함수가 자기 자신을 호출하는지)
# 수동 확인 필요

# IPC-3: apiFuncNum 설정 확인
grep -n "apiFuncNum" {{Module}}/{{MODULE}}_Motion.c

# IPC-4: API 모드 열거형 확인
grep -n "AB_API_MODE_SIZE" include/{{MODULE}}ApiLocal.h

# SV-1: export 파일 확인
cat {{Module}}/export

# CP-3: __stdcall 매크로 확인
grep -n "__stdcall" include/{{MODULE}}ApiDef.h

# NM-4: 헤더 가드 확인
grep -rn "#ifndef WMX3_" include/ --include="*.h"
```
