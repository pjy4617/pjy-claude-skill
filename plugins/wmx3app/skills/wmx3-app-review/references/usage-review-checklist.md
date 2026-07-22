# WMX3 애플리케이션 사용 검토 체크리스트 (7카테고리 / 35항목 + 로봇 보충 R)

WMX3 API를 **사용하는 애플리케이션** 코드의 검토 기준. wmx3md의 모듈(rtdll) 리뷰 체크리스트와 달리, 이 문서는 WMX3 API **호출 측**(응용 프로그램)의 올바른 사용법을 다룬다.

## 표기 규칙

- **탐지 방법**의 grep 패턴은 소스 파일(`*.c` `*.cpp` `*.h` `*.cs`) 대상 `grep -rn`(정규식이면 `-E`) 기준으로 패턴만 표기한다. 여러 패턴 병기(쉼표 구분)는 OR — 각각 `-e "패턴"`으로 전달.
- grep 패턴은 **1차 스크리닝 휴리스틱**이다. 명중 라인은 반드시 Read로 원문을 확인한 뒤 판정하고, 리포트에는 **파일:라인** 근거를 남긴다. "(수동)" 표기는 grep만으로 판정 불가 — 코드 흐름 확인 필수.
- 심각도: **CRITICAL**(즉시 수정 — 미정의 동작·오동작·마이그레이션 파손 중 조용한 동작 변화) / **MAJOR**(배포 전 수정 — 컴파일 오류로 즉시 드러나는 마이그레이션 파손 포함) / **MINOR**(리팩토링 권장) / **INFO**(참고).
- 근거 출처: `wmx37-user-manual-kr` 다이제스트(릴리즈 노트·모션/기본 프로그래밍 지침·지원 사양)와 `wmx3-user-manual-kr` 다이제스트(§4 아키텍처 — 디바이스·통신/서보온). 로봇 옵션 항목(보충 섹션 R)은 `wmx3-robot-help-kr` 다이제스트. 디테일은 다이제스트의 키워드 인덱스로 원본 핀포인트.

---

## 카테고리 1: 생명주기/리소스 (5항목)

근거: 디바이스 모델 `CreateDevice(path, DeviceType)` / `CloseDevice()`, .NET Dispose 규칙 (wmx3-user-manual-kr §4 아키텍처 — 디바이스).

| # | 항목 | 심각도 | 탐지 방법 | 수정 방향 |
|---|------|--------|-----------|-----------|
| 1.1 | **CreateDevice↔CloseDevice 짝 불일치** | MAJOR | `CreateDevice`, `CloseDevice` 각각 검색 → 생성 경로마다 대응하는 해제가 있는지 호출 짝 비교(수동) | 모든 생성 경로(정상/오류)에 CloseDevice 보장 — C++는 RAII 래퍼, C#은 finally/using 패턴 |
| 1.2 | **.NET Dispose 누락** | CRITICAL | C# 파일 중 `WMX3ApiCLR` 검출 + 같은 파일에 `Dispose` 미검출 | `CloseDevice()` 후 `Dispose()` 호출 — 미호출 시 GC가 비관리 리소스를 조기 해제해 **정의되지 않은 동작**(다이제스트 명문) |
| 1.3 | **CloseDevice→Dispose 순서 위반** | MAJOR | `Dispose` 호출부·`using` 블록을 Read — 스코프 종료(암묵 Dispose) 전에 `CloseDevice` 호출 여부(수동) | 종료 순서를 CloseDevice → Dispose로 통일. using 블록은 블록 끝 전에 CloseDevice가 오도록 배치 |
| 1.4 | **통신 정지 없이 종료** | MAJOR | `StartCommunication` 존재 + `StopCommunication` 부재, 또는 종료 핸들러에 정지 호출 없음 | 종료 시퀀스를 역순으로: 모션 정리 → `StopCommunication` → `CloseDevice`(→ .NET은 `Dispose`) |
| 1.5 | **예외/조기 반환 경로에서 정리 누락** | MAJOR | 초기화~종료 사이의 `throw`, 조기 `return`; C#에서 `try` 있는데 `finally`/`using` 부재(수동) | 정리 코드를 RAII/using/finally로 단일화해 모든 탈출 경로에서 실행 보장 |

---

## 카테고리 2: 시퀀스 정합성 (4항목)

근거: `StartCommunication()` → Engine State = Communicating → (통신 직후 전 축 서보 오프) → `SetServoOn()` → 모션 API. 상태는 `GetStatus()`로 취득 (wmx3-user-manual-kr §4 통신/서보온).

