---
name: wmx3-app-test
description: "WMX3.7 애플리케이션 테스트. 시뮬레이터 플랫폼(SimuPlatform·simu_network.def)으로 실 하드웨어 없이 모션·시퀀스를 검증하고, C++ gtest / C# xUnit·NUnit 픽스처 기반 테스트 코드 작성, 시나리오 테스트(원점복귀·프로파일·보간·이벤트·에러 주입), 실기(EtherCAT) 전환 전 체크리스트 점검을 수행한다. 'WMX 테스트', 'WMX3 테스트', '시뮬레이터 테스트', '모션 테스트', 'simu 검증' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# WMX3 애플리케이션 테스트

> 이 스킬은 WMX3.7 API를 호출하는 **애플리케이션**(장비 제어 SW)의 테스트를 담당합니다.
> 실제 테스트 설계·코드 작성·실행·판정은 **wmx3app-test-engineer 에이전트**에게 위임합니다.
> 시뮬레이터 플랫폼 구성은 `references/simulator-platform.md`, 테스트 전략·픽스처 패턴은 `references/test-strategy.md`를 참조합니다.
>
> ※ 이 플러그인(wmx3app)은 WMX3 API를 호출하는 **응용 프로그램 개발**용입니다. WMX3 엔진에 로드되는 **내부 모듈(rtdll) 개발**은 `wmx3md` 플러그인이 담당합니다.

## 매뉴얼 다이제스트 연동

manual-digest로 등록된 `wmx37-user-manual-kr`(및 `wmx3-user-manual-kr`) 다이제스트가 있으면 1차 참조하고(`~/.claude/manuals/wmx37-user-manual-kr/digest.md`, project 스코프는 `.claude/manuals/`), 디테일은 다이제스트의 키워드 인덱스로 원본을 핀포인트한다. 다관절 로봇 제어를 다루면 `wmx3-robot-help-kr`(Robot Option — 기구학·Joint/Cartesian 좌표계·PTP/CP·XML/URDF 로봇 정의·충돌 감지) 다이제스트도 함께 1차 참조한다(`~/.claude/manuals/wmx3-robot-help-kr/digest.md`). 다이제스트가 없는 환경이면 이 스킬의 `references/` 문서만으로 진행하고, `/manual-digest`로 WMX3.7 매뉴얼 등록을 제안한다. 답변/산출물에는 출처(§/토픽)를 명시한다.

## 테스트 절차 (6단계)

1. **테스트 대상·수준 결정** — 무엇을(초기화 시퀀스/모션 로직/이벤트/에러 처리), 어느 수준에서(로직 단위 / 시뮬레이터 통합 / 실기 전 체크) 검증할지 결정
2. **시뮬레이터 플랫폼 구성** — Module.ini에서 SimuPlatform 유효화 + `simu_network.def` 작성 (실 하드웨어·NIC 없이 모션 검증 — `references/simulator-platform.md`)
3. **테스트 코드 작성** — C++ gtest / C# xUnit·NUnit. 초기화/종료 픽스처 패턴(CreateDevice→StartCommunication→SetServoOn / 역순 정리, .NET은 CloseDevice 후 Dispose 필수 — `references/test-strategy.md`)
4. **시나리오 테스트** — 원점복귀·모션 프로파일·보간 궤적·이벤트·에러 주입 (아래 카탈로그)
5. **결과 판정** — 위치 도달(허용 오차)·상태 천이(GetStatus)·오류 코드(심볼 상수 비교)
6. **리포트** — PASS/FAIL 표 + 발견 이슈 심각도 등급화(CRITICAL/MAJOR/MINOR/INFO)

## 테스트 수준

