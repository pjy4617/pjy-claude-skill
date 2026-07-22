---
name: wmx3-app-design
description: "WMX3.7 애플리케이션 시스템 설계. 장비 요구사항(축 수·사이클타임·I/O·정밀도·안전)을 분석해 플랫폼 선택(EtherCAT/시뮬레이터/M4/TSN/하이브리드), 축 구성(기어비·사용자 단위·원점 전략), 요구 동작→WMX3 기능 매핑, 성능/안정성 전략, 에러/안전 설계를 담은 설계 문서를 산출한다. 'WMX 시스템 설계', 'WMX3 설계', '모션 시스템 설계', '축 구성 설계', 'WMX 아키텍처', '플랫폼 선택' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Agent
---

# WMX3 애플리케이션 시스템 설계

> 이 스킬은 WMX3.7 라이브러리를 **사용하는 애플리케이션**(장비 제어 SW)의 시스템 설계를 수행합니다.
> 실제 설계 작업은 **wmx3app-architect 에이전트**에게 위임합니다.
> `references/` 5개 문서(아키텍처 코어·플랫폼 선택·기능 매핑·성능/안정성·로봇 옵션)를 참조합니다.

**wmx3md 플러그인과의 구분**: wmx3md는 WMX3 엔진에 로드되는 **내부 모듈(rtdll) 개발**용,
이 플러그인(wmx3app)은 WMX3 API를 호출하는 **응용 프로그램 개발**용입니다.
사용자 rtdll(커스텀 제어 모듈)이 필요하다고 판단되면 wmx3md 플러그인으로 안내하세요.

## 입력

장비/시스템 요구사항. 다음이 부족하면 **요구사항 인터뷰**로 수집합니다.

### 요구사항 인터뷰 체크리스트

| # | 항목 | 확인 내용 |
|---|------|----------|
| 1 | 장비 유형 | 반송/조립/검사/디스펜서/레이저/프레스/갠트리 스테이지 등 |
| 2 | 축 수·종류 | 서보 축 수, 가상 축 필요 여부, 갠트리(동기) 축 쌍 |
| 3 | 네트워크/플랫폼 | EtherCAT 슬레이브 구성 유무, CC-Link IE TSN/M4 장비, 실 HW 없는 개발 단계 여부 |
| 4 | 사이클타임 | 통신 주기 요구, 타이밍 크리티컬 동작(트리거 정밀도) |
| 5 | I/O 점수 | 디지털/아날로그 점수, 고속 응답이 필요한 I/O |
| 6 | 정밀도 | 위치 분해능, 기어비/사용자 단위(mm, deg, pulse), 보정(피치/백래시) 필요성 |
| 7 | 궤적/동기 요구 | 보간(직선/원호/경로), 캠(E-CAM), 마스터-슬레이브 동기, 비전 트리거 |
| 8 | 안전 요구 | 리미트, 토크 제한, Watchdog, 비상 정지 시나리오 |
| 9 | 언어/환경 | C++ / C#(.NET), 기존 코드베이스(3.6u3 이식 여부), RT 앱 필요성 |
| 10 | 운영/진단 | 로그 요구(데이터/API/메모리), 유지보수 시나리오 |
| 11 | 다관절 로봇 | 다관절 로봇 포함 여부(기구 구성·DOF), 티칭/좌표 요구, 충돌 감지 필요성 |

## 설계 절차 (7단계)

1. **요구사항 분석** — 위 체크리스트로 요구를 표로 정리하고, 미확정 항목은 질문으로 확정한다.
2. **플랫폼 선택** — EtherCAT / 시뮬레이터 / M4 / TSN·CC-Link / 하이브리드 5종 중 선택.
   `references/platform-selection.md`의 비교 표·선택 플로차트를 따른다.
3. **축 구성 설계** — 축 번호 배치, 기어비(Numerator/Denominator)·사용자 단위, 단회전(Single Turn) 여부,
   원점 복귀 전략(원점 유형 선택·Home Offset), 갠트리 축 구성,
   통신 주기(CommCycle) 확정 및 인터럽트-축 배치 결정 — 보간/동기/E-CAM/데이터 로그 그룹 축은
   동일 인터럽트에 배치(InterruptMismatch 예방, 근거: 미러 `funcnotes_ipt`·wmx3-app-implement 스킬
   `references/cpp-implementation.md` §8).
   위치 파이프라인 이해는 `references/architecture-core.md` 참조.
4. **요구 동작 → WMX3 기능 매핑** — 시나리오별 기능 배치(프로파일·보간·PVT·E-CAM·Look-Ahead·
   터치 프로브·PSO·폐루프·Dynamic 모션 등). `references/motion-function-map.md`의 매핑 표를 따른다.
   다관절 로봇이면 **Robot Option**(Kinematics/Coordinate) 적용 — `references/robot-option.md`.
