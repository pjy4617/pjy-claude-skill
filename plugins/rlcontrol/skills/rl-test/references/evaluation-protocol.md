# RL 정책 성능 평가 프로토콜

> **원칙**: RL 성능 수치는 **고분산·재현성 취약**하다. 단일 실행·최고 실행(cherry-pick) 보고는 신뢰할 수 없다. 이 문서는 장비 제어 실무에서 방어 가능한 성능 주장을 만들기 위한 통계·베이스라인·평가 절차를 정의한다.
> **출처 표기**: 방법론 근거는 Henderson et al. 2018("Deep Reinforcement Learning that Matters"), Agarwal et al. 2021(rliable, "Deep Reinforcement Learning at the Edge of the Statistical Precipice")의 통상 표기로만 인용한다. 라이브러리(rliable·SB3 등) API·버전 세부는 context7 MCP 또는 공식 문서로 확인한다(추측 금지).

## 1. 왜 RL 평가는 특별히 어려운가 (재현성·분산 함정)

- **랜덤 시드 민감성**: 동일 알고리즘·하이퍼파라미터라도 시드만 바꿔도 성능이 크게 갈릴 수 있다(Henderson et al. 2018). 한 시드의 성공은 알고리즘의 성공이 아니다.
- 성능을 좌우하는 숨은 요인: 구현/코드베이스 편차, 하이퍼파라미터, 환경 확률성, 보상 스케일, 평가 예산.
- 흔한 함정:
  - 단일 시드 보고 / 최고 실행만 보고(cherry-pick)
  - 평균만 보고해 분산(불확실성)을 은폐
  - 학습에 쓴 시드로 평가(정보 누수)
  - stochastic 정책으로 평가해 탐색 노이즈를 성능에 혼입
  - 서로 다른 학습 예산·평가 예산을 비교
  - 체리픽된 체크포인트만 보고
- **실무 함의**: 장비에 배포할 정책은 "운 좋은 한 번"이 아니라 **재현 가능한 분포**로 입증해야 한다.

## 2. 다중 시드 (최소 5~10)

- 학습을 서로 다른 랜덤 시드로 **최소 5개, 권장 10개** 반복한다. 안전-크리티컬·실기 배포 후보는 상단(10)을 지향.
- 시드는 **학습 시드와 평가 시드를 분리**한다 — 평가는 학습에 쓰지 않은 held-out 시드/에피소드에서 수행.
- 각 시드마다 동일한 학습 예산(환경 스텝 수)·동일 하이퍼파라미터를 사용한다.
- 시드 수가 적으면(<5) 통계적 결론을 유보하고 "예비 결과"로만 보고한다.

## 3. 집계 통계 — 평균±신뢰구간, IQM/부트스트랩

- 점 추정만 쓰지 말고 **불확실성(신뢰구간)**을 항상 함께 보고한다.
- 기본: **평균±표준편차** 또는 **평균±95% 신뢰구간**(정규 근사 또는 부트스트랩).
- **IQM(Interquartile Mean, 중앙 50% 데이터의 평균)**: 소수 시드에서 평균보다 이상치에 강건하고 중앙값보다 통계적으로 효율적 — rliable(Agarwal et al. 2021) 권장 지표.
- **층화 부트스트랩 신뢰구간(stratified bootstrap CI)**: 시드 수가 적을 때 CI를 신뢰성 있게 추정.
- 추가 rliable 관점: performance profile(성능 분포 곡선), probability of improvement(두 정책 비교 시 개선 확률), optimality gap. rliable 라이브러리 API·버전은 context7/공식 문서로 확인한다.
- **정규화**: 여러 태스크/환경을 묶을 때는 태스크별 정규화 점수(예: 랜덤=0, 기준 컨트롤러=1)로 스케일을 통일한 뒤 집계한다.

## 4. 학습곡선 · 점근 성능 · 샘플 효율 구분