| # | 항목 | 심각도 | 탐지 방법 | 수정 방향 |
|---|------|--------|-----------|-----------|
| 2.1 | **통신 개시 전 API 호출** | CRITICAL | 호출 순서 추적(수동): `StartCommunication` 이전에 `SetServoOn`·모션 지령·I/O 액세스가 실행되는 경로 | 초기화 시퀀스 준수: `CreateDevice` → `StartCommunication` → 상태 확인 → `SetServoOn` → 모션 |
| 2.2 | **서보온 전 모션 지령** | CRITICAL | `SetServoOn` 부재, 또는 모션 호출 앞에 서보온·서보온 상태 확인 없음(수동) | 통신 직후 전 축은 서보 오프가 기본 — `SetServoOn` 후 상태 확인을 거쳐 모션 지령 |
| 2.3 | **GetStatus 기반 상태 확인 없이 진행** | MAJOR | `GetStatus` 미검출, 또는 상태 확인 대신 고정 `Sleep`으로 시퀀스 진행하는 구간 | Engine State(Communicating)·서보온·모션 완료를 `GetStatus`로 확인 후 다음 단계로 진행(타임아웃 포함) |
| 2.4 | **원점 미확립 상태에서 절대 위치 운전** | MAJOR | `StartHome` 부재 + 절대 위치 지령 사용(수동) — 원점 확립 절차 유무 확인 | 원점 복귀(`StartHome`) 또는 좌표 확립 절차를 운전 전에 수행 (튜토리얼4 "원점과 좌표" 참조) |

---

## 카테고리 3: 에러 처리 (4항목)

근거: 오류 코드 모듈별 분류(wmx3-user-manual-kr §5 오류 코드), v3.7 오류 코드 값 시프트(wmx37-user-manual-kr 릴리즈 노트).

| # | 항목 | 심각도 | 탐지 방법 | 수정 방향 |
|---|------|--------|-----------|-----------|
| 3.1 | **반환 코드 미확인** | CRITICAL | 주요 API(`CreateDevice`, `StartCommunication`, `SetServoOn`, `StartHome`, 모션 지령)의 반환값이 대입·비교 없이 버려지는 호출문(수동) | 모든 WMX3 API 호출의 반환 코드를 확인하고 실패 분기(정지/재시도/보고)를 둔다 |
| 3.2 | **오류코드 정수 하드코딩** | MAJOR | `73734`, `73735`, `0x1200` 등 오류코드로 보이는 정수 리터럴 비교 | 심볼 상수로 교체 — v3.7에서 API버퍼 오류코드 값이 +1 시프트됨(카테고리 6.6 참조). 정수 비교는 버전 간 파손 |
| 3.3 | **재시도 vs 중단 전략 부재** | MINOR | 오류 분기에서 일괄 무시(continue)·무조건 종료만 존재(수동) | 오류를 재시도 가능/불가로 분류하고 재시도 상한·백오프·최종 중단 기준을 명시 |
| 3.4 | **오류 시 진단 정보 미기록** | MINOR | 오류 분기에 로깅 부재; 오류 코드 수치만 출력하고 문맥(축·API명) 없음 | 오류 코드·축 번호·호출 API·상태를 기록. WMX3의 데이터 로그/API 로그 기능과 연계해 재현 진단 확보 |

---

## 카테고리 4: 성능/실시간성 (5항목)

근거: 트리거 모션 — "Windows API 호출 타이밍의 지연·지터 제거" 명문, API 버퍼(링 버퍼), 고속 I/O "Ex" 접미어 함수(어드레스 공간 직접 액세스, **ApiBuffer에서 실행 불가**), 대기 작업(멀티스레드·타임아웃), RTX SDK 실시간 앱 주의사항 (wmx37-user-manual-kr §모션/기타 기능·지원 사양).

