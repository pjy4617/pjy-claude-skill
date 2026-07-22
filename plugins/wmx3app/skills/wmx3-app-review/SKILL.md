---
name: wmx3-app-review
description: "기존 프로젝트의 WMX3 API 사용을 7개 카테고리 35항목 체크리스트로 검토한다. 생명주기/리소스, 시퀀스 정합성, 에러 처리, 성능/실시간성, 안정성/안전, v3.6u3→3.7 마이그레이션, 코드 품질을 심각도 4등급(CRITICAL/MAJOR/MINOR/INFO)으로 등급화하고 파일:라인 근거와 수정 제안을 제시한다. 'WMX 사용 검토', 'WMX3 리뷰', 'WMX 코드 검토', 'WMX3 사용법 점검', 'wmx 마이그레이션 검토', 'WMX 프로젝트 진단' 등의 요청에 자동 적용. (WMX3 엔진 내부 모듈(rtdll) 개발 코드 리뷰는 wmx3md의 wmx3-code-review 담당 — 이 스킬은 WMX3 API를 호출하는 응용 프로그램 대상)"
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep, Agent
---

# WMX3 애플리케이션 사용 검토

> 이 스킬은 WMX3 API를 **사용하는 애플리케이션**(장비 제어 SW) 코드를 7개 카테고리, 35개 항목으로 검토합니다.
> 실제 검토는 **wmx3app-usage-reviewer 에이전트**에게 위임합니다 — **읽기 전용 검토**이며 코드를 수정하지 않습니다.
> 체크리스트 상세는 `references/usage-review-checklist.md`를 참조합니다.

**wmx3md와의 구분**: wmx3md 플러그인의 `wmx3-code-review`는 WMX3 엔진에 로드되는 **내부 모듈(rtdll) 개발** 코드 리뷰이고, 이 스킬은 WMX3 API를 호출하는 **응용 프로그램**의 사용법 검토입니다.

---

## 검토 절차 (5단계)

### 1. 프로젝트 스캔 — WMX3 사용 지점 식별

```bash
grep -rn -e "WMX3Api" -e "WMX3ApiCLR" -e "CreateDevice" -e "StartCommunication" \
  -e "RobotMotion" -e "Kinematics" -e "StartPTPPos" \
  --include="*.c" --include="*.cpp" --include="*.h" --include="*.cs" <프로젝트 경로>
```

스캔 결과로 다음을 파악합니다:
- **언어**: C++(`wmx3Api` 네임스페이스) / C#(`WMX3ApiCLR` 네임스페이스)
- **사용 모듈**: WMX3Api(메인)·CoreMotion·AdvancedMotion·Io·ApiBuffer·EventControl·UserMemory·Compensation·CyclicBuffer·Log 등
- **WMX3 버전 맥락**: 3.6u3 코드의 3.7 이식 여부(마이그레이션 카테고리 적용 판단)
- **플랫폼**: EtherCAT(`ec_network.def`) / 시뮬레이터(`simu_network.def`) 등
- **로봇 옵션 사용 여부**: `RobotMotion`/`Kinematics`/`StartPTPPos` 검출 시 보충 섹션 R 적용(아래 참조)

### 2. 체크리스트 검토

`references/usage-review-checklist.md`의 7개 카테고리 35항목을 순서대로 적용합니다.
각 항목의 grep 패턴은 1차 스크리닝용이며, 명중 라인은 반드시 Read로 원문을 확인한 뒤 판정합니다.
로봇 옵션(Robot Option) 사용 프로젝트면 체크리스트 끝의 **보충 섹션 R**(로봇 옵션 사용 시 추가 확인)을
추가 적용하고 `wmx3-robot-help-kr` 다이제스트를 참조합니다 — 7카테고리 35항목 + 로봇 보충 R.

### 3. 심각도 등급화

| 등급 | 의미 | 조치 |
|------|------|------|
| **CRITICAL** | 미정의 동작·오동작·v3.7 마이그레이션 파손(조용한 동작 변화) | 즉시 수정 |
| **MAJOR** | 안정성·안전·성능에 실질 영향(컴파일 오류로 즉시 드러나는 마이그레이션 파손 포함) | 배포 전 수정 |
| **MINOR** | 유지보수성 저하, 개선 권장 | 다음 리팩토링 시 수정 |
| **INFO** | 참고 사항 | 필요 시 검토 |

### 4. 항목별 근거와 수정 제안

발견 항목마다 **파일:라인** 근거와 구체적 수정 방향(체크리스트의 "수정 방향" 열 기반)을 제시합니다.

### 5. 종합 리포트 (마크다운)

아래 "리포트 형식"에 따라 심각도별로 정리해 보고합니다.

---

## 검토 카테고리 요약

| 카테고리 | 항목 수 | 핵심 관심사 |
|---------|---------|------------|
| 1. 생명주기/리소스 | 5항목 | CreateDevice↔CloseDevice 짝, .NET Dispose, 종료 시퀀스 |
| 2. 시퀀스 정합성 | 4항목 | 통신 개시→서보온→모션 순서, GetStatus 상태 확인 |
| 3. 에러 처리 | 4항목 | 반환 코드 확인, 오류코드 하드코딩(v3.7 시프트 위험) |
| 4. 성능/실시간성 | 5항목 | 폴링 vs 이벤트/트리거, ApiBuffer, 고속 I/O Ex |
| 5. 안정성/안전 | 5항목 | Watchdog, 리미트, 토크 제한, 타임아웃, 갠트리/동기 |
| 6. v3.7 마이그레이션 | 8항목 | 3.6u3→3.7 호환성 깨짐 8건 전수 탐지 |
| 7. 코드 품질 | 4항목 | 매직 넘버 축 번호, 설정 하드코딩, 스레드 안전성 |

