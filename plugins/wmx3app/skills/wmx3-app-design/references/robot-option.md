# Robot Option (다관절 로봇 제어) 설계 가이드

WMX3 위에 얹는 **로보틱스(다관절 로봇) 제어 확장** — Robot Option 채택 판단과 설계에 필요한 도메인 지식.
근거: `wmx3-robot-help-kr` 다이제스트(WMX3 Robot Help KR, **v3.6u3**, CHM). 각 절에 출처(§/토픽)를 표기한다.

> **버전 주의**: 이 문서와 로봇 다이제스트는 **v3.6u3 Robot Help 기준**이다. v3.7에서의 로봇 옵션 변경 여부는
> 다이제스트에 없으므로, v3.7 적용 시 Robot Option 릴리즈 노트(§1 `_robot__option__doc__releasenote.html`
> — 3.2→3.6u3 14개 변경 이력)를 확인한다.

## 1. 개요 — 내부 2개 RTDLL 모듈 (출처: 다이제스트 개요·§3 아키텍처)

Robot Option은 일반 축 모션(CoreMotion/AdvancedMotion)과 달리 **기구학(Kinematics)**과 **좌표계 변환**을 통해
조인트 공간 ↔ 직교(Cartesian) 공간을 오가며 다관절 로봇을 제어한다. 내부는 두 개의 RTDLL 모듈로 구성된다:

| 모듈 | 역할 |
|------|------|
| **Coordinate** | 회전을 포함한 **6자유도(6-DOF) 공간 자료형**, 로봇 끝단(end-effector) 위치/속도 경로 생성, **좌표계 변환 + 티칭(teaching) API**. Kinematics 내부에서 호출되며 기구학과 직접 연관되지는 않는다 |
| **Kinematics** | 로봇 구조 파라미터·상태 자료형, 로봇 파라미터 구성·제어 API. 실제 **PTP/CP 모션 실행 진입점**(`mKinematics.StartPTPPos(...)` 등) |

## 2. 좌표계 3종 (출처: §3 좌표계 `..._guide__coordinate.html`)

| 좌표계 | 표현 | 특징 | 토픽 |
|--------|------|------|------|
| **Joint(조인트)** | 각 조인트(관절) 각도 | 로봇에 친숙 | `..._coordinate__joint.html` |
| **Cartesian(카테시안)** | 끝단 위치/자세를 `X,Y,Z` + 회전 `(u,v,w)` 또는 `(Rx,Ry,Rz)` | 사람에게 직관적 | `..._coordinate__cartesian.html` |
| **Robot(로봇)** | 베이스 좌표 기준 (`baseJointCoordinate`) | — | `..._coordinate__robot.html` |

## 3. 로봇 정의 — XML + URDF (출처: §3 아키텍처 `..._architecture__xml__file.html` / `..._architecture__urdf__file.html`)

- 로봇 정의는 코드가 아닌 **별도 XML 파일 + URDF 파일**로 관리한다 (기구 구조·링크별 관성·tool 정보).
- **충돌 감지를 쓰려면 링크별 관성(inertia) 정보가 필수** — URDF/XML 작성 시점에 관성 데이터 확보 계획을 세운다.
- 로봇 설정: 기구적 물성치(kinematics params), 모션 프로파일(`..._robot__setting__motion__profile.html`),
  설정 데이터 흐름(`..._function__data__flow.html`) (출처: §3 로봇 설정).
- 구성 파일: setup.ini 등 (출처: §2 설정 가이드 `..._setup__guide__setup__ini.html`).

## 4. 모션 타입 (출처: §3 로봇 모션)

| 모션 | 특성 | API / 토픽 |
|------|------|-----------|
| **PTP(Point-To-Point)** | 조인트별 개별 동작, 시작/종료만 동기화, 경로 무관·최고속. 목표는 조인트 또는 Cartesian 좌표 | `RobotMotion.mKinematics.StartPTPPos(PtpMotionParam::PtpPosParam)` / `..._robot__motion__ptp.html` |
| **CP(Continuous Path)** | 경로 제어 모션 | `..._robot__motion__cp.html` |
| **Override 모션** | 실행 중인 로봇 모션에 대한 오버라이드 | `..._robot__override__motion.html` |
| **Wait** | 대기 | `..._robot__wait__motion.html` |

## 5. 충돌 감지 전제조건 4가지 (출처: §3 기타 기능 `..._guide__robot__collision__detection.html`)