| # | 항목 | 심각도 | 탐지 방법 | 수정 방향 |
|---|------|--------|-----------|-----------|
| 4.1 | **바쁜 폴링 루프** | MAJOR | `while` 루프 내 `GetStatus` + `Sleep(0)`, `Sleep(1)`, `sleep_for`, `Thread.Sleep` 조합 | 이벤트(EventControl)·대기 작업(타임아웃 지정)·트리거 모션으로 대체해 CPU 낭비와 반응 지연 제거 |
| 4.2 | **타이밍 크리티컬 경로에서 통상 API 사용** | MAJOR | "I/O 조건 감지 → 모션 개시" 등 시간 민감 로직을 앱 스레드에서 직접 수행하는 구간(수동) | 트리거 모션·ApiBuffer·이벤트로 엔진 측 실행으로 이관 — Windows API 호출 타이밍의 지연·지터 제거(매뉴얼 명문) |
| 4.3 | **고속 I/O Ex 함수 미활용** | INFO | 고빈도 I/O 액세스 루프에서 통상 I/O 함수만 사용(수동) | "Ex" 접미어 고속 I/O 함수 검토 — 통상 API 실행 처리를 우회해 어드레스 공간 직접 액세스 |
| 4.4 | **ApiBuffer 내 Ex 함수 사용** | CRITICAL | `ApiBuffer` 사용 파일에서 `Ex(` 접미 호출 공존 시 해당 호출이 버퍼에 기록되는지 확인(수동 — Win32 `...Ex` API 오탐 주의) | Ex 접미어 함수는 **ApiBuffer에서 실행 불가** — 버퍼 기록 구간에서는 통상 I/O 함수로 대체 |
| 4.5 | **RT 앱 결정성 저해 요소** | MINOR | `IMDLL_RT.lib` 링크 프로젝트(RTX SDK 실시간 앱)에서 `printf`, `cout` 등 콘솔 출력·무한 루프 | RT 공간 앱에서는 콘솔 출력이 결정성에 영향 — 최소화하고 무한 루프 금지. RTX SDK는 별도 IntervalZero 라이선스 필요(적용 여부 먼저 확인) |

---

## 카테고리 5: 안정성/안전 (5항목)

근거: Watchdog·리미트 스위치·보정(wmx3-user-manual-kr §5 기타 기능), 토크 제한 `Config::`·MaxTorqueLimitRamp·갠트리/동기(wmx37-user-manual-kr).

| # | 항목 | 심각도 | 탐지 방법 | 수정 방향 |
|---|------|--------|-----------|-----------|
| 5.1 | **Watchdog 타임아웃 설계 미검토** | MAJOR | `SetWatchdog` 검색(수동) — 0 지정(운영 환경 무효화) 여부·타임아웃 값의 복구 시나리오 정합 확인; 미검출 시 기본 15초(`ImAliveTimeOut`) 의존임을 리포트에 명시(미검출 자체는 결함 아님) | 복구 시나리오(앱 크래시→재기동→재접속)에 맞춰 타임아웃을 설계·명기. 운영 환경에서 `SetWatchdog(0)` 무효화 금지 — 무효화 시 닫히지 못한 디바이스가 엔진 재기동까지 유지 |
| 5.2 | **리미트 미구성** | MAJOR | 리미트 스위치/소프트웨어 리미트 파라미터 설정 코드 부재(파라미터 설정부 Read, 수동) | 리미트 스위치 처리·소프트웨어 리미트를 축별로 구성. LS Type은 명시 설정(카테고리 6.7 연계) |
| 5.3 | **토크 제한 미구성** | MAJOR | `SetMaxTrqLimit`, `SetPositiveTrqLimit`, `SetNegativeTrqLimit` 미검출 | 축별 토크 제한을 구성(v3.7은 `Config::` 소속). 급변 완화가 필요하면 MaxTorqueLimitRamp(3.7 신설) 검토 |
| 5.4 | **타임아웃 없는 대기** | MAJOR | 대기 작업·완료 대기 루프에 타임아웃 인수/탈출 조건 부재(수동) | 모든 대기에 타임아웃을 지정하고 초과 시 오류 처리(정지·보고). 무한 대기 금지 |
| 5.5 | **갠트리/동기 축 보호 부재** | MAJOR | `Sync`, `Gantry` 검색 → 동기/갠트리 사용 지점에서 오류 시 해제·정지 처리 유무(수동) | 동기 이탈·오류 시 안전 정지 시퀀스를 정의하고, 갠트리는 전용 원점 복귀 절차(갠트리 원점복귀)를 준수 |

---

## 카테고리 6: v3.6u3 → v3.7 마이그레이션 (8항목)

근거: wmx37-user-manual-kr 릴리즈 노트(`kr/release-notes/index.html`) — 호환성 깨짐 8건 전수. 3.6u3 코드를 3.7로 이식했거나 이식 예정인 프로젝트에 적용.

