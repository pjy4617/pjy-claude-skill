# Gymnasium 환경 구현 가이드

강화학습 파이프라인의 실패 대부분은 알고리즘이 아니라 **환경 정의**에서 시작한다.
이 문서는 장비 제어 문제를 **Gymnasium 현행 API**로 구현하는 패턴을 정리한다.
알고리즘/보상/안전의 설계 근거는 `rl-design`의 산출물을 따르고, 여기서는 "코드로 어떻게
정확히 옮기는가"에 집중한다.

> 라이브러리 버전별 세부 인자·클래스명(예: `gymnasium.__version__`, `spaces` 시그니처)은
> **단정하지 말고 context7 MCP(`mcp__plugin_context7_context7__*`) 또는 Gymnasium 공식
> 문서로 확인**한다. 이 문서의 코드는 현행 5-튜플 API 계약을 보여주는 골격이다.

## 1. Gym → Gymnasium 마이그레이션 (가장 먼저 확인)

Gymnasium은 구 OpenAI Gym의 후속 표준이다. **핵심 API 두 곳이 바뀌었다.**

| 항목 | 구 Gym (4-튜플) | Gymnasium (5-튜플) |
|------|-----------------|--------------------|
| `reset` 반환 | `obs` | `(obs, info)` |
| `step` 반환 | `(obs, reward, done, info)` | `(obs, reward, terminated, truncated, info)` |
| 종료 개념 | `done` 하나 | `terminated`(MDP 종료) / `truncated`(시간·스텝 절단) 분리 |
| 시드 | `env.seed(s)` 별도 함수 | `reset(seed=s)` 인자로 통합 |

- **왜 분리가 중요한가 (MAJOR)**: 가치 부트스트래핑이 달라진다.
  - `terminated=True`(목표 도달·실패로 에피소드가 **실제로 끝남**): 다음 상태 가치를
    부트스트랩하지 않는다 → 타깃 `= r`.
  - `truncated=True`(시간 한계 등으로 **인위적으로 끊음**, 물리적으로는 계속됨):
    다음 상태 가치를 부트스트랩한다 → 타깃 `= r + γ·V(s')`.
  - 둘을 `done = terminated or truncated`로 합쳐 부트스트랩을 일괄 처리하면
    시간 절단 에피소드에서 가치가 편향된다. Stable-Baselines3 등 현행 프레임워크는
    5-튜플을 받아 이를 올바르게 처리하므로, **환경이 두 플래그를 정확히 구분해서**
    반환해야 한다.
- 구 Gym 코드/환경을 써야 하면 `shimmy` 또는 `gymnasium.wrappers`의 호환 어댑터로
  감싼다. **신규 코드는 반드시 Gymnasium 5-튜플로 작성**한다.

## 2. 환경 스켈레톤

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np


class PlantEnv(gym.Env):
    """장비 제어 환경 — Gymnasium 현행 API.

    관측/행동은 정규화된 좌표([-1, 1] 등)로 정의하고, 실제 물리 단위 변환은
    환경 내부(_denormalize/_normalize)에서 처리한다.
    """

    metadata = {"render_modes": [], "render_fps": 0}

    def __init__(self, config=None):
        super().__init__()
        cfg = config or {}
        self.dt = cfg.get("dt", 0.001)          # 제어 주기(초) — 시뮬레이터 스텝과 일치
        self.max_steps = cfg.get("max_steps", 1000)

        # 관측 공간: 정규화 권장 (신경망 학습 안정성)
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(6,), dtype=np.float32)
        # 행동 공간: 연속제어는 Box([-1,1]) 권장 → 내부에서 물리 명령으로 역정규화
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(2,), dtype=np.float32)

        self._step_count = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)     # self.np_random 시드 고정 — 재현성의 출발점
        self._step_count = 0
        self._init_plant_state()     # 시뮬레이터/장비 상태 초기화
        obs = self._get_obs()        # observation_space 내부의 np.float32 벡터
        info = {}
        return obs, info             # ← 2-튜플

    def step(self, action):
        self._step_count += 1
        action = np.asarray(action, dtype=np.float32)

        # 1) 안전 계층: 정책 출력을 물리 한계로 클리핑 + shielding (삽입 지점)
        safe_action = self._apply_safety_layer(action)
        # 2) 정규화 행동 → 실제 명령 역정규화 후 플랜트 전진
        self._advance_plant(self._denormalize_action(safe_action))

        obs = self._get_obs()
        reward = self._compute_reward()
        terminated = self._is_terminal()                 # 목표 도달 또는 실패(안전 위반 등)
        truncated = self._step_count >= self.max_steps   # 시간/스텝 한계 절단
        info = {"constraint_violation": self._violation_flag()}
        return obs, reward, terminated, truncated, info  # ← 5-튜플

    # --- 내부 헬퍼 (구현체별로 채운다) ---
    def _init_plant_state(self): ...
    def _advance_plant(self, cmd): ...
    def _get_obs(self) -> np.ndarray: ...
    def _compute_reward(self) -> float: ...
    def _is_terminal(self) -> bool: ...
    def _violation_flag(self) -> bool: ...
    def _denormalize_action(self, a): ...
    def _apply_safety_layer(self, a): ...
