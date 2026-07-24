# WMX3 Config Export(파라미터 export XML) 포맷 가이드

> WMX3 엔진의 파라미터 설정 전체를 내보낸 XML 파일의 구조·파라미터 그룹·핵심 필드 사전.
> WMX3Agent / WOS 등 GUI 도구의 "파라미터 Export" 기능 산출물이며, 반대로 Import 시
> 엔진 파라미터를 일괄 복원한다. 이 파일은 코드(ENI/ec_network.def)가 아니라 **엔진 런타임
> 파라미터**의 스냅샷이다 — 실기의 축 구성·안전 설정을 그대로 담고 있다.

## 1. 최상위 구조

```
<Parameters ver="1.00">
  <GlobalParameters>                 ← 엔진 전역 설정 (1개)
    <FlightRecorderParam> ... </FlightRecorderParam>
    <EmergencyStopParam> ... </EmergencyStopParam>
    <GlobalParam> ... </GlobalParam>            (버전/구성에 따라 존재)
  </GlobalParameters>
  <AxisParameters Axis="0">          ← 축별 설정 (통상 128개, Axis="0"~"127")
    <FeedbackParam> ... </FeedbackParam>
    <HomeParam> ... </HomeParam>
    <LimitParam> ... </LimitParam>
    <MotionParam> ... </MotionParam>
    <SyncParam> ... </SyncParam>
    <AlarmParam> ... </AlarmParam>
    <FlightRecorderParam> ... </FlightRecorderParam>
    <EmergencyStopParam> ... </EmergencyStopParam>
    <AxisParam> ... </AxisParam>
  </AxisParameters>
  <AxisParameters Axis="1"> ... </AxisParameters>
  ...
</Parameters>
```

- 루트: `<Parameters ver="...">` — `ver`는 파라미터 스키마 버전(파일 예: `1.00`). WMX3
  SDK 버전(3.6u3/3.7)과는 별개이며, 새 파라미터가 추가되면 스키마 버전이 오른다.
- **인코딩**: 선언은 `UTF-8`. 대부분 ASCII 숫자라 인코딩 문제는 드물다.
- **값 표기**: 부동소수는 항상 소수점 6자리 문자열(`300.000000`), 정수/불리언은 `0`/`1` 등
  정수 문자열. 불리언 필드는 `0`=off, `1`=on 관례.
- **축 개수는 고정이 아니다**: 통상 128축이 통째로 export되지만, 엔진 구성에 따라 다를 수
  있으므로 개수를 하드코딩하지 말고 `AxisParameters` 요소를 실제로 카운트한다.

## 2. 핵심: "설정된 축"만 골라내기

128축 대부분은 **공장 디폴트 그대로**이고 실제 장비에 쓰이는 축은 소수다. 128축을 전부
나열하면 노이즈만 커진다. 따라서 분석의 첫 단계는 **디폴트에서 벗어난 축(active axis)** 식별이다.

**판별 방식(파서 채택)**: 각 필드(`Group/Field`)의 전체 축 값 중 **최빈값(mode)** 을
baseline(디폴트 추정)으로 잡고, baseline과 다른 필드가 하나라도 있는 축을 "설정 축"으로 본다.
특정 필드명에 의존하지 않아 스키마가 조금 달라져도 견고하다.

`assets/parse_wmx_config.py <xml>` 가 이 판별과 요약·플래그를 자동 수행한다.

## 3. 파라미터 그룹 사전

각 그룹의 대표 필드와 의미. (전체 필드는 export 원문을 Grep으로 확인 — 그룹당 수~수십 개)

### 3.1 GlobalParameters (엔진 전역)

| 그룹 | 대표 필드 | 의미 |
|------|-----------|------|
| `FlightRecorderParam` | `EnableFlightRecorder` | 플라이트 레코더(내부 트레이스) 사용 0/1 |
|  | `TriggerFlightRecorderOnAmpAlarm` | 앰프 알람 시 자동 트리거 0/1 |
|  | `FlightRecorderTimeStamp` | 타임스탬프 수집 0/1 |
| `EmergencyStopParam` | `EnableEStopSignal` | 외부 E-Stop 입력 신호 사용 0/1 |
|  | `EStopSignalSource` / `...Level` / `...ByteAddress` / `...BitAddress` | E-Stop 입력 신호 소스·레벨·I/O 주소 |
|  | `EnableEStopStatusSignal` | E-Stop 상태 출력 신호 사용 0/1 |
|  | `EStopLevel1Type` | 레벨1 E-Stop 정지 유형 |
| `GlobalParam` | (구성별) | 보간 데이터 크기 등 엔진 전역 값 (없을 수 있음) |

### 3.2 AxisParam (축 기본 — 가장 중요)

| 필드 | 의미 | 비고 |
|------|------|------|
| `AxisCommandMode` | 축 지령 모드 | 0=위치(CSP) / 1·2=속도·토크 등 모드 구분 |
| `AxisGearRatioNumerator` / `...Denominator` | 기어비 분자/분모 | **사용자 단위 환산의 핵심**. 분모 0 금지 |
| `AxisUnit` | 축 단위 정의 값 | 0이면 미설정(펄스 기준) 가능성 |
| `SingleTurnMode` / `SingleTurnEncoderCount` | 단회전 모드/엔코더 카운트 | Count는 1회전 분해능(예 65536=2^16) |
| `MaxTrqLimit` / `PositiveTrqLimit` / `NegativeTrqLimit` | 최대·양·음 토크 제한(%) | 통상 300(=300%) 등. 값이 과도한지 검토 |
| `AxisPolarity` | 축 극성(방향) | 지령/피드백 방향 |
| `MaxMotorSpeed` | 최대 모터 속도(rpm) | 과속 감시 기준 |
| `AbsoluteEncoderMode` | 절대 엔코더 사용 0/1 | 1이면 원점복귀 절차가 달라짐 |
| `AbsoluteEncoderHomeOffset` | 절대 엔코더 원점 오프셋 | 절대 엔코더 원점 기준 |
| `VelocityFeedforwardGain` | 속도 피드포워드 게인 | |
| `EncoderRangeMode` / `EncoderRangeLow` / `EncoderRangeHigh` | 엔코더 범위 모드/하한/상한 | 회전형 무한축 등 |

