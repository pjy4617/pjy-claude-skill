---
name: wmx3-code-review
description: "WMX3 모듈 코드 리뷰. RT 안전성, IPC 정합성, 크로스플랫폼 호환성, 네이밍, 심볼 가시성 항목을 체크리스트 기반으로 검토한다. '코드 리뷰', '리뷰해줘', 'wmx3 검증', 'RT 안전성', '코드 검토', 'IPC 검증', '모듈 리뷰' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
---

# WMX3 모듈 코드 리뷰

> 이 스킬은 WMX3 모듈의 코드 품질을 5개 카테고리, 35개 항목으로 검토합니다.
> 실제 리뷰는 **wmx3-code-reviewer 에이전트**에게 위임합니다.
> `references/review-checklist.md`를 참조합니다.

## 리뷰 카테고리 요약

| 카테고리 | 항목 수 | 핵심 관심사 |
|---------|---------|------------|
| 1. RT 안전성 | 12항목 | malloc 금지, 재귀 금지, 무한 대기 금지 |
| 2. IPC 정합성 | 8항목 | 구조체 일치, API 모드 번호, apiFuncNum |
| 3. 크로스플랫폼 | 6항목 | `#ifdef`, 타입 크기, 경로 |
| 4. 네이밍 | 5항목 | 접두어, 파일명, 헤더 가드 |
| 5. 심볼 가시성 | 4항목 | exports 파일 vs 구현 |

---

## 카테고리 1: RT 안전성 (12항목)

RT(실시간) 컨텍스트에서 `Motion_Process()`가 매 제어 사이클마다 호출되므로, 다음 규칙을 엄격히 준수해야 합니다.

| # | 항목 | 설명 | 심각도 |
|---|------|------|--------|
| 1.1 | **동적 메모리 금지** | `malloc`, `calloc`, `realloc`, `free` 사용 금지. 정적 또는 스택 할당만 허용 | CRITICAL |
| 1.2 | **재귀 함수 금지** | 스택 오버플로우 위험. 재귀는 반복문으로 변환 | CRITICAL |
| 1.3 | **무한 대기 금지** | `while(1)` 또는 timeout 없는 루프 금지. 반드시 최대 반복 횟수 또는 타임아웃 설정 | CRITICAL |
| 1.4 | **전역 변수 보호** | 여러 컨텍스트에서 접근하는 전역 변수는 OSL 뮤텍스로 보호 | MAJOR |
| 1.5 | **부동소수점 주의** | FPU 컨텍스트 저장/복원 여부 확인. RT 환경에서는 정수 연산 우선 | MAJOR |
| 1.6 | **printf/logging 금지** | RT 컨텍스트에서 printf, fprintf, syslog 호출 금지 | MAJOR |
| 1.7 | **시스템 콜 금지** | `open`, `read`, `write`, `socket` 등 블로킹 시스템 콜 금지 | CRITICAL |
| 1.8 | **스택 크기 제한** | 함수 내 대형 지역 배열 금지 (스택 오버플로우). 정적 변수 사용 | MAJOR |
| 1.9 | **예외 처리 금지** | C++ 예외(`throw/catch`) 금지. 에러 코드 반환 방식 사용 | MAJOR |
| 1.10 | **STL 컨테이너 금지** | `std::vector`, `std::map` 등 동적 메모리 컨테이너 금지 | MAJOR |
| 1.11 | **인터럽트 안전** | 인터럽트 핸들러에서 호출될 수 있는 함수는 재진입 안전(reentrant) 보장 | MAJOR |
| 1.12 | **초기화 완료 확인** | `Motion_Init()`이 완료되지 않은 상태에서 `Motion_Process()` 진입 방어 | MAJOR |

---

## 카테고리 2: IPC 정합성 (8항목)

Layer 1(Core RTDLL)과 Layer 2(C++ API)는 직접 링크하지 않고 공유 헤더를 통해 구조체를 공유합니다. 불일치 시 데이터 오염 발생.

| # | 항목 | 설명 | 심각도 |
|---|------|------|--------|
| 2.1 | **구조체 레이아웃 일치** | `ApiLocal.h`의 구조체가 C 모듈과 C++ API에서 동일하게 포함되는지 확인 | CRITICAL |
| 2.2 | **API 모드 번호 일치** | enum 값이 `apiFuncs[]` 배열 인덱스와 일치하는지 확인 | CRITICAL |
| 2.3 | **apiFuncNum 정확성** | `apiFuncNum`이 `apiFuncs[]` 실제 배열 크기와 일치하는지 확인 | CRITICAL |
| 2.4 | **패킹 지시자** | 크로스플랫폼 전송 구조체에 `#pragma pack` 또는 `__attribute__((packed))` 적용 여부 | MAJOR |
| 2.5 | **포인터 필드 금지** | IPC 전송 구조체에 포인터 필드 금지 (주소 공간이 다름) | CRITICAL |
| 2.6 | **가변 길이 배열 금지** | IPC 구조체에 VLA(Variable Length Array) 금지. 고정 크기만 허용 | MAJOR |
| 2.7 | **엔디안 안전성** | 다른 아키텍처 간 통신 시 엔디안 변환 여부 확인 | INFO |
| 2.8 | **버전 호환성** | 구조체 변경 시 이전 버전과의 호환성 또는 버전 필드 존재 여부 | MINOR |

---

## 카테고리 3: 크로스플랫폼 호환성 (6항목)

WMX3 모듈은 Windows(RTX64/Standard)와 Linux(RT/Xenomai) 양쪽에서 빌드됩니다.

