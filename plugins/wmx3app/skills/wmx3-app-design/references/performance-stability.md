# WMX3 애플리케이션 성능·안정성 전략

비실시간 OS(Windows) 앱에서 WMX3을 쓸 때의 성능(지터·응답)과 안정성(감시·보호·진단) 설계 지침.
사실은 모두 다이제스트(`wmx3-user-manual-kr`, `wmx37-user-manual-kr`)와 v3.7 매뉴얼 미러에서 확인된 것이다.

## 1. 지터의 근원과 3가지 제거 수단

API 함수를 Windows 애플리케이션에서 직접 호출하면 Windows가 실시간 OS가 아니기 때문에 실행 타이밍에
지연이 발생할 수 있다 (출처: 미러 `guide/motion/other_functions/other_api_buffer/index.html` 원문).
타이밍 크리티컬 동작에는 다음 3수단으로 **판정과 실행을 엔진 측으로 옮긴다**.

| 수단 | 원리 | 적용 대상 |
|------|------|-----------|
| ① 트리거 모션 | 트리거 조건(잔여 시간/거리·완료·목표까지 거리 등) 충족까지 엔진이 실행을 지연 → "Windows에서 호출되었을 때의 실행 타이밍에 의한 지연이나 지터가 없어진다" | 모션 개시 타이밍 (연속 동작 체인·동시 개시) |
| ② API 버퍼 | API 함수를 미리 버퍼에 저장 → "통신 사이클의 정확도의 타이밍으로 순차 실행" | 사전 계획 가능한 시퀀스 전체 |
| ③ 이벤트 | 입력 조건(코어모션·I/O·UserMemory 등) → 출력 동작(모션·API버퍼·I/O 등)을 엔진이 처리 | 조건 반응형 동작 (센서 → 즉시 반응) |

출처: ① 미러 `guide/motion/trigger/trigger_overview.html` ② 미러 `other_api_buffer/index.html`
③ `wmx37-user-manual-kr` digest §기타 기능(이벤트 — 입력/출력 구성).

## 2. API 버퍼 설계 지침

출처: 미러 `other_api_buffer/apb_architecture.html`, `index.html` + `wmx37` digest.

- **구조**: 버퍼는 IMDLL 내부에 위치. 채널 0 ~ `maxApiBufferChannel`-1로 분리되며 채널별 독립 동작.
  크기는 `CreateApiBuffer`로 할당 시 지정. **링 버퍼** 구조 — 크기 N에 대해 실제 저장은 N-1
  (출처: `wmx37` digest §기타 기능 "API 버퍼 — 링 버퍼 N-1 상세").
- **기록/실행**: `StartRecordBufferChannel`/`EndRecordBufferChannel`로 기록 채널 전환.
  실행 시점은 `Execute`와 버퍼 내 `Wait`/`Sleep` 함수로 제어. `Rewind(blockIndex)`로 부분 재실행(3.7).
- **흐름 제어**: `FlowIf` 등 Flow 제어 + 3.7 다중조건 트리 `ApiBufferMultiCondition`(AND/OR/XOR/NOT 게이트).
  기존 `ApiBufferCondition*` 2번째 인수 코드는 3.7에서 업데이트 필요 (출처: `wmx37` digest 사양 변경).
- **오류 로그**: 버퍼 실행 API의 오류는 즉시 반환 대신 채널별 오류 로그(최신 `maxApiBufferErrorLog`개,
  `None`은 저장 안 함)에 기록 — **버퍼 실행 시퀀스 뒤에 오류 로그 확인 단계를 설계에 넣을 것**.
- **v3.7 `GetCumulativeBlockCount`**: 버퍼 처리와 동기화된 블록 카운트로 오류 로그의 API 호출을 식별
  (`GetStatus`와 달리 추가 직후에도 최신값 보장. 출처: `wmx37` digest 릴리즈 노트).
- **제약**: 일부 API는 버퍼에 기록 불가 또는 동작 특성이 다름("특별한 성질을 가진 API 함수" 참조).
  기록 중 채널에 `Execute`/`Halt`/`Clear`/`Rewind` 호출 시 `AlreadyRecordingForSpecifiedChannel` 오류(3.7 명확화).

## 3. 고속 I/O "Ex" 함수

출처: 미러 `guide/motion/other_functions/other_io/expedited.html` 원문.

