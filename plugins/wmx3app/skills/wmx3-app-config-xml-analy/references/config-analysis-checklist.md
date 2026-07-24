# WMX3 Config Export 분석 체크리스트

> 파라미터 export XML의 **설정 축**을 대상으로 한 안전/일관성 검토 항목.
> 파서(`assets/parse_wmx_config.py`)가 명백한 위험을 자동 플래그하지만, 아래 항목은
> **사람/체크리스트 판정**이 필요한 것들이다. 심각도 4등급을 사용한다.

| 등급 | 의미 | 조치 |
|------|------|------|
| **CRITICAL** | 미정의 동작·안전 파손·0 나눗셈 등 즉시 위험 | 즉시 수정 |
| **MAJOR** | 안전·안정성에 실질 영향(리미트 보호 해제 등) | 실기 적용 전 수정 |
| **MINOR** | 감시 누락·유지보수성 | 검토 후 보완 |
| **INFO** | 참고(설정 특성 안내) | 필요 시 확인 |

자동 플래그와 체크리스트 판정은 **후보**다 — 실기 장비 사양·설계 산출물과 대조해 최종 확정한다.

---

## A. 축 구성 정합성 (AxisParam)

| # | 항목 | 확인 | 심각도 기준 |
|---|------|------|------------|
| A1 | 기어비 분모 0 | `AxisGearRatioDenominator != 0` | 0 → **CRITICAL**(사용자 단위 환산 0 나눗셈) |
| A2 | 기어비 설계 일치 | 설계 산출물의 기어비(분자/분모)와 일치하는가 | 불일치 → **MAJOR** |
| A3 | 단회전 카운트 | `SingleTurnEncoderCount`가 엔코더 사양(예 2^n)과 일치, 0 아님 | 0 → **CRITICAL**, 불일치 → **MAJOR** |
| A4 | 토크 제한 | `MaxTrqLimit`/`Positive`/`Negative`가 장비 허용 토크 이내 | 과도 → **MAJOR**, 근거 불명 → **MINOR** |
| A5 | 최대 속도 | `MaxMotorSpeed`가 모터 정격 이내 | 정격 초과 → **MAJOR** |
| A6 | 축 극성 | `AxisPolarity`가 기구 방향 정의와 일치 | 반대 → **MAJOR**(역주행) |
| A7 | 절대 엔코더 | `AbsoluteEncoderMode`와 원점 전략 일관(절대=원점복귀 불필요) | 불일치 → **MINOR**, 특성 → **INFO** |
| A8 | 지령 모드 | `AxisCommandMode`가 제어 방식(위치/속도/토크)과 일치 | 불일치 → **MAJOR** |

## B. 안전 제한 (LimitParam / MotionParam)

| # | 항목 | 확인 | 심각도 기준 |
|---|------|------|------------|
| B1 | 오버트래블 금지 | `ProhibitOvertravel == 1` (설정 축) | 0 → **MAJOR**(리미트 초과 보호 해제) |
| B2 | 소프트리밋 활성 | `SoftLimitType` 및 양/음 위치가 스트로크 내로 설정 | 전부 0(비활성) → **INFO~MAJOR**(장비 특성에 따라) |
| B3 | 소프트리밋 범위 | `SoftLimitNegativePos < SoftLimitPositivePos`, 스트로크 이내 | 역전/초과 → **MAJOR** |
| B4 | 리미트 감속도 | `LSDec`/`LSSlowDec`가 급정지로 기구 손상 없는 값 | 근거 불명 → **MINOR** |
| B5 | 퀵스톱 감속도 | `QuickStopDec`가 비상 정지에 적절 | 과소 → **MINOR** |

## C. 팔로잉 에러/알람 (AlarmParam)

| # | 항목 | 확인 | 심각도 기준 |
|---|------|------|------------|
| C1 | 위치 팔로잉 에러 감시 | `FollowingErrorStopped`/`Moving` 임계가 0 아님 | 둘 다 0 → **MINOR**(위치 이탈 무감시) |
| C2 | 속도 팔로잉 에러 감시 | `VelFollowingError*` 설정 여부 | 무설정 → **INFO** |
| C3 | 앰프 알람 서보 오프 | `ServoOffDuringAmpAlarm == 1` | 0 → **MAJOR**(알람에도 서보 유지) |
| C4 | 서보온 팔로잉 에러 | `ServoOnFollowingError`가 합리적 | 과대 → **MINOR** |

