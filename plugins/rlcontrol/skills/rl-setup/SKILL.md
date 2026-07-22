---
name: rl-setup
description: "강화학습(RL) 제어 플러그인 환경 초기 설정. 에이전트 4명과 CLAUDE.md를 프로젝트에 설치합니다. 플러그인 설치 후 최초 1회 실행 필요. 'rlcontrol 설정', 'RL 플러그인 셋업', 'rlcontrol 에이전트 설치', 'rl-setup', '강화학습 플러그인 초기화' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob
---

# 강화학습(RL) 제어 스킬 환경 초기 설정

이 스킬은 강화학습 제어 플러그인(rlcontrol)의 에이전트와 CLAUDE.md를 현재 프로젝트에 설치합니다.

> **원칙 먼저**: 이 플러그인은 "RL을 쓰자"가 아니라 **"RL을 정말 써야 하는가"부터 냉정하게 판별**하는 워크플로입니다.
> 대부분의 제어 문제는 고전 제어(PID/LQR/MPC)로 충분하며, RL은 안전성·재현성·샘플효율·검증난이도
> 리스크를 들여옵니다. 설치 후 첫 작업은 항상 `rl-assess`(적용 가능성 게이트)로 시작하는 것을 권장합니다.

## 실행 절차

### 1단계: 플러그인 디렉토리 확인

`${CLAUDE_SKILL_DIR}` 기준으로 상위 디렉토리에서 `agents/`와 `claude-md/` 폴더를 찾습니다.

```
PLUGIN_DIR = ${CLAUDE_SKILL_DIR}/../../
```

### 2단계: 프로젝트 경로 확인

설치를 진행하기 전에 사용자에게 프로젝트 경로를 질문합니다:

> 강화학습(RL) 제어 프로젝트를 설치할 경로를 알려주세요.
> (엔터만 누르면 현재 디렉토리에 설치합니다)

- 사용자가 경로를 입력하면: 해당 경로를 `PROJECT_ROOT`로 설정
- 사용자가 입력하지 않으면 (빈 값): 현재 작업 디렉토리를 `PROJECT_ROOT`로 설정
- `PROJECT_ROOT`가 존재하지 않으면 생성 여부를 사용자에게 확인 후 생성

이후 모든 단계는 `PROJECT_ROOT` 기준으로 실행합니다.

### 3단계: 에이전트 설치

`PROJECT_ROOT/.claude/agents/` 디렉토리에 **4개** 에이전트를 복사합니다.

```bash
mkdir -p ${PROJECT_ROOT}/.claude/agents
```

복사 대상 (PLUGIN_DIR/agents/ 아래):
- `rlctrl-feasibility-analyst.md` — RL 적용 가능성 검토 전문가 (읽기 전용 분석·MDP 정식화·고전 제어 대비·Go/No-Go 판정)
- `rlctrl-algorithm-designer.md` — 알고리즘 선정·환경/보상/안전 설계 전문가 (SAC/PPO/오프라인/Safe RL·보상 설계·안전 아키텍처)
- `rlctrl-implementer.md` — 구현 전문가 (Gymnasium 환경·SB3/CleanRL 학습 파이프라인·안전 계층·ONNX 실시간 추론 배포)
- `rlctrl-evaluator.md` — 성능·기능 테스트 전문가 (다중 시드 통계·베이스라인 대비·제약 위반율·강건성·sim-to-real 검증)

각 파일을 읽어서 `${PROJECT_ROOT}/.claude/agents/`에 동일한 이름으로 작성합니다.
이미 존재하는 파일은 덮어쓰기 전에 사용자에게 확인합니다.

### 4단계: CLAUDE.md 병합

`PLUGIN_DIR/claude-md/CLAUDE.md`의 내용을 읽어서 `${PROJECT_ROOT}/.claude/CLAUDE.md`에 추가합니다.

- `${PROJECT_ROOT}/.claude/CLAUDE.md`가 없으면 새로 생성합니다.
- 이미 존재하면, `## Reinforcement Learning for Control` 섹션이 있는지 확인합니다.
  - 있으면: "이미 설치되어 있습니다" 안내
  - 없으면: 파일 끝에 추가

### 5단계: 설치 결과 보고

```
강화학습(RL) 제어 스킬 환경 설치 완료!

에이전트 (4명):
  ✅ rlctrl-feasibility-analyst — RL 적용 가능성 검토 (읽기 전용, MDP 정식화·고전 제어 대비·Go/No-Go)
  ✅ rlctrl-algorithm-designer  — 알고리즘 선정·환경/보상/안전 설계 (SAC/PPO/오프라인/Safe RL)
  ✅ rlctrl-implementer         — 구현 (Gymnasium 환경·SB3 학습 파이프라인·안전 계층·ONNX 배포)
  ✅ rlctrl-evaluator           — 성능·기능 테스트 (다중 시드 통계·베이스라인·강건성·sim-to-real)

스킬 (5개): 플러그인으로 이미 활성화됨
  rl-assess     — 강화학습 적용 가능성 검토 (게이트 — RL 부적합 판정 가능)
  rl-design     — 알고리즘 검토 및 환경/보상/안전 설계
  rl-implement  — Gymnasium 환경·에이전트·학습 파이프라인 구현
  rl-test       — 성능·기능 테스트/평가 (다중 시드·sim-to-real)
  rl-setup      — 환경 초기 설정 (현재 스킬)

CLAUDE.md: ✅ Reinforcement Learning for Control 설정 추가됨

시작하기 (게이트 우선):
  "이 온도 제어 루프에 강화학습을 적용할 수 있는지 검토해줘" 로 시작하세요.
  적용 가능성 게이트(rl-assess)가 먼저 Go/No-Go를 판정합니다 — No면 고전 제어 권장안을 냅니다.
  사용 가이드: 플러그인 docs/USAGE_GUIDE.md
```

## 매뉴얼/라이브러리 근거 연동

- 제어 장비가 **WMX3 모션 제어** 기반이면 `wmx3app` 플러그인의 SimuPlatform을 학습·평가 환경(Gymnasium
  래퍼)으로, 실기 전환은 `wmx3-app-test`의 실기 전환 체크리스트를 재사용할 수 있습니다(크로스 플러그인 시너지, 강제 아님).
- RL 라이브러리(Gymnasium·Stable-Baselines3·CleanRL·d3rlpy 등)의 **버전별 세부 API는 단정하지 말고**
  context7 MCP(`mcp__plugin_context7_context7__*`) 또는 공식 문서로 확인합니다. 이 규칙은 설치되는
  CLAUDE.md와 각 에이전트에도 명시되어 있습니다.
