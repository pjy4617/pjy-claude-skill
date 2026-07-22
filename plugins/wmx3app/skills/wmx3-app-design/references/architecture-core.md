# WMX3 아키텍처 코어 — 애플리케이션 설계 필수 지식

WMX3 애플리케이션 설계 전에 반드시 이해해야 하는 핵심 개념을 정리한다.
모든 사실은 WMX3 사용자 매뉴얼(v3.6u3 CHM 다이제스트 `wmx3-user-manual-kr` / v3.7 다이제스트
`wmx37-user-manual-kr`)과 v3.7 매뉴얼 한국어 미러(`kr/guide/general/`)에서 확인된 것이다. 각 절에 출처를 표기한다.

## 1. WMX3란 — 소프트웨어 모션 컨트롤러

WMX3은 Soft Servo Systems(Movensys)의 **소프트웨어 기반 모션 컨트롤러 라이브러리**다.
모든 기능은 `rtdll`(실시간 DLL)로 구현되어 필요한 모듈만 로드해서 사용하는 **모듈형 아키텍처**를 취하며,
사용하지 않는 모듈은 무효화해 시스템 리소스를 절약할 수 있다.

모듈형 구조의 이점 (출처: v3.7 미러 `kr/guide/general/architecture_overview.html`):

- 기능 개선·수정 시 시스템 전체를 갱신할 필요가 없다 (모듈 단위 갱신).
- **다른 플랫폼 모듈을 로드하면 사용자 애플리케이션을 변경하지 않고 통신 프로토콜을 변경**할 수 있다.
- 여러 플랫폼 모듈을 동시에 로드하면 **하이브리드 통신 프로토콜** 구성이 가능하다.
- 사용자 Rtdll을 개발하면 특수 제어 기능을 엔진 내부에 구현할 수 있다
  (→ 이것은 **wmx3md 플러그인**(모듈 개발)의 영역. 본 플러그인은 API를 호출하는 응용 프로그램 담당).
- 모듈 간 고속 데이터 교환이 가능하다.

언어 바인딩은 **C++ / .NET(WMX3ApiCLR) / Python** 3종.
API Reference는 C++ 기준으로 기술된다 (출처: `wmx3-user-manual-kr` digest 개요).

## 2. RT/비RT 배치 3패턴

WMX3 엔진과 사용자 애플리케이션의 배치는 3가지 패턴이 있다
(출처: v3.7 미러 `kr/guide/general/architecture_overview.html` — 데이터 흐름 그림 3종):

| 패턴 | 사용자 앱 | WMX3 엔진 | 용도 |
|------|-----------|-----------|------|
| ① 표준 | 비실시간 OS (Windows) | 실시간 OS (RTX) | 대부분의 장비 제어 앱. API 호출 지연·지터는 트리거 모션/ApiBuffer로 흡수 |
| ② RT 앱 | 실시간 OS (RTX 공간) | 실시간 OS | 최고 결정성이 필요할 때. RTX SDK 별도 라이선스 필요 (`references/performance-stability.md` §7) |
| ③ 엔진 비RT | 비실시간 OS | 비실시간 공간 | 엔진이 실시간 공간에서 동작하지 않는 구성 |

설계 시 기본값은 패턴 ①이다. 패턴 ②는 성능 요구가 트리거 모션·ApiBuffer·이벤트로 충족되지 않을 때만 검토한다.

## 3. 디바이스 모델 — CreateDevice / CloseDevice

애플리케이션은 `CreateDevice(path, DeviceType)`로 디바이스를 만들어 엔진과 연결하고,
종료 시 `CloseDevice()`로 닫는다. **.NET은 CloseDevice 후 `Dispose()` 호출이 필수**다
(미호출 시 GC가 비관리 리소스를 조기 해제하여 정의되지 않은 동작 발생.
출처: `wmx3-user-manual-kr` digest 핵심 아키텍처 / §4 보충정보 C++ vs .NET).

### 디바이스 유형 4종 (출처: v3.7 미러 `kr/guide/general/architecture_device_types.html`)

