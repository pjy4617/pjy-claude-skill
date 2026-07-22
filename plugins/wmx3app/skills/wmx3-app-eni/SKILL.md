---
name: wmx3-app-eni
description: "WMX3 EtherCAT ENI 파일 제작·편집·검토. WMX3 전용 ENI(표준 ETG2100 비호환·슬레이브별 분할)와 ec_network.def 연계 설정, 슬레이브 ESI(ETG.2000) 분석, PDO/CANopen 매핑, EcConfigurator/NetConfigurator 생성 워크플로를 다룬다. 'ENI 파일 만들어', 'ENI 생성', 'ENI 제작', 'EtherCAT 네트워크 구성', 'ec_network.def 설정', '슬레이브 ENI', 'ESI 분석', 'ESI로 ENI', 'ENI 검토' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Agent
---

# WMX3 EtherCAT ENI 파일 제작

> 이 스킬은 WMX3 EtherCAT 플랫폼(EcPlatform)용 **ENI 파일**의 제작·편집·검토를 담당합니다.
> WMX3의 ENI는 **표준 ETG2100 ENI와 호환되지 않습니다** — 전체 네트워크 설정은 `ec_network.def`로
> 분리되고, ENI 파일은 **슬레이브별로 분할**되어 해당 슬레이브의 데이터그램과 WMX3 내부 메모리
> 공간(WMX3-I/O 공간·WMX3-CANopen 공간)의 연결만 기술합니다 (근거: ecconfigurator-kr 개요·§4.1).
> 실제 작업(ESI XML·다이제스트 대량 파싱, ENI 생성/검토)은 **wmx3app-eni-builder 에이전트**에게
> 위임하여 격리된 컨텍스트에서 수행합니다.

**wmx3md 플러그인과의 구분**: wmx3md는 WMX3 엔진에 로드되는 **내부 모듈(rtdll) 개발**용,
이 플러그인(wmx3app)은 WMX3 API를 호출하는 **응용 프로그램 개발**용입니다.
**wmx3-app-design과의 관계**: 설계 절차 2단계(플랫폼 선택)에서 EtherCAT을 선택한 경우의
네트워크 구성 후속 작업을 이 스킬이 담당합니다.

## 입력 수집 체크리스트

다음이 부족하면 질문으로 수집합니다.

