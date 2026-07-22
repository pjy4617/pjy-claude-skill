# WMX3 3.6u3 → 3.7 마이그레이션 가이드 (호환성 깨짐 8항목)

기존 3.6u3 기반 애플리케이션 코드를 3.7로 이식할 때 반드시 확인할 **호환성 깨짐 8항목**을
Before/After 코드와 탐지 grep 패턴으로 정리한다.
(근거: WMX3.7 매뉴얼 미러 `kr/release-notes/index.html` v3.6u3→v3.7 사양 변경 절 원문 확인.
다이제스트: `wmx37-user-manual-kr` "v3.6u3 → v3.7 변경 요약")

> 심각도: 컴파일 오류로 드러나는 항목은 MAJOR(수정 강제됨), 컴파일은 통과하지만 **런타임 동작이
> 조용히 바뀌는 항목은 CRITICAL**(놓치기 쉬움)로 표기한다.

## 마이그레이션 절차 요약

1. 아래 8항목의 grep을 전부 실행해 잔존 구 API를 목록화
2. 항목별 Before/After에 따라 치환 (③⑥은 **값 변환/재산정** 동반 — 이름만 바꾸면 안 됨)
3. 빌드 → 컴파일 오류(①②④⑤) 소거 확인
4. 런타임 항목(③⑥⑦⑧)은 시뮬레이터 플랫폼에서 동작 검증 (wmx3-app-test 스킬)

---

## ① ClosedLoop 명명 변경 — MAJOR

클래스 `Command` → `ClosedLoopCommand`, API `StartController` → `StartClosedLoop`,
`StopController` → `StopClosedLoop`. 멤버 함수 명명은 camelCase → **PascalCase**
(원문 예: `Ramp`의 `fromRate`→`FromRate`·`fromTime`→`FromTime`, `PidGain`의
`getProportionalGain`→`GetProportionalGain`, `ClosedLoopOptions`의 `setRamp`→`SetRamp`·
`setControlOutputOffset`→`SetControlOutputOffset`, `ClosedLoopCommand`의 `setTrigger`→`SetTrigger`·
`setOptions`→`SetOptions`).

```cpp
// Before (3.6u3) — 함수명 수준. 구 시그니처는 3.6u3 API Reference에서 확인
// Command cmd; cmd.setTrigger(...); StartController(...); StopController(...);

// After (3.7)
// ClosedLoopCommand cmd;      // 클래스명 변경
// cmd.SetTrigger(...);        // 멤버 PascalCase — 시그니처는 API Reference에서 확인
// StartClosedLoop(...);       // API명 변경
// StopClosedLoop(...);
```

```bash
# 탐지: 구 API명/구 camelCase 멤버 잔존
grep -rn "StartController\|StopController" --include="*.cpp" --include="*.h" --include="*.cs" .
grep -rn "\.setTrigger\|\.setOptions\|\.setRamp\|\.fromRate\|\.fromTime\|\.getProportionalGain" \
    --include="*.cpp" --include="*.cs" .
```

## ② 토크 커맨드 5클래스 삭제 → 빌더 패턴 TrqCommand — MAJOR

v3.6 클래스 **`TriggerTrqCommand` / `RampTimeTrqCommand` / `TriggerRampTimeTrqCommand` /
`RampRateTrqCommand` / `TriggerRampRateTrqCommand` 삭제**. 통합 `TrqCommand`의
`SetTrigger` / `SetRamp` / `SetRampRate` / `SetRampTime` / `SetMaxMotorSpeed` 메서드 사용.
함수 대체(원문 확인):

| v3.6 함수 | v3.7 대체 |
|-----------|-----------|
| `StartRampTimeTrq`, `StartRampRateTrq` | `StartTrq` (+ `SetRamp` 사용) |
| `StartPosToRampTimeTrq`, `StartPosToRampRateTrq` | `StartPosToTrq` (+ `SetRamp` 사용) |
| `StartVelToRampTimeTrq`, `StartVelToRampRateTrq` | `StartVelToTrq` (+ `SetRamp` 사용) |