```

- `reset`의 `super().reset(seed=seed)` 호출은 **필수** — `self.np_random`(PCG64 기반)이
  시드로 초기화되어 에피소드 무작위성이 재현 가능해진다. 환경 내부의 모든 난수는
  `self.np_random`을 쓴다(전역 `np.random` 금지 — 재현성 깨짐).
- 관측/보상/종료는 반환 직전에 dtype·shape·범위를 지키는지 확인한다(§6 `check_env`).

## 3. 공간(spaces) 정의

| 공간 | 용도 | 예 |
|------|------|-----|
| `spaces.Box(low, high, shape, dtype)` | 연속 관측·연속 행동 | 위치/속도 관측, 토크/속도 지령 |
| `spaces.Discrete(n)` | 이산 행동(단일) | n개 모드/스텝 선택 |
| `spaces.MultiDiscrete([...])` | 다중 이산 행동 | 축별 이산 명령 |
| `spaces.Dict({...})` | 이질적 관측 묶음 | {센서: Box, 모드: Discrete} |

- **연속제어 행동은 `Box(low=-1, high=1)` 정규화 범위를 권장**한다. SAC/TD3/PPO 등은
  정규화된 행동에서 탐색·학습이 안정적이다. 실제 물리 한계로의 변환은 환경 내부에서 한다.
- `dtype`은 관측 `np.float32`, 이산 행동 `np.int64`가 프레임워크 기본과 잘 맞는다.
- 관측에 각도가 있으면 `sin/cos` 인코딩으로 불연속(±π 랩어라운드)을 제거하는 것을 검토한다.

## 4. 관측·행동 정규화

정규화는 학습 안정성에 결정적이다. 두 층위가 있다.

1. **환경 내부 정규화(권장)**: 물리 단위 관측을 대략적 스케일로 나눠 `[-1, 1]` 부근으로
   맞추고, 행동은 `[-1, 1]`을 물리 명령으로 역정규화한다. 물리 지식이 반영되므로 안정적.
2. **러닝 통계 정규화(VecNormalize)**: 관측/보상을 온라인 평균·분산으로 표준화(§5).
   통계를 **반드시 저장·복원**해야 추론 시 정책이 같은 분포를 본다.

```python
def _normalize_obs(self, raw):
    # 물리 관측을 설계 시 정한 스케일로 나눠 [-1, 1] 부근으로 (INFO: 스케일은 설계 근거로 고정)
    return (raw / self._obs_scale).astype(np.float32)

def _denormalize_action(self, a):
    # 정책 출력 [-1, 1] → 실제 명령 범위 [cmd_low, cmd_high]
    a = np.clip(a, -1.0, 1.0)
    return self._cmd_low + (a + 1.0) * 0.5 * (self._cmd_high - self._cmd_low)
```

## 5. 벡터화 (VecEnv)

샘플 수집 처리량을 위해 여러 환경을 병렬로 돌린다.

```python
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize, SubprocVecEnv

# n_envs개 병렬 (SubprocVecEnv=프로세스 병렬, 기본 DummyVecEnv=순차)
vec_env = make_vec_env(lambda: PlantEnv(), n_envs=8, seed=0,
                       vec_env_cls=SubprocVecEnv)
