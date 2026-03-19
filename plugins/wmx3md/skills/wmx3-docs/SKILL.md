---
name: wmx3-docs
description: "WMX3 모듈의 사용자 설명서(MD)를 자동 생성합니다. C++ API 헤더에서 함수 시그니처, 매개변수, 반환값, 에러 코드를 추출하여 마크다운 문서를 생성합니다. '문서 생성', '설명서 만들어', 'API 문서', 'docs', '사용법', '매뉴얼', 'README' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[모듈명 또는 대상 헤더 경로]"
---

# WMX3 모듈 사용자 설명서 생성

> 이 스킬은 문서 구조와 생성 절차를 정의합니다.
> 실제 문서 작성은 **wmx3-doc-writer 에이전트**에게 위임됩니다.

## 핵심 원칙

1. **소스 기반 자동 추출**: C++ API 헤더(`{{MODULE_NAME}}Api.h`)에서 클래스/메서드 자동 추출
2. **예제 코드 포함**: 각 API에 C++/C# 사용 예제 제공
3. **에러 코드 문서화**: `{{MODULE_NAME}}ApiDef.h`에서 에러 코드, 상수, 열거형 추출
4. **한국어 작성**: 모든 설명은 한국어

## 생성 문서 구조

```
docs/
├── {{MODULE_NAME}}_UserGuide.md       ← 메인 사용자 가이드
├── {{MODULE_NAME}}_API_Reference.md   ← API 레퍼런스 (전체 함수)
├── {{MODULE_NAME}}_ErrorCodes.md      ← 에러 코드 목록
└── {{MODULE_NAME}}_Examples.md        ← 사용 예제 모음
```

## 문서 생성 워크플로우

### 1단계: 소스 분석

대상 파일에서 정보를 추출합니다:

| 대상 파일 | 추출 정보 |
|-----------|-----------|
| `include/{{MODULE_NAME}}Api.h` | 클래스, 메서드 시그니처, 매개변수 |
| `include/{{MODULE_NAME}}ApiDef.h` | 상수, 열거형, 구조체, 에러 코드 |
| `include/{{MODULE_NAME}}ApiLocal.h` | API 모드 목록 (내부 참조) |
| `{{MODULE_NAME}}Api/{{MODULE_NAME}}Api.cpp` | 메서드 구현 (동작 상세) |
| `{{MODULE_NAME}}Api/{{MODULE_NAME}}Api_ApiLog.cpp` | 로그 메시지 (에러 설명) |

```bash
# API 클래스의 public 메서드 추출
grep -n "^\s*\(int\|void\|bool\|WMX3_.*\)\s" include/{{MODULE_NAME}}Api.h
```

### 2단계: wmx3-doc-writer 에이전트 위임

추출된 정보를 기반으로 에이전트에게 문서 작성을 위임합니다.

### 3단계: 문서 구조 검증

생성된 문서의 완성도를 확인합니다:

- [ ] 모든 public 메서드가 문서화되었는지
- [ ] 각 메서드에 매개변수 설명이 있는지
- [ ] 반환값과 에러 코드가 명시되었는지
- [ ] 사용 예제가 포함되었는지
- [ ] 열거형/상수 목록이 완전한지

## 사용자 가이드 (UserGuide.md) 템플릿

```markdown
# {{MODULE_NAME}} 사용자 가이드

## 개요
- 모듈 설명
- 주요 기능 요약
- 의존 모듈

## 시작하기

### 헤더 포함
\`\`\`cpp
#include "{{MODULE_NAME}}Api.h"
\`\`\`

### 초기화
\`\`\`cpp
wmx3Api::{{MODULE_NAME}} module;
int ret = module.Create(deviceHandle, channelId);
\`\`\`

## 주요 API

### 기능별 분류
- 데이터 전송 API
- 상태 조회 API
- 제어 API
- 유틸리티 API

### 각 API 상세
- 함수 시그니처
- 매개변수 표
- 반환값
- 사용 예제
- 관련 에러 코드

## 에러 처리
- 공통 에러 코드 표
- 에러 처리 패턴

## 제한 사항
- 채널 수 제한
- 버퍼 크기 제한
- RT 환경 주의사항
```