```cpp
// Before (3.6u3) — 함수명 수준. 구 클래스 멤버 구성은 3.6u3 API Reference에서 확인
// RampTimeTrqCommand trq;  ... StartRampTimeTrq(...);

// After (3.7) — 빌더 패턴. 각 Set* 메서드의 정확한 시그니처는 API Reference에서 확인
// Torque::TrqCommand trq;
// trq.axis = 0;
// trq.torque = 100;                 // (tutorial3-7에서 확인된 기본 멤버)
// trq.SetRamp(/* Ramp — ③ 참조. API Reference에서 시그니처 확인 */);
// err = wmxlib_cm.torque->StartTrq(&trq);
```

```bash
# 탐지: 삭제된 클래스/대체된 함수 잔존 (컴파일 오류로도 드러남)
grep -rn "TriggerTrqCommand\|RampTimeTrqCommand\|RampRateTrqCommand" \
    --include="*.cpp" --include="*.h" --include="*.cs" .
grep -rn "StartRampTimeTrq\|StartRampRateTrq\|StartPosToRampTimeTrq\|StartPosToRampRateTrq\|StartVelToRampTimeTrq\|StartVelToRampRateTrq" \
    --include="*.cpp" --include="*.cs" .
```

## ③ 토크 램프 시간 단위: 사이클 수(uint) → 초(double) — CRITICAL

v3.6은 `rampCycleTime`으로 램프 시간을 **인터럽트 사이클 수**로 지정했으나, v3.7은
`Ramp::FromTime`으로 **초 단위(double)** 지정. **이름 치환만 하고 값을 그대로 두면 램프 시간이
완전히 달라진다** (컴파일로 잡히지 않는 값 의미 변화).

변환식(릴리즈노트 원문): `timeSeconds = rampCycleTime * interruptPeriod_ms / 1000.0`
(`interruptPeriod_ms` = 인터럽트 주기 밀리초). 원문 예: 주기 1ms·500사이클 → `500 * 1 / 1000.0 = 0.5초`.

```cpp
// Before (3.6u3): 램프 시간 500 "사이클" (주기 1ms 가정 = 0.5초)
// cmd.rampCycleTime = 500;   // unsigned int, 사이클 수

// After (3.7): 초 단위 double로 재산정하여 지정
// Ramp ramp = Ramp::FromTime(0.5);   // 500사이클 × 1ms ÷ 1000 = 0.5초
//                                    // FromTime의 정확한 시그니처는 API Reference에서 확인
// trq.SetRamp(ramp);
```

```bash
# 탐지: 구 멤버명 잔존 + 사이클 수로 보이는 정수 리터럴 램프 값
grep -rn "rampCycleTime" --include="*.cpp" --include="*.h" --include="*.cs" .
grep -rn "SetRampTime\s*(\s*[0-9]\{2,\}\s*)" --include="*.cpp" --include="*.cs" .   # 수십 이상 정수 → 사이클 값 의심
```

## ④ 토크 제한·최대 모터 속도 함수: Torque::/Velocity:: → Config:: — MAJOR

축 레벨 파라미터이므로 Config 클래스로 이동(원문 확인):

| v3.6 | v3.7 |
|------|------|
| `Torque::SetMaxTrqLimit` / `GetMaxTrqLimit` | `Config::SetMaxTrqLimit` / `GetMaxTrqLimit` |
| `Torque::SetPositiveTrqLimit` / `GetPositiveTrqLimit` | `Config::SetPositiveTrqLimit` / `GetPositiveTrqLimit` |
| `Torque::SetNegativeTrqLimit` / `GetNegativeTrqLimit` | `Config::SetNegativeTrqLimit` / `GetNegativeTrqLimit` |
| `Velocity::SetMaxMotorSpeed` / `GetMaxMotorSpeed` | `Config::SetMaxMotorSpeed` / `GetMaxMotorSpeed` |

```cpp
// Before (3.6u3)
// err = wmxlib_cm.torque->SetMaxTrqLimit(...);
// err = wmxlib_cm.velocity->SetMaxMotorSpeed(...);

// After (3.7) — CoreMotion의 config 하위에서 호출 (tutorial3-8의 config-> 접근과 동일 계열)
// err = wmxlib_cm.config->SetMaxTrqLimit(...);    // 시그니처는 API Reference에서 확인
// err = wmxlib_cm.config->SetMaxMotorSpeed(...);
```