| DeviceType | 낮은 우선순위 | ExitWOCnt | 특성 |
|------------|:---:|:---:|------|
| `Normal` | × | × | 전용 API 프로세스 스레드 보유. 명령 처리·응답이 매우 빠름. 대부분의 앱은 이것만 사용 |
| `DeviceTypeLowPriority` | ○ | × | 통신 사이클 끝에서 시스템 처리 후 명령 1개씩 처리. 빠른 응답이 불필요한 Task 전용 |
| `DeviceTypeExitWOCnt` | × | ○ | 남은 디바이스 수 카운트에서 제외 (모니터링 툴 등) |
| `DeviceTypeLowpriorityExitWOCnt` | ○ | ○ | 위 둘의 조합 |

- 디바이스 유형을 지정하지 않으면 `Normal`로 생성된다.
- `CloseDevice`로 닫을 때 남은 디바이스가 0이 되면 **엔진이 종료**된다.
  `ExitWOCnt` 유형은 이 카운트에 포함되지 않으며, 엔진 종료 후 이 디바이스의 API 호출은
  `IMLibIsNotRunning` 오류를 반환한다.
- 블로킹 함수는 다음 통신 사이클이 끝날 때까지 응답이 지연될 수 있다.

### Watchdog (디바이스 생존 감시)

엔진은 디바이스 생성 시마다 Watchdog 스레드를 만들어 100ms 주기로 생존을 보고받는다.
앱이 `CloseDevice` 없이 비정상 종료하면 타임아웃(기본 15초 또는 `Modules.ini`의 `ImAliveTimeOut`) 후
엔진이 자동으로 디바이스를 닫는다. 상세와 `SetWatchdog` 설계 지침은
`references/performance-stability.md` §5 참조
(출처: v3.7 미러 `kr/guide/motion/other_functions/other_watchdog.html`).

## 4. 통신 개시와 서보 온 — 표준 시퀀스

출처: v3.7 미러 `kr/guide/general/architecture_comm_servoon.html`
(3.6u3 CHM `..._architecture__c_o_m_m__s_e_r_v_o_o_n.html`과 동일 계보).

1. `StartCommunication()` — `Module.ini`, 네트워크 정의 파일, `RtxTcpIp.ini` 설정으로
   서보 네트워크와 사이클릭 통신 개시를 시도한다.
2. 통신이 확립되면 `GetStatus()`로 취득하는 **Engine State가 `Communicating`** 이 된다.
3. **통신 시작 직후 모든 축은 서보 오프** 상태다. 서보 온/오프 상태는 GetStatus의 Servo On 상태로 확인한다.
4. `SetServoOn()`으로 서보를 켠다. **서보는 서보 온 상태에서만 위치 지령(Pos Cmd)을 따른다.**
   서보 오프 중에는 위치 지령이 매 사이클 피드백 위치와 같게 설정된다
   (→ 서보 오프 축을 손으로 움직인 뒤 서보 온하면 지령은 직전 피드백 위치와 같아짐).
5. 통신 정지는 `StopCommunication()`.

### 애플리케이션 표준 초기화/종료 골격

```text
[초기화]  CreateDevice → (CoreMotion 등 모듈 클래스 준비) → StartCommunication
          → GetStatus로 Engine State = Communicating 확인 → SetServoOn → 모션 API
[종료]    모션 정지 확인 → 서보 오프 → StopCommunication → CloseDevice → (.NET) Dispose
```

각 단계에서 반환 코드를 확인하고 다음 단계로 진행하는 것이 원칙이다
(구현 상세는 wmx3-app-implement 스킬의 references 참조).

## 5. 축 위치와 사용자 단위 — 위치 데이터 파이프라인

출처: `wmx3-user-manual-kr` digest 핵심 아키텍처
(토픽 `_w_m_x_d_o_c__a_r_c_h_i_t_e_c_t_u_r_e__p_o_s.html`, v3.7 미러 `kr/guide/general/architecture_pos.html`).

