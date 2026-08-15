# WMX3 애플리케이션 개발 플러그인 사용 가이드 (v1.3.0)

## 개요

WMX3.7 라이브러리를 **사용하는 애플리케이션**(장비 제어 SW)의 풀스택 개발 플러그인입니다.
요구사항 → 시스템 설계(플랫폼 선택·축 구성·기능 매핑·성능/안정성 전략) → C++/C# 구현 →
시뮬레이터 플랫폼 기반 테스트 → 기존 프로젝트 WMX3 사용 검토까지의 전체 흐름을 지원합니다.

> **wmx3md 플러그인과의 구분**: `wmx3md`는 WMX3 엔진에 로드되는 **내부 모듈(rtdll) 개발**용,
> `wmx3app`은 WMX3 API를 호출하는 **응용 프로그램 개발**용입니다.

## 설치

```bash
# 1. 마켓플레이스 추가 (한 번만)
/plugin marketplace add pjy4617/pjy-claude-skill

# 2. wmx3app 플러그인 설치
/plugin install wmx3app@pjy-skills

# 3. 에이전트 + CLAUDE.md 설치 (최초 1회)
/wmx3-app-setup
```

셋업 시 프로젝트 경로를 질문합니다:

```
> WMX3 애플리케이션 프로젝트를 설치할 경로를 알려주세요.
> (엔터만 누르면 현재 디렉토리에 설치합니다)
```

지정한 경로의 `.claude/agents/`에 에이전트 5명이 복사되고, `.claude/CLAUDE.md`에
`## WMX3 Application Development` 섹션이 병합됩니다(이미 있으면 "이미 설치" 안내).

## 스킬 목록 (7개)

| 스킬 | 호출 예시 | 설명 |
|------|-----------|------|
| `wmx3-app-setup` | "wmx3app 설정" | 에이전트 5명 + CLAUDE.md 설치 (최초 1회) |
| `wmx3-app-design` | "WMX 시스템 설계해줘" | 요구사항 → 플랫폼 선택·축 구성·기능 매핑·성능/안정성 전략 → 설계 문서 |
| `wmx3-app-implement` | "WMX C++ 구현해줘" | 초기화/종료 골격·모션·이벤트·에러 처리·3.6u3→3.7 마이그레이션 |
| `wmx3-app-test` | "시뮬레이터 테스트해줘" | SimuPlatform 구성·gtest/xUnit 픽스처·시나리오 테스트·실기 전 체크 |
| `wmx3-app-review` | "WMX 사용 검토해줘" | 기존 프로젝트 WMX3 사용 검토 (7카테고리 체크리스트, 심각도 4등급) |
| `wmx3-app-eni` | "ENI 파일 만들어줘" | WMX3 전용 EtherCAT ENI 파일 제작·편집·검토 (슬레이브 ESI 분석·ec_network.def 연계·PDO/CANopen 매핑) |
| `wmx3-app-config-xml-analy` | "wmx_parameters.xml 분석해줘" | WMX3 Config Export(파라미터 export XML) 분석 — 128축 중 설정 축 식별·기어비/토크/소프트리밋/원점 요약·안전 일관성 검토(심각도 4등급). 동봉 파서(`parse_wmx_config.py`)로 텍스트·CSV·JSON 산출 |

## 에이전트 목록 (5명)

| 에이전트 | 역할 |
|----------|------|
| `wmx3app-architect` | WMX3.7 시스템 설계 (요구사항 인터뷰·플랫폼 결정·축/좌표 설계·기능 매핑·성능/안정성 전략·설계 문서) |
| `wmx3app-implementer` | C++/C# 구현 (초기화/종료 골격·언어별 패턴·에러 처리 일관화·v3.7 마이그레이션·빌드) |
| `wmx3app-test-engineer` | 시뮬레이터 기반 테스트 (SimuPlatform 구성·gtest/xUnit 픽스처·시나리오 설계·판정·리포트) |
| `wmx3app-usage-reviewer` | WMX3 사용 검토 (체크리스트 7카테고리·CRITICAL/MAJOR/MINOR/INFO·파일:라인 근거·읽기 전용) |
| `wmx3app-eni-builder` | EtherCAT ENI 파일 제작 (WMX3 전용 ENI·ec_network.def 연계·PDO/CANopen 매핑·검증 체크리스트) |

## 빠른 시작 — 설계→구현→테스트→검토 파이프라인

### 1. 시스템 설계

```
"3축 갠트리 장비를 EtherCAT으로 제어하는 WMX 시스템 설계해줘"
```

