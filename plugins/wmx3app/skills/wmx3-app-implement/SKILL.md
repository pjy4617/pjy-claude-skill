---
name: wmx3-app-implement
description: "WMX3.7 애플리케이션 C++/C# 구현. 설계 문서(wmx3-app-design 산출물) 또는 직접 요구를 받아 초기화/종료 시퀀스(CreateDevice→StartCommunication→SetServoOn), 모션·I/O·이벤트·ApiBuffer 기능 구현, 에러 처리 일관화, 3.6u3→3.7 마이그레이션을 수행한다. 'WMX 구현', 'WMX3 코드 작성', 'WMX C++ 구현', 'WMX C# 구현', '모션 프로그램 작성', 'WMX3 마이그레이션' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# WMX3 애플리케이션 C++/C# 구현

> 이 스킬은 WMX3.7 라이브러리를 **사용하는 애플리케이션**(장비 제어 SW)의 C++/C# 구현을 담당합니다.
> 실제 구현 작업은 **wmx3app-implementer 에이전트**에게 위임합니다.
>
> **wmx3md 플러그인과의 구분**: wmx3md는 WMX3 엔진에 로드되는 **내부 모듈(rtdll) 개발**용,
> 이 플러그인(wmx3app)은 WMX3 API를 호출하는 **응용 프로그램 개발**용입니다.
> 엔진 내부 모듈을 만들어야 한다면 wmx3md의 `wmx3-module-create`를 사용하세요.

## 입력

