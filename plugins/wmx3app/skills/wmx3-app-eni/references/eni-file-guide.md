# WMX3 EtherCAT ENI 파일 가이드

WMX3 EtherCAT 플랫폼(EcPlatform)용 ENI(EtherCAT Network Information) 파일의 구조·명명·매핑·도구
워크플로 참조 문서. 근거는 `ecconfigurator-kr`(EcConfigurator 사용자 설명서, App v61321/WMX3 v3.7)·
`netconfigurator-kr`(NetConfigurator 사용자 매뉴얼, App v61311/WMX3.7) 다이제스트다.
이 문서에 없는 ENI 파일 내부 키 이름·상세 문법은 **추측하지 말고** 도구가 생성한 ENI 원문 또는
WMX3UserManual EtherCAT 섹션(v3.7 미러 `kr/guide/ec/`)에서 확인한다.

## 1. WMX3 ENI 개념 (출처: ecconfigurator-kr 개요·§4.1 p.24-25)

- WMX3-EtherCAT의 ENI는 **표준 ETG2100 기반 ENI와 호환되지 않는다**. 전체 네트워크 설정은
  `ec_network.def`(마스터스택 동작 파라미터)로 분리되고, **ENI 파일은 슬레이브별로 분할**되어
  해당 슬레이브의 데이터그램과 WMX3 내부 메모리 공간(WMX3-I/O 공간, WMX3-CANopen 공간)의
  연결만 기술한다. 타 마스터용 표준 ENI를 그대로 가져와 쓸 수 없다.
- **ENI가 하는 일 3가지**: ① Init→OP 전환 파라미터 정의 ② WMX3-I/O 공간↔PDO 연결
  ③ WMX3-CANopen 공간↔PDO 연결.
- **I/O 장치**는 모든 PDO 항목이 WMX3-I/O 공간에 매핑되고, **서보 장치**는 지원 CANopen 객체가
  WMX3-CANopen 공간에 매핑된다(+ 서보의 Digital I/O는 동시에 I/O 공간에도).
- WMX3 I/O 공간은 입력/출력 각 **8000byte**. EtherCAT 데이터그램 = 헤더 10byte +
  데이터 최대 1486byte + WKC(작업 카운터) 2byte.
- **적용 시기**: `StartCommunication`(WMX3Api 클래스) 실행 = 통신 시작 초기에 ENI+DEF 로드.

## 2. 파일 3종과 경로 (출처: ecconfigurator-kr §2 p.5, §4.1 p.25)