| 수준 | 대상 | WMX3 의존 | 실행 환경 |
|------|------|-----------|-----------|
| 로직 단위 | WMX3 비의존 앱 로직(궤적 계산, 시퀀스 상태기계 등) | 없음(분리 설계) | 어디서나 |
| 시뮬레이터 통합 | WMX3 API 호출 경로 전체(초기화~모션~종료) | WMX3 엔진 + SimuPlatform | 실 HW·NIC 불필요 |
| 실기 인수 | 실 서보·센서·안전 계통 | WMX3 엔진 + EcPlatform | 실 장비 (전환 전 체크리스트 필수) |

## 시뮬레이터 검증 경계 (요약)

시뮬레이터 가상축은 피드백 소스를 지정하지 않으면 **지령값을 그대로 복사한 피드백**을 생성한다 — 즉 편차 0으로 완벽 추종하는 축이다(출처: `kr/guide/simu/network_def.html`). 따라서:

- **검증 가능**: API 시퀀스·상태 천이, 모션 지령 로직(프로파일·보간·ApiBuffer·이벤트), 기어비/사용자 단위 설정 정합성, IO 매핑 + SimuApi 주입 기반 스위치·알람 연동 로직
- **검증 불가/제한**: 실 서보 편차·게인 튜닝, EtherCAT 네트워크(ENI·`ec_network.def`·배선·NIC), 실 드라이브 알람 거동, 기계 요소(백래시·마찰), 하드웨어 안전 회로

상세 경계 표는 `references/simulator-platform.md` §6 참조.

## 시나리오 카탈로그

| 시나리오 | 방법 | 판정 |
|----------|------|------|
| 초기화/종료 시퀀스 | CreateDevice→StartCommunication→SetServoOn, 역순 종료 | Engine State=Communicating 도달, 서보 온 상태, 정리 후 자원 누수 없음 |
| 원점복귀 | `simu_network.def`에 HSFb/LSPFb/LSNFb 매핑(UserDef=1) + SimuApi SetIn* 주입으로 홈/리미트 스위치 모의 → StartHome | 원점 완료 상태, Home Offset 반영 위치 |
| 모션 프로파일 | 사용하는 프로파일별 단축 이동 | 목표 위치 도달(허용 오차 내), 상태 천이 |
| 보간 궤적 | 선형·원호·헬리컬 보간 지령 | 경유/종점 위치, 축 간 동기 |
| 이벤트/ApiBuffer | 입력 조건→출력 동작, 버퍼 실행 순서·Wait/FlowIf 분기 | 기대 순서·조건 분기 결과 |
| 에러 주입 | AlmFb/AlmCode 매핑 + SetIn* 주입으로 알람·리미트 트립 모의 | 앱의 오류 처리 경로(정지·복구·보고) 동작 |

## 로봇 옵션(Robot Option) 테스트

다관절 로봇(Robot Option)을 사용하는 애플리케이션이면 다음을 추가한다
(근거: `wmx3-robot-help-kr` 다이제스트 §4 RobotMotionApi 튜토리얼 — v3.6u3 기준):

| 항목 | 방법 | 판정 |
|------|------|------|
| 3D Simulation 활용 | 튜토리얼 ③ **3D Simulation**으로 실 로봇 없이 로봇 모션 확인 | 시뮬레이션 상 동작·상태 확인 |
| 로봇 시나리오 | 튜토리얼 순서 준용: 자세 초기화(⑤) → PTP(⑥) → CP(⑦) → 충돌 감지 설정(⑧) 검증 | 각 단계 상태·로봇 에러 코드 |
| 좌표계 변환 검증 | Joint↔Cartesian 변환 왕복 결과 정합성 (Coordinate 모듈 — 함수명은 Robot Help API Reference 확인) | 왕복 결과 허용 오차 내 일치 |
| 충돌 감지 전제조건 점검 | 4가지 전제조건(URDF/XML 링크 관성·전류 피드백·SetToolInfo·baseJointCoordinate=0) 충족 확인을 테스트 항목화 | 4항목 전부 충족 |

## 실기(EtherCAT) 전환 전 체크리스트

시뮬레이터에서 전 시나리오 PASS 후에도, 시뮬→실기에서 달라지는 다음 항목을 반드시 점검한다:

