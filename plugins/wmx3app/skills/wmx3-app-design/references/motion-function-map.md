# 요구 동작 → WMX3 기능 매핑 표

장비 요구 동작을 WMX3.7 기능/API에 매핑하기 위한 참조표.
함수명·클래스명은 모두 WMX3 매뉴얼 다이제스트(`wmx3-user-manual-kr`, `wmx37-user-manual-kr`) 또는
v3.7 매뉴얼 미러 원문에서 확인된 것이다. 각 행에 출처를 표기한다.

## 1. 시나리오별 매핑 표

| 요구 동작 (시나리오) | WMX3 기능 | 주요 API (담당 클래스) | 출처 |
|----------------------|-----------|------------------------|------|
| 단축 점대점 위치결정 (픽앤플레이스 이동) | 기본 모션 + 모션 프로파일 26종 | `StartPos`/`StartMov` (CoreMotion) | 미러 `guide/motion/trigger/trigger_overview.html` 함수 목록, digest §5 기본 모션 |
| 조그/연속 속도 운전 (수동 운전·컨베이어) | 조그·속도 모션 | `StartJog`/`StartVel` (CoreMotion) | 미러 `trigger_overview.html` 함수 목록 |
| 토크 운전 (권취 장력 등) | 토크 모션 | `StartTrq` — v3.7은 빌더 패턴 `TrqCommand`(`SetTrigger`/`SetRamp`/`SetRampRate`/`SetRampTime`) | `wmx37` digest 사양 변경(토크 커맨드 통합) |
| 다축 직선/원호/헬리컬 보간 (XY 스테이지·윤곽 가공) | 보간 Interpolation | `StartLinearIntplPos/Mov`, `StartCircularIntplPos/Mov`, `StartHelicalIntplPos/Mov` (CoreMotion) | 미러 `trigger_overview.html` 함수 목록, digest §5 |
| 모션 간 부드러운 연결 (코너 감속 최소화) | Fast Blending / Blending / Smoothing 오버라이드 | 보간 블렌딩 계열 (CoreMotion) / ApiBuffer 블렌딩 | `wmx37` digest §모션(보간), 미러 `other_api_buffer/apb_blending_*.html` |
| CAD 경로·디스펜서 연속 궤적 | 경로 보간 / 회전 동반 경로 보간 | `StartPathIntplPos/Mov`, `StartPathIntpl3DPos/Mov`, `StartPathIntplWithRotation` (AdvancedMotion) | 미러 `trigger_overview.html` 함수 목록, digest §5 고급 모션 |
| 대량 세그먼트 실행 중 추가·속도 최적화 | **예측 경로 보간(Look-Ahead)** — 실행 중 지령 추가·출력 명령·구간당 속도·저크 제한·3–6차원·보조축 | Look-Ahead 계열 (AdvancedMotion) | `wmx37` digest §고급 모션, 미러 `guide/motion/advanced_motion/adv_path_interpolation_look_ahead/` |
| 자유 곡선 통과 (스플라인) | Spline 4종 | `StartCSplinePos/Mov`, `StartCBSplinePos/Mov` (AdvancedMotion) | 미러 `trigger_overview.html` 함수 목록, digest §5 고급 모션 |
| 시간 파라메트릭 궤적 (외부 계산 궤적 재생) | PVT / PT / VT / AT 지령 | `StartPVT`, `StartPT`, `StartVT`, `StartAT` (CoreMotion) | 미러 `trigger_overview.html` 함수 목록, digest §5 |
| 자체 궤적 생성기 직결 (매 사이클 프로파일 하달) | PM(Profile Mode) 모션 | PMMotion 클래스 | digest §5 PM 모션, §8 |
| 마스터-슬레이브 캠 동작 (로터리 나이프·필름 이송) | **E-CAM** (v3.7 채널 아키텍처) | `SetEcamMaster`/`SetEcamSlave` → `StartEcam`/`StopEcam` → `ClearEcamMaster`/`ClearEcamSlave` (AdvancedMotion) | 미러 `guide/motion/ecam/ecam_architecture.html` |
| 축 간 기어 동기 (갠트리 외 일반 동기) | 동기 Synchronization (보상·원점·기어비·위상·그룹) | Sync 계열 (CoreMotion) | digest §5 기본 모션 동기 |
| 원점 복귀 | Homing — 원점 유형 21종 (CurrentPos/ZPulse/HS 계열/LS 계열/TouchProbe/HSTouchProbe/MechanicalEndDetection 계열) + 갠트리 원점 복귀 | `StartHome` (digest §5 Homing "핵심 API") | 미러 `guide/motion/homing/homing_types.html`, digest §5 Homing |
| 비전 트리거 위치 래치 (플라잉 캡처) | 터치 프로브 (SW/HW) — SW는 일반 DI 입력을 엔진이 통신 주기 정밀도로 래치 | `SetSoftwareTouchProbe(channel, enable, axis, byteAddrs, bitOffset, logic, mode)`, `GetSoftwareTouchProbeCounterValue` | `wmx37` digest §기타 기능(터치 프로브) |
| 위치 동기 펄스 출력 (레이저·디스펜싱) | **PSO** (Source·comparator·데이터 포인트·출력·예제 3종) | PSO 기능 — 클래스는 API Reference에서 확인 | digest §5 기타 기능 PSO, `wmx37` digest §기타 기능 |
| 정밀 타이밍 모션 개시 (지터 제거) | **트리거 모션** — 조건 충족까지 실행을 엔진이 지연 | `TriggerPosCommand` 등 + `TriggerType`(RemainingTime/RemainingDistance/SameTimeCompletion/CompletedTime/CompletedDistance/StaggeredTimeCompletion/StaggeredDistanceCompletion/DistanceToTarget 외) + 트리거 이벤트 | 미러 `guide/motion/trigger/trigger_overview.html`, `index.html`, 미러 Doxygen `api/html/classwmx3_api_1_1_trigger_type-members.html`(TriggerType 열거자 전체 멤버) |
| 실행 직전 목표값 갱신 (얼라인 보정 반영) | **Dynamic 모션 (v3.7 신규)** — ApiBuffer에 저장된 모션의 목표를 실행 전 동적 변경 | `StartDynamicPos`/`StartDynamicMov`/`StartDynamicLinearIntplPos/Mov` + `SetDynamicPos`/`GetDynamicPos` | `wmx37` digest 릴리즈 노트(신규 기능) |
| 힘 제어·프레스·압입 (외부 센서 피드백 제어) | **폐루프 Closed-Loop (v3.7 신설)** — 위치/속도/토크 전환, setpoint 램핑 | `StartClosedLoopTo*`/`Start*ToClosedLoop`, `Ramp` 클래스, `PidParam.rampRate` | `wmx37` digest 릴리즈 노트, 미러 `guide/motion/basic_motion/basic_closed_loop/` |
| 모션 종류 간 연속 전환 (속도→위치 등) | 모션 전환 함수 | `StartVelToPos/Mov`, `StartTrqToPos/Mov`, `StartPosToVel`, `StartPosToJog` 등 | 미러 `trigger_overview.html` 함수 목록 |
| 실행 중 속도/조건 변경 | 오버라이드 모션 (저속 오버라이드·가속도 리셋·Overtravel·역방향) / 계획 속도 오버라이드(PVO) | 오버라이드 계열 (CoreMotion) | `wmx37` digest §기본 모션, §기타 기능(PVO) |
| 사전 계획 시퀀스의 결정론적 실행 | **API 버퍼** — 통신 사이클 정밀도로 순차 실행 | ApiBuffer 클래스 (`references/performance-stability.md` §2) | 미러 `other_api_buffer/index.html` |
| 디버깅용 슬로우 모션 재생 | **Motion Slowdown Factor (v3.7 신설)** — 시간 스케일링(팩터 N = 1/N 속도) | `SetMotionSlowdown`/`GetMotionSlowdown` | `wmx37` digest 릴리즈 노트, 미러 `guide/motion/basic_motion/slowdown_factor/` |
| 다관절 로봇 PTP 이송 (조인트/Cartesian 목표) | **Robot Option** PTP — 조인트별 개별 동작·시작/종료만 동기화·경로 무관 최고속 | `RobotMotion.mKinematics.StartPTPPos(PtpMotionParam::PtpPosParam)` | `wmx3-robot-help-kr` digest §3 로봇 모션 |
| 로봇 끝단 경로 제어 | **Robot Option** CP(Continuous Path) 모션 | `RobotMotion.mKinematics` (PTP/CP 실행 진입점) | `wmx3-robot-help-kr` digest §3 로봇 모션 |
| 로봇 충돌 감지 (외력/이상 시 자동 정지) | **Robot Option** 충돌 감지 — 전제조건 4가지(링크 관성·전류 피드백·tool 정보·baseJointCoordinate=0) | `SetToolInfo`, `RobotMotionParam.robotParam` | `wmx3-robot-help-kr` digest §3 기타 기능 |