예상치 못한 외력/이상 시 자동 정지하는 기능. **아래 4가지가 모두 충족돼야 동작한다** — 설계 단계에서 충족 가능성을 확정할 것:

1. URDF/XML에 **모든 링크의 관성** 정보 기재
2. 각 조인트 모터의 **실시간 전류 피드백**
3. `SetToolInfo`로 tool 정보 설정 (관성행렬 미포함 시 **점질량 가정**)
4. `RobotMotionParam.robotParam.baseJointCoordinate`의 point/rotation **전부 0**

## 6. 핵심 API 지도 (출처: 다이제스트 핵심 개념·§5 API Reference)

| API | 역할 | API Reference 토픽 |
|-----|------|--------------------|
| `wmx3Api::RobotMotion` | 로봇 모션 메인 클래스 — 멤버 `mKinematics`/`mCoordinate` 보유 | `classwmx3_api_1_1_robot_motion.html` |
| `RobotMotion.mKinematics` | Kinematics 진입점 — PTP/CP 실행, 로봇 파라미터 | `classwmx3_api_1_1kinematics_1_1_kinematics.html` |
| `RobotMotion.mCoordinate` | 좌표 변환·6-DOF 자료형·티칭 | `classwmx3_api_1_1coordinate_1_1_coordinate.html` |
| `RobotMotionParam` | 로봇 모션 파라미터 (`.robotParam` / `.profile`) | §5 Class List `usergroup3.html` |
| `PtpMotionParam::PtpPosParam` | PTP 위치 지령 파라미터 | §5 Class List `usergroup3.html` |

함수 시그니처·파라미터 상세는 §5 API Reference 클래스 토픽에서 확인한다 — 추측 금지.

## 7. 로봇 상태·로깅·에러 코드 (출처: §3 프로그래밍 가이드)

- **로봇 상태 읽기** — `..._guide__robot__status.html`
- **로봇 로깅** — `..._guide__robot__log.html`
- **로봇 전용 에러 코드** — `..._guide__error__code.html` (일반 WMX3 오류 처리와 구분해 로봇 에러 코드 처리를 설계)

## 8. 설계 시 결정 항목

| 결정 | 판단 기준 |
|------|-----------|
| **Robot Option 채택 여부** | 다관절 로봇(기구학적 링크 구조, 조인트↔직교 좌표 변환 필요)이면 Robot Option. 독립 축의 조합(스테이지·갠트리 등)이면 일반 축 모션(CoreMotion/AdvancedMotion)으로 충분 |
| **일반 축 모션과의 역할 분담** | 로봇 본체 = Robot Option(PTP/CP), 주변 축(반송·인덱스 등) = CoreMotion/AdvancedMotion — 시나리오별 담당을 설계서에 명시 |
| **좌표계 선택** | 티칭/작업 지시 관점(Cartesian) vs 조인트 관점(Joint) — §2 표 기준으로 시나리오별 결정 |
| **로봇 정의 파일 계획** | XML+URDF 작성 담당, 링크 관성 데이터 확보(충돌 감지 요구 시 필수), tool 정보 |
| **충돌 감지 요구** | §5 전제조건 4가지의 충족 가능성(특히 조인트 모터의 실시간 전류 피드백 지원 여부) 확인 |

## 9. 학습 경로 — RobotMotionApi 튜토리얼 8단계 (출처: §4 `_robot__option__doc__tutorial__main.html`)

① 프로젝트 생성 → ② 시스템 초기화 → ③ **3D Simulation** → ④ 상태 읽기 및 에러 처리 →
⑤ 로봇 자세 초기화 → ⑥ **PTP Motion** → ⑦ **CP Motion** → ⑧ **충돌 감지 기능 설정**

구현·테스트 시퀀스도 이 순서를 기본 골격으로 삼는다 (테스트는 ③ 3D Simulation 우선 활용).

## 다이제스트 연동

- 1차 참조: `~/.claude/manuals/wmx3-robot-help-kr/digest.md` (v3.6u3, CHM — 위치 단위는 토픽 HTML 파일)
- 핀포인트: 다이제스트 키워드 인덱스의 토픽 파일명으로 원본 CHM을 `extract_chmLib`로 추출한 뒤
  **CP949로 디코딩**해 Read
- 베이스 WMX3 개념(통신·서보온·디바이스 등)은 `wmx3-user-manual-kr`/`wmx37-user-manual-kr` 다이제스트 참조
