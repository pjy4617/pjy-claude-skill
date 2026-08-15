---
name: wmx3-app-setup
description: "WMX3.7 애플리케이션 개발 스킬 환경 초기 설정. 에이전트 5명과 CLAUDE.md를 프로젝트에 설치합니다. 플러그인 설치 후 최초 1회 실행 필요. 'wmx3app 설정', 'wmx3 앱 셋업', 'wmx3app 에이전트 설치', 'wmx3app setup' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob
---

# WMX3 애플리케이션 개발 스킬 환경 초기 설정

이 스킬은 WMX3.7 애플리케이션 개발 플러그인(wmx3app)의 에이전트와 CLAUDE.md를 현재 프로젝트에 설치합니다.

> **wmx3md 플러그인과의 구분**: wmx3md는 WMX3 엔진에 로드되는 **내부 모듈(rtdll) 개발**용,
> wmx3app은 WMX3 API를 호출하는 **응용 프로그램(장비 제어 SW) 개발**용입니다.
> 두 플러그인은 에이전트 접두어(`wmx3-*` vs `wmx3app-*`)가 달라 같은 프로젝트에 공존할 수 있습니다.

## 실행 절차

### 1단계: 플러그인 디렉토리 확인

`${CLAUDE_SKILL_DIR}` 기준으로 상위 디렉토리에서 `agents/`와 `claude-md/` 폴더를 찾습니다.

```
PLUGIN_DIR = ${CLAUDE_SKILL_DIR}/../../
```

### 2단계: 프로젝트 경로 확인

설치를 진행하기 전에 사용자에게 프로젝트 경로를 질문합니다:

> WMX3 애플리케이션 프로젝트를 설치할 경로를 알려주세요.
> (엔터만 누르면 현재 디렉토리에 설치합니다)

- 사용자가 경로를 입력하면: 해당 경로를 `PROJECT_ROOT`로 설정
- 사용자가 입력하지 않으면 (빈 값): 현재 작업 디렉토리를 `PROJECT_ROOT`로 설정
- `PROJECT_ROOT`가 존재하지 않으면 생성 여부를 사용자에게 확인 후 생성

이후 모든 단계는 `PROJECT_ROOT` 기준으로 실행합니다.

### 3단계: 에이전트 설치

`PROJECT_ROOT/.claude/agents/` 디렉토리에 5개 에이전트를 복사합니다.

```bash
mkdir -p ${PROJECT_ROOT}/.claude/agents
```

복사 대상 (PLUGIN_DIR/agents/ 아래):
- `wmx3app-architect.md` — WMX3.7 시스템 설계 전문가 (플랫폼 선택·축 구성·기능 매핑·성능/안정성 전략)
- `wmx3app-implementer.md` — C++/C# 구현 전문가 (초기화/종료 시퀀스·모션·에러 처리·v3.7 마이그레이션)
- `wmx3app-test-engineer.md` — 시뮬레이터 기반 테스트 전문가 (SimuPlatform·gtest/xUnit 픽스처·시나리오)
- `wmx3app-usage-reviewer.md` — WMX3 사용 검토 전문가 (읽기 전용, 체크리스트 7카테고리·심각도 4등급)
- `wmx3app-eni-builder.md` — EtherCAT ENI 파일 제작 전문가 (WMX3 전용 ENI·ec_network.def 연계·PDO/CANopen 매핑 검증)

각 파일을 읽어서 `${PROJECT_ROOT}/.claude/agents/`에 동일한 이름으로 작성합니다.
이미 존재하는 파일은 덮어쓰기 전에 사용자에게 확인합니다.

### 4단계: CLAUDE.md 병합

`PLUGIN_DIR/claude-md/CLAUDE.md`의 내용을 읽어서 `${PROJECT_ROOT}/.claude/CLAUDE.md`에 추가합니다.

- `${PROJECT_ROOT}/.claude/CLAUDE.md`가 없으면 새로 생성합니다.
- 이미 존재하면, `## WMX3 Application Development` 섹션이 있는지 확인합니다.
  - 있으면: "이미 설치되어 있습니다" 안내
  - 없으면: 파일 끝에 추가

