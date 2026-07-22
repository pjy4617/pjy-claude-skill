# 크로스 언어 배포 가이드 — Python 학습 → ONNX → C#/C++ 구동 프로그램 추론

RL 학습은 Python 생태계(Gymnasium/SB3/PyTorch)가 사실상 표준이고, 실기 구동 프로그램은
C#/C++이 흔하다. **학습·배포 언어를 분리**해 Python으로 학습하고 정책망만 ONNX로 내보낸 뒤,
C#/C++ 구동 프로그램에서 추론하는 것이 표준·권장 패턴이다(Python을 실기 제어 루프에 얹지 않는다).

> ONNX / ONNX Runtime의 **C++·C# API 클래스·인자·헤더·패키지 세부는 단정하지 말고**
> ONNX Runtime 공식 문서 또는 context7 MCP(`mcp__plugin_context7_context7__*`)로 확인한 뒤
> 확정한다. 아래 코드는 **개념 골격**이며 정확한 시그니처는 배포 버전에서 재검증한다.
> 개념·아키텍처·함정은 확립된 사실로 기술한다.

## 1. 아키텍처

```
[Python: 학습·실험]                 [배포 경계]              [C#/C++: 실기 구동 프로그램]
 Gymnasium 환경                                               관측 수집(센서/모션 상태)
 SB3/PyTorch 학습        ── export ──▶  policy.onnx      ──▶  관측 정규화 (학습과 동일)
 옵티마이저·리플레이·크리틱          (정책망만)                ONNX Runtime 추론
 VecNormalize 통계       ── export ──▶  obs_mean/var          행동 역스케일(→ 물리 지령)
                                        + clip_obs            안전 계층(clip·rate·shield·폴백)
                                                              제어 지령 인가(모션 API)
```

- ONNX로 내보내는 것은 **결정론적 정책망(관측 → 행동 MLP)뿐**이다. 옵티마이저·리플레이
  버퍼·크리틱 네트워크 등 학습 인프라는 배포에 전혀 필요 없다.