| # | 항목 | 심각도 | 탐지 방법 | 수정 방향 |
|---|------|--------|-----------|-----------|
| 6.1 | **ClosedLoop 구 명명 잔존** | MAJOR | `StartController`; ClosedLoop 문맥에서 구 `Command` 클래스 사용(수동) | `StartController`→`StartClosedLoop`, `Command`→`ClosedLoopCommand`로 갱신. 멤버 명명 camelCase→PascalCase 변경도 반영 |
| 6.2 | **삭제된 토크 커맨드 클래스 사용** | MAJOR | `TriggerTrqCommand`, `StartRampTimeTrq` (구 토크 커맨드 5클래스 계열) | 3.7에서 5클래스 삭제(컴파일 오류로 즉시 드러남) — 빌더 패턴 `TrqCommand`(`SetTrigger`/`SetRamp`/`SetRampRate`/`SetRampTime`) + `StartTrq` 계열로 대체 |
| 6.3 | **토크 램프 시간 단위 미변환** | CRITICAL | `SetRampTime` 인수가 정수 리터럴(사이클 수로 의심)인 곳; 사이클 수 계산식 잔존 | 단위가 인터럽트 사이클 수(uint)→**초(double)**로 변경 — `timeSeconds = rampCycleTime × interruptPeriod_ms / 1000`으로 변환. 미변환 시 램프 시간이 조용히 달라짐 |
| 6.4 | **`Torque::`/`Velocity::` 함수 잔존** | MAJOR | `SetMaxTrqLimit`, `SetPositiveTrqLimit`, `SetNegativeTrqLimit`, `SetMaxMotorSpeed` 호출부의 소속 스코프가 `Torque`/`Velocity`인지 확인 | 토크 제한·최대 모터 속도 함수는 **`Config::`로 이동** — 호출 스코프를 Config로 갱신 |
| 6.5 | **ApiBuffer API 변경 미반영** | MAJOR (기록 중 채널 조건부 동작은 CRITICAL) | `ApiBufferCondition`(구 2번째 인수 코드), 멀티채널 함수 구 시그니처; 기록 중 채널에서 `Execute`/`Halt`/`Clear`/`Rewind` 호출부(수동) | `FlowIf`/`Wait`는 다중조건 트리(`ApiBufferMultiCondition`)로, 멀티채널 함수는 `ApiBufferChannelSelection` 오버로드로 갱신. 기록 중 채널에서의 호출은 `AlreadyRecordingForSpecifiedChannel` 오류가 됨을 처리(조용한 동작 변화 — v37-migration.md ⑤-1 CRITICAL) |
| 6.6 | **오류 코드 값 시프트 미대응** | CRITICAL | `0x12006`, `73734` 등 API버퍼 오류코드 정수 리터럴; 오류코드를 파싱하는 외부 스크립트/로그 분석기 | `RewindBlockIndexOutOfRange`(0x12006) 삽입으로 후속 API버퍼 오류코드가 +1 시프트(예: `AlreadyRecordingForSpecifiedChannel` 73734→73735) — 심볼 상수로 교체하고 외부 파서도 점검 |
| 6.7 | **LS Type 기본값 변경 미인지** | MAJOR | 리미트 스위치 파라미터 설정부에서 LS Type을 명시하지 않고 기본값에 의존하는 곳(수동) | 기본값이 None→**Dec**로 변경 — 의도한 타입을 명시적으로 설정해 버전 무관하게 동작 고정 |
| 6.8 | **SetCommandPos/SetFeedbackPos 동시 호출** | MAJOR | `SetCommandPos`, `SetFeedbackPos` — 두 함수를 같은 시점에 함께 호출하는 부위 | 3.7부터 동시 호출 시 에러 반환 — 호출을 분리하고 각 반환 코드를 확인 |

---

## 카테고리 7: 코드 품질 (4항목)

| # | 항목 | 심각도 | 탐지 방법 | 수정 방향 |
|---|------|--------|-----------|-----------|
| 7.1 | **매직 넘버 축 번호** | MINOR | 모션·서보 API 호출에 축 번호를 정수 리터럴로 직접 전달하는 곳(수동 — 호출 인수 확인) | 축 번호를 명명 상수/enum/설정으로 정의(예: `AXIS_X`) — 배선 변경·축 재배치 시 일괄 수정 가능하게 |
| 7.2 | **설정 하드코딩** | MINOR | `ec_network.def`, `simu_network.def`, 절대 경로 리터럴, IP 리터럴 | 구성 파일 경로·네트워크 정의·장비 파라미터를 설정 파일/명령행 인수로 외부화 |
| 7.3 | **공유 상태 스레드 안전성** | MAJOR | 여러 스레드에서 접근하는 상태 캐시·플래그·최근 오류 변수의 동기화 부재(수동) | 앱 측 공유 상태를 뮤텍스/원자적 접근으로 보호. 대기 작업은 매뉴얼의 멀티스레드·타임아웃 규칙에 따라 사용 |
| 7.4 | **초기화/종료 시퀀스 중복** | MINOR | `CreateDevice`~`SetServoOn` 시퀀스가 여러 파일/함수에 복제되어 있는지 확인 | 공통 래퍼(세션 클래스)로 단일화 — C++ RAII/C# using 기반으로 생명주기·시퀀스 규칙을 한 곳에서 보장 |