### 5단계: 설치 결과 보고

```
WMX3 애플리케이션 개발 스킬 환경 설치 완료!

에이전트 (5명):
  ✅ wmx3app-architect       — WMX3.7 시스템 설계 (플랫폼 선택·축 구성·기능 매핑)
  ✅ wmx3app-implementer     — C++/C# 구현 (초기화 시퀀스·모션·에러 처리·v3.7 마이그레이션)
  ✅ wmx3app-test-engineer   — 시뮬레이터 기반 테스트 (SimuPlatform·gtest/xUnit)
  ✅ wmx3app-usage-reviewer  — WMX3 사용 검토 (읽기 전용, 7카테고리 체크리스트)
  ✅ wmx3app-eni-builder     — EtherCAT ENI 파일 제작 (WMX3 전용 ENI·ec_network.def·PDO/CANopen 매핑)

스킬 (7개): 플러그인으로 이미 활성화됨
  wmx3-app-setup            — 환경 초기 설정 (현재 스킬)
  wmx3-app-design           — 요구사항 → WMX3 시스템 설계
  wmx3-app-implement        — C++/C# 구현
  wmx3-app-test             — 시뮬레이터 플랫폼 기반 테스트
  wmx3-app-review           — 기존 프로젝트 WMX3 사용 검토
  wmx3-app-eni              — EtherCAT ENI 파일 제작
  wmx3-app-config-xml-analy — Config Export(파라미터 export XML) 분석

CLAUDE.md: ✅ WMX3 애플리케이션 개발 설정 추가됨

권장 사항:
  manual-digest 플러그인으로 WMX3.7 매뉴얼(wmx37-user-manual-kr)을 등록하면
  설계·구현·리뷰 시 다이제스트를 1차 근거로 활용합니다. (없어도 동작합니다)
  다관절 로봇(Robot Option)을 사용하는 프로젝트면 로봇 매뉴얼(wmx3-robot-help-kr)
  다이제스트도 함께 등록을 권장합니다.
  EtherCAT ENI 제작을 다루는 프로젝트면 ecconfigurator-kr·netconfigurator-kr
  다이제스트도 함께 등록을 권장합니다.

시작하기:
  "3축 갠트리 스테이지 WMX3 시스템 설계해줘" 로 시작하세요.
  사용 가이드: 플러그인 docs/USAGE_GUIDE.md
```

## 매뉴얼 다이제스트 연동

manual-digest로 등록된 `wmx37-user-manual-kr`(및 `wmx3-user-manual-kr`) 다이제스트가 있으면 1차 참조하고
(`~/.claude/manuals/wmx37-user-manual-kr/digest.md`, project 스코프는 `.claude/manuals/`),
디테일은 다이제스트의 키워드 인덱스로 원본을 핀포인트합니다.
다관절 로봇 제어를 다루면 `wmx3-robot-help-kr`(Robot Option — 기구학·Joint/Cartesian 좌표계·
PTP/CP·XML/URDF 로봇 정의·충돌 감지) 다이제스트도 함께 1차 참조합니다
(`~/.claude/manuals/wmx3-robot-help-kr/digest.md`).
EtherCAT ENI 파일 제작을 다루면 `ecconfigurator-kr`(EcConfigurator — ENI 구조·ec_network.def·
CANopen 객체표)·`netconfigurator-kr`(NetConfigurator — ESI 기반 ENI 생성 워크플로) 다이제스트도
함께 1차 참조하며, 등록을 권장합니다
(`~/.claude/manuals/ecconfigurator-kr/digest.md`, `~/.claude/manuals/netconfigurator-kr/digest.md`).
다이제스트가 없는 환경이면 각 스킬의 `references/` 문서만으로 진행하고,
`/manual-digest`로 WMX3.7 매뉴얼 등록을 제안합니다.
답변/산출물에는 출처(§/토픽)를 명시합니다.
