---
name: wmx3-module-add-api
description: "기존 WMX3 모듈에 새 API 모드 핸들러 추가. enum 값, C 핸들러, C++ 메서드, apiFuncs[] 등록까지 6~7개 파일을 체크리스트 기반으로 동시 수정한다. 'API 추가', '핸들러 추가', '기능 추가', 'API 모드', '새 명령', '새 API', '모드 추가해줘' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[API 모드명]"
---

# WMX3 모듈 API 모드 핸들러 추가

> 이 스킬은 기존 WMX3 모듈에 새 API 모드를 추가하는 체크리스트 기반 워크플로우입니다.
> `references/api-mode-addition-checklist.md`를 참조합니다.

## 워크플로우 개요

```
[1단계] 기존 모듈 구조 분석
         현재 API 모드 수, 마지막 enum 값, 파일 목록
         │
         ▼
[2단계] 새 API 모드 정의
         이름, 입력/출력 구조체, 핸들러 로직
         │
         ▼
[3단계] 6~7개 파일 동시 수정 (체크리스트)
         │
         ▼
[4단계] apiFuncNum 카운터 갱신
         │
         ▼
[5단계] wmx3-build-checker로 빌드 검증
```

---

## 1단계: 기존 모듈 구조 분석

수정 전에 다음 정보를 파악합니다:

```bash
# 현재 API 모드 enum 값 확인
grep -n "apifunc\|ApiFuncNum\|API_MODE\|_CMD" include/{{MODULE_NAME}}ApiLocal.h

# 현재 apiFuncs[] 배열 크기 확인
grep -n "apiFuncNum\|apiFuncs\[" {{MODULE_NAME}}/{{MODULE_NAME}}_Motion.c

# 기존 핸들러 함수 목록 확인
grep -n "^static\|^void\|^int\|^WMX3_ERR" {{MODULE_NAME}}/{{MODULE_NAME}}_Funcs.h
```

분석 결과 정리:
- 현재 API 모드 수: N개
- 마지막 enum 값: N (다음 추가값은 N+1)
- `apiFuncNum`: 현재 N → 추가 후 N+1

---

## 2단계: 새 API 모드 정의

수집 항목:

| 항목 | 예시 |
|------|------|
| API 모드 이름 | `GetStatus` |
| enum 상수명 | `AB_APIFUNC_GET_STATUS` |
| 입력 구조체명 | `ApiBufferGetStatusInput` (없으면 생략) |
| 출력 구조체명 | `ApiBufferGetStatusOutput` (없으면 생략) |
| 핸들러 로직 설명 | "버퍼 상태(실행중/정지/에러)를 출력 구조체에 채워 반환" |

---

## 3단계: 파일 수정 체크리스트

아래 7개 파일을 순서대로 수정합니다. 각 파일 수정 후 체크박스를 표시합니다.

### [ ] 파일 1: `include/{{MODULE_NAME}}ApiLocal.h`

새 enum 값 추가:

```c
typedef enum {
    // ... 기존 값들 ...
    AB_APIFUNC_GET_STATUS = N,   // ← 추가
} ApiBufferApiFuncId;

// 입력 구조체 (입력 파라미터가 있는 경우)
typedef struct {
    int channelNo;
} ApiBufferGetStatusInput;

// 출력 구조체 (반환값이 있는 경우)
typedef struct {
    int status;        // 0: 정지, 1: 실행중, 2: 에러
    int errorCode;
} ApiBufferGetStatusOutput;
```

### [ ] 파일 2: `{{MODULE_NAME}}/{{MODULE_NAME}}_Funcs.h`

핸들러 함수 선언 추가:

```c
// 새 API 모드 핸들러 선언
int {{MODULE_PREFIX}}_GetStatus(void *pArgs, void *pOutput);
```

### [ ] 파일 3: `{{MODULE_NAME}}/{{MODULE_NAME}}_Funcs.c`

핸들러 함수 구현 추가:

```c
/**
 * @brief 버퍼 실행 상태를 조회한다.
 * @param pArgs   ApiBufferGetStatusInput* 입력 구조체
 * @param pOutput ApiBufferGetStatusOutput* 출력 구조체
 * @return 0: 성공, 음수: 에러 코드
 */
int {{MODULE_PREFIX}}_GetStatus(void *pArgs, void *pOutput)
{
    ApiBufferGetStatusInput  *pIn  = (ApiBufferGetStatusInput *)pArgs;
    ApiBufferGetStatusOutput *pOut = (ApiBufferGetStatusOutput *)pOutput;

    if (pIn == NULL || pOut == NULL) {
        return WMX3_ERR_INVALID_PARAM;
    }

    /* TODO: 실제 로직 구현 */
    pOut->status    = g_moduleState.status;
    pOut->errorCode = g_moduleState.errorCode;

    return 0;
}
```

