---
name: rl-implement
description: "강화학습(RL) 환경·에이전트·학습 파이프라인 구현. rl-design의 설계 문서(또는 직접 요구)를 받아 Gymnasium 환경(reset/step 5-튜플·Box/Discrete·정규화·벡터화·시뮬레이터 래퍼), 프레임워크(Stable-Baselines3/CleanRL/Tianshou/RLlib, 오프라인 d3rlpy) 기반 에이전트 구성, 학습 파이프라인(하이퍼파라미터·체크포인트·로깅·다중 시드 재현성), 안전 계층·ONNX 실시간 추론 배포까지 구현한다. 'RL 환경 구현', '강화학습 코드 작성', 'Gymnasium 환경 만들어', 'SB3 학습', '정책 학습 파이프라인', 'RL 에이전트 구현', 'ONNX 배포' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# 강화학습(RL) 환경·에이전트·학습 파이프라인 구현

> 이 스킬은 rl-design의 설계 문서(선정 알고리즘·환경 규격·보상 함수·안전 아키텍처)를
> **동작하는 학습 코드**로 구현합니다.
> 실제 구현 작업은 **rlctrl-implementer 에이전트**에게 위임합니다.
>
> 페르소나: 강화학습을 20년 이상 실제 장비 제어 프로젝트에 상용으로 적용해 온 전문가.
> 화려한 알고리즘보다 **재현 가능하고 안전하게 배포되는 정책**을 우선합니다.

## 전제

이 스킬은 rl-assess가 **Go 판정**한 문제를 rl-design이 설계한 이후 단계입니다.
설계 문서가 없이 곧바로 구현을 요청받았다면, 최소한 다음을 확인한 뒤 진행합니다.
확인이 안 되면 rl-assess/rl-design 선행을 권합니다.

- 행동공간(연속/이산)·관측공간 정의와 스케일
- 선정 알고리즘(예: 연속제어 SAC/PPO, 이산 PPO/DQN 계열, 오프라인 CQL/IQL)
- 보상 함수와 **안전 제약**(위반 시 종료·페널티·shielding 대상)
- 학습 환경(시뮬레이터/로그 데이터)과 sim-to-real 전제

## 입력

- rl-design 스킬의 설계 문서(권장) 또는 직접 구현 요구
- 대상 시뮬레이터/장비 인터페이스(있으면 API·사이클타임·관측/명령 형식)
- 사용할 프레임워크 선호(없으면 절차에서 결정 — 기본 Stable-Baselines3)
- 실시간 추론 배포 대상 여부(ONNX·추론 지연 예산·제어 루프 주기)

## 실행 절차

| 단계 | 작업 | 참조 |
|------|------|------|
| ① | 설계 확인 (관측/행동공간·알고리즘·보상·안전 제약·학습 환경) | rl-design 산출물 |
| ② | **Gymnasium 환경 구현**: `gymnasium.Env` 서브클래스, `reset(seed) -> (obs, info)`, `step(action) -> (obs, reward, terminated, truncated, info)` **5-튜플**, `observation_space`/`action_space`(Box/Discrete), 관측·행동 정규화, 벡터화, 시뮬레이터/장비 래퍼(안전 계층 삽입 지점), `check_env` 검증 | `references/environment-design.md` |
| ③ | **프레임워크 선택·에이전트 구성**: SB3(생산 기본)/CleanRL(연구·커스터마이즈)/Tianshou/RLlib(분산), 오프라인은 d3rlpy, Safe RL은 omnisafe/safety-gymnasium | `references/framework-guide.md` |
| ④ | **학습 파이프라인**: 하이퍼파라미터 관리·정규화 저장/복원·EvalCallback/CheckpointCallback·TensorBoard/W&B 로깅·**다중 시드 재현성** | `references/training-and-deployment.md` |
| ⑤ | **안전 계층·실시간 추론 배포**: action clipping·shielding·폴백 고전 제어기 상시 대기·ONNX export·추론 지연 예산·장비 제어 루프에 정책 삽입. 실기 구동이 C#/C++이면 크로스 언어 배포 | `references/environment-design.md` + `references/training-and-deployment.md` + `references/cross-language-deployment.md`(C#/C++ 구동) |
| ⑥ | **학습 실행·수렴 확인**: 짧은 스모크 학습 → 학습곡선·평가 보상 상승 확인, 그다음 본 학습 (테스트/평가는 rl-test에 위임) | — |

성능·기능 평가(다중 시드 통계·베이스라인 대비·제약 위반율·강건성·sim-to-real 검증)는
`rl-test` 스킬(rlctrl-evaluator 에이전트)에 위임합니다.

## rlctrl-implementer 에이전트 위임

실제 코드 작성·수정·학습 실행은 `rlctrl-implementer` 에이전트에게 위임합니다.

