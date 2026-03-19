# 새 API 모드 추가 체크리스트

기존 WMX3 모듈에 새 API 모드(새 기능 함수)를 추가할 때 수정이 필요한 파일과 각 파일별 수정 포인트를 정리합니다.

ApiBuffer 모듈 구조를 기준으로 설명합니다.

---

## 수정 파일 목록 (7개)

```
1. include/{{MODULE}}ApiLocal.h   ← API 모드 열거형에 새 모드 추가
2. {{Module}}/{{MODULE}}_Funcs.h  ← 핸들러 함수 선언 추가
3. {{Module}}/{{MODULE}}_Funcs.c  ← 핸들러 함수 구현 추가
4. {{Module}}/{{MODULE}}_Motion.c ← Motion_Setup에서 핸들러 등록
5. {{Module}}Api/{{Module}}Api.cpp ← C++ API 래퍼 함수 구현
6. include/{{Module}}Api.h         ← C++ API 클래스에 함수 선언
7. {{Module}}Api/{{Module}}ApiUtil.h/cpp ← C++↔C 구조체 변환 (필요 시)
```

---

## 1. include/{{MODULE}}ApiLocal.h — API 모드 열거형

`AB_API_MODE_SIZE` **이전에** 새 모드를 추가합니다.

```c
typedef enum {
    AB_API_MODE_GET_VERSION,
    AB_API_MODE_EXECUTE,
    AB_API_MODE_HALT,
    // ...기존 모드들...
    AB_API_MODE_REGISTER_INTERRUPT_ID,

    AB_API_MODE_{{NEW_FUNCTION}},   // ← 여기에 추가 (SIZE 바로 앞)

    AB_API_MODE_SIZE   // ← 이 값이 apiFuncNum으로 사용됨 (절대 이 뒤에 추가하지 말 것)
} AB_API_MODE;
```

IPC 데이터 전송 구조체도 추가합니다 (필요 시):
```c
// 새 API의 입력 파라미터 구조체
typedef struct {
    int param1;
    double param2;
    // ...
} AB_{{NEW_FUNCTION}}_DATA, *PAB_{{NEW_FUNCTION}}_DATA;
```

---

## 2. {{Module}}/{{MODULE}}_Funcs.h — 핸들러 선언

```c
// 기존 선언들...
int IM_API bufApiRegisterInterruptID(WMX3_API_PARAM);

int IM_API bufApi{{NewFunction}}(WMX3_API_PARAM);   // ← 추가
```

---

## 3. {{Module}}/{{MODULE}}_Funcs.c — 핸들러 구현

```c
int IM_API bufApi{{NewFunction}}(WMX3_API_PARAM) {
    PIM_LIB_MPARAM lmParam = (PIM_LIB_MPARAM)mParam;
    PAPIBUFFER_DATA pApiBufferData = (PAPIBUFFER_DATA)lmParam->mParam;

    // 입력 데이터 파싱
    PAB_{{NEW_FUNCTION}}_DATA pInputData = (PAB_{{NEW_FUNCTION}}_DATA)pData;

    // 파라미터 유효성 검사
    if (pInputData->param1 < 0 || pInputData->param1 >= MAX_VALUE) {
        WMX3_API_RETURN_ERROR(WMX3_API_ERROR_ARGUMENT_OUT_OF_RANGE, 0);
    }

    // 실제 로직 (Util 함수로 위임 권장)
    int ret = {{NewFunction}}Logic(pApiBufferData, pInputData);
    if (ret) {
        WMX3_API_RETURN_ERROR(ret, 0);
    }

    // 반환 데이터가 있는 경우
    // *((int*)pData) = resultValue;
    // WMX3_API_RETURN_SUCCESS(sizeof(int));

    WMX3_API_RETURN_SUCCESS(0);  // 반환 데이터 없는 경우
}
```

---

## 4. {{Module}}/{{MODULE}}_Motion.c — Motion_Setup 핸들러 등록

```c
Motion_API Motion_Setup(IM_LIB_MODULE_FUNCS* pModuleFunc, ...) {
    // ...기존 등록...
    if (pModuleFunc != NULL) {
        pModuleFunc->apiFuncs[AB_API_MODE_GET_VERSION]           = bufApiGetVersion;
        // ...기존 핸들러들...
        pModuleFunc->apiFuncs[AB_API_MODE_REGISTER_INTERRUPT_ID] = bufApiRegisterInterruptID;

        pModuleFunc->apiFuncs[AB_API_MODE_{{NEW_FUNCTION}}]      = bufApi{{NewFunction}};  // ← 추가

        pModuleFunc->apiFuncNum = AB_API_MODE_SIZE;  // 자동으로 새 모드 포함
        // ...
    }
}
```

`apiFuncNum = AB_API_MODE_SIZE`를 그대로 유지하면 열거형에 추가된 값이 자동 반영됩니다.

---

## 5. {{Module}}Api/{{Module}}Api.cpp — C++ API 래퍼 구현

```cpp
WMX3APIFUNC wmx3Api::ApiBuffer::{{NewFunction}}(int param1, double param2) {
    if (wmx3Api == NULL) {
        return WMX3_API_ERROR_INVALID_DEVICE;
    }

    // C++ 파라미터 → C 구조체 변환
    AB_{{NEW_FUNCTION}}_DATA inputData;
    memset(&inputData, 0, sizeof(inputData));
    inputData.param1 = param1;
    inputData.param2 = param2;

    // IPC 호출: 모드 번호로 RTDLL 핸들러 디스패치
    int ret = imdll_SendAndReceive(
        wmx3Api->dev,
        WMX3_MODULE_ID_APIBUFFER,
        AB_API_MODE_{{NEW_FUNCTION}},
        &inputData, sizeof(inputData),
        NULL, 0, NULL,
        &apiBufferVersion
    );

    return ret;
}
```

