# WMX3 MODULE_ID 할당 체계

---

## 1. MODULE_ID 역할

`WMX3_MODULE_ID_*`는 WMX3 엔진에서 각 모듈을 고유하게 식별하는 정수 상수입니다.

주요 사용 위치:
- `Motion_ModuleId()` 반환값
- `pAllAxisIoData->userMemory[MODULE_ID]` 인덱스
- `imdll_SendAndReceive()` 호출 시 `moduleId` 파라미터
- `IM_UtilVerifySecurityCode(MODULE_ID, ...)` 보안 코드 검증
- 이벤트 등록: `pEvPub->registerCustomEvent(MODULE_ID, &event)`

---

## 2. 기존 모듈 ID 목록

`WMX3EngineDef.h`에 정의된 표준 모듈 ID:

```c
// WMX3EngineDef.h (참고용 - 실제 값은 설치된 SDK 헤더 확인)
typedef enum {
    WMX3_MODULE_ID_CORE_MOTION  = ...,   // CoreMotion 모듈
    WMX3_MODULE_ID_EVENT        = ...,   // Event 모듈
    WMX3_MODULE_ID_IO           = ...,   // IO 모듈
    WMX3_MODULE_ID_USER_MEMORY  = ...,   // UserMemory 모듈
    WMX3_MODULE_ID_APIBUFFER    = ...,   // ApiBuffer 모듈 (이 모듈)
    // ...기타 표준 모듈들...
} WMX3_MODULE_ID;
```

**중요:** 실제 숫자값은 설치된 WMX3 SDK의 `WMX3EngineDef.h`를 직접 확인하세요. 여기서는 패턴만 기술합니다.

---

## 3. 새 모듈 ID 할당 규칙

### 3.1 SDK 파트너 모듈 (공식 배포)

Soft Servo Systems로부터 공식 모듈 ID를 발급받아야 합니다:
- 연락처: Soft Servo Systems, Inc.
- ID 충돌 시 엔진이 로딩을 거부하거나 잘못된 PubData 포인터를 반환할 수 있음

### 3.2 커스텀 모듈 (내부 개발)

WMX3 SDK가 예약해 놓은 커스텀 모듈 범위를 사용합니다:

```c
// WMX3EngineDef.h의 커스텀 모듈 범위 확인 필요
// 일반적으로 높은 번호 대역이 커스텀 모듈용으로 예약됨
#define WMX3_MODULE_ID_{{NEW_MODULE}} {{ASSIGNED_ID}}
```

### 3.3 충돌 방지 절차

1. 현재 `WMX3EngineDef.h`에서 사용 중인 ID 전체 목록 확인
2. 프로젝트 내 `MODULE_IDS.md` 또는 팀 문서에서 내부 할당 ID 확인
3. 기존 ID와 겹치지 않는 값 선택
4. 팀 문서에 새 ID 등록
5. `WMX3EngineDef.h`에 `#define WMX3_MODULE_ID_{{NEW_MODULE}} {{VALUE}}` 추가

---

## 4. licCode 값 형식

`Motion_ModuleId()`에서 반환하는 라이선스 코드:

```c
Motion_API Motion_ModuleId(char licCode[WMX3_RTDLL_SDK_LIC_CODE_SIZE]) {
    // 24자 영숫자 문자열 (Soft Servo Systems 발급)
    snprintfs(licCode, WMX3_RTDLL_SDK_LIC_CODE_SIZE, "LPPRQLX28LUKKFFTM7ASN5KJ");
    return WMX3_MODULE_ID_APIBUFFER;
}
```

- `WMX3_RTDLL_SDK_LIC_CODE_SIZE`: 라이선스 코드 버퍼 크기 (null 종단 포함)
- 실제 코드는 24자 영대문자+숫자 조합
- 모듈 ID별로 고유한 라이선스 코드 발급
- 커스텀 모듈의 경우 개발팀과 협의하여 테스트용 코드 사용

---

## 5. Motion_Init에서의 검증

```c
Motion_API Motion_Init(WMX3_MP_ALL_AXIS_IO_DATA* pAllAxisIoData,
                       WMX3_MODULE_INIT_DATA*    pInitData)
{
    // 보안 코드 검증: MODULE_ID + licCode의 조합 확인
    if (!IM_UtilVerifySecurityCode(WMX3_MODULE_ID_{{MODULE_ID}}, pInitData->securityCode)) {
        return {{MODULE}}_ERROR_INVALID_SECURITY_CODE;
    }
    // ... 초기화 계속 ...
}
```

- `IM_UtilVerifySecurityCode`: IMLib 함수, MODULE_ID와 licCode의 유효성을 검증
- 검증 실패 시 즉시 에러 반환, 모듈 초기화 중단

---

## 6. 실제 ID 확인 방법

```bash
# 설치된 WMX3 SDK에서 모듈 ID 확인 (Windows)
grep -n "WMX3_MODULE_ID_" "%WMX3EngineReleasePath%/include/WMX3EngineDef.h"

# Linux
grep -n "WMX3_MODULE_ID_" "${ENG_REL}/include/WMX3EngineDef.h"
```

---

## 7. MODULE_ID 관련 개발 체크리스트

- [ ] `WMX3EngineDef.h`에서 기존 ID 전체 목록 확인
- [ ] 새 ID가 기존 ID와 겹치지 않음
- [ ] `Motion_ModuleId()`에서 올바른 ID 반환
- [ ] `Motion_Init()`에서 동일 ID로 `IM_UtilVerifySecurityCode` 호출
- [ ] `imdll_SendAndReceive()` 호출 시 동일 ID 사용
- [ ] 팀 ID 할당 문서에 새 모듈 등록