- **학습곡선(learning curve)**: x=환경 스텝(또는 에피소드), y=집계 성능(IQM±CI). 시드 밴드(음영)로 분산을 표시하고, x축은 반드시 동일 예산 기준으로 정렬한다.
- **점근 성능(asymptotic performance)**: 충분히 학습한 뒤 수렴 성능 — "얼마나 잘하나".
- **샘플 효율(sample efficiency)**: 목표 성능 도달까지 필요한 스텝 수 — "얼마나 빨리·적은 데이터로". 실 장비 데이터가 비싼 경우(오프라인/실기 학습) 특히 중요.
- 두 축은 트레이드오프일 수 있으므로 **분리 보고**한다. 실기·오프라인 시나리오면 샘플 효율에 가중한다.

## 5. 베이스라인 설정 (반드시 대비)

성능 수치는 절대값이 아니라 **베이스라인 대비**로 해석한다.

| 베이스라인 | 목적 |
|-----------|------|
| 랜덤 정책 | 하한 — 학습이 실제로 일어났는지 확인 |
| 무학습/초기 정책 | 개선량 측정 기준 |
| 고전 제어기(PID/LQR/MPC) | 실무 대안 — RL이 이걸 못 이기면 도입 근거가 약함(`rl-assess` 게이트와 연결) |
| 기존 배포 정책/컨트롤러 | 회귀 방지 — 새 정책이 현행보다 나은가 |

- 모든 베이스라인은 **동일 환경·동일 평가 프로토콜**로 측정한다.
- 고전 제어기를 못 이기면 정직하게 보고한다 — RL 부적합 신호일 수 있으며 `rl-assess`로 회귀할 근거가 된다.

## 6. deterministic 평가

- 학습은 탐색을 위해 stochastic 정책이지만, **평가·배포는 결정적(deterministic) 정책**으로 측정한다(예: SB3 `predict(obs, deterministic=True)`).
- 이유: 정책 자체 성능을 측정하려면 탐색 노이즈를 제거해야 한다. 단, 환경 확률성은 남으므로 다중 에피소드 평균이 필요하다.
- 평가 롤아웃 골격 (Gymnasium **5-튜플** API):

```python
# deterministic 정책으로 평가 전용 시드에서 다중 에피소드 롤아웃한다.
# 주의: SB3 model.predict(obs, deterministic=True)는 (action, state) 튜플을 반환한다.
#       predict의 정확한 시그니처·반환형은 context7/공식 문서로 확인할 것.
def evaluate_policy_seeds(make_env, policy, eval_seeds, n_episodes=30):
    returns = []                             # 시드별 에피소드 리턴 집계
    for seed in eval_seeds:                   # 학습 시드와 겹치지 않는 평가 전용 시드
        env = make_env()
        for ep in range(n_episodes):
            obs, info = env.reset(seed=seed + ep)   # reset -> (observation, info)
            done = False
            ep_return = 0.0
            while not done:
                action, _ = policy.predict(obs, deterministic=True)  # 평가는 결정적 정책
                obs, reward, terminated, truncated, info = env.step(action)  # 5-튜플
                ep_return += reward
                done = terminated or truncated       # 종료 = terminated 또는 truncated
            returns.append(ep_return)
        env.close()
    return returns                            # 이후 IQM·부트스트랩 CI로 집계(§3)
```

- **평가 에피소드 수**: 환경 확률성이 크면 시드당 수십 에피소드 이상을 권장한다. 결정적 환경이면 적어도 된다.

## 7. 평가 체크리스트

- [ ] 시드 ≥5 (실기 후보 ≥10), 학습/평가 시드 분리
- [ ] 신뢰구간(부트스트랩/IQM) 보고 — 점 추정 단독 금지
- [ ] 학습곡선(동일 예산·시드 밴드) + 점근 성능 + 샘플 효율 분리 보고
- [ ] 베이스라인 4종(랜덤·무학습·고전 제어·기존 정책) 동일 프로토콜로 대비
- [ ] deterministic 평가, 평가 에피소드 수 명시
- [ ] 최고 실행 cherry-pick 금지, 실패 시드 포함 보고
- [ ] 라이브러리(rliable/SB3) API·버전은 context7/공식 문서로 확인
- [ ] 시뮬 성능 ≠ 실기 성능 — 안전·강건성은 `functional-safety-tests.md`로 이어서 검증