반환 데이터가 있는 경우:
```cpp
WMX3APIFUNC wmx3Api::ApiBuffer::{{NewFunctionGet}}(int* pResult) {
    int inputChannel = 0;  // 또는 필요한 입력

    int ret = imdll_SendAndReceive(
        wmx3Api->dev,
        WMX3_MODULE_ID_APIBUFFER,
        AB_API_MODE_{{NEW_FUNCTION}},
        &inputChannel, sizeof(inputChannel),  // 입력 데이터
        pResult, sizeof(int), NULL,            // 출력 데이터 버퍼
        &apiBufferVersion
    );

    return ret;
}
```

---

## 6. include/{{Module}}Api.h — C++ API 클래스 선언

```cpp
namespace wmx3Api {
    class ApiBuffer {
    public:
        // ...기존 선언들...
        WMX3APIFUNC Rewind(unsigned int channel);

        WMX3APIFUNC {{NewFunction}}(int param1, double param2);  // ← 추가
    };
}
```

필요하다면 입력/출력 데이터 클래스도 추가:
```cpp
namespace wmx3Api {
    class {{NewFunction}}Input {
    public:
        {{NewFunction}}Input();
        int param1;
        double param2;
    };
}
```

---

## 7. {{Module}}Api/{{Module}}ApiUtil.h/cpp — 구조체 변환

C++ 클래스 ↔ C 구조체 변환이 복잡한 경우:

```cpp
// ApiBufferApiUtil.h
void Convert{{NewFunction}}InputToC(
    const wmx3Api::{{NewFunction}}Input* pCppInput,
    AB_{{NEW_FUNCTION}}_DATA* pCInput);

// ApiBufferApiUtil.cpp
void Convert{{NewFunction}}InputToC(
    const wmx3Api::{{NewFunction}}Input* pCppInput,
    AB_{{NEW_FUNCTION}}_DATA* pCInput)
{
    memset(pCInput, 0, sizeof(*pCInput));
    pCInput->param1 = pCppInput->param1;
    pCInput->param2 = pCppInput->param2;
}
```

단순한 타입(int, double 등)은 별도 변환 함수 없이 직접 대입합니다.

---

## apiFuncNum 갱신 규칙

`apiFuncNum`은 **항상 `AB_API_MODE_SIZE`로 유지**합니다. 새 모드를 추가하면 열거형 값이 자동으로 증가하므로 별도 수정이 필요 없습니다.

```c
// Motion_Setup - 수정 불필요
pModuleFunc->apiFuncNum = AB_API_MODE_SIZE;  // 자동으로 최신 크기 반영
```

단, `apiFuncs[]` 배열의 크기(`IM_MAX_API_FUNC_SIZE` 등)를 초과하지 않는지 확인하세요.

---

## 전체 수정 체크리스트

### include/{{MODULE}}ApiLocal.h
- [ ] `AB_API_MODE_SIZE` 이전에 `AB_API_MODE_{{NEW_FUNCTION}}` 추가
- [ ] 필요 시 IPC 데이터 구조체 `AB_{{NEW_FUNCTION}}_DATA` 추가

### {{Module}}/{{MODULE}}_Funcs.h
- [ ] `bufApi{{NewFunction}}(WMX3_API_PARAM)` 선언 추가

### {{Module}}/{{MODULE}}_Funcs.c
- [ ] `bufApi{{NewFunction}}` 구현 추가
- [ ] 파라미터 유효성 검사 포함
- [ ] `WMX3_API_RETURN_ERROR` / `WMX3_API_RETURN_SUCCESS` 매크로 사용

### {{Module}}/{{MODULE}}_Motion.c
- [ ] `pModuleFunc->apiFuncs[AB_API_MODE_{{NEW_FUNCTION}}] = bufApi{{NewFunction}}` 추가
- [ ] `apiFuncNum = AB_API_MODE_SIZE` 유지 확인

### {{Module}}Api/{{Module}}Api.cpp
- [ ] `imdll_SendAndReceive` 호출로 C++ 래퍼 구현
- [ ] 입력 데이터 구조체 초기화 (`memset(0)`)
- [ ] 올바른 `sizeof` 값 사용

### include/{{Module}}Api.h
- [ ] `ApiBuffer` 클래스에 `WMX3APIFUNC {{NewFunction}}(...)` 선언 추가
- [ ] 필요 시 입출력 데이터 클래스 추가

### {{Module}}Api/{{Module}}ApiUtil (필요 시)
- [ ] C++ ↔ C 변환 함수 추가

### 선택적 추가 파일
- [ ] `{{Module}}Api_ApiLog.cpp`: 새 API의 로그 문자열 변환 케이스 추가
- [ ] `ApiBufferApi_CLRLib/`: .NET 래퍼에 대응 함수 추가 (Windows, Visual Studio 빌드)
- [ ] `C++ Builder/`: C++ Builder 프로젝트에 대응 함수 추가 (해당하는 경우)

---

## 빠른 검증

새 API 모드 추가 후 검증:

```bash
# 1. 모드 번호 일관성 확인
grep -n "AB_API_MODE_{{NEW_FUNCTION}}" include/ {{Module}}/ {{Module}}Api/ -r

# 2. apiFuncNum 확인
grep -n "apiFuncNum" {{Module}}/{{MODULE}}_Motion.c

# 3. 빌드 오류 확인
cmake --build build-linux-debug 2>&1 | grep -i error
```