`wmx3app-architect`가 요구사항(축 수·장비 유형·사이클타임·I/O 점수·정밀도·안전 요구)을
인터뷰로 보충한 뒤 플랫폼 선택(EtherCAT/시뮬레이터/M4/TSN/하이브리드), 축 구성(기어비·
사용자 단위·원점 전략), 요구 동작→WMX3 기능 매핑, 초기화/운전/종료 시퀀스를 담은
설계 문서(마크다운)를 산출합니다.

### 2. 구현

```
"설계 문서 기반으로 C++로 구현해줘"   또는   "C#으로 WMX3 코드 작성해줘"
```

`wmx3app-implementer`가 초기화/종료 골격(`CreateDevice` → `StartCommunication` →
`SetServoOn`, 종료 역순, .NET은 `CloseDevice` 후 `Dispose` 필수)부터 모션·I/O·이벤트·
ApiBuffer 구현, 에러 처리 일관화까지 수행합니다. 기존 3.6u3 코드 이식이면
`references/v37-migration.md`(호환성 깨짐 8항목)를 적용합니다.

### 3. 테스트

```
"시뮬레이터로 원점복귀랑 보간 궤적 테스트해줘"
```

`wmx3app-test-engineer`가 SimuPlatform(`simu_network.def`)을 구성해 실 하드웨어 없이
모션을 검증하고, gtest(C++)/xUnit·NUnit(C#) 픽스처로 시나리오 테스트(원점복귀·프로파일·
보간 궤적·이벤트·에러 주입)를 작성·판정합니다. 실기(EtherCAT) 전환 전 체크리스트도 제공합니다.

### 4. 사용 검토

```
"이 프로젝트 WMX3 사용법 점검해줘"   또는   "wmx 마이그레이션 검토해줘"
```

`wmx3app-usage-reviewer`가 프로젝트를 스캔해 생명주기/리소스, 시퀀스 정합성, 에러 처리,
성능/실시간성, 안정성/안전, v3.7 마이그레이션, 코드 품질의 7카테고리를 검토하고
심각도(CRITICAL/MAJOR/MINOR/INFO)와 파일:라인 근거를 붙인 리포트를 만듭니다.
코드는 수정하지 않는 읽기 전용 검토입니다.

## 단독 사용 예

각 스킬은 파이프라인 없이 단독으로도 사용할 수 있습니다:

```
"EtherCAT이랑 시뮬레이터 중 어떤 플랫폼 써야 해?"        → wmx3-app-design
"6축 로봇 PTP/CP 이송 시스템 설계해줘"                    → wmx3-app-design (Robot Option)
"3.6u3 프로젝트를 3.7로 마이그레이션해줘"                 → wmx3-app-implement
"CI에서 돌릴 시뮬레이터 테스트 픽스처 만들어줘"           → wmx3-app-test
"에러 처리 누락만 빠르게 점검해줘"                        → wmx3-app-review
"서보 4축 + IO 2대 구성 ENI 파일 만들어줘"                → wmx3-app-eni
"보유 ESI 파일 분석해서 ENI 계획 세워줘"                  → wmx3-app-eni (ESI 분석)
```

## manual-digest 연동 (권장)

이 플러그인의 스킬/에이전트는 manual-digest로 등록된 WMX3.7 매뉴얼 다이제스트
(`wmx37-user-manual-kr`, 보조로 `wmx3-user-manual-kr`)가 있으면 이를 1차 근거로 사용하고,
디테일은 다이제스트의 키워드 인덱스로 원본 매뉴얼을 핀포인트합니다. 다관절 로봇 제어를 다루면
`wmx3-robot-help-kr`(Robot Option — 기구학·Joint/Cartesian 좌표계·PTP/CP·XML/URDF 로봇 정의·
충돌 감지) 다이제스트도 함께 1차 참조합니다(`~/.claude/manuals/wmx3-robot-help-kr/digest.md`).
EtherCAT ENI 파일 제작을 다루면 `ecconfigurator-kr`(EcConfigurator — ENI 구조·ec_network.def·
CANopen 객체표)·`netconfigurator-kr`(NetConfigurator — ESI 기반 ENI 생성 워크플로) 다이제스트를
1차 참조합니다(`~/.claude/manuals/ecconfigurator-kr/digest.md`, `~/.claude/manuals/netconfigurator-kr/digest.md`).