다관절 로봇(Robot Option) 행의 상세 — 좌표계 3종·XML/URDF 로봇 정의·핵심 API 지도·튜토리얼 8단계 —
는 `robot-option.md` 참조 (로봇 다이제스트는 **v3.6u3 기준**).

## 2. 보조 기능 매핑 표 (모션 외 요구)

| 요구 | WMX3 기능 | 담당 클래스 | 출처 |
|------|-----------|------------|------|
| 디지털/아날로그 I/O 제어 | 입출력 어드레스 공간·초기 출력·아날로그·비트마스크. 대량/저지연은 고속 "Ex" 함수 (제약: ApiBuffer 내 실행 불가 — `references/performance-stability.md` §3) | `Io` | `wmx37` digest §기타 기능(I/O), 미러 `other_io/expedited.html` |
| 앱 간/PLC 연계 공유 데이터 | 사용자 메모리 | `UserMemory` | digest §5 기타 기능 |
| 조건 반응 자동화 (센서 → 즉시 동작) | 이벤트 — 입력(코어모션·이벤트·I/O·UserMemory) → 출력(코어모션·이벤트·API버퍼·I/O·UserMemory) | `EventControl` | `wmx37` digest §기타 기능(이벤트 입력/출력 구성) |
| 위치 정밀도 보정 | 보정 — 피치 오차/2D 피치 오차/백래시 (위치 파이프라인에 합산) | `Compensation` | digest §5 기타 기능, `wmx3` digest 핵심 아키텍처(Compensation) |
| 갠트리(문형) 축 쌍 | 갠트리 원점 복귀 + 동기(Synchronization) 구성 | `CoreMotion`(동기) 등 | digest §5 Homing(갠트리 원점 복귀)·기본 모션(동기) |
| 운전 데이터 수집·진단 | 데이터 로그·API 로그·메모리 로그 | `Log` | digest §5 기타 기능, §8 |