```text
Encoder Feedback (32bit 펄스, 서보 드라이브 반환)
  → 사이클마다 변화량 누적한 64bit 엔코더 피드백 (펄스, 멀티턴 반영)
  → Feedback Position(Actual Pos) = 펄스 ÷ 기어비 → 사용자 단위(user units)

지령은 역방향: Pos Cmd(사용자 단위) → 중간 엔코더 지령 → Encoder Command(32bit 펄스, mod 2^32)
```

변환에 관여하는 축 파라미터:

| 파라미터 | 역할 | 설계 시 결정 사항 |
|----------|------|------------------|
| Gear Ratio Numerator/Denominator | 펄스 ↔ 사용자 단위 변환비 | 사용자 단위(mm/deg/pulse)와 분해능 |
| Axis Polarity | 회전 방향 | 기구 방향과 좌표계 부호 일치 |
| Single Turn Mode / Encoder Count | 지정 펄스에서 0으로 wrap | 무한 회전축(턴테이블 등) 여부 |
| Home Offset | 원점 오프셋 | 원점 복귀 전략과 기계 좌표 정의 |
| Compensation | 피치오차·2D피치오차·백래시 보정 합산 | 정밀도 요구에 따른 보정 사용 여부 |

64bit 피드백은 ±2^63 범위 한계가 있다 (싱글턴 축은 무한 회전 가능).

## 6. API 클래스 지도 (wmx3Api 네임스페이스)

출처: `wmx3-user-manual-kr` digest §8 API Reference.

| 클래스 | 담당 |
|--------|------|
| `WMX3Api` | 메인 (디바이스·통신·엔진 제어) |
| `CoreMotion` | 기본 모션 (digest §5 기본 모션 구성: 프로파일·오버라이드·트리거·보간·대기 작업·동기·PVT·폐루프) |
| `AdvancedMotion` | 고급 모션 (Spline·경로 보간·Look-Ahead·E-CAM) |
| `PMMotion` | 프로파일 직접 하달 (자체 궤적 생성기 연동) |
| `Io` | 입출력 (고속 Ex 함수 포함) |
| `Compensation` | 보정 (피치/2D피치/백래시) |
| `ApiBuffer` | API 버퍼 (사전 계획 시퀀스의 결정론적 실행) |
| `CyclicBuffer` | 사이클릭 버퍼 |
| `EventControl` | 이벤트 (입력 조건 → 출력 동작) |
| `UserMemory` | 사용자 메모리 |
| `Log` | 데이터/API/메모리 로그 |

플랫폼 전용 네임스페이스: `ecApi`(EtherCAT) / `simuApi`(시뮬레이터).
.NET에서는 `WMX3ApiCLR`, `WMX3ApiCLR.SimuApiCLR` 등 `...CLR` 접미사 네임스페이스로 매핑되고,
멤버 변수 첫 글자 대문자·`IDisposable`/`Dispose` 규칙 차이가 있다
(출처: `wmx3-user-manual-kr` digest §4 보충정보 C++ vs .NET).

## 7. 설계 체크 요점

- [ ] 디바이스는 몇 개, 어떤 유형으로 만들 것인가 (기본 Normal 1개, 모니터링 별도면 LowPriority/ExitWOCnt 검토)
- [ ] 초기화/종료 시퀀스가 §4 표준 골격을 따르는가 (.NET이면 Dispose까지)
- [ ] 축별 기어비·사용자 단위·단회전·Home Offset·보정이 §5 표로 정의되었는가
- [ ] 필요한 API 클래스(§6)와 모듈이 식별되었는가
- [ ] RT/비RT 배치 패턴(§2)이 결정되었는가 — 기본은 패턴 ①

## 출처 요약

- `wmx3-user-manual-kr` digest (v3.6u3 CHM): 개요·핵심 아키텍처·§4 보충정보·§8 API Reference
- `wmx37-user-manual-kr` digest (v3.7 HTML): 기본 프로그래밍 지침 절
- v3.7 매뉴얼 미러 `kr/guide/general/`: `architecture_overview.html`, `architecture_device_types.html`,
  `architecture_comm_servoon.html`, `architecture_pos.html`
- Watchdog: `kr/guide/motion/other_functions/other_watchdog.html`
