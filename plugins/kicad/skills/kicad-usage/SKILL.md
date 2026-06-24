---
name: kicad-usage
description: "KiCad 10.0 자체의 *사용 방법*을 알려준다 — 프로그램 조작·메뉴·단축키·기능 사용법을 묻는 질문에 번들된 공식 매뉴얼 다이제스트(kicad 프로젝트 매니저 / pcbnew PCB 에디터 / gerbview / kicad-cli)로 답한다. 'KiCad 사용법', 'KiCad 어떻게 써', 'pcbnew 사용법', 'PCB 에디터에서 ~ 어떻게', '보드 스택업 설정', '디자인 룰 설정', 'DRC 룰(.kicad_dru) 작성법', '차동쌍 배선 방법', '길이 튜닝', 'Zone/구리 채움', '풋프린트 만드는 법', '거버/드릴 내보내기(Plot)', 'STEP/3D 내보내기', 'GerbView 사용법', 'D-code 보기', 'kicad-cli 명령어/옵션', '단축키(hotkey) 알려줘', 'KiCad 설치/최초 설정', '라이브러리 설정', '프로젝트 템플릿', 'Plugin & Content Manager' 등 *KiCad 프로그램 자체의 조작/기능*을 묻는 질문에 자동 적용. ※ 사용자의 .kicad_sch/.kicad_pcb 파일을 *분석/리뷰/생성*하는 것은 kicad-analyze·kicad-review·kicad-design 스킬이 담당하고, 'KiCad라는 도구를 어떻게 쓰는가'(How-to) 안내는 이 스킬이 담당한다."
user-invocable: true
allowed-tools: Read, Grep, Glob, WebFetch
---

# KiCad 사용법 안내 (KiCad 10.0 매뉴얼 다이제스트)

이 스킬은 **KiCad 10.0 프로그램 자체의 사용 방법**을 알려준다. KiCad 공식 매뉴얼 4종을 한국어 다이제스트로 압축해 `references/`에 번들했으며, 사용자가 "KiCad에서 X 어떻게 해?"라고 물으면 원본 매뉴얼을 매번 읽지 않고 이 다이제스트를 1차 참조원으로 사용한다.