- `Ex` 접미어 I/O 함수는 **통상의 API 실행 처리를 우회하여 입력/출력 어드레스 공간 메모리에 직접 액세스**한다.
- 데이터 경로 비교 (원문 그대로):
  - 통상: `IoApi → IMDLL → WMX3Engine(Module Manager) → IoModule → … → IoApi`
  - 고속: `IoApi(Ex) ↔ MPInterface`
- **적용 기준**: 많은 I/O 함수를 단시간에 호출하는 경우, I/O 응답을 최대한 빠르게 해야 하는 경우.
- **제약**: 통상 API 실행 처리를 우회하므로 **API 버퍼에서 고속 I/O 함수를 실행할 수 없다**.
  → 설계 시 "버퍼 시퀀스 내 I/O"는 통상 I/O 함수, "앱 루프의 대량/저지연 I/O"는 Ex 함수로 분리.

## 4. 폴링 vs 이벤트/Wait — 대기 설계

- 상태 변화 감지를 `GetStatus` 바쁜 폴링(짧은 Sleep 루프)으로 구현하지 말 것 — CPU 낭비와 반응 지터.
  조건 반응은 이벤트(§1-③), 시퀀스 내 대기는 ApiBuffer `Wait`, 스레드 대기는 **대기 작업**
  (멀티스레드·타임아웃 지원. 출처: `wmx37` digest §기본 모션 "대기 작업")을 우선한다.
- 블로킹 함수는 다음 통신 사이클 종료까지 응답이 지연될 수 있다
  (출처: 미러 `architecture_device_types.html`) — UI 스레드에서 직접 호출하지 않는다.
- 빠른 응답이 불필요한 백그라운드 Task(모니터링 등)는 LowPriority 디바이스로 분리해
  본선 제어 디바이스의 응답성을 보호한다 (출처: 미러 `architecture_device_types.html`).
- 주기 반복 명령이 필요하면 CyclicBuffer(열기/닫기·명령 추가/실행·중단)를 검토한다
  (출처: `wmx37` digest §기타 기능 CyclicBuffer).

## 5. Watchdog — 비정상 종료 감시

출처: 미러 `guide/motion/other_functions/other_watchdog.html` 원문.

- 디바이스 생성 시마다 Watchdog 스레드가 생성되어 **100ms 주기**로 정상 동작을 보고한다.
- 앱이 `CloseDevice` 없이 비정상 종료하면, 타임아웃(기본 **15초** 또는 `Modules.ini`의
  `ImAliveTimeOut`) 경과 후 엔진이 디바이스를 자동으로 닫는다.
- `SetWatchdog`로 디바이스별 타임아웃 변경 가능 — **최소 1000ms**. 0 지정 시 무효화되지만,
  무효화하면 닫히지 못한 디바이스가 엔진 재기동까지 열린 채 유지되므로 **운영 환경에서는 무효화 금지**.
- Watchdog 타임아웃으로 마지막 디바이스가 닫히면 엔진도 자동 종료된다(`AutoQuitWithoutActiveDev`로 변경 가능).
- 설계 지침: 장비 복구 시나리오(앱 크래시 → 재기동 → 재접속)에 맞춰 타임아웃을 정하고 설계서에 명기.

## 6. 로그 기반 진단 설계

- WMX3은 **데이터 로그·API 로그·메모리 로그**를 제공한다 (출처: `wmx37` digest §기타 기능,
  `wmx3-user-manual-kr` digest §8 Log 클래스). 설계 단계에서 다음을 정한다:
  - 데이터 로그: 어떤 축/신호를 어느 상황(양산 상시/이슈 재현)에 수집할지
  - API 로그: 시퀀스 이슈 추적용 — 재현 시 활성화 절차
  - ApiBuffer 오류 로그 + `GetCumulativeBlockCount`(§2)로 버퍼 시퀀스 내 실패 API 식별
- **Motion Slowdown Factor(v3.7 신설)를 디버깅에 활용**: 인터럽트 단위 시간 스케일링(시간 제수)로
  팩터 N이면 1/N 속도 재생 — 고속 시퀀스의 육안 검증·충돌 리스크 저감에 유용.
  `SetMotionSlowdown`/`GetMotionSlowdown` (출처: `wmx37` digest 릴리즈 노트,
  미러 `guide/motion/basic_motion/slowdown_factor/`). **양산 코드에 잔류 금지** — 리뷰 항목으로 명기.

