# PCB 에디터 ③ — 검사·EDA 임포트·출력 생성 — KiCad 10.0 사용 다이제스트

> **원문**: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html

> **범위**: Forward/Back annotation, Geographical re-annotation, DRC(Design Rule Check), 보드 통계, 측정 도구, Find, Search 패널, 3D 뷰어, Net inspector, 타 EDA 보드 임포트, 출력 생성(Plot Gerber/PostScript/SVG/DXF/PDF·Drill·IPC-2581·ODB++·Position·BOM·Print·STEP/3D·기타), Design variants

> 한국어 요약 다이제스트. 섹션 제목의 #anchor로 원문 핀포인트: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#<anchor>

## 목차

- [Forward and back annotation](#forward-and-back-annotation) — 회로도↔보드 동기화 개요
- [Update PCB From Schematic (forward annotation)](#forward-annotation) — 회로도 변경을 보드로 전달 (F8)
- [Forward annotation 옵션](#options) — re-link/replace/delete 등 동작 제어
- [Re-linking symbols and footprints](#re-linking) — UUID/refdes 기반 링크
- [Update Schematic from PCB (back annotation)](#back-annotation) — 보드 변경을 회로도로 역전달
- [Back annotation 옵션](#options_2) — refdes/value/net 등 개별 활성화
- [Back annotation with CMP files](#back_annotation_with_cmp_files) — 풋프린트 할당만 동기화하는 제한적 방법
- [Geographical re-annotation](#geographical-re-annotation) — 물리적 위치 기반 refdes 자동 부여
- [Design rules checking (DRC)](#design-rule-checking) — 설계 규칙 검증
- [Clearance and constraint resolution](#clearance-and-constraint-resolution) — 적용 규칙 조회
- [DRC configuration](#drc_configuration) — 위반 심각도 설정
- [List of DRC checks](#list-of-drc-checks) — 전체 DRC 체크 목록·기본 심각도
- [User-definable DRC violations](#text-var-drc) — `${DRC_ERROR}`/`${DRC_WARNING}` 텍스트 변수
- [DRC report file](#drc_report_file) — .rpt/JSON 리포트 저장
- [Board Statistics](#board-statistics) — 보드 통계 다이얼로그
- [Measurement tool](#measurement-tool) — 거리/각도 측정 (Ctrl+Shift+M)
- [Find tool](#find_tool) — 텍스트 검색
- [Search panel](#search_panel) — 도킹 검색 패널 (Ctrl+G)
- [3D Viewer](#threed-viewer) — 3D 보드 뷰 (Alt+3)
- [Net inspector](#net-inspector) — 넷 통계 패널
- [Importing boards from other EDA tools](#importing-boards) — 타 EDA 보드 임포트 개요
- [Supported import formats](#supported_import_formats) — 지원 포맷 표
- [How to import a board](#how_to_import_a_board) — 임포트 절차
- [Layer mapping](#layer_mapping) — 레이어 매핑
- [Post-import cleanup](#post_import_cleanup) — 임포트 후 정리
- [Format-specific notes](#format_specific_notes) — 포맷별 지원/제약
- [Importing Specctra session files](#specctra-session-import) — 오토라우터 결과(.ses) 임포트
- [Generating outputs](#generating_outputs) — 출력 생성 개요
- [Plotting (Gerber/PostScript/SVG/DXF/PDF)](#plotting) — Plot 다이얼로그
- [Drill files](#drill-files) — Excellon/Gerber X2 드릴 파일
- [IPC-2581](#ipc-2581-export) — IPC-2581 XML 팹출력
- [ODB++](#odb-export) — ODB++ 팹출력
- [Component placement (position) files](#component_placement_position_files) — 픽앤플레이스 위치 파일
- [Footprint reports](#footprint_reports) — 풋프린트 리포트
- [IPC-D-356 netlists](#ipc_d_356_netlists) — 베어보드 검사용 넷리스트
- [Bill of Materials](#bill_of_materials) — (레거시) BOM
- [Printing](#printing) — 2D 프린터 출력
- [Specctra DSN](#specctra_dsn) — 오토라우터용 DSN 익스포트
- [GenCAD](#gencad) — GenCAD 익스포트
- [VRML](#vrml-exporter) — VRML 3D 모델
- [IDF](#idf-exporter) — IDFv3 기계 데이터
- [3D models (STEP/GLB/…)](#_3d-export) — STEP 등 3D 모델 익스포트
- [Footprint association (CMP) files](#footprint_association_cmp_files) — CMP 익스포트
- [Hyperlynx](#hyperlynx) — HyperLynx 익스포트
- [Design variants](#pcb-design-variants) — 디자인 변형 개요
- [Selecting a variant in the PCB editor](#selecting-a-variant-in-the-pcb-editor) — 변형 선택
- [Viewing variant effects](#viewing-variant-effects) — 변형 효과 보기
- [Generating variant-aware outputs](#pcb-generating-variant-aware-outputs) — 변형별 출력
- [Command-line variant support](#command-line-variant-support) — `--variant` CLI

---

## Forward and back annotation · #forward-and-back-annotation

- Forward annotation = 회로도 변경을 보드로 동기화, Back annotation = 보드 변경을 회로도로 동기화.

## Update PCB From Schematic (forward annotation) · #forward-annotation

- 회로도(Schematic Editor)의 설계 정보를 보드(Board Editor)로 동기화하는 도구. 각 심볼의 풋프린트를 보드에 추가하고 변경된 회로도 정보를 보드로 전달하며, 특히 보드 넷 연결을 회로도에 맞게 갱신한다.
- 접근: **Tools** → **Update PCB from Schematic** (`F8`) — 회로도/보드 에디터 양쪽에서 가능. 보드 에디터 상단 툴바 아이콘으로도 가능.
- 적용될 변경은 *Changes To Be Applied* 창에 나열되며, **Update PCB** 버튼을 누르기 전까지 PCB는 수정되지 않는다.
- 하단 체크박스로 메시지 종류별 표시/숨김 가능. **Save…​** 버튼으로 변경 리포트를 파일로 저장.
- 💡 **NOTE:** 회로도→PCB 전달의 권장 방식. 구버전처럼 netlist를 export/import할 필요가 없다.

### Forward annotation 옵션 · #options

| Option | 설명 |
| --- | --- |
| Re-link footprints to schematic symbols based on their reference designators | 체크 시 각 풋프린트의 고유 ID를 동일 refdes의 심볼에 맞게 갱신(refdes 기준 재링크). 일반적으로 **체크 해제** 권장. (사용 시점은 아래 Re-linking 참조) |
| Group footprints based on symbol group | 체크 시 연결된 심볼이 그룹이면 풋프린트도 PCB에서 그룹으로 묶음 |
| Replace footprints with those specified by symbols | 체크 시 회로도 심볼이 지정한 풋프린트로 PCB 풋프린트를 교체. 해제 시 심볼이 다른 풋프린트를 지정해도 기존 풋프린트 유지 |
| Delete footprints with no symbols | 체크 시 대응 심볼이 없는 풋프린트 삭제. "Not in schematic" 속성 풋프린트는 영향 없음. 해제 시 삭제 안 함 |
| Override locks | 체크 시 잠금이 삭제/교체 여부에 영향 없음. 해제 시 잠긴 풋프린트는 절대 삭제/교체 안 됨 |
| Update footprint fields from symbols | 체크 시 심볼의 신규/변경 필드를 풋프린트로 전달해 동기화. 해제 시 풋프린트 필드 미갱신 |
| Remove footprint fields not found in symbols | 체크 시 대응 심볼에 없는 풋프린트 필드 제거. 해제 시 유지(풋프린트가 추가 필드 보유 허용) |

### Re-linking symbols and footprints · #re-linking

- 심볼과 풋프린트는 고유 식별자(UUID)로 링크되며, KiCad가 자동 관리한다. refdes가 바뀌어도 연결을 유지한다. 새 객체는 생성 시 식별자를 부여받는다.

#### Re-linking by unique identifier (default) · #re_linking_by_unique_identifier_default

- 정상 사용 시 **Re-link …** 옵션은 체크 해제. 동일 식별자 심볼이 풋프린트를 갱신(refdes 무관), 매칭 없는 식별자는 새 풋프린트를 추가.
- refdes가 회로도에서 바뀌면(예: 재annotation) Update PCB 실행 시 PCB의 refdes가 갱신된다.

#### Re-linking by reference designator · #re_linking_by_reference_designator

- 체크 시 refdes 기준으로 링크. 심볼이 in-place 갱신이 아니라 삭제 후 교체되는 워크플로(블록/시트 잘라내기·복사 후 재annotation)에서 유용 — 이 경우 식별자 기반 링크가 끊긴다.
- refdes는 같지만 내부 식별자가 바뀐 경우, 식별자 기준 갱신은 기존 풋프린트를 삭제하고 새로 추가해 위치를 잃게 만든다. refdes 기준 재링크로 매칭 refdes를 가이드 삼아 링크를 재생성한다.
- 링크 재수립 후 다음 forward annotation은 정상(식별자 기반, 즉 체크 해제)으로 한다.

## Update Schematic from PCB (back annotation) · #back-annotation

- 보드 변경을 회로도로 역동기화하는 도구. refdes, value, attributes(DNP/Exclude From BOM 등), 풋프린트 할당, 기타 필드, net 이름을 보드→회로도로 동기화. 각 변경 유형은 개별 on/off.
- 접근: **Tools** → **Update Schematic From PCB** (회로도/보드 에디터 양쪽).
- 적용될 변경은 *Changes To Be Applied* 창에 나열되며, **Update Schematic** 버튼 전까지 회로도는 수정 안 됨. **Save…​** 로 리포트 저장.

### Back annotation 옵션 · #options_2

| Option | 설명 |
| --- | --- |
| Re-link footprints to schematic symbols based on their reference designators | 체크 시 refdes 기준 재링크. refdes 갱신과는 양립 불가. 보통 **체크 해제** 권장 |
| Reference designators | 체크 시 심볼 refdes를 연결 풋프린트에 맞게 갱신 |
| Values | 체크 시 심볼 value를 풋프린트 value에 맞게 갱신 |
| Attributes | 체크 시 심볼 속성(exclude from BOM, DNP 등) 갱신 |
| Other fields | 체크 시 기타 필드 갱신 (refdes/value/footprint은 각각 별도 옵션) |
| Footprint assignments | 체크 시 보드에서 변경/교체된 풋프린트 할당을 갱신 |
| Net names | 체크 시 보드의 net 이름 변경을 회로도로 반영. 필요시 net label 갱신/추가 |
| Prefer symbol unit swaps over label swaps | 멀티유닛 심볼의 게이트(유닛) 스왑 감지 시, net label 스왑이 아니라 심볼 유닛 스왑으로 회로도 갱신 |
| Prefer symbol pin swaps over label swaps | 핀 간 net 스왑 감지 시, net label 스왑이 아니라 심볼 핀 스왑으로 갱신(가능 시). 핀 스왑은 Schematic Editor 환경설정의 Editing Options에서 **Allow unconstrained pin swaps**가 활성일 때만 가능 |

- 💡 **NOTE:** Geographical Reannotation을 refdes back-annotation과 조합하면 레이아웃 위치 기반으로 전체 부품을 재annotation할 수 있다.

### Back annotation with CMP files · #back_annotation_with_cmp_files

- 일부 변경은 CMP 파일로 동기화 가능: PCB 에디터에서 **File** → **Export** → **Footprint Association (.cmp) File…​** 로 내보내고 Schematic Editor에서 **File** → **Import** → **Footprint Assignments…​** 로 가져온다.
- 💡 **NOTE:** 이 방법은 풋프린트 할당과 풋프린트 필드 변경만 동기화 가능. Update Schematic from PCB 사용 권장.

## Geographical re-annotation · #geographical-re-annotation

- 풋프린트의 보드 상 물리 위치를 기준으로 refdes를 자동 설정하는 도구.
- 실행: **Tools** → **Geographical Reannotate…​**.
- 다이얼로그 섹션:
  - **Footprint Order**: 풋프린트 위치가 재annotation에 어떻게 반영될지 설정.
  - **Reannotation Scope**: 재annotation 대상 — 보드 전체 / 전·후면 / 선택 항목.
  - **Reference Designators**: 새 refdes 할당 방식. 전면/후면 풋프린트에 대해 별도 설정.
- **Reannotate PCB** 버튼으로 적용.
- ⚠️ **NOTE:** 이 도구는 보드의 refdes만 갱신하고 회로도는 갱신하지 않는다. 이후 반드시 **re-link … reference designators** 옵션을 **해제**한 상태로 Update Schematic from PCB를 실행해 회로도에 동기화할 것. 안 하면 보드와 회로도의 refdes가 불일치.

---

# Inspecting a board · #inspecting_a_board

## Design rules checking (DRC) · #design-rule-checking

- 보드가 Board Setup에 정의된 요구사항을 만족하고 모든 패드가 netlist/회로도대로 연결됐는지 검증하는 도구. 라우팅 중 일부 위반은 자동 방지되지만 다수는 자동 방지가 불가하므로, 제조 파일 생성 전 반드시 DRC를 실행해야 한다.
- 실행: 상단 툴바 DRC 아이콘, 또는 **Inspect** → **Design Rules Checker**.
- DRC Control 상단 옵션:
  - **Refill all zones before performing DRC**: 활성 시 DRC 실행 때마다 zone 리필. 비활성 시 수동 리필 안 했으면 결과가 틀릴 수 있음.
  - **Test for parity between PCB and schematic**: 활성 시 PCB 규칙 외에 회로도-PCB 차이도 검사. standalone 모드에서는 무효.
- 추가 옵션(config 메뉴):
  - **Report all errors for each track**: 활성 시 트랙 세그먼트별 모든 clearance 오류 보고(느려짐). 비활성 시 첫 오류만.
  - **Cross-probe Selected Items**: 활성 시 DRC 창에서 항목/위반 선택 시 캔버스 커서가 해당 위치로 이동.
  - **Center on Cross-probe**: 활성 시 선택 항목/위반 마커로 캔버스 중앙 정렬(Cross-probe Selected Items 비활성 시 무효). PCB 에디터 Display Options의 **Center view on cross-probed items**가 켜져 있으면 이 옵션과 무관하게 중앙 정렬됨.
- 결과는 창 중앙에 3개 탭(Rule violations / unconnected items / 회로도-PCB 차이)과 4번째 탭(ignored tests)으로 표시. **Save…​** 로 plaintext 리포트 생성.
- 위반은 관련 객체를 하위에 나열. 위반 클릭 시 영향 영역 중앙 이동(설정에 따라), 객체 클릭 시 하이라이트.
- 위반 유형별 컨텍스트 액션 제공 — clearance 위반은 clearance resolution, custom rule 위반은 constraint resolution, board vs. library footprint mismatch는 Compare Footprint with Library 및 update from library.
- 하단에 errors/warnings/exclusions 개수 표시, 각 유형 체크박스로 필터링. **Delete Marker**(선택 위반 제거, 다음 DRC까지) / **Delete All Markers**(전체 제거).
- 위반 우클릭 메뉴:
  - **Exclude this violation:** 해당 위반만 무시. 우클릭 → **Remove exclusion for this violation** 로 해제.
  - **Exclude with comment…​:** 사유 코멘트 입력하며 제외. **Exclusions** 체크박스로 표시 시 코멘트 함께 보임. **Edit exclusion comment…​** 로 편집/추가.
  - **Exclude all violations of rule:** 동일 custom DRC rule이 유발한 *모든* 위반 제외(custom rule 위반에만 표시). 이미 제외된 항목엔 **Remove all exclusions for violations of rule**.
  - **Change severity:** warning↔error 변경(해당 유형 전체에 적용).
  - **Ignore all:** 해당 유형 전체 무시 → **Ignored Tests** 탭으로 이동. 그 탭 우클릭 또는 Board Setup의 Violation Severity 패널에서 해제.
  - **Edit violation severities…​:** Board Setup의 Violation Severity 패널 오픈.
- 제외/무시된 위반은 실행 간 기억됨. 제외 위반은 **Exclusions** 체크 시에만 표시, 무시 항목은 표시 안 되고 **Ignored Tests** 탭에 목록.

### Clearance and constraint resolution · #clearance-and-constraint-resolution

- 선택 항목에 적용되는 clearance/design constraint 규칙을 조회하는 도구. 복잡한 규칙의 보드에서 어느 규칙이 적용되는지 확인할 때 유용.
- 두 객체 간 clearance 조회: 두 객체 선택 후 **Inspect** → **Clearance Resolution**. 미선택 시 선택 프롬프트. Clearance Report 다이얼로그가 copper layer별 필요 clearance와 근거 규칙을 표시. hole clearance, physical clearance도 조회 가능.
- 💡 **NOTE:** 두 항목 미선택 후 실행하면 인터랙티브하게 두 항목을 고르도록 안내 — 서로 다른 그룹의 항목 등 동시에 선택하기 어려운 두 항목의 clearance 확인에 유용.
- 객체에 적용되는 design constraint 조회: 선택 후 **Inspect** → **Constraints Resolution**. 미선택 시 선택 프롬프트. Constraints Report 다이얼로그가 적용 제약을 표시.

### DRC configuration · #drc_configuration

- 각 DRC 체크의 심각도는 Board Setup의 **Violation Severity** 섹션에서 설정 — error marker / warning marker / no marker(ignored).
- ⚠️ **NOTE:** Violation Severity에서 규칙을 Ignore로 설정하면 해당 검사가 **완전히 비활성화**된다. 주의해서 사용. (개별 위반 무시는 DRC 창에서 가능)

### List of DRC checks · #list-of-drc-checks

- KiCad가 검사하는 설계 규칙과 기본 심각도 목록. 모든 심각도는 설정 가능하며, 일부는 custom design rule로만 사용 가능.

#### Electrical DRC checks · #electrical_drc_checks

| Violation | Description | Default Severity |
| --- | --- | --- |
| Items shorting two nets | 서로 다른 net의 copper 항목이 충돌. 의도적이면 net tie 사용 고려 | Error |
| Tracks crossing | 다른 net의 트랙이 교차 | Error |
| Clearance violation | 다른 net의 두 copper 항목 간 거리가 설정 clearance보다 작음. clearance는 board-level minimum, net class, custom rule에서. clearance resolution으로 상세 확인 가능. physical clearance(기본 미설정, custom rule)도 보고 | Error |
| Creepage violation | 다른 net copper 항목 간 creepage 거리가 설정값보다 작음. custom rule의 `creepage` constraint로 설정 | Error |
| Via is not connected or is connected on only one layer | via가 한 레이어에서만 연결되거나 미연결 | Warning |
| Track has unconnected end | 트랙 세그먼트 끝이 다른 copper 객체에 미연결 | Warning |
| Thermal relief connection to zone incomplete | 패드의 zone 연결에 thermal relief spoke가 부족. 최소 개수는 board-level 또는 custom rule. 부족 시 수동으로 track/copper shape로 연결 추가 가능 | Error |

#### Design for manufacturing DRC checks · #dfm-drc

| Violation | Description | Default Severity |
| --- | --- | --- |
| Board edge clearance violation | copper와 board edge 거리가 설정 copper-to-edge clearance보다 작음. oval hole은 board edge로 간주. 음수 clearance는 겹침 허용 | Error |
| Hole clearance violation | hole(pad/via)과 다른 copper 객체 거리가 설정 copper-to-hole clearance보다 작음(공통 레이어 보유 시만). physical hole clearance(기본 미설정)도 보고 | Error |
| Drilled hole too close to other hole | drilled hole 간 거리가 설정 hole-to-hole clearance보다 작음. through/blind/buried via 및 패드 through hole = drilled. micro via는 레이저라 제외. 비원형 hole은 라우팅이라 제외 | Error |
| Drilled holes co-located | drilled hole이 다른 hole과 정확히 같은 위치 | Warning |
| Track width | 트랙 폭이 설정 범위 밖. board-level minimum 또는 custom rule. net class의 optimal width는 라우터용일 뿐 min/max를 설정하지 않음(custom rule 필요) | Error |
| Track angle | 연결된 두 트랙 세그먼트 각도가 범위 밖. custom rule `track_angle` constraint | Error |
| Track segment length | 트랙 세그먼트 길이가 범위 밖. custom rule `track_segment_length` constraint | Error |
| Annular width | pad/via annular width가 범위 밖. board-level minimum은 board setup constraints, max·세부는 custom rule | Error |
| Hole size out of range | drilled hole 직경이 범위 밖(가장 작은 드릴 비트 기준). through/blind/buried via, 패드 through hole 포함. micro via 제외 | Error |
| Micro via hole size out of range | micro via hole 직경이 범위 밖(레이저 드릴 최소) | Error |
| Courtyards overlap | 풋프린트 courtyard끼리 겹침. custom rule `courtyard_clearance`(음수면 교차 허용) | Error |
| Footprint has no courtyard defined | 풋프린트에 `F.Courtyard`/`B.Courtyard` graphic shape 없음 | Ignore |
| Footprint has malformed courtyard | courtyard에 비폐쇄 shape 포함(여러 개라도 각각 폐쇄면 정상) | Error |
| Board has malformed outline | `Edge.Cuts`가 유효 외곽을 못 이룸(폐쇄·비자기교차 필요). 나노미터 스케일의 극소 graphic도 보고 | Error |
| Copper sliver | 작고 쐐기 모양의 copper 돌출 검출 | Warning |
| Solder mask aperture bridges items with different nets | 단일 soldermask 개구부가 다른 net copper 항목 다수를 노출(어셈블리 시 쇼트 위험) | Error |
| Copper connection too narrow | copper 연결이 설정 minimum connection width보다 좁게 necking | Warning |
| Track connected to post-machined or backdrilled layer | 트랙이 post-machining/backdrilling으로 제거된 레이어의 pad/via에 연결 | Error |
| Track endpoint not centered on via | 트랙 끝이 via 안이지만 via 중심이 아님(length tuner 길이 부정확) | Warning |
| Tuning profile track geometries | 트랙 geometry(폭/diff pair gap)가 tuning profile 값과 불일치 | Ignore |

#### Schematic parity DRC checks · #schematic_parity_drc_checks

| Violation | Description | Default Severity |
| --- | --- | --- |
| Duplicate footprints | 동일 refdes 풋프린트가 보드에 다수(회로도 심볼에 대응하지 않는 경우는 미보고) | Warning |
| Missing footprint | 회로도 심볼은 있는데 보드에 풋프린트가 없음 | Warning |
| Extra footprint | 회로도 심볼 없이 보드에만 풋프린트 존재 | Warning |
| Footprint attributes don’t match symbol | 풋프린트 `Value`/DNP/Exclude from BOM이 심볼과 다름, 또는 할당 풋프린트가 실제와 다름. Update PCB/Schematic으로 동기화 | Warning |
| Footprint doesn’t match symbol’s footprint filters | 풋프린트가 심볼의 footprint filter와 불일치(필터 없으면 미발생) | Ignore |
| Pad net doesn’t match schematic | 풋프린트 pad와 심볼 pin 간 net 불일치(또는 대응 pin/pad 부재) | Warning |
| Missing connection between items | 같은 net의 두 copper 객체가 보드에서 미연결 | Error |

#### Signal integrity DRC checks · #signal_integrity_drc_checks

| Violation | Description | Default Severity |
| --- | --- | --- |
| Track length out of range | diff pair 트랙이 설정 min/max 길이 벗어남. custom rule `length` constraint | Error |
| Skew between tracks out of range | 트랙 길이와 대상 트랙 최대 길이 차가 설정 max skew 초과. custom rule `skew` constraint | Error |
| Too many or too few vias on a connection | net의 via 수가 설정 min/max 벗어남. custom rule `via_count` constraint | Error |
| Differential pair gap out of range | diff pair gap이 설정 min/max 벗어남(coupled 구간만). custom rule `diff_pair_gap`. net class optimal gap은 라우터용일 뿐 min/max 미설정 | Error |
| Differential uncoupled length too long | diff pair의 uncoupled 구간이 설정 max보다 김(비평행 = uncoupled). custom rule `diff_pair_uncoupled` constraint | Error |

#### Readability DRC checks · #readability_drc_checks

| Violation | Description | Default Severity |
| --- | --- | --- |
| Silkscreen clearance | silkscreen 객체가 다른 silkscreen 객체와 교차(가독성 영향). shape끼리만의 교차는 미보고. board-level silkscreen minimum item clearance 또는 custom rule `silk_clearance`. 음수면 교차 허용 | Warning |
| Silkscreen clipped by solder mask | silkscreen이 solder mask 개구부와 교차(맨 copper/기판에 인쇄될 수 있음) | Warning |
| Silkscreen clipped by board edge | silkscreen이 board edge와 교차(보드 밖으로 일부 벗어남). `silk_clearance` constraint | Warning |
| Text height out of range | 텍스트 높이가 범위 밖. board-level minimum은 board setup constraints, max·세부는 custom rule | Warning |
| Text thickness out of range | 텍스트 두께가 범위 밖. KiCad stroke font는 thickness 설정값, 외부 폰트는 glyph 최소 물리 두께 | Warning |
| Mirrored text on front layer | front layer 텍스트에 mirrored 속성(앞에서 거꾸로 보임) | Ignore |
| Non-Mirrored text on back layer | back layer 텍스트에 mirrored 속성 없음(뒤에서 거꾸로 보임) | Ignore |

#### Miscellaneous DRC checks · #miscellaneous_drc_checks

| Violation | Description | Default Severity |
| --- | --- | --- |
| Items not allowed | 허용되지 않는 위치에 객체 배치(keep out rule area 또는 `disallow` custom rule) | Error |
| Copper zones intersect | 다른 net의 copper zone 충돌(쇼트) | Error |
| Isolated copper fill | copper fill 일부가 같은 net의 다른 copper에 미연결(island) | Warning |
| Footprint is not valid | net tie group에 풋프린트에 없는 pad 포함, 또는 pad가 둘 이상의 net tie group에 속함 | Error |
| Padstack is questionable | pad 설정이 실수일 가능성(예: copper pad 없는 PTH, BGA 속성 PTH, solder paste 있는 connector pad, 양면 copper SMD, outer layer copper 없는 SMD, annulus 없는 PTH, hole이 copper 밖, solder mask clearance 문제, 음수 local clearance, 과도한 corner chamfer/radius 등) | Warning |
| PTH inside courtyard | 풋프린트 PTH pad가 다른 풋프린트 courtyard 안(heatsink pad 속성은 허용) | Error |
| NPTH inside courtyard | 풋프린트 NPTH pad가 다른 풋프린트 courtyard 안 | Error |
| Item on a disabled copper layer | 항목(pad/via 등)이 stackup에 없는 copper layer에 존재 | Error |
| Unresolved text variable | 보드/drawing sheet의 text variable이 해석 안 됨(값 미정의) | Error |
| Footprint component type doesn’t match footprint pads | 풋프린트 component type(SMD/THT/unspecified)이 pad 기준 예상과 불일치. unspecified면 비교 안 함 | Ignore |
| Footprint field does not match symbol field | 심볼에 있는 필드가 풋프린트에 없거나 값이 다름 | Warning |
| Footprint not found in libraries | 보드 풋프린트가 활성 라이브러리(global/project 테이블)에 없음. update/compare 불가 | Warning |
| Footprint doesn’t match copy in library | 보드 풋프린트가 라이브러리 버전과 다름. Compare Footprint with Library로 비교·업데이트 가능 | Warning |
| Through hole pad has no hole | THT 풋프린트 pad에 hole 없음 | Error |

### User-definable DRC violations · #text-var-drc

- 특수 text variable로 DRC warning/error를 수동 트리거 가능 — 후속 검토 대상을 플래그할 때 유용.
- 사용: 텍스트 항목/text box에 `${DRC_ERROR <violation name>}` 또는 `${DRC_WARNING <violation name>}` 입력(어느 보드 레이어든). DRC 실행 시 해당 이름의 위반 생성. 이 변수는 빈 문자열로 해석되고, 중괄호 뒤 텍스트는 위반 description에 포함. 변수는 텍스트 객체의 **맨 앞**에 있어야 트리거됨.
- 예: `${DRC_ERROR TODO}Length match tracks` → 보드엔 "Length match tracks"만 표시, "TODO" 이름의 DRC error 생성.

### DRC report file · #drc_report_file

- DRC 다이얼로그의 **Save…​** 버튼으로 리포트 저장. plaintext(`.rpt`) 또는 JSON 형식.
- 💡 **NOTE:** `kicad-cli` 도구로도 text(`.rpt`)/JSON 리포트 생성 가능.

## Board Statistics · #board-statistics

- 보드 크기와 각종 항목 개수 등 보드 내용 요약을 보여주는 다이얼로그. **Inspect** → **Show Board Statistics**.
- **General** 탭 — 객체 개수:
  - Footprints: type(THT/SMD/unspecified) 및 board side별
  - Pads: type(THT/SMD/connector/NPTH)별
  - Vias: type(through/blind/buried/micro)별
  - 보드 치수, 면적, 전/후면 copper 면적, 그 외 제조 기술 통계(minimum track width, minimum track clearance, minimum drill diameter)
- 옵션:
  - **Subtract holes from board area**: 체크 시 through hole 면적을 보드 면적에서 제외.
  - **Subtract holes from copper areas**: 체크 시 copper 면적에서 through hole 면적 제외.
  - **Exclude footprints with no pads**: 체크 시 pad 없는 풋프린트를 개수에서 제외.
- **Drill Holes** 탭 — 보드의 고유 드릴 hole 유형별로 특성(shape, X/Y size, plating, pad/via type, start/stop layer)과 개수 나열.
- **Generate Report File…​** 버튼으로 파일 저장.

## Measurement tool · #measurement-tool

- PCB 상 점 사이 거리·각도를 측정하는 도구.
- 활성화: 우측 툴바 measurement 아이콘, 또는 단축키 `Ctrl`+`Shift`+`M`. 활성 후 클릭으로 시작점, 다시 클릭으로 측정 완료.
- 표시: 총(radial) 거리, X/Y 방향 거리, 수평 기준 각도 — 즉 Cartesian과 radial(polar) 거리 모두.
- 💡 **NOTE:** 빠른 일회성 측정용 — 측정값은 도구 활성 동안만 표시된다. 출력물/플롯에 영구 표시되는 치수는 Dimension 도구를 사용.

## Find tool · #find_tool

- PCB의 텍스트(refdes, 풋프린트 필드, graphic text)를 검색. 매치 시 캔버스가 줌·중앙 정렬되고 텍스트가 하이라이트됨. 상단 툴바 Find 버튼으로 실행.
- 옵션:

| Option | 설명 |
| --- | --- |
| Match case | 대소문자 구분 여부 |
| Whole words only | 완전한 단어만 매치(해제 시 부분 매치) |
| Wildcards | `?`=임의 한 글자, `*`=임의 다수 글자. 활성 시 부분 매치 안 됨(`abc*`는 `abcd` 매치, `abc`는 안 됨) |
| Wrap | 마지막 hit 후 첫 hit로 순환 |
| Search footprint reference designators | refdes 검색 여부 |
| Search footprint values | value 필드 검색 여부 |
| Include hidden fields | 숨겨진 풋프린트 필드 검색 여부 |
| Search other text items | graphical text 및 value/reference 외 풋프린트 필드 등 기타 텍스트 검색 여부 |
| Search DRC markers | 보드 DRC 마커의 위반 description 검색 여부 |
| Search net names | net 이름 검색 여부 |

## Search panel · #search_panel

- 풋프린트, zone(copper zone·rule area), net, ratsnest(미라우팅 세그먼트), 텍스트, 그룹, 드릴 정보를 나열하는 도킹 패널.
- 표시/숨김: **View** → **Panels** → **Search**, 또는 `Ctrl`+`G`.
- 검색 문자열로 필터 가능(미사용 시 전체 나열). 항목별 필터 기준:
  - Footprints: 필드 내용. config 메뉴의 **Search Hidden Fields**로 숨김 필드 포함, **Search Metadata**로 메타데이터(library link, description, keywords) 포함.
  - Zones: zone/rule area 이름.
  - Net·ratsnest: net 이름.
  - Text(text/textbox/dimension): 텍스트 내용.
  - Groups: 그룹 이름.
  - Drills: 임의 컬럼.
- 컬럼 헤더 클릭으로 오름/내림차순 정렬.
- 필터는 wildcard(`*`, `?`)와 정규식(슬래시로 감싸기, 예 `/footprint value/`) 지원.
- 항목 클릭 시 캔버스에서 선택(config 설정에 따라 pan/zoom). 더블클릭 시 properties 다이얼로그(net·ratsnest는 net classes 다이얼로그) 오픈.

## 3D Viewer · #threed-viewer

- 보드와 부품의 3차원 뷰. 시점 변경, 부품 종류별 표시/숨김, PCB 에디터↔3D 뷰어 cross-probe, raytraced 렌더 생성 가능.
- 표시: **View** → **3D Viewer**, 또는 `Alt`+`3`.
- 💡 **NOTE:** 3D 모델 파일이 존재하고 풋프린트에 할당된 경우에만 모델이 표시됨. KiCad 표준 라이브러리의 다수 풋프린트는 아직 모델 파일이 없으나(향후 생성 대비) 경로만 가질 수 있음.

### Navigating the 3D view · #navigating_the_3d_view

- 좌클릭 드래그 = orbit(기본 회전 중심은 보드 centroid). `Space`로 커서 위치를 새 pivot으로 재설정.
- 휠 스크롤 = 줌. `Ctrl`+스크롤 = 좌우 pan, `Shift`+스크롤 = 상하 pan. 가운데 버튼 드래그 = pan.
- **3D Navigator**: 6개 구(Front/Back/Left/Right/Top/Bottom)로 표준 직교 뷰에 즉시 접근하는 위젯. 구 클릭으로 카메라 재배향. **Preferences** → **Show 3D Navigator**로 표시/숨김.
- **View** → **3D Grid** 메뉴로 그리드 크기 설정. **Preferences** → **Show Model Bounding Boxes**로 부품 bounding box 표시.
- PCB 에디터와 3D 뷰어가 모두 열려 있으면 PCB에서 풋프린트 선택 시 3D 뷰어에서도 하이라이트. 색상: **Preferences** → **Preferences…​** → **3D Viewer** → **Realtime Renderer** → **Selection Color**.

### Appearance Manager · #appearance_manager

- 뷰어 우측 패널로 객체/레이어 종류별 visibility, color, opacity 관리.
- 각 항목은 visibility 아이콘으로 표시/숨김. PCB 레이어는 색상 스와치 더블클릭으로 color/opacity 편집.
- **use board stackup colors**: Board Setup의 Physical Stackup editor 색상 사용. **use PCB editor copper colors**: PCB 에디터 copper 색상 사용.
- **Preset** 선택기로 외형 구성 저장/로드. `Ctrl`+`Tab`로 preset 순환(Ctrl 누른 채 Tab 반복). 내장 preset: "Follow PCB Editor", "Follow PCB Plot Settings", "legacy colors".
- **Viewports** 선택기로 viewport 저장/복원. `Shift`+`Tab`로 순환(Shift 누른 채 Tab 반복).

### Generating images with the 3D Viewer · #generating_images_with_the_3d_viewer

- 현재 뷰 이미지 저장: **File** → **Export Image…​**(출력 크기·해상도 선택 가능). copy 버튼 또는 **Edit** → **Copy 3D Image to Clipboard**로 클립보드 복사.
- **Raytracing** 모드: 더 물리적으로 정확한 렌더(느리지만 시각적으로 우수). raytracing 버튼 또는 **Preferences** → **Raytracing**. raytracing 모드에서는 3D grid·selection highlight 미표시.
- 색상·렌더링 옵션(두 모드 모두): **Preferences** → **Preferences…​** → **3D Viewer**.

### 3D viewer controls · #3d_viewer_controls

- 대부분의 뷰 옵션은 상단 툴바로 제어. 💡 **NOTE:** 툴바 내용은 3D Viewer Preferences의 **Toolbar** 페이지에서 편집 가능.

| 아이콘 | 기능 |
| --- | --- |
| import3d | Reload the 3D model |
| copy | Copy 3D image to clipboard |
| ray tracing | Render current view using raytracing |
| refresh | Redraw |
| zoom in | Zoom in |
| zoom out | Zoom out |
| zoom fit | Fit drawing in display area |
| rotate cw x | Rotate X clockwise |
| rotate ccw x | Rotate X counterclockwise |
| rotate cw y | Rotate Y clockwise |
| rotate ccw y | Rotate Y counterclockwise |
| rotate cw z | Rotate Z clockwise |
| rotate ccw z | Rotate Z counterclockwise |
| flip board | Flip board view |
| left/right/up/down | Pan board left/right/up/down |
| ortho | Enable/disable orthographic projection |
| layers manager | Show/hide the Appearance Manager |

## Net inspector · #net-inspector

- 보드의 모든 net 통계를 보는 도킹 패널. net 추가/제거/이름 변경도 가능.
- 열기: Appearance 패널 Nets 섹션 상단의 list nets 아이콘, 또는 **View** → **Panels** → **Net Inspector**.
- net 더블클릭 또는 우클릭 **Highlight Selected Net**으로 하이라이트(다중 선택 가능). 우클릭 **Clear Net Highlighting**으로 해제.
- 컬럼 제목 클릭으로 정렬. Filter 박스로 제한(기본은 net name + net class 둘 다, config 메뉴의 **Filter by Net Name**/**Filter by Netclass**로 한정).
- 기본적으로 미연결 net과 pad 없는 net은 미표시. config 메뉴의 **Show Unconnected Nets**/**Show Zero Pad Nets**로 표시.
- net별 통계:
  - **Pad Count**: net의 pad 수(SMD+THT).
  - **Via Count**: net의 via 수.
  - **Via Length**: net의 모든 via 길이 합(각 via는 항상 full height 계산 = Via Count × stackup height).
  - **Track Length**: net의 모든 트랙 세그먼트 길이 합(topology 무시, 분기 모두 포함). copper layer별로도 보고.
  - **Die Length**: net 패드들의 Pad to Die Length 값 합.
- 컬럼 표시/숨김: config → **Show / Hide Columns**. config → **Save Net Inspector Report**로 CSV 저장(필터/숨김과 무관하게 전체 net·컬럼 포함).

### Grouping nets · #grouping_nets

- net을 그룹화해 정리·조회 가능. 각 그룹은 멤버 전체의 합산 통계를 단일 net처럼 표시(예: 직렬 저항으로 나뉜 신호의 두 net을 묶어 총 길이 분석).
- net class별 그룹: config → **Group by netclass**.
- 커스텀 그룹: config → **Add Custom Group** 후 패턴 지정. net 이름에 패턴 포함 시 그룹에 묶임(예: `CAN`은 `CAN_RX`/`CAN_TX` 매치). 대소문자 무시. 슬래시로 감싸 정규식 사용 가능(예: `/^AN/`은 `AN0`,`AN1`엔 매치, `CAN`엔 안 됨).
- 그룹 제거: config 또는 우클릭 → **Remove Selected Custom Group**. 전체 제거: config → **Remove All Custom Groups**.

### Editing nets · #editing_nets

- net 생성/삭제/이름 변경:
  - 생성: 우클릭 → **Add Net** 후 이름 입력.
  - 삭제: 우클릭 → **Delete Selected Net**(다중 선택 시 모두 삭제).
  - 이름 변경: 우클릭 → **Rename Selected Net** 후 새 이름.
- 💡 **NOTE:** 보통 net은 보드에서 편집하지 않고 회로도에서 정의 후 Update PCB From Schematic으로 갱신하는 것이 권장됨. Net Inspector는 회로도를 쓰지 않는 대안 워크플로용.
- 💡 **NOTE:** 보드에서 수정한 net은 back-annotation으로 회로도를 갱신하기 전까지 회로도에 영향 없음.

### Differences between Net Inspector and Length Tuner · #differences_between_net_inspector_and_length_tuner

- 두 도구는 목적·계산 방식이 달라 net 길이를 다르게 보고한다. Net Inspector는 net의 각 트랙 세그먼트·via 길이를 단순 합산, length tuner는 두 점 사이 경로의 유효 전기 길이를 계산.
  - **Track length**: Net Inspector = 세그먼트 단순 합. Length tuner = 유효 전기 길이(패드 경유 최단 경로 최적화 포함).
  - **분기 topology**: Net Inspector = 모든 분기 포함. Length tuner = 점대점 길이로 가장 가까운 분기에서 멈춤.
  - **Via height**: Net Inspector = 항상 effective via height 포함(상/하단 모두 연결 시 full height, 아니면 연결 레이어 간 stackup height). Length tuner = 동일 방식이나 board constraint settings의 **use stackup height**가 켜진 경우에만 via 포함(꺼지면 via 미포함).

---

# Importing boards from other EDA tools · #importing-boards

- KiCad는 다양한 서드파티 EDA 도구의 PCB 설계를 임포트하며, 임포트된 보드는 KiCad 네이티브 포맷으로 변환된다. 변환 후 편집·design rule 조정·출력 모두 가능.
- ⚠️ **NOTE:** 임포트는 외부 파일에서 **새 KiCad 보드를 생성**하며, 기존 KiCad 설계에 병합하지 않는다. 임포트 후 저장해 `.kicad_pcb` 파일을 만들 것.

## Supported import formats · #supported_import_formats

| Source EDA Tool | File Extension(s) | Layer Mapping | Library Import |
| --- | --- | --- | --- |
| Altium Designer | `.PcbDoc` | Yes | Yes |
| Altium Circuit Maker | `.CMPcbDoc` | Yes | No |
| Altium Circuit Studio | `.CSPcbDoc` | Yes | No |
| Cadence Allegro | `.brd` | Yes | No |
| CADSTAR PCB Archive | `.cpa` | Yes | Yes |
| Eagle (Autodesk) | `.brd` (XML) | Yes | Yes |
| EasyEDA / JLCEDA Standard | `.json`, `.zip` | No | Yes |
| EasyEDA / JLCEDA Professional | `.epro`, `.zip` | No | Yes |
| Fabmaster | `.txt`, `.fab` | No | No |
| gEDA / Lepton EDA | `.pcb` | No | Yes |
| P-CAD 200x | `.pcb` (ASCII) | No | No |
| PADS (ASCII) | `.asc` | Yes | No |
| Solidworks PCB | `.SWPcbDoc` | Yes | No |

- 추가로 Specctra session(`.ses`) 임포트로 오토라우터 결과를 기존 보드로 가져올 수 있다(아래 별도 워크플로).

## How to import a board · #how_to_import_a_board

1. **File** → **Import** → **Non-KiCad Board File…​**.
2. 파일 다이얼로그에서 파일 형식 드롭다운을 원하는 포맷으로 변경.
3. 외부 보드 파일 선택 후 **Open**.
- 포맷에 따라 layer mapping 다이얼로그가 나타날 수 있다.
- 💡 **TIP:** Eagle·Allegro 등 일부 포맷은 `.brd` 확장자를 공유 — 적절한 파일 형식 필터를 선택하면 KiCad가 파일 내용으로 정확한 포맷을 자동 감지한다.

## Layer mapping · #layer_mapping

- 임포트 시 외부 파일의 레이어를 KiCad 레이어로 매핑하는 단계. 각 소스 레이어 옆 드롭다운으로 대상 KiCad 레이어 선택. best-guess 자동 매핑이 제공되나 반드시 검토할 것.
  - **Copper layers:** 특히 다층 보드의 inner layer가 올바른 copper layer로 매핑되는지 확인.
  - **Silkscreen/solder mask/paste:** front/back 대응 레이어로 매핑.
  - **Mechanical/documentation:** 적절한 User 레이어로 매핑하거나 불필요 시 unmapped.
  - **Unmapped layers:** *Unassigned*로 두면 해당 레이어 내용은 임포트에서 제외됨.
- Layer mapping 지원 포맷: Altium Designer, Altium Circuit Maker, Altium Circuit Studio, Cadence Allegro, CADSTAR, Eagle, PADS, Solidworks PCB.

## Post-import cleanup · #post_import_cleanup

1. **DRC 실행:** **Inspect** → **Design Rules Checker** — 임포트 중 발생한 문제 식별.
2. **Board setup 검토:** **File** → **Board Setup** — stackup, design rules, net classes 확인(임포트는 best-effort 변환).
3. **Footprint 확인:** 임포트 풋프린트는 보드 파일에 임베드됨 — KiCad 라이브러리 풋프린트로 교체 고려(3D 모델·최신 pad shape 활용).
4. **Zone 점검:** 임포트 후 zone fill 재계산 필요할 수 있음 — **Edit** → **Fill All Zones** (`B`).
5. **Net 할당 확인:** Nets inspector(**Inspect** → **Board Statistics**) 또는 개별 track/pad net 속성으로 net 이름·net class 검증.
6. **KiCad 프로젝트로 저장:** **File** → **Save As…​** — `.kicad_pcb`로 저장.
- 💡 **TIP:** 일부 importer는 하단 message panel에 메시지를 출력 — 미지원 기능·임포트 실패 항목 경고 확인.

## Format-specific notes · #format_specific_notes

### Altium Designer · #import-altium-designer
- `.PcbDoc`에 대한 포괄 지원. **지원:** 외곽·cutout, copper(최대 32층)·silkscreen·solder mask·paste·mechanical, track/arc/via(blind·buried 포함), pad(THT/SMD/custom), copper fill·polygon pour, 부품 배치·풋프린트 geometry, net 정보, design rules(부분), 임베디드 풋프린트 라이브러리.
- **제약:** 임베디드 OLE 객체 미임포트, 복잡 design rule은 단순화, diff pair rule은 best-effort, Situs 오토라우터/임베디드 시뮬레이션 미지원.
- 추가로 Altium 풋프린트 라이브러리(`.PcbLib`)·통합 라이브러리(`.IntLib`)를 footprint library manager로 직접 임포트 가능.

### Altium Circuit Maker · #import-altium-circuit-maker
- `.CMPcbDoc` — Altium Designer와 동일 기반 포맷. 동일하게 처리, layer mapping 지원.

### Altium Circuit Studio · #import-altium-circuit-studio
- `.CSPcbDoc` — Altium Designer와 유사 지원. layer mapping 적용, 동일 파싱 엔진.

### Cadence Allegro · #import-cadence-allegro
- 바이너리 `.brd` 직접 임포트. **지원:** 외곽, copper·signal routing, padstack·via, 부품 배치, net 정보, 자동 제안 layer mapping.
- **제약:** Allegro design rule·constraint 완전 임포트 안 됨, flex-circuit stackup 미지원, 일부 pad shape 근사.
- 💡 **NOTE:** Allegro `.brd`는 바이너리, Eagle `.brd`는 XML — KiCad가 내용으로 자동 식별.

### CADSTAR PCB Archive · #import-cadstar
- Zuken CADSTAR `.cpa`. **지원:** 외곽·template, 전체 copper stackup, track/via/copper pour, 부품 배치·풋프린트 geometry, net·net class, layer mapping, 풋프린트 라이브러리 임포트.
- **제약:** CADSTAR template area 근사/단순화, 일부 고급 constraint 미변환.

### Eagle (Autodesk) · #import-eagle
- XML 포맷 Eagle `.brd`(v6.x 이상) 성숙 지원. **지원:** 외곽, 전체 copper·signal layer, track/via/polygon, SMD/THT pad(annular ring 자동), 부품 배치·package geometry, netlist·net class, design rule(가능 시 변환), intelligent layer mapping, 임베디드 풋프린트 라이브러리.
- **제약:** ULP script·CAM job 미임포트, 일부 Eagle DRC rule 단순화, 바이너리 Eagle 파일(v6.x 이전)은 미지원(Eagle에서 XML로 재저장 필요).
- Eagle 풋프린트 라이브러리(`.lbr`)도 footprint library manager로 임포트 가능.
- 💡 **TIP:** Eagle 회로도 파일(`.sch`)은 KiCad Schematic Editor에서 임포트해 전체 설계를 가져올 수 있다.

### EasyEDA / JLCEDA Standard · #import-easyeda
- 웹 기반 EasyEDA(JLCEDA Standard). **파일:** `.json`, `.zip`. EasyEDA의 **Export EasyEDA** 옵션으로 생성.
- **지원:** 외곽, copper·routing, pad/via, 부품 배치, net 정보, 임베디드 풋프린트 라이브러리. **제약:** 일부 custom pad shape 부정확, panelization 데이터 미임포트.

### EasyEDA / JLCEDA Professional · #import-easyeda-pro
- 데스크톱 EasyEDA Professional. **파일:** `.epro`, `.zip`. 멀티보드 프로젝트는 board chooser 다이얼로그 표시.
- **지원:** 외곽, copper·routing, pad/via, 부품 배치, net 정보, 풋프린트 라이브러리(`.elibz`는 library manager로도 임포트). **제약:** EasyEDA Pro 고유 고급 기능 일부 미대응.

### Fabmaster · #import-fabmaster
- Valor/Mentor Fabmaster(`.txt`, `.fab`) — board geometry, 부품 배치, layer 정보 포함.
- **제약:** 제조 중심 데이터라 설계 의도(예: 회로 연결성) 누락 가능, layer mapping 비인터랙티브(자동 할당), net 정보 불완전 가능.

### gEDA / Lepton EDA · #import-geda
- 오픈소스 gEDA PCB·Lepton EDA. **파일:** `.pcb`.
- **지원:** layer·routing, via, element(부품) 배치, netlist, 풋프린트 라이브러리(gEDA `.fp`는 library manager로 임포트). **제약:** gEDA layer model이 단순해 일부 layer 할당 조정 필요.

### P-CAD · #import-pcad
- P-CAD 200x ASCII `.pcb`. (Altium에 인수 후 단종된 레거시 도구)
- **제약:** ASCII `.pcb`만 지원(바이너리 미지원), P-CAD design rule 미임포트, 일부 고유 기능 미대응.

### PADS · #import-pads
- Siemens(Mentor) PADS — ASCII·바이너리 모두 지원.
- **PADS ASCII (`.asc`)**: PADS Layout의 텍스트 export. PADS Layout의 **File** → **Export**에서 ASCII 형식 선택해 생성.
- **지원:** 외곽, board setup(layer stackup), copper·routing(track/via), pad·풋프린트, copper pour·zone, net 정보, text·dimension, keepout area, intelligent layer mapping.
- **제약:** 일부 PADS pad shape/padstack 근사, design rule·constraint best-effort 변환, reuse block 정의 일부 미보존.

### Solidworks PCB · #import-solidworks
- `.SWPcbDoc`(구 PCBWorks) — Altium 파생 포맷, Altium Designer importer와 코드 공유. layer mapping 지원. Altium Designer 임포트 고려사항이 동일 적용.

## Importing Specctra session files · #specctra-session-import

- Specctra DSN/SES는 외부 오토라우터용 워크플로 — 새 보드를 생성하지 않고 오토라우터의 라우팅 결과를 **기존** KiCad 보드에 적용.
1. 보드를 Specctra DSN으로 export: **File** → **Export** → **Specctra DSN…​**.
2. 외부 오토라우터를 `.dsn`에 실행해 session(`.ses`) 생성.
3. session 파일 임포트: **File** → **Import** → **Specctra Session…​**.
- KiCad가 `.ses`를 읽어 라우팅된 track·via를 보드에 추가. 임포트 성공하려면 보드의 풋프린트·net·외곽이 원래 export와 일치해야 함.
- 💡 **NOTE:** Specctra session 임포트는 라우팅만 추가하며 풋프린트·netlist·외곽은 수정하지 않는다.

---

# Generating outputs · #generating_outputs

- KiCad는 제조·외부 SW 연동에 유용한 다양한 포맷의 파일을 생성. File 메뉴의 여러 섹션에 위치:
  - **Fabrication Outputs**: PCB 제조 준비용 가장 일반적 작업.
  - **Export**: 외부 SW가 읽을 파일 생성.
  - **Plot**: PCB의 2D 라인 드로잉을 여러 포맷으로 export.
  - **Print**: PCB 뷰를 2D 프린터로 출력.

## Plotting (Gerber / PostScript / SVG / DXF / PDF) · #plotting

- Gerber가 PCB 제조용 기본 플롯 포맷. Gerber 생성: **File** → **Fabrication Outputs** → **Gerbers (.gbr)…​** → Plot 다이얼로그.
- Plot 다이얼로그는 PostScript/SVG/DXF/PDF 생성에도 사용. **File** → **Plot…​** 또는 상단 툴바 Plot 버튼으로도 열림. **Plot format** 드롭다운으로 포맷 선택.
- 대부분 옵션은 공통이며 일부는 포맷별 고유.
- **Plot** 버튼으로 생성, 메시지는 Output Messages 패널에 표시(체크박스 필터).
- **Generate Drill Files…​** = Generate Drill Files 다이얼로그, **Run DRC…​** = DRC 실행.

### Plotting options · #plotting_options

| Option | 설명 |
| --- | --- |
| Include Layers | 보드에 쓰인 모든 레이어를 활성화. 비활성 레이어는 플롯 안 됨 |
| Plot on All Layers | 선택 레이어를 각 base 레이어 플롯에 추가(위에 겹쳐 플롯). 화살표 버튼으로 순서 조정(하위 항목이 나중에=위에 플롯) |
| Design variant | 플롯할 design variant 지정 |
| Output directory | 저장 위치. 상대경로면 프로젝트 디렉토리 기준 |
| Plot drawing sheet | 활성 시 각 레이어에 drawing sheet 테두리·title block 플롯. Gerber 플롯 시 보통 비활성 권장 |
| Subtract soldermask from silkscreen | 활성 시 soldermask 미덮임 영역의 silkscreen 자동 제거 |
| Indicate DNP on fabrication layers | 활성 시 `F.Fab`/`B.Fab`에 DNP 풋프린트 표시. **Hide**(플롯 제외) 또는 **Cross-out**(X 표시) |
| Sketch pads on fabrication layers | 활성 시 fab 레이어에 pad 외곽 그림. **Include pad numbers** 시 pad 번호도 |
| Drill marks | Gerber 외 포맷에서 드릴 hole 위치 마크. 실제 크기 또는 더 작은 크기 |
| Scaling | 1:1 외 scale 지원 포맷에서 plot scale 설정. Auto는 지정 page 크기에 맞춤 |
| Use drill/place file origin | 활성 시 좌표 원점 = drill/place file origin. 비활성 시 absolute origin(워크시트 좌상단) |
| Mirrored plot | 일부 포맷에서 수평 미러 출력 |
| Negative plot | 일부 포맷에서 negative 모드(빈 공간에 shape, 객체 자리에 빈 공간) |
| Check zone fills before plotting | 활성 시 출력 전 zone fill 검사·재필. 비활성 시 출력이 부정확할 수 있음! |

- 💡 **NOTE:** KiCad 9.0 이전엔 플롯 시 via tenting 전역 제어가 있었으나, 9.0부터는 Board Setup에서 전역 제어되고 각 via properties에서 override 가능.

### Gerber options · #gerber_options

| Option | 설명 |
| --- | --- |
| Use Protel filename extensions | 활성 시 Protel 기반 확장자(`.GBL`, `.GTL` 등), 비활성 시 `.gbr` |
| Generate Gerber job file | 활성 시 Gerber job file(`.gbrjob`) 생성(stackup·재질·finish 정보 포함) |
| Coordinate format | Gerber 좌표 저장 방식 — 제조사 권장값 확인 |
| Use extended X2 format | 활성 시 X2 포맷(netlist 등 확장 속성 포함). 구형 CAM과 비호환 가능 |
| Include netlist attributes | 활성 시 CAM 검증용 netlist 정보 포함(X2 비활성 시 Gerber 주석으로) |
| Disable aperture macros | 활성 시 모든 shape를 primitive로 플롯. 구형/버그 CAM 호환용으로만 |

### PostScript options · #postscript_options
- **Scale factor:** 보드→PostScript 좌표 스케일. X/Y 다르게 주면 왜곡(출력 장치 스케일 보정용).
- **Track width correction:** 플롯 시 track/via/pad 크기에 더하거나(음수면 빼는) 전역 보정.
- **Force A4 output:** 활성 시 보드 크기와 무관하게 A4 출력.

### SVG options · #svg_options
- **Precision:** 좌표 저장 유효 자릿수.
- **Output mode:** color 또는 black and white.
- **Fit page to board:** 활성 시 SVG 크기 = 보드 외곽 크기.

### DXF options · #dxf_options
- **Plot graphic items using their contours:** 두께 있는 shape 처리 — 활성 시 외곽 contour, 비활성 시 centerline(두께 미반영).
- **Use KiCad font to plot text:** 활성 시 텍스트를 KiCad 폰트의 graphic shape로, 비활성 시 DXF text 객체(다른 폰트·위치/크기 차이).
- **Single document:** 활성 시 선택 레이어 전체를 단일 DXF에(각 PCB 레이어 = DXF 레이어).
- **Export units:** DXF 단위(DXF는 단위계가 없으므로 임포트할 SW와 동일 단위로 export).

### PDF options · #pdf_options
- **Output mode:** color 또는 black and white.
- **Generate property popups for front footprints:** 활성 시 전면 풋프린트 부품 정보의 인터랙티브 팝업 추가.
- **Generate property popups for back footprints:** 후면 풋프린트용(상세는 Schematic Editor 문서 참조).
- **Generate metadata from AUTHOR and SUBJECT variables:** `AUTHOR`/`SUBJECT` 프로젝트 text variable로 PDF Author/Subject 속성 설정.
- **Single document:** 활성 시 각 레이어를 단일 PDF 내 개별 시트로, 비활성 시 레이어마다 별도 PDF.
- **Background color:** PDF 배경색(black and white 모드에선 불가).

## Drill files · #drill-files

- 대부분 제조 공정에 필요한 CNC 드릴 파일을 Excellon 또는 Gerber X2로 생성. 드릴 위치를 그린 drill map도 생성 가능.
- 열기: **File** → **Fabrication Outputs** → **Drill Files (.drl)…​**, 또는 Plot 다이얼로그의 **Generate Drill Files…​**.
- 옵션:

| Option | 설명 |
| --- | --- |
| Output folder | 저장 폴더(상대경로는 프로젝트 기준) |
| Drill file format | Excellon(대부분 제조사) 또는 Gerber X2 |
| Mirror Y axis | Excellon에서 Y 좌표 미러. 외주 제조 시 일반적으로 미사용(자체 제작 편의용) |
| Minimal header | Excellon 최소 헤더. 제조사 요청 시에만 |
| PTH and NPTH in single file | 기본은 plated/non-plated를 별도 Excellon. 활성 시 단일 파일 병합(제조사 요청 시에만) |
| Use alternate drill mode for oval holes | oval hole 표현 방식. 비활성 시 route 명령(대부분 정확). 제조사 요청 시에만 alternate |
| Generate map | drill map 생성 여부·포맷(Postscript/Gerber X2/DXF/SVG/PDF) |
| Origin | **Absolute**(좌상단 page origin) 또는 **Drill/place file origin** |
| Drill units | 드릴 좌표·크기 단위 |
| Zeros | Excellon zero 포맷 — 제조사 권장 따름 |

## IPC-2581 · #ipc-2581-export

- 보드의 완전한 제조·어셈블리 데이터를 담은 XML. 제조사가 받으면 Gerber·drill·placement 파일을 대체 가능.
- 생성: **File** → **Fabrication Outputs** → **IPC-2581 File (.xml)…​**.
- 옵션:

| Option | 설명 |
| --- | --- |
| File | 생성 파일명(상대경로는 프로젝트 기준) |
| Units | **millimeters** 또는 **inches** |
| Precision | 소수점 자릿수 |
| Version | IPC-2581 표준 버전 (B 또는 C) |
| Compress output | 활성 시 ZIP 압축 |
| Internal ID | BOM internal ID 컬럼용 풋프린트 필드(생성 unique ID 또는 임의 필드) |
| Manufacturer P/N | BOM 제조사 부품번호 컬럼용 필드(생략 가능) |
| Manufacturer | BOM 제조사 컬럼용 필드(생략 가능) |
| Distributor P/N | BOM 유통사 부품번호 컬럼용 필드(생략 가능) |
| Distributor | BOM 유통사 컬럼용 필드(생략 가능) |
| BOM revision | BOM revision 값(생략 시 회로도 root sheet의 `Revision` 필드 사용) |

## ODB++ · #odb-export

- 완전한 제조·어셈블리 데이터를 담은 파일 데이터베이스. 제조사가 받으면 Gerber·drill·placement 파일 대체 가능.
- 생성: **File** → **Fabrication Outputs** → **ODB++ Output File…​**.
- 옵션:

| Option | 설명 |
| --- | --- |
| Output file | 생성 파일명(상대경로는 프로젝트 기준) |
| Units | **millimeters** 또는 **inches** |
| Precision | 소수점 자릿수 |
| Compression format | **ZIP**/**TGZ**/**none**(none이면 폴더 출력) |

## Component placement (position) files · #component_placement_position_files

- 각 부품의 중심 위치·방향을 나열한 텍스트 파일. 픽앤플레이스 머신 프로그래밍용, 완전 조립 PCB 주문 시 필요할 수 있음.
- 생성: **File** → **Fabrication Outputs** → **Component Placement (.pos, .gbr)…​**.
- 💡 **NOTE:** 풋프린트에 "Exclude from position files"가 켜져 있으면 placement 파일에 미포함(물리 부품 아닌 풋프린트 제외용). DNP·"Exclude from BOM" 부품도 선택적으로 제외 가능.
- 옵션:

| Option | 설명 |
| --- | --- |
| Design variant | placement에 사용할 variant 선택 |
| Output directory | 저장 위치 |
| Format | plain text(UTF-8) / CSV / Gerber X3 |
| Units | 위치 단위 |
| Include only SMD footprints | 활성 시 SMD fab 속성 풋프린트만 |
| Exclude all footprints with through hole pads | 활성 시 THT pad 보유 풋프린트 제외(fab type이 SMD라도) |
| Exclude all footprints with the Do Not Populate flag set | 활성 시 DNP 풋프린트 제외 |
| Exclude all footprints with the Exclude from BOM flag set | 활성 시 Exclude from BOM 풋프린트 제외 |
| Include board edge layer | Gerber placement에서 보드 외곽 포함 여부 |
| Use drill/place file origin | 활성 시 drill/place file origin 기준, 비활성 시 page origin(좌상단) |
| Use negative X coordinates for footprints on bottom layer | 활성 시 bottom layer 풋프린트 X 좌표 반전 |
| Generate single file with both front and back positions | 활성 시 전·후면을 단일 파일, 비활성 시 별도 파일 |

## Footprint reports · #footprint_reports

- 보드 내 모든 풋프린트의 텍스트 리포트 생성. **File** → **Fabrication Outputs** → **Footprint Report (.rpt)…​**. 설정 옵션 없음.

## IPC-D-356 netlists · #ipc_d_356_netlists

- 베어 PCB 제조 검사에 적합한 IPC-D-356 포맷 netlist 생성. **File** → **Fabrication Outputs** → **IPC-D-356 Netlist File…​**.
- 옵션 하나: **Do not export unconnected pads** 체크 시 net 미연결 pad 제외.

## Bill of Materials · #bill_of_materials

- 보드의 모든 풋프린트를 담은 CSV BOM 생성. **File** → **Fabrication Outputs** → **Bill of Materials…​**. 설정 옵션 없음.
- ⚠️ **WARNING:** 이 BOM exporter는 레거시용이며 권장되지 않음. 대신 Schematic Editor의 BOM Exporter(다중 포맷·고설정성) 사용 권장.

## Printing · #printing

- 보드 뷰를 표준 프린터로 출력. **File** → **Print…​**.
- 💡 **NOTE:** PDF 프린터로 PDF를 만들 수도 있으나, 더 설정 가능하고 정확한 Plot 기능 권장.
- 옵션:

| Option | 설명 |
| --- | --- |
| Include layers | 출력 레이어 선택(미선택은 비표시). 우클릭 = 레이어 선택 명령 |
| Output mode | black and white 또는 full color |
| Print drawing sheet | 활성 시 page 테두리·title block 출력 |
| Print according to objects tab of appearance manager | 활성 시 Objects 탭에서 숨긴 객체를 출력에서 숨김 |
| Print background color | full color 시 뷰 배경색 출력 여부 |
| Use a different color theme for printing | full color 시 다른 color theme 사용 |
| Drill marks | 드릴 hole을 실제 크기/작은 크기로 표시 또는 숨김 |
| Print mirrored | 활성 시 수평 미러 출력 |
| Print one page per layer | 활성 시 레이어마다 개별 page. 이때 **Print board edges on all pages**로 각 page에 Edge.Cuts 추가 여부 |
| Scale | Page Setup 기준 출력 스케일 |

## Specctra DSN · #specctra_dsn

- 서드파티 오토라우터용 파일 생성. **File** → **Export** → **Specctra DSN…​**. 설정 옵션 없음.

## GenCAD · #gencad

- 제조·테스트·타 SW 임포트용 GenCAD 파일 생성. **File** → **Export** → **GenCAD…​**.
- 옵션:
  - **Flip bottom footprint padstacks:** 활성 시 bottom-side 풋프린트용 flipped padstack 정의 추가.
  - **Generate unique pin names:** 활성 시 핀 이름에 접미사 추가(동일 이름 핀 방지).
  - **Generate a new shape for each footprint instance:** 활성 시 동일하더라도 모든 인스턴스에 고유 풋프린트 출력.
  - **Use drill/place file origin as origin:** 활성 시 좌표를 drill/place file origin 기준.
  - **Save the origin coordinates in the file:** 활성 시 origin 좌표 포함, 비활성 시 origin (0,0).

## VRML · #vrml-exporter

- PCB와 풋프린트 지정 VRML을 담은 VRML(`.wrl`) 3D 모델 생성(시각 우선·치수 정밀도 비중요 용도). **File** → **Export** → **VRML…​**.
- 옵션:
  - **User defined origin:** 활성 시 display origin 기준 origin 수동 지정, 비활성 시 display origin.
  - **Units:** 모델 단위계.
  - **Ignore 'Do not populate' components:** 활성 시 DNP 풋프린트 VRML 제외.
  - **Ignore 'Unspecified' components:** 활성 시 Unspecified type 풋프린트 제외.
  - **Copy 3D model files to 3D model path:** 활성 시 참조 VRML을 하위 디렉토리로 복사하고 참조(디렉토리명 = footprint 3D model path 필드), 비활성 시 임베드.
  - **Use relative paths to model files in board VRML file:** 활성 시 외부 모델 상대경로, 비활성 시 절대경로(위 copy 옵션 활성 시에만 사용 가능).

## IDF · #idf-exporter

- 기계 CAD 연동용 IDFv3 board(`.emn`)·library(`.emp`) 파일 export. 외곽·cutout, 모든 pad·mounting through hole(slotted 포함), 부품 외곽을 export(기타 IDFv3 엔티티는 미export).
- 💡 **NOTE:** 모델 포함 전에 풋프린트에 IDF 부품 모델을 부착해야 함(부착법은 footprint 문서, IDF 지침은 Advanced Topics 문서 참조).
- 실행: **File** → **Export** → **IDFv3…​**.
- 옵션:
  - **Set board reference point:** 모델 reference point를 display origin 기준 지정(미선택 시 PCB centroid).
  - **Output units:** millimeters 또는 mils.
  - **Ignore 'Do not populate' components:** 활성 시 DNP 제외.
  - **Ignore 'Unspecified' components:** 활성 시 Unspecified type 제외.
- 출력은 기계 CAD에서 보거나 `idf2vrml` 도구로 VRML 변환 가능.

## 3D models (STEP / GLB / BREP / XAO / PLY / STL / STPZ / U3D / PDF) · #_3d-export

- PCB와 풋프린트 지정 STEP 파일로 3D 모델 생성. 지원 포맷: STEP, GLB(binary glTF), BREP(OCCT 네이티브), XAO(SALOME/Gmsh), PLY, STL, STPZ(GZIP STEP), U3D, PDF.
- 💡 **NOTE:** KiCad 라이브러리는 STEP·VRML(`.wrl`) 모델을 모두 포함하나 풋프린트는 VRML만 참조. VRML은 STEP export에 미포함되지만, **substitute similarly named models** 옵션 활성 시 동명 STEP을 대신 포함.
- 실행: **File** → **Export** → **STEP / GLB / BREP / XAO / PLY / STL…​**.
- **Format** 드롭다운으로 포맷, **File** 선택기로 파일명, **Variant** 드롭다운으로 design variant 선택.

### Board options · #board_options
- **Export board body:** 활성 시 board body(non-copper) 모델링.
- **Cut vias in board body:** 활성 시 conductor layer 미모델링이어도 via hole을 body에 cut.
- **Export silkscreen:** 활성 시 silkscreen 모델링(평면 face, 비입체).
- **Export solder mask:** 활성 시 solder mask 모델링(평면 face).
- **Export components:** 활성 시 부품 3D 모델 포함. **All components** / **Only selected** / **Components matching filter**(refs 필터, wildcard·콤마 지원, 예 `C1,R*`).

### Conductor options · #conductor_options
- **Export tracks and vias:** 활성 시 outer layer track·via 모델링.
- **Export pads:** 활성 시 pad 모델링.
- 💡 **NOTE:** exporter가 각 pad에 0.005mm 금속 두께를 추가(pad를 주변 금속과 별개 face로 분리). 원치 않으면 `kicad-cli`의 `--no-extra-pad-thickness` 옵션 사용.
- **Export zones:** 활성 시 outer layer zone 모델링.
- **Export inner conductor layers:** 활성 시 inner conductor layer 모델링.
- **Fuse shapes (time consuming):** 활성 시 교차 geometry를 단일 shape로 융합(export 시간 크게 증가).
- **Fill all vias:** 활성 시 conductor layer에 via hole을 cut하지 않음.
- **Net filter (supports wildcards):** 입력 시 매치 net의 conductor만 모델링(예: `/tx_*`).

### Coordinates · #coordinates
- **Coordinates:** 모델 origin 선택. **user defined origin** 시 display origin 기준 origin 수동 지정.

### Other options · #other_options
- **Ignore 'Do not populate' components:** 활성 시 DNP 부품 제외.
- **Ignore 'Unspecified' components:** 활성 시 Unspecified type 부품 제외.
- **Substitute similarly named models:** VRML은 STEP/BREP/XAO에 못 쓰므로, 활성 시 동명 STEP 모델을 대신 포함. KiCad 라이브러리 풋프린트는 VRML을 지정하므로 라이브러리 풋프린트의 3D 모델을 이 다이얼로그로 export하려면 이 옵션을 켜야 함.
- **Overwrite old file:** 활성 시 동명 파일 덮어쓰기.
- **Don’t write P-curves to STEP file:** 활성 시 parametric curve 비활성(파일 크기 감소, 일부 SW 호환성 저하 가능).
- **Board outline chaining tolerance:** 두 점을 일치로 간주할 최소 거리. 외곽이 비연속이면 tolerance를 높여볼 것.

## Footprint association (CMP) files · #footprint_association_cmp_files

- PCB↔회로도 간 풋프린트 할당·일부 필드 동기화용 CMP 파일. export: **File** → **Export** → **Footprint Association (.cmp) File…​**, 회로도 import: Schematic Editor의 **File** → **Import** → **Footprint Assignments**. 매우 제한적 back-annotation이므로 Update Schematic from PCB 권장. 설정 옵션 없음.

## Hyperlynx · #hyperlynx

- Mentor Graphics(Siemens) HyperLynx 시뮬레이션/분석용 파일 생성. **File** → **Export** → **Hyperlynx…​**. 설정 옵션 없음.

---

# Design variants · #pcb-design-variants

- 단일 PCB로 여러 제품 구성을 표현하는 기능. variant는 Schematic Editor에서 정의하고 **Update PCB from Schematic**으로 보드에 전달. PCB 에디터는 variant 효과 보기·활성 variant 선택·variant별 제조 출력 생성을 제공.
- variant 생성·편집은 Schematic Editor 매뉴얼의 Design variants 참조.

## Selecting a variant in the PCB editor · #selecting-a-variant-in-the-pcb-editor

- 메인 툴바의 variant 선택 드롭다운(Schematic Editor와 동일 동작). variant 선택 시 보드 뷰가 해당 variant의 부품 상태를 반영.
- variant 활성 시:
  - 해당 variant에서 DNP인 부품은 fab 레이어에 X 표시.
  - 필드 텍스트(Value, Footprint, custom)가 variant override 반영.
  - `${VARIANT}`/`${VARIANT_DESC}` text가 활성 variant 이름·설명으로 해석.
- `<Default>` 선택 시 override 없는 base 설계로 복귀.

## Viewing variant effects · #viewing-variant-effects

### Component visibility and DNP · #component-visibility-and-dnp
- variant 활성 시 해당 variant에서 DNP인 부품은 fab 레이어(F.Fab/B.Fab)에 X로 표시(base의 DNP 동작과 동일하나 variant별 제어). variant 전환 시 보드 뷰 실시간 갱신.

### 3D viewer · #three-d-viewer
- 3D 뷰어가 활성 variant 반영 — 현재 variant에서 DNP인 부품은 3D 뷰에서 숨김. 특정 variant를 보려면 3D 모델 열기 전(또는 보는 중) PCB 에디터 툴바 드롭다운에서 선택.

### Footprint properties · #footprint-properties
- 비기본 variant 활성 시 Properties 패널·Footprint Properties 다이얼로그(풋프린트 더블클릭)가 base 대신 variant override(필드 값, DNP 속성, exclusion flag)를 표시. 패널/다이얼로그로 개별 풋프린트 override 편집 가능.

## Generating variant-aware outputs · #pcb-generating-variant-aware-outputs

- PCB 에디터의 여러 출력 다이얼로그에 variant 선택기가 있음. 출력 생성 전 variant를 선택하면 해당 variant의 부품 상태가 파일에 반영됨.

### Gerber and fabrication output · #gerber-and-fabrication-output
- Plot 다이얼로그(**File** → **Plot…​**)에 **Variant** 드롭다운. variant 선택 시 해당 구성의 fab 레이어 DNP 표시를 반영한 Gerber 생성. **Indicate DNP on fabrication layers** 활성 시 DNP 부품을 F.Fab/B.Fab에 X로 표시.

### Position files · #position-files
- Component Placement 다이얼로그(**File** → **Fabrication Outputs** → **Component Placement (.pos, .gbr)…​**)에 variant 선택기. 선택 variant에서 DNP/position 제외 부품은 출력에서 생략 — variant별 픽앤플레이스 파일 생성 가능.

### 3D model export (STEP/VRML) · #three-d-model-export
- 3D model export 다이얼로그(**File** → **Export** → **STEP/GLB/BREP/XAO/PLY/STL…​**)에 variant 선택기. 선택 variant에서 DNP인 부품은 export 모델에서 제외.

### ODB++ and IPC-2581 · #odb-and-ipc2581
- ODB++·IPC-2581은 CLI로 variant 선택 지원. `pcb export odb` / `pcb export ipc2581`에 `--variant` 인자 사용.

## Command-line variant support · #command-line-variant-support

- 모든 PCB export 명령이 `--variant` 인자 지원 — 다중 variant 출력의 스크립트/자동화 가능.
- 특정 variant Gerber export:

```
kicad-cli pcb export gerbers --variant "WiFi-only" my_board.kicad_pcb
```

- 다중 variant를 한 명령으로(`--variant` 여러 번 + 출력 경로에 `${VARIANT}`):

```
kicad-cli pcb export gerbers \
    --variant "WiFi-only" \
    --variant "WiFi-BT" \
    -o "gerbers_${VARIANT}/" \
    my_board.kicad_pcb
```

- 위 예는 `gerbers_WiFi-only/`, `gerbers_WiFi-BT/` 두 세트 생성. 동일 패턴이 `pcb export step`, `pcb export pos`, `pcb export dxf`, `sch export bom` 등 variant 지원 명령에 적용. `--variant` 미지정 시 default variant 사용.
- 💡 **NOTE:** 출력 경로의 `${VARIANT}` text variable은 export 시 확장되며, 회로도/보드 text item의 `${VARIANT}`와는 독립적이다.
- 전체 export 명령·variant 옵션 목록은 Command-Line Interface 레퍼런스 참조.
