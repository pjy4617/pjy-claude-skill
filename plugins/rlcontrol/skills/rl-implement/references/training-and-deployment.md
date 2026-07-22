# 학습 파이프라인 · 실시간 추론 배포 가이드

이 문서는 두 가지를 다룬다. (1) **재현 가능한 학습 파이프라인**과 (2) 학습된 정책을
**안전하게 실기에 배포**하는 절차. 장비 제어에서는 "돌아가는 학습"보다 "재현되고, 검증된
뒤, 안전 계층을 통과해 배포되는 정책"이 목표다.

> 라이브러리 버전별 세부(콜백 인자·ONNX export 헬퍼·`predict` 시그니처)는 **단정하지 말고
> context7 MCP(`mcp__plugin_context7_context7__*`) 또는 공식 문서로 확인**한다.

## 1. 학습 파이프라인

### 1.1 하이퍼파라미터 관리

- 하이퍼파라미터는 코드에 흩뿌리지 말고 **하나의 설정(dict/YAML)**으로 모은다 →
  실험 추적·재현·튜닝이 쉬워진다.
- 시작점은 프레임워크 기본값·RL Zoo의 튜닝된 값에서 출발하고, 알고리즘별 감도가 큰
  파라미터(SAC: `learning_rate`·`tau`·`gamma`·`buffer_size`·엔트로피 계수, PPO:
  `n_steps`·`batch_size`·`clip_range`·`gae_lambda`)부터 조정한다.
- 정확한 인자명·기본값은 버전마다 다르므로 context7/공식 문서로 확인한다.

```python
CONFIG = {
    "algo": "SAC",
    "total_timesteps": 1_000_000,
    "n_envs": 4,
    "seed": 0,
    "hyperparams": {          # 값은 공식 문서/rl-zoo 기본값에서 출발 → 실험으로 조정
        "learning_rate": 3e-4,
        "gamma": 0.99,
        "tau": 0.005,
        "buffer_size": 1_000_000,
    },
}
```

### 1.2 정규화 통계 저장/복원 (CRITICAL)

`VecNormalize`의 관측/보상 통계는 정책의 일부다. 저장하지 않으면 추론이 무너진다.

```python
# 학습 종료 시
model.save("policy.zip")
train_env.save("vecnormalize.pkl")     # 관측/보상 러닝 통계

# 평가/추론 시 — 반드시 같은 통계로 복원
from stable_baselines3.common.vec_env import VecNormalize
eval_env = VecNormalize.load("vecnormalize.pkl", base_env)
eval_env.training = False              # 통계 갱신 중지
eval_env.norm_reward = False           # 평가/추론에서는 보상 정규화 끔
```

### 1.3 콜백 (평가·체크포인트)

```python
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback

# 주기적 결정론적 평가 + 최고 성능 모델 저장
eval_cb = EvalCallback(eval_env, best_model_save_path="./ckpt/best/",
                       log_path="./eval_logs/", eval_freq=10_000,
                       n_eval_episodes=10, deterministic=True)
# 주기적 스냅샷 (학습 중단·롤백 대비)
ckpt_cb = CheckpointCallback(save_freq=50_000, save_path="./ckpt/periodic/",
                             save_replay_buffer=False)
model.learn(total_timesteps=CONFIG["total_timesteps"], callback=[eval_cb, ckpt_cb])
```

- 평가는 **`deterministic=True`**(정책 평균 행동)로 한다 — 학습 시의 탐색 노이즈를 뺀
  실제 배포 성능에 가깝다.
- 평가 환경 시드는 학습과 **다르게** 둔다(과적합/시드 누수 방지).
- **best 모델과 통계의 시점 불일치 주의**: `best_model.zip`은 학습 **중간** 시점의 정책인데,
  학습 종료 후 저장한 `vecnormalize.pkl`은 **종료** 시점 통계다(통계는 학습 내내 갱신).
  best 모델을 배포 대상으로 고르면 best 갱신 시점에 통계도 함께 저장하는 커스텀 콜백으로
  정책-통계 시점을 일치시킨다 — "통계는 정책의 일부"(§1.2)의 시간축 버전.

### 1.4 로깅

- TensorBoard(SB3 내장, `tensorboard_log=`) 또는 W&B로 학습곡선·손실·평가 보상·
  제약 위반율을 남긴다. 정성 판단이 아니라 **곡선과 통계**로 수렴을 판정한다.
- 안전-관련 지표(shield 발동률·하드 한계 접근·제약 위반)를 `info`로 흘려 로깅한다.