## API 레퍼런스 (API_Reference.md) 템플릿

각 메서드를 다음 형식으로 문서화:

```markdown
### SetCmdBuffer

PDO 주소에 전송할 데이터를 Queue에 저장합니다.

**시그니처**
\`\`\`cpp
int SetCmdBuffer(int channel, uint16_t pdoAddress,
                 const std::vector<std::vector<int>>& data);
\`\`\`

**매개변수**

| 매개변수 | 타입 | 설명 |
|----------|------|------|
| channel | int | Queue 채널 번호 (0~254) |
| pdoAddress | uint16_t | 대상 PDO 주소 |
| data | vector<vector<int>> | 전송 데이터 (2차원 배열) |

**반환값**
- `0`: 성공
- `0x00012001`: 채널 범위 초과
- `0x00012002`: 버퍼 가득 참

**사용 예제**
\`\`\`cpp
wmx3Api::CmdBuffer buf;
buf.Create(hDevice, 0);

int ret = buf.SetCmdBuffer(0, 0x300, {
    {1, 200, 201},
    {2, 300, 301},
    {3, 400, 401}
});
\`\`\`

**동작 설명**
- 내부 Queue에 데이터를 순서대로 저장
- EtherCAT 통신 주기마다 Queue에서 하나씩 꺼내어 전송
- Queue에 데이터가 있을 때 추가 데이터 저장 가능

**관련 API**: GetCmdBufferCount, ClearCmdBuffer
```

## 정적 유틸리티 문서화

```markdown
## 정적 유틸리티 함수

| 함수 | 설명 |
|------|------|
| ErrorToString() | 에러 코드 → 문자열 변환 (char/wchar_t) |
| CmdBufferLogToString() | API 로그 데이터 → 문자열 변환 |
| GetLibVersion() | 라이브러리 버전 조회 |
```

## 에러 코드 문서 (ErrorCodes.md) 템플릿

```markdown
# {{MODULE_NAME}} 에러 코드

## 에러 코드 범위
- `0x0001X000` ~ `0x0001XFFF`: {{MODULE_NAME}} 전용

## 에러 코드 목록

| 코드 | 이름 | 설명 | 대처 방법 |
|------|------|------|-----------|
| 0x00000000 | SUCCESS | 성공 | - |
| 0x00012001 | CHANNEL_OUT_OF_RANGE | 채널 번호 범위 초과 | 채널을 0~254 범위로 |
| ... | ... | ... | ... |
```

## 예제 문서 (Examples.md) 템플릿

사용 시나리오별 완전한 예제:

```markdown
# {{MODULE_NAME}} 사용 예제

## 예제 1: 기본 사용
\`\`\`cpp
// 모듈 생성 및 초기화
wmx3Api::{{MODULE_NAME}} module;
module.Create(hDevice, 0);

// 기본 동작
// ...

// 정리
module.Destroy();
\`\`\`

## 예제 2: 에러 처리
...

## 예제 3: 다중 채널 사용
...
```

## C# 예제 포함 규칙

CLR Wrapper가 있는 경우, 각 API에 C# 예제도 포함:

```markdown
**C# 사용 예제**
\`\`\`csharp
var module = new WMX3ApiCLR.{{MODULE_NAME}}();
module.Create(hDevice, 0);

int ret = module.SetCmdBuffer(0, 0x300, data);
if (ret != 0)
{
    string errMsg = WMX3ApiCLR.{{MODULE_NAME}}.ErrorToString(ret);
    Console.WriteLine($"Error: {errMsg}");
}
\`\`\`
```

## 문서 품질 기준

- 모든 public API 100% 문서화
- 각 API에 최소 1개 사용 예제
- 에러 코드에 대처 방법 포함
- 매개변수 범위/제한사항 명시
- 관련 API 상호 참조 링크

$ARGUMENTS