---

## 보충 섹션 R: 로봇 옵션(Robot Option) 사용 시 추가 확인 (6항목)

프로젝트가 Robot Option(다관절 로봇 제어)을 사용하는 경우(스캔에서 `RobotMotion`, `Kinematics`, `StartPTPPos` 검출)에만 적용하는 보충 섹션 — 위 7카테고리 35항목과 **별도**로 집계한다. 근거: `wmx3-robot-help-kr` 다이제스트(§3 프로그래밍 가이드 — 좌표계·로봇 모션·충돌 감지·에러 코드, **v3.6u3 기준** — v3.7 로봇 변경 여부는 Robot Option 릴리즈 노트 확인).

| # | 항목 | 심각도 | 탐지 방법 | 수정 방향 |
|---|------|--------|-----------|-----------|
| R.1 | **URDF/XML 링크 관성 누락 상태로 충돌 감지 기대** | MAJOR | 충돌 감지 사용 흔적 + 로봇 정의 XML/URDF 파일에 링크 관성(inertia) 정보 누락(파일 Read, 수동) | 충돌 감지 전제조건 ① — URDF/XML에 **모든 링크의 관성** 기재. 누락 시 충돌 감지가 무력화됨 |
| R.2 | **SetToolInfo 미호출** | MAJOR | 충돌 감지 사용 + `SetToolInfo` 미검출 | 전제조건 ③ — `SetToolInfo`로 tool 정보 설정. 관성행렬 미포함 시 **점질량 가정**임을 인지하고 필요 시 관성행렬 포함 |
| R.3 | **baseJointCoordinate 비영(非零) 상태로 충돌 감지 기대** | MAJOR | `baseJointCoordinate` 설정부 Read — point/rotation에 0 이외 값 대입 + 충돌 감지 병용(수동) | 전제조건 ④ — `RobotMotionParam.robotParam.baseJointCoordinate`의 point/rotation **전부 0**이어야 충돌 감지 동작 |
| R.4 | **Joint/Cartesian 좌표 혼용 실수** | MAJOR | PTP/CP 지령의 목표값 구성부 Read — 조인트 각도 값과 Cartesian(X,Y,Z + Rx,Ry,Rz) 값의 좌표계/단위 혼동(수동) | 시나리오별 사용 좌표계(Joint/Cartesian/Robot)를 명시하고, 변환은 Coordinate 모듈 API로 일원화 |
| R.5 | **로봇 에러 코드 미처리** | MAJOR | 로봇 API(`RobotMotion` 계열) 반환 코드 처리부에 로봇 전용 에러 코드 분기 부재(수동) | 로봇 전용 에러 코드(§3 `..._guide__error__code.html`)를 오류 처리 체계에 포함 — 일반 WMX3 오류와 구분해 진단 |
| R.6 | **티칭 데이터 관리 부재** | MINOR | 티칭 포인트가 코드에 리터럴로 산재; 버전 관리·백업 없는 티칭 데이터(수동) | 티칭 데이터를 외부 데이터(파일/설정)로 분리하고 변경 이력을 관리 (티칭 API는 Coordinate 모듈) |

---

## 항목 수 집계

| 카테고리 | 항목 수 |
|---------|---------|
| 1. 생명주기/리소스 | 5 |
| 2. 시퀀스 정합성 | 4 |
| 3. 에러 처리 | 4 |
| 4. 성능/실시간성 | 5 |
| 5. 안정성/안전 | 5 |
| 6. v3.7 마이그레이션 | 8 |
| 7. 코드 품질 | 4 |
| **합계** | **35** |

> 로봇 옵션 사용 프로젝트는 여기에 **보충 섹션 R(6항목)**을 추가 적용 — 7카테고리 35항목 + 로봇 보충 R.