> 출처: KiCad 10.0 공식 문서(<https://docs.kicad.org/10.0/en/>). 각 다이제스트 섹션 제목 끝의 `#anchor`로 원문을 핀포인트할 수 있다(예: `https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#routing-tracks`).

## 다른 KiCad 스킬과의 역할 분담

| | 이 스킬 (kicad-usage) | kicad-design / kicad-review / kicad-analyze |
|---|---|---|
| 대상 | **KiCad 프로그램(앱)** 그 자체 | 사용자의 **회로/PCB 파일**(.kicad_sch/.kicad_pcb) |
| 질문 유형 | "KiCad에서 ~ 어떻게 하나?"(How-to) | "이 보드 ~ 해줘/검토해줘"(작업 수행) |
| 동작 | 매뉴얼 다이제스트 조회 → 출처와 함께 답변 | 파일 파싱·생성·리뷰·ERC/DRC·BOM |

"넷 추적해줘", "DRC 돌려줘", "이 회로도 리뷰해줘", "PRD로 회로도 만들어줘" → **kicad-analyze/review/design**. "PCB 에디터에서 DRC 룰 어떻게 작성해?", "차동쌍 배선 어떻게 해?", "Gerber 어떻게 내보내?" → **이 스킬**.

## 번들된 다이제스트 (references/)

| 파일 | 다루는 범위 | 원문 |
|------|------------|------|
| `INDEX.md` | 토픽 → 파일/anchor 마스터 인덱스. **답변 전 먼저 본다.** | — |
| `kicad-project.md` | KiCad 프로젝트 매니저, 설치/최초설정, 파일·폴더 구조, 경로/환경변수/라이브러리 설정, Jobsets, 프로젝트 템플릿, Plugin & Content Manager, Preferences, 단축키 | kicad/kicad.html |
| `pcbnew-1-setup-ui.md` | PCB 에디터 화면/표시·선택, 보드 레이어/Appearance, PCB 생성, **Board Setup**(스택업·디자인 룰·넷클래스·제약) | pcbnew/pcbnew.html |
| `pcbnew-2-editing-routing.md` | 배치·그리기·그리드, 풋프린트/패드/**Zone**, **트랙/비아 배선**, **차동쌍**, **길이 튜닝**, Teardrops, Backdrill, 그래픽, Rule area, Group/Array, 핀/게이트 스왑 | pcbnew/pcbnew.html |
| `pcbnew-3-inspect-output.md` | Forward/Back annotation, **DRC**, 보드 통계, 측정/Find/Search, 3D 뷰어, Net inspector, 타 EDA 임포트, **출력 생성**(Plot/Gerber/Drill/IPC-2581/ODB++/Position/BOM/STEP), Design variants | pcbnew/pcbnew.html |
| `pcbnew-4-footprints.md` | 풋프린트 라이브러리 관리, **풋프린트 에디터**(패드·필드·레이어·net tie·3D 모델·wizard·체크), 멀티채널 레이아웃, 디자인 블록 | pcbnew/pcbnew.html |
| `pcbnew-5-advanced-rules.md` | 설정/커스터마이즈, Text variables/expressions, Graphical DR editor, **Custom design rules(.kicad_dru)**, Python **Scripting**, IDF 아웃라인 | pcbnew/pcbnew.html |
| `pcbnew-6-hotkeys.md` | PCB Editor / 3D Viewer / Common **단축키** 전체 표 | pcbnew/pcbnew.html |
| `gerbview.md` | **GerbView** 거버/드릴 뷰어 — 인터페이스, 툴바, Layers Manager, 메뉴, 인쇄 | gerbview/gerbview.html |
| `kicad-cli.md` | **kicad-cli** 명령행 레퍼런스 — fp/jobset/pcb/sch/sym/version 서브커맨드와 옵션/플래그 | cli/cli.html |

## 답변 워크플로

1. **`references/INDEX.md`를 먼저 읽는다** — 질문 토픽이 어느 파일·anchor에 있는지 찾는다. (`Grep`으로 키워드 검색해도 됨: `grep -ri "키워드" references/`)
2. 해당 다이제스트 파일을 `Read`하고, 질문에 맞는 섹션을 근거로 한국어로 답한다.
3. **출처를 항상 명시**한다 — 다이제스트 파일명 + 원문 anchor(예: "출처: pcbnew §Length tuning · `pcbnew.html#length-tuning`"). 메뉴 경로·옵션명·단축키·CLI 플래그는 영어 원문 그대로 인용한다.
4. 다이제스트로 **부족할 때만** 원문을 핀포인트한다: `WebFetch`로 `<원문 URL>#<anchor>`를 가져와 해당 섹션만 확인. (오프라인이면 다이제스트 범위로 답하고 한계를 밝힌다.)
5. 추측 금지 — 다이제스트/원문에 없으면 "매뉴얼에 명시되지 않음"이라고 말한다.

## 답변 원칙

- 절차 질문은 **번호 목록**으로(메뉴 경로 + 단축키 포함). 예: "**Place → Add Footprint** (단축키 `A`)".
- 단축키·CLI 플래그·룰 문법은 다이제스트의 표/코드펜스를 그대로 인용한다.
- 버전 차이 주의: 이 다이제스트는 **KiCad 10.0** 기준이다. 사용자가 9.x를 쓰면(메모리상 본 환경 기본은 9.0+) 대부분 동일하나 일부 UI/기능이 다를 수 있음을 필요 시 덧붙인다.
- 사용자가 자신의 보드에 실제로 적용하길 원하면(예: "그럼 내 보드에 이 DRC 룰 넣어줘") kicad-analyze/design 스킬로 자연스럽게 연결한다.

## 사용 예시

```
"KiCad에서 차동쌍 어떻게 배선해?"            → pcbnew-2-editing-routing.md (#routing-differential-pairs)
"보드 스택업이랑 임피던스 어디서 설정해?"      → pcbnew-1-setup-ui.md (#board-setup-stackup)
"커스텀 DRC 룰(.kicad_dru) 문법 알려줘"        → pcbnew-5-advanced-rules.md (#custom-design-rules)
"거버랑 드릴 파일 어떻게 내보내?"              → pcbnew-3-inspect-output.md (#plotting, #drill-files)
"kicad-cli로 PCB DRC 돌리는 명령 뭐야?"        → kicad-cli.md (pcb drc)
"GerbView에서 D-code 어떻게 봐?"               → gerbview.md
"PCB 에디터 단축키 정리해줘"                   → pcbnew-6-hotkeys.md
"KiCad 라이브러리 경로 어떻게 설정해?"         → kicad-project.md (#libraries-configuration)
```

$ARGUMENTS