| # | 항목 | 설명 | 심각도 |
|---|------|------|--------|
| 3.1 | **`#ifdef` 가드 완전성** | `_WIN32`, `__linux__`, `RTX64` 등 플랫폼별 코드 분기가 양쪽 모두 처리되는지 확인 | MAJOR |
| 3.2 | **타입 크기 안전성** | `int`, `long` 크기가 플랫폼마다 다름. 고정 크기 타입(`int32_t`, `uint64_t`) 사용 | MAJOR |
| 3.3 | **경로 구분자** | 하드코딩된 `/` 또는 `\\` 경로 금지. OS 중립 경로 사용 | MINOR |
| 3.4 | **DllMain 가드** | Windows 전용 `DllMain`은 `#ifdef _WIN32` 내부에만 존재해야 함 | MAJOR |
| 3.5 | **심볼 내보내기** | Linux: `.exports` 파일로 내보낼 심볼 명시. Windows: `__declspec(dllexport)` 또는 `.def` 파일 | MAJOR |
| 3.6 | **컴파일러 확장 주의** | MSVC 전용(`__forceinline`, `__cdecl`) 또는 GCC 전용(`__attribute__`) 사용 시 적절한 가드 | MINOR |

---

## 카테고리 4: 네이밍 규칙 (5항목)

| # | 항목 | 설명 | 심각도 |
|---|------|------|--------|
| 4.1 | **모듈 접두어 일관성** | 모든 공개 함수는 모듈 접두어(`AB_`, `PC_` 등)로 시작 | MINOR |
| 4.2 | **파일명 규칙** | Core: `{{MODULE_NAME}}_Funcs.c` 형식. API: `{{MODULE_NAME}}Api.cpp` 형식 | MINOR |
| 4.3 | **헤더 가드** | 모든 `.h` 파일에 `#ifndef {{MODULE_NAME_UPPER}}_H` 형식의 인클루드 가드 존재 | MINOR |
| 4.4 | **상수 네이밍** | 매직 넘버 금지. 명명된 상수(`#define`, `enum`, `const`) 사용 | MINOR |
| 4.5 | **enum 네이밍** | `{MODULE_PREFIX}_APIFUNC_{NAME}` 형식 준수 | INFO |

---

## 카테고리 5: 심볼 가시성 (4항목)

| # | 항목 | 설명 | 심각도 |
|---|------|------|--------|
| 5.1 | **exports 파일 동기화** | `exports/{{MODULE_NAME}}.exports`에 나열된 심볼이 실제로 구현되어 있는지 확인 | MAJOR |
| 5.2 | **WMX3 표준 심볼 필수 포함** | `Motion_ModuleId`, `Motion_ModuleInfo`, `Motion_Setup`, `Motion_Init`, `Motion_Cleanup`, `Motion_Process` 모두 exports에 포함 | CRITICAL |
| 5.3 | **내부 함수 비공개** | `static` 키워드로 파일 범위 함수가 외부에 노출되지 않는지 확인 | MINOR |
| 5.4 | **C++ 링키지 가드** | C 헤더가 C++ 파일에서 포함될 때 `extern "C"` 가드 적용 여부 | MAJOR |

---

## wmx3-code-reviewer 에이전트 위임

이 스킬은 실제 리뷰 작업을 `wmx3-code-reviewer 에이전트`에게 위임합니다.

에이전트에게 전달할 정보:
- 리뷰 대상 파일 목록 (또는 전체 모듈 디렉토리)
- 특별히 집중할 카테고리 (없으면 전체 35항목)
- 최근 변경된 파일 (`git diff` 결과)

---

## 심각도별 리포트 형식

리뷰 결과는 다음 형식으로 보고합니다:

```
== WMX3 코드 리뷰 결과 ==

검토 파일: ApiBuffer_Funcs.c, ApiBufferApi.cpp, ApiBufferApiLocal.h

[CRITICAL] 2건
  🔴 1.1 동적 메모리 금지 위반
     위치: ApiBuffer_Funcs.c:142
     내용: `malloc(sizeof(BufferEntry))` 사용됨
     수정: 정적 배열 `g_bufferPool[MAX_ENTRIES]`로 교체

  🔴 2.3 apiFuncNum 불일치
     위치: ApiBuffer_Motion.c:87
     내용: apiFuncNum=12이나 apiFuncs[] 배열 크기=13
     수정: apiFuncNum을 13으로 수정

[MAJOR] 1건
  🟠 1.4 전역 변수 미보호
     위치: ApiBuffer_Util.c:55
     내용: `g_executeCount` 뮤텍스 없이 접근
     수정: OSL_MutexLock/Unlock으로 보호

[MINOR] 3건
  🟡 4.3 헤더 가드 누락
     위치: ApiBuffer_Funcs.h:1
     내용: include guard 없음
     수정: #ifndef APIBUFFER_FUNCS_H 추가

  ... (나머지 MINOR)

[INFO] 1건
  🔵 2.7 엔디안 안전성 미확인
     위치: ApiBufferApiLocal.h
     내용: 타겟 플랫폼이 리틀엔디안이 아닌 경우 대비 없음
     참고: 현재 지원 플랫폼(x86/ARM)은 리틀엔디안이므로 즉시 수정 불필요

== 요약 ==
CRITICAL: 2건  ← 즉시 수정 필요
MAJOR:    1건  ← 배포 전 수정 필요
MINOR:    3건  ← 다음 리팩토링 시 수정 권장
INFO:     1건  ← 참고 사항

다음 단계:
  CRITICAL 항목을 수정한 뒤 "다시 리뷰해줘"로 재검토하세요.
```
