# PCB 에디터 ④ — 풋프린트·라이브러리·멀티채널·디자인블록 — KiCad 10.0 사용 다이제스트

> **원문**: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html

> **범위**: 풋프린트 라이브러리 관리/브라우징, 풋프린트 에디터 개요, 풋프린트 생성/편집(패드·그래픽/텍스트·필드·레이어·clearance override·net tie/jumper·3D 모델·임베딩·rule area·wizard·체크), 멀티채널 레이아웃(스키매틱/보드 절차·토폴로지 매칭·라우팅 복제·트러블슈팅), 디자인 블록

> 한국어 요약 다이제스트. 섹션 제목의 #anchor로 원문 핀포인트: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#<anchor>

## 목차

**풋프린트 & 라이브러리**
- [Footprints and footprint libraries](#footprints_and_footprint_libraries) — 풋프린트=라이브러리 닉네임+이름 식별자 개념
- [Managing footprint libraries](#managing-footprint-libraries) — global/project fp-lib-table, 지원 포맷, 중첩 테이블
- [Initial configuration](#initial_configuration) — 첫 실행 설정·Reset Libraries
- [Managing table entries](#managing_table_entries) — 추가/제거/활성화/닉네임 규칙
- [Nested library tables](#nested-library-tables) — 중첩 라이브러리 테이블
- [Path variable substitution](#fp-path-variable-substitution) — `${PATH_VAR}`·`${KIPRJMOD}`
- [Using the GitHub plugin](#using_the_github_plugin) — 6.0에서 제거됨
- [Migrating footprint libraries to KiCad format](#migrating-footprint-libraries) — Migrate Libraries 변환
- [Browsing footprint libraries](#browsing_footprint_libraries) — Footprint Library Browser 툴바

**풋프린트 생성/편집**
- [Creating and editing footprints](#creating-and-editing-footprints) — 풋프린트 구성요소 개요
- [Footprint editor overview](#footprint_editor_overview) — 에디터 실행·창 구성
- [Top toolbar](#top_toolbar) / [Left toolbar display controls](#left_toolbar_display_controls) / [Right toolbar tools](#right_toolbar_tools)
- [Browsing, modifying, and saving footprints](#browsing_modifying_and_saving_footprints) — 저장·Save As·Export·보드 사본 편집
- [Creating a new footprint library](#creating_a_new_footprint_library) — `.pretty` 폴더 생성
- [Creating a new footprint](#creating_a_new_footprint) — 신규 풋프린트·기본 필드·anchor
- [Editing footprint properties](#footprint-editor-properties) — General 탭 속성·attribute
- [Footprint pads](#fp-pads) — 패드 추가·도구
- [Editing pad properties](#footprint-pad-properties) — pad type·copper/technical layer·padstack·shape·fab properties
- [Pad connections](#pad-connections) — teardrop·zone·thermal relief
- [Pad clearance overrides](#pad-clearance-overrides) — pad clearance·mask/paste 확장
- [Pad post-machining and backdrilling](#pad-post-machining-and-backdrilling)
- [Custom pad shapes](#custom-pad-shapes) — Pad Edit Mode
- [Default pad properties](#default-pad-properties) / [Renumbering pads](#renumbering-pads) / [Pad table](#pad-table) / [Pad arrays](#pad-arrays)
- [Footprint graphics and text](#fp-graphical-objects) — courtyard·Edge.Cuts·그래픽 도구
- [Bulk editing footprint text and graphics](#bulk_editing_footprint_text_and_graphics) / [Cleaning up footprint graphics](#cleaning_up_footprint_graphics)
- [Footprint fields](#fp-fields) — 명명된 필드 vs 텍스트
- [Footprint layers](#fp-layers) / [Private footprint layers](#private_footprint_layers)
- [Clearance overrides](#fp-clearance-overrides) / [Clearance override hierarchy](#clearance_override_hierarchy)
- [Pad connections, net ties, and jumper pads](#fp-pad-connections) / [Net ties](#net-ties) / [Jumper pads](#fp-jumper-pads)
- [3D models](#fp-3d-models) / [Embedding files](#fp-embedding-files)
- [Rule areas](#fp-rule-areas) / [Reference images](#fp-reference-images)
- [Footprint wizards](#footprint-wizards) / [Checking footprints](#checking-footprints)

**멀티채널 레이아웃**
- [Multichannel layout](#multichannel) — 반복 회로 블록 배치/라우팅 복제 개요
- [Multichannel design procedure: schematic](#multichannel-schematic) — 채널 정의·등가성
- [Multichannel design procedure: board](#multichannel-board) — placement rule area 설정
- [Generating placement rule areas](#multichannel-generate-rule-areas) / [Repeating the layout](#multichannel-repeat-layout)
- [Target rule area table](#multichannel-repeat-layout-dialog) / [Repeat layout options](#repeat_layout_options)
- [Topology matching](#multichannel-topology-matching) / [How components are matched](#how_components_are_matched) / [Tie-breaking](#tie_breaking_for_identical_components) / [Mismatch error details](#mismatch_error_details)
- [Routing duplication details](#multichannel-routing-duplication) / [What is copied](#what_is_copied) / [Net reassignment](#net_reassignment) / [Existing target routing](#existing_target_routing) / [Layer considerations](#layer_considerations) / [When routing duplication fails](#when_routing_duplication_fails)
- [Other item duplication](#multichannel-other-items) / [Step-by-step multichannel workflow](#multichannel-step-by-step)
- [Troubleshooting multichannel layouts](#multichannel-troubleshooting) 및 하위 트러블슈팅 섹션

**디자인 블록**
- [Design blocks](#pcb-design-blocks) — 회로/레이아웃 조각 재사용
- [Creating and managing design blocks](#creating-and-managing-design-blocks) / [Creating a new design block library](#creating_a_new_design_block_library) / [Creating a new design block](#creating_a_new_design_block) / [Updating an existing design block](#updating-an-existing-design-block)
- [Using design blocks in a board](#using-pcb-design-blocks) / [Directly placing design blocks in a board](#directly_placing_design_blocks_in_a_board) / [Applying layouts to design blocks from a schematic](#applying_layouts_to_design_blocks_from_a_schematic) / [Grouped design blocks](#grouped-design-blocks)

---

# 풋프린트와 풋프린트 라이브러리

## Footprints and footprint libraries · #footprints_and_footprint_libraries

- KiCad는 풋프린트를 **footprint library**(풋프린트 모음)로 조직한다.
- 보드 내 각 풋프린트는 **라이브러리 닉네임 + 풋프린트 이름** 조합인 전체 이름으로 고유 식별된다. 예: `Capacitor_SMD:C_0603_1608Metric` = `Capacitor_SMD` 라이브러리의 `C_0603_1608Metric` 풋프린트.

## Managing footprint libraries · #managing-footprint-libraries

- 풋프린트 라이브러리를 닉네임에 매핑하는 **library table**을 사용. global 테이블 + project별 테이블이 있으며, 테이블에 포함되지 않은 라이브러리는 로드되지 않는다.
- 편집: **Preferences** → **Manage Footprint Libraries…​**.
- **Global** 테이블: 현재 프로젝트와 무관하게 항상 사용 가능. KiCad config 폴더의 `fp-lib-table` 파일에 저장(위치는 OS별 상이).
- **Project specific** 테이블: 현재 프로젝트에서만 사용 가능. 프로젝트 폴더의 `fp-lib-table` 파일에 저장(프로젝트별 라이브러리가 있을 때).
- 많은(또는 전체) 라이브러리는 중첩 테이블(nested library table)에 담길 수 있다. 중첩 테이블 항목 옆 (small new window) 버튼을 누르면 새 탭에서 펼쳐 본다.
- **직접 사용 가능한 라이브러리 포맷** (비-KiCad EDA 네이티브 포맷 포함):

| 포맷 | 설명 |
| --- | --- |
| KiCad `.pretty` | `.pretty` 확장자 폴더, 내부에 `.kicad_mod` 파일 |
| KiCad Legacy | `.mod` 파일 |
| Altium Designer | `.PcbLib` 또는 `.IntLib` |
| CADSTAR PCB Archive | `.cpa` |
| Eagle | `.lbr` |
| EasyEDA / JLCEDA Standard | `.json` 또는 `.zip` |
| EasyEDA / JLCEDA Professional | `.elibz`, `.epro`, `.zip` |
| GEDA | `.fp` 파일을 담은 폴더 |

- 비-KiCad 라이브러리(Legacy 포함)는 **Migrate Libraries** 버튼으로 KiCad `.pretty` 포맷으로 변환 가능.
- ⚠️ **NOTE**: KiCad는 네이티브 `.pretty` 포맷(및 내부 `.kicad_mod`)에만 쓰기 지원. 다른 모든 포맷은 **read-only** — 수정하려면 먼저 KiCad 포맷으로 변환해야 한다.
- 라이브러리 테이블은 다른 테이블(*nested* library table)을 포함할 수 있으며, 중첩 테이블 안의 라이브러리는 메인 테이블에 직접 들어있는 것처럼 로드된다.

### Initial configuration · #initial_configuration

- 첫 실행(또는 config 없음) 시 KiCad가 새 config 생성 또는 이전 버전 import를 안내(풋프린트 라이브러리 테이블 설정 포함). 자세한 내용은 Project Manager 문서.
- 풋프린트 라이브러리 테이블 다이얼로그의 **Reset Libraries** 버튼으로 기본값 복원 가능.
- ⚠️ **WARNING**: Reset은 디스크의 풋프린트 라이브러리 테이블을 영구적으로 변경한다.
- 기본 테이블은 단일 항목 = KiCad 기본 라이브러리 전체를 담은 중첩 테이블을 가리킴. 이 중첩 테이블은 KiCad/라이브러리와 함께 업데이트되므로 직접 편집하지 말 것.
- 💡 **NOTE**: 기본 라이브러리가 중첩 테이블로 포함되므로, 개인 라이브러리 설정에 영향 없이 KiCad 버전 간 기본 라이브러리 목록을 업데이트 받을 수 있다.

### Managing table entries · #managing_table_entries

- 라이브러리는 global/project 테이블(또는 그 중첩 테이블)에 추가되어야만 사용 가능.
- **추가**: (Folder) 버튼으로 라이브러리 선택, 또는 (Plus) 버튼으로 경로 직접 입력 → 현재 열린 테이블(Global/Project Specific)에 추가.
- **제거**: 항목 선택 후 (Delete) 버튼.
- **중첩 테이블 추가**: (small folder) 버튼 옆 아래쪽 화살표 → **Table** 라이브러리 타입 선택 → 테이블 파일로 이동.
- (Up)/(Down) 버튼: 테이블 내 순서 이동(단, Browser/Editor/Add Footprint 표시 순서에는 영향 없음).
- **Enable** 체크박스 해제 시 라이브러리 비활성 — 테이블에는 남지만 로드되지 않아 로딩 시간 단축.
- 범위 선택: 첫 라이브러리 클릭 후 마지막 라이브러리 `Shift`-클릭.
- **닉네임 규칙**: 동일 테이블 내 중복 불가. global/project 간 중복은 허용되며, project 테이블이 우선한다. 닉네임은 파일명/경로와 무관해도 됨. 콜론(`:`)은 닉네임/풋프린트 이름에 사용 불가(닉네임-풋프린트 구분자).
- 각 항목은 유효한 경로 필요(absolute / relative / path variable). 적절한 포맷 선택 필수. KiCad 포맷만 저장 가능, 나머지는 read-only.
- 선택적 description 필드 존재. option 필드는 현재 미사용(설정해도 효과 없음).

### Nested library tables · #nested-library-tables

- 라이브러리 테이블은 라이브러리뿐 아니라 다른 테이블(*nested* table)을 포함할 수 있고, 중첩 테이블의 라이브러리는 상위 테이블에 직접 들어있는 것처럼 로드된다.
- 용도 예: 회사 표준 라이브러리 테이블을 만들어 공유 → 각 사용자가 자신의 global 테이블에 중첩 테이블로 추가하면 표준 라이브러리 셋에 접근.
- 기본 config에서 global 테이블의 단일 항목이 KiCad 기본 라이브러리를 나열하는 중첩 테이블이며, KiCad 업데이트 시 개인 설정을 건드리지 않고 갱신된다.

### Path variable substitution · #fp-path-variable-substitution

- 풋프린트 라이브러리 테이블은 path variable 치환 지원. 구문: `${PATH_VAR_NAME}`.
- 기본 path variable 다수 정의됨(Project Manager 문서 참조). 설정: **Preferences** → **Configure Paths…​**.
- path variable을 쓰면 변수만 갱신해주면 라이브러리 위치를 옮겨도 테이블이 깨지지 않는다.
- 💡 **NOTE**: 구버전 versioned 변수는 현재 버전 대응 변수로 자동 해석된다(구 변수가 명시 정의되지 않았다면). 예: `${KICAD9_FOOTPRINT_DIR}` → `${KICAD10_FOOTPRINT_DIR}` 값으로 자동 해석.
- `${KIPRJMOD}`: 항상 현재 프로젝트 디렉토리의 절대경로로 확장되는 특수 변수. 절대경로 없이 프로젝트 폴더에 라이브러리를 둘 수 있어 프로젝트 이동 시에도 테이블 유지.

### Using the GitHub plugin · #using_the_github_plugin

- ⚠️ **NOTE**: KiCad는 버전 6.0에서 GitHub 라이브러리 플러그인 지원을 **제거**했다.

### Migrating footprint libraries to KiCad format · #migrating-footprint-libraries

- 비-KiCad 포맷(Legacy `.mod` 포함)은 read-only. 변경 저장하려면 KiCad 포맷(`.pretty` 폴더 내 `.kicad_mod`)으로 변환 필요.
- ⚠️ **NOTE**: 신버전 KiCad는 구포맷 라이브러리를 열 수 있지만, 신버전이 저장한 파일은 구버전 KiCad가 읽을 수 없다.
- **변환 절차**: 풋프린트 라이브러리 테이블에서 라이브러리 선택 → **Migrate Libraries** 버튼. 여러 개는 `Ctrl`-클릭/`Shift`-클릭으로 동시 변환. 또는 Footprint Editor에서 열어 새 라이브러리로 저장하면 한 개씩 변환 가능.

## Browsing footprint libraries · #browsing_footprint_libraries

- **Footprint Library Browser**로 라이브러리 내용을 빠르게 검토. 열기: 메인 Board Editor 툴바의 (Library viewer) 아이콘 또는 **View** → **Footprint Library Browser**.
- 절차: 좌측 패널에서 라이브러리 선택 → 두 번째 패널에 풋프린트 목록 → 이름 선택 시 풋프린트 표시.
- 풋프린트 이름 더블클릭 또는 (Insert footprint in board) 버튼으로 보드에 추가.

**Top 툴바**

| 버튼 | 기능 |
| --- | --- |
| Previous / Next footprint | 라이브러리 내 이전/다음 풋프린트 선택 |
| refresh / zoom in / out / fit | Zoom 도구 |
| 3D | 3D Viewer로 열기 |
| Add to board | 보드에 풋프린트 추가 |
| auto fit | 열 때마다 자동 zoom-to-fit |

**Left 툴바**

| 버튼 | 기능 |
| --- | --- |
| cursor | Selection 도구(기본) |
| measurement | 두 점 간 거리 인터랙티브 측정 |
| grid | 그리드 표시 on/off |
| polar coord | 상태바 좌표를 polar/Cartesian 전환 |
| unit inch/mil/mm | 좌표·치수 단위(inch/mil/mm). 클릭으로 순환, 길게 눌러 팔레트에서 직접 선택 |
| cursor crosshair | 십자선을 small/fullscreen/45도 fullscreen 전환 |
| pad number | 패드 번호 표시/숨김 |
| pad sketch | 패드를 filled/outline 표시 전환 |
| text sketch | 텍스트를 filled/outline 전환 |
| show mod edge | 그래픽을 filled/outline 전환 |

---

# Creating and editing footprints · #creating-and-editing-footprints

- 풋프린트 = 컴포넌트 패키지와 회로기판 간 물리적 인터페이스. 포함 요소:
  - **Pads**: 조립 방식 정의. 보드에서 트랙이 패드에 라우팅되고 패드는 라우터의 자석 스냅 지점이 됨. 모양/레이어 완전 커스터마이즈 가능, plated/unplated/홀 없음 가능.
  - **Graphic shapes & text**: 기술적/미적 목적. 물리(실크/마스크)·비물리 레이어에 배치. 동박(copper) 레이어에 두면 전기적 연결 형성 가능.
  - **3D models**: 기계 CAD/시각화용. 보통 외부 파일 링크지만 임베딩도 가능.
  - **Metadata**.
- 풋프린트는 라이브러리(보통 `.pretty`로 끝나는 폴더)로 조직되며, 각 풋프린트는 라이브러리 폴더 내 `.kicad_mod` 파일.

## Footprint editor overview · #footprint_editor_overview

- Footprint Editor: 라이브러리 생성, 풋프린트 추가/편집/삭제/이전(transfer), export/import 수행.
- 실행: KiCad Project Manager에서 또는 Board Editor의 **Tools** → **Footprint Editor**. 보드의 풋프린트에서 직접 열어 라이브러리 사본 또는 보드 사본을 편집할 수도 있다.
- ⚠️ **NOTE**: 라이브러리 사본 편집은 보드에 추가된 사본에 영향 없음(보드 사본을 라이브러리에서 업데이트하기 전까지). 반대로 보드 사본 편집은 라이브러리 사본/다른 보드 사본에 영향 없음.
- 창 구성: 3개 툴바 + 편집 캔버스. 좌측 collapsible 패널(footprint tree, Properties Manager), 우측(appearance panel, selection filter), 하단 message panel(선택 객체 상세).
- 💡 **NOTE**: 툴바 내용은 Footprint Editor Preferences의 **Toolbar** 페이지에서 편집 가능.

### Top toolbar · #top_toolbar

| 버튼 | 기능 |
| --- | --- |
| new footprint | 선택 라이브러리에 새 풋프린트 생성 |
| module wizard | wizard로 새 풋프린트 생성 |
| save | 현재 풋프린트 저장 |
| print | 현재 풋프린트 인쇄 |
| undo / redo | 마지막 편집 취소/재실행 |
| refresh | 화면 새로고침 |
| zoom in/out/fit/area | 확대/축소/맞춤/선택영역 맞춤 |
| rotate ccw/cw | 선택 항목 반시계/시계 회전 |
| mirror h/v | 수평/수직 미러 |
| group / ungroup | 선택 항목 그룹 추가/제거 |
| module options | 현재 풋프린트 속성 편집 |
| options pad | 선택 패드 속성 편집 |
| datasheet | 현재 풋프린트 데이터시트 열기 |
| erc (footprint checker) | footprint checker 실행(설계 오류 검사) |
| load module board | 보드의 풋프린트를 에디터에서 편집 |
| insert module board | 현재 풋프린트를 보드에 삽입 |

### Left toolbar display controls · #left_toolbar_display_controls

| 버튼 | 기능 |
| --- | --- |
| grid | 그리드 표시 on/off. **Note**: 기본적으로 그리드 숨김이 grid snapping을 끄지 않음(Preferences의 Display Options에서 변경) |
| grid override enable | item별 grid override on/off |
| polar coord | 좌표 polar/Cartesian 전환 |
| unit inch/mil/mm | 단위 전환(클릭 순환, 길게 눌러 팔레트) |
| cursor crosshair | 십자선 small/fullscreen/45도 전환 |
| line mode | 신규 zone/그래픽/dimension 배치 시 free/90도/45도 line mode 전환. `Shift`+`Space`로도 토글 |
| pad sketch | 패드 filled/outline 전환 |
| show mod edge | 그래픽 filled/outline 전환 |
| text sketch | 텍스트 filled/outline 전환 |
| contrast mode | 비활성 레이어 표시를 Normal/Dim 전환. Dim/Hide면 버튼 강조됨; Hide는 Appearance Panel 또는 `Ctrl`+`H`로만 |
| search tree | 라이브러리/풋프린트 tree 표시 토글 |
| layers manager | 우측 Appearance·Selection Filter 패널 표시/숨김 |
| tools | 좌측 Properties Manager 패널 표시/숨김 |

### Right toolbar tools · #right_toolbar_tools

| 버튼 | 기능 |
| --- | --- |
| cursor | Selection 도구(기본) |
| pad | 패드 추가: 캔버스 클릭으로 배치 |
| add keepout area | **Rule area**(구 keepout) 추가: 항목 배치·zone filling 제한, named area로 custom 룰 적용 |
| add line | 선 그리기. **Note**: 그래픽 객체이며 트랙과 다름. net 할당 불가 |
| add arc | 호 그리기: center → start → end. 우클릭으로 arc 편집 모드 변경 |
| add rectangle | 사각형(filled/outline) |
| add circle | 원(filled/outline) |
| add graphical polygon | 다각형(filled/outline). **Note**: filled zone과 다름 — net 할당 불가, clearance 미유지 |
| add bezier | 베지에 곡선: start/end + 2 control point. Backspace로 직전 점 취소 |
| image | 참조용 비트맵 이미지(제조 출력에 미포함) |
| text / add textbox / table | 텍스트 / 텍스트박스 / 테이블 추가 |
| dimensions | orthogonal/aligned/center/radial/leader dimension 추가 |
| delete cursor | 삭제 도구: 객체 클릭 삭제 |
| Anchor | Anchor 도구: 좌클릭으로 풋프린트 anchor(원점) 설정 |
| grid select axis | grid 원점 설정 |
| measurement | 두 점 거리 측정 |

## Browsing, modifying, and saving footprints · #browsing_modifying_and_saving_footprints

- (Footprint tree) 버튼: 라이브러리 목록 표시/숨김으로 active 라이브러리 선택. 새 풋프린트는 active 라이브러리에 생성됨.
- 풋프린트 이름 클릭 시 에디터에서 열림, hover 시 미리보기.
- **저장**: 현재 라이브러리에 저장은 (Save) 버튼.
- **Save As…​** (**File** → **Save As…​**): 같은/다른 라이브러리에 새 이름으로 저장.
- **Export Footprint** (**File** → **Export** → **Footprint…​**): 현재 풋프린트만 담은 단일-풋프린트 라이브러리 파일 생성.
- **보드 풋프린트 편집**: Board Editor에서 풋프린트 우클릭 → **Open in Footprint Editor** (`Ctrl`+`E`). 또는 Footprint Editor 상단 (load module board) 버튼.
- ⚠️ 보드 사본 편집/저장은 그 보드의 해당 풋프린트만 갱신 — 다른 사본·원본 라이브러리 사본 미변경. 보드 사본을 열면 info bar가 라이브러리 미수정을 경고하며, 링크로 라이브러리 버전을 열 수 있음(`Ctrl`+`Shift`+`E`).

## Creating a new footprint library · #creating_a_new_footprint_library

- **File** → **New Library…​** → 위치/이름 선택. 라이브러리는 폴더로 저장되며 폴더명 = 라이브러리명 + `.pretty` 접미사.
- 파일 브라우저에서 global / project 라이브러리 테이블 중 선택(global = 전체 프로젝트, project = 현재 프로젝트만).
- 💡 **NOTE**: 라이브러리 테이블 관리(삭제·이름변경 포함)는 **Preferences** → **Manage Footprint Libraries…​**.

## Creating a new footprint · #creating_a_new_footprint

- 생성: (New Footprint) 버튼 또는 **File** → **New Footprint…​** → 선택 라이브러리에 untitled 풋프린트 생성·열림.
- 이름 설정: 속성 다이얼로그((module options) 버튼 또는 `E`)에서. 이름은 심볼에 풋프린트 할당 시 사용되며 디스크상 파일명이기도 함.
- 신규 풋프린트의 기본 항목: 두 mandatory 필드 `Reference`(텍스트 `REF**`, 보드 추가 시 심볼의 reference designator로 치환)와 `Value`(초기 `Untitled`, 보드 추가 시 심볼 `Value`로 갱신). 추가로 `${REFERENCE}` 텍스트 변수 항목(보드에서 `Reference` 필드 값으로 해석).
- 이 항목들은 풋프린트 anchor(원점, magenta 십자)에 중심. anchor 재배치는 (Anchor) 버튼 선택 후 새 위치 클릭 — `(0, 0)` 점이 바뀜.
- 💡 **NOTE**: 일부 흔한 풋프린트는 수동 생성 대신 footprint wizard로 파라미터 기반 생성 가능.

## Editing footprint properties · #footprint-editor-properties

- 풋프린트는 텍스트 필드, attribute(예: Do Not Populate), clearance/zone connection, 3D model path 등 속성/메타데이터를 가짐. 라이브러리 사본에 초기 정의되나, 보드 추가 후 인스턴스별 개별 편집 가능(같은 풋프린트 두 사본의 속성을 따로 편집 가능).
- 텍스트 필드·attribute는 대응 심볼의 필드/attribute에서 자동 설정됨. **Update PCB From Schematic**으로 심볼→풋프린트 동기화, **Update Schematic From PCB**로 풋프린트→심볼 동기화.
- 편집: (module options) 버튼으로 Footprint Properties 다이얼로그 열기(캔버스 빈 곳 더블클릭도 가능). 핵심 설정은 **General** 탭. 다른 탭: layers, clearance overrides, pad connections(net ties·jumper), 3D models, embedded files.

**General 탭 설정**

- **Footprint name**: 라이브러리 내 이름(= 디스크 파일명, 초기엔 `Value` 필드와 동일). `Value`는 에디터에서 편집 가능하고 보드 추가 시 심볼 `Value`로 갱신됨.
- **Description**: 풋프린트 설명(사람이 읽을 용도 + 검색에 사용).
  - ⚠️ **NOTE**: 이 description 속성은 **풋프린트** 설명이며, 보드 추가 시 심볼 description으로 설정되는 `Description` *필드*와 다름.
- **keywords**: 검색용 추가 용어(풋프린트 이름·`Description`과 조합). Footprint Chooser/Editor 검색에 사용, Chooser에서 셋이 함께 표시됨.
- **Component type**: `SMD` / `Through hole` / `Unspecified`. 영향:
  - placement 파일·STEP 등 export 필터링, IPC-2581 export 메타데이터.
  - 3D viewer에서 type별 표시/숨김(예: SMD 숨기고 through hole만).
  - Board Statistics에서 type별 분리 보고.
  - DRC·footprint checker는 부모 type과 불일치 패드 보고(예: SMD 풋프린트의 through hole 패드).
- **Not in schematic** / **Exclude from position files** / **Exclude from bill of materials** / **Do not populate**: 보드 추가 시 attribute 기본 상태 설정. 링크 심볼의 attribute 값이 이를 override.
  - **not in schematic**: 심볼 대응을 기대하지 않음. Update PCB from schematic 시 보통 심볼 없는 풋프린트를 **delete footprints with no symbols** 설정에 따라 제거하지만, 이 attribute 설정 시 삭제 안 됨.
  - **exclude from POS files**: placement 파일 export에서 제외.
  - **exclude from bill of materials**: 스키매틱/PCB BOM export에서 제외. 심볼과 양방향 sync.
  - **do not populate**: 주로 심볼 attribute, 심볼과 양방향 sync. placement 파일·일부 출력에서 선택적 제외 가능, 3D viewer에서 숨김 가능.

## Footprint pads · #fp-pads

- 패드 추가: 우측 툴바 (pad) 버튼 → 캔버스 클릭. `Esc`로 취소할 때까지 클릭마다 새 패드 추가, 패드 번호는 직전 대비 +1.
- 기본 SMD/through-hole 패드 모양은 Pad Properties 다이얼로그에서 설정. 일부는 custom 모양·post-machining/backdrilling 필요.
- 다중 패드 풋프린트 보조 도구: default pad properties, pad 재번호 도구, pad table, array 도구.

### Editing pad properties · #footprint-pad-properties

- 패드 편집: 패드 속성 다이얼로그(`E`). Properties Manager로도 가능. 자주 편집하는 속성은 **General** 탭(위치·형상·레이어). 다른 탭: zone/thermal/teardrop 연결, clearance·mask/paste 확장 override, post-machining·backdrilling.

**Pad type** (활성 기능 제어)

| type | 설명 |
| --- | --- |
| **SMD** | 전기 연결, 홀 없음. 단일 동박 레이어에 존재 |
| **Through-hole** | 전기 연결, plated 홀. 홀은 전 레이어, 동박 패드는 다중 레이어(Copper layers 설정 참조) |
| **Edge Connector** | `Edge.Cuts` 보드 외곽과 겹침 허용된 SMD 패드 |
| **NPTH, Mechanical** | 비-plated through hole, 전기 연결 없음 |
| **SMD Aperture** | 홀·전기 연결 없음. 기술 레이어에 특정 디자인(paste/mask aperture) 추가용 |

- **Copper layers** (패드 형상이 존재할 동박 레이어):
  - SMD: `F.Cu` 또는 `B.Cu`(풋프린트 위치 기준 front/back). 패드가 `B.Cu`인데 풋프린트를 뒷면으로 뒤집으면 그 패드는 `F.Cu`가 됨(함께 뒤집힘).
  - Through-hole: 동박과 미연결(트랙/zone 없음) 레이어에서 패드 형상 제거 가능. **connected layers only** = 미연결 레이어에서 제거, **`F.Cu`, `B.Cu`, and connected layers** = 내부 미연결 레이어에서 제거. 고밀도 설계에서 내부 레이어 라우팅 면적 확보에 유용.
- **Technical layers** 체크박스: 패드 형상의 aperture가 추가될 기술 레이어 제어. 기본적으로 동박 레이어에 맞는 paste·mask 레이어에 aperture.
  - SMD: 패드 동박과 일치하는 외곽 레이어에 mask/paste aperture.
  - Through-hole: 기본 `F.Mask`·`B.Mask` 둘 다 mask aperture, paste aperture 없음. front/back mask·paste 독립 on/off.
  - ⚠️ **NOTE**: **Clearance Overrides** 탭의 solder mask expansion·solder paste margin 값은 패드의 활성 mask/paste 레이어 전부에 적용.
- **Pad number**: 보드에서 전기 연결 대상. 대응 심볼의 같은 번호 핀과 동일 net.
- **Position X/Y**: 풋프린트 원점 기준 패드 중심 위치.
- **Padstack mode** (레이어별 직경·홀 크기 = padstack):

| mode | 동작 |
| --- | --- |
| **Normal** | 모든 레이어 동일 직경·홀 크기 |
| **Front/Inner/Back** | front/back/inner(내부는 동일) 별도 제어. **Edit layer** 드롭다운으로 선택 |
| **Custom** | 각 레이어 완전 독립 제어. **Edit layer** 드롭다운으로 선택 |

- **Pad shape**: circular / oval / rectangular / trapezoidal / rounded rectangle / chamfered rectangle / chamfered with other corners rounded / custom (circular base) / custom (rectangular base). 모양별 옵션 존재(예: rounded rectangle = pad size X/Y, angle, corner size, corner radius).
  - 💡 **NOTE**: 캔버스에서 패드 코너 편집 핸들 드래그로 크기 조정 가능.
  - 💡 **NOTE**: 다이얼로그로 불가능한 비정형 패드는 custom pad shape 생성.
- **Hole**(Through-hole/NPTH): **hole shape** = circular/oval. 기본 패드가 홀 중심에 위치하나 **offset shape from hole** 활성 시 패드를 홀 대비 offset 가능(circular 패드는 offset 불가).
- **Fabrication properties** (주로 Gerber X2 aperture attribute 메타데이터, 일부는 DRC 영향):

| 속성 | 비고 |
| --- | --- |
| **BGA pad** | SMD 패드만, Gerber X2만 영향 |
| **Fiducial, local to footprint** / **global to board** | Gerber X2만 영향 |
| **Test point** | SMD/through hole만, 외곽 레이어만, Gerber X2만 영향 |
| **heatsink pad** | through hole이지만 SMD 풋프린트에 허용(없으면 PTH가 SMD 풋프린트에서 DRC 위반). Gerber X2 영향 |
| **castellated pad** | 보드 edge 의도적 교차(제조 시 이등분). edge 교차해도 라우팅 허용(보통은 DRC error). STEP export 시 edge로 클립. Gerber X2 영향 |
| **mechanical** | through hole을 SMD 풋프린트에 DRC 위반 없이 사용(마운팅 등). heatsink와 유사하나 Gerber X2 미영향 |
| **press-fit pad** | 솔더 없이 리드 압입용. Gerber X2만 영향 |
| **None** | 해당 없음. 효과 없음 |

- **Specify pad to die length**: 이 패드에 연관시킬 길이 → length tuning 도구·Net Inspector가 라우팅 트랙 길이에 가산. 내부 bondwire 길이 등 더 정확한 length matching에 사용.
- **Specify pad to die delay**: pad-to-die length와 유사하나 time-domain tuning용 — 라우팅 트랙 delay에 가산.

### Pad connections · #pad-connections

- 패드 속성의 **Connections** 탭: 패드가 다른 객체와 연결되는 방식(teardrop·zone·thermal relief).
- **Teardrops** 섹션: 트랙-패드 teardrop 연결 설정(teardrop 문서 참조).
- **Pad connection**: 패드의 zone 연결을 solid / thermal relief / no connection 중 선택. 개별 패드 또는 풋프린트 전체 설정 가능. 기본은 **From parent footprint**, 풋프린트 기본은 zone properties의 connection mode 사용.
- **Zone knockout**: 패드가 custom shape일 때 zone filler 동작 제어(thermal relief + custom shape 조합 시 다른 결과).
- **Relief gap**: thermal spoke 길이(패드 형상과 zone 동박 사이 gap). 보통 비워두면 연결 zone 설정 상속.
- **Spoke width**: Thermal Relief 모드 spoke 폭. 보통 비워두면 zone 설정 상속.
- ⚠️ **NOTE**: KiCad 9 이전엔 relief gap/spoke width `0`이 상속을 유발. KiCad 9+에서는 `0`이 그 값을 `0`으로 설정, **빈 값**이 상속을 유발.

### Pad clearance overrides · #pad-clearance-overrides

- **Clearance Overrides** 탭: 패드별 board clearance·mask/paste 확장 override.
- **Pad clearance**: 패드와 다른 net의 동박 형상(트랙·via·패드·zone) 간 최소 clearance. 보통 비움 → 풋프린트 clearance override, 그것도 비면 board 설계규칙·netclass 규칙 상속.
  - ⚠️ **NOTE**: KiCad 9 이전엔 `0`이 상속 유발. KiCad 9+에서는 `0`이 `0`으로 설정, 빈 값이 상속 유발.
- **Solder mask expansion**: 패드 형상과 F.Mask/B.Mask aperture 형상 간 크기 차이. 양수 = mask aperture가 동박보다 큼(전방향 inflation). 예: `0.1mm` → 사방 `0.1mm` 테두리, 축 측정 시 개구부가 `0.2mm` 더 넓음.
- **Solder paste clearance**: F.Paste/B.Paste aperture 형상 차이. absolute offset(`-0.1mm`), 상대값(`-5%`), 또는 둘 다(`-0.1mm - 5%`) 지정. `0`/빈값 = 패드와 동일 크기. 양수 = 더 큼, 음수 = 더 작음.

### Pad post-machining and backdrilling · #pad-post-machining-and-backdrilling

- 패드 속성의 **Backdrill** 탭에서 post-machining·backdrill 작업 제어. 자세한 내용은 별도 섹션(post-machining/backdrilling)에서.

### Custom pad shapes · #custom-pad-shapes

- 내장 패드 모양으로 부족할 때 **Pad Edit Mode**로 기본 패드 + 그래픽 형상을 합쳐 임의 모양 패드 구성.
- **절차**:
  1. (pad) 버튼으로 일반 패드 추가 → 이 base pad가 custom pad의 anchor/스냅 지점(트랙 부착 정확 위치에 배치). 모양/크기는 무관하나 홀은 최종 패드에 유지됨(SMD base→SMD custom, through hole base→through hole custom). custom 패드 번호는 base에서 상속.
  2. base pad 선택 → 우클릭 → **Edit Pad as Graphic Shapes** (`Ctrl`+`E`)로 Pad Edit Mode 진입 → 그래픽 형상 추가. base pad에 닿는 형상이 union됨.
  3. 종료: 우클릭 → **Finish Pad Edit** 또는 `Ctrl`+`E` 재입력. base pad에 닿는 동일 레이어 형상이 합쳐짐(through hole base는 `F.Cu` 형상이 모든 동박 레이어에 적용). 비접촉/다른 레이어 형상은 분리 유지. 편집 중 비연속 형상·다른 패드는 dim 처리.
- custom pad는 단일 base pad만 포함. base/연속 그래픽에 닿는 추가 패드(번호 동일 여부 무관)는 분리 유지.
- 💡 **NOTE**: 여러 anchor가 필요하면 같은 번호의 추가 패드를 custom pad 위에 겹쳐 배치 → 분리 유지되지만 추가 anchor로 작동, 전기적으로 연결됨.
- 기존 custom pad 수정: 선택 후 Pad Edit Mode 재진입.
- **number box**: 비정형 패드의 자동 번호 위치가 부적절할 때 사각형 추가 후 Properties Manager에서 **Number Box** 체크 → wireframe으로 표시되며 종료 시 번호 표시 영역으로 사용.
- **thermal relief template**: 보드에서 zone 연결 시 thermal spoke를 자동 추가(기본 spoke는 pad anchor에 연결). 기본 spoke 위치 override는 line shape 추가 후 Properties Manager에서 **Thermal Relief Template** 체크. template가 있으면 KiCad가 자동 spoke를 추가하지 않고 template 위치에만 spoke 배치. spoke 폭·relief gap은 여전히 pad/footprint/zone 속성으로 정의.

### Default pad properties · #default-pad-properties

- 새 패드는 **default pad properties**를 복사. 패드 편집 시마다 그 속성이 default로 저장되어 다음 새 패드가 가장 최근 편집 패드와 일치.
- 직접 편집: **Edit** → **Default Pad Properties…​**. 또는 기존 패드 우클릭 → **Copy Pad Properties to Default**.
- 기존 패드 갱신: target 패드 선택 → 우클릭 → **Paste Default Pad Properties to Selected**. 또는 선택 패드 속성을 다른 패드에 적용 **Push Default Pad Properties to Other Pads…​**.
- Push 도구 필터 옵션:

| 옵션 | 효과 |
| --- | --- |
| **do not modify pads having a different shape** | 정확히 같은 shape 속성 패드만 갱신 |
| **do not modify pads having different layers** | 같은 레이어 패드만 |
| **do not modify pads having a different orientation** | 같은 orientation 패드만 |
| **do not modify pads having a different type** | 같은 pad type 패드만 |
| (옵션 없음) | 풋프린트 내 모든 패드 갱신 |

### Renumbering pads · #renumbering-pads

- Renumber Pads 도구(**Edit** → **Renumber Pads…​**)로 빠른 재번호.
- 옵션: **first pad number**(시작 번호), **numbering step**(증가량), 선택적 **pad name prefix**(증가 부분 앞 삽입).
- **OK** 후 패드를 클릭하면 순차 번호 부여. 더블클릭으로 그 패드 재번호 후 시퀀스 종료, `Esc`로 변경 폐기.

### Pad table · #pad-table

- Pad Table((Pad table) 버튼): 풋프린트 전 패드·속성을 표 형태로 표시, bulk 편집에 유용. 셀 클릭으로 임의 속성 편집.
- 💡 **NOTE**: 헤더 행 우클릭으로 컬럼 표시/숨김 가능.

### Pad arrays · #pad-arrays

- source 패드 우클릭 → **Create from Selection** → **Create Array…​** (`Ctrl`+`T`)로 패드 배열 생성(다른 객체 배열에도 사용 가능, 패드는 추가 번호 옵션 제공).
- **Renumber pads** 활성 시 배열 생성하며 재번호. grid 배열은 numbering direction(**horizontal, then vertical** / **vertical, then horizontal**) 선택. **reverse numbering on alternate rows/columns**로 행/열마다 방향 교차.
- 시작 번호: **use first free number**(미사용 첫 번호) 또는 **pad numbering start** 값. 이후 **continuous**(1,2,3…) 또는 **coordinate** 기반(A1,A2,…,B1,…). **pad numbering skip**(step) 지정. coordinate 방식은 축별 시작/step 별도 구성. 자릿수: decimal(0-9) / hexadecimal(0-F) / 전체 알파벳 / 모호 문자(I,O,S,Q,X,Z) 제외 알파벳.

## Footprint graphics and text · #fp-graphical-objects

- 풋프린트는 그래픽 형상·텍스트·dimension 포함 가능. 비물리 레이어(`F.Fab`, `User.Drawings`) 또는 제조 레이어(`Edge.Cuts`, 실크/마스크/동박)에 배치. 동박 레이어 객체는 전기 연결 가능.
- `F.Courtyard`/`B.Courtyard`의 닫힌 형상 = front/back courtyard(풋프린트 물리적 범위, 배치 제한). courtyard 겹침 시 DRC 위반.
- `Edge.Cuts` 형상 = 그 풋프린트 포함 PCB의 보드 edge. 닫힌 형상 = cutout, 안 닫힌 형상 = unclosed edge(전체 보드에서 닫아야 함).
- **그래픽 생성 버튼 & 단축키**:

| 객체 | 단축키 |
| --- | --- |
| Lines | `Ctrl`+`Shift`+`L` |
| Arcs | `Ctrl`+`Shift`+`A` |
| Bezier curves | `Ctrl`+`Shift`+`B` |
| Rectangles | (없음) |
| Circles | `Ctrl`+`Shift`+`C` |
| Polygons | `Ctrl`+`Shift`+`P` |
| Text | `Ctrl`+`Shift`+`T` |
| Textboxes / Tables / Dimensions | (여러 dimension 타입 제공) |

- 💡 **NOTE**: 신규 텍스트/형상의 기본 스타일은 **Preferences** → **Footprint Editor** → **Default Values**에서 설정.

### Bulk editing footprint text and graphics · #bulk_editing_footprint_text_and_graphics

- **Edit Text and Graphics Properties** 다이얼로그(**Edit** → **Edit Text & Graphic Properties…​**)로 텍스트·그래픽 속성 일괄 편집. 자세한 내용은 PCB Editor 문서.

### Cleaning up footprint graphics · #cleaning_up_footprint_graphics

- 그래픽 cleanup 전용 도구(**Tools** → **Cleanup Graphics…​**):
  - **Merge lines into rectangles**: 사각형을 이루는 개별 선들을 단일 rectangle로 결합.
  - **Delete redundant graphics**: 중복/degenerate 그래픽 삭제.
  - **Merge overlapping graphics into pads**: 패드와 겹친 copper 그래픽을 custom pad로 병합.
- 변경 사항은 하단에 표시되며 **Update Footprint** 버튼을 눌러야 적용.

## Footprint fields · #fp-fields

- field = 풋프린트 관련 정보를 담는 named value. 보드 레이어에 표시되거나 숨겨질 수 있음. 일부는 특수 의미(`Reference`, `Footprint`로 심볼/풋프린트 식별). 나머지는 가격·재고 등 KiCad가 해석하지 않는 정보 가능.
- 라이브러리 풋프린트의 필드는 보드 추가 시 포함됨. 보드에서 새 필드 추가 가능, 풋프린트별 편집 가능. 심볼 필드도 보드로 전달되어 풋프린트 필드로 추가됨.
- ⚠️ **NOTE**: field ≠ graphic text. field는 이름+값(`Reference`=`R101`), text는 값만. field는 Footprint Properties에서 추가/삭제, text는 footprint editor에서만 추가. field는 심볼과 sync. KiCad 8.0 이전엔 풋프린트에 named field 없이 graphic text만 있었음.
- 모든 라이브러리 풋프린트는 4개 기본 필드(`Reference`, `Value`, `Datasheet`, `Description`)를 가지며 삭제 불가. `Reference` 초기값 `REF**`, `Value` 초기값 = 풋프린트 이름. 보드에서 4개 기본 필드 값은 대응 심볼의 일치 필드 값으로 설정.
- ⚠️ **NOTE**: `Description` *필드*는 심볼 설명이며 심볼 description으로 덮어써짐. 풋프린트에는 별도의 footprint description *속성*(필드 아님)이 있음.
- 필드는 board 레이어를 지정하는 layer를 가지며 visible/hidden 가능.
- 편집: 필드 더블클릭, 선택/hover 후 `E`, 또는 우클릭 → **Properties…​**.
- 추가/삭제/편집: (module options)로 Footprint Properties 열기. 필드 이름은 자유롭게 명명하되 `ki_`로 시작(`ki_description`)하는 이름은 KiCad 예약 — 사용자 필드에 쓰지 말 것.
- 필드 속성은 properties grid의 컬럼으로 표시(헤더 우클릭으로 컬럼 표시/숨김).

## Footprint layers · #fp-layers

- 기본 풋프린트 레이어: front copper(`F.Cu`), back copper(`B.Cu`), 모든 내부 동박을 대표하는 `Inner layers`.
- Layers 탭의 **Use custom stackup** 활성 시 **Copper layers** 드롭다운으로 정확한 동박 레이어 수 지정 → 각 레이어 커스터마이즈. 풋프린트보다 동박 레이어가 적은 보드에 추가되면 초과 레이어 항목은 무시됨.
- **User Layers** 테이블로 추가 user(비-동박) 레이어 추가. 보드에 그 레이어가 구성되어 있으면 board editor에 표시.
- 💡 **NOTE**: 풋프린트 user 레이어 개수·이름은 Footprint Editor preferences의 **User Layer Names**에서 전역 설정. 이 user 레이어는 모든 풋프린트에 개별 레이어와 함께 표시됨.

### Private footprint layers · #private_footprint_layers

- private 레이어: Footprint Editor에서 보고 편집할 수 있으나 보드 추가 시 절대 표시되지 않는 레이어. PCB Editor·제조 출력에 미포함 — 풋프린트 작업 시 참고 메모/그래픽 등에 유용.
- 기존 `User.*` 레이어(`User.Drawings`, `User.Comments`, `User.Eco1`, `User.1` 등)를 private로 설정 가능. **Layers** 탭에서 private layer 추가 후 원하는 레이어 선택.

## Clearance overrides · #fp-clearance-overrides

- Footprint properties의 **Clearance Overrides** 탭: 풋프린트별 board clearance·mask/paste 확장 override.
- **Pad clearance**: 풋프린트 패드와 다른 net 동박 형상 간 최소 clearance. 보통 비움 → board 설계규칙·netclass 규칙 상속. 개별 패드는 패드 clearance를 비-blank로 설정해 override.
  - ⚠️ **NOTE**: KiCad 9 이전 `0`=상속, KiCad 9+ `0`=`0` 설정·빈 값=상속.
- **Solder mask expansion**: 패드 형상과 F.Mask/B.Mask aperture 간 크기 차이(양수=더 큼, 전방향 inflation). 예 `0.1mm` → 사방 `0.1mm` 테두리, 개구부 `0.2mm` 넓음.
- **Solder paste clearance**: F.Paste/B.Paste aperture 차이. absolute(`-0.1mm`)/상대(`-5%`)/둘 다(`-0.1mm - 5%`). `0`/빈값=동일 크기. 양수=더 큼, 음수=더 작음.
- **exempt from courtyard requirement** 체크 시 courtyard 없어도 DRC 위반 없음. 미체크면 `F.Courtyard`/`B.Courtyard` 그래픽 없는 풋프린트는 "Footprint has no courtyard defined" DRC 위반.

### Clearance override hierarchy · #clearance_override_hierarchy

- clearance·mask expansion·paste margin은 우선순위 계층으로 해석(가장 구체적인 레벨 우선):
  1. **Pad-level override**: 개별 패드 직접 설정. 최우선, 그 패드에만.
  2. **Footprint-level override**: 풋프린트 **Clearance Overrides** 탭. 패드별 override 없는 모든 패드에.
  3. **Board-level default**: **Board Setup** → **Solder Mask/Paste**의 global 값. footprint/pad override 없는 모든 패드에.

## Pad connections, net ties, and jumper pads · #fp-pad-connections

- Footprint Properties의 **Pad Connections** 탭: 패드의 zone 연결, net tie(서로 다른 net을 short), jumper pad(컴포넌트 내부 연결) 설정.
- **Pad connection to zones**: 풋프린트 패드의 zone 연결을 solid/thermal relief/no connection. 기본 **From zone setting**(연결 zone properties의 모드 사용). 이 탭은 풋프린트 전체 override, 개별 패드는 패드 속성에서 **From parent footprint** 외 값으로 override.

### Net ties · #net-ties

- net tie: 두 개 이상의 서로 다른 net을 한 동박 영역에서 전기 연결. 보통은 net 간 clearance 위반 DRC error지만, 풋프린트를 net tie로 구성하면 위반 없이 short 가능. 다중 ground 연결, kelvin sense 연결 등에 사용.
- 각 net은 자신의 패드가 있어야 함. 패드는 보통 다른 패드와 short 불가 → short할 패드를 **net tie group**에 추가해야 함.
- **생성**: Footprint Properties **Pad Connections** 탭의 **Net Ties** 테이블에 short할 패드 번호 추가. 예: 패드 `1`·`2`를 short → `1,2` 또는 `1 2` 한 줄 추가.
- group 생성 후 지정 패드 short 허용. 패드 직접 겹침 또는 두 패드를 덮는 copper shape로 연결.
- 풋프린트는 다중 net tie group 가능. 각 group은 2개 이상 net short하되 group 간 전기적 분리 필수.

### Jumper pads · #fp-jumper-pads

- jumper pad: 풋프린트 패드 일부/전체를 내부 short. jumpered 패드는 항상 같은 net(스키매틱/PCB에 명시 연결 없어도 short 간주). 예: 와이어 점퍼, 다중 shield 패드 커넥터, 양측 short된 스위치.
- KiCad가 jumpered 패드를 short로 보므로 스키매틱/PCB에서 short된 패드 중 하나만 연결하면 됨.
- ⚠️ **NOTE**: jumper pad ≠ net tie. net tie는 다른 net을 동박으로 bridge(각 패드가 다른 net), jumper pad는 같은 net(연결이 보드 밖 컴포넌트에서 이뤄진다고 가정).
- 설정: **Pad Connections** 탭.
  - **All pads with duplicate numbers are jumpers** 활성 시 같은 번호 패드(및 링크 심볼 핀)끼리 jumper(예: 번호 1 패드들 상호 연결).
  - 다른 번호 패드는 (small plus) 버튼으로 **Explicit pad jumper groups** 추가. 공백/콤마 구분. `1 2`/`1, 2` = 패드 1·2 jumper, `3 4 5`/`3, 4, 5` = 패드 3·4·5 jumper.
  - 💡 **NOTE**: jumper 설정은 링크 심볼에서 전달됨 — Symbol Editor에서 심볼 jumper pin 구성 가능.

## 3D models · #fp-3d-models

- Footprint Properties의 **3D Models** 탭: 외부 3D model 파일 첨부 + 3D 미리보기.
- 미리보기 우측 버튼: orthographic projection on/off, PCB model 표시/숨김, 6개 면-정렬 시점, refresh. 하단 버튼은 미리보기 PCB 두께 설정.
- 다이얼로그 상단에서 외부 model 첨부. 첨부 model은 풋프린트 미리보기·전체 PCB 3D view에 표시. 포맷: **STEP, VRML, IDF**. path에 `${KIPRJMOD}`·`${KICAD9_3DMODEL_DIR}` 등 path variable 사용 가능. **Configure Paths** 버튼으로 변수 설정. 로드 실패 시 좌측 컬럼에 error 아이콘.
- 💡 **NOTE**: 구버전 versioned path variable은 현재 버전 값으로 자동 해석(예: `${KICAD8_FOOTPRINT_DIR}` → `${KICAD9_FOOTPRINT_DIR}`).
- 💡 **NOTE**: 표준 라이브러리의 많은 풋프린트는 model 파일이 아직 없으나, 향후 생성 대비 미존재 model path를 담고 있을 수 있음.
- 기본적으로 model은 풋프린트 원점에 offset/scaling/rotation 없이 배치. 좌측 컨트롤로 offset·scaling·rotation 적용. **opacity** 슬라이더로 투명도, 테이블 우측 **show** 체크 해제로 완전 숨김.

## Embedding files · #fp-embedding-files

- 외부 파일을 풋프린트에 임베딩 = 파일 사본을 풋프린트 내부에 저장. 외부 파일 대신 임베딩 사본 참조 → 이식성 향상(외부 파일 의존 제거)하나 파일 크기 증가. 특히 3D model 임베딩에 유용.
- 임베딩 파일은 보드 추가 시 dedup: 한 파일이 임베딩되고 같은 풋프린트 다중 인스턴스가 추가되면 사본 1개만 임베딩되고 모든 인스턴스가 공유. 풋프린트 임베딩 파일은 부모 보드에서 참조 불가. 자세한 내용은 Board Setup 문서.
- 💡 **NOTE**: 3D model을 한 번에 추가+임베딩: **3D Models** 탭에서 model 추가 시 파일 브라우저의 **Embed File** 체크 → 임베딩 + 임베딩 참조를 path로 자동 사용.

## Rule areas · #fp-rule-areas

- rule area(=keepout): 특정 DRC 룰을 정의할 수 있는 풋프린트 영역. 영역 내 특정 객체 유형에 DRC error 발생시키는 기본 룰 + custom DRC 룰과 조합해 복합 동작 정의. 풋프린트 rule area는 보드 추가 시 발효.
- **추가**: 우측 툴바 (add keepout area) 버튼(`Ctrl`+`Shift`+`K`) → 캔버스 클릭으로 첫 코너 → Rule Area Properties 다이얼로그 → 구성 후 **OK** → 코너 계속 배치 → 시작 코너 클릭/더블클릭으로 종료(임의 polygon).
- 자세한 내용은 PCB editor 문서.

## Reference images · #fp-reference-images

- PCB Editor처럼 Footprint Editor에서도 참조 이미지 사용 가능. 풋프린트 참조 이미지는 Footprint Editor에서만 표시 — PCB Editor·제조 출력에 미표시.
- **추가**: 우측 툴바 (image) 버튼 → 이미지 파일 선택. 자세한 내용은 PCB Editor 문서.

## Footprint wizards · #footprint-wizards

- footprint wizard: 파라미터 기반으로 흔한 풋프린트 생성. 제공 wizard:
  - BGA / QFN / QFP / SOIC, MSOP, SSOP, TSSOP 등 / SIP·DIP / ZIP / ZOIC 패키지
  - FPC connectors / Micromatch SMD connectors
  - Circular pad arrays / Touch sliders / Mutual capacitance touch buttons
  - USS-39 barcodes / QR codes
- **사용**: (module wizard) 버튼 → 타입 선택 → 파라미터 입력 → (export footprint names) 버튼으로 풋프린트 에디터로 전송 → 수동 수정·저장.
- 자체 wizard 생성도 가능(Advanced Topics 챕터의 Scripting 섹션 참조).

## Checking footprints · #checking-footprints

- footprint checker: 상단 툴바 (erc) 버튼으로 실행. 감지된 이슈는 다이얼로그 목록 + 캔버스 화살표 표시, 이슈 클릭 시 캔버스에서 focus.
- **체크 항목**:
  - 잘못되거나 누락된 courtyard
  - 풋프린트 type 불일치 패드(through hole 패드 없는 풋프린트는 surface mount type이어야 함)
  - 홀 없는 through hole 패드
  - 동박 레이어에 없는 plated through hole 패드
  - copper annulus 없는 plated through hole 패드
  - 홀이 패드 안에 완전히 들지 않는 plated through hole 패드
  - front·back 양쪽에 있는 surface mount 패드
  - copper/paste·mask 레이어 불일치 surface mount 패드(front copper + back paste/mask 등)
  - 다른 홀과 co-located/너무 가까운 패드
  - silkscreen-solder mask 개구부 충돌
  - net tie group 밖에서 다른 패드와 short되는 패드
  - net tie group의 존재하지 않는 패드
  - 다중 net tie group에 나타나는 패드

---

# Multichannel layout · #multichannel

- 멀티채널 레이아웃: PCB의 반복적 회로 블록 배치/라우팅을 복제하는 기능. 동일 subcircuit 다수(오디오 믹서 채널, 다출력 전원 단, LED 드라이버 채널 등) 설계에서 한 블록만 배치/라우팅 후 나머지 일치 블록에 자동 복제.
- **3단계 워크플로**:
  1. **Schematic setup**: 반복 부분을 지정. 각 반복 블록 = *channel*.
  2. **Rule area generation**: 각 채널의 물리 경계를 정의하는 placement rule area를 PCB에 생성.
  3. **Layout replication**: 한 *reference* 채널을 수동 배치/라우팅 → **Repeat Layout** 도구로 모든 *target* 채널에 복제.
- 채널 지정 방법: hierarchical sheet(채널당 반복 sheet), component class(채널당 고유 class), named group. 각 채널은 단일 sheet/class/group의 심볼·연결과 정확히 대응.
- 한 rule area = 한 채널. 하나는 *reference*(수동 배치·라우팅), 나머지는 *target*(reference 배치·라우팅 재사용). 자동 배치는 placement rule area로 제한.
- 💡 **NOTE**: KiCad는 멀티채널 기능 데모 프로젝트 `multichannel`을 포함.

## Multichannel design procedure: schematic · #multichannel-schematic

- 스키매틱에서 각 채널에 속하는 컴포넌트(심볼) 지정. **채널은 서로 등가**여야 함:
  - 각 채널의 심볼 수가 동일
  - 대응 심볼의 reference designator prefix 동일(예: `R`/`U`, 단 full designator는 unique)
  - 대응 심볼의 풋프린트 동일
  - 심볼 간 연결이 각 채널에서 등가
- 예: Channel 1~4 등가(연결을 다르게 그려도 underlying net 동일, Channel 2의 다른 심볼·Channel 3의 다른 값도 등가성을 깨지 않음). 대응 심볼은 같은 풋프린트 사용(R1·R3·R5·R7 동일, R2·R4·R6·R8 동일). 반례: Channel A(추가 병렬 저항)·Channel B(두 저항 간 연결 누락)는 비등가.
- **채널 지정 3방식**:
  - **Hierarchical sheets**: 각 채널 = 다른 sheet. 보통 같은 sheet 파일을 채널당 한 번씩 instantiate. 각 instantiation은 해당 채널의 모든 심볼 포함, 여분 없음.
  - **Component classes**: 각 채널 = 다른 component class. 해당 채널 심볼 전부 포함, 여분 없음.
  - **Groups**: named group으로 채널 = 보드 풋프린트 group. sheet/class 부적합 시 명시적 정의 방법.
- 💡 **TIP**: hierarchical sheet가 가장 흔하고 편리 — 같은 sheet 파일 다중 instantiate로 회로 동일성 보장, 스키매틱 에디터가 자동으로 unique reference designator 부여.

## Multichannel design procedure: board · #multichannel-board

- 보드에서 각 채널 = placement 룰이 구성된 rule area. 채널마다 rule area 추가. 하나는 reference(수동 배치/라우팅), 나머지는 target. 필요한 설정:
  - **Placement** 탭: 채널 컴포넌트를 담은 hierarchical sheet/component class/named group 선택.
  - **Keepouts** 탭: 보통 미선택(특정 항목 제외 필요 시 제외).
  - rule area **layers**: 채널에 포함되는 레이어로 설정. 항목은 reference·target 양쪽에 그 레이어가 활성일 때만 복사됨.
  - **area name**: Repeat Layout 다이얼로그 라벨용. 필수는 아니나 unique 이름 없으면 GUI에서 구분 어려움.

### Generating placement rule areas · #multichannel-generate-rule-areas

- placement rule area는 수동 생성 또는 **Tools** → **Multi-Channel** → **Generate Placement Rule Areas…​**로 자동 생성. 이 도구가 hierarchical sheet·component class·named group을 스캔해 선택한 각각에 rule area 생성.
- ⚠️ **NOTE**: 도구는 채널이 아닌 sheet/class/group에도 rule area를 생성할 수 있음 — 원하는 것만 선택할 책임은 사용자에게.
- 다이얼로그 3 탭: **Sheets**(sheet path·파일명), **Component Classes**, **Groups**. 각각 채널인 행의 **Generate** 체크.
- 추가 옵션:

| 옵션 | 설명 |
| --- | --- |
| **Replace existing placement rule areas** | 활성 시 채널의 기존 rule area를 새것으로 교체. 비활성 시 이미 rule area 있는 채널은 skip |
| **Group footprints with their placement rule areas** | 활성 시 채널의 rule area를 연관 풋프린트 전부와 group화(단일 entity로 조작). group 기반 source는 이미 group에 속하므로 비활성 |

- **OK** 시 각 선택 채널에 대해: ① sheet/class/group 소속 풋프린트 query ② 작은 margin의 convex hull 계산 ③ 90도 세그먼트만의 axis-aligned polygon으로 rectify ④ placement area로 rule area 생성(source type 기록) ⑤ rule area layer를 모든 동박 레이어로 설정 ⑥ Replace existing 체크 + 매칭 존재 시 기존 제거 ⑦ Group footprints 체크 시 rule area + 풋프린트로 group 생성 ⑧ `auto-placement-area-<source>` 패턴으로 자동 명명.
- 생성 후 원하는 항목이 모두 복사되도록 layer 구성을 변경할 수 있음.
- ⚠️ **NOTE**: rule area가 풋프린트와 group화되면 rule area 편집을 위해 group에 진입(또는 ungroup)해야 함.
- 💡 **TIP**: 생성 후 reference rule area를 reference 채널 라우팅 전부를 감싸도록 확대. target rule area는 Repeat Layout 시 reference에 맞춰 자동 resize됨.

### Repeating the layout · #multichannel-repeat-layout

- reference 채널 layout 복제: **Tools** → **Multi-Channel** → **Repeat Layout…​**.
- **워크플로**:
  1. **reference rule area 선택**: 도구 실행 전 선택하거나, 미선택 실행 시 클릭 프롬프트. 복제 원본.
  2. **Topology check**: 다른 모든 placement rule area를 찾아 reference와 회로 토폴로지 일치 여부 검사(컴포넌트·연결의 1:1 매핑=isomorphism 탐색). 큰 설계는 진행 표시.
  3. **Repeat Layout 다이얼로그 구성**: 토폴로지 결과 표시, 업데이트할 target·복사할 항목 선택.
  4. **실행**: **OK**로 선택 target에 적용.
- rule area 선택 상태로 실행 시 그것이 reference. 미선택 시 선택 프롬프트. rule area를 담은 group 선택도 가능(group 내 rule area 사용).

#### Target rule area table · #multichannel-repeat-layout-dialog

- 다이얼로그 상단 표가 layout 받을 target rule area 제어. 각 행 = 한 target:

| 컬럼 | 설명 |
| --- | --- |
| **Copy** | 복제 받을지 체크박스. 토폴로지 일치 target은 기본 체크, 불일치는 미체크·선택 불가 |
| **Rule Area** | target rule area 이름(zone properties 구성값) |
| **Status** | 일치 시 "OK", 불일치 시 error 메시지. details 아이콘으로 상세 불일치 사유 |

- status "OK"인 target에만 복사. "OK" 아니면 토폴로지를 reference에 매칭 불가(스키매틱 채널 매칭 요건 참조).

#### Repeat layout options · #repeat_layout_options

| 옵션 | 설명 |
| --- | --- |
| **Anchor footprint** | 드롭다운 선택 시 그 풋프린트(및 각 채널 동급)가 채널 anchor — 각 채널이 anchor 풋프린트 기준 배치·orientation. 미선택 시 reference rule area 중심 기준 |
| **Copy footprint placement** | 활성 시 reference 풋프린트 배치를 target에 복제. reference에 enclosed/intersect되는 풋프린트만 복사(완전 외부 미복사). reference·target 양쪽 활성 레이어만 |
| **Copy routing** | 활성 시 reference 내 트랙·via를 target에 복사. reference에 fully enclosed만 복사(부분/완전 외부 미복사). 양쪽 활성 레이어만. target 기존 라우팅은 복사 전 제거 |
| **Restrict to routing connected within the area** | Copy routing 하위 옵션. 체크 시 reference 내 패드와 net 공유하는 트랙·via만 복사(통과만 하는 무관 트랙 방지) |
| **Copy other items** | 활성 시 reference에 fully enclosed된 기타 항목(zone·그래픽)을 복사. 부분/완전 외부 미복사(예: reference 채널을 intersect만 하는 대형 zone은 미복사). 양쪽 활성 레이어만 |
| **Group items with their target rule areas** | 활성 시 target에 복사된 항목을 rule area와 group화(단일 entity 조작) |
| **Include locked items** | 활성 시 locked 항목도 복사·갱신. 비활성 시 reference의 locked는 미복사, target의 locked는 미갱신·미삭제 |

- **OK** 후 reference layout이 target에 적용. info bar가 갱신된 rule area 수 확인. 완료 후 각 채널은 개별 편집 가능.
- 💡 **TIP**: reference 채널을 다듬으며 Repeat Layout을 여러 번 실행 가능 — 매 실행이 target 내용을 현재 reference 상태로 교체.

## Topology matching · #multichannel-topology-matching

- 멀티채널의 핵심 = topology matching 알고리즘. reference 채널 컴포넌트가 각 target 컴포넌트에 어떻게 대응되는지 결정. 채널 매칭 실패 진단에 이해 중요.

### How components are matched · #how_components_are_matched

- KiCad가 reference·target 채널 연결성을 분석하여 카탈로그:
  - **Components**: 풋프린트당 1개, reference designator prefix(숫자 접미사 앞 글자, `R1`→`R`)로 식별.
  - **Pins**: 풋프린트별 패드당 1개.
  - **Connections**: 어느 핀이 같은 net을 공유하는가.
- 두 컴포넌트는 같은 prefix면 "같은 종류". hierarchical 설계에서 reference에 채널 식별자 포함 시(예: `TRIM_1.1`·`TRIM_2.1`) 공통 prefix 감지하고 trailing 채널 접미사를 채널 식별자로 처리해 매칭.
- 모든 핀 연결을 보존하는 1:1 매핑(isomorphism) 탐색. 즉 reference의 연결된 패드 쌍은 target에서도 대응 패드가 연결되어야 함. 매칭은 reference designator 번호가 아니라 실제 net 연결성 기반(`R1`이 반드시 `R1`에 매핑되지 않고 같은 연결 패턴의 저항에 매핑).

### Tie-breaking for identical components · #tie_breaking_for_identical_components

- target에 동일 연결성 컴포넌트가 여럿일 때(예: 같은 power/ground 간 동일 디커플링 캡 행) tie-breaking:
  1. **Symbol/sheet instance matching**: reference·target 컴포넌트가 같은 hierarchical sheet instance 출신이면 우선 매칭(hierarchical sheet 설계의 가장 신뢰성 높은 tie-breaker).
  2. **Position-based proximity**: reference 짝과 물리적으로 가까운 컴포넌트 선호.

### Mismatch error details · #mismatch_error_details

- target이 토폴로지 검사 실패 시 **Status** 컬럼에 error 요약, details 아이콘으로 상세 다이얼로그:
  - 매칭 안 된 특정 컴포넌트와 이유.
  - 일치 안 하면 reference vs target의 총 컴포넌트 수.
  - 비교용 각 영역의 전 컴포넌트 목록.
- 흔한 실패 이유·해결은 Troubleshooting 섹션 참조.

## Routing duplication details · #multichannel-routing-duplication

- **Copy routing** 활성 시 reference rule area의 모든 트랙·via를 각 target에 복제.

### What is copied · #what_is_copied

- 보드의 각 트랙/via가 reference rule area polygon에 *enclosed by*되는지 검사. fully enclosed만 복사 후보, 부분 overlap/완전 외부는 미복사.
- 복사 항목별: ① 항목(트랙 세그먼트/via) 복제 ② rule area 중심(또는 anchor 풋프린트) 간 offset 기준 reference→target 위치로 translate ③ anchor 풋프린트 orientation 차이만큼 rotate ④ 컴포넌트 매칭으로 어느 target 패드가 같은 net에 연결되는지 조회해 net 재할당.

### Net reassignment · #net_reassignment

- 복제 항목의 net 재할당: ① reference 채널에서 해당 라우팅과 같은 net에 연결된 패드 찾기 ② 그 패드의 부모 풋프린트 조회 ③ 매칭된 target 풋프린트의 대응 패드 찾기 ④ target 패드 net을 복제 항목에 할당. 수동 개입 없이 자동 재할당.

### Existing target routing · #existing_target_routing

- target에 복사 전, target rule area 활성 레이어의 기존 라우팅 제거(이전 반복 잔여 없는 clean 복사). **Restrict to routing connected within the area** 활성 시 영역 내 패드 연결 라우팅만 제거.

### Layer considerations · #layer_considerations

- 라우팅 항목은 reference·target *양쪽* 활성 레이어일 때만 복사:
  - reference가 `F.Cu`+`B.Cu`인데 target이 `F.Cu`만이면 front-copper만 복사.
  - 내부 동박 레이어 라우팅 복사는 양쪽 rule area에 그 레이어를 명시 포함해야 함.
- 💡 **TIP**: 라우팅이 쓰는 모든 동박 레이어를 양쪽 rule area에 활성화. 내부 동박 레이어를 rule area layer set에 추가하지 않아 내부 라우팅이 조용히 누락되는 게 흔한 이슈.

### When routing duplication fails · #when_routing_duplication_fails

- **Routing extends outside the rule area**: reference 밖으로 나간 트랙은 미복사. via fan-out 포함 모든 라우팅을 감싸도록 충분히 크게.
- **Net reassignment failure**: net을 target 채널 net에 매핑 불가 시(예: 채널 소속 아닌 global net) 복제 트랙이 reference net 유지 가능. **Restrict to routing connected within the area**로 무관 트랙 복사 방지.
- **Layer mismatch**: reference 라우팅이 target 미활성 레이어 사용 시 그 세그먼트는 조용히 누락.

## Other item duplication · #multichannel-other-items

- **Copy other items** 활성 시 reference 내 zone·그래픽(드로잉·텍스트·dimension)도 복제. 동일 displacement·rotation transform 적용.
- zone은 라우팅과 같은 컴포넌트-매칭 조회로 net 재할당. zone은 모든 레이어가 양쪽 rule area에 있을 때만 복사.
- 미연결 그래픽(실크 텍스트·board outline·fab 드로잉)은 net 할당 없이 복사. 양쪽 활성 레이어여야 함.
- 💡 **NOTE**: 풋프린트 텍스트 항목(reference designator·value·필드)은 standalone이 아니라 풋프린트 배치의 일부로 처리 — 위치·visibility·attribute가 reference 풋프린트 필드에 맞춰 갱신.

## Step-by-step multichannel workflow · #multichannel-step-by-step

1. **스키매틱 설계**: 반복 회로를 hierarchical sheet로(또는 component class/group 할당). 채널당 한 번 instantiate. 모든 채널 동일 토폴로지 보장.
2. **netlist import / Update PCB**: 스키매틱을 PCB로 전송. 모든 채널 풋프린트가 보드에 나타남.
3. **placement rule area 생성**: **Tools** → **Multi-Channel** → **Generate Placement Rule Areas…​** → 채널 sheet/class/group 체크 → **OK**.
4. **rule area 배치**: 각 생성 rule area를 원하는 위치로 이동(풋프린트는 아직 rule area 안에 없어도 됨 — repeat layout 단계에서 처리).
5. **reference 채널 설계**: 한 rule area를 reference로 선택, 풋프린트를 rule area 안에 배치하고 완전 라우팅. boundary가 복제할 풋프린트·라우팅·기타 항목을 모두 감싸도록.
6. **필요 시 reference rule area 확대**: auto-generated가 라우팅을 못 감쌀 수 있음. via fan-out·local zone 포함 모든 라우팅을 감싸도록 outline 편집.
7. **Repeat Layout 실행**: reference rule area 선택 → **Tools** → **Multi-Channel** → **Repeat Layout…​**. 다이얼로그에서: 모든 target **OK** 확인 / 필요 시 anchor 풋프린트 선택 / **Copy footprint placement**·**Copy routing**·**Copy other items** 활성 / **OK**.
8. **결과 검토**: 각 target 채널 배치·라우팅 확인. DRC 실행.
9. **반복**: reference 채널 layout 변경 시 편집 후 Repeat Layout 재실행 → target 갱신.

## Troubleshooting multichannel layouts · #multichannel-troubleshooting

### Channels fail topology matching · #channels_fail_topology_matching

- status가 "OK" 아닌 error면 토폴로지 불일치. details 아이콘으로 상세 확인. 흔한 원인:
  - **Missing or extra components**: 각 채널 sheet/class가 정확히 같은 심볼 셋을 갖는지 확인(한 채널에만 디커플링 캡 추가 등 흔한 실수).
  - **Different reference designator prefixes**: target 컴포넌트 prefix가 reference 어느 것과도 다름(`R` vs `C`).
  - **Different footprint assignments**: 대응 심볼이 같은 풋프린트를 써야 함(`R1`이 0402, `R3`이 0603이면 패드 수 차이로 매칭 실패).
  - **Different net connections**: 한 채널에서 net이 다르게 연결됨(wire 삭제/오연결).
  - **Nested hierarchical sheets**: 채널 sheet 내 child sheet도 query에 포함됨 — 채널 간 nested sheet 동일성 확인.

### Routing does not appear in target channels · #routing_does_not_appear_in_target_channels

- **Rule area too small**: 가장 흔함. reference 밖 라우팅 미복사 — rule area 확대.
- **Layer mismatch**: 라우팅 사용 동박 레이어를 양쪽 rule area에 활성화(**Layers** 탭 확인).
- **Unrelated routing filtered out**: **Restrict to routing connected within the area** 체크 시 영역 내 패드에 없는 net의 트랙·via는 skip(net 기반 검사이므로 영역 내 패드와 net 공유 via는 물리적 미라우팅이어도 복사). 영역 내 패드 없는 net 라우팅 복사가 필요하면 해제.
- **Net reassignment to wrong net**: 채널 고유가 아닌 global/공유 net(power 등) 트랙은 reference net 유지 가능. **Restrict to routing connected within the area**로 방지.

### Footprint placement is not copied · #footprint_placement_is_not_copied

- **Footprint outside reference area**: 풋프린트는 reference에 enclosed/intersect되어야 함. 완전 외부 미복사.
- **Layer not enabled**: 양쪽 활성 레이어일 때만 복사.
- **Locked footprints**: **Include locked items** 미체크 시 reference의 locked는 미복사, target의 locked는 미이동.

### Other items do not appear in target channels · #other_items_do_not_appear_in_target_channels

- **Item not fully enclosed**: zone·그래픽은 reference에 fully enclosed되어야 복사(boundary만 intersect하는 대형 zone은 미복사).
- **Zone layer mismatch**: zone은 모든 레이어가 양쪽 rule area에 있어야 복사.
- **Locked items**: **Include locked items** 미체크 시 reference의 locked 미복사, target의 locked 미갱신.

### Target rule area shape is wrong · #target_rule_area_shape_is_wrong

- target outline은 reference rule area 모양에 맞춰 자동 갱신(target 위치로 translate·rotate). 예상과 다르면 reference outline 확인 — target은 직접 복사본.

### Tips for clean multichannel designs · #tips_for_clean_multichannel_designs

- **Use hierarchical sheets**: 단일 sheet 파일 다중 instantiate로 채널 회로 동일성 보장.
- **Name your rule areas**: 설명적 이름(`Channel 1`, `Channel 2`)으로 Repeat Layout 다이얼로그에서 식별.
- **Make the reference rule area generous**: 라우팅 주위 여유 공간이 boundary clipping보다 나음.
- **Route the reference channel completely**: Repeat Layout 전 완전 라우팅(부분 라우팅도 복제 가능하나 검증 용이).
- **Group items with rule areas**: 복제 후 채널 단위 이동에 편리.
- **Run DRC after replication**: 다른 board 영역의 clearance 위반·net 할당 문제 검출.

---

# Design blocks · #pcb-design-blocks

- design block: 스키매틱/레이아웃 일부를 저장해 재사용. 같은/다른 프로젝트에서 재사용. 심볼·풋프린트처럼 design block library에 저장·조직. 한 block은 스키매틱 조각, 레이아웃 조각, 또는 둘 다 포함.
- 스키매틱 design block instantiate 시 저장된 스키매틱 조각이 현재 sheet 또는 새 subsheet에 삽입. 레이아웃 design block instantiate는 저장된 board 조각을 보드에 직접 추가. 둘 다 포함 시 스키매틱 조각 심볼에 대응하는 풋프린트에 레이아웃 적용 가능.
- 보통 스키매틱 조각으로 먼저 생성 후 나중에 레이아웃 추가. 스키매틱 조각 재사용은 Schematic Editor 매뉴얼에서 다룸.
- **레이아웃 design block 사용**: 먼저 **View** → **Panels** → **Design Blocks**로 Design Blocks 패널 표시(스키매틱 에디터 우측 docked). 닫기: 같은 메뉴 재선택, 패널 우상단 close 버튼, 또는 패널 우클릭 → **Hide Library Tree**.
- 패널에서 design block library 생성, design block 생성·편집·PCB 배치.

## Creating and managing design blocks · #creating-and-managing-design-blocks

- design block은 design block library에 저장 — block 저장 전 library 추가 필요.

### Creating a new design block library · #creating_a_new_design_block_library

- library tree 우클릭 → **New Library…​** → 위치/이름 선택. 폴더로 저장, 폴더명 = 라이브러리명 + `.kicad_blocks` 접미사.
- global / project library table 선택(global=전체, project=현재 프로젝트만).
- 💡 **NOTE**: 관리(삭제·이름변경)는 **Preferences** → **Manage Design Block Libraries…​**. design block library table은 symbol·footprint library table과 동일하게 동작.

### Creating a new design block · #creating_a_new_design_block

- PCB Editor에서 보드 전체 또는 객체 선택으로 생성. source 객체 선택(sheet 열기 또는 캔버스 객체 선택) → block을 담을 library 우클릭 → **Save Board as Design Block…​** 또는 **Save Selection as Design Block…​**.
- ⚠️ **NOTE**: 기존 design block(스키매틱만 있고 레이아웃 없는 것 포함)에 레이아웃 조각 저장 시 새 block 생성 금지 — 기존 block update.
- Design Block Properties 다이얼로그 속성:
  - **Name**: library tree·preview 표시명. 필터·그룹/sheet 추가 시 기본 이름.
  - **Keywords**: 공백 구분 키워드. preview 표시·필터링.
  - **Description**: library tree·preview 표시. 필터링.
  - **Default Fields**: key/value 쌍. 스키매틱이 sheet로 배치될 때 hierarchical sheet field로 포함(sheet 아닌 배치 시 무시).
- 생성 후 편집: library tree에서 우클릭 → **Properties…​**.

### Updating an existing design block · #updating-an-existing-design-block

- 기존 design block 레이아웃 업데이트: 먼저 수정할 design block 배치 후 레이아웃 편집. 레이아웃 부분이 없으면 스키매틱에 배치 → update pcb from schematic으로 링크 풋프린트 추가 → 레이아웃 편집.
- 저장: 저장할 board 요소 선택 → design block 이름 우클릭 → **Update Design Block from Selection**(기존 내용을 선택으로 교체).
- 다른 방법: 현재 board가 저장할 것만 담으면 우클릭 → **Update Design Block from Board**(board 전체로 교체). group으로 배치됐으면 캔버스의 group 우클릭 → **Save to Linked Design Block**.

## Using design blocks in a board · #using-pcb-design-blocks

- 레이아웃 design block 사용 2가지(상황별):
  - **직접 추가**: 스키매틱 심볼과 무관하게 보드에 직접 추가. 스키매틱에 대응 없는 board 항목을 미리 정해진 배열로 추가할 때 유용(예: 특정 패턴 마운팅 홀).
  - **스키매틱 연동**: 스키매틱에 design block 사용 시 Update PCB from Schematic으로 심볼의 할당 풋프린트를 보드에 추가 후 design block 저장 레이아웃 적용. 스키매틱 조각 + 링크 레이아웃 동시 재사용.

### Directly placing design blocks in a board · #directly_placing_design_blocks_in_a_board

- Design Blocks 패널로 직접 배치. 패널 library tree는 design block library와 각 block 나열(expand/collapse). 상단 **Recently Used** pseudo-library에 최근 배치 block. library 우클릭 → **Pin Library**로 상단 고정.
- 필터: 패널 상단 textbox로 name·description·keyword 필터. 기본 best match 정렬, (config) 메뉴 → **Sort Alphabetically**.
- block 선택 시 하단에 name·metadata(description·keyword)와 그래픽 preview 표시.
- **추가**: library tree에서 더블클릭 또는 우클릭 → **Place Design Block**.
- 배치 옵션:
  - **Place repeated copies**: 활성 시 이전 block 배치 완료 후 다시 배치 시작. 취소는 `Esc` 또는 우클릭 → **Cancel**.
  - **Place as group**: 활성 시 내용을 group으로 추가하고 group library link를 source design block/library로 설정. group 배치는 필수 아니나 일부 기능은 group이어야 사용 가능(Grouped 섹션 참조).
  - **Keep annotations**: 활성 시 저장된 design block 정의대로 풋프린트 annotation 유지. 비활성 시 삽입하며 annotation clear.
- 배치 후 design block 내용은 일반 스키매틱 객체처럼 편집·이동·삭제 가능.

### Applying layouts to design blocks from a schematic · #applying_layouts_to_design_blocks_from_a_schematic

- 스키매틱 심볼에 링크된 풋프린트에 레이아웃 재사용: 스키매틱+레이아웃 조각 둘 다 가진 design block 필요. 스키매틱에 추가 후 대응 풋프린트에 저장 레이아웃 적용.
- ⚠️ **NOTE**: 프로젝트 내 레이아웃 재사용 대안으로 multichannel 도구도 고려.
- **절차**:
  1. 스키매틱+레이아웃 둘 다 가진 design block 생성.
  2. 스키매틱에 추가 — **place as group**으로 배치.
  3. Update PCB from schematic — **Group footprints based on symbol group** 활성. 스키매틱 design block 심볼 대응 풋프린트를 보드에 추가·group화. group은 올바른 design block을 가리키는 library link 설정.
  4. PCB Editor에서 그 group 선택 → 우클릭 → **Apply Design Block Layout**. 풋프린트를 design block 레이아웃대로 재배치, 패드 간 트랙 그리기, 그래픽·텍스트 등 추가. 새 항목도 group에 추가.

## Grouped design blocks · #grouped-design-blocks

- design block을 보드에 배치할 때 group으로 배치 옵션. 스키매틱에서 group화된 경우 스키매틱→보드 전송 시에도 group 옵션. 일부 기능은 group일 때만 사용 가능 — 특히 PCB에서 레이아웃 적용하려면 스키매틱·PCB 양쪽에서 group화 필수.
- **group 시 사용 가능 기능**:
  - 우클릭 → **Place Linked Design Block**로 추가 인스턴스 배치.
  - 우클릭 → **Save to Linked Design Block**로 PCB design block을 library 버전에 갱신.
  - update PCB from schematic으로 스키매틱 group을 PCB로 복사(design block 심볼 대응 풋프린트 group화).
  - 그룹 풋프린트 우클릭 → **Apply Design Block Layout**로 레이아웃 적용.
  - 레이아웃 적용 대안으로 multichannel 도구로 한 group 레이아웃을 다른 group에 복제(group으로 스키매틱 배치 → PCB 전송 → 한 group 수동 레이아웃 → multichannel로 복제).
- **group화 방법**: 가장 쉬운 방법은 스키매틱 배치 시 **Place as group** 체크 → update PCB from schematic 시 **Group footprints based on symbol groups** 활성.
- 직접 레이아웃 design block 배치 시 PCB에서 **Place as group** 체크.
- 사후 group화: design block 내용 전부 선택 → group화(여분·누락 없이 정확히). group properties에서 **Library link**를 `<library>:<block>` 형식으로 design block 이름·library에 일치 설정. 예: `amplifiers` library의 `inverting_amplifier` block → `amplifiers:inverting_amplifier`.