## 7. RTX SDK 실시간 앱 — 판단 기준

출처: `wmx37-user-manual-kr` digest §지원 사양(`support-spec/rtx_dev_realtime.html`) 요약.

- RTX SDK로 RTX OS 위에서 동작하는 **실시간 앱**을 작성할 수 있다. `IMDLL_RT.lib` 링크(IMDll.dll 불필요),
  **VC++ 한정**.
- **⚠️ WMX3·RTX 런타임 라이선스와 별도로 IntervalZero RTX SDK 라이선스가 필요** (매뉴얼 명문).
- 실시간 앱 주의사항: 콘솔 출력이 결정성에 영향을 주며, 무한 루프 금지.
- **판단 기준**: 트리거 모션·ApiBuffer·이벤트(§1)로 타이밍 요구를 충족할 수 있으면 비RT 앱(배치 패턴 ①)을
  유지한다. RT 앱은 ①로 불가능한 사이클 단위 응답 로직이 앱 측에 있어야 할 때만 선택하고,
  라이선스 비용·VC++ 제약·개발 난이도를 설계서 리스크 절에 기록한다.

## 8. 안정성·안전 설계 체크리스트

| 항목 | 내용 | 심각도(미비 시) |
|------|------|------|
| 반환 코드 확인 | 모든 WMX3 API 반환 코드 확인. 오류코드 정수 하드코딩 금지(v3.7에서 API버퍼 오류코드 값 시프트 — `RewindBlockIndexOutOfRange` 0x12006 삽입으로 후속 코드 +1. 출처: `wmx37` digest 사양 변경) | CRITICAL |
| Watchdog | §5 기준 타임아웃 설계. 무효화(0) 금지 | MAJOR |
| 리미트 스위치 | 축별 리미트 구성. **v3.7에서 LS Type 기본값 None→Dec 변경** — 기본값 의존 코드 재확인 (출처: `wmx37` digest 사양 변경) | MAJOR |
| 토크 제한 램프 | **MaxTorqueLimitRamp(v3.7 신규)**: `SetMaxTrqLimitRampRate`/`Enable`, `AxisParam.enableMaxTrqLimitRamp`/`maxTrqLimitRampRate`/`posFErrorInstantMaxTrqLimitThreshold` — 급격한 토크 제한 변화 완화 | MAJOR |
| 기계 끝단 보호 | **Keep Mech End Torque Limit(v3.7 신규)**: 기계 끝단 감지 후 낮은 토크 제한 유지, `HomeParam.keepMechEndTorqueLimit`(기본 true) | MINOR |
| 타임아웃 있는 대기 | 무한 대기 금지 — 대기 작업의 타임아웃 사용 | MAJOR |
| 종료 시퀀스 | 모션 정지 → 서보 오프 → StopCommunication → CloseDevice(→.NET Dispose) 역순 정리, 예외 경로 포함 | CRITICAL |
| 토크 제한/최대 속도 API 위치 | v3.7에서 `Torque::`/`Velocity::` → `Config::`(`SetMaxTrqLimit`/`SetPositiveTrqLimit`/`SetNegativeTrqLimit`/`SetMaxMotorSpeed`) 이동 — 신규 설계는 Config:: 기준 (출처: `wmx37` digest 사양 변경) | MAJOR |

## 출처 요약

- v3.7 미러: `guide/motion/other_functions/other_api_buffer/index.html`·`apb_architecture.html`(버퍼 구조·오류 로그),
  `guide/motion/other_functions/other_io/expedited.html`(Ex 함수·경로·제약),
  `guide/motion/other_functions/other_watchdog.html`(Watchdog 수치),
  `guide/motion/trigger/trigger_overview.html`(지터 제거 명문),
  `guide/general/architecture_device_types.html`(블로킹·LowPriority)
- `wmx37-user-manual-kr` digest: 릴리즈 노트(GetCumulativeBlockCount·Slowdown·MaxTorqueLimitRamp·
  Keep Mech End·오류코드 시프트·LS Type·Config:: 이동), §지원 사양(RTX SDK 라이선스)
- `wmx3-user-manual-kr` digest: §5 기타 기능(로그·CyclicBuffer·이벤트), §8 Log 클래스
