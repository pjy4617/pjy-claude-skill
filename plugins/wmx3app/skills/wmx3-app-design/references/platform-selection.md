# WMX3.7 플랫폼 선택 가이드

WMX3은 통신 프로토콜을 **플랫폼 모듈(rtdll)** 교체만으로 바꿀 수 있고, 애플리케이션 코드는 변경되지 않는다
(출처: v3.7 미러 `kr/guide/general/architecture_overview.html`).
v3.7은 5종 플랫폼을 지원한다 (출처: `wmx37-user-manual-kr` digest 개요·섹션별 요약 "플랫폼 (5종)").

## 1. 플랫폼 5종 비교 표

| 플랫폼 | 모듈/API | 필수 구성 파일 | 용도 | 제약·비고 |
|--------|----------|----------------|------|-----------|
| **EtherCAT** | `EcPlatform.rtdll` / `ecApi` | `Module.ini` [Platform x] + `ec_network.def` + ENI 파일 | 실 장비 제어 표준. EtherCAT 슬레이브(서보·I/O) 네트워크 | 지원 NIC 확인 필요. DC(Distributed Clock) 인터럽트 사용 시 EcPlatform에 인터럽트 할당 |
| **시뮬레이터** | `SimuPlatform.rtdll` / `simuApi` | `Module.ini` [Platform x] + `simu_network.def` | **실 HW 없이 모션 검증**. 개발 초기·CI·리허설 | 기본 동작: 할당되지 않은 모든 축을 가상 축으로 설정(UserDef=0). 타 플랫폼과 혼용 시 정의 순서 주의(§3) |
| **M4** (3.7 신규) | M4 플랫폼 | 필수 오브젝트·지원 NIC (매뉴얼 M4 챕터) | M4 통신 장비 구성 | 상세 챕터(`guide/m4/`)는 **정본 CHM에만 수록** — 미러에 없음 |
| **TSN·CC-Link** (3.7 신규) | TSN 플랫폼 | 필수 오브젝트·지원 NIC (매뉴얼 TSN 챕터) | CC-Link IE TSN 장비 구성 | 상세 챕터(`guide/tsn/`)는 **정본 CHM에만 수록** |
| **EC-M4 / EC-TSN 하이브리드** (3.7 신규) | 복수 플랫폼 동시 로드 | 각 플랫폼의 구성 파일 병행 | EtherCAT + M4/TSN 혼합 네트워크 | 하이브리드 구성 일반 원칙은 §4 |

> M4/TSN 상세가 필요하면 정본 CHM
> (`/home/pjy4617/Repos/Movensys/wmx37-manual-KR/WMX3UserManual_kR.chm`, CP949)을 핀포인트 추출한다
> (출처: `wmx37-user-manual-kr` digest 헤더 — "정본 CHM에만 = M4/TSN guide 챕터").

## 2. 선택 플로차트

```text
실 하드웨어(서보/I/O)를 제어하는가?
├─ 아니오 (개발 초기·로직 검증·CI) ────────────→ 시뮬레이터 (SimuPlatform)
└─ 예
   ├─ 네트워크가 EtherCAT 단일 ────────────────→ EtherCAT (EcPlatform)
   ├─ CC-Link IE TSN 장비 사용 ────────────────→ TSN·CC-Link 플랫폼 (3.7)
   ├─ M4 장비 사용 ────────────────────────────→ M4 플랫폼 (3.7)
   └─ EtherCAT + M4/TSN 혼합 ──────────────────→ EC-M4 / EC-TSN 하이브리드 (3.7)

※ 실기 플랫폼을 선택했더라도, 개발·테스트 단계에서는 시뮬레이터 병행(또는 혼용) 구성을 권장.
   (wmx3-app-test 스킬의 references/simulator-platform.md 참조)
```

## 3. Module.ini 플랫폼 구성

플랫폼 활성화는 `Module.ini`의 `[Platform x]` 섹션으로 한다
(출처: v3.7 미러 `kr/guide/ec/ec_use.html`, `kr/guide/simu/use.html`).

```ini
; Module.ini 예 — EtherCAT + 시뮬레이터 병행
MessageLevel = 0
PrintLog = 0
[Platform 0]
Location = .\platform\ethercat\
DllName = EcPlatform.rtdll
disable = 0
[Platform 1]
Location = .\platform\simu\
DllName = SimuPlatform.rtdll
disable = 0
```

- `Location` — 플랫폼 rtdll이 배치된 폴더.
- `DllName` — rtdll 파일명.
- `Disable` — 유효화하려면 `0`.
- **인터럽트 할당은 무효/일시중단이 아닌 플랫폼에 `Module.ini` 정의 순으로** 이뤄진다.
  EtherCAT DC 신호를 인터럽트 프로세스로 쓰려면 EcPlatform에 인터럽트가 할당되어야 한다.
- 시뮬레이터 타이머를 인터럽트 프로세스로 쓰려면 SimuPlatform에 인터럽트를 할당한다.

### 시뮬레이터 + 실기 플랫폼 혼용 시 축 배치 주의 (출처: `kr/guide/simu/use.html`)

