## WMX3 Application Development

### 환경

- WMX3 SDK: **3.7** (Soft Servo Systems / Movensys 소프트웨어 모션 컨트롤러 라이브러리)
- 언어:
  - C++11 이상 — `wmx3Api` 네임스페이스, x64
  - .NET C# — `WMX3ApiCLR` (멤버 첫 글자 대문자, `IDisposable`/`Dispose` 규칙, 네임스페이스 `...CLR` 접미사)
- 플랫폼 (3.7 기준 5종):
  - **EtherCAT** — `EcPlatform`, `ec_network.def`·ENI 파일
  - **시뮬레이터** — `SimuPlatform`, `simu_network.def` (실 HW 없이 모션 검증)
  - **M4** (3.7 신규) / **TSN·CC-Link** (3.7 신규) / **EC-M4·EC-TSN 하이브리드** (3.7 신규)
- 주요 API 클래스(`wmx3Api`): `WMX3Api`(메인), `CoreMotion`(기본 모션), `AdvancedMotion`,
  `PMMotion`, `Io`, `Compensation`, `ApiBuffer`, `CyclicBuffer`, `EventControl`, `UserMemory`,
  `Log` + 플랫폼 `ecApi` / `simuApi`
- 다관절 로봇 = **Robot Option** 확장: `wmx3Api::RobotMotion`(멤버 `mKinematics`/`mCoordinate`),
  로봇 정의는 코드가 아닌 **XML + URDF 파일**(링크별 관성·tool 정보)

> **wmx3md와의 구분**: 이 프로젝트는 WMX3 API를 **호출하는 응용 프로그램**(장비 제어 SW) 개발이다.
> WMX3 엔진에 로드되는 내부 모듈(rtdll) 개발은 별도 플러그인 `wmx3md` 담당.

### 필수 시퀀스 규칙

**초기화 (순서 고정)**:

```
CreateDevice(path, DeviceType)   ← 디바이스 생성
  → StartCommunication()         ← 서보 네트워크와 사이클릭 통신 개시
  → GetStatus()로 Engine State = Communicating 확인
  → SetServoOn()                 ← 통신 직후 전 축은 서보 오프 상태.
                                    서보 온 상태에서만 위치 지령을 따른다
  → 모션 API 호출 (StartHome / 모션 프로파일 / 보간 등)
```

**종료 (역순 고정)**:

```
모션 정지 → 서보 오프 → StopCommunication() → CloseDevice()
```

- **.NET 필수**: `CloseDevice()` 후 반드시 `Dispose()` 호출 — 미호출 시 GC가 비관리 리소스를
  조기 해제하여 정의되지 않은 동작 (매뉴얼 §4 아키텍처·디바이스 명문).
- 상태 확인 없이 다음 단계로 진행하지 않는다 — 모든 상태는 `GetStatus()`로 취득.
- 축 위치는 기어비(Gear Ratio Numerator/Denominator)를 거친 **사용자 단위(user units)**로 다룬다.
  기어비·단회전(Single Turn)·Home Offset은 축 구성 설계 산출물을 따르고 코드에 매직 넘버로 넣지 않는다.

### 에러 처리 규칙

- 모든 WMX3 API의 **반환 코드를 항상 확인**한다. 무시 금지.
- **오류코드 정수 하드코딩 금지** — v3.7에서 API 버퍼 오류코드 값이 시프트됨
  (`RewindBlockIndexOutOfRange` 0x12006 삽입 → 후속 코드 +1,
  예: `AlreadyRecordingForSpecifiedChannel` 73734→73735). 반드시 심볼 상수 사용.
- 재시도 가능 오류와 즉시 중단 오류를 구분하는 일관된 에러 처리 계층을 둔다.
- 3.6u3 코드 이식 시 `wmx3-app-implement` 스킬의 `references/v37-migration.md`
  (호환성 깨짐 8항목: ClosedLoop 명명·TrqCommand 빌더 통합·토크 램프 시간 단위 초 변경·
  `Torque::`/`Velocity::`→`Config::` 이동·ApiBuffer 조건부 동작·오류코드 시프트 등)를 적용한다.

### 성능/안정성 규칙

- 타이밍 크리티컬 경로에서 Sleep 폴링 금지 → **트리거 모션·ApiBuffer·이벤트·대기(Wait) API** 사용.
  (트리거 모션은 "Windows API 호출 타이밍의 지연·지터 제거"가 매뉴얼 명문)
- 고속 I/O는 **"Ex" 접미어 함수**(어드레스 공간 직접 액세스) 사용 —
  단, **ApiBuffer 안에서는 Ex 함수 실행 불가**.