### 1.5 다중 시드 재현성 (MAJOR — RL의 핵심 함정)

Deep RL은 **시드에 따라 결과 분산이 크다**(Henderson et al. 2018, "Deep RL That Matters").
단일 시드의 좋은 결과는 운일 수 있다. 따라서:

- **최소 5~10개 시드로 학습**하고, 평균±신뢰구간으로 성능을 보고한다(세부 통계는 `rl-test`).
- 시드는 3층에서 고정한다.

```python
import random, numpy as np, torch

def set_global_seeds(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    # 완전 결정론이 필요하면(성능 저하 감수): torch.use_deterministic_algorithms(True)

# 학습 루프: 시드마다 별도 실행 디렉토리로 분리
for seed in [0, 1, 2, 3, 4]:
    set_global_seeds(seed)
    env = make_vec_env(lambda: PlantEnv(), n_envs=4, seed=seed)
    env = VecNormalize(env, norm_obs=True, norm_reward=True)
    model = SAC("MlpPolicy", env, seed=seed, tensorboard_log=f"./tb/seed{seed}/")
    model.learn(total_timesteps=CONFIG["total_timesteps"])
    model.save(f"policy_seed{seed}.zip")
    env.save(f"vecnormalize_seed{seed}.pkl")
```

- 완전한 비트 단위 재현은 GPU 비결정성 등으로 어렵다 — 버전 고정 + 시드 고정 +
  통계적 보고(다중 시드)로 재현성을 확보한다.

## 2. 실시간 추론 배포

### 2.1 추론 (결정론적 정책)

```python
# 배포 시에는 탐색을 끈 결정론적 정책
obs = eval_env.reset()                                   # VecEnv.reset()은 obs만 반환
while running:
    action, _ = model.predict(obs, deterministic=True)   # 평균 행동
    # eval_env는 §1.2의 VecNormalize.load로 만든 SB3 VecEnv → 4-튜플 규약(5-튜플 아님)
    obs, rewards, dones, infos = eval_env.step(action)
    # 에피소드 종료는 dones 배열, 시간 절단은 infos[i].get("TimeLimit.truncated")로 판별
```

- **정규화 통계 복원**을 반드시 선행한다(§1.2). 통계 없이 `predict`하면 잘못된 관측 분포.
- `predict`의 정확한 반환·인자는 버전마다 다르므로 context7/공식 문서로 확인한다.

### 2.2 ONNX export — 프레임워크 의존성 제거

실기 제어 루프에 PyTorch/SB3 전체를 얹기보다, **정책 네트워크만 ONNX로 export**해
경량 런타임(onnxruntime)으로 추론하면 의존성·지연이 준다.

```python
import torch

class PolicyWrapper(torch.nn.Module):
    """SB3 정책의 결정론적 행동만 뽑는 얇은 래퍼 → ONNX export 대상."""
    def __init__(self, policy):
        super().__init__()
        self.policy = policy
    def forward(self, obs):
        # 결정론적 행동 텐서만 반환 — SAC/TD3 계열 정책 기준.
        # PPO/A2C의 ActorCriticPolicy.forward는 (actions, values, log_prob) 3-튜플을
        # 반환하므로 이 래퍼를 그대로 쓰면 ONNX가 3출력이 된다 → actor(행동 분포 평균)만
        # 분리 추출할 것. (버전별 내부 API는 공식 문서/context7로 확인)
        return self.policy(obs, deterministic=True)

wrapper = PolicyWrapper(model.policy)
dummy = torch.zeros(1, model.observation_space.shape[0])
torch.onnx.export(wrapper, dummy, "policy.onnx",
                  input_names=["obs"], output_names=["action"],
                  opset_version=17)     # opset·SB3 내부 API는 context7/공식 문서로 확인
```

```python
# 실기측 경량 추론 (프레임워크 의존성 없이)
import onnxruntime as ort, numpy as np
sess = ort.InferenceSession("policy.onnx")

def infer(obs_raw):
    obs = normalize(obs_raw)                       # 저장한 통계로 동일 정규화 (필수)
    action = sess.run(None, {"obs": obs[None].astype(np.float32)})[0][0]
    return apply_safety_layer(action)              # 배포 루프에도 안전 계층 재적용
```

- **정규화 통계도 함께 배포**한다 — export 대상은 네트워크뿐이므로 관측 정규화는
  실기측에서 저장된 통계로 재현해야 한다.
