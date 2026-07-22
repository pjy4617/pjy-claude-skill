# 시뮬레이터 플랫폼 (SimuPlatform) 구성 가이드

> **근거**: WMX3.7 사용자 매뉴얼(KR) 시뮬레이터 플랫폼 장 — 로컬 미러 `kr/guide/simu/` 하위
> `index.html`(개요) / `use.html`(유효화) / `network_def.html`(simu_network.def) / `precautions.html`(유의사항) / `supported_nic.html`(NIC) / `error_codes.html`(에러 코드).
> 3.6u3 CHM 다이제스트(`wmx3-user-manual-kr`) §6 시뮬레이터 플랫폼과 동일 계보.

## 1. 개요

SimuPlatform은 WMX3의 시뮬레이션 기능을 구현하는 플랫폼 모듈이다. **가상축**을 시뮬레이션하여 실 하드웨어 없이 모션을 확인하거나, 특정 기능과 결합해 다른 플랫폼의 물리 축 제어에 활용할 수 있다(출처: `kr/guide/simu/index.html`). WMX3는 플랫폼 모듈 교체만으로 애플리케이션 변경 없이 통신 프로토콜을 바꿀 수 있으므로(다이제스트 개요), 시뮬레이터에서 검증한 앱 코드를 그대로 EtherCAT 플랫폼으로 가져갈 수 있다.

- API: C++ `simuApi` 네임스페이스, .NET `WMX3ApiCLR.SimuApiCLR` (출처: 3.6u3 다이제스트 §8)
- **NIC 불필요** — "시뮬레이터 플랫폼에서는 NIC는 필요하지 않습니다" (출처: `kr/guide/simu/supported_nic.html`)

## 2. SimuPlatform 유효화 (Module.ini)

Module.ini 파일에서 `SimuPlatform.rtdll`이 유효한 `[Platform x]` 섹션으로 존재해야 한다(출처: `kr/guide/simu/use.html`):

| 키 | 의미 |
|----|------|
| `Location` | SimuPlatform.rtdll이 배치된 폴더 |
| `DllName` | rtdll 파일명 (`SimuPlatform.rtdll`) |
| `Disable` | 이 플랫폼을 유효화하려면 `0` |

```ini
; Module.ini 예 (원문 예시 — xxx는 사용하는 실 플랫폼으로 치환)
MessageLevel = 0
PrintLog = 0

[Platform 0]
Location = .\platform\xxx\
DllName = xxx.rtdll
disable = 0

[Platform 1]
Location = .\platform\simu\
DllName = SimuPlatform.rtdll
disable = 0
```

**동작 규칙** (출처: `kr/guide/simu/use.html`):

- SimuPlatform 타이머를 인터럽트 프로세스로 쓰려면 SimuPlatform에 인터럽트를 할당해야 하며, 인터럽트는 비활성화되지 않은 플랫폼에 **Module.ini 정의 순으로** 할당된다.
- 기본값(UserDef=0)으로 SimuPlatform은 **할당되지 않은 모든 축을 가상축으로 설정**한다.
- 비시뮬레이터 플랫폼과 함께 쓸 때 모든 축이 가상축이 되지 않게 하려면 **SimuPlatform을 비시뮬레이터 플랫폼 뒤에 정의**한다. SimuPlatform이 먼저 정의된 경우에는 `UserDef`로 원하는 축만 가상축으로 지정한다.
- 원문에는 `Module.ini` / `Modules.ini` 표기가 혼재하나 동일 파일을 가리킨다(다이제스트 §3은 Module.ini).

## 3. 시뮬레이션 정의 (simu_network.def)

설정 파일은 **SimuPlatform.rtdll과 동일한 폴더**에 두며, 모든 설정 이름·값은 대소문자를 구별하지 않고 `name = value` 형식이다(출처: `kr/guide/simu/network_def.html` — 이하 이 절 전부 동일 출처).

### 섹션

| 섹션 | 의미 | 유효 범위 |
|------|------|-----------|
| `[Master x]` | 마스터 x의 정보 | x: 0–1 |
| `[Axis x]` | 축 x의 정보 | x: 0–127 |

- 마스터가 하나면 Master 섹션 생략 가능(파일 처음의 파라미터가 유일 마스터에 적용).
- 복수 마스터를 쓰려면 Module.ini의 `NumOfMaster`·`NumOfInterrupt`도 적절히 설정해야 한다.
- `[Axis x]`는 `UserDef = 1` 줄 뒤에 정의하며, 각 마스터에서 축 번호는 0부터 시작한다. 섹션명 `[Axis x]`의 x는 축 인덱스와 무관하고, 실제 축 인덱스는 `Index` 키로 지정한다.

### 마스터 설정

| 이름 | 설명 | 유효값 | 기본값 |
|------|------|--------|--------|
| `CommCycle` | 통신주기(us) | 8000/4000/3000/2000/1000/500/250/125 | 1000 (1ms) |
| `NumOfAxes` | SimuPlatform에 할당할 축 수 | 미지정 시 사용 가능한 모든 축 | — |
| `StartAxis` | 할당 시작 축 인덱스 | 미지정 시 첫 사용 가능 인덱스 | — |
| `PrintLog` | 통신 정지 후 로그 출력 | 0/1 | 0 |
| `MessageLevel` | 콘솔 메시지 레벨(Module.ini 설정을 덮어씀) | 0(에러)~3(디버그) | 0 |
| `UserDef` | 축별 네트워크 정보 정의 활성화 | 0/1 | 0 |

### 축 설정 (UserDef = 1일 때)

가상축은 IO 데이터를 피드백 소스로 쓰거나, 지령을 IO 데이터로 복사할 수 있다:

