---
name: wmx3-setup
description: "WMX3 모듈 개발 스킬 환경 초기 설정. 에이전트 6명과 CLAUDE.md를 프로젝트에 설치합니다. 플러그인 설치 후 최초 1회 실행 필요. 'wmx3 설정', 'wmx3 setup', 'wmx3 에이전트 설치', 'wmx3 초기 설정' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob
---

# WMX3 스킬 환경 초기 설정

이 스킬은 WMX3 모듈 개발 플러그인의 에이전트와 CLAUDE.md를 현재 프로젝트에 설치합니다.

## 실행 절차

### 1단계: 플러그인 디렉토리 확인

`${CLAUDE_SKILL_DIR}` 기준으로 상위 디렉토리에서 `agents/`와 `claude-md/` 폴더를 찾습니다.

```
PLUGIN_DIR = ${CLAUDE_SKILL_DIR}/../../
```

### 2단계: 프로젝트 경로 확인

설치를 진행하기 전에 사용자에게 프로젝트 경로를 질문합니다:

> WMX3 모듈 프로젝트를 설치할 경로를 알려주세요.
> (엔터만 누르면 현재 디렉토리에 설치합니다)

- 사용자가 경로를 입력하면: 해당 경로를 `PROJECT_ROOT`로 설정
- 사용자가 입력하지 않으면 (빈 값): 현재 작업 디렉토리를 `PROJECT_ROOT`로 설정
- `PROJECT_ROOT`가 존재하지 않으면 생성 여부를 사용자에게 확인 후 생성

이후 모든 단계는 `PROJECT_ROOT` 기준으로 실행합니다.

### 3단계: 에이전트 설치

`PROJECT_ROOT/.claude/agents/` 디렉토리에 6개 에이전트를 복사합니다.

```bash
mkdir -p ${PROJECT_ROOT}/.claude/agents
```

복사 대상 (PLUGIN_DIR/agents/ 아래):
- `wmx3-module-designer.md` — WMX3 모듈 아키텍처 설계 전문가
- `wmx3-code-generator.md` — 템플릿 기반 WMX3 모듈 코드 생성
- `wmx3-build-checker.md` — CMake 빌드 시스템 검증 전문가
- `wmx3-test-writer.md` — gtest/gmock 기반 단위 테스트 작성 전문가
- `wmx3-code-reviewer.md` — WMX3 모듈 코드 리뷰 전문가 (RT 안전성, IPC 정합성)
- `wmx3-doc-writer.md` — API 사용자 설명서 작성 전문가

각 파일을 읽어서 `${PROJECT_ROOT}/.claude/agents/`에 동일한 이름으로 작성합니다.
이미 존재하는 파일은 덮어쓰기 전에 사용자에게 확인합니다.

### 4단계: CLAUDE.md 병합

`PLUGIN_DIR/claude-md/CLAUDE.md`의 내용을 읽어서 `${PROJECT_ROOT}/.claude/CLAUDE.md`에 추가합니다.

- `${PROJECT_ROOT}/.claude/CLAUDE.md`가 없으면 새로 생성합니다.
- 이미 존재하면, `## WMX3 Module Development` 섹션이 있는지 확인합니다.
  - 있으면: "이미 설치되어 있습니다" 안내
  - 없으면: 파일 끝에 추가

### 5단계: 설치 결과 보고

```
WMX3 스킬 환경 설치 완료!

에이전트 (6명):
  ✅ wmx3-module-designer  — WMX3 모듈 아키텍처 설계
  ✅ wmx3-code-generator   — 템플릿 기반 코드 생성
  ✅ wmx3-build-checker    — CMake 빌드 검증
  ✅ wmx3-test-writer      — gtest/gmock 단위 테스트 작성
  ✅ wmx3-code-reviewer    — RT 안전성 + IPC 정합성 코드 리뷰
  ✅ wmx3-doc-writer       — API 사용자 설명서 작성

스킬 (8개): 플러그인으로 이미 활성화됨
  wmx3-setup            — 환경 초기 설정 (현재 스킬)
  wmx3-module-create    — 새 WMX3 모듈 스캐폴딩 생성
  wmx3-build            — CMake 빌드 실행
  wmx3-module-add-api   — 기존 모듈에 API 모드 핸들러 추가
  wmx3-tdd              — gtest/gmock 기반 단위 테스트
  wmx3-code-review      — 모듈 코드 리뷰 (RT 안전성, IPC 정합성)
  wmx3-docs             — API 사용자 설명서 자동 생성
  wmx3-deploy           — /opt/lmx 배포 스크립트 생성 및 실행

CLAUDE.md: ✅ WMX3 모듈 개발 설정 추가됨

시작하기:
  "ApiBuffer 같은 모듈 만들어줘" 로 시작하세요.
  사용 가이드: 플러그인 docs/USAGE_GUIDE.md
```