에이전트에게 전달할 정보:
- 설계 문서 경로(있으면) 또는 요구사항 요약(관측/행동공간·알고리즘·보상·안전 제약)
- 대상 시뮬레이터/장비 인터페이스 정보(API·사이클타임·관측/명령 형식)
- 프레임워크 선호와 실시간 배포 대상 여부(ONNX·추론 지연 예산)
- **references 정본 절대 경로**: `${CLAUDE_SKILL_DIR}/references/` 아래 문서들
  (`environment-design.md`, `framework-guide.md`, `training-and-deployment.md`,
  `cross-language-deployment.md` — C#/C++ 구동 배포 시 필수) —
  호출 시 실제 절대 경로로 치환하여 전달
  (에이전트는 `.claude/agents/`로 단독 설치되어 상대 references 경로가 깨지므로,
  스킬이 정본 절대 경로를 넘겨줘야 함 — wmx3app에서 확립된 패턴)
- 안전 아키텍처(shielding 규칙·폴백 제어기·비상 정지 조건)와 sim-to-real 전제

## 필수 API 계약 (Gymnasium 현행 API)

> **핵심**: 이 플러그인의 모든 환경 코드는 구 Gym이 아닌 **Gymnasium** 현행 API를 따릅니다.

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np


class PlantEnv(gym.Env):
    """장비 제어 환경 — Gymnasium 현행 API(5-튜플)."""

    metadata = {"render_modes": []}

    def __init__(self, config=None):
        super().__init__()
        # 관측/행동 공간은 정규화된 범위를 권장 (예: [-1, 1])
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(6,), dtype=np.float32)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)          # self.np_random 시드 고정 (재현성)
        obs = self._get_obs()             # np.float32, observation_space 내부
        info = {}
        return obs, info                  # ← 2-튜플 (obs, info)

    def step(self, action):
        # action은 policy 출력 → 실제 명령으로 역정규화 + 안전 클리핑
        safe_action = self._apply_safety_layer(action)
        self._advance_plant(safe_action)
        obs = self._get_obs()
        reward = self._compute_reward()
        terminated = self._is_goal_or_failure()   # MDP상 종료(목표 도달·실패)
        truncated = self._is_time_limit()          # 시간/스텝 한계로 절단
        info = {}
        return obs, reward, terminated, truncated, info   # ← 5-튜플
```

- 위 골격의 `_get_obs`/`_apply_safety_layer`/`_advance_plant`/`_compute_reward`/`_is_goal_or_failure`/
  `_is_time_limit`(스텝 카운터 포함)는 **플랜트별로 구현해야 하는 헬퍼**입니다 — 이 골격만 복사하면
  실행되지 않습니다(구현 골격·스텁 예: `references/environment-design.md`).
- **Gym → Gymnasium 마이그레이션 주의**: 구 Gym의 4-튜플 `(obs, reward, done, info)`가
  Gymnasium에서 **5-튜플 `(obs, reward, terminated, truncated, info)`**로 바뀌었습니다.
  `done = terminated or truncated`로 뭉뚱그리면 **부트스트래핑이 틀려집니다**
  (시간 절단 `truncated`는 가치 부트스트랩을 계속해야 하고, 실제 종료 `terminated`만
  부트스트랩을 끊어야 함). `reset`도 `(obs)` 단일 반환 → `(obs, info)` 2-튜플로 변경.
  구 Gym 코드를 이식할 때는 `gymnasium.wrappers`/`shimmy` 어댑터 사용을 검토하되,
  신규 코드는 반드시 5-튜플로 작성합니다. (세부: `references/environment-design.md`)
- **라이브러리 버전 세부는 단정하지 않습니다** — Gymnasium/Stable-Baselines3/PyTorch의
  정확한 버전·인자·클래스명은 **context7 MCP(`mcp__plugin_context7_context7__*`) 또는
  공식 문서**로 확인한 뒤 사용합니다(추측 금지).

## 최소 학습 예제 (Stable-Baselines3 SAC)

```python
# SB3 SAC 최소 학습 골격 — 연속제어 기본값 (SAC — Haarnoja et al. 2018)
from stable_baselines3 import SAC
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3.common.callbacks import EvalCallback

SEED = 0
# 벡터화 + 관측/보상 정규화 (정규화 통계는 학습 후 반드시 저장·복원)
train_env = make_vec_env(lambda: PlantEnv(), n_envs=4, seed=SEED)
train_env = VecNormalize(train_env, norm_obs=True, norm_reward=True)

# 평가 전용 환경 — 학습과 다른 시드 · 보상 정규화 끔 · 통계 갱신 정지(training=False)
eval_env = make_vec_env(lambda: PlantEnv(), n_envs=1, seed=SEED + 100)
eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=False, training=False)

model = SAC("MlpPolicy", train_env, seed=SEED, verbose=1,
            tensorboard_log="./tb/")   # 하이퍼파라미터는 공식 문서/rl-zoo 기본값에서 출발
# 평가 콜백: 별도 eval_env로 주기적 결정론적 정책 평가 + 최고 성능 체크포인트 저장
# (EvalCallback이 매 평가마다 sync_envs_normalization으로 학습→평가 정규화 통계 자동 동기화)
eval_cb = EvalCallback(eval_env, best_model_save_path="./ckpt/",
                       eval_freq=10_000, deterministic=True)