## D. 원점복귀 (HomeParam)

| # | 항목 | 확인 | 심각도 기준 |
|---|------|------|------------|
| D1 | 원점 방식 | `HomeType`/`HomeDir`가 기구 원점 센서 구성과 일치 | 불일치 → **MAJOR** |
| D2 | 원점 속도 | `HomingVelSlow`/`Fast`(+Acc/Dec)가 안전 범위 | 과속 → **MINOR** |
| D3 | 절대 엔코더 정합 | 절대 엔코더 축이면 원점복귀 방식/오프셋이 일관 | 혼란 설정 → **MINOR** |
| D4 | 기계 끝단 검출 | `MechanicalEndDetection*` 사용 시 토크/시간 임계 타당 | 근거 불명 → **MINOR** |

## E. 갠트리/동기 (SyncParam)

| # | 항목 | 확인 | 심각도 기준 |
|---|------|------|------------|
| E1 | 갠트리 짝 일관 | 갠트리/기어링 마스터-슬레이브 축의 파라미터가 짝으로 일관 | 불일치 → **MAJOR** |
| E2 | Desync 감속도 | `MasterDesyncDec`/`SlaveDesyncDec`가 동기 해제 시 안전 | 근거 불명 → **MINOR** |
| E3 | 갠트리 원점 옵션 | `HomeParam/Gantry*`가 슬레이브 HS/LS/Z 사용과 일관 | 불일치 → **MAJOR** |

## F. 전역 안전 (GlobalParameters)

| # | 항목 | 확인 | 심각도 기준 |
|---|------|------|------------|
| F1 | E-Stop 신호 | 안전 요구가 있으면 `EnableEStopSignal`/주소 설정 | 요구 있는데 미설정 → **MAJOR** |
| F2 | E-Stop 상태 출력 | `EnableEStopStatusSignal` 필요 시 설정 | 미설정 → **INFO** |
| F3 | 플라이트 레코더 | 진단 필요 시 `EnableFlightRecorder`/앰프 알람 트리거 활성 | 진단 어려움 → **INFO** |

## G. 코드와의 대조 (선택 — 프로젝트 소스가 함께 있을 때)

| # | 항목 | 확인 |
|---|------|------|
| G1 | 축 번호 일치 | 설정 축 번호가 코드에서 실제 사용하는 축과 일치(미사용 축에만 설정/설정 축 미사용 방지) |
| G2 | 파라미터 하드코딩 | 코드가 export 파라미터(기어비·토크 제한 등)를 매직 넘버로 중복 하드코딩하지 않는가 |
| G3 | 사용자 단위 전제 | 코드의 위치/속도 지령이 export 기어비가 만드는 사용자 단위 전제와 일치하는가 |

> G 카테고리는 `wmx3-app-review`(코드 검토)와 연계된다. 코드 소스가 함께 제공되면
> 이 export 분석 결과를 근거로 `wmx3-app-review`를 이어서 수행할 수 있다.

---

## 리포트 형식

```
== WMX3 Config Export 분석 결과 ==

대상: temp/wmx_parameters.xml (ver 1.00 / 128축 중 설정 5축: 0~4)

[설정 축 개요]
  Axis 0: 지령모드 1, 기어비 1000:1, 절대엔코더, 토크 300%
  Axis 1: 지령모드 2, 기어비 1000:1, 절대엔코더 ...
  ...

[CRITICAL] 0건
[MAJOR] 1건
  🟠 B1 오버트래블 금지 해제 — Axis 4: ProhibitOvertravel=0
     근거: MotionParam/ProhibitOvertravel (checklist B1)
     조치: 리미트 초과 보호를 위해 1로 설정 검토
[MINOR] 5건
  🟡 C1 팔로잉 에러 무감시 — Axis 0~4: FollowingError 임계 0
     ...
[INFO] 8건
  🔵 A7 절대 엔코더 — Axis 0~2
  🔵 B2 소프트리밋 비활성 — Axis 0~4
  ...

== 요약 ==
CRITICAL 0 / MAJOR 1 / MINOR 5 / INFO 8

다음 단계:
  - MAJOR 항목을 실기 사양과 대조해 확정
  - 코드 소스가 있으면 wmx3-app-review 로 코드-파라미터 정합성 이어서 검토
```