| 분류 | 키 | 형식 |
|------|----|------|
| 축 지정 | `Index` (0–127) | 정수 |
| 피드백 소스 | `PosFb` / `VelFb` / `TrqFb` / `AlmCode` | `IoType;IoAddr;IoSize` |
| 피드백 소스(비트) | `SrvOnFb` / `AlmFb` / `HSFb` / `LSPFb` / `LSNFb` | `IoType;IoAddr;IoBit` |
| 지령 복사처 | `PosCmd` / `VelCmd` / `TrqCmd` | `IoType;IoAddr;IoSize` |
| 지령 복사처(비트) | `SrvOnCmd` / `AlmCLR` | `IoType;IoAddr;IoBit` |

- `IoType`: 0=입력, 1=출력 / `IoAddr`: IO 주소 / `IoSize`·`IoBit`: 길이·비트
- **★ 피드백 소스를 지정하지 않으면 시뮬레이터 모듈이 피드백을 생성하며, 그 값은 지령치를 그대로 복사한 값이다. 이 경우 모션 모듈(coreMotion.rtdll 등)에게 가상축은 "편차 없이 완벽히 추종하는 축"으로 동작한다.** — 시뮬레이터 검증 경계(§6)의 근거.
- 지령 복사처를 지정하지 않으면 지령이 IO로 출력되지 않는다(외부 출력 없음).

```ini
; 예 (원문 예시): IO 입력 0~3바이트 = 축 3의 위치 피드백, IO 출력 12~15바이트 = 축 3의 위치 지령 복사
UserDef = 1
[Axis 0]
Index = 3
PosFb = 0;0;4
VelFb = 0;4;4
TrqFb = 0;8;4
PosCmd = 1;12;4

[Axis 1]
Index = 6
```

### Promisc (특수)

`Promisc = 1`이면 동일 축 인덱스의 실제 축과 가상축이 공존할 수 있다(지령은 복사처 IO로 출력되면서 동시에 실제 축도 제어, 피드백은 PDO 우선). **원문 주의**: 특수한 용도나 명확한 목적이 없는 통상 사용은 피할 것.

## 4. 유의사항 (출처: `kr/guide/simu/precautions.html`)

- SimuApi의 `SetIn***`(Bit/Byte/Bytes/Bits) 함수는 원래 **읽기 전용인 IO Input 주소에 데이터 쓰기**를 가능하게 한다 → 테스트에서 스위치/알람 신호 주입에 활용(`references/test-strategy.md` §5).
- 단, Simulation + EtherCAT 같은 **멀티 마스터** 운용 시 동일 IO Input 주소에 대해 두 플랫폼 간 **데이터 간섭**이 발생할 수 있다(예: 같은 주소에 Simu=1, EtherCAT=0을 쓰면 값 불확실). 하이브리드 구성 테스트 시 주소 영역을 분리할 것.

## 5. 에러 코드 (출처: `kr/guide/simu/error_codes.html`)

시뮬레이터 API 에러 코드는 `SimuErrorCode` 클래스에 정의되며 Simu 클래스 함수가 반환할 수 있다. 문서화된 값: `SimuError` = 4096 (0x1000, "Simu Error. 예약").

## 6. 시뮬레이터로 검증 가능한 것 / 불가능한 것 (경계)

기본 가상축의 피드백 = 지령 복사(편차 0)라는 성질(§3 ★)이 경계를 결정한다.

### 검증 가능

| 항목 | 조건 |
|------|------|
| API 시퀀스·상태 천이 (CreateDevice→StartCommunication→SetServoOn→모션→역순 종료, GetStatus) | 기본 구성 그대로 |
| 모션 지령 로직 — 프로파일·보간·PVT·트리거·ApiBuffer·이벤트의 지령 생성 경로와 목표 도달 | 기본 구성 그대로 |
| 기어비·사용자 단위·단회전 등 위치 파이프라인 설정 정합성 | 기본 구성 그대로 |
| 홈/리미트 스위치 연동 로직 (원점복귀, 리미트 정지) | `UserDef=1` + `HSFb`/`LSPFb`/`LSNFb` IO 매핑 + SimuApi `SetIn*` 주입 |
| 알람 처리 경로 (알람 상태·코드 수신 시 앱의 정지/복구 로직) | `AlmFb`/`AlmCode` 매핑 + 주입. 값 모의일 뿐 실 드라이브 알람 거동은 아님 |
| 멀티 플랫폼 공존 구성의 축 배치 | 정의 순서·UserDef 규칙 준수, IO 간섭 주의(§4) |

### 검증 불가 / 제한

| 항목 | 이유 |
|------|------|
| 실 서보 편차·게인 튜닝·진동/동특성 | 기본 피드백 = 지령 복사(편차 0) — 추종 오차가 존재하지 않음 |
| MechEnd 계열 원점복귀의 기계 끝단 검출 | 피드백=지령 복사(편차 0)라 지령-피드백 위치 차이가 발생하지 않아 검출 조건 불성립(§3 ★) — 별도 IO 모의 없이는 제한적 |
| EtherCAT 네트워크 — ENI·`ec_network.def`·슬레이브 구성·배선·NIC | 시뮬레이터는 NIC 자체가 불필요, 네트워크 계층이 존재하지 않음 |
| 실 드라이브 알람 코드의 의미·복구 절차 | 주입 알람은 값 모의 |
| 실기 타이밍·지터 | SimuPlatform은 타이머 기반 인터럽트로 동작 — 실 네트워크·부하 조건과 다름 |
| 기계 요소 — 백래시·마찰·관성·기구 간섭 | 물리 모델 없음 |
| 하드웨어 안전 회로 — 비상정지·안전 입력 실배선 | 실기 전용 |

→ 실기 전환 시 점검 항목은 `SKILL.md`의 "실기(EtherCAT) 전환 전 체크리스트" 참조.