- **행동 재스케일 주의**: SB3 `predict()`는 정책 출력(tanh로 [-1,1] 압착)을 action_space
  경계로 재스케일해 돌려준다. 이 플러그인 권장대로 행동공간이 [-1,1]이면 항등이라 문제없지만,
  다른 Box 범위를 쓰면 ONNX 추출 정책의 출력([-1,1])과 `predict()` 출력이 달라진다 —
  실기측 역스케일에 같은 매핑을 반영해야 패리티 테스트가 통과한다.
- ONNX export 절차·SB3 내부 정책 API는 버전 의존적이다 → context7/공식 문서로 확인.

### 2.3 추론 지연 예산 (CRITICAL)

- 제어 루프 주기(예: 1kHz → 1ms) 안에 **관측 취득 + 추론 + 안전 계층 + 명령 인가**가
  모두 들어가야 한다. 추론 지연을 실측하고 예산을 잡는다.
- 지연이 예산을 넘으면: 네트워크 축소·양자화·추론 스레드 분리·주기 완화(예: 정책은
  저주기, 하위 폴백 제어기는 고주기)로 대응한다.
- 지연 초과·추론 실패는 **폴백 전환 트리거**로 처리한다(§2.4).

### 2.4 안전 계층·폴백 (배포 루프)

학습 시 환경 래퍼에 넣은 안전 계층(`environment-design.md` §6)을 **배포 루프에서도 재적용**한다.

- **action clipping / shielding**: 정책 출력은 항상 물리 한계로 클리핑하고, 안전 규칙
  위반 행동은 안전 행동으로 대체.
- **폴백 고전 제어기 상시 대기**: 정책 이상·추론 지연 초과·관측 이상(센서 결측/범위 초과)
  시 즉시 PID/LQR 등 폴백으로 전환. 폴백은 학습과 무관하게 항상 동작 가능해야 한다.
- **비상 정지**: 하드 안전 한계 접근 시 정책과 무관하게 정지.
- **사람 감독**: 초기 실기 전환은 사람 감독 하 가드 운전으로 시작.

### 2.5 학습 ↔ 실기 안전 검증 게이트

시뮬 성능이 곧 실기 성능이 아니다(**sim-to-real 갭**). 배포 전 게이트를 통과시킨다.

1. **시뮬 검증(rl-test)**: 다중 시드 성능·베이스라인 대비·제약 위반율·외란/파라미터
   강건성(도메인 랜덤화)·워스트케이스가 기준을 만족하는가.
2. **정규화·ONNX 정합**: export한 정책이 원 정책과 동일 행동을 내는지(수치 오차 허용범위),
   정규화 통계가 배포에 반영됐는지.
3. **지연 예산 실측**: 추론 지연이 제어 주기 예산 안인지.
4. **안전 계층 동작 확인**: 클리핑·shield·폴백·비상 정지가 의도대로 발동하는지(주입 시험).
5. **가드형 실기 전환**: 사람 감독 하 저위험 조건 → 점진 확대. 실기 전환 체크리스트는
   `rl-test`(rlctrl-evaluator)와 sim-to-real 절차를 따른다. WMX3 기반이면 `wmx3-app-test`의
   실기 전환 체크리스트를 원용할 수 있다(크로스 플러그인 시너지, 강제 아님).

> 이 게이트를 통과하지 못한 정책은 실기에 배포하지 않는다. 안전 계층 없는 직배포는 금지(CRITICAL).

## 3. 체크리스트

- [ ] 하이퍼파라미터 단일 설정화, 시작점은 공식 기본값/rl-zoo
- [ ] `VecNormalize` 통계 저장, 평가/추론 시 복원(`training=False`, `norm_reward=False`)
- [ ] EvalCallback(deterministic·다른 시드)·CheckpointCallback·로깅(TensorBoard/W&B)
- [ ] **다중 시드(5~10) 학습**, 3층 시드 고정, 버전 고정
- [ ] 배포는 `predict(deterministic=True)`, ONNX export + 정규화 통계 동반
- [ ] 추론 지연 예산 실측, 안전 계층(클리핑·shield·폴백·비상정지) 배포 루프 재적용
- [ ] 학습↔실기 안전 검증 게이트 통과 후에만 가드형 실기 전환
- [ ] 버전별 세부 API는 context7/공식 문서로 확인(단정 금지)

---
근거: Stable-Baselines3 콜백·VecNormalize·정책 export 문서, PyTorch ONNX export,
"Deep RL That Matters"(Henderson et al. 2018)의 재현성·분산 논점.
정확한 버전·시그니처·export 절차는 context7 또는 공식 문서로 확인.