```bash
# 탐지: torque/velocity 경유의 제한·속도 함수 호출 잔존
grep -rn "torque->Set.*TrqLimit\|torque->Get.*TrqLimit\|velocity->SetMaxMotorSpeed\|velocity->GetMaxMotorSpeed" \
    --include="*.cpp" .
grep -rn "Torque\.\(Set\|Get\).*TrqLimit\|Velocity\.\(Set\|Get\)MaxMotorSpeed" --include="*.cs" .
```

## ⑤ ApiBuffer 제어 함수 사양 변경 — MAJOR (일부 CRITICAL)

원문 확인 4가지:

1. **조건부 동작 명확화**: `Execute`/`Halt`/`Clear`/`Rewind`를 **기록 중인 채널**에서 호출하면
   `AlreadyRecordingForSpecifiedChannel` 오류 반환. 기록 중이 아닌 채널이면 다른 채널 기록 중일 때
   버퍼에 기록되고, 기록 비활성 시 즉시 실행. (기존 코드의 암묵 가정이 깨질 수 있음 — CRITICAL)
2. **`Rewind`에 `blockIndex` 매개변수 추가**(기본값 0) — 지정 블록부터 부분 재실행.
   범위 초과 시 신설 `RewindBlockIndexOutOfRange` 오류 (⑥의 시프트 원인).
3. **멀티채널 함수 통합**: `ExecuteMultipleChannel`/`HaltMultipleChannel`/`ClearMultipleChannel`/
   `RewindMultipleChannel` → `ApiBufferChannelSelection` 매개변수를 받는 오버로드된
   `Execute`/`Halt`/`Clear`/`Rewind`로 변경.
4. **`FlowIf` 다중조건 오버로드의 2번째 매개변수**: `ApiBufferCondition*` → `ApiBufferMultiCondition*`
   (AND/OR/XOR/NOT 다중조건 트리, 대기 절에도 적용 — 다이제스트는 `Wait`도 동일 계열 변경으로 요약).
   **2번째 인수로 `ApiBufferCondition*`을 전달하던 기존 코드는 업데이트 필요.**

```cpp
// Before (3.6u3)
// err = apiBuf.ExecuteMultipleChannel(...);          // 멀티채널 전용 함수
// err = apiBuf.FlowIf(ch, cond, ...);                // 2번째 인수 ApiBufferCondition*

// After (3.7) — 정확한 시그니처는 API Reference에서 확인
// err = apiBuf.Execute(/* ApiBufferChannelSelection */);   // 오버로드로 통합
// err = apiBuf.FlowIf(ch, /* ApiBufferMultiCondition* */ ...); // 다중조건 트리
```

```bash
# 탐지
grep -rn "ExecuteMultipleChannel\|HaltMultipleChannel\|ClearMultipleChannel\|RewindMultipleChannel" \
    --include="*.cpp" --include="*.cs" .
grep -rn "FlowIf\|ApiBufferCondition" --include="*.cpp" --include="*.cs" .   # 2번째 인수 타입 수동 확인
grep -rn "StartRecordBufferChannel" --include="*.cpp" --include="*.cs" .     # 기록 중 Execute 호출 경로 수동 확인
```

## ⑥ 오류 코드 값 시프트 — CRITICAL

`RewindBlockIndexOutOfRange`가 **0x12006 위치에 삽입**되어 후속 API 버퍼 오류 코드 정수값이
**+1씩 이동**. 원문 예: `AlreadyRecordingForSpecifiedChannel` **73734 → 73735**.
심볼 상수 비교 코드는 무영향, **정수 하드코딩 파서/매핑 테이블은 조용히 오동작**한다.

```cpp
// Before (3.6u3) — 위험 패턴
// if (err == 73734) { /* AlreadyRecording... 처리 — 3.7에서는 다른 오류를 잡게 됨 */ }

// After (3.7) — 심볼 상수로 비교
// if (err == ErrorCode::AlreadyRecordingForSpecifiedChannel) { ... }
//     // 열거자 명칭/소속은 API Reference(오류 코드)에서 확인
```

