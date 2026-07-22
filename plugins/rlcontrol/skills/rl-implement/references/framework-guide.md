# RL 프레임워크 비교·선택 가이드

강화학습 구현은 "알고리즘을 처음부터 짤 것인가, 검증된 프레임워크를 쓸 것인가"의 선택에서
시작한다. 장비 제어 상용 프로젝트에서는 **재현성·유지보수성·검증 용이성**이 최우선이므로,
특별한 이유가 없으면 검증된 프레임워크(기본 Stable-Baselines3)를 쓴다.

> 각 라이브러리의 정확한 버전·설치 명령·클래스/인자 시그니처·지원 알고리즘 목록은
> **context7 MCP(`mcp__plugin_context7_context7__*`) 또는 각 공식 문서로 확인**한다.
> 이 문서는 "무엇을 언제 고르는가"의 선택 기준이며, API 세부를 단정하지 않는다.

## 1. 프레임워크 카탈로그

| 프레임워크 | 성격 | 백엔드 | 대표 알고리즘 | 언제 쓰나 |
|-----------|------|--------|--------------|-----------|
| **Stable-Baselines3 (SB3)** | 생산 기본·검증된 구현 | PyTorch | PPO, A2C, SAC, TD3, DDPG, DQN | **첫 선택.** Gymnasium 지원, VecNormalize·콜백·로깅 완비 |
| **SB3-Contrib** | SB3 확장 | PyTorch | TQC, QR-DQN, RecurrentPPO, ARS, TRPO, MaskablePPO | SB3에 없는 알고리즘(분포형 TQC/QR-DQN·순환 정책·행동 마스킹) |
| **RL Baselines3 Zoo** | SB3용 학습 프레임워크·튜닝된 하이퍼파라미터 | PyTorch | (SB3/Contrib 래핑) | 하이퍼파라미터 시작점·Optuna 튜닝·재현 스크립트 |
| **CleanRL** | 단일 파일 참조 구현 | PyTorch | PPO, SAC, TD3, DDPG, DQN 등 | 알고리즘을 깊이 커스터마이즈·연구·정확히 이해해야 할 때 |
| **Tianshou** | 모듈화된 연구용 라이브러리 | PyTorch | 광범위(온/오프폴리시·오프라인) | 유연한 실험 구성·커스텀 트레이너가 필요할 때 |
| **Ray RLlib** | 분산·대규모 | PyTorch/TF | 광범위(PPO, SAC, IMPALA, APPO 등) | 대규모 분산 학습·멀티에이전트·클러스터 확장 |
| **d3rlpy** | 오프라인 RL 전문 | PyTorch | CQL, IQL, BCQ, TD3+BC, BEAR 등 | 로그 데이터만 있고 온라인 탐색 불가할 때 |
| **omnisafe / safety-gymnasium** | Safe RL 전문 | PyTorch | CPO, Lagrangian-PPO/SAC 등 제약 RL | 안전 제약(제약 MDP)이 학습 목표에 직접 들어갈 때 |

- **온라인·연속제어 제어 문제 기본값**: SB3의 SAC(샘플효율·안정성) 또는 PPO(견고·튜닝 관대).
  분포형이 필요하면 SB3-Contrib의 TQC.
- **이산 행동**: SB3 PPO 또는 DQN 계열(분포형은 SB3-Contrib QR-DQN).
- **로그 데이터만·탐색 불가**: d3rlpy(오프라인 RL) — 실기에서 새 데이터를 못 모으는 상황.
- **안전 제약이 강함**: omnisafe/safety-gymnasium의 제약 RL + 환경측 shielding 병용.
- **분산·대규모 병렬**: Ray RLlib.

## 2. 선택 기준

| 질문 | 판단 |
|------|------|
| 상용·유지보수 중심인가? | 예 → **SB3(+Contrib)**. 검증된 구현·문서·커뮤니티 |
| 알고리즘 내부를 바꿔야 하나? | 예 → CleanRL(단일 파일)·Tianshou(모듈화). 아니오 → SB3 |
| 온라인 탐색이 가능한가(시뮬레이터 有)? | 아니오(로그만) → d3rlpy 오프라인 RL |
| 안전 제약이 학습 목표인가? | 예 → omnisafe + 환경 shielding |
| 학습 규모가 단일 머신을 넘는가? | 예 → Ray RLlib |
| 순환 정책(부분관측)·행동 마스킹이 필요한가? | 예 → SB3-Contrib(RecurrentPPO/MaskablePPO) |

