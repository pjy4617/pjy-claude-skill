# WMX3 모듈 개발 플러그인 사용 가이드 (v1.1.0)

## 개요

WMX3 모션 제어 모듈 풀스택 개발 플러그인입니다.
apibuffer 모듈을 기준 패턴으로 한 3-layer 모듈 스캐폴딩, 빌드, 테스트, 코드 리뷰, 배포, 문서 생성을 지원합니다.

## 설치

```bash
# 1. 마켓플레이스 추가 (한 번만)
/plugin marketplace add pjy4617/pjy-claude-skill

# 2. WMX3 플러그인 설치
/plugin install wmx3md@pjy-skills

# 3. 에이전트 + CLAUDE.md 설치 (최초 1회)
/wmx3-setup
```

셋업 시 프로젝트 경로를 질문합니다:
```
> WMX3 모듈 프로젝트를 설치할 경로를 알려주세요.
> (엔터만 누르면 현재 디렉토리에 설치합니다)
```

지정한 경로에 에이전트 6명과 CLAUDE.md가 설치됩니다.

## 스킬 목록 (8개)

| 스킬 | 호출 예시 | 설명 |
|------|-----------|------|
| `wmx3-setup` | "wmx3 설정" | 에이전트 + CLAUDE.md 설치 (최초 1회) |
| `wmx3-module-create` | "새 모듈 만들어줘" | 3-layer 모듈 스캐폴딩 생성 |
| `wmx3-build` | "빌드해줘" | CMake 빌드 실행 (OS 자동 감지) |
| `wmx3-module-add-api` | "API 추가해줘" | 기존 모듈에 API 모드 핸들러 추가 |
| `wmx3-tdd` | "테스트 작성해줘" | gtest/gmock 기반 단위 테스트 |
| `wmx3-code-review` | "코드 리뷰해줘" | RT 안전성 + IPC 정합성 리뷰 (44항목) |
| `wmx3-docs` | "문서 생성해줘" | API 사용자 설명서 자동 생성 |
| `wmx3-deploy` | "배포해줘" | 빌드된 .so/.a 및 헤더를 /opt/lmx/에 배포 |

## 에이전트 목록 (6명)

| 에이전트 | 역할 |
|----------|------|
| `wmx3-module-designer` | 모듈 아키텍처 설계 (API 모드, 의존성, 데이터 구조) + 설계 산출물 전달 규약 |
| `wmx3-code-generator` | 템플릿 기반 코드 생성 (WMX3_API_PARAM 5파라미터 시그니처, 플레이스홀더 치환) |
| `wmx3-build-checker` | CMake 빌드 검증 (4단계 심각도 등급, 심볼, 크로스플랫폼, Windows 환경변수 검증) |
| `wmx3-test-writer` | gtest/gmock 테스트 코드 작성 |
| `wmx3-code-reviewer` | 코드 리뷰 44항목 (RT 안전성 16, IPC 정합성 11, 크로스플랫폼 8, 네이밍 5, 심볼 4) |
| `wmx3-doc-writer` | API 사용자 설명서 작성 + 에이전트 연동 안내 |

## 빠른 시작

### 1. 새 모듈 생성

```
"CmdBuffer라는 모듈 만들어줘"
```

이 요청은 다음을 자동 수행합니다:
1. wmx3-module-designer가 아키텍처 설계
2. wmx3-code-generator가 템플릿에서 코드 생성
3. wmx3-build-checker가 빌드 검증

### 2. 빌드

```
"빌드해줘"
```

Linux에서는 직접 실행, Windows에서는 빌드 명령을 안내합니다.

### 3. API 추가

```
"SetCmdBuffer API 추가해줘"
```

WMX3_API_PARAM(5파라미터) 시그니처로 6~7개 파일을 체크리스트 기반으로 동시 수정합니다.

### 4. 테스트 작성

```
"TDD로 CmdBuffer_Funcs 테스트해줘"
```

gtest/gmock으로 호스트 기반 단위 테스트를 생성합니다.

### 5. 코드 리뷰

```
"코드 리뷰해줘"
```

RT 안전성(16항목), IPC 정합성(11항목), 크로스플랫폼(8항목), 네이밍(5항목), 심볼(4항목)의 총 44항목을 검사합니다.

### 6. 문서 생성

```
"API 문서 만들어줘"
```

C++ API 헤더에서 함수 시그니처를 추출하여 마크다운 문서를 생성합니다.

## 3-layer 아키텍처

```
사용자 애플리케이션 (C++ / C#)
    ↓
Layer 2: <ModuleName>Api (C++11 정적 라이브러리)
    ↓ IPC (IMDll)
Layer 1: <ModuleName> (C99 Core RTDLL/SO)
    ↓
WMX3 엔진 + IMLib + OSL

[선택] Layer 3: <ModuleName>Api_CLRLib (C++/CLI .NET 래퍼, Windows 전용)
```

## 빌드 프리셋

| 프리셋 | 플랫폼 | 용도 |
|--------|--------|------|
| `linux-release` | Linux RT | 릴리스 빌드 |
| `linux-debug` | Linux RT | 디버그 빌드 |
| `linux-relwithdebinfo` | Linux RT | 릴리스 + 디버그 심볼 |
| `linux-xenomai` | Linux Xenomai | Xenomai RTOS 빌드 |
| `windows` | Windows RTX64 | Windows 빌드 |

## CLR Wrapper 참고

CLR Wrapper(Layer 3)는 `--with-clr` 옵션으로 선택적 생성됩니다.
현재 CLR 템플릿은 미제공이며, wmx3-code-generator 에이전트가 apibuffer의 CLR 구조를 참조하여 수동 생성합니다.

## 환경 변수

```bash
# 필수
export LMX_INSTALLER_ROOT=/opt/wmx3  # WMX3 SDK 설치 경로
```