| 파일 | 위치 | 내용 |
|------|------|------|
| **ENI** | `C:\eni\`(기본) 또는 DEF 지정 위치(`EniFolder`) | 슬레이브별 통신 설정(전환 파라미터·PDO 매핑) |
| **DEF** | `<InstallDir>\Platform\EtherCAT\ec_network.def` | 마스터스택 동작 파라미터(전체 네트워크 설정) |
| **ESI** | `<InstallDir>\ESI\` | ETG2000 기반 슬레이브 정보(`.xml`), 제조사에서 입수 |

`<InstallDir>` 기본값은 `C:\Program Files\SoftServo\WMX3`.

## 3. ENI 파일명 4형식과 참조 우선순위 (출처: ecconfigurator-kr §4.1 p.25-26, netconfigurator-kr §3.1.4.1 p.15·§5.2.2 p.62)

파일명의 리비전/시리얼/제품코드/별칭은 **4byte 16진수** 표기(예: V+P 형식 `00000000_00000000.txt`).

참조 우선순위 (높음 → 낮음):

| 순위 | 형식 | 비고 |
|------|------|------|
| 1 | 전용 ENI — `ec_network.def [Slave N]`의 `EniFile=` 절대경로 | **UserDef 유효 시에만** 적용 |
| 2-1 | `벤더ID_제품코드_리비전_일련번호.txt` | 공유 ENI 폴더(`[Master x]` `EniFolder` 또는 기본 `C:\eni`)에서 검색 |
| 2-2 | `벤더ID_제품코드_리비전.txt` | |
| 2-3 | `벤더ID_제품코드_Alias_XX.txt` | |
| 2-4 | `벤더ID_제품코드.txt` | 기본값. 동일 벤더/제품 복수 슬레이브가 중복 참조 가능 |

NetConfigurator의 "ENI File 제품 적용 범위"도 동일 서열: V+P+Revision+Serial > V+P+Revision >
V+P+Alias > V+P (우선순위 4>3>2>1).

## 4. ENI 섹션 구조 (출처: ecconfigurator-kr §4.1 p.25)

| 섹션 | 시점 | 내용 |
|------|------|------|
| `[init2preop]` | Init→PreOP 전 ESC 레지스터 쓰기 | SM/FMMU 설정, ESC Reg0108(R/W 주소 오프셋)·Reg0400(Watchdog Divider)·Reg0410(Watchdog Time PDI)·Reg0420(Watchdog Time Process Data) |
| `[preop2safeop]` | PreOP→SafeOP 전 SdoDownload | PDO/PDO Entry 구성, 모듈러 장치 0xF030, InitCmd |

워치독 Reg0410/0420 기본값은 100ms (Reg0410 기본값 1000 = 100us×1000, 출처: ecconfigurator-kr §3.2 p.16).
타임아웃 시 ESC DL Status bit1=0 → 앰프 알람으로 이어질 수 있으므로 임의 변경하지 않는다.

## 5. 매핑 포맷 (출처: ecconfigurator-kr §4.1 p.24)

- **CANopen 매핑**: `[변수명]: [axis], [offset], [size]`
  예 `TargetPosition: 0, 5, 4` — 프레임 offset 5byte의 4byte를 축 0의 TargetPosition에 할당.
- **I/O 매핑**: `[정의명령]: [offset], [size]`
  예 `IoInput: 0, 10`.
- 위 표기는 다이제스트의 예시형 기준이다 — **실제 구분자·공백 등 정확한 문법은 도구(EcConfigurator/NetConfigurator)가 생성한 ENI 원문을 기준으로 확인**한다.

통신 방향 정의(출처: ecconfigurator-kr §2 p.6): I/O Input = 슬레이브→마스터(TxPDO 방향),
I/O 출력 = 마스터→슬레이브(RxPDO 방향). **주의**: WMX3의 Ecat 클래스 API(TxPdoWrite 등)에서는
Tx/Rx 정의가 반대(마스터→슬레이브가 TxPDO)다.

## 6. WMX3 지원 CANopen 객체 (실시간 제어 대상, 출처: ecconfigurator-kr §4.2 p.29-31)

| 방향 | 객체 (인덱스) |
|------|--------------|
| **Rx** (마스터→슬레이브) | ControlWord 0x6040, ModesOfOperation 0x6060, TargetPosition 0x607A, TargetVelocity 0x60FF, TargetTorque 0x6071, TouchProbeFunction 0x60B8, VelocityOffset 0x60B1, MaxTorque 0x6072, Positive/NegativeTorqueLimit 0x60E0/0x60E1, MaxMotorSpeed 0x6080, ProfileVelocity/Accel/Decel 0x6081/0x6083/0x6084, TorqueOffset 0x60B2, DigitalOutput 0x60FE, HomingMethod 0x6098, SpeedDuringSearchForSwitch/Zero 0x6099:01/02, HomingAcceleration 0x609A |
| **Tx** (슬레이브→마스터) | StatusWord 0x6041, ModesOfOperationDisplay 0x6061, ErrorCode 0x603F, PositionActualValue 0x6064, VelocityActualValue 0x606C, TorqueActualValue 0x6077, FollowingError 0x60F4, TouchProbeStatus 0x60B9, TouchProbePosition 0x60BA~0x60BD, DigitalInput 0x60FD |

- MaxProfileVelocity 0x607F·TouchProbePosition2는 ENI가 지원하나 연결 파라미터가 없어
  PDOMapping에서 제외된다.
- WMX Api 변수는 장치 PDO가 해당 값을 지원하고 **ENI에 매핑되어야** 갱신된다
  (예: TxPDO에 Actual Velocity가 없으면 Api Velocity 미갱신 — netconfigurator-kr §4.2 p.33, §5.2.2 p.64-65).

## 7. CANopen 인덱스 영역 (출처: ecconfigurator-kr §4.2 p.28)

- 0x1600-0x17FF **RxPDO Mapping** / 0x1A00-0x1BFF **TxPDO Mapping** /
  0x1C12 **RxPDO Assignment** / 0x1C13 **TxPDO Assignment**.
- PDO Mapping 항목 값(4Byte) = `[객체 인덱스 2Byte][서브인덱스 1Byte][Bit size 1Byte]`.
- 그 외 영역: 0x2000-0x5FFF 벤더 고유, 0x6000-0x6FFF 입력 프로세스 데이터,
  0x7000-0x7FFF 출력 프로세스 데이터, 0xF000-0xFFFF 장치(모듈러 0xF030 포함).

## 8. ec_network.def 연계 (출처: ecconfigurator-kr §5 p.43-46, netconfigurator-kr §5.1.3 p.54-57)

- **EniFolder**: 공유 ENI 폴더 지정(`[Master x]`). 미지정 시 기본 `C:\eni`.
- **[Slave N] `EniFile=`**: 슬레이브 전용 ENI 절대경로 — UserDef 유효 시에만 적용(§3의 우선순위 1).
- **UserDef(사용자 정의)**: 슬레이브의 축 번호·I/O 크기·I/O 주소·ENI 파일을 고정 —
  토폴로지 변경에 대한 사용자 프로그램 영향 최소화. 테이블은 **비교 영역**(통신 시작 시
  실 네트워크와 비교하는 장비 정보)과 **정의 영역**(축·I/O Size 매핑)으로 구성되며
  **영역(주소) 겹침 금지**(충돌 시 NetConfigurator가 Red 표시). EcConfigurator의
  "사용자 정의 추출" 버튼으로 온라인 슬레이브 정보를 UserDef 테이블로 복사할 수 있다.
- **Reserve 영역**: I/O 크기에 여유 확보 — 이후 모듈/PDO 추가가 Reserve 이내면 타 슬레이브
  I/O 주소에 영향 없음. Reserve 영역은 객체 미연결이라 I/O API로 R/W해도 제어에 무영향.
- 적용 시기는 ENI와 동일하게 `StartCommunication` 시작 시 로드.

## 9. ESI 파일 분석 (출처: ecconfigurator-kr §2 p.5, netconfigurator-kr §5.2 p.59·§5.2.1 p.60·§4.2.5 p.39-43·§7.7 p.86-88)

ESI(EtherCAT Slave Information)는 **ETG.2000 기반 XML**로 제조사가 제공하며 기본 배치는
`<InstallDir>\ESI\`다(§2 참조 — ecconfigurator-kr §2 p.5). NetConfigurator는 이 ESI를 기반으로
ENI를 생성하고, ESI 파일 뷰어(ESI↔장치 매칭 상태·Revision List·주요 Define 정보 검색 —
netconfigurator-kr §5.2.1 p.60)를 제공한다. ESI는 텍스트(XML)이므로 도구 없이
**Read/Grep으로 직접 분석**할 수 있다.

### 9.1 추출 항목

| 추출 항목 | 용도 |
|-----------|------|
| 벤더 ID·제품 코드·리비전(4byte 16진수) | ENI 파일명 4형식·참조 우선순위 결정, 실기 스캔 결과와 Revision 일치 확인(불일치 시 최신 ESI 권장 — netconfigurator-kr §5.2 p.59) |
| RxPdo/TxPdo 정의와 Entry(Index/SubIndex/BitLen) | PDO 구성 후보 — WMX3 지원 CANopen 객체 표와 대조해 매핑 가능/불가 판정(TxPDO에 Actual Velocity(0x606C) 없으면 Api Velocity 미갱신 경고 — netconfigurator-kr §5.2.2 p.64-65) |
| CoE Object Dictionary(Dictionary 영역 존재 시) | 오프라인 객체 확인·Startup(SdoDownload) 후보(OD 오프라인 로드는 Dictionary 영역 필요 — netconfigurator-kr §4.2.5 p.39-43) |
| DC 지원(OpModes) | 동기 모드(DC/FreeRun) 결정 근거 |
| 모듈형 Slot 정보 | 모듈 구성 필요 여부(Slot Type — netconfigurator-kr §5.2.2 모듈 p.66-67) |

### 9.2 분석 원칙

- 위 요소명(Vendor/Id, Device의 ProductCode/RevisionNo, RxPdo/TxPdo와 Entry(Index/SubIndex/BitLen),
  Sm, Dc, Slots/Module, Profile/Dictionary 등)은 ETG.2000 일반 요소 수준의 안내다 —
  **정확한 스키마 경로는 실제 ESI 파일에서 Grep으로 확인**하고 추측하지 않는다.
- **Revision 일치 원칙**: 장치 리비전과 ESI 리비전 불일치(Revision Mismatch) 시에도 ENI 생성은
  가능하나 동일 Revision 권장, 불일치 시 **최신 ESI 사용 권장**(netconfigurator-kr §5.2 p.59).
- **Dictionary 영역 유무**: ESI에 Object Dictionary(Dictionary) 영역이 있어야 NetConfigurator의
  OD 오프라인 로드(ESI의 Object Data 표시 — netconfigurator-kr §4.2.5 p.39-43)와 Object File
  오프라인 생성(§6.1.1 p.74-76)이 가능하다. 없으면 온라인(장치 Read)으로만 객체를 확인한다.
- **ESI가 없을 때의 대안**: 제조사에서 입수한다. 실기 연결이 가능하면 EcConfigurator 온라인
  스캔으로 장치 확인은 가능하나 ESI 없으면 "Unknown" 표시(ecconfigurator-kr §2.3 p.6).
  Offline Mode 활용(장치 정보 확인·ENI 생성·Object File·UserDef 비교 영역 작성 —
  netconfigurator-kr §7.7 p.86-88)은 ESI Load가 전제다.

## 10. 도구 워크플로 2종

### 10.1 EcConfigurator 빠른 시작 (출처: ecconfigurator-kr §2.3 p.6)

Step1 ESI 파일을 `<InstallDir>\ESI\`에 저장 → Step2 기기 연결 → Step3 앱 실행·네트워크 스캔
(ESI 없으면 "Unknown" 표시) → Step4 마스터 노드+메인 탭의 **MakeENIs** 화면에서 일괄 생성 →
Step5 통신 시작·OP 확인(노드 색상: 녹색 Init / 파란색 PreOP / 보라색 SafeOP / **검은색 OP**).
오프라인 노드(Offline·UserDef)는 통계/파라미터 R/W는 불가하나 **ENI 편집·생성은 가능**
(실기기 조달 전 설정 — §2.2 p.4).

### 10.2 NetConfigurator (출처: netconfigurator-kr §3.1.4 p.15-16, §5.2.2 p.61-72, §7.7 p.86-88, §8.1 p.90-104)

- **ENI Quick Make**: 빠른 생성 → 전체 슬레이브 ESI/ENI 상태 일람 → ENI 모두 만들기 →
  통신 시작(모든 Slave AL State OP면 성공).
- **ENI 편집기 탭 흐름**: 일반 → PDO 구성 → (모듈 구성) → SM → 시작 명령 → (EoE).
  일반 탭에서 파일 적용 범위(§3의 4형식)·Identification ADO·DC/FreeRun·ESC 레지스터/와치독·
  기타 옵션(AllowPdoReadWrite 등, Default 0)을 설정. 시작 명령 그룹 기본값:
  PDO Config = Checked, Module Download·CoE Init = Unchecked.
- **Offline Mode**: 실기 없이 ESI Load로 장치 정보 확인·ENI 생성·Object File 작성·UserDef
  비교 영역 작성 가능.
- **Revision Mismatch**: 장치 리비전과 ESI 리비전 불일치 시에도 ENI 생성은 가능하나
  동일 Revision 권장, 불일치 시 **최신 ESI 사용 권장**.
- 특수 상황: Alias 기반 HotConnect 오동작 시 Identification ADO=None, RTOS에서 PDO 직접
  읽기 필요 시에만 Allow Pdo Read Write 활성화(§8.1.2).

## 11. 검증 체크리스트

wmx3app-eni-builder 에이전트의 검증 항목과 동일하다.

| 항목 | 심각도 | 확인 내용 |
|------|--------|----------|
| 파일명 형식 | CRITICAL | §3의 4형식 중 하나, 리비전/시리얼/제품코드/별칭 4byte 16진수 표기 |
| 서보 필수 객체 매핑 | CRITICAL | 사용하는 제어 모드에 필요한 객체(ControlWord 0x6040/StatusWord 0x6041/TargetPosition 0x607A/PositionActualValue 0x6064 등)가 §6 지원 표 범위에서 매핑되어 있는가 |
| TxPDO Actual Velocity | MAJOR | TxPDO에 VelocityActualValue(0x606C) 누락 시 Api Velocity 미갱신 |
| I/O 공간 초과 | CRITICAL | 입력/출력 각 8000byte 초과 여부 |
| 오프셋 중복/겹침 | CRITICAL | 슬레이브 간 I/O 주소·UserDef 비교/정의 영역 겹침 금지 |
| AllowPdoReadWrite | MAJOR | 불필요하게 1로 활성화 금지 — 안전상 기본 0(중요 PDO 오작동 위험) |
| 워치독 레지스터 | MINOR | Reg0410/0420 기본 100ms에서 변경했다면 근거 확인 |
| 적용 확인 | INFO | `StartCommunication` 후 모든 슬레이브 AL State OP (EcConfigurator 노드 색상/NetConfigurator AL Status로 판정) |

## 12. v3.7 EoE (출처: netconfigurator-kr Release Note p.2-5, §5.2.2 EoE p.71)

- WMX3.7에서 EoE(Ethernet over EtherCAT) 옵션이 ENI·EcNetwork.def에 신규 반영.
- ENI 편집기 EoE 탭(EoE 지원 장치에서 활성): IP/MacAddress/Gateway/Subnet Mask/DNS 설정.
- **전역 EoE Specific Parameters**(Slave ID·Alias 활용)는 WMX3.7 이상 신규.

## 출처 요약

- `ecconfigurator-kr` digest: 개요(ETG2100 비호환·슬레이브별 분할), §2 p.4-6(파일 3종·노드 트리·
  빠른 시작·통신 방향), §3.2 p.16(워치독), §4.1 p.24-26(역할 3가지·8000byte·매핑 포맷·섹션·
  파일명/우선순위), §4.2 p.28-31(인덱스 영역·지원 CANopen 객체), §5 p.43-46(UserDef·Reserve),
  §6.1 p.47(PDO 접근 기본 차단·Mask)
- `netconfigurator-kr` digest: §3.1.4 p.15-16(Quick Make·오프라인 장치), §4.2 p.33(Api 변수↔PDO
  매핑), §4.2.5 p.39-43(OD 오프라인 로드·Dictionary 영역), §5.1.3 p.54-57(UserDef·영역 겹침·Red
  표시), §5.2 p.59(Revision Mismatch), §5.2.1 p.60(ESI 파일 뷰어), §5.2.2
  p.61-72(편집기 탭 흐름·일반/PDO/시작 명령/EoE), §7.7 p.86-88(Offline Mode), §8.1 p.90-104(예제)