로봇 옵션 사용 프로젝트에는 위 7카테고리 35항목에 더해 **보충 섹션 R. 로봇 옵션 사용 시 추가 확인**(6항목 —
URDF/XML 링크 관성·SetToolInfo·baseJointCoordinate·좌표 혼용·로봇 에러 코드·티칭 데이터)을 별도 적용합니다.

---

## 매뉴얼 다이제스트 연동

manual-digest로 등록된 `wmx37-user-manual-kr`(및 `wmx3-user-manual-kr`) 다이제스트가 있으면 1차 참조하고(`~/.claude/manuals/wmx37-user-manual-kr/digest.md`, project 스코프는 `.claude/manuals/`), 디테일은 다이제스트의 키워드 인덱스로 원본을 핀포인트한다. 다관절 로봇 제어를 다루면 `wmx3-robot-help-kr`(Robot Option — 기구학·Joint/Cartesian 좌표계·PTP/CP·XML/URDF 로봇 정의·충돌 감지) 다이제스트도 함께 1차 참조한다(`~/.claude/manuals/wmx3-robot-help-kr/digest.md`). 다이제스트가 없는 환경이면 이 스킬의 `references/` 문서만으로 진행하고, `/manual-digest`로 WMX3.7 매뉴얼 등록을 제안한다.

검토 결과의 각 판정에는 근거 출처(다이제스트 §/토픽 또는 체크리스트 항목 번호)를 명시합니다.

---

## wmx3app-usage-reviewer 에이전트 위임

이 스킬은 실제 검토 작업을 `wmx3app-usage-reviewer` 에이전트에게 위임합니다. **에이전트는 읽기 전용으로 동작하며 코드를 수정하지 않습니다** — 수정이 필요하면 리포트를 근거로 `wmx3-app-implement` 스킬(wmx3app-implementer 에이전트)을 사용하세요.

에이전트에게 전달할 정보:
- 검토 대상 경로(프로젝트 루트 또는 파일 목록)
- 언어(C++/C#)와 WMX3 버전 맥락(3.6u3 코드의 3.7 이식 여부)
- 특별히 집중할 카테고리 (없으면 전체 35항목)
- 최근 변경된 파일 (`git diff` 결과, 있으면)
- references 정본 절대 경로: `${CLAUDE_SKILL_DIR}/references/` 아래 문서들 — 호출 시 실제 절대 경로로 치환하여 전달

---

## 리포트 형식

```
== WMX3 애플리케이션 사용 검토 결과 ==

검토 대상: src/MotionController.cpp, src/TorqueCtrl.cpp, src/Program.cs (WMX3 3.7 / C++·C# 혼재)

[CRITICAL] 2건
  🔴 3.1 반환 코드 미확인
     위치: src/MotionController.cpp:88
     내용: StartHome(...) 반환값을 확인하지 않고 다음 단계 진행
     수정: 반환 코드 확인 후 실패 분기 추가 (checklist 3.1)

  🔴 6.3 토크 램프 시간 단위 미변환
     위치: src/TorqueCtrl.cpp:120
     내용: SetRampTime(500) — 3.6u3의 인터럽트 사이클 수(uint) 값으로 의심
     수정: 초(double) 단위로 변환 — timeSeconds = rampCycleTime × interruptPeriod_ms / 1000
           (wmx37-user-manual-kr 릴리즈 노트, checklist 6.3)

[MAJOR] 1건
  🟠 1.4 StopCommunication 없이 종료
     위치: src/Program.cs:203
     내용: 종료 핸들러에서 StartCommunication 대응 정지 호출 부재
     수정: 종료 시퀀스에 StopCommunication → CloseDevice → Dispose 역순 정리 추가

[MINOR] 1건
  🟡 7.2 설정 하드코딩
     위치: src/MotionController.cpp:31
     내용: ec_network.def 절대 경로 리터럴
     수정: 구성 파일 경로를 설정/인수로 외부화

[INFO] 1건
  🔵 4.3 고속 I/O Ex 미활용
     위치: src/IoScan.cpp:55
     내용: 고빈도 I/O 루프에서 통상 I/O 함수 사용
     참고: "Ex" 접미어 고속 I/O 함수 검토 가치 있음 (ApiBuffer 내 실행 불가 제약 유의)

== 요약 ==
CRITICAL: 2건  ← 즉시 수정 필요
MAJOR:    1건  ← 배포 전 수정 필요
MINOR:    1건  ← 다음 리팩토링 시 수정 권장
INFO:     1건  ← 참고 사항

다음 단계:
  CRITICAL 항목을 수정한 뒤 "다시 검토해줘"로 재검토하세요.
  수정 작업은 wmx3-app-implement 스킬로 진행할 수 있습니다.
```