## 3. 모션 프로파일 선택 지침

프로파일은 26종이 제공된다 (사다리꼴·S자·저크비율·저크제한·2속도·가속시간·일정감속도·속도고정 계열 등.
출처: `wmx37-user-manual-kr` digest §모션 프로그래밍 지침 "모션 프로파일 26종", 미러 `guide/motion/profile/`).

| 요구 | 권장 프로파일 계열 |
|------|--------------------|
| 일반 이송 (기본값) | 사다리꼴(Trapezoidal) |
| 진동 억제·기구 보호 | S자 / 저크비율 / 저크제한 계열 |
| 접근-정착 2단 속도 | 2속도 계열 |
| 시간 기준 제어 | 가속시간 계열 |

트리거 모션 예제에서 확인된 기본 사용법: `Motion::PosCommand`의 `profile.type = ProfileType::Trapezoidal`,
`profile.velocity/acc/dec`, `target` 설정 후 `StartPos`/`StartMov` 호출
(출처: 미러 `guide/motion/trigger/trigger_overview.html` 예제 코드).

## 4. 트리거 모션 인수 구조 (지터 제거의 핵심)

트리거 모션은 "지정된 트리거 조건이 충족될 때까지 모션 지령의 실행을 지연"시키며, 이로 인해
**"Windows 애플리케이션에서 호출되었을 때의 API 함수의 실행 타이밍에 의한 지연이나 지터가 없어진다"**
(출처: 미러 `guide/motion/trigger/trigger_overview.html` 원문).