| # | 항목 | 확인 내용 |
|---|------|----------|
| 1 | 슬레이브 구성 | 벤더/제품/리비전/수량, 서보·I/O·모듈형(Slot Type) 장치 구분 |
| 2 | ESI 파일 | 제조사 제공 ESI(`.xml`) 보유 여부와 경로 (ETG.2000 기반, 기본 배치 `<InstallDir>\ESI\`) — 보유 시 에이전트가 분석해 ENI 계획 근거로 사용 |
| 3 | 실기 연결 | 실 네트워크 연결·스캔 가능(온라인) vs HW 없음(오프라인, ESI 기반) |
| 4 | 주소 고정 | 축 번호·I/O 주소 고정(UserDef) 필요성 (토폴로지 변경에 대한 앱 영향 최소화) |
| 5 | 기존 자산 | 기존 ENI 파일·`ec_network.def` 존재 여부와 경로 |
| 6 | 동기 모드 | 슬레이브별 DC(Distributed Clock)/FreeRun 요구 (서보는 통상 DC) |
| 7 | 대상 작업 | 신규 생성 / 기존 편집 / 검토 중 무엇인가 |

## 절차 (5단계)

1. **입력 수집** — 위 체크리스트로 슬레이브 구성·ESI·연결 환경·작업 종류를 확정한다.
2. **경로 결정** — 원칙: **GUI 도구 생성 권장**(온라인이면 EcConfigurator 스캔→MakeENIs,
   오프라인이면 NetConfigurator/EcConfigurator Offline Mode + ESI),
   텍스트 직접 작업은 기존 ENI **편집·검토**(매핑 오프셋 조정, 파일명/우선순위 정리)에 한정한다.
3. **wmx3app-eni-builder 위임** — 에이전트에게 전달할 정보:
   - 수집된 슬레이브 구성 표(벤더/제품/리비전/수량/장치 유형)
   - 보유 ESI 파일 경로(있으면 — 에이전트가 Read/Grep으로 분석해 ENI 계획 근거로 사용),
     기존 ENI·`ec_network.def` 경로(있으면)
   - 온라인/오프라인 여부, UserDef(축·I/O 주소 고정) 요구
   - 슬레이브별 동기 모드(DC/FreeRun) 요구
   - 대상 작업(신규 생성/편집/검토)과 산출물 출력 경로
4. **산출물 확인** — 신규 생성(도구 안내) 경로면 도구 절차 안내와 생성 후 검토 계획(검증
   체크리스트로 확인할 항목)을, 기존 편집·검토 경로면 생성/수정된 ENI 파일·`ec_network.def`
   변경점·검증 체크리스트 결과(심각도 CRITICAL/MAJOR/MINOR/INFO)를, 공통으로 실기 적용 절차와
   미확인 항목을 확인한다. ESI 분석을 수행한 경우 ESI 분석 표도 산출물에 포함된다.
5. **적용 안내** — ENI/DEF는 `StartCommunication`(WMX3Api) 실행 시 로드된다.
   통신 시작 후 **모든 슬레이브 AL State가 OP**인지 확인한다
   (EcConfigurator 노드 색상 검은색=OP / NetConfigurator AL Status).

## 경로 결정 기준 (2단계 판단 표)

| 상황 | 권장 경로 |
|------|----------|
| 신규 생성 + 실기 연결 가능 | EcConfigurator 온라인 스캔 → MakeENIs 일괄 생성 (빠른 시작 Step1~5) |
| 신규 생성 + HW 없음 | NetConfigurator Offline Mode 또는 EcConfigurator Offline 슬레이브 + ESI |
| 기존 ENI 편집·검토 | 텍스트 직접 작업 — ENI·`ec_network.def`·ESI는 텍스트/XML이므로 Read/Grep으로 파싱 |
| 축·I/O 주소 고정 필요 | `ec_network.def` UserDef + 전용 ENI(`EniFile=`) — 에이전트가 설정 |

새 ENI를 백지에서 손으로 쓰는 것은 권장하지 않습니다 — **도구 생성 후 검토·수정**이 기본입니다.

## references 문서

| 파일 | 내용 |
|------|------|
| `references/eni-file-guide.md` | WMX3 ENI 개념(비호환·분할·역할 3가지)·파일 3종과 경로·파일명 4형식과 참조 우선순위·섹션 구조·매핑 포맷·WMX3 지원 CANopen 객체 표·ec_network.def 연계(UserDef/Reserve)·ESI 파일 분석·도구 워크플로 2종·검증 체크리스트·v3.7 EoE |

## 매뉴얼 다이제스트 연동

manual-digest로 등록된 `ecconfigurator-kr`·`netconfigurator-kr` 다이제스트가 있으면 1차 참조하고
(`~/.claude/manuals/ecconfigurator-kr/digest.md`, `~/.claude/manuals/netconfigurator-kr/digest.md`,
project 스코프는 `.claude/manuals/`), 디테일은 다이제스트의 키워드 인덱스로 원본을 핀포인트합니다.
EtherCAT 플랫폼 일반(EcPlatform 활성화·`ec_network.def` 하위 토픽·지원 NIC)은
`wmx37-user-manual-kr` 다이제스트를 함께 참조합니다(`~/.claude/manuals/wmx37-user-manual-kr/digest.md`).
다이제스트가 없는 환경이면 이 스킬의 `references/eni-file-guide.md`만으로 진행하고,
`/manual-digest`로 EcConfigurator/NetConfigurator 매뉴얼 등록을 제안합니다.
답변/산출물에는 출처(§/p./토픽)를 명시합니다.