- 등록 위치: `~/.claude/manuals/` (global) 또는 `.claude/manuals/` (project)
- 등록 방법: `/manual-digest <WMX3.7 매뉴얼 경로>` (manual-digest 플러그인 필요)
- 다이제스트가 없는 환경에서도 각 스킬의 `references/` 문서만으로 동작하지만,
  API 시그니처·오류코드 등 정밀 확인이 필요한 작업에는 **wmx37-user-manual-kr 등록을 권장**합니다
  (로봇 사용 시 `wmx3-robot-help-kr`, ENI 제작 시 `ecconfigurator-kr`·`netconfigurator-kr`도 함께 권장).

## FAQ

**Q. wmx3md 플러그인과 무엇이 다른가요?**
A. wmx3md는 WMX3 엔진에 로드되는 내부 모듈(rtdll)을 만드는 플러그인(C99 Core + C++ API
3계층, RT 안전성 규칙)이고, wmx3app은 그 엔진의 API(`wmx3Api`/`WMX3ApiCLR`)를 호출하는
응용 프로그램을 설계·구현·테스트·검토하는 플러그인입니다. 두 플러그인은 함께 설치해도
에이전트 이름이 충돌하지 않습니다(`wmx3-*` vs `wmx3app-*`).

**Q. 시뮬레이터 플랫폼만으로 어디까지 검증할 수 있나요? 라이선스는요?**
A. SimuPlatform은 실 하드웨어 없이 모션을 검증하는 플랫폼입니다(매뉴얼 §6 시뮬레이터
플랫폼 / `kr/guide/simu/`). 원점복귀·프로파일·보간 등 모션 로직 검증에 적합하며, 실 서보
파라미터·실기 안전 동작은 실기 전환 후 별도 확인이 필요합니다. 시뮬레이터 사용에 관한
라이선스 조건은 매뉴얼 다이제스트에 명시되어 있지 않으므로, 보유한 WMX3 라이선스
구성(배포처 Movensys)에서 확인하세요.

**Q. 실시간(RT) 공간에서 동작하는 애플리케이션도 만들 수 있나요?**
A. 가능합니다 — RTX SDK로 RT 공간 앱을 작성할 수 있으며 `IMDLL_RT.lib`를 링크합니다
(VC++ 한정). 단, **WMX3·RTX 런타임 라이선스와 별도로 IntervalZero RTX SDK 라이선스가
필요**하다고 매뉴얼에 명문화되어 있습니다(지원 사양 §실시간 환경 응용프로그램 개발 지원,
`support-spec/rtx_dev_realtime.html`). 콘솔 출력의 결정성 영향·무한 루프 금지 등
실시간 앱 주의사항도 함께 확인하세요.

**Q. 로봇(다관절) 제어도 되나요?**
A. 됩니다 — WMX3 위에 얹는 **Robot Option** 확장이 필요합니다. `wmx3Api::RobotMotion`
(멤버 `mKinematics`/`mCoordinate`)으로 PTP(`StartPTPPos`)/CP 모션을 실행하고, 로봇 정의는
코드가 아닌 XML + URDF 파일로 관리합니다(좌표계는 Joint/Cartesian/Robot 3종). 충돌 감지를
쓰려면 전제조건 4가지 — ① URDF/XML에 모든 링크 관성 ② 각 조인트 모터의 실시간 전류 피드백
③ `SetToolInfo`로 tool 정보 등록 ④ `RobotMotionParam.robotParam.baseJointCoordinate`의
point/rotation 전부 0 — 를 충족해야 합니다(Robot Help §3 충돌 감지). 로봇 옵션 문서는
`wmx3-robot-help-kr` 다이제스트 기준이 **v3.6u3**이므로, v3.7에서의 차이는 릴리즈 노트로
확인하세요.

**Q. 3.6u3에서 3.7로 올릴 때 무엇이 깨지나요?**
A. ClosedLoop 명명 변경, 토크 커맨드 5클래스 삭제→`TrqCommand` 빌더 통합, 토크 램프 시간
단위 변경(사이클 수→초), `Torque::`/`Velocity::`→`Config::` 이동, ApiBuffer 조건부 동작·
다중조건 API 변경, **오류 코드 값 시프트**(하드코딩 파서 주의) 등 8항목입니다
(릴리즈 노트 `kr/release-notes/index.html`). `wmx3-app-implement`의
`references/v37-migration.md`에 Before/After와 탐지 grep 패턴이 정리되어 있고,
`wmx3-app-review`로 기존 코드의 잔존 구 API를 진단할 수 있습니다.