### 3.3 MotionParam (모션 프로파일/제한)

| 필드 | 의미 |
|------|------|
| `QuickStopDec` | 퀵스톱 감속도 |
| `ProhibitOvertravel` | 오버트래블(리미트 초과) 금지 0/1 — **0이면 리미트 보호 해제** |
| `LinearIntplOverrideType` / `CircularIntplOverrideType` | 직선/원호 보간 오버라이드 방식 |
| `EnableGlobalStartingVelocity` / `GlobalStartingVelocity` 등 | 전역 시작/종료/최소 속도 설정 |

### 3.4 LimitParam (리미트/소프트리밋)

| 필드 | 의미 |
|------|------|
| `LSType` / `PositiveLSType` / `NegativeLSType` | 리미트 스위치 유형(양/음) |
| `Invert*LSPolarity` | 리미트 스위치 극성 반전 |
| `LSDec` / `LSSlowDec` | 리미트 정지 감속도 |
| `SoftLimitType` / `PositiveSoftLimitType` / `NegativeSoftLimitType` | 소프트리밋 유형 — **0이면 비활성 가능성** |
| `SoftLimitPositivePos` / `SoftLimitNegativePos` | 소프트리밋 양/음 위치. Type=0 + 둘 다 0 → 소프트웨어 위치 제한 없음 |
| `NearLSType` / `ExternalLSType` 등 | 근접·외부 리미트 스위치 계열 |

### 3.5 HomeParam (원점복귀)

| 필드 | 의미 |
|------|------|
| `HomeType` | 원점복귀 방식 |
| `HomeDir` | 원점복귀 방향 |
| `HomingVelSlow` / `HomingVelFast` (+`Acc`/`Dec`) | 저속/고속 원점 속도·가감속 |
| `HomePosition` / `HomeShift*` | 원점 위치/시프트 |
| `Gantry*` | 갠트리(마스터-슬레이브) 원점복귀 옵션 계열 |
| `MechanicalEndDetection*` | 기계 끝단 검출(토크/시간 기반) 계열 |

### 3.6 FeedbackParam (피드백/인포지션)

| 필드 | 의미 |
|------|------|
| `InPosWidth`~`InPosWidth5` | 인포지션 폭(다단) |
| `PosSetWidth` / `DelayedPosSetWidth` / `DelayedPosSetMilliseconds` | 위치 도달/지연 위치 설정 폭·시간 |
| `VelMonitorSource` | 속도 모니터 소스 |

### 3.7 AlarmParam (팔로잉 에러/알람)

| 필드 | 의미 |
|------|------|
| `FollowingErrorType` / `FollowingErrorStopped` / `FollowingErrorMoving` | 위치 팔로잉 에러 유형·정지/이동 임계 — **둘 다 0이면 감시 없음** |
| `VelFollowingError*` (+`Milliseconds`) | 속도 팔로잉 에러 임계·시간 |
| `ServoOffDuringAmpAlarm` | 앰프 알람 시 서보 오프 0/1 |
| `ServoOnFollowingError` | 서보온 시 허용 팔로잉 에러 |

### 3.8 SyncParam (동기/갠트리)

| 필드 | 의미 |
|------|------|
| `InSyncWidth` / `SyncGain` / `SyncCompensationMode` | 동기 폭·게인·보상 모드 |
| `MasterDesyncType` / `MasterDesyncDec` / `SlaveDesyncType` / `SlaveDesyncDec` | 마스터·슬레이브 비동기(desync) 방식·감속도 |
| `MatchPos` | 위치 매칭 |

### 3.9 축별 FlightRecorderParam / EmergencyStopParam

- 축별 `FlightRecorderParam/CollectAxisFlightRecorderData` — 해당 축 플라이트 레코더 수집 0/1
- 축별 `EmergencyStopParam/EStopDec` — 해당 축 E-Stop 감속도

## 4. 원본 핀포인트 방법

export XML은 텍스트이므로 MCP 없이 Read/Grep/awk 로 처리한다.

```bash
# 특정 축(예: Axis 3) 블록만 추출
awk '/<AxisParameters Axis="3">/{f=1} f{print} f&&/<\/AxisParameters>/{exit}' <xml>

# 특정 필드의 축별 값 분포
grep -oE '<MaxTrqLimit>[^<]+' <xml> | sort | uniq -c

# 그룹 하나만 (예: 축 0 AxisParam)
awk '/<AxisParameters Axis="0">/{f=1} f&&/<AxisParam>/{p=1} p{print} f&&/<\/AxisParam>/{exit}' <xml>
```

## 5. 설계 산출물과의 대조

이 파일은 실기 엔진의 **현재 파라미터 상태**다. `wmx3-app-design`의 축 구성 설계 산출물
(기어비·단회전·Home Offset·토크 제한·소프트리밋 계획)과 대조하면, **설계 의도와 실제 엔진
설정의 불일치**를 찾을 수 있다. 이것이 이 스킬의 주된 검토 축이다.