- 구동 프로그램은 관측·정규화·추론·역스케일·안전 계층·제어를 모두 자기 언어(C#/C++)로 수행한다.

## 2. 무엇을 export하나

결정론적 정책망(관측→행동)만 ONNX로 내보낸다. export 래퍼 골격과 `torch.onnx.export`
호출은 **`training-and-deployment.md` §2.2**에 이미 있으므로 그것을 참조한다(여기서 재작성하지 않음).
export 절차·opset·SB3 내부 정책 API는 버전 의존적 → context7/공식 문서로 확인한다.

## 3. 정규화 패리티 (CRITICAL)

`VecNormalize`의 관측 mean/var(+`clip_obs`)와 행동 역스케일은 **정책의 일부**다. C#/C++ 추론
전에 학습 때와 **정확히 동일한 정규화**를 재현하지 않으면 정책이 조용히 오작동한다(크래시 없이
성능만 무너져 발견이 늦다). 두 가지 방법:

- **(a) 통계 파일 export + 구동측 재현**: 학습에서 obs mean/var·`clip_obs`(및 행동 스케일)를
  파일(JSON/바이너리)로 내보내고, 구동 프로그램이 매 스텝
  `obs_norm = clip((obs - mean) / sqrt(var + eps), -clip_obs, +clip_obs)`를 계산한다.
  `eps`·클립 경계·dtype(float32) **파라미터는 학습과 동일 값**으로 맞춘다. (판정은 결과의
  비트 일치가 아니라 §8 패리티 테스트의 허용 오차 기준 — 내부 연산 정밀도 차이로
  결과의 비트 단위 일치는 일반적으로 불가능하다.)
- **(b) 정규화·역스케일을 ONNX 그래프에 접합 (권장)**: 정규화·역스케일 연산을 정책망 앞뒤에
  그래프로 합쳐 하나의 ONNX로 만든다. 구동 프로그램은 원시 관측을 넣고 물리 지령을 받으므로
  **정규화 드리프트를 원천 차단**한다. 접합 방법은 export 시점에 결정하고 §8 패리티 테스트로 검증.

## 4. ONNX Runtime C++

실시간 제어에서는 지연·지터가 관건이다. 개념 골격:

```cpp
// 개념 골격 — 정확한 클래스·인자·헤더·네임스페이스는 ONNX Runtime C++ 문서/context7로 확인
#include <onnxruntime_cxx_api.h>          // 헤더 경로·패키지는 배포 버전에서 확인

// [1] 세션은 프로그램 시작 시 1회 생성·재사용 (핫 루프 안에서 생성 금지)
Ort::Env  env(ORT_LOGGING_LEVEL_WARNING, "rlctrl");
Ort::SessionOptions opts;
opts.SetIntraOpNumThreads(1);             // 결정성·지연 안정화(스레드 1)
opts.SetInterOpNumThreads(1);
// CPU EP 기본. GPU/가속 EP는 지연·지터 특성을 재검증한 뒤에만 사용.
// 주의: 모델 경로 인자는 ORTCHAR_T* — Windows 빌드에서는 wide 문자열(L"policy.onnx") 필요.
Ort::Session session(env, ORT_TSTR("policy.onnx"), opts);

// [2] 입출력 텐서 버퍼는 사전 할당 — 핫 루프 내 new/malloc 금지
//     입출력 이름은 export 시 지정한 이름(예: "obs"/"action")과 일치시킨다.
// [3] 매 제어 주기: 관측 정규화 → CreateTensor(사전 할당 버퍼) → session.Run
//     → 출력 역스케일 → 안전 계층. (Run의 정확한 시그니처는 문서 확인)
```

- **세션 1회 생성·재사용**, 입출력 텐서 **버퍼 사전 할당**(핫 루프 내 동적 할당 금지).
- intra/inter-op 스레드를 1로 두어 결정성·지연을 안정화(멀티스레드는 지터를 키운다).
- CPU EP를 기본으로 하고, 가속 EP는 지연/지터를 실측해 예산을 만족할 때만 채택한다.

## 5. ONNX Runtime C#

C#은 관리형(GC) 언어라 **GC 지터**가 실시간의 최대 리스크다. 개념 골격:

```csharp
// 개념 골격 — 정확한 클래스·인자는 ONNX Runtime C#(Microsoft.ML.OnnxRuntime) 문서/context7로 확인
// [1] InferenceSession은 1회 생성·재사용
// [2] DenseTensor<float>·NamedOnnxValue로 입력 구성 → session.Run으로 추론
// [3] 핫 루프 내 할당 금지 — 입출력 버퍼/ArrayPool<float> 재사용
//     GC 지터 억제: Server GC + GCSettings.LatencyMode = SustainedLowLatency
//     WMX3ApiCLR 같은 관리형 경계를 쓸 때는 마샬링 비용·GC 압력을 함께 관리
```

- 핫 루프 내 할당을 없애고(버퍼·`ArrayPool<float>` 재사용), Server GC +
  `GCSettings.LatencyMode = SustainedLowLatency`로 GC 지터를 억제한다.
- **결정성·최저 지터가 필요하면 추론도 C++를 권장**한다(C# GC 지터 리스크를 감수할 수 없을 때).

## 6. 안전 계층은 구동 프로그램 쪽 (CRITICAL)

Python 환경의 SafetyWrapper는 **학습용**이다. 실기 안전은 **C#/C++ 구동 프로그램**에 구현한다.

- action clipping·rate limit·shielding·**폴백 고전 제어기 상시 대기**·watchdog·비상 정지·
  NaN/범위 검사를 구동 프로그램 코드 구조로 강제한다.
- 추론 실패·지연 초과·관측 이상(센서 결측/범위 초과) → 즉시 **폴백 전환**. 폴백은 정책과
  무관하게 항상 동작 가능해야 한다.
- Python에서 검증한 안전 계층 로직을 구동 프로그램 언어로 **이식·재검증**한다(같은 규칙, 다른 구현).

## 7. WMX3 통합 (크로스 플러그인)

대상이 WMX3 모션 제어 기반이면 제어 루프는 다음과 같다(WMX3는 예시 — 도메인 일반성 유지):

```
GetStatus로 관측 수집 → 정규화(§3) → ONNX 추론(§4/§5) → 역스케일 → 안전 계층(§6)
  → 모션 API 지령(속도/토크, Config::/CoreMotion)
```

- 전 과정이 **사이클타임 예산** 안에 끝나야 한다(관측+정규화+추론+안전+지령).
- wmx3app의 초기화/종료 시퀀스·에러 처리·안전 규칙을 준수한다.
- 실기 전환은 rl-test의 **실기 전환 가드 게이트**(다중 시드·배포 구성 그대로 평가·폴백 대기 등)를 따른다.

## 8. 검증

- **(a) 패리티 테스트 (필수)**: 동일 관측 배치에 대해 Python 추론 결과와 C#/C++ 추론 결과가
  허용 오차(예: 1e-5) 내로 일치하는지 확인한다. 정규화(§3)와 ONNX 변환의 회귀를 잡는 1차 방어선.
- **(b) 추론 지연 실측**: 평균·워스트케이스·백분위(p99 등)를 측정해 제어 주기 예산과 대조한다.
- **(c) 가드형 브링업**: 사람 감독 하 저속·소범위로 시작 → 롤백 계획을 갖춘 채 점진 확대.

패리티는 두 단계로 나눠 잡으면 원인 국소화가 쉽다. ① Python 안에서 원 정책 vs onnxruntime
출력을 먼저 대조해 **ONNX 변환 회귀**를 격리하고, ② 같은 고정 관측 배치를 파일로 저장해
C#/C++ 추론과 대조하면 **언어 경계·정규화 재현 회귀**만 남는다.

```python
# 개념 골격 — ① ONNX 변환 패리티(원 정책 vs onnxruntime), 정확한 predict 내부 API는 문서 확인
import numpy as np, onnxruntime as ort

obs_batch = np.random.uniform(-1, 1, size=(256, N_OBS)).astype(np.float32)  # 고정 시드 권장
ref = policy_action(obs_batch)                       # SB3 정책의 결정론적 행동(원본)
sess = ort.InferenceSession("policy.onnx")
got = sess.run(None, {"obs": obs_batch})[0]
assert np.max(np.abs(ref - got)) < 1e-5              # 변환 회귀 방지

# ② obs_batch·기대출력을 파일로 저장 → C#/C++ 구동 프로그램이 같은 배치로 추론해 동일 오차로 대조
np.save("parity_obs.npy", obs_batch); np.save("parity_expected.npy", got)
```

- 관측이 정규화 전 원시값이라면 배치를 **정규화까지 포함**해 저장/대조해 정규화 패리티(§3)도 함께 검증한다.
- 허용 오차·배치 크기는 정책 규모·수치 민감도에 맞춰 정하고, 실패 시 정규화·opset·dtype부터 의심한다.

## 9. 확인 지시

- ONNX Runtime **버전·패키지명·클래스·인자·헤더**(C++ `onnxruntime_cxx_api.h`,
  C# `Microsoft.ML.OnnxRuntime` 등)는 **ONNX Runtime 공식 문서·context7로 확인**한 뒤 확정한다.
- ONNX **opset·export 절차·정책 내부 API**는 `training-and-deployment.md` §2.2 + context7/공식 문서.

---
근거: 학습(Python)·배포(C#/C++) 언어 분리는 산업 실기 배포의 표준 패턴. ONNX Runtime의
C++/C# 런타임 개념(세션 재사용·버퍼 사전 할당·스레드·GC 지터)·정규화 패리티 함정은 확립된 사실.
정확한 API 클래스·인자·버전은 ONNX Runtime 공식 문서 또는 context7로 확인한다.
