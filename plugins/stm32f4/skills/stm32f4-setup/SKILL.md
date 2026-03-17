---
name: stm32f4-setup
description: "STM32F4 스킬 환경 초기 설정. 에이전트 2명과 CLAUDE.md를 프로젝트에 설치합니다. 플러그인 설치 후 최초 1회 실행 필요. 'stm32f4 설정', 'stm32 setup', '에이전트 설치', 'stm32 초기 설정' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob
---

# STM32F4 스킬 환경 초기 설정

이 스킬은 STM32F4 플러그인의 에이전트와 CLAUDE.md를 현재 프로젝트에 설치합니다.

## 실행 절차

### 1단계: 플러그인 디렉토리 확인

`${CLAUDE_SKILL_DIR}` 기준으로 상위 디렉토리에서 `agents/`와 `claude-md/` 폴더를 찾습니다.

```
PLUGIN_DIR = ${CLAUDE_SKILL_DIR}/../../
```

### 2단계: 에이전트 설치

프로젝트 루트의 `.claude/agents/` 디렉토리에 2개 에이전트를 복사합니다.

```bash
mkdir -p .claude/agents
```

복사 대상 (PLUGIN_DIR/agents/ 아래):
- `kicad-stm32-checker.md` — KiCad 회로도 STM32 핀/페리페럴 검증자
- `stm32f4-test-writer.md` — 호스트 기반 단위 테스트 작성 전문가

각 파일을 읽어서 `.claude/agents/`에 동일한 이름으로 작성합니다.
이미 존재하는 파일은 덮어쓰기 전에 사용자에게 확인합니다.

### 3단계: CLAUDE.md 병합

`PLUGIN_DIR/claude-md/CLAUDE.md`의 내용을 읽어서 프로젝트 `.claude/CLAUDE.md`에 추가합니다.

- `.claude/CLAUDE.md`가 없으면 새로 생성합니다.
- 이미 존재하면, `## STM32F4 Firmware Project` 섹션이 있는지 확인합니다.
  - 있으면: "이미 설치되어 있습니다" 안내
  - 없으면: 파일 끝에 추가

### 4단계: 프로젝트 디렉토리 생성

기본 디렉토리 구조를 생성합니다:

```bash
mkdir -p Core/{Inc,Src} Drivers/{BSP/{Inc,Src},Device/{Inc,Src}} Middlewares/{Inc,Src} Startup Linker build
```

### 5단계: 설치 결과 보고

```
STM32F4 스킬 환경 설치 완료!

에이전트 (2명):
  ✅ kicad-stm32-checker  — KiCad 회로도 STM32 핀/페리페럴 검증
  ✅ stm32f4-test-writer  — 호스트 기반 단위 테스트 (Unity+FFF)

스킬 (3개): 플러그인으로 이미 활성화됨
  stm32f4-firmware    — 5단계 에이전트 파이프라인
  kicad-stm32-review  — 회로도 검증 체크리스트 (42항목)
  stm32f4-tdd         — 호스트 기반 TDD

CLAUDE.md: ✅ STM32F4 프로젝트 설정 추가됨
디렉토리: ✅ Core/ Drivers/ Middlewares/ Startup/ Linker/ build/

시작하기:
  "STM32F407로 SPI 펌웨어 만들어줘" 로 시작하세요.
  사용 가이드: 플러그인 docs/USAGE_GUIDE.md
```