1. **플랫폼 구성 전환** — Module.ini에서 EcPlatform 유효화. 시뮬+실 플랫폼 공존 시 정의 순서·UserDef 규칙 재확인(출처: `kr/guide/simu/use.html`)
2. **EtherCAT 네트워크 준비** — `ec_network.def`·ENI 파일·지원 NIC 확인 (시뮬레이터는 NIC 불필요였음 — 실기에서 처음 검증되는 영역)
3. **실 서보 파라미터 재검증** — 기어비 Num/Den·사용자 단위·축 극성·단회전·Home Offset. 시뮬레이터는 편차 0이라 설정 오류가 가려질 수 있음
4. **리미트·토크 제한·안전** — 리미트 스위치 실배선/논리 확인, 토크 제한(v3.7은 `Config::SetMaxTrqLimit` 계열), Watchdog, 비상정지 경로
5. **원점복귀 실검증** — 실 센서로 홈 타입 재확인. MechEnd 계열(기계 끝단 검출 — 지령·피드백 위치 차이가 Mechanical End Detection Position Difference를 Detection Time 동안 초과하면 검출, 출처: kr/guide/motion/homing/homing_me.html)은 시뮬레이터 기본 가상축이 피드백=지령 복사(편차 0)라 검출 조건이 성립하지 않으므로 실기에서만 유효
6. **저속 시운전** — 첫 실기 운전은 저속·소거리로. 필요 시 Motion Slowdown Factor(v3.7, `SetMotionSlowdown` — 팩터 N=1/N 속도)로 감속 실행
7. **테스트 전용 코드 제거** — SimuApi SetIn* 주입 등 시뮬레이터 전용 호출이 프로덕션 경로에 남지 않았는지 Grep 확인
8. **오류 코드 처리 확인** — 오류코드 정수 하드코딩 금지(v3.7에서 API버퍼 오류코드 값 시프트), 심볼 상수 비교인지 확인
9. **모니터링 준비** — GetStatus 폴링/이벤트, 데이터 로그·API 로그 활성화로 첫 운전 기록 확보

> 통신 이상(케이블 단선·슬레이브 탈락) 대응 경로는 시뮬레이터에 네트워크 계층이 없어 **실기에서 최초 검증**된다
> (`references/simulator-platform.md` §6, 구현 지침은 wmx3-app-implement `references/error-handling.md` §5).

## wmx3app-test-engineer 에이전트 위임

이 스킬은 실제 작업을 `wmx3app-test-engineer` 에이전트에게 위임합니다. 에이전트에게 전달할 정보:

- 테스트 대상 코드/프로젝트 경로와 언어(C++/C#)
- 테스트 수준(로직 단위 / 시뮬레이터 통합 / 실기 전 체크)
- 시뮬레이터 구성 상태(Module.ini·simu_network.def 존재 여부, 축 수·통신주기)
- 중점 시나리오(없으면 카탈로그 전체)
- references 정본 절대 경로: `${CLAUDE_SKILL_DIR}/references/` 아래 문서들 — 호출 시 실제 절대 경로로 치환하여 전달

## 리포트 형식

```
== WMX3 애플리케이션 테스트 결과 ==

환경: SimuPlatform, CommCycle=1000(1ms), 축 4, WMX3 3.7
프레임워크: gtest

| 시나리오 | 케이스 | 결과 |
|----------|--------|------|
| 초기화/종료 | 정상 경로 / 통신 실패 경로 | PASS / PASS |
| 원점복귀 | HS 주입 원점 | PASS |
| 에러 주입 | 알람 시 정지 처리 | FAIL |

발견 이슈:
  [MAJOR] 알람 주입 시 서보 오프 없이 재시도 — src/MotionSeq.cpp:120 (수정 제안 포함)

실기 전환 전 체크리스트: 9항목 중 7 확인 / 2 미확인(NIC, 리미트 배선)
```