- 인수 3개: **트리거 유형**(시작 조건 종류), **트리거 축**(조건을 만족해야 하는 축), **트리거 값**(거리·시간 등 추가 매개변수)
- 트리거 축은 지령 축과 동일 축 지정 가능 (연속 동작 체인 구성)
- `StartPos`~`StartTrq`, 보간·경로·스플라인·PVT 계열 등 광범위한 Start 함수가 트리거 실행 가능
  (전체 목록: 미러 `trigger_overview.html`)

## 5. E-CAM 설계 제약 (v3.7 아키텍처)

출처: 미러 `guide/motion/ecam/ecam_architecture.html`.

- 마스터 채널(`SetEcamMaster`, 최대 `maxEcamMasterChannel`개) / 슬레이브 채널(`SetEcamSlave`,
  최대 `maxEcamSlaveChannel`개) 분리. 여러 슬레이브 채널이 동일 마스터 채널 참조 가능.
- 슬레이브 채널 1개가 `EcamSlaveData`의 AxisSelection으로 여러 슬레이브 축을 동일 테이블로 제어 가능.
- **축 매핑 제한**: 한 축은 여러 E-CAM 작업 동시 사용 불가 / 마스터·슬레이브 동시 지정 불가 /
  여러 슬레이브 채널 동시 할당 불가 (위반 시 `SetEcamMaster`/`SetEcamSlave`가 오류 반환).
- 마스터 채널 삭제(`ClearEcamMaster`) 시 종속 슬레이브 채널 연쇄 삭제.
- v3.6u3 코드 이식 시 명명 ECAM→Ecam PascalCase 변경 주의 (출처: `wmx37` digest 릴리즈 노트).

## 6. 기능 매핑 작성 절차

1. 요구 동작을 시나리오 단위로 분해한다 (①의 표 좌측 열 어휘로 정규화).
2. 표에서 기능·API를 선택하고, 겹치는 경우 우선순위를 정한다
   (예: 타이밍 크리티컬 → 트리거 모션/ApiBuffer 우선, `references/performance-stability.md`).
3. v3.7 신설 기능(폐루프·Dynamic·Slowdown·E-CAM 신아키텍처)을 쓰는 경우 설계서에 "3.7 필수"를 명기한다.
4. 설계서의 기능 매핑 표에 **출처(§/토픽)** 열을 유지한다.
5. 확신이 없는 함수 시그니처는 다이제스트 키워드 인덱스로 원본(미러/CHM)을 핀포인트해 확인한다 — 추측 금지.

## 출처 요약

- `wmx3-user-manual-kr` digest: §5 모션 프로그래밍 지침(기본/고급/PM/기타 기능), §8 API 클래스
- `wmx37-user-manual-kr` digest: 릴리즈 노트(폐루프·Dynamic·E-CAM·Slowdown·토크 커맨드), 섹션별 요약
- `wmx3-robot-help-kr` digest: §3 로봇 모션(PTP/CP)·기타 기능(충돌 감지) — 상세는 `robot-option.md`
- v3.7 미러: `guide/motion/trigger/trigger_overview.html`(트리거 정의·인수·실행 가능 함수 목록·예제),
  `guide/motion/ecam/ecam_architecture.html`(E-CAM 채널·제약),
  `guide/motion/homing/homing_types.html`(원점 유형 21종 목록),
  `guide/motion/basic_motion/basic_closed_loop/`·`slowdown_factor/`(v3.7 신설 기능 페이지),
  `guide/motion/advanced_motion/adv_path_interpolation_look_ahead/`(Look-Ahead 하위 토픽)