- `wmx3-app-design` 스킬의 설계 문서(권장) 또는 직접 구현 요구
- 구현 언어(C++/C#) — 명시되지 않았으면 사용자에게 확인
- 대상 WMX3 버전(기본 3.7)과 플랫폼(EtherCAT/시뮬레이터 등)

## 실행 절차

| 단계 | 작업 | 참조 |
|------|------|------|
| ① | 설계 문서/요구사항 확인 (축 수·모션 기능·I/O·에러 정책) | — |
| ② | 언어·프로젝트 구조 결정 (C++ VC++ x64 / C# .NET x64) | `references/cpp-implementation.md`, `references/csharp-implementation.md` |
| ③ | 초기화/종료 골격 작성: `CreateDevice` → `StartCommunication` → `SetServoOn`(서보온 확인 폴링) / 종료는 역순(모션 정지 확인 → 서보 오프 → `StopCommunication` → `CloseDevice`, C#은 추가로 `Dispose`) | 언어별 references |
| ④ | 기능 구현 (모션·보간·I/O·이벤트·ApiBuffer 등 — 다이제스트·references 근거) | 언어별 references + 매뉴얼 다이제스트 |
| ⑤ | 에러 처리 일관화 (반환 코드 확인·`ErrorToString`·정리 경로 보장) | `references/error-handling.md` |
| ⑥ | 기존 3.6u3 코드 이식 시 호환성 깨짐 8항목 적용 | `references/v37-migration.md` |
| ⑦ | 빌드 확인 (컴파일 오류/링크 오류 해결까지) | — |

EtherCAT 네트워크 구성(ENI 파일·`ec_network.def`)이 필요하면 `wmx3-app-eni` 스킬(wmx3app-eni-builder 에이전트)에 위임합니다.

## wmx3app-implementer 에이전트 위임

실제 코드 작성·수정·빌드는 `wmx3app-implementer` 에이전트에게 위임합니다.

에이전트에게 전달할 정보:
- 설계 문서 경로(있으면) 또는 요구사항 요약
- 구현 언어와 기존 프로젝트 경로(신규/기존 여부)
- 마이그레이션 여부(3.6u3 코드 이식이면 `references/v37-migration.md` 적용 지시)
- references 정본 절대 경로: `${CLAUDE_SKILL_DIR}/references/` 아래 문서들 — 호출 시 실제 절대 경로로 치환하여 전달
- 로봇 옵션 포함 시: `wmx3-app-design` 스킬의 `references/robot-option.md` 절대 경로도 함께 전달

## 필수 골격 (언어 공통 시퀀스)

```text
[초기화]  CreateDevice(경로, DeviceTypeNormal)
            → StartCommunication(타임아웃)     ← Engine State = Communicating
            → SetServoOn(축, 1)                ← GetStatus 폴링으로 서보온 확인
[운전]    모션/I/O/이벤트/ApiBuffer API 호출  ← 모든 반환값 확인
[종료]    모션 정지 확인 (Stop/ExecQuickStop → GetStatus 폴링·반복 상한)
            → SetServoOn(축, 0)
            → StopCommunication()
            → CloseDevice()
            → (.NET만) 모듈 객체 Dispose() → WMX3Api Dispose()
```

- 종료는 **모션 정지 확인 → 서보 오프 → StopCommunication → CloseDevice** 역순 고정 —
  모션 정지는 `Stop`/`ExecQuickStop`(WMX3.7 매뉴얼 CoreMotion에서 함수 존재 확인) 호출 후
  GetStatus 폴링(반복 상한)으로 정지 완료를 확인합니다.
- 토크/속도 운전 축은 `Stop`이 아닌 해당 모드의 정지 함수(토크는 `StopTrq` —
  `Motion::Stop` Remarks, Doxygen `classwmx3_api_1_1_motion.html`)를 사용합니다.
- 통신 개시 직후 전 축은 서보 오프 상태이며, 서보 온 상태에서만 위치 지령을 따릅니다.
  (근거: wmx3-user-manual-kr 다이제스트 §4 통신/서보온, wmx37 미러 tutorial1-6/1-7)
- .NET에서 `Dispose()` 미호출 시 GC가 비관리 리소스를 조기 해제하여 **정의되지 않은 동작**이
  발생할 수 있습니다. (근거: 보충정보 IDisposable)

## 로봇 옵션(Robot Option) 구현 노트

다관절 로봇 제어가 포함된 구현이면 다음을 적용합니다 (근거: `wmx3-robot-help-kr` 다이제스트 — v3.6u3 기준):

- **진입점**: `wmx3Api::RobotMotion` — 멤버 `mKinematics`(PTP/CP 실행·로봇 파라미터)와
  `mCoordinate`(좌표 변환·티칭)를 사용
- **로봇 정의 파일**: 코드가 아닌 XML + URDF(링크별 관성·tool 정보) — 파일 준비와 로드 구성을 구현 범위에 포함
- **PTP/CP 호출**: PTP는 `RobotMotion.mKinematics.StartPTPPos(PtpMotionParam::PtpPosParam)` —
  CP 등 그 외 함수의 시그니처 상세는 Robot Help API Reference(§5 클래스 토픽)에서 확인 후 사용
- **충돌 감지 설정**: `SetToolInfo`로 tool 정보 설정(관성행렬 미포함 시 점질량 가정) + 전제조건 4가지
  (모든 링크 관성·실시간 전류 피드백·tool 정보·`RobotMotionParam.robotParam.baseJointCoordinate` 전부 0) 충족 확인
- 도메인 상세는 `wmx3-app-design` 스킬의 `references/robot-option.md` 참조

## references

| 파일 | 내용 |
|------|------|
| `references/cpp-implementation.md` | C++ 프로젝트 설정(헤더/라이브러리/x64), 초기화·종료 골격, 에러 래퍼, 블로킹/논블로킹 구분, 멀티스레드·인터럽트·메모리 할당 주의 |
| `references/csharp-implementation.md` | WMX3ApiCLR 참조 설정, C++↔.NET 차이 10항목, Dispose 순서, GC 함정, 이벤트/콜백 패턴 |
| `references/error-handling.md` | 반환 코드 확인 원칙, ErrorToString, 재시도 vs 중단, 운전 중 통신 이상 처리, v3.7 오류코드 시프트 주의, 로그 연계 |
| `references/v37-migration.md` | 3.6u3→3.7 호환성 깨짐 8항목 Before/After + 탐지 grep 패턴 |

## 매뉴얼 다이제스트 연동

manual-digest로 등록된 `wmx37-user-manual-kr`(및 `wmx3-user-manual-kr`) 다이제스트가 있으면
1차 참조하고(`~/.claude/manuals/wmx37-user-manual-kr/digest.md`, project 스코프는 `.claude/manuals/`),
디테일은 다이제스트의 키워드 인덱스로 원본을 핀포인트합니다.
다관절 로봇 제어를 다루면 `wmx3-robot-help-kr`(Robot Option — 기구학·Joint/Cartesian 좌표계·PTP/CP·
XML/URDF 로봇 정의·충돌 감지) 다이제스트도 함께 1차 참조합니다(`~/.claude/manuals/wmx3-robot-help-kr/digest.md`).
다이제스트가 없는 환경이면
이 스킬의 `references/` 문서만으로 진행하고, `/manual-digest`로 WMX3.7 매뉴얼 등록을 제안합니다.
답변/산출물에는 출처(§/토픽)를 명시합니다.

## 구현 시 금지 사항

- **추측으로 API 함수명/시그니처를 만들지 않는다** — 다이제스트 또는 매뉴얼 원본(API Reference)에서
  확인된 것만 사용. 확인 못 한 시그니처는 함수명 수준까지만 쓰고 API Reference 확인을 지시.
- 오류코드 정수값 하드코딩 금지 (v3.7에서 API 버퍼 계열 오류코드 값이 시프트됨 —
  `references/error-handling.md` 참조).
- 종료 경로 생략 금지 — 모든 예외/오류 경로에서 `StopCommunication`/`CloseDevice`(/`Dispose`)가
  호출되도록 보장.