- 팀에 검증·리뷰 인력이 얇을수록 **표준 프레임워크(SB3)**로 수렴하는 것이 안전하다.
  자체 구현은 미묘한 버그(부트스트랩·정규화·타깃 네트워크)로 재현성을 해치기 쉽다.
- 프레임워크 선택은 되돌리기 비싸다 — 환경(Gymnasium)만 표준을 지키면 프레임워크 간
  이식은 상대적으로 쉬우므로, **환경은 프레임워크 독립적으로** 설계한다(`environment-design.md`).

## 3. 최소 학습 예제 (SB3 SAC)

연속제어 기본값으로 SAC(Haarnoja et al. 2018)를 SB3로 학습하는 최소 골격.

```python
# SB3 SAC 최소 학습 — 환경은 environment-design.md의 Gymnasium 5-튜플 환경(PlantEnv)
from stable_baselines3 import SAC
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback

SEED = 0

# 1) 벡터화 + 관측/보상 정규화
train_env = make_vec_env(lambda: PlantEnv(), n_envs=4, seed=SEED)
train_env = VecNormalize(train_env, norm_obs=True, norm_reward=True)

# 2) 평가 전용 환경 (학습 통계로 정규화, 보상 정규화·학습 갱신은 끔)
eval_env = make_vec_env(lambda: PlantEnv(), n_envs=1, seed=SEED + 100)
eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=False, training=False)

# 3) 모델 — 하이퍼파라미터는 SB3 공식 문서/rl-zoo 기본값에서 출발 (context7로 확인)
model = SAC(
    "MlpPolicy", train_env, seed=SEED, verbose=1,
    tensorboard_log="./tb/",
)

# 4) 콜백 — 주기적 결정론적 평가 + 최고 성능/주기 체크포인트 저장
eval_cb = EvalCallback(eval_env, best_model_save_path="./ckpt/best/",
                       eval_freq=10_000, n_eval_episodes=10, deterministic=True)
ckpt_cb = CheckpointCallback(save_freq=50_000, save_path="./ckpt/periodic/")

# 5) 학습 → 정책·정규화 통계 저장(추론 시 동일 통계 필수)
model.learn(total_timesteps=200_000, callback=[eval_cb, ckpt_cb])
model.save("sac_plant")
train_env.save("vecnormalize.pkl")
```

```python
# 알고리즘 교체는 클래스만 바꾼다(환경·파이프라인 재사용)
from stable_baselines3 import PPO, TD3, DQN     # 이산은 DQN/PPO
from sb3_contrib import TQC, QRDQN, RecurrentPPO  # 분포형·순환 정책 (SB3-Contrib)
```

- **정규화 통계(`vecnormalize.pkl`)를 저장하지 않으면 추론이 무너진다** — 평가·배포에서
  반드시 복원한다(`VecNormalize.load` → `training=False`, `norm_reward=False`).
- 하이퍼파라미터의 정확한 인자명·기본값은 프레임워크·버전마다 다르다 → context7/공식 문서 확인.
- 다중 시드 학습·통계·평가 프로토콜은 `training-and-deployment.md`와 `rl-test`가 담당한다.

## 4. 프레임워크 공통 재현성·검증 유의

- **버전 고정**: 프레임워크·PyTorch·Gymnasium·CUDA 버전을 잠근다(예: lock 파일).
  버전 차이가 결과 차이의 흔한 원인이다(MAJOR).
- **시드 3층 고정**: 라이브러리 전역 시드 + 프레임워크 `seed=` + 환경 `reset(seed=)`.
- **로깅**: TensorBoard(내장) 또는 W&B로 학습곡선·손실·평가 보상을 남긴다.
- **오프라인/Safe RL은 별도 검증 관점**: 오프라인은 분포 밖(OOD) 행동 과대평가,
  Safe RL은 제약 위반율을 학습 지표로 함께 본다 — 세부는 rl-design/rl-test 참조.

---
근거: Stable-Baselines3·SB3-Contrib·RL Zoo·CleanRL·Tianshou·Ray RLlib·d3rlpy·
omnisafe/safety-gymnasium 공식 프로젝트의 확립된 성격·지원 알고리즘.
정확한 버전·설치·시그니처는 context7 또는 각 공식 문서로 확인.
