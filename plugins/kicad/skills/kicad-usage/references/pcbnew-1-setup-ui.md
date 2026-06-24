# PCB 에디터 ① — 화면/표시·선택·보드 셋업 — KiCad 10.0 사용 다이제스트

> **원문**: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html

> **범위**: PCB 에디터 UI/캔버스 탐색/단축키 개념, 보드 레이어, Appearance 패널, 선택·선택 필터, 넷 하이라이트, 스키매틱 크로스프로브, 좌측 툴바, PCB 생성(스키매틱에서 시작/처음부터), Board Setup(스택업·물리 파라미터·텍스트/그래픽·디자인 룰·넷클래스·제약·파일 임베딩·설정 가져오기)

> 한국어 요약 다이제스트. 섹션 제목의 #anchor로 원문 핀포인트: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#<anchor>

## 목차

- [Display and selection controls (그룹)](#display-and-selection) — 표시·선택 컨트롤 챕터 개요
- [Introduction to the KiCad PCB Editor](#introduction_to_the_kicad_pcb_editor) — PCB 에디터 개요와 통합 기능(DRC·라우터·팹출력·3D)
- [The PCB Editor user interface](#the_pcb_editor_user_interface) — 메인 UI 구성 요소
- [Navigating the editing canvas](#navigating_the_editing_canvas) — 팬/줌/뷰 플립·좌표 표시
- [Hotkeys](#hotkeys) — 단축키 목록·편집·저장 위치
- [Board layers](#board_layers) — 보드 레이어와 active layer 개념
- [Display order for board layers](#display_order_for_board_layers) — active layer 기준 동적 표시 순서
- [The appearance panel](#appearance-panel) — Layers/Objects/Nets 3탭 표시 제어
- [Layer controls](#layer_controls) — Layers 탭 색/가시성/표시모드
- [Object controls](#object_controls) — Objects 탭 색/불투명도
- [Layer presets](#layer_presets) — 레이어 가시성 프리셋 저장/호출
- [Viewports](#viewports) — 뷰 위치·줌 저장/호출
- [Net and net class controls](#net_and_net_class_controls) — Nets 탭 넷/넷클래스 가시성·색
- [Selection and the selection filter](#selection) — 선택 방법·선택 필터
- [Net highlighting](#net-highlighting) — 넷 하이라이트
- [Cross-probing from the schematic](#cross_probing_from_the_schematic) — 스키매틱↔PCB↔3D 크로스프로브
- [Left toolbar display controls](#left-toolbar-display-controls) — 좌측 툴바 표시 버튼
- [Creating a PCB](#creating_a_pcb) — PCB 생성 개요
- [Basic PCB concepts](#basic_pcb_concepts) — footprint/net/track/via/zone
- [Capabilities](#capabilities) — 레이어/해상도/크기 한계
- [Starting from a schematic](#starting_from_a_schematic) — 권장 워크플로(F8)
- [Starting from scratch](#starting-from-scratch) — 스키매틱 없이 시작
- [Board setup](#board_setup) — Board Setup 다이얼로그 개요
- [Configuring board stackup and physical parameters](#board-setup-stackup) — 스택업 설정
- [Board editor layers](#board_editor_layers) — 레이어 활성화/이름/사용자 레이어
- [Physical stackup](#physical_stackup) — 물리 스택업·두께
- [Board finish](#board_finish) — 카퍼 피니시·캐스털레이션
- [Solder mask/paste](#solder_maskpaste) — 솔더마스크/페이스트 클리어런스
- [Zone hatch offsets](#zone_hatch_offsets) — 존 해치 오프셋 기본값
- [Configuring text and graphics](#configuring_text_and_graphics) — 텍스트/그래픽 설정 개요
- [Defaults](#board-setup-defaults) — 신규 텍스트/그래픽/존 기본값
- [Formatting](#formatting) — 점선 포맷·풋프린트 적용
- [Text variables](#board-setup-text-variables) — 프로젝트 텍스트 변수 `${VAR}`
- [Configuring design rules](#configuring_design_rules) — 디자인 룰 설정 개요
- [Constraints](#board-setup-constraints) — 보드 전역 최소 제약
- [Pre-defined sizes](#board-setup-pre-defined-sizes) — 트랙/비아 사전 정의 크기
- [Teardrops](#board-setup-teardrops) — 티어드롭 기본값
- [Length-tuning patterns](#length_tuning_patterns) — 길이 튜닝 패턴 기본값
- [Tuning profiles](#tuning_profiles) — 임피던스 기반 레이어별 튜닝 프로파일
- [When to enable time-domain tuning](#when_to_enable_time_domain_tuning) — 시간영역 튜닝 활성 시점
- [Understanding track propagation parameters](#understanding_track_propagation_parameters) — 마이크로스트립/스트립라인 전파
- [Understanding via propagation parameters](#understanding_via_propagation_parameters) — 비아 전파 지연
- [How tuning profiles, net classes, and the length tuner work together](#how_tuning_profiles_net_classes_and_the_length_tuner_work_together) — 3요소 연계
- [Net classes](#board-setup-net-classes) — 넷클래스 라우팅/클리어런스 규칙
- [Component classes](#component-classes) — 컴포넌트 클래스 자동 할당 규칙
- [Understanding component classes](#component-class-concepts) — 컴포넌트 클래스 개념
- [Where component classes are defined](#where_component_classes_are_defined) — 정의 위치
- [How multiple classes combine](#how_multiple_classes_combine) — 다중 클래스 결합
- [Schematic-defined and PCB-defined classes](#schematic_defined_and_pcb_defined_classes) — 두 정의 출처
- [Assignment rule details](#component-class-assignment-rules) — 할당 규칙 구성
- [Assignment rule examples](#assignment_rule_examples) — 할당 규칙 예시
- [How classes update](#how_classes_update) — 클래스 갱신(F8)
- [Using component classes in custom DRC rules](#component-classes-in-drc) — DRC 룰 내 사용
- [Custom rules](#custom_rules) — 커스텀 디자인 룰 텍스트 에디터
- [Violation severity](#board-setup-violation-severity) — 위반 심각도 설정
- [Embedding files](#pcb-embedding-files) — 파일 임베딩
- [Importing settings](#importing_settings) — 다른 보드에서 설정 가져오기

---

## Introduction to the KiCad PCB Editor · #introduction_to_the_kicad_pcb_editor

- KiCad PCB Editor는 Linux/macOS/Windows용 PCB 레이아웃 애플리케이션. 모든 KiCad 파일은 OS 간 100% 호환.
- 풋프린트 배치, 트랙 라우팅, 라이브러리 관리, 스키매틱 데이터 전송이 모두 에디터 내에서 수행되는 통합 애플리케이션.
- KiCad Schematic Editor와 직접 통신하여 중간 파일 없이 스키매틱에서 PCB 설계. 다른 패키지의 넷리스트 파일도 import 가능.
- 풋프린트 라이브러리 에디터 포함. 추가 핵심 기능:
  - **DRC**(Design rules check): 오결선/누락 연결, 카퍼 clearance·최소 폭 위반 등 자동 검출
  - 스크립트 가능한 디자인 룰(복잡한 제약/조건)
  - 인터랙티브 라우터: push-and-shove / walkaround / highlight collisions 모드, 차동 페어 라우팅, length·skew 튜닝
  - 팹/플롯 파일 출력: Gerber, IPC-2581, ODB++, GenCAD, PDF, PostScript, SVG
  - 3D 뷰어 및 3D 모델 생성: STEP, GLB, BREP, XAO, PLY, STL, IDF, VRML

## The PCB Editor user interface · #the_pcb_editor_user_interface

- 메인 UI 구성 요소:
  1. Top toolbars (파일 관리, zoom 도구, 편집 도구)
  2. Left toolbar (표시 옵션)
  3. Properties panel
  4. Message panel and status bar
  5. Right toolbar (드로잉·설계 도구)
  6. Appearance panel
  7. Selection filter panel
  8. Editing canvas

## Navigating the editing canvas · #navigating_the_editing_canvas

- 캔버스는 설계 중인 보드를 보는 뷰. 팬/줌이 가능하고 뷰를 뒤집어 보드를 바닥에서 볼 수 있다.
- 기본: 마우스 가운데/오른쪽 버튼 드래그 = 팬, 휠 스크롤 = 줌 인/아웃. 동작은 Preferences의 Mouse and Touchpad 섹션에서 변경(Configuration and Customization 참조).
- Top toolbar의 줌 도구:
  - Zoom In: 뷰포트 중앙 기준 확대
  - Zoom Out: 뷰포트 중앙 기준 축소
  - Zoom to Page: drawing sheet 프레임에 맞춤
  - Zoom to Objects: drawing sheet 안의 아이템에 맞춤
  - Zoom to Selection: 박스를 그려 확대 영역 지정
- 창 하단에 커서 현재 위치(X, Y), 현재 zoom factor(Z), 커서 상대 위치(dx, dy, dist), grid 설정, 표시 단위가 나타난다.
- 💡 `Space`를 누르면 상대 좌표를 0으로 리셋 — 두 점 사이 거리 측정이나 객체 정렬에 유용.

## Hotkeys · #hotkeys

- `Ctrl`+`F1`: 현재 단축키 목록 표시. 기본 단축키 목록은 매뉴얼의 Actions Reference 섹션에 수록.
- 이 매뉴얼의 단축키는 표준 PC 키보드 라벨 기준. Apple 키보드는 `Ctrl` 대신 `Cmd`, `Alt` 대신 `Option` 사용.
- 다수 액션은 기본 단축키가 없지만, hotkey editor(**Preferences** → **Preferences…​** → **Hotkeys**)에서 할당/재정의 가능.
- 💡 단축키로 가능한 액션 다수는 context menu(캔버스 우클릭)에서도 사용 가능. 선택 항목/활성 도구에 따라 메뉴가 달라진다.
- 단축키는 KiCad 설정 디렉토리의 `user.hotkeys` 파일에 저장:

| OS | 경로 |
| --- | --- |
| Windows | `%APPDATA%\kicad\10.0\user.hotkeys` |
| Linux | `~/.config/kicad/10.0/user.hotkeys` |
| macOS | `~/Library/Preferences/kicad/10.0/user.hotkeys` |

- hotkey editor의 **Import Hotkeys** 버튼으로 `user.hotkeys` 파일에서 설정 가져오기 가능.

## Display and selection controls (그룹) · #display-and-selection

PCB 에디터의 화면 **표시·선택** 컨트롤 묶음 챕터. 하위 섹션: Board layers, Appearance 패널, Selection/선택 필터, Net highlighting, 스키매틱 Cross-probing, 좌측 툴바 표시 컨트롤.

## Board layers · #board_layers

- 레이어는 보드의 물리 카퍼 레이어와, silkscreen·solder mask·board edge 같은 그래픽 레이어를 나타낸다.
- 항상 하나의 **active layer**가 존재. active layer는 다른 레이어 위에 그려지고, 새로 생성되는 객체에 할당된다. top toolbar의 layer selector 드롭다운에 표시되고 appearance panel에서 강조된다.
- active layer 변경 방법: appearance panel에서 레이어 이름 좌클릭 / top toolbar 드롭다운 선택 / 단축키.
- 레이어를 숨겨 보드 뷰를 단순화 가능. active layer라도 숨길 수 있다.

## Display order for board layers · #display_order_for_board_layers

- 보드 레이어 표시 순서는 동적이며 active layer에 따라 달라진다. active layer는 항상 최상단에 그려진다.
- active layer와 관련된 레이어들이 무관한 레이어보다 위에 그려진다. 예: B.Silkscreen을 active로 하면 다른 back 레이어들(B.Cu, B.Adhesive, B.Paste, B.Mask, B.Fab, B.Courtyard)이 front·user·inner copper 레이어 위에 그려지고 B.Silkscreen이 최상단. Edge.Cuts를 active로 하면 그것이 최상단에 오고 User.* 레이어와 Margin도 앞으로 나온다.
- ⚠️ 선택된 객체는 active layer가 아니어도 항상 최상단에 그려진다.

## The appearance panel · #appearance-panel

- 드로잉 캔버스 객체의 가시성·색·불투명도를 관리하는 패널. 3개 탭:
  - **Layers** 탭: 보드 레이어 제어
  - **Objects** 탭: 그래픽 객체 타입별 제어
  - **Nets** 탭: ratsnest 및 카퍼 아이템 표시 제어

### Layer controls · #layer_controls

- Layers 탭은 각 보드 레이어를 색·가시성 상태와 함께 표시. active layer는 색 스와치 왼쪽 화살표 표시기로 강조.
- 레이어 좌클릭 → active layer 선택. 가시성 아이콘 좌클릭 → 표시/숨김 토글. 색 스와치 더블클릭/가운데클릭 → 레이어 색 변경.
- ⚠️ appearance panel에서 레이어 색을 바꾸려면 먼저 Preferences에서 custom color theme를 생성해야 한다.
- 레이어 목록 아래 확장 패널에 레이어 표시 옵션 존재:
  - 첫 설정: 비활성 레이어 표시 방식 — normal / dimmed / hidden. 단일 레이어에 집중하기 위해 사용.
  - 💡 비활성 레이어 표시모드가 "Dim" 또는 "Hide"일 때 비활성 레이어 아이템은 선택 불가.
  - 💡 `Ctrl`+`H`로 표시모드를 빠르게 순환.
- **Flip board view**: 보드를 바닥에서 본 것처럼 표시(Y축 기준 미러). View 메뉴에도 있음.
  - ⚠️ 뷰를 뒤집어도 시각적 레이어 순서는 바뀌지 않는다 — active layer가 여전히 맨 앞, 나머지는 정상 순서.

### Object controls · #object_controls

- Objects 탭은 Layers 탭과 유사. 차이점: 일부 객체는 색 설정이 없고, 4개 객체 타입(tracks, vias, pads, zones)은 불투명도 슬라이더를 가진다.
- 여기 불투명도 설정은 layer color의 불투명도와 곱해진다. 기본적으로 모든 객체는 완전 불투명이나, zones만 채워진 존 아래 객체가 보이도록 translucent(반투명)로 설정됨.

### Layer presets · #layer_presets

- 레이어 프리셋: 어떤 레이어/객체가 보이고 숨겨졌는지를 저장해 쉽게 호출. 내장 프리셋 여러 개 + 사용자 커스텀 프리셋 저장 가능.
- 커스텀 프리셋은 보드의 project settings에 저장(프리셋이 특정 보드 스택업에 특화될 수 있으므로).
- 프리셋 로드: appearance panel 하단 Presets 드롭다운에서 선택, 또는 quick switcher(`Ctrl` 누른 채 `Tab`). quick switcher 창에서 `Tab`/`Shift`+`Tab`로 순환, `Ctrl` 떼면 강조된 프리셋 로드.
- 커스텀 프리셋 저장: 가시성 컨트롤로 보이게 할 레이어 선택 → Presets 드롭다운 **Save preset…​** → 이름 지정. 수정은 같은 이름으로 다시 저장(덮어쓰기). 삭제는 드롭다운 **Delete preset…​**에서 선택.

### Viewports · #viewports

- 뷰포트: 현재 뷰 위치와 줌 레벨을 저장해 나중에 빠르게 복귀하거나 여러 저장된 뷰 사이를 전환.
- 뷰포트 로드: appearance panel 하단 Viewports 드롭다운에서 선택, 또는 quick switcher(`Shift` 누른 채 `Tab`). 창에서 `Tab`으로 순환, `Shift` 떼면 강조된 뷰포트 로드.
- 새 뷰포트 저장: 원하는 영역으로 스크롤/줌 → Viewports 드롭다운 **Save viewport…​** → 이름 지정. 수정은 같은 이름으로 저장(덮어쓰기). 삭제는 **Delete viewport…​**에서 선택.

### Net and net class controls · #net_and_net_class_controls

- Nets 탭은 보드의 모든 넷과 넷클래스 목록 표시. 각 넷은 가시성 컨트롤(ratsnest에서의 가시성)을 가진다.
- ratsnest에서 넷을 숨겨도 보드 연결성은 바뀌지 않고 DRC에 영향 없음 — ratsnest를 이해하기 쉽게 만드는 용도일 뿐.
- 각 넷/넷클래스에 색 할당 가능. 기본적으로 이 색은 넷의 ratsnest 선(또는 넷클래스의 모든 넷)에 적용. 넷은 기본 색 없음(색 스와치에 체커보드 패턴으로 표시). 색 스와치 더블클릭/우클릭 → 색 설정. 넷클래스를 스키매틱과 같은 색으로 하려면 넷클래스 우클릭 → **Use color from schematic**.
- ⚠️ Default 넷클래스는 색 할당 불가 — 이 클래스의 넷은 color theme의 기본 ratsnest 색을 사용.
- appearance panel에서 넷/넷클래스 선택 및 하이라이트 가능: 넷/넷클래스 우클릭 → 메뉴에서 옵션 표시.
- 넷클래스 목록 아래 확장 패널에 넷 표시 옵션:
  - 넷 색 적용 방식: **All**(넷/넷클래스에 속한 모든 카퍼 아이템 pads·tracks·vias·zones에 색 적용) / **Ratsnest**(기본값, ratsnest만 영향) / **None**(넷·넷클래스 색 무시)
  - ratsnest 선 그리기 방식: **All layers**(모든 미연결 아이템 간 ratsnest 그림) / **Visible layers**(숨겨진 레이어의 아이템에는 미연결이어도 ratsnest 안 그림)
  - 💡 ratsnest 선 두께는 Preferences의 PCB Editor Editing Options 섹션에서 조정 가능.

## Selection and the selection filter · #selection

- 캔버스 아이템 선택은 좌클릭. 도구 비활성 시 단일 클릭으로 객체 선택.
- `Esc`는 항상 현재 도구/작업을 취소하고 selection tool로 복귀. selection tool 활성 중 `Esc`는 현재 선택 해제.
- **사각형/올가미(lasso) 선택**: 우측 툴바의 cursor / lasso 팔레트로 모드 전환.
  - 💡 팔레트에서 도구 전환: 도구 아이콘에 좌클릭&홀드 또는 클릭&드래그로 팔레트 표시 → 원하는 도구 위에서 버튼 release.
- **사각형 선택**: 클릭&드래그.
  - 왼→오른쪽: 박스 안에 완전히 들어간 아이템만 선택(노란색 박스, 배타적 선택 커서).
  - 오른→왼쪽: 박스에 닿는 모든 아이템 선택(파란색 박스, 포함 선택 커서).
- **올가미 선택**: 클릭&드래그로 시작(기존 선택 해제). 좌버튼 홀드 드래그 = 자유 곡선, release = 직선 시작, 다시 클릭 = 직선 완료. 자유곡선/직선 세그먼트를 반복. 더블클릭으로 완료.
  - 시계방향: 올가미 안에 완전히 든 아이템만(노란색, 배타).
  - 반시계방향: 닿는 아이템 모두(파란색, 포함).
- ⚠️ 선택 수정 modifier 키는 클릭/드래그에 적용되며, lasso 선택에는 사용 불가.

**단일 아이템 클릭 선택 modifier:**

| Windows | Linux | macOS | 효과 |
| --- | --- | --- | --- |
| `Ctrl` | `Ctrl` | `Cmd` | 선택 토글. (참고: `Ctrl`+클릭은 **Preferences** → **PCB Editor** → **Editing Options**에서 highlight net으로 재매핑 가능) |
| `Shift` | `Shift` | `Shift` | 기존 선택에 아이템 추가 |
| `Ctrl`+`Shift` | `Ctrl`+`Shift` | `Cmd`+`Shift` | 기존 선택에서 아이템 제거 |
| long click | long click 또는 `Alt` | long click 또는 `Option` | 팝업 메뉴로 선택 명확화(clarify) |

**사각형 선택 드래그 modifier:**

| Windows | Linux | macOS | 효과 |
| --- | --- | --- | --- |
| `Ctrl` | `Ctrl` | `Cmd` | 선택 토글 |
| `Shift` | `Shift` | `Shift` | 기존 선택에 아이템 추가 |
| `Ctrl`+`Shift` | `Ctrl`+`Shift` | `Cmd`+`Shift` | 기존 선택에서 아이템 제거 |

- **Selection filter panel**(우측 하단): 마우스로 선택 가능한 객체 타입을 제어. 원치 않는 타입을 끄면 밀집 보드에서 선택이 쉬워진다.
  - **All items** 체크박스: 다른 항목을 한꺼번에 on/off하는 단축.
  - **Locked items** 체크박스: 나머지와 독립적 — 잠긴 아이템 선택 허용 여부.
  - 선택 필터에서 객체 타입 우클릭 → 해당 타입만 선택 허용하도록 빠르게 변경.
  - 비활성화된 타입의 객체를 반복 선택 시도하면 해당 체크박스가 깜빡여 알림.
- **Expand Selection**(우클릭 context menu 또는 단축키 `U`): 연결된 카퍼 아이템 선택 시 같은 넷의 다른 카퍼 아이템으로 선택 확장. 1회 실행 = 가장 가까운 pad까지, 2회 = 모든 레이어의 모든 연결 아이템까지. 선택 필터를 따르므로 비활성 타입 객체에 도달하면 확장 정지(예: via 선택 비활성 시 via에 닿을 때까지 확장).
- 객체 선택 시 message panel(하단)에 객체 정보 표시. 객체 더블클릭 → 속성 편집 창.

## Net highlighting · #net-highlighting

- 전기적 넷(또는 넷 집합)을 하이라이트하여 PCB 전역에서 어떻게 라우팅되었는지 시각화. 활성 시 하이라이트된 넷은 밝은 색, 나머지는 평소보다 어두운 색.
- PCB 에디터에서 넷을 선택해 하이라이트하거나, cross-probe highlighting 활성 시 스키매틱에서 넷을 선택하여 활성화.
- PCB 에디터에서 하이라이트할 넷 선택 방법:
  - 카퍼 객체 선택 후, 또는 카퍼 객체 위에 호버한 채 단축키 ` ` ` `(backtick)
  - 카퍼 객체 우클릭 → **Net Inspection Tools** → **Highlight Net**
  - Appearance 패널 **Nets** 탭에서 넷 우클릭 → **Highlight**
  - Net Inspector에서 넷 더블클릭
- Highlight Net 단축키를 누르면 선택된 카퍼 아이템들의 넷이 하이라이트. 선택된 카퍼 아이템이 없으면 커서 아래 카퍼 아이템의 넷이 하이라이트.
- 하이라이트 해제: Clear Net Highlight 액션(단축키 `~`), 또는 빈 영역에 Highlight net 도구 사용. 기본적으로 `Esc`도 하이라이트 해제(**Preferences** → **PCB Editor** → **Editing Options**에서 비활성 가능).
- 넷 하이라이트 선택 후에는 좌측 툴바의 **Toggle Net Highlighting** 액션이 활성화(단축키 `Ctrl`+` ` ` `). 새 넷을 고르지 않고 하이라이트 표시만 on/off.

## Cross-probing from the schematic · #cross_probing_from_the_schematic

- KiCad는 스키매틱↔PCB 양방향 크로스프로빙 지원. 여러 유형 존재.
- **Selection cross-probing**: 스키매틱에서 심볼/핀을 선택하면 PCB의 대응 풋프린트/패드 선택, 역방향도 가능.
- 크로스프로빙은 3D Viewer에서도 동작 — 3D Viewer에서 컴포넌트 선택 시 스키매틱·PCB에서도 선택, 반대로도 동작.
- 기본적으로 크로스프로브 시 대상 아이템을 화면 중앙에 두고 zoom to fit. 이 centering/zooming 동작 비활성화, 또는 selection cross-probing 전체 비활성화는 Preferences의 Display Options 섹션에서 설정. **Flash cross-probed selection** 활성 시 크로스프로브된 아이템이 3번 깜빡여 찾기 쉬움.
- selection cross-probing이 비활성이어도 수동 크로스프로브 가능: 스키매틱→PCB는 객체 우클릭 → **Select on PCB**, PCB→스키매틱은 객체 우클릭 → **Select** → **Select on Schematic**.
- **Highlight cross-probing**: 스키매틱과 PCB에서 동시에 넷 하이라이트. Display Options의 "Highlight cross-probed nets" 활성 시 스키매틱 에디터에서 넷/버스 하이라이트하면 PCB 에디터의 대응 넷도 하이라이트.

## Left toolbar display controls · #left-toolbar-display-controls

- 좌측 툴바는 PCB 에디터의 아이템 표시 방식을 변경하는 옵션 제공.
- 일부 버튼은 팔레트로 여러 항목 제공(버튼 우하단 작은 화살표로 표시). 팔레트 표시: 버튼 클릭&홀드 또는 클릭&드래그. 팔레트는 닫혀 있을 때 가장 많이 선택된 항목을 표시.
- 💡 툴바 내용은 PCB Editor Preferences의 **Toolbar** 페이지에서 편집 가능.

| 버튼 | 기능 |
| --- | --- |
| grid | grid 표시 on/off. (참고: 기본적으로 grid를 숨겨도 grid snapping은 비활성화되지 않음 — Preferences의 Display Options에서 변경) |
| grid override enable | item-specific grid override on/off |
| polar coord | status bar 좌표 표시를 polar/Cartesian 전환 |
| unit inch/mil/mm | 좌표·치수 표시·입력 단위(inches/mils/mm). 버튼 클릭 = 다음 단위로 토글, 팔레트 확장 = 직접 선택 |
| cursor shape/fullscreen/fullscreen45 | 커서 십자선 small / fullscreen / 45도 회전 fullscreen 전환. 클릭 = 다음으로 토글, 팔레트 확장 = 직접 선택 |
| free/90deg/45deg angle wire | 새 트랙·존·그래픽·치수 등의 line mode를 free angle / 90도 / 45도 전환. 클릭 = 토글, 팔레트 = 직접 선택. `Shift`+`Space`로도 토글 |
| general ratsnest | ratsnest 표시 on/off |
| curved ratsnest | ratsnest 선을 straight/curved 전환 |
| contrast mode | 비활성 레이어 표시모드를 Normal/Dim 전환. (참고: 표시모드가 Dim 또는 Hide면 버튼 강조, 누르면 Normal로 변경. Hide 모드는 Appearance Panel 컨트롤 또는 단축키 `Ctrl`+`H`로만 접근) |
| net highlight | 넷 하이라이트 선택 시 표시 on/off. (참고: 하이라이트된 넷 없으면 비활성. 넷 하이라이트는 단축키 ` ` ` `, 카퍼 객체 우클릭 → Net Tools → Highlight Net, 또는 Appearance Nets 탭에서 우클릭) |
| show zone | 존 채워진 영역 표시 |
| show zone disable | 존 외곽선만 표시 |
| pad sketch | 패드 표시를 filled/outline 전환 |
| via sketch | 비아 표시를 filled/outline 전환 |
| showtrack | 트랙 표시를 filled/outline 전환 |
| layers manager | 우측 Appearance·Selection Filter 패널 표시/숨김 |
| tools | 좌측 Properties Manager 패널 표시/숨김 |

## Creating a PCB · #creating_a_pcb

(PCB 생성 워크플로의 상위 섹션. 하위 항목은 아래 참조.)

### Basic PCB concepts · #basic_pcb_concepts

- KiCad의 PCB는 일반적으로 다음으로 구성:
  - **footprints**: 전자 부품과 그 패드를 나타냄
  - **nets**: 패드 간 연결 정의
  - **tracks**, **vias**, **filled zones**: 각 넷의 패드 간 카퍼 연결 형성
  - 다양한 graphic shapes: board edge, silkscreen 표시 등 기타 정보 정의
- KiCad는 보통 PCB의 넷 정보를 연결된 스키매틱과 동기화하지만, PCB 에디터 내에서 직접 넷 생성/편집도 가능.

### Capabilities · #capabilities

- 최대 32 copper layers, 14 technical layers(silkscreen, solder mask, component adhesive, solder paste 등), 13 general-purpose drawing layers 생성 가능.
- 내부 측정 해상도는 모든 객체 1 nanometer, 32-bit 정수로 저장 → 약 4 m × 4 m 크기까지 보드 제작 가능.
- KiCad는 현재 프로젝트/스키매틱당 보드 파일 1개 지원.

### Starting from a schematic · #starting_from_a_schematic

- **스키매틱에서 보드 생성이 KiCad 권장 워크플로**. 새 프로젝트 생성 시 KiCad는 프로젝트와 같은 이름의 빈 보드 파일을 생성.
- 스키매틱 작성 후 보드 설계 시작: 보드 파일을 열기만 하면 됨(KiCad 프로젝트 매니저에서, 또는 스키매틱 에디터의 "Open PCB in board editor" 버튼).
- 스키매틱 설계 정보(풋프린트·넷 연결)를 보드 에디터로 import: **Tools** → **Update PCB from Schematic…​** 액션(`F8`). top toolbar의 Update pcb from schematic 아이콘도 가능.
- ⚠️ Update PCB from Schematic이 스키매틱→PCB 정보 전송의 선호 방식. 구버전 KiCad는 넷리스트를 export/import했으나 더 이상 넷리스트 파일이 필요 없다.
- Update Schematic from PCB 도구(역방향 어노테이션)는 매뉴얼의 forward annotation 섹션 참조.

### Starting from scratch · #starting-from-scratch

- 대응 스키매틱 없이 보드 생성도 가능하나 제한이 있고 대부분 사용자에게 비권장.
- 방법: PCB 에디터를 standalone(KiCad 프로젝트 매니저가 아닌)으로 실행. 설계 시작 전 보드 파일을 저장하는 것이 좋음(이때 board settings를 저장할 project 파일도 생성됨).
- File 메뉴 "Save As…​"로 보드 파일 저장 위치 선택 → 같은 위치에 같은 이름의 project 파일 생성.

## Board setup · #board_setup

- 보드 설계 시작 전 Board Setup 다이얼로그로 기본 파라미터 설정.
- 열기: top toolbar의 options board 아이콘 클릭, 또는 File 메뉴 → "Board Setup…​".

### Configuring board stackup and physical parameters · #board-setup-stackup

- Board Stackup 섹션은 보드의 스택업과 레이어를 설정.

#### Board editor layers · #board_editor_layers

- Board Editor Layers 페이지: 레이어 이름 변경, 사용 안 할 non-copper 레이어 비활성화, 문서화 등을 위한 사용자 정의 레이어 추가.
  - 예: back silkscreen 미사용 시 `B.Silkscreen` 레이어 옆 박스 uncheck.
  - copper layers, courtyard layers, `Edge.Cuts`는 필수 레이어라 비활성화 불가.
- ⚠️ copper layer를 signal / power plane / mixed / jumper로 지정 가능 — 단 사용자 가이드용일 뿐. 트랙·존은 타입과 무관하게 어떤 copper layer에든 라우팅 가능.
- 사용자 정의 레이어(`User.1`, `User.2` 등)는 우상단 **Add User Defined Layer…​** 버튼으로 추가. 라우팅 불가, 임의 그래픽/정보 포함 가능.
  - 기본은 **auxiliary** 레이어(front/back 어느 쪽에도 대응 안 함). **Off-board, front** 또는 **Off-board, back**으로 설정하면 해당 면에 대응하며 객체를 front↔back으로 flip 가능.
  - 인접 front/back 레이어는 paired로 취급: `User.2`가 front, `User.3`이 back이면 `User.2` 객체 flip 시 `User.3`으로 이동(역도 동일).

#### Physical stackup · #physical_stackup

- Physical Stackup 페이지: PCB layer 스택업에 포함되는 보드 레이어(copper, dielectric, solder mask, silkscreen) 제어.
- 💡 비물리 레이어 추가, 모든 레이어 이름 설정, 선택 레이어 활성/비활성은 **Board Editor Layers** 페이지에서 한다.
- 좌상단에서 copper layer 수 설정 후, 원하면 스택업의 물리 파라미터 입력. 기본값 유지 가능하나 주의:
  - board thickness 값은 보드 3D 모델 export 시 사용됨
  - layer thickness는 via를 포함하는 넷의 net length 계산에 포함됨
  - 이 기능 사용 계획 시 스택업 두께를 정확히 맞추는 것이 좋음
- Dielectric/soldermask/silkscreen 레이어에 색 할당 가능(3D 뷰어·3D 모델 export의 보드 외관에 영향).
- ⚠️ KiCad는 현재 짝수 copper layer 스택업만 지원. 홀수 레이어 설계(예: 플렉시블 PCB, 메탈코어 PCB)는 다음 짝수로 선택하고 여분 레이어를 무시.
- 페이지 하단 **Board thickness from stackup** 값은 테이블의 스택업 파라미터로 자동 계산.
- **Adjust Dielectric Thickness** 버튼 + 전체 두께 입력 → dielectric 레이어 두께를 전체 PCB 두께에 맞게 자동 조정. locked(locked 컬럼 체크) dielectric 레이어는 조정되지 않음.

#### Board finish · #board_finish

- Board Finish 섹션: copper finish 정의, castellations나 edge plating 같은 특수 기능 설정.
- ⚠️ 이 설정은 현재 Gerber job 파일의 board attributes 출력에만 영향.

#### Solder mask/paste · #solder_maskpaste

- Solder Mask/Paste 섹션: solder mask/paste 형상과 parent pad의 copper 형상 사이 clearance(양수/음수)를 전역 조정. 전역 설정이며 개별 풋프린트/패드의 clearance override가 우선.
  - 양수 clearance → 마스크/페이스트 개구부가 copper보다 *큼*. 음수 → *작음*.
- ⚠️ **WARNING**: 대부분 상용 PCB 팹은 이 값들이 0이길 기대하고 CAM 과정에서 자체 조정한다. 본인이 직접 제작하거나 팹의 구체적 조언이 없으면 기본값 0으로 두는 것이 보통 최선.
- 주요 설정:

| 설정 | 의미 |
| --- | --- |
| **Solder mask expansion** | parent pad 대비 마스크 개구부 크기. `0`이면 패드와 동일, 양수는 더 큼, 음수는 더 작음. 개별 풋프린트/패드 expansion이 override |
| **Solder mask minimum web width** | 마스크 개구부 사이 web의 최소 폭(개구부 간 최소 거리). 이보다 가까운 개구부들은 하나로 병합되어 플롯 |
| **Solder mask to copper clearance** | 마스크 개구부와 (개구부 parent와) 다른 넷 copper 사이 최소 거리. 이보다 작으면 DRC error |
| **Allow bridged solder mask apertures between pads within footprints** | 같은 풋프린트 내 여러 패드가 하나의 마스크 개구부를 공유할 때 DRC 위반 발생 여부 제어(최소 web width로 개구부 병합 시 발생 가능) |
| **Tent vias** | 비아를 top/bottom에서 tenting(마스크로 덮음)할지. front/back 독립 제어. 개별 via가 via properties로 override |
| **Solder paste clearance** | parent pad 대비 솔더 페이스트 형상(F.Paste/B.Paste 개구부와 패드 형상의 크기차). 절대 오프셋(`-0.1mm`), 패드 치수 상대값(`-5%`), 또는 둘 다(`-0.1mm - 5%`) 지정. `0`/공백이면 패드와 동일. 양수는 큼, 음수는 작음. 개별 풋프린트/패드 설정이 override |

#### Zone hatch offsets · #zone_hatch_offsets

- Zone Hatch Offsets 페이지: 존 해치 패턴의 레이어별 기본 오프셋 설정. X·Y 오프셋 별도 설정.
- 레이어 간 hatching grid 오프셋을 강제(일부 응용에서 필요). 개별 존은 zone Properties 다이얼로그에서 override 가능.

### Configuring text and graphics · #configuring_text_and_graphics

- Text & Graphics 섹션: text 객체·graphic shape·dimension 객체의 포맷 설정 + 프로젝트 text variables 설정.

#### Defaults · #board-setup-defaults

- Defaults 섹션: 보드에 새로 배치되는 text/graphic shape에 사용될 속성 설정.
- Line thickness, text size, text appearance를 다이얼로그의 6개 레이어 카테고리별로 설정. 새 객체의 레이어에 따라 자동 적용. 객체 속성에서 per-object override 가능.
- dimension 객체의 기본 속성은 모든 레이어에 대해 설정 가능(자세한 내용은 dimensions 섹션).
- Defaults 페이지에는 신규 zone의 기본 설정도 포함(새 존에 적용, per-zone override 가능).

#### Formatting · #formatting

- Formatting 섹션: 특정 보드 아이템 포맷 제어.
- **Dashed Line** 섹션: 점선 외관 제어. **Dash length**(대시 길이), **Gap length**(대시/도트 간 간격). 길이는 line width 상대값 — gap length `2`는 line width의 2배.
- 페이지 하단 체크박스들은 **Defaults** 페이지 설정을 보드에 추가되는 풋프린트에 자동 적용하는 방식 제어:
  - **Apply board defaults to footprint fields**: 풋프린트 fields에 기본 설정 적용
  - **Apply board defaults to footprint text**: 풋프린트 text 객체에 적용
  - **Apply board defaults to non-copper footprint shapes**: 풋프린트 non-copper 레이어 그래픽 shape에 적용(copper 레이어 shape은 미변경)
  - **Apply board defaults to footprint dimensions**: 풋프린트 dimensions에 적용
  - **Apply board defaults to footprint barcodes**: 풋프린트 barcodes에 적용

#### Text variables · #board-setup-text-variables

- Text Variables 섹션: 프로젝트 text variable 생성. KiCad는 변수명을 할당된 텍스트 문자열로 치환. 치환 구문 `${VARIABLENAME}`이 쓰인 모든 곳에서 발생.
- 예: `VERSION` 변수를 `1.0`으로 설정 → PCB의 text 객체에 `${VERSION}` 입력 시 `1.0`으로 표시. 값을 `2.0`으로 바꾸면 모든 `${VERSION}` 텍스트 자동 갱신. 일반 텍스트와 혼합 가능(`Version: ${VERSION}` → `Version: 1.0`).
- text variable은 Schematic Setup에서도 생성 가능. 프로젝트 전역이라 스키매틱에서 만든 변수는 보드에서도, 반대로도 사용 가능.
- 내장 system text variable도 다수 존재.

### Configuring design rules · #configuring_design_rules

- 디자인 룰은 인터랙티브 라우터 동작, copper zone fill, design rule checker를 제어. 언제든 수정 가능하나, 보드 설계 시작 시점에 알려진 모든 룰을 확립할 것을 권장.

#### Constraints · #board-setup-constraints

- 기본 디자인 룰은 Constraints 섹션에서 설정. 보드 전체에 적용되며 보드 제조사 권장값으로 설정.
- ⚠️ 여기 설정한 최소값은 *절대* 최소이며 더 구체적인 디자인 룰로도 override 불가. 예: 보드 일부는 0.2mm, 나머지는 0.3mm clearance가 필요하면 — Constraints의 minimum copper clearance에 0.2mm를 넣고, net class나 custom rule로 더 큰 0.3mm를 설정.
- 추가 기능:

| 설정 | 설명 |
| --- | --- |
| **Arc/circle approximated by segments** | 원형 형상(arc/circle)을 직선 세그먼트로 근사할 때 허용되는 최대 오차(세그먼트 위 점과 실제 곡선 간 최대 거리). 기본 0.005mm보다 낮추면 매끄럽지만 큰 보드에서 매우 느릴 수 있음. 기본값은 제조 공차로 인해 실제 보드에서 감지되지 않는 수준 |
| **Allow fillets outside zone outline** | 존은 Zone Properties에서 fillet(둥근 모서리) 추가 가능. 기본적으로 fillet 포함 어떤 존 copper도 존 외곽선 밖 불허(→ 내측 코너는 fillet 설정해도 fillet 안 됨). 활성 시 내측 코너가 fillet되며 copper가 외곽선 밖으로 확장 |
| **Minimum thermal relief spoke count** | 패드를 존에 연결하는 thermal relief spoke의 최소 허용 개수. 위반 시 DRC 위반 생성 |
| **Include stackup height in track length calculations** | 기본적으로 length tuner는 via로 레이어를 이동하는 트랙의 추가 길이를 스택업 높이로 계산(스택업 높이 정확 설정 의존). 비활성 시 length tuner 길이 계산에서 via 길이 제외(via가 길이를 추가하지 않는 것으로 간주) |

#### Pre-defined sizes · #board-setup-pre-defined-sizes

- Pre-defined Sizes 섹션: 라우팅 중 사용할 트랙·비아 치수 정의. net class로 넷별 기본 치수를 정할 수 있지만(아래), 여기서 사이즈 목록을 정의하면 라우팅 중 이 사이즈들을 step through 가능.
- 예: 기본 트랙 폭 0.2mm, 전류 큰 구간 0.3mm, 공간 제한 구간 0.15mm를 정의해두고 라우팅 중 전환.

#### Teardrops · #board-setup-teardrops

- Teardrops 섹션: 다양한 티어드롭 타입의 기본 파라미터 설정. round 객체 연결, rectangular 객체 연결, 트랙 간 연결별로 다른 설정. 티어드롭 추가 시 또는 개별 연결 아이템 속성에서 override 가능. 각 설정은 teardrops 문서 참조.

#### Length-tuning patterns · #length_tuning_patterns

- Length-tuning patterns 섹션: 길이 튜닝 패턴 타입별(single-track length, differential-pair length, differential-pair skew) 기본 파라미터 설정. 보드에 추가된 각 튜닝 패턴 속성에서 override 가능. length tuning 문서 참조.

#### Tuning profiles · #tuning_profiles

- Tuning profiles: 특정 임피던스 요구가 있는 single-ended·differential 트랙의 레이어별 라우팅 파라미터 정의. 보드 스택업과 목표 신호 임피던스로 트랙 폭·gap을 자동 계산 가능.
- net class에 할당하면 인터랙티브 라우터가 해당 값 사용. DRC가 튜닝 프로파일 파라미터와 불일치하는 트랙에 대해 옵션으로 위반 생성 가능.
- 추가: small plus 버튼. 이름 지정 필수, **Single**(단일 트랙) / **Differential**(차동) 선택. **Target impedance**는 선택이나 트랙 geometry 계산에 필수.
  - **Enable time domain tuning** 체크 시 length tuner가 이 프로파일 할당 트랙을 time domain tuning으로 처리, 미체크 시 track length 기준으로 튜닝.
- **Track Propagation** 섹션: 레이어별 트랙 geometry와 전파 지연 정의. 각 행 = 다른 레이어의 트랙. 테이블 아래 small plus로 행 추가, small trash로 제거.
  - 각 행: **Signal Layer**, **Bottom Reference** 레이어, 선택적 **Top Reference** 레이어(stripline geometry용). **Track Width**, **Unit Delay** 값, 차동 페어는 추가로 **Diff Pair Gap**.
  - width/gap/delay를 수동 입력(외부 도구 계산), 또는 각 필드의 small refresh 버튼으로 자동 계산. width/gap은 target impedance와 신호↔레퍼런스 레이어 간 스택업 두께로 계산. 차동 페어는 width·gap 중 최소 하나는 수동 입력하고 나머지를 계산. delay는 트랙 geometry로 계산. 계산기는 레퍼런스 레이어가 1개면 microstrip, 2개면 stripline geometry 가정. 계산기 사용에는 프로파일의 **Target Impedance** 입력과 보드 스택업 설정 필요.
- **Via Propagation** 섹션: 비아의 전파 지연 정의. **Global unit delay**는 비아의 일반 단위거리당 전파 지연. 아래 테이블에서 개별 layer pair override 추가 가능.
  - 각 행: **Signal Layer From/To**(신호 트랙이 비아에 연결되는 레이어), **Via Layer From/To**(전체 via 구조의 시작·끝 레이어). Through via는 보드 top/bottom에서 시작·끝. 다른 비아 타입은 inner layer에서 시작/끝 가능.
  - 각 override에 **Delay** 값으로 그 via 타입의 전파 지연 지정.
- 프로파일 전체 삭제: 페이지 하단 small trash 버튼.
- 사용: 튜닝 프로파일을 net class에 할당하면 인터랙티브 라우터가 그 net class 트랙에 프로파일의 width·diff pair gap을 net class 값으로 사용, length tuner는 전파 지연을 time-domain 튜닝에 사용, DRC는 옵션으로 geometry 불일치 위반 생성.
- net class에 할당: Board Setup의 **Net Classes** 페이지 → 해당 net class의 **Tuning Profile** 컬럼에서 프로파일 선택(컬럼이 안 보이면 테이블 스크롤 또는 컬럼 숨김 해제).

##### When to enable time-domain tuning · #when_to_enable_time_domain_tuning

- **Enable time domain tuning** 체크박스: length tuner를 time-domain 모드(전파 지연 매칭)와 length-domain 모드(물리 트레이스 길이 매칭) 중 어느 쪽으로 동작시킬지 제어(이 프로파일 할당 넷에 대해).
- time-domain 튜닝 활성 권장 시점:
  - 매칭 넷이 전파 속도가 다른 여러 레이어에 라우팅됨(예: microstrip + stripline 혼합)
  - 설계 사양이 타이밍 버짓을 mm가 아닌 picoseconds로 정의
  - 레이어 간 비아 전환의 유전 특성 차이로 인한 지연차가 길이 매칭만으로 잡히지 않을 만큼 유의미함
- time-domain 비활성 시 프로파일은 여전히 라우터·DRC용 레이어별 트랙 geometry(width/gap)를 제공하나, length tuner는 전파 지연이 아닌 물리 길이를 매칭.
- 💡 custom DRC rule로 per-net 튜닝 모드 override 가능. time unit으로 작성된 `length`/`skew` 제약(예: `500ps`)은 프로파일 설정과 무관하게 매칭 넷에 대해 length tuner를 time-domain 모드로 강제.

##### Understanding track propagation parameters · #understanding_track_propagation_parameters

- **Track Propagation** 테이블의 각 행 = 신호 레이어 + 레퍼런스 plane(들). 신호+레퍼런스 조합이 전송선 geometry를 결정:
  - **레퍼런스 1개**(bottom reference만): **microstrip** geometry 가정. 단일 레퍼런스 plane 위/아래에 트레이스가 있는 외부 레이어에 전형적.
  - **레퍼런스 2개**(bottom + top reference): **stripline** geometry 가정. 두 레퍼런스 plane 사이에 트레이스가 끼인 내부 레이어에 전형적.
- 유효 유전율 차이로 microstrip/stripline의 전파 속도(따라서 unit delay)가 다름. stripline은 유전체에 완전 봉입되어 유효 유전율이 높아 전파가 느림(mm당 unit delay 큼). microstrip은 공기에 일부 노출되어 전파가 빠름(unit delay 작음).
- **Unit Delay**는 단위거리당 전파 지연(예: ps/mm). 외부 임피던스 계산기로 계산해 수동 입력하거나, small refresh 자동 계산 버튼으로 KiCad가 스택업·트레이스 geometry로 계산.
- 💡 보드 스택업(레이어 두께, 유전체)을 변경한 후에는 각 delay 필드의 small refresh 버튼으로 unit delay 재계산. 스택업 변경 시 delay 값은 자동 갱신되지 않음.

##### Understanding via propagation parameters · #understanding_via_propagation_parameters

- **Via Propagation** 섹션은 time-domain 모드에서 via 지연 계산 방식 제어.
- **Global unit delay**는 모든 비아의 기본 단위거리당 전파 지연. 이 값에 via의 electrical height(신호가 실제 사용하는 레이어 간 스택업 거리, 전체 via span이 아님)를 곱해 via 지연 기여분 산출.
- 더 정밀한 제어: 글로벌 delay 필드 아래 테이블에 **per-layer-pair override** 추가. 각 override는 특정 레이어 간 via 전환의 절대 지연값 지정. override가 글로벌 unit delay 계산보다 우선.
- 각 override 행의 4개 레이어 필드:
  - **Signal Layer From** / **Signal Layer To**: 라우팅된 트랙이 비아에 연결되는 copper 레이어
  - **Via Layer From** / **Via Layer To**: 전체 via 구조의 시작·끝 레이어(예: through via는 `F.Cu`와 `B.Cu`)
- 이 4-레이어 명세로 같은 물리 via 구조라도 신호가 실제 전환하는 레이어에 따라 다른 지연 정의 가능.

##### How tuning profiles, net classes, and the length tuner work together · #how_tuning_profiles_net_classes_and_the_length_tuner_work_together

- 세 기능의 관계:
  1. *tuning profile*은 특정 임피던스 목표에 대한 레이어별 트랙 geometry와 전파 지연 파라미터 정의.
  2. *net class*는 공통 라우팅 파라미터를 공유하는 넷을 그룹화. 튜닝 프로파일을 net class에 할당하면 프로파일의 geometry·delay 값이 클래스 내 모든 넷에 적용.
  3. *length tuner*는 넷의 net class에 연결된 튜닝 프로파일을 읽음. time-domain 튜닝이 활성이면 프로파일의 레이어별 delay로 전파 지연을 계산·매칭, 비활성이면 물리 길이 매칭으로 폴백.
- 인터랙티브 라우터가 튜닝 프로파일 할당 net class의 트랙을 라우팅할 때, 현재 레이어의 트랙 폭·차동 페어 gap을 자동 사용 → 라우팅 geometry가 전파 지연 계산 가정과 일치.

#### Net classes · #board-setup-net-classes

- Net Classes 섹션: 넷 클래스별 라우팅·clearance 룰 설정.
- 한 넷에 둘 이상의 net class 할당 가능. 다중 클래스 넷은 effective aggregate net class를 형성 — 해당 속성이 설정된 최고 우선순위 net class에서 속성 취득. 우선순위는 Schematic/Board Setup 다이얼로그의 순서로 결정. `Default` net class는 모든 명시적 클래스 고려 후 누락 속성의 fallback(→ 다른 클래스를 명시 할당받아도 넷이 `Default`의 일부일 수 있음).
- net class는 Schematic 또는 Board Setup 다이얼로그에서 생성·편집 가능.
- 상단 테이블: 설계의 net class와 각 클래스에 적용되는 디자인 룰 표시. 일부 컬럼은 숨겨지거나 옆으로 스크롤될 수 있음. 테이블 헤더 우클릭으로 컬럼 표시/숨김.
- 모든 클래스는 copper clearance, track width, via sizes, differential pair sizes 값을 가짐. 더 구체적 룰이 override하지 않는 한 트랙·비아 생성에 사용(Custom Rules 참조).
- ⚠️ 어떤 룰도 Constraints 섹션의 최소값을 override 못 함. 예: net class clearance를 `0.1 mm`로 설정해도 Constraints의 Minimum Clearance가 `0.2 mm`면 그 클래스 넷의 clearance는 `0.2 mm`.
- net class의 track width·via size는 PCB 에디터의 track width/via size 컨트롤이 "use netclass values"일 때 사용 — 기본/최적 사이즈이지 최소/최대가 아님. 다른 값으로 수동 변경해도 DRC 위반 아님. 트랙 폭/비아 size를 특정 값으로 제한하려면 Custom Rules 사용.
- **Tuning Profile** 컬럼에서 net class에 튜닝 프로파일 할당 → 레이어별 트랙 geometry(트랙 폭·차동 페어 gap)와 트랙·비아 전파 지연 부여. 라우터가 라우팅에 사용, length tuner가 time-domain 모드에서 전파 지연 사용. "Tuning profile track geometries" 위반 severity를 Warning/Error로 설정하면 geometry 불일치 트랙에 DRC 위반 생성.
- **PCB Color** 컬럼에서 각 net class에 색 할당. appearance panel의 넷 색 설정에 따라 ratsnest 선이나 copper 객체의 기본 색 override. **Import colors from schematic** 버튼으로 모든 net class를 스키매틱 에디터의 색으로 설정. 레이어 기본색을 쓰려면 net class 색을 transparent로.
- 하단부: pattern-based net class 할당 목록. 작업법은 Schematic Editor 문서에 설명되며 Board/Schematic Setup 양쪽에서 편집 가능.
- pattern-based 할당은 PCB 캔버스에서 직접 생성 가능: copper 트랙/존 우클릭 → **Assign netclass…​**. net class는 스키매틱에서 net class directive/label로도 할당 가능.

#### Component classes · #component-classes

- Component Classes 섹션: 컴포넌트를 컴포넌트 클래스에 자동 할당하는 룰 생성. 자동 할당 외에 Schematic Editor에서 수동 할당도 가능.
- 컴포넌트 클래스는 컴포넌트의 named grouping — 스키매틱의 심볼이나 보드의 풋프린트에 할당되며 어느 쪽으로 할당하든 심볼·대응 풋프린트 양쪽에 적용. 멀티채널 설계의 채널 그룹화, custom DRC 룰의 풋프린트 그룹화에 사용. 컴포넌트는 둘 이상의 클래스 가능.
- **Assign component class per sheet** 활성 시 스키매틱의 모든 sheet마다 컴포넌트 클래스를 생성하고 각 sheet 컴포넌트를 그 클래스에 할당.
- 룰 추가: **Add Custom Assignment** 버튼 → **Component class** 텍스트박스에 클래스명 입력 → small plus 버튼으로 조건 추가하고 메뉴에서 조건 타입 선택.
- 조건 타입:

| 조건 타입 | 매칭 기준 |
| --- | --- |
| **Reference** | 풋프린트 reference designator. 콤마 구분 다중 가능. 와일드카드 `*`(0개 이상 임의 문자), `?`(단일 문자). config 버튼으로 선택 풋프린트의 reference 사용 |
| **Footprint** | 풋프린트 library와 identifier. 와일드카드 지원. small library 버튼으로 라이브러리에서 선택 |
| **Side** | PCB 면(front/back/any) |
| **Rotation** | 풋프린트 회전 각도 |
| **Footprint Field Value** | 지정 풋프린트 field 값. field명·값 와일드카드 지원 |
| **Sheet** | 풋프린트 연결 심볼이 속한 스키매틱 sheet 이름 |
| **Custom Expression** | custom DRC rule condition clause. 예: `A.intersectsArea('some_area_name')`는 named area와 교차하는 풋프린트 매칭 |

- 한 룰에 다중 조건 추가 가능. **Match all** = 모든 조건 충족 시 할당, **Match any** = 하나라도 충족 시 할당.
- net highlight 버튼으로 룰 테스트(매칭 풋프린트를 캔버스에 하이라이트).
- 조건 삭제: 조건 옆 small trash. 룰 전체+조건 삭제: 클래스명 옆 small trash.

##### Understanding component classes · #component-class-concepts

- 컴포넌트 클래스는 하나 이상의 풋프린트에 부착되는 named label. net class(넷에 적용, clearance·track width 등 전기 특성 영향)와 달리 컴포넌트 클래스는 풋프린트에 적용, 조직화·룰 스코핑 목적.
- 흔한 용도: 멀티채널 설계 채널 정의, custom DRC 룰을 특정 컴포넌트 그룹에 스코핑, 기능·전압 도메인·열 요구 등 기준 조직화.

##### Where component classes are defined · #where_component_classes_are_defined

- 컴포넌트 클래스는 스키매틱 에디터 또는 PCB 에디터의 Board Setup에서 정의:

| 정의 방법 | 에디터 | 설명 |
| --- | --- | --- |
| rule area 내 directive label의 `Component Class` 필드 | Schematic | rule area 내 모든 심볼에 클래스 할당 |
| `Component Class` 심볼 필드 | Schematic | 개별 심볼 properties에 `Component Class` 필드 추가로 직접 할당 |
| Board Setup 할당 룰 | PCB | reference designator·풋프린트 identifier·보드 면·회전·field 값·sheet 멤버십·custom DRC 표현식 등 조건으로 풋프린트에 할당. **Board Setup** → **Design Rules** → **Component Classes** |
| 자동 sheet 기반 클래스 | PCB | Board Setup에서 **Assign component class per sheet** 활성 시 sheet마다 자동 생성·할당 |

- Schematic 정의 클래스는 **Update PCB from Schematic** 시 PCB로 전달, 보드 파일에 persist, 스키매틱 수정+PCB 업데이트 전까지 불변. PCB 정의 클래스는 Board Setup 할당 룰에서 오며 보드 상태 변경(예: 풋프린트를 반대 면으로 이동) 시마다 재평가.

##### How multiple classes combine · #how_multiple_classes_combine

- 풋프린트는 둘 이상의 컴포넌트 클래스에 속할 수 있음. 이때 모든 클래스명이 알파벳순 정렬되어 콤마 구분 목록으로 표시. 예: `Power_Stage`와 `Channel_A`에 모두 속하면 `Channel_A, Power_Stage`로 표시.
- 풋프린트 선택 후 Properties Panel 또는 status bar의 **Component Class** 필드로 클래스 확인.
- 💡 custom DRC 룰에서 `A.hasComponentClass('ClassName')`으로 풋프린트가 특정 클래스에 속하는지 테스트(다른 클래스 소속과 무관).

##### Schematic-defined and PCB-defined classes · #schematic_defined_and_pcb_defined_classes

- 컴포넌트 클래스 할당의 두 범주:
  - **Schematic-defined**: 심볼이나 directive label의 `Component Class` 필드에서 옴. **Update PCB from Schematic** 시 PCB로 전달되어 보드 파일에 persist. 스키매틱 수정+PCB 업데이트 전까지 불변.
  - **PCB-defined**: **Board Setup** → **Design Rules** → **Component Classes**의 할당 룰에서 옴. 보드 상태 변경(풋프린트 면 이동, 보드 업데이트 등)마다 재평가. per-footprint로 저장되지 않고 on demand 계산.
- 풋프린트의 effective class = 모든 schematic-defined + PCB-defined 할당의 합집합. 예: schematic-defined `Analog_Frontend`이고 Board Setup 룰이 `High_Speed`를 할당하면 → `Analog_Frontend, High_Speed`.

##### Assignment rule details · #component-class-assignment-rules

- Board Setup의 Component Classes 패널 각 할당 룰 구성:
  1. **component class name** — 매칭 풋프린트에 할당될 클래스
  2. 하나 이상의 **conditions** — 풋프린트가 충족해야 할 기준
  3. **match operator** — **Match all**(AND: 모든 조건 참) 또는 **Match any**(OR: 최소 하나 참)
- 사용 가능한 조건 타입 파라미터:

| 조건 타입 | 파라미터 |
| --- | --- |
| Reference | reference designator 콤마 구분 목록(와일드카드 `*`, `?`) |
| Footprint | library 한정 풋프린트명(와일드카드 지원) |
| Side | `Front`, `Back`, `Any` |
| Rotation | 회전 각도(degrees) 또는 `Any` |
| Footprint Field | field명과 값(둘 다 와일드카드) |
| Sheet | 스키매틱 sheet 이름 |
| Custom Expression | 임의 DRC 표현식 |

- 각 조건은 모든 풋프린트에 평가되는 DRC 표현식으로 컴파일. 내장 조건이 부족하면 Custom Expression으로 DRC 표현식 직접 지정. 내장 조건별 생성 DRC 표현식:

| 조건 타입 | 생성 DRC 표현식 |
| --- | --- |
| Reference | `A.Reference == 'R1' \|\| A.Reference == 'R2'` |
| Footprint | `A.Library_Link == 'Resistor_SMD:R_0402_1005Metric'` |
| Side | `A.Layer == 'F.Cu'` 또는 `A.Layer == 'B.Cu'` |
| Rotation | `A.Orientation == 90 deg` |
| Footprint Field | `A.getField('Voltage') == '3.3V'` |
| Sheet | `A.memberOfSheet('SheetName')` |

- **Match all**은 `&&`(AND), **Match any**는 `||`(OR)로 조인.

##### Assignment rule examples · #assignment_rule_examples

- **예1 — reference designator로 할당**: bypass capacitor(C1, C2, C3)를 `Bypass_Caps`로. Component class: `Bypass_Caps`, Condition: Reference = `C1,C2,C3`.
- **예2 — 풋프린트 와일드카드**: 0402 저항을 `Small_Passives`로. Footprint = `Resistor_SMD:R_0402*`.
- **예3 — 보드 면+회전**: back 면 90도 회전 컴포넌트를 `Back_Rotated`로. Match all, Side = `Back`, Rotation = `90`.
- **예4 — 풋프린트 field 값**: `Voltage` field가 `3.3V`인 컴포넌트를 `3V3_Domain`으로. Footprint Field = (Field name: `Voltage`, Value: `3.3V`).
- **예5 — sheet 멤버십**: 특정 계층 sheet 컴포넌트를 `ADC_Channel`로. Sheet = `/ADC`.
- **예6 — custom DRC 표현식**: named rule area와 교차하는 풋프린트를 `Critical_Region`으로. Custom Expression = `A.intersectsArea('high_density_zone')`.

##### How classes update · #how_classes_update

- **Update PCB from Schematic**(**Tools** → **Update PCB from Schematic…​** 또는 `F8`) 실행 시 컴포넌트 클래스가 스키매틱→PCB로 재전달. 각 풋프린트에서 스키매틱에서 삭제된 클래스는 제거, 새 클래스는 추가. 각 풋프린트의 schematic-defined 할당은 Board Setup의 PCB-defined 할당과 결합되어 effective 컴포넌트 클래스 형성.
- 💡 PCB 에디터 풋프린트의 **Component Class** 필드는 read-only. schematic-defined + PCB-defined 결합 반영. schematic-defined 클래스 변경은 스키매틱에서 대응 심볼 편집 후 PCB 업데이트.

##### Using component classes in custom DRC rules · #component-classes-in-drc

- 컴포넌트 클래스를 custom 디자인 룰에서 참조해 제약을 특정 컴포넌트 그룹에 스코핑. 주 메커니즘: `hasComponentClass()` 표현식 함수(풋프린트가 named 클래스에 속하면 true). 그래픽 디자인 룰 에디터로도 컴포넌트 클래스 참조 룰 생성 가능.
- 예 — `Power_Stage` 클래스 풋프린트의 모든 아이템에 최소 clearance 강제:

```
(rule "Power component clearance"
    (condition "A.hasComponentClass('Power_Stage')")
    (constraint clearance (min 0.3mm))
)
```

- 예 — 두 컴포넌트 클래스 간 courtyard clearance 강제:

```
(rule "Keep analog away from digital"
    (condition "A.hasComponentClass('Analog') && B.hasComponentClass('Digital')")
    (constraint courtyard_clearance (min 2mm))
)
```

- 전체 표현식 언어 레퍼런스·예제는 Custom Design Rules 참조.

#### Custom rules · #custom_rules

- Custom Rules 섹션: custom rules 언어로 디자인 룰을 작성하는 텍스트 에디터. 기본 constraints나 net class 설정으로 다루지 못하는 특정 DRC를 생성.
- custom rule은 정의에 에러가 없을 때만 적용. **Check Rule Syntax** 버튼으로 정의를 테스트하고 Board Setup 닫기 전 문제 수정.
- custom rules 언어와 예제 룰은 Advanced Topics 챕터의 Custom Design Rules 참조.

#### Violation severity · #board-setup-violation-severity

- Violation Severity 섹션: 각 DRC 검사 타입의 severity 설정. 각 룰을 error marker / warning marker / no marker(ignored)로 설정 가능.
- ⚠️ 개별 룰 위반은 Design Rule Checker에서 무시 가능. Violation Severity에서 룰을 Ignore로 설정하면 해당 디자인 룰 검사 자체가 완전 비활성화 — 주의해서 사용.
- 각 위반 타입 설명과 전체 비활성 없이 개별 위반 무시하는 법은 DRC 문서 참조.

### Embedding files · #pcb-embedding-files

- 외부 파일을 보드 파일 내에 임베딩 가능 — 파일 복사본을 보드 파일 안에 저장. 외부 파일 대신 임베딩 복사본을 참조하여 외부 파일 의존을 없애 프로젝트가 portable해짐.
- 임베딩 가능·사용 대상: Fonts, datasheets, drawing sheets, SPICE models, footprint 3D models. 기타 임의 파일도 보관/export용으로 임베딩 가능하나 KiCad 기능엔 미사용. 파일은 압축 후 임베딩되지만 보드 파일 크기는 증가.
- 관리: Board Setup의 Embedded Files 섹션. 임베딩: small folder 버튼 → 파일 선택. 임베딩 후 *embedded reference*(`kicad-embed://`로 시작하는 고유 식별자)와 함께 목록에 표시. 이 reference를 외부 파일 경로처럼 Board Editor 다른 곳에서 사용 가능. 우클릭 → **Copy Embedded Reference**로 복사. 제거: small trash 버튼(남은 링크는 무효화).
- 💡 3D 모델·drawing sheet는 풋프린트(3D 모델)/보드(drawing sheet)에 추가 시 파일 브라우저의 **Embed Files** 옵션 활성화로 직접 임베딩 가능(Board Setup 추가 후 reference 참조와 결과 동일한 단축).
- **Embed fonts** 체크박스: 보드에 쓰인 모든 폰트 임베딩 → 폰트 미설치 컴퓨터에서도 해당 폰트 텍스트 편집 가능.
- 풋프린트에도 파일 임베딩 가능(보드의 풋프린트 복사본 또는 라이브러리). 그 파일은 해당 풋프린트 인스턴스 내에서만 사용 가능. 풋프린트 임베딩 파일은 보드 추가 시 dedup — 같은 파일을 임베딩한 풋프린트 다중 인스턴스라도 복사본 1개만 임베딩되고 모든 인스턴스가 공유.
- 예: 여러 풋프린트에서 쓸 3D 모델을 프로젝트에 임베딩 — Board Setup으로 모델 임베딩 후 internal reference 복사하여 각 풋프린트의 3D 모델 경로로 붙여넣기. 또는 단일 풋프린트(보드 또는 소스 라이브러리)에 임베딩(이 경우 풋프린트 export 시 portable, 임베딩은 풋프린트 properties에서 관리). 더 편한 방법: 풋프린트 properties 다이얼로그에서 3D 모델 추가 시 파일 브라우저의 **Embed File** 옵션 활성화.
- 💡 보드의 모든 풋프린트 3D 모델을 한 번에 임베딩: **Tools** → **Collect and Embed 3D Models**. 보드 풋프린트가 참조하는 모든 외부 3D 모델을 보드에 임베딩하고 각 풋프린트의 참조를 임베딩 파일 참조로 교체.
- 스키매틱에도 파일 임베딩 가능.

### Importing settings · #importing_settings

- 기존 보드에서 board setup의 일부 또는 전부를 import 가능. 원하는 설정을 가진 "template" 보드를 만들어두고 새 보드마다 수동 입력 대신 import.
- 💡 특정 보드에서 설정을 자주 import한다면 그 설계로 template project를 만드는 것을 고려.
- 방법: Board Setup 다이얼로그 하단 **Import Settings from Another Board…​** 버튼 → 가져올 `kicad_pcb` 파일 선택 → 가져올 설정 선택(현재 설정은 선택한 보드 값으로 덮어쓰기).
- import 가능 설정:
  - Board layers and physical stackup
  - Solder mask/paste defaults
  - Zone hatched fill offsets
  - Text and graphics default properties
  - Text & graphics formatting
  - Design rule constraints
  - Predefined track & via dimensions
  - Teardrop defaults
  - Length-tuning pattern defaults
  - Net classes
  - Component classes
  - Tuning Profiles
  - Custom rules
  - Violation severities