model.learn(total_timesteps=200_000, callback=eval_cb)
model.save("sac_plant")
train_env.save("vecnormalize.pkl")     # 정규화 통계 저장 (추론 시 동일 통계 필수)
```

- 알고리즘/하이퍼파라미터의 정확한 인자·기본값은 **context7 또는 SB3 공식 문서**로 확인합니다.
- 다중 시드·평가 프로토콜·안전 검증 게이트는 `rl-test`가 담당하되, 이 스킬에서
  최소 스모크 학습으로 **파이프라인이 실제 수렴하는지**만 확인합니다.

## 안전 계층·배포 (요약)

장비 제어는 안전-크리티컬입니다. 학습된 정책을 실기에 **직접** 배포하지 않습니다.

- **action clipping / shielding**: 정책 출력은 항상 물리 한계로 클리핑하고, 안전 규칙을
  위반하는 행동은 안전 행동으로 대체(shield)합니다. 삽입 지점은 환경 래퍼 + 배포 루프 양쪽.
- **폴백 고전 제어기 상시 대기**: 정책 이상·추론 지연 초과·관측 이상 시 즉시 PID/LQR 등
  폴백으로 전환하고 비상 정지 조건을 둡니다.
- **ONNX 실시간 추론 배포**: 학습 프레임워크 의존성 없이 정책만 ONNX로 export →
  추론 지연이 제어 루프 주기 예산 안에 드는지 측정. 정규화 통계도 함께 배포.
- **크로스 언어 배포(실기 구동이 C#/C++)**: 실기 구동 프로그램이 C#/C++이면 Python 학습 →
  ONNX → C#/C++ 추론이 표준 패턴입니다. 정규화 패리티·구동측 안전 계층·패리티 테스트는
  `references/cross-language-deployment.md`를 따릅니다.
- **시뮬 우선 → 가드형 실기 전환**: 시뮬레이터에서 검증(rl-test) → 사람 감독 하 실기 전환.
  (세부: `references/training-and-deployment.md` — 학습↔실기 안전 검증 게이트)

## references

| 파일 | 내용 |
|------|------|
| `references/environment-design.md` | Gymnasium 환경 구현 — `gymnasium.Env` 서브클래스, reset/step **5-튜플**, Box/Discrete spaces, 관측/행동 정규화, 벡터화(VecEnv), 시뮬레이터/장비 래퍼(안전 계층 삽입 지점), `check_env`, **Gym→Gymnasium 4→5튜플 마이그레이션** |
| `references/framework-guide.md` | 프레임워크 비교·선택 — SB3/SB3-Contrib/CleanRL/Tianshou/Ray RLlib/d3rlpy/omnisafe·safety-gymnasium, 선택 기준, 최소 학습 예제(SB3 SAC), 버전 확인은 context7 |
| `references/training-and-deployment.md` | 학습 파이프라인(하이퍼파라미터·정규화 저장/복원·콜백·로깅·**다중 시드 재현성**) + 실시간 추론 배포(`predict(deterministic=True)`·ONNX·추론 지연 예산·안전 계층·폴백)·학습↔실기 안전 검증 게이트 |
| `references/cross-language-deployment.md` | **크로스 언어 배포** — Python 학습 → ONNX → C#/C++ 구동 프로그램 추론: 아키텍처, **정규화 패리티**, ONNX Runtime C++/C# 개념(실시간·GC 주의), **구동측 안전 계층**, WMX3 통합, 패리티 테스트. ONNX Runtime API 세부는 context7/공식 문서 확인 |

## 크로스 플러그인 시너지

대상 장비가 WMX3 모션 제어 기반이면 `wmx3app` 플러그인의 **SimuPlatform**을 Gymnasium
래퍼로 감싸 학습·평가 환경으로 쓸 수 있고, 실기 전환은 `wmx3-app-test`의 실기 전환
체크리스트를 따를 수 있습니다(강제 아님).

## 구현 시 금지 사항

- **구 Gym 4-튜플 사용 금지** — 신규 환경은 반드시 Gymnasium 5-튜플. `terminated`와
  `truncated`를 분리하고, 시간 절단(truncated)에서 가치 부트스트랩을 끊지 않는다.
- **미확인 라이브러리 API 단정 금지** — Gymnasium/SB3/PyTorch의 버전별 인자·클래스명은
  context7/공식 문서로 확인. 확인 못 한 것은 함수명 수준까지만 쓰고 확인 지시를 남긴다.
- **정규화 통계 유실 금지** — `VecNormalize` 통계(관측/보상)를 저장하지 않고 추론하면 정책이
  전혀 다른 분포를 보게 된다. 학습 시 저장 → 추론 시 동일 통계 로드를 반드시 보장.
- **안전 계층 없는 실기 배포 금지** — action clipping·shielding·폴백·비상 정지 없이
  학습 정책을 실기 제어 루프에 넣지 않는다. 시뮬 검증(rl-test) 통과가 실기 전환의 전제.
- **시드 미고정 금지** — 재현성을 위해 환경(`reset(seed=)`)·프레임워크(`seed=`)·라이브러리
  전역 시드를 고정하고, 평가는 학습과 다른 시드로 수행한다.