# 관측/보상 러닝 통계 정규화 — 통계는 학습 후 save로 보존
vec_env = VecNormalize(vec_env, norm_obs=True, norm_reward=True, clip_obs=10.0)
```

- **재현성(MAJOR)**: `make_vec_env(seed=...)`로 각 하위 환경에 결정론적 시드를 뿌린다.
  `SubprocVecEnv`는 프로세스별 시드 전파를 확인한다.
- `VecNormalize`는 **학습 후 `vec_env.save("vecnormalize.pkl")`**, 평가/추론 시
  `VecNormalize.load`로 복원하고 `training=False`, `norm_reward=False`로 둔다.
- 실기 장비 래퍼는 병렬화가 불가능한 경우가 많다 — 학습은 시뮬레이터 다중 인스턴스로,
  실기는 단일 환경으로 분리한다.

## 6. 시뮬레이터/장비 래퍼 — 안전 계층 삽입 지점

실제 장비/시뮬레이터는 `gymnasium.Env` 인터페이스로 **감싼다**. 이 래퍼가 안전 계층의
1차 삽입 지점이다.

```python
class SafetyWrapper(gym.Wrapper):
    """행동을 물리 한계로 클리핑하고 안전 규칙 위반을 shield한다.

    학습·평가·배포 모두에서 정책과 플랜트 사이에 항상 존재해야 한다(CRITICAL).
    """

    def step(self, action):
        safe = self._shield(action)              # 위반 행동 → 안전 행동 대체
        obs, reward, terminated, truncated, info = self.env.step(safe)
        info["shield_active"] = bool((safe != action).any())
        if self._hard_limit_violated(obs):       # 하드 안전 한계 초과 → 즉시 종료
            terminated = True
            reward += self._violation_penalty
        return obs, reward, terminated, truncated, info
```

- **시뮬레이터 연동**: `_advance_plant`에서 시뮬레이터를 한 제어 주기(`dt`)만큼 전진시킨다.
  시뮬레이터 스텝 시간과 환경 `dt`, 실기 사이클타임이 **일치**해야 sim-to-real 갭이 준다.
- **장비 연동(실기)**: 관측 취득·명령 인가를 장비 API로 구현하되, 명령 인가 직전 안전
  클리핑/shield를 반드시 통과시키고, 이상 시 폴백 고전 제어기로 전환하는 경로를 둔다.
  실기 전환 자체의 검증은 `rl-test`(rlctrl-evaluator)와 sim-to-real 게이트에서 다룬다.
- WMX3 모션 제어 기반 장비라면 `wmx3app`의 SimuPlatform을 이 래퍼로 감싸 학습·평가
  환경으로 쓸 수 있다(크로스 플러그인 시너지, 강제 아님).

## 7. `check_env`로 규격 검증

구현 직후 반드시 계약 위반을 자동 점검한다.

```python
from gymnasium.utils.env_checker import check_env      # Gymnasium 순정 체커
# from stable_baselines3.common.env_checker import check_env  # SB3 체커(정책 호환성까지 점검)

check_env(PlantEnv())   # 5-튜플/공간 dtype/범위/시드 처리 등 규격 위반을 조기 검출
```

- 자주 걸리는 위반: 관측이 `observation_space`를 벗어남, dtype 불일치(`float64` 반환),
  `reset`이 `info`를 빠뜨림, `step`이 4-튜플 반환, `terminated`/`truncated` 혼동.
- 체커 통과는 최소 조건일 뿐 — 보상/종료의 **의미적** 정확성은 rl-design 설계와
  대조해 사람이 확인한다.

## 8. 체크리스트

- [ ] `reset(seed=...)` → `(obs, info)` 2-튜플, `super().reset(seed=seed)` 호출
- [ ] `step` → `(obs, reward, terminated, truncated, info)` 5-튜플, 두 플래그 의미 구분
- [ ] 관측/행동 dtype·shape·범위가 공간 정의와 일치, 환경 내 난수는 `self.np_random`
- [ ] 행동 정규화([-1,1]) + 내부 역정규화, 관측 정규화(내부 또는 VecNormalize)
- [ ] 안전 래퍼(클리핑·shield·하드 한계 종료)가 정책↔플랜트 사이에 상시 존재
- [ ] 벡터화 시 시드 전파, `VecNormalize` 통계 저장/복원 계획
- [ ] `check_env` 통과, 시뮬레이터 `dt`·실기 사이클타임 일치
- [ ] 버전별 세부 API는 context7/공식 문서로 확인(단정 금지)

---
근거: Gymnasium 공식 API 계약(`reset`/`step` 5-튜플, `spaces`, `env_checker`),
Stable-Baselines3 `VecEnv`/`VecNormalize` 문서. 정확한 버전·시그니처는 context7로 확인.