5. **실시간·성능 전략** — 지터 제거(트리거 모션·ApiBuffer·이벤트), 고속 I/O Ex 함수, 폴링 vs 이벤트/Wait,
   CyclicBuffer, RTX SDK RT 앱 필요성 판단. `references/performance-stability.md` 참조.
6. **에러/안전 설계** — 반환 코드 확인 체계, 오류 코드 모듈별 분류 활용(정수 하드코딩 금지 — v3.7 값 시프트),
   Watchdog 타임아웃, 리미트 스위치, 토크 제한 램프(MaxTorqueLimitRamp), 비상 정지 시퀀스.
7. **설계 문서 산출** — 아래 산출물 형식의 마크다운 문서를 작성한다.

## 산출물: 설계 문서 형식

```markdown
# {장비명} WMX3.7 시스템 설계서

## 1. 요구사항 요약           ← 인터뷰 결과 표
## 2. 시스템 아키텍처          ← 구성 다이어그램(앱 ↔ WMX3 엔진 ↔ 플랫폼 ↔ 슬레이브), RT/비RT 배치
## 3. 플랫폼 선정              ← 선정 근거, Module.ini 플랫폼 구성, 통신 주기·인터럽트 구성(Module.ini 정의 순서=할당 순서), 구성 파일(ec_network.def/ENI 또는 simu_network.def) 계획
## 4. 축 구성 표               ← 축 번호 | 용도 | 기어비 | 사용자 단위 | 원점 유형 | 리미트 | 보정 | 인터럽트('인터럽트' 열은 멀티 인터럽트/하이브리드 구성 시 필수, 단일 인터럽트 구성은 생략 가능)
## 5. 기능 매핑 표             ← 요구 동작 | WMX3 기능/API 클래스 | 근거(§/토픽)
## 6. 시퀀스 설계              ← 초기화/운전/종료/이상 시 시퀀스 (CreateDevice→StartCommunication→SetServoOn→운전→역순 정리)
## 7. 성능·실시간 전략         ← 지터 대책(트리거 모션·ApiBuffer·이벤트), I/O 전략
## 8. 에러·안전 설계           ← 오류 처리 정책, Watchdog, 리미트/토크 제한
## 9. 리스크와 미결 사항       ← 항목별 심각도(CRITICAL/MAJOR/MINOR/INFO)와 완화책, HW 미확정/추가 확인 항목
```

리스크 심각도는 레포 관례에 따라 **CRITICAL / MAJOR / MINOR / INFO** 4등급으로 표기합니다.

## wmx3app-architect 에이전트 위임

실제 설계 작업은 `wmx3app-architect` 에이전트에게 위임합니다. 에이전트에게 전달할 정보:

- 수집된 요구사항(인터뷰 결과 표)
- 기존 시스템/코드베이스가 있으면 그 경로 (3.6u3 → 3.7 이식 여부 포함)
- 설계 문서 출력 경로 (기본: 프로젝트 루트 `docs/` 또는 사용자 지정)
- references 정본 절대 경로: `${CLAUDE_SKILL_DIR}/references/` 아래 문서들 — 호출 시 실제 절대 경로로 치환하여 전달

## references 문서

| 파일 | 내용 |
|------|------|
| `references/architecture-core.md` | 디바이스 모델·통신/서보온 시퀀스·위치 파이프라인·RT/비RT 배치 3패턴·모듈형 구조·API 클래스 지도 |
| `references/platform-selection.md` | 플랫폼 5종 비교 표·선택 플로차트·Module.ini 구성·하이브리드 구성 |
| `references/motion-function-map.md` | 요구 동작 → WMX3 기능 매핑 표 (시나리오별 API 배치) |
| `references/performance-stability.md` | 지터 제거·고속 I/O Ex·Watchdog·로그 진단·Slowdown Factor·RTX SDK 판단 기준 |
| `references/robot-option.md` | Robot Option 도메인 가이드 — 좌표계 3종·XML/URDF 로봇 정의·PTP/CP·충돌 감지 전제조건·핵심 API 지도 (v3.6u3 기준) |

## 매뉴얼 다이제스트 연동

manual-digest로 등록된 `wmx37-user-manual-kr`(및 `wmx3-user-manual-kr`) 다이제스트가 있으면 1차 참조하고
(`~/.claude/manuals/wmx37-user-manual-kr/digest.md`, project 스코프는 `.claude/manuals/`),
디테일은 다이제스트의 키워드 인덱스로 원본을 핀포인트합니다.
다관절 로봇 제어를 다루면 `wmx3-robot-help-kr`(Robot Option — 기구학·Joint/Cartesian 좌표계·PTP/CP·
XML/URDF 로봇 정의·충돌 감지) 다이제스트도 함께 1차 참조합니다(`~/.claude/manuals/wmx3-robot-help-kr/digest.md`).
다이제스트가 없는 환경이면 이 스킬의 `references/` 문서만으로 진행하고,
`/manual-digest`로 WMX3.7 매뉴얼 등록을 제안합니다.
답변/산출물에는 출처(§/토픽)를 명시합니다.