### [ ] 파일 4: `{{MODULE_NAME}}/{{MODULE_NAME}}_Motion.c`

`Motion_Setup()` 내부 `apiFuncs[]` 배열에 등록:

```c
static IMApiFunc apiFuncs[] = {
    // ... 기존 항목들 ...
    { AB_APIFUNC_GET_STATUS, {{MODULE_PREFIX}}_GetStatus },   // ← 추가
};

// apiFuncNum 갱신 (배열 크기와 일치해야 함)
static int apiFuncNum = N + 1;  // ← N을 N+1로 수정
```

> **주의**: `apiFuncNum`이 `apiFuncs[]` 실제 배열 크기와 다르면 런타임 크래시 발생.
> `sizeof(apiFuncs) / sizeof(apiFuncs[0])` 표현식을 사용하면 자동 계산됩니다.

### [ ] 파일 5: `{{MODULE_NAME}}Api/{{MODULE_NAME}}Api.h`

C++ 메서드 선언 추가:

```cpp
namespace wmx3Api {
class {{MODULE_NAME}} {
public:
    // ... 기존 메서드들 ...

    /**
     * @brief 버퍼 실행 상태를 조회한다.
     * @param channelNo 채널 번호
     * @param output    [출력] 상태 정보
     * @return WMX3 에러 코드 (0: 성공)
     */
    int GetStatus(int channelNo, ApiBufferGetStatusOutput &output);
};
} // namespace wmx3Api
```

### [ ] 파일 6: `{{MODULE_NAME}}Api/{{MODULE_NAME}}Api.cpp`

C++ 메서드 구현 추가:

```cpp
int wmx3Api::{{MODULE_NAME}}::GetStatus(int channelNo,
                                         ApiBufferGetStatusOutput &output)
{
    ApiBufferGetStatusInput input;
    input.channelNo = channelNo;

    return SendCommand(AB_APIFUNC_GET_STATUS, &input, &output);
}
```

### [ ] 파일 7: `{{MODULE_NAME}}Api/{{MODULE_NAME}}ApiUtil.cpp` (구조체 변환이 필요한 경우)

C++ ↔ C 구조체 변환 함수 추가 (구조체 필드 이름이 다른 경우에만):

```cpp
// 변환이 필요한 경우에만 추가
void ConvertGetStatusOutput(const ApiBufferGetStatusOutput &src,
                             wmx3Api::ApiBufferGetStatusOutput &dst)
{
    dst.status    = src.status;
    dst.errorCode = src.errorCode;
}
```

---

## 4단계: apiFuncNum 카운터 검증

모든 파일 수정 후 카운터가 일치하는지 최종 확인:

```bash
# apiFuncNum 값 확인
grep -n "apiFuncNum" {{MODULE_NAME}}/{{MODULE_NAME}}_Motion.c

# apiFuncs[] 항목 수 확인 (실제 등록된 핸들러 수)
grep -c "AB_APIFUNC_" {{MODULE_NAME}}/{{MODULE_NAME}}_Motion.c
```

두 값이 일치하지 않으면 수정합니다.

---

## 5단계: 빌드 검증

`wmx3-build-checker 에이전트`에 위임하여 빌드 검증을 수행하거나, 직접 빌드:

```bash
cmake --preset linux-release && cmake --build --preset linux-release
```

빌드 에러가 없으면 완료를 보고합니다.

---

## 수정 완료 보고

```
API 모드 추가 완료!

추가된 API 모드: GetStatus (enum 값: N)

수정된 파일 (7개):
  ✅ include/ApiBufferApiLocal.h      — enum + 구조체 추가
  ✅ ApiBuffer/ApiBuffer_Funcs.h      — 핸들러 선언 추가
  ✅ ApiBuffer/ApiBuffer_Funcs.c      — 핸들러 구현 추가
  ✅ ApiBuffer/ApiBuffer_Motion.c     — apiFuncs[] 등록 + apiFuncNum 갱신
  ✅ ApiBufferApi/ApiBufferApi.h      — C++ 메서드 선언 추가
  ✅ ApiBufferApi/ApiBufferApi.cpp    — C++ 메서드 구현 추가
  ✅ ApiBufferApi/ApiBufferApiUtil.cpp — 구조체 변환 추가

apiFuncNum: N → N+1
빌드: ✅ 성공

다음 단계:
  "GetStatus 테스트 작성해줘" → wmx3-tdd 스킬
  "코드 리뷰해줘"              → wmx3-code-review 스킬
```

$ARGUMENTS