- 타임아웃 없는 대기 금지. Watchdog·리미트 스위치·토크 제한 구성을 확인한다.
- v3.7 신기능 활용 후보:
  - Closed-Loop 전환: `StartClosedLoopTo*` / `Start*ToClosedLoop`, `Ramp` 클래스
  - Dynamic 모션: `StartDynamicPos` / `StartDynamicMov` / `SetDynamicPos`
    (ApiBuffer에서 실행 전 목표값 동적 변경)
  - `SetMotionSlowdown` (Motion Slowdown Factor — 시간 스케일링, 디버깅 활용)
  - MaxTorqueLimitRamp, ApiBuffer `GetCumulativeBlockCount`
  - E-CAM 3.7 아키텍처: `SetEcamMaster` / `SetEcamSlave`

### 실시간 응용 (선택)

- RTX SDK로 RT 공간 애플리케이션 작성 가능 — `IMDLL_RT.lib` 링크, VC++ 한정.
- **주의**: WMX3·RTX 런타임 라이선스와 별도로 **IntervalZero RTX SDK 라이선스 필요** (매뉴얼 명문).
- RT 앱에서는 콘솔 출력의 결정성 영향·무한 루프 금지 등 실시간 주의사항을 지킨다.

### 매뉴얼 다이제스트 참조

manual-digest로 등록된 `wmx37-user-manual-kr`(및 `wmx3-user-manual-kr`) 다이제스트가 있으면
1차 참조하고(`~/.claude/manuals/wmx37-user-manual-kr/digest.md`, project 스코프는 `.claude/manuals/`),
디테일은 다이제스트의 키워드 인덱스로 원본을 핀포인트한다. 다관절 로봇 제어를 다루면
`wmx3-robot-help-kr`(Robot Option — 기구학·Joint/Cartesian 좌표계·PTP/CP·XML/URDF 로봇 정의·충돌 감지)
다이제스트도 함께 1차 참조한다(`~/.claude/manuals/wmx3-robot-help-kr/digest.md`).
EtherCAT ENI 파일 제작을 다루면 `ecconfigurator-kr`(EcConfigurator — ENI 구조·ec_network.def·CANopen 객체표)·
`netconfigurator-kr`(NetConfigurator — ESI 기반 ENI 생성 워크플로) 다이제스트도 함께 1차 참조한다
(`~/.claude/manuals/ecconfigurator-kr/digest.md`, `~/.claude/manuals/netconfigurator-kr/digest.md`). 다이제스트가 없는 환경이면
wmx3app 플러그인 스킬의 `references/` 문서만으로 진행하고, `/manual-digest`로 WMX3.7 매뉴얼
등록을 제안한다. 답변/산출물에는 출처(§/토픽)를 명시한다.

### 요청 → 스킬/에이전트 라우팅

| 요청 유형 | 스킬 | 위임 에이전트 |
|-----------|------|---------------|
| 시스템 설계 (플랫폼 선택·축 구성·기능 매핑·성능/안정성 전략) | `wmx3-app-design` | `wmx3app-architect` |
| C++/C# 구현 (초기화 골격·모션·이벤트·에러 처리·3.7 마이그레이션) | `wmx3-app-implement` | `wmx3app-implementer` |
| 테스트 (시뮬레이터 리허설·gtest/xUnit 픽스처·시나리오·실기 전 체크) | `wmx3-app-test` | `wmx3app-test-engineer` |
| 기존 프로젝트 WMX3 사용 검토 (API 오용·에러 처리·성능·마이그레이션) | `wmx3-app-review` | `wmx3app-usage-reviewer` |
| ENI/EtherCAT 네트워크 구성 (WMX3 전용 ENI·ec_network.def·PDO/CANopen 매핑) | `wmx3-app-eni` | `wmx3app-eni-builder` |
| Config Export 분석 (파라미터 export XML — 설정 축 식별·기어비/토크/소프트리밋/원점 요약·안전 일관성 검토) | `wmx3-app-config-xml-analy` | (스킬 내 파서 + 필요 시 위임) |

검토 리포트의 심각도 등급은 **CRITICAL / MAJOR / MINOR / INFO** 4단계를 사용한다.

### 에이전트/스킬 구성

- 스킬 (7): wmx3-app-setup, wmx3-app-design, wmx3-app-implement, wmx3-app-test, wmx3-app-review, wmx3-app-eni, wmx3-app-config-xml-analy
- 에이전트 (5): wmx3app-architect, wmx3app-implementer, wmx3app-test-engineer, wmx3app-usage-reviewer, wmx3app-eni-builder
- 에이전트 재설치/갱신이 필요하면 `/wmx3-app-setup` 재실행 (기존 파일은 덮어쓰기 전 확인)
- 사용 가이드: 플러그인 `docs/USAGE_GUIDE.md`