```bash
# 탐지: 오류코드로 의심되는 정수 리터럴 (상세는 error-handling.md §6)
grep -rn "7373[0-9]\|0x1200[0-9]" --include="*.cpp" --include="*.cs" --include="*.h" .
grep -rn "err\s*==\s*[0-9]\{3,\}" --include="*.cpp" --include="*.cs" .
```

## ⑦ 리미트 스위치 유형(LS Type) 기본값: None → Dec — MAJOR

리미트 스위치 해제 시 위치 오차를 최소화하기 위해 기본값이 `None`에서 `Dec`(감속 정지)로 변경
(원문 확인). **LS Type을 명시 설정하지 않던 코드는 리미트 스위치 트리거 시 축 정지 거동이 바뀐다**
(컴파일 무영향·런타임 거동 변화). 3.6u3의 `None` 거동에 의존했다면 명시적으로 파라미터를 설정할 것.

```cpp
// Before (3.6u3): LS Type 미설정 → 기본 None (엔진 측 무동작)
// After (3.7):   LS Type 미설정 → 기본 Dec (감속 정지)
// 기존 거동 유지가 필요하면 축 파라미터에서 LS Type을 명시 설정
//   (파라미터 명칭·설정 함수는 매뉴얼 리미트 스위치 토픽/API Reference에서 확인)
```

```bash
# 탐지: LS Type을 명시 설정하는 코드가 있는지 (없으면 기본값 변화 영향 검토 대상)
grep -rni "lsType\|LimitSwitchType\|LS Type" --include="*.cpp" --include="*.cs" --include="*.xml" .
```

## ⑧ SetCommandPos / SetFeedbackPos 동시 호출 시 에러 — MAJOR

두 함수를 **동일 타이밍에 호출하면 에러를 반환**하도록 변경(원문: "두 함수의 특성상 동일 타이밍에
호출할 경우 문제가 발생할 수 있습니다"). 3.6u3에서 두 호출을 연달아/병렬로 수행하던 코드는
v3.7에서 오류를 받게 된다 → 순차 호출 + 각 반환값 확인으로 수정. 지령·피드백을 함께 맞추려면
`SetCommandPosToFeedbackPos`(원문 블로킹 함수 목록에서 존재 확인) 사용을 검토 —
용법은 API Reference에서 시그니처 확인.

```cpp
// Before (3.6u3): 무확인 연속 호출 (스레드 경합 포함)
// home->SetCommandPos(...); home->SetFeedbackPos(...);   // 동시 실행 가능성

// After (3.7): 순차 + 반환값 확인, 동시 호출 경로 제거
// err = home->SetCommandPos(...);  if (err != ErrorCode::None) { ... }
// err = home->SetFeedbackPos(...); if (err != ErrorCode::None) { ... }
```

```bash
# 탐지: 두 함수의 사용 지점을 모두 나열해 동시 호출 가능성(멀티스레드 포함) 수동 확인
grep -rn "SetCommandPos\|SetFeedbackPos" --include="*.cpp" --include="*.cs" .
```

---

## 마이그레이션 완료 체크리스트

- [ ] ①~⑧ 탐지 grep 전부 실행, 히트 0 또는 전 건 수정 완료
- [ ] ③ 램프 시간 값을 사이클→초로 **재산정**했는가 (이름만 치환하지 않았는가)
- [ ] ⑥ 로그 파서/매핑 테이블의 정수 오류코드를 v3.7 기준으로 재생성했는가
- [ ] ⑦ LS Type 기본값 변화의 거동 영향을 검토했는가
- [ ] 빌드 통과 + 시뮬레이터 플랫폼 회귀 테스트 통과 (wmx3-app-test)

---
출처: WMX3.7 매뉴얼 미러 `kr/release-notes/index.html` v3.7 사양 변경 절(전 항목 원문 확인),
다이제스트 `wmx37-user-manual-kr` "v3.6u3 → v3.7 변경 요약". 구 API(3.6u3)의 정확한 시그니처는
3.6u3 API Reference, 신 API(3.7)는 3.7 API Reference(`api/html/`)에서 확인할 것.