- SimuPlatform은 기본적으로 **할당되지 않은 모든 축을 가상 축으로 설정**한다(UserDef = 0).
- 실기 플랫폼과 함께 쓸 때 모든 축이 가상 축이 되는 것을 막으려면:
  - `Module.ini`에서 **SimuPlatform을 실기 플랫폼 뒤에 정의**하거나,
  - SimuPlatform이 앞에 오는 경우 `UserDef`로 원하는 축만 가상 축으로 지정한다.
- 복수 인터럽트 구성에서는 앞 인터럽트의 시뮬레이터 플랫폼이 먼저 축을 설정하므로 UserDef 설정 필요.

### 멀티 마스터 데이터 간섭 주의 (출처: `kr/guide/simu/precautions.html`)

SimuApi의 `SetIn***`(Bit/Byte/Bytes/Bits) 함수는 원래 읽기 전용인 I/O Input 주소에 쓰기를 가능하게 한다.
Simulation + EtherCAT 같은 멀티 마스터 운용에서 **동일 I/O Input 주소에 두 플랫폼이 쓰면 값에
불확실성(간섭)이 발생**할 수 있다. 혼용 설계 시 입력 주소 공간을 플랫폼별로 분리할 것.

## 4. EtherCAT 플랫폼 구성 요소

출처: `wmx3-user-manual-kr` digest §7 / v3.7 미러 `kr/guide/ec/`.

| 구성 요소 | 내용 | 미러 토픽 |
|-----------|------|-----------|
| EcPlatform 활성화 | `Module.ini` [Platform x] 설정 (§3 예 참조) | `ec_use.html` |
| 필수 개체 | EtherCAT 마스터 필수 오브젝트 | `objects.html` |
| 네트워크 정의 | `ec_network.def` (AL 상태·사이클 모드·DC·핫커넥트·사용자 정의 등 하위 토픽) | `ec_def*.html` |
| ENI 파일 | EtherCAT Network Information (슬레이브 구성) | `ec_eni*.html` |
| 지원 NIC | EtherCAT용 호환 NIC 목록 — 설계 초기에 반드시 확인 | `supported_nic.html`, 3.6u3 digest §2 지원 사양 |
| 로그·오류 | 데이터 로그·메모리 로그·라이브러리/콘솔 오류 코드 | `log*.html`, `ec_errcode_*.html` |

ENI 생성·편집은 EcConfigurator/NetConfigurator 등 별도 GUI 도구 영역이다
(각각 `ecconfigurator-kr`/`netconfigurator-kr` 다이제스트가 등록된 환경이면 그쪽을 참조).
EtherCAT 선택 시 ENI/DEF(`ec_network.def`) 제작은 `wmx3-app-eni` 스킬(wmx3app-eni-builder 에이전트)로 위임한다.

## 5. 하이브리드 구성

- 여러 플랫폼 모듈을 동시에 로드하면 동일 시스템에서 하이브리드 통신 프로토콜을 구현할 수 있다
  (출처: v3.7 미러 `kr/guide/general/architecture_overview.html`).
- v3.7은 **EC-M4·EC-TSN 하이브리드**를 공식 플랫폼 구성으로 신설했다
  (출처: `wmx37-user-manual-kr` digest 개요 — "EC-M4·EC-TSN 하이브리드(신규)").
- 설계 시 결정 사항: 플랫폼별 축/슬레이브 분담, `Module.ini` 정의 순서(=인터럽트 할당 순서),
  입력 주소 공간 분리(§3 멀티 마스터 주의).
- 보간/동기/E-CAM/데이터 로그 그룹 축은 **동일 인터럽트에 배치**한다
  (위반 시 InterruptMismatch — wmx3-app-implement `references/cpp-implementation.md` §8).

## 6. 설계 문서에 기록할 플랫폼 결정 사항

- [ ] 선택 플랫폼과 근거 (플로차트 경로)
- [ ] `Module.ini` [Platform x] 구성 초안 (정의 순서 포함)
- [ ] 네트워크 정의 파일 (`ec_network.def` / `simu_network.def`) 준비 계획
- [ ] EtherCAT이면: ENI 준비 방법, 지원 NIC 확인 결과
- [ ] 개발/테스트 단계의 시뮬레이터 활용 계획 (별도 구성 or 혼용)
- [ ] 혼용 시: 축 배치(UserDef)·입력 주소 분리 방안

## 출처 요약

- `wmx37-user-manual-kr` digest: 개요(플랫폼 5종·3.7 신설), 섹션별 요약 "플랫폼", 헤더(M4/TSN은 정본 CHM 전용)
- `wmx3-user-manual-kr` digest: §2 지원 사양(NIC), §6 시뮬레이터 플랫폼, §7 EtherCAT 플랫폼
- v3.7 미러: `kr/guide/ec/ec_use.html`(EcPlatform 활성화·Module.ini 예),
  `kr/guide/simu/use.html`(SimuPlatform 유효화·가상 축·정의 순서),
  `kr/guide/simu/precautions.html`(멀티 마스터 간섭),
  `kr/guide/general/architecture_overview.html`(플랫폼 교체·하이브리드)
