---
name: wmx3-module-create
description: "새 WMX3 RTDLL 모듈 스캐폴딩 생성. 3계층 구조(Core RTDLL / C++ API / CLR 래퍼)를 템플릿 기반으로 생성한다. '모듈 만들어', '새 모듈', 'wmx3 module', '모듈 생성', '스캐폴딩', 'RTDLL 생성', '새 wmx3 모듈 만들어줘' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[모듈명]"
---

# WMX3 새 모듈 스캐폴딩 생성

> 이 스킬은 WMX3 모듈의 전체 파일 구조를 생성하는 워크플로우를 정의합니다.
> 실제 아키텍처 설계는 **wmx3-module-designer 에이전트**에게,
> 코드 생성은 **wmx3-code-generator 에이전트**에게,
> 빌드 검증은 **wmx3-build-checker 에이전트**에게 위임합니다.

## 워크플로우 개요

```
[사용자 입력 수집]
       │
       ▼
[1단계] wmx3-module-designer — 아키텍처 설계
       │  API 모드 정의, 데이터 구조, 의존성 목록
       ▼
[2단계] wmx3-code-generator  — 코드 생성
       │  templates/ 치환 → 파일 생성 (Windows + Linux)
       ▼
[3단계] wmx3-build-checker   — 빌드 검증
       │  CMakeLists.txt, CMakePresets.json 검증
       ▼
[결과 보고] 생성된 파일 목록 + 다음 단계 안내
```

---

## 사용자 입력 수집

스킬 시작 시 다음 정보를 수집합니다. 미지정 항목은 괄호 안 기본값을 사용합니다.

| 항목 | 질문 | 기본값 |
|------|------|--------|
| 모듈명 | "모듈 이름을 입력하세요 (예: ApiBuffer, PositionCapture)" | 필수 (기본값 없음) |
| 모듈 설명 | "모듈의 역할을 한 줄로 설명해주세요" | 필수 (기본값 없음) |
| 의존 모듈 | "이 모듈이 의존하는 WMX3 모듈이 있나요? (예: CoreMotion, Event)" | 없음 |
| CLR 래퍼 | "--with-clr 옵션을 사용하시겠습니까? (C#/.NET 지원)" | 미포함 |

---

## 플레이스홀더 치환 규칙

템플릿 파일의 `{{PLACEHOLDER}}` 형식을 다음 규칙으로 치환합니다.

| 플레이스홀더 | 의미 | 예시 (입력: ApiBuffer) |
|------------|------|----------------------|
| `{{MODULE_NAME}}` | PascalCase | `ApiBuffer` |
| `{{module_name}}` | lowercase | `apibuffer` |
| `{{module_name_snake}}` | snake_case | `api_buffer` |
| `{{MODULE_NAME_UPPER}}` | UPPERCASE | `APIBUFFER` |
| `{{MODULE_PREFIX}}` | 약어 접두어 (2~4자) | `AB` |
| `{{MODULE_DESCRIPTION}}` | 모듈 설명 | `명령 버퍼링 실행 엔진` |
| `{{YEAR}}` | 현재 연도 | `2025` |

> `{{MODULE_PREFIX}}` 결정 규칙:
> - PascalCase 단어 첫 글자들을 대문자로 조합 (ApiBuffer → AB)
> - 단어가 하나인 경우 앞 2~3자 대문자 사용 (Monitor → MON)

---

## 1단계: wmx3-module-designer 에이전트 위임

다음 정보를 제공하여 아키텍처 설계를 요청합니다:
- 모듈명, 설명, 의존 모듈 목록
- `references/` 디렉토리의 설계 가이드 참조

설계 결과물:
- API 모드 목록 (enum 이름, 입력/출력 구조체)
- C 핸들러 함수 시그니처
- C++ 메서드 시그니처
- 파일 구조 목록

---

## 2단계: wmx3-code-generator 에이전트 위임

`assets/templates/` 의 템플릿 파일들을 읽어 치환 후 생성합니다.

### 생성되는 파일 구조

```
wmx3_module_{{module_name}}/
├── CMakeLists.txt
├── CMakePresets.json
├── {{MODULE_NAME}}/                     ← Core RTDLL (C99)
│   ├── {{MODULE_NAME}}.c                  (Windows DllMain, Linux 진입점)
│   ├── {{MODULE_NAME}}_Motion.c           (Motion_Setup/Init/Cleanup/Process)
│   ├── {{MODULE_NAME}}_Funcs.c            (API 모드 핸들러 구현)
│   ├── {{MODULE_NAME}}_Funcs.h            (핸들러 함수 선언)
│   ├── {{MODULE_NAME}}_Util.c             (유틸리티 함수)
│   ├── {{MODULE_NAME}}_Util.h
│   └── exports/
│       └── {{MODULE_NAME}}.exports        (Linux 심볼 내보내기)
├── {{MODULE_NAME}}Api/                  ← C++ API (C++11)
│   ├── {{MODULE_NAME}}Api.cpp             (wmx3Api::{{MODULE_NAME}} 클래스)
│   ├── {{MODULE_NAME}}ApiUtil.cpp         (C++ ↔ C 구조체 변환)
│   └── {{MODULE_NAME}}ApiTypes.cpp        (기본값 초기화 생성자)
├── {{MODULE_NAME}}Api_CLRLib/           ← CLR 래퍼 (--with-clr 시만 생성)
│   ├── {{MODULE_NAME}}ApiCSharp.h       ※ CLR 템플릿은 현재 미제공.
│   └── {{MODULE_NAME}}ApiCSharp.cpp        wmx3-code-generator가 apibuffer CLR 구조를 참조하여 수동 생성.
└── include/                             ← 공유 헤더
    ├── {{MODULE_NAME}}ApiLocal.h          (API 모드 enum, 공유 구조체)
    └── {{MODULE_NAME}}Api.h               (C++ 공개 API 선언)
```

> **Windows + Linux 양쪽 모두 생성**: CMakePresets.json에 `windows`, `linux-release`,
> `linux-debug`, `linux-relwithdebinfo`, `linux-xenomai` 프리셋을 포함합니다.

---

## 3단계: wmx3-build-checker 에이전트 위임

생성된 파일의 빌드 시스템을 검증합니다:
- CMakeLists.txt 소스 파일 목록 일치 여부
- CMakePresets.json 프리셋 조건 (`hostSystemName`) 정확성
- 헤더 include 경로 유효성
- `LMX_INSTALLER_ROOT` 환경변수 의존성 문서화

---

## 결과 보고

```
WMX3 모듈 스캐폴딩 생성 완료!

모듈명: {{MODULE_NAME}}
생성된 파일 (N개):
  ✅ {{MODULE_NAME}}/{{MODULE_NAME}}_Motion.c
  ✅ {{MODULE_NAME}}/{{MODULE_NAME}}_Funcs.c
  ✅ {{MODULE_NAME}}Api/{{MODULE_NAME}}Api.cpp
  ... (전체 목록)

다음 단계:
  1. "wmx3 빌드해줘"         → wmx3-build 스킬로 빌드 검증
  2. "API 모드 추가해줘"      → wmx3-module-add-api 스킬
  3. "테스트 작성해줘"        → wmx3-tdd 스킬
  4. "코드 리뷰해줘"          → wmx3-code-review 스킬

환경변수 설정 필요:
  export LMX_INSTALLER_ROOT=/opt/lmx
```

$ARGUMENTS
