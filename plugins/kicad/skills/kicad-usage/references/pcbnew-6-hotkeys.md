# PCB 에디터 ⑥ — 단축키 레퍼런스(Actions reference) — KiCad 10.0 사용 다이제스트

> **원문**: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html

> **범위**: PCB Editor / 3D Viewer / Common 액션과 기본 단축키 표

> 한국어 요약 다이제스트. 섹션 제목의 #anchor로 원문 핀포인트: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#<anchor>

## 목차

- [Actions reference](#pcbnew-actions-reference) — PCB Editor에서 단축키에 할당 가능한 모든 액션 목록
- [PCB Editor](#pcb_editor) — PCB 에디터 전용 액션·기본 단축키 표 (정렬/레이어/라우터/존/풋프린트 등)
- [3D Viewer](#3d_viewer) — 3D 뷰어 전용 액션·기본 단축키 표 (회전/뷰/렌더링/그리드)
- [Common](#common) — KiCad 전반(PCB 에디터 포함) 공용 액션·기본 단축키 표

> 💡 모든 액션의 단축키는 **Preferences → Hotkeys** 섹션에서 자유롭게 재할당할 수 있다. 아래 표의 "기본 단축키"는 KiCad 10.0 출하 시 기본값이며 빈 칸은 기본 단축키가 할당되지 않은 액션이다.

---

## Actions reference · #pcbnew-actions-reference

PCB Editor에서 사용 가능한 모든 **액션**(단축키에 할당할 수 있는 명령) 목록이다. 아래 세 그룹(PCB Editor / 3D Viewer / Common)으로 나뉜다.

---

## PCB Editor · #pcb_editor

PCB 에디터 전용 액션. 단축키는 **Hotkeys** 섹션에서 임의 액션에 할당 가능.

| 액션 | 기본 단축키 | 설명 |
| --- | --- | --- |
| Align to Bottom |  | 선택 항목을 커서 아래 항목의 하단 가장자리에 정렬 |
| Align to Horizontal Center |  | 선택 항목을 커서 아래 항목의 수평 중심에 정렬 |
| Align to Vertical Center |  | 선택 항목을 커서 아래 항목의 수직 중심에 정렬 |
| Align to Left |  | 선택 항목을 커서 아래 항목의 좌측 가장자리에 정렬 |
| Align to Right |  | 선택 항목을 커서 아래 항목의 우측 가장자리에 정렬 |
| Align to Top |  | 선택 항목을 커서 아래 항목의 상단 가장자리에 정렬 |
| Distribute Horizontally by Centers |  | 좌·우 끝 항목 사이에서 항목 중심이 균등 분포되도록 분배 |
| Distribute Horizontally with Even Gaps |  | 좌·우 끝 항목 사이에서 항목 간 간격이 균등하도록 분배 |
| Distribute Vertically by Centers |  | 상·하 끝 항목 사이에서 항목 중심이 균등 분포되도록 분배 |
| Distribute Vertically with Even Gaps |  | 상·하 끝 항목 사이에서 항목 간 간격이 균등하도록 분배 |
| Create Array… | `Ctrl`+`T` |  |
| Place Off-Board Footprints |  | 보드 영역 밖 부품 자동 배치 수행 |
| Place Selected Footprints |  | 선택 부품 자동 배치 수행 |
| Switch Track to Next Layer | `Ctrl`+`+` | 트랙을 다음 활성 구리 레이어로 전환 |
| Switch Track to Previous Layer | `Ctrl`+`-` | 트랙을 이전 활성 구리 레이어로 전환 |
| Flip Board View |  | 보드를 반대 면에서 보기 |
| Automatic zoom |  | 풋프린트 변경 시 자동 줌 |
| Sketch Graphic Items |  | 그래픽 항목을 외곽선 모드로 표시 |
| Decrease Layer Opacity | `{` | 현재 레이어를 더 투명하게 |
| Increase Layer Opacity | `}` | 현재 레이어를 덜 투명하게 |
| Switch to Copper (B.Cu) Layer | `PgDn` |  |
| Switch to Inner Layer 1 |  |  |
| Switch to Inner Layer 10 |  |  |
| Switch to Inner Layer 11 |  |  |
| Switch to Inner Layer 12 |  |  |
| Switch to Inner Layer 13 |  |  |
| Switch to Inner Layer 14 |  |  |
| Switch to Inner Layer 15 |  |  |
| Switch to Inner Layer 16 |  |  |
| Switch to Inner Layer 17 |  |  |
| Switch to Inner Layer 18 |  |  |
| Switch to Inner Layer 19 |  |  |
| Switch to Inner Layer 2 |  |  |
| Switch to Inner Layer 20 |  |  |
| Switch to Inner Layer 21 |  |  |
| Switch to Inner Layer 22 |  |  |
| Switch to Inner Layer 23 |  |  |
| Switch to Inner Layer 24 |  |  |
| Switch to Inner Layer 25 |  |  |
| Switch to Inner Layer 26 |  |  |
| Switch to Inner Layer 27 |  |  |
| Switch to Inner Layer 28 |  |  |
| Switch to Inner Layer 29 |  |  |
| Switch to Inner Layer 3 |  |  |
| Switch to Inner Layer 30 |  |  |
| Switch to Inner Layer 4 |  |  |
| Switch to Inner Layer 5 |  |  |
| Switch to Inner Layer 6 |  |  |
| Switch to Inner Layer 7 |  |  |
| Switch to Inner Layer 8 |  |  |
| Switch to Inner Layer 9 |  |  |
| Switch to Next Layer | `+` |  |
| Cycle Layer Pair Presets | `Shift`+`V` | 프리셋 레이어 페어 간 순환 |
| Switch to Previous Layer | `-` |  |
| Toggle Layer | `V` | 활성 레이어 페어 내 레이어 간 전환 |
| Switch to Component (F.Cu) layer | `PgUp` |  |
| Local Ratsnest |  | 선택 항목의 ratsnest 표시 토글 |
| Net Color Mode (3-state) |  | 모든 넷/래츠네스트만/없음에 대해 넷·넷클래스 색상 사용을 순환 |
| Display next footprint |  |  |
| Sketch Pads |  | 패드를 외곽선 모드로 표시 |
| Display previous footprint |  |  |
| Curved Ratsnest Lines |  | ratsnest를 곡선으로 표시 |
| Ratsnest Mode (3-state) |  | 모든 레이어/가시 레이어만/없음에 대해 ratsnest 표시 순환 |
| Repair Board |  | 각종 진단을 실행하고 보드 복구 시도 |
| Appearance |  | appearance 매니저 표시/숨김 |
| Net Inspector |  | net inspector 표시/숨김 |
| Show Pad Numbers |  |  |
| Scripting Console |  | Python 스크립팅 콘솔 표시 |
| Show Ratsnest |  | 보드의 미연결 연결을 나타내는 선/호 표시 |
| Sketch Text Items |  | 풋프린트 텍스트를 선 모드로 표시 |
| Sketch Tracks | `K` | 트랙을 외곽선 모드로 표시 |
| Sketch Vias |  | 비아를 외곽선 모드로 표시 |
| Draw Zone Outlines |  | 존 경계만 표시 |
| Draw Zone Fills |  | 존의 채워진 영역 표시 |
| Toggle Zone Display |  | 존 채움 표시와 외곽선만 표시 사이 순환 |
| Zone Manager…​ |  | zone manager 다이얼로그 표시 |
| Create Arc from Selection |  | 선택한 선분에서 호 생성 |
| Create Rule Area from Selection…​ |  | 선택에서 rule area 생성 |
| Create Lines from Selection…​ |  | 선택에서 그래픽 선 생성 |
| Create Polygon from Selection…​ |  | 선택에서 그래픽 폴리곤 생성 |
| Create Tracks from Selection |  | 선택한 그래픽 선에서 트랙 생성 |
| Create Zone from Selection…​ |  | 선택에서 구리 존 생성 |
| Create Outsets from Selection…​ |  | 선택 항목에서 outset 선 생성 |
| Design Rules Checker |  | design rules checker 창 표시 |
| DRC Rule Editor |  | DRC rule editor 창 열기 |
| Open in Footprint Editor | `Ctrl`+`E` |  |
| Edit Library Footprint… | `Ctrl`+`Shift`+`E` |  |
| Append Board…​ |  | 다른 보드를 열어 그 내용을 현재 보드에 추가 |
| Assign Netclass…​ |  | 패턴에 매칭되는 넷에 netclass 할당 |
| Automatically select track width |  | 기존 트랙에서 라우팅 시 현재 폭 설정 대신 그 트랙의 폭 사용 |
| Board Setup…​ |  | 레이어·디자인 규칙·각종 기본값 등 board setup 편집 |
| Clear Net Highlighting | `~` |  |
| Collect And Embed 3D Models |  | 풋프린트 3D 모델을 수집해 보드에 임베드 |
| Drill/Place File Origin |  | 드릴 파일·부품 배치 파일용 원점 배치 |
| Reset Drill Origin |  |  |
| Export Footprint Association (.cmp) File…​ |  | 회로도 백어노테이션용 풋프린트 연결 파일(*.cmp) 내보내기 |
| Export Footprints…​ |  | 보드의 풋프린트를 신규 또는 기존 풋프린트 라이브러리에 추가(기존 풋프린트는 제거하지 않음) |
| Export GenCAD…​ |  | GenCAD 보드 표현 내보내기 |
| Hyperlynx…​ |  |  |
| Export IDFv3…​ |  | IDF 3D 보드 표현 내보내기 |
| Export STEP/GLB/BREP/XAO/PLY/STL…​ |  | STEP, GLB, BREP, XAO, PLY, STL 3D 보드 표현 내보내기 |
| Export Specctra DSN…​ |  | Specctra DSN 라우팅 정보 내보내기 |
| Export VRML…​ |  | VRML 3D 보드 표현 내보내기 |
| Bill of Materials…​ |  | 보드에서 BOM 생성 |
| IPC-D-356 Netlist File… |  | IPC-D-356 넷리스트 파일 생성 |
| Drill Files (.drl)…​ |  | Excellon 드릴 파일 생성 |
| Gerbers (.gbr)…​ |  | 제조용 Gerber 생성 |
| IPC-2581 File (.xml)…​ |  | IPC-2581 파일 생성 |
| ODB++ Output File…​ |  | ODB++ 출력 파일 생성 |
| Component Placement (.pos, .gbr)…​ |  | pick and place용 부품 배치 파일 생성 |
| Footprint Report (.rpt)…​ |  | 현재 보드의 모든 풋프린트 리포트 생성 |
| Hide Net in Ratsnest |  | 선택 넷을 미연결 ratsnest 선/호에서 숨김 |
| Highlight Net | `` ` `` | 커서 아래 넷 하이라이트 |
| Highlight Net |  | 선택 넷의 모든 구리 항목 하이라이트 |
| Import Netlist…​ |  | 넷리스트를 읽어 보드 연결성 업데이트 |
| Import Specctra Session…​ |  | 라우팅된 Specctra session(*.ses) 파일 가져오기 |
| Line Modes |  | 그리기·드래그를 수평/수직/45도 동작으로 제한 |
| Line Modes |  | 임의 각도로 그리기·드래그 |
| Line Modes | `Shift`+`Space` | 다음 각도 스내핑 모드로 전환 |
| Line Modes |  | 그리기·드래그를 수평 또는 수직 동작으로 제한 |
| Lock |  | 캔버스에서 항목 이동·크기 변경 방지 |
| Non-KiCad Board File…​ |  | 타 애플리케이션의 보드 파일 가져오기 |
| Place Footprints | `A` |  |
| Rescue |  | 보드를 비우고 PCB 에디터가 자동 저장한 마지막 rescue 파일 가져오기 |
| Switch to Schematic Editor |  | 회로도 에디터에서 회로도 열기 |
| Show Net in Ratsnest |  | 선택 넷을 미연결 ratsnest 선/호에 표시 |
| Toggle Last Net Highlight |  | 최근 하이라이트한 두 넷 간 토글 |
| Toggle Lock | `L` | 선택 항목 잠금/해제 |
| Toggle Net Highlight | `` Alt+` `` |  |
| Switch Track Width to Previous | `Shift`+`W` | 트랙 폭을 이전 사전 정의 크기로 변경 |
| Switch Track Width to Next | `W` | 트랙 폭을 다음 사전 정의 크기로 변경 |
| Unlock |  | 캔버스에서 항목 이동·크기 변경 허용 |
| Decrease Via Size | `\` | 비아 크기를 이전 사전 정의 크기로 변경 |
| Increase Via Size | `'` | 비아 크기를 다음 사전 정의 크기로 변경 |
| Duplicate Zone onto Layer… |  |  |
| Merge Zones |  |  |
| Export footprint to editor |  | 풋프린트를 에디터로 내보내기 |
| Reset wizard parameters |  | 위저드 파라미터를 기본값으로 재설정 |
| Select next wizard page |  | 다음 파라미터 페이지 선택 |
| Select previous wizard page |  | 이전 파라미터 페이지 선택 |
| Show wizards selector |  | 실행할 위저드 스크립트 선택 |
| Rebuild All Generators |  | 모든 generator의 지오메트리 재구성 |
| Update All Tuning Patterns |  | 기존 튜닝 패턴을 범위 내에서 재튜닝 시도 |
| Rebuild Selected Generators |  | 선택 generator의 지오메트리 재구성 |
| Generators Manager |  | Generator 객체용 매니저 다이얼로그 표시 |
| Change Footprint… |  | 라이브러리의 다른 풋프린트 할당 |
| Change Footprints…​ |  | 라이브러리의 다른 풋프린트들 할당 |
| Cleanup Graphics…​ |  | 중복 항목 등 정리 |
| Cleanup Tracks & Vias…​ |  | 중복 항목·쇼트 항목 등 정리 |
| Edit Teardrops…​ |  | 보드 전역에 teardrop 추가·제거·편집 |
| Edit Text & Graphics Properties…​ |  | 보드 전역의 텍스트·그래픽 속성 편집 |
| Edit Track & Via Properties…​ |  | 보드 전역의 트랙·비아 속성 편집 |
| Global Deletions…​ |  | 보드에서 트랙·풋프린트·그래픽 항목 삭제 |
| Remove Unused Pads…​ |  | 관통홀 패드·비아의 미연결 내부 레이어 제거 또는 복원 |
| Swap Layers…​ |  | 트랙·도면을 한 레이어에서 다른 레이어로 이동 |
| Update Footprint… |  | 라이브러리 변경 사항을 포함하도록 풋프린트 업데이트 |
| Update Footprints from Library…​ |  | 라이브러리 변경 사항을 포함하도록 풋프린트들 업데이트 |
| Compare Footprint with Library |  | 보드 풋프린트와 라이브러리 등가물의 차이 표시 |
| Clearance Resolution |  | 선택한 두 객체 간 활성 레이어의 clearance 해석 표시 |
| Constraints Resolution |  | 선택 객체의 constraints 해석 표시 |
| Show Board Statistics |  | 보드 통계 표시 |
| Show Footprint Associations |  | 풋프린트 라이브러리·회로도 심볼 연결 표시 |
| Draw Aligned Dimensions |  |  |
| Apply Design Block Layout |  | 연결된 design block 레이아웃을 선택 그룹에 적용 |
| Draw Arcs | `Ctrl`+`Shift`+`A` |  |
| Switch Arc Posture | `/` |  |
| Add Barcode |  | 바코드 추가 |
| Draw Bezier Curve | `Ctrl`+`Shift`+`B` |  |
| Draw Center Dimensions |  |  |
| Switch Dimension Arrows |  | 내향·외향 치수 화살표 간 전환 |
| Draw Circles | `Ctrl`+`Shift`+`C` |  |
| Close Outline |  | 진행 중인 외곽선 닫기 |
| Decrease Line Width | `Ctrl`+`-` |  |
| Delete Last Point | `Back` | 현재 항목에 마지막으로 추가한 점 삭제 |
| Draw Tables |  |  |
| Draw Polygons | `Ctrl`+`Shift`+`P` |  |
| Increase Line Width | `Ctrl`+`+` |  |
| Draw Leaders |  |  |
| Draw Lines | `Ctrl`+`Shift`+`L` |  |
| Draw Orthogonal Dimensions | `Ctrl`+`Shift`+`H` |  |
| Add Board Characteristics |  | 그래픽 레이어에 board characteristics 테이블 추가 |
| Place Design Block | `Shift`+`B` | 선택한 design block을 현재 보드에 추가 |
| Import Graphics…​ | `Ctrl`+`Shift`+`F` | 2D 도면 파일 가져오기 |
| Place Linked Design Block |  | 선택 그룹에 연결된 design block 배치 |
| Place Point |  | reference/snap 포인트 추가 |
| Place Reference Images |  | 참조용 비트맵 이미지 추가(이미지는 출력에 포함되지 않음) |
| Add Stackup Table |  | 그래픽 레이어에 board stackup 테이블 추가 |
| Draw Radial Dimensions |  |  |
| Draw Rectangles |  |  |
| Draw Rule Areas | `Ctrl`+`Shift`+`K` |  |
| Save to Linked Design Block |  | 선택 그룹을 연결된 design block에 저장 |
| Place the Footprint Anchor | `Ctrl`+`Shift`+`N` | 풋프린트 앵커 포인트 설정 |
| Add a Similar Zone | `Ctrl`+`Shift`+`.` | 기존 존과 동일한 설정의 존 추가 |
| Draw Text | `Ctrl`+`Shift`+`T` |  |
| Draw Text Boxes |  |  |
| Place Vias | `Ctrl`+`Shift`+`X` | 독립형 비아 배치 |
| Draw Filled Zones | `Ctrl`+`Shift`+`Z` |  |
| Add a Zone Cutout | `Shift`+`C` | 기존 존 또는 rule area에 cutout 추가 |
| Get and Move Footprint | `T` | reference designator로 풋프린트를 선택해 커서 아래에 두고 이동 |
| Chamfer Lines…​ |  | 선택 선들 사이 모서리 깎기 |
| Change Track Width |  | 선택한 트랙·비아 크기 업데이트 |
| Delete Full Track | `Shift`+`Del` | 선택 항목과 구리 연결 삭제 |
| Dogbone Corners…​ |  | 선택 선에 dogbone 모서리 추가 |
| Duplicate and Increment | `Ctrl`+`Shift`+`D` | 선택 항목 복제, 패드 번호 증가 |
| Edit Corners…​ |  | 테이블로 폴리곤 모서리 편집 |
| Extend Lines to Meet |  | 선들이 서로 만나도록 연장 |
| Fillet Lines…​ |  | 선택 선에 접하는 호 추가 |
| Fillet Tracks |  | 선택한 직선 트랙 세그먼트에 접하는 호 추가 |
| Change Side / Flip | `F` | 선택 항목을 보드 반대 면으로 뒤집기 |
| Heal Shapes |  | 도형을 연결(연장·절단 또는 추가 지오메트리 적용 가능) |
| Intersect Polygons |  | 선택 폴리곤들의 교집합 생성 |
| Merge Polygons |  | 선택 폴리곤들을 단일 폴리곤으로 병합 |
| Mirror Horizontally |  | 선택 항목을 Y축 기준으로 미러 |
| Mirror Vertically |  | 선택 항목을 X축 기준으로 미러 |
| Move Corner To…​ |  | 활성 모서리를 정확한 위치로 이동 |
| Move Exactly… | `Shift`+`M` | 선택 항목을 정확한 양만큼 이동 |
| Move Midpoint To…​ |  | 활성 중점을 정확한 위치로 이동 |
| Pack and Move Footprints | `P` | 선택 풋프린트를 reference로 정렬하고 크기 기준으로 묶어 이동 시작 |
| Properties… | `E` |  |
| Rotate Counterclockwise | `R` |  |
| Rotate Clockwise | `Shift`+`R` |  |
| Simplify Polygons |  | 폴리곤 외곽선 단순화, 불필요한 점 제거 |
| Skip | `Tab` | 다음 항목으로 건너뛰기 |
| Subtract Polygons |  | 마지막 선택 폴리곤에서 선택 폴리곤 빼기 |
| Swap | `Alt`+`S` | 선택 항목 위치 교환 |
| Swap Gate Nets |  | 풋프린트의 게이트 간 넷과 연결 구리 교환 |
| Swap Pad Nets |  | 선택한 두 패드 간 넷과 연결 구리 교환 |
| Copy with Reference…​ |  | 지정한 시작점과 함께 선택 항목을 클립보드에 복사 |
| Move | `M` |  |
| Move Individually | `Ctrl`+`M` | 선택 항목을 하나씩 이동 |
| Move with Reference…​ |  | 지정한 시작점과 함께 선택 항목 이동 |
| Attempt Finish | `F` | 현재 라우트를 가장 가까운 ratsnest 끝까지 완성 시도 |
| Attempt Finish Selected (Autoroute) | `Shift`+`F` | 선택한 모든 패드를 순차적으로 자동 라우팅 시도 |
| Break Track |  | 트랙 세그먼트를 커서 위치에서 연결된 두 세그먼트로 분할 |
| Cancel Current Item |  | 현재 항목 건너뛰고 다음 선택 항목 라우팅 |
| Route From Other End | `Ctrl`+`E` | 현재 세그먼트 커밋 후 가장 가까운 ratsnest 끝에서 다음 세그먼트 시작 |
| Custom Track/Via Size… | `Q` | 트랙 폭·비아 크기 변경 다이얼로그 표시 |
| Cycle Router Mode |  | 라우터를 다음 모드로 순환 |
| Route Differential Pair | `6` | 차동 페어 라우팅 |
| Differential Pair Dimensions…​ |  | Differential Pair Dimension 설정 열기 |
| Drag 45 Degree Mode | `D` | 연결 트랙을 45도로 유지하며 트랙 세그먼트 드래그 |
| Drag Free Angle | `G` | 트랙 각도 제한 없이 트랙의 가장 가까운 조인트 드래그 |
| Router Highlight Mode |  | 라우터를 highlight 모드로 전환 |
| Place Blind/Buried Via | `Alt`+`Shift`+`V` | 현재 라우팅 트랙 끝에 blind/buried 비아 추가 |
| Place Microvia | `Ctrl`+`V` | 현재 라우팅 트랙 끝에 microvia 추가 |
| Place Through Via | `V` | 현재 라우팅 트랙 끝에 through-hole 비아 추가 |
| Route Selected | `Shift`+`X` | 선택 항목을 ratsnest 앵커에서 순차 라우팅 |
| Route Selected From Other End | `Shift`+`E` | 선택 항목을 ratsnest 앵커 반대 끝에서 순차 라우팅 |
| Select Layer and Place Blind/Buried Via… | `Alt`+`<` | 레이어 선택 후 현재 라우팅 트랙 끝에 blind/buried 비아 추가 |
| Select Layer and Place Micro Via…​ |  | 레이어 선택 후 현재 라우팅 트랙 끝에 micro 비아 추가 |
| Select Layer and Place Through Via… | `<` | 레이어 선택 후 현재 라우팅 트랙 끝에 through-hole 비아 추가 |
| Set Layer Pair…​ |  | 라우팅용 활성 레이어 페어 변경 |
| Interactive Router Settings… | `Ctrl`+`<` | Interactive Router 설정 열기 |
| Router Shove Mode |  | 라우터를 shove 모드로 전환 |
| Route Single Track | `X` | 트랙 라우팅 |
| Switch Track Posture | `/` | 현재 라우팅 트랙의 posture 전환 |
| Track Corner Mode 45 | `Ctrl`+`W` | 트랙 라우팅 시 45° 모서리로 전환 |
| Track Corner Mode 90 | `Ctrl`+`Alt`+`W` | 트랙 라우팅 시 90° 모서리로 전환 |
| Track Corner Mode Arc 45 | `Ctrl`+`Shift`+`W` | 트랙 라우팅 시 arc 45° 모서리로 전환 |
| Track Corner Mode Arc 90 | `Alt`+`W` | 트랙 라우팅 시 arc 90° 모서리로 전환 |
| Track Corner Mode Switch | `Ctrl`+`/` | 트랙 라우팅 시 sharp/rounded 및 45°/90° 모서리 간 전환 |
| Undo Last Segment | `Back` | 현재 트랙을 한 세그먼트 되돌림 |
| Router Walkaround Mode |  | 라우터를 walkaround 모드로 전환 |
| Deselect All Tracks in Net |  | 같은 넷에 속한 모든 트랙·비아 선택 해제 |
| Filter Selected Items…​ |  | 타입별로 선택에서 항목 제거 |
| Grab Nearest Unconnected Footprints | `Shift`+`O` | 각 선택 넷에서 가장 가까운 미연결 풋프린트를 선택해 이동 시작 |
| Select/Expand Connection | `U` | 연결을 선택하거나 기존 선택을 정션·패드·전체 연결로 확장 |
| Select All Tracks in Net |  | 같은 넷에 속한 모든 트랙·비아 선택 |
| Select on Schematic |  | 회로도 에디터에서 대응 항목 선택 |
| Sheet |  | 회로도 시트의 모든 풋프린트·트랙 선택 |
| Items in Same Hierarchical Sheet |  | 동일 회로도 시트의 모든 풋프린트·트랙 선택 |
| Select All Unconnected Footprints | `O` | 각 선택 넷에 속한 모든 미연결 풋프린트 선택 |
| Unroute Segment | `Back` | 세그먼트를 가장 가까운 세그먼트까지 언라우트 |
| Unroute Selected |  | 선택 항목을 가장 가까운 패드까지 언라우트 |
| Tune Length of a Differential Pair | `8` |  |
| Tune Skew of a Differential Pair | `9` |  |
| Tune Length of a Single Track | `7` |  |
| Draw Microwave Polygonal Shapes |  | 정점 목록에서 마이크로웨이브 폴리곤 도형 생성 |
| Draw Microwave Gaps |  | 마이크로웨이브용 지정 길이 갭 생성 |
| Draw Microwave Lines |  | 마이크로웨이브용 지정 길이 선 생성 |
| Draw Microwave Stubs |  | 마이크로웨이브용 지정 길이 스텁 생성 |
| Draw Microwave Arc Stubs |  | 마이크로웨이브용 지정 크기 스텁(호) 생성 |
| Footprint Checker |  | footprint checker 창 표시 |
| Copy Footprint |  |  |
| Create Footprint…​ |  | Footprint Wizard로 새 풋프린트 생성 |
| Cut Footprint |  |  |
| Delete Footprint from Library |  |  |
| Duplicate Footprint |  |  |
| Edit Footprint |  | 선택 풋프린트를 에디터 캔버스에 표시 |
| Export Current Footprint…​ |  | 편집한 풋프린트를 파일로 내보내기 |
| Footprint Properties…​ |  |  |
| Import Footprint…​ |  | 파일에서 풋프린트 가져오기 |
| Load footprint from current PCB |  | 현재 보드에서 풋프린트 로드 |
| New Footprint | `Ctrl`+`N` | 비어 있는 새 풋프린트 생성 |
| Pad Table…​ |  | 패드 일괄 편집용 패드 테이블 표시 |
| Paste Footprint |  |  |
| Rename Footprint…​ |  |  |
| Repair Footprint |  | 각종 진단을 실행하고 풋프린트 복구 시도 |
| Insert footprint into PCB |  | 현재 보드에 풋프린트 삽입 |
| Generate Placement Rule Areas…​ |  | best-fit placement rule area 생성 |
| Repeat Layout…​ |  | 동일한 다중 채널에 배치·라우팅 복제 |
| Paste Default Pad Properties to Selected |  | 현재 패드 속성을 앞서 복사한 속성으로 교체 |
| Copy Pad Properties to Default |  | 현재 패드 속성 복사 |
| Push Pad Properties to Other Pads…​ |  | 현재 패드 속성을 다른 패드들에 복사 |
| Default Pad Properties… |  | 새 패드 생성 시 사용할 패드 속성 편집 |
| Renumber Pads… |  | 원하는 순서로 클릭하여 패드 재번호 |
| Edit Pad as Graphic Shapes | `Ctrl`+`E` | 커스텀 모양 패드를 개별 그래픽 도형으로 편집하도록 그룹 해제 |
| Add Pad |  | 패드 추가 |
| Finish Pad Edit | `Ctrl`+`E` | 맞닿은 모든 그래픽 도형을 편집 패드로 재그룹 |
| Delete Design Block |  | 선택 design block을 라이브러리에서 제거 |
| Properties… |  | design block 속성 편집 |
| Save Board as Design Block…​ |  | 현재 보드에서 새 design block 생성 |
| Save Selection as Design Block…​ |  | 현재 선택에서 새 design block 생성 |
| Design Blocks |  | design blocks 라이브러리 표시/숨김 |
| Update Design Block from Board |  | design block 레이아웃을 현재 보드로 설정 |
| Update Design Block from Selection |  | design block 레이아웃을 현재 선택으로 설정 |
| Create Corner | `Ins` | 모서리 생성 |
| Keep Arc Center, Adjust Radius |  | 호 편집 모드를 중심 유지·반경/끝점 조정으로 전환 |
| Keep Arc Endpoints or Direction of Starting Point |  | 호 편집 모드를 끝점 유지 또는 다른 점 방향 유지로 전환 |
| Keep Arc Radius and Center, adjust angle |  | 호 편집 모드를 끝점 이동 시 반경 유지로 전환 |
| Chamfer Corner |  | 모서리 챔퍼 |
| Remove Corner |  | 모서리 제거 |
| Interactive Offset Tool |  | 항목을 정확한 양만큼 오프셋하는 대화형 도구 |
| Position Relative To… | `Shift`+`P` | 선택 항목을 다른 항목에 상대적으로 정확한 양만큼 배치 |
| Geographical Reannotate…​ |  | PCB를 지리적 순서로 재어노테이트 |
| Open Plugin Directory |  | 기본 시스템 파일 매니저에서 디렉토리 열기 |
| Edit Table…​ | `Ctrl`+`E` |  |
| Draft Fill Selected Zone(s) |  | 다른 상호작용 존 무시하고 선택 존의 구리 채움 업데이트 |
| Fill All Zones | `B` | 모든 존의 구리 채움 업데이트 |
| Unfill Selected Zone(s) |  | 선택 존의 구리 채움 제거 |
| Unfill All Zones | `Ctrl`+`B` | 모든 존의 구리 채움 제거 |
| Decrease Amplitude | `4` | 튜닝 패턴 진폭을 한 단계 감소 |
| Increase Amplitude | `3` | 튜닝 패턴 진폭을 한 단계 증가 |
| Decrease Spacing | `2` | 튜닝 패턴 간격을 한 단계 감소 |
| Increase Spacing | `1` | 튜닝 패턴 간격을 한 단계 증가 |

> 💡 라우터 인터랙티브 단축키 핵심: `X` Route Single Track(단일 트랙 라우팅), `6` Route Differential Pair, `V` Place Through Via, `Q` Custom Track/Via Size, `F` Attempt Finish, `D` Drag 45°, `G` Drag Free Angle, `/` Switch Track Posture, `Back` Undo Last Segment.

> 💡 트랙 폭·비아 크기: `W`/`Shift`+`W` 트랙 폭 다음/이전, `'`/`\` 비아 크기 증가/감소.

> 💡 길이·스큐 튜닝 단축키: `7` 단일 트랙 길이, `8` 차동 페어 길이, `9` 차동 페어 스큐. 튜닝 패턴 조정은 `1`/`2` 간격, `3`/`4` 진폭.

> ⚠️ 동일 이름 액션이 둘 이상 존재한다(예: `Highlight Net` 2개, `Line Modes` 4개, `Properties…` 2개). 표에는 모두 원문 그대로 보존했으며 단축키·설명으로 구분된다. `Ctrl`+`E`도 컨텍스트별로 Open in Footprint Editor / Route From Other End / Edit Pad as Graphic Shapes / Finish Pad Edit / Edit Table… 등에 매핑된다.

---

## 3D Viewer · #3d_viewer

3D 뷰어 전용 액션. 단축키는 **Hotkeys** 섹션에서 임의 액션에 할당 가능.

| 액션 | 기본 단축키 | 설명 |
| --- | --- | --- |
| Show 3D Models marked DNP | `D` | 'Do Not Place' 표시된 풋프린트도 3D 모델 표시 |
| Show 3D Models not in POS File | `P` | .pos 파일에 없는 풋프린트도 3D 모델 표시 |
| Show Unspecified 3D Models | `V` | 'unspecified' 타입 풋프린트의 3D 모델 표시 |
| Show SMD 3D Models | `S` | 'Surface mount' 타입 풋프린트의 3D 모델 표시 |
| Show Through Hole 3D Models | `T` | 'Through hole' 타입 풋프린트의 3D 모델 표시 |
| Copy 3D image to clipboard |  | 현재 3D 이미지를 클립보드에 복사 |
| Export Image…​ |  | 현재 뷰를 이미지 파일로 내보내기 |
| Flip Board | `F` | 보드 뷰 뒤집기 |
| Home View | `Home` | 홈 위치·줌으로 다시 그리기 |
| Render CAD Colors |  | 재질의 diffuse 색상 기반 CAD 색상 스타일 사용 |
| Render Solid Colors |  | 3D 모델 파일의 diffuse 색상 속성만 사용 |
| Render Realistic Materials |  | 각 3D 모델 파일의 모든 재질 속성 사용 |
| Move Board Down | `Down` |  |
| Move Board Left | `Left` |  |
| Move Board Right | `Right` |  |
| Move Board Up | `Up` |  |
| No 3D Grid |  |  |
| Set Pivot | `Space` | 보드 회전 중심점 배치(가운데 마우스 클릭) |
| Reload board |  | 보드 다시 로드 후 3D 뷰 새로고침 |
| Rotate X Clockwise |  |  |
| Rotate X Counterclockwise |  |  |
| Rotate Y Clockwise |  |  |
| Rotate Y Counterclockwise |  |  |
| Rotate Z Clockwise | `Shift`+`R` |  |
| Rotate Z Counterclockwise | `R` |  |
| 3D Grid 10mm |  |  |
| 3D Grid 1mm |  |  |
| 3D Grid 2.5mm |  |  |
| 3D Grid 5mm |  |  |
| Show Model Bounding Boxes |  | 리얼타임 렌더러에서 3D 모델 바운딩 박스 표시 |
| Show Appearance Manager |  | appearance 매니저 표시/숨김 |
| Show 3D Navigator |  |  |
| Toggle Orthographic Projection |  | 직교 투영 켜기/끄기 |
| Use raytracing |  | 현재 뷰를 Raytracing으로 렌더링 |
| View Back | `Shift`+`Y` |  |
| View Bottom | `Shift`+`Z` |  |
| View Front | `Y` |  |
| View Left | `Shift`+`X` |  |
| View Right | `X` |  |
| View Top | `Z` |  |

> 💡 3D 뷰 방향 단축키: `Y`/`Shift`+`Y` Front/Back, `Z`/`Shift`+`Z` Top/Bottom, `X`/`Shift`+`X` Right/Left, `Home` Home View, `F` Flip Board, `R`/`Shift`+`R` Z축 회전 CCW/CW, `Space` Set Pivot.

> 💡 3D 모델 표시 필터 토글: `D` DNP, `P` POS 파일에 없는 모델, `V` unspecified, `S` SMD, `T` Through hole.

---

## Common · #common

KiCad 전반(PCB 에디터 포함)에서 사용 가능한 공용 액션. 단축키는 **Hotkeys** 섹션에서 임의 액션에 할당 가능.

| 액션 | 기본 단축키 | 설명 |
| --- | --- | --- |
| Close | `Ctrl`+`W` |  |
| Quit | `Ctrl`+`Q` |  |
| Refresh Plugins |  | 모든 python 플러그인 다시 로드·플러그인 메뉴 새로고침 |
| Exclude Marker |  | Checker 창의 현재 위반을 제외로 표시 |
| Next Marker |  |  |
| Previous Marker |  |  |
| Add Library… |  | 기존 라이브러리 폴더 추가 |
| Center Justify |  | 필드·텍스트 항목 가운데 정렬 |
| Pan to Center Selected Objects |  |  |
| Collapse All |  |  |
| 45 Degree Crosshairs |  | 45·135도 정렬 전체 창 십자선 표시 |
| Click | `Return` | 좌클릭 수행 |
| Double-click | `End` | 좌측 더블클릭 수행 |
| Cursor Down | `Down` |  |
| Cursor Down Fast | `Ctrl`+`Down` |  |
| Full-Window Crosshairs |  | 0·90도 정렬 전체 창 십자선 표시 |
| Cursor Left | `Left` |  |
| Cursor Left Fast | `Ctrl`+`Left` |  |
| Cursor Right | `Right` |  |
| Cursor Right Fast | `Ctrl`+`Right` |  |
| Small crosshairs |  | 0·90도 정렬 작은 십자선 사용 |
| Cursor Up | `Up` |  |
| Cursor Up Fast | `Ctrl`+`Up` |  |
| Grid Origin…​ |  | 그리드 원점 설정 |
| Edit Grids…​ |  | 그리드 정의 편집 |
| Expand All |  |  |
| Switch to Fast Grid 1 | `Alt`+`1` |  |
| Switch to Fast Grid 2 | `Alt`+`2` |  |
| Cycle Fast Grid | `Alt`+`4` |  |
| Switch to Next Grid | `N` |  |
| Switch to Previous Grid | `Shift`+`N` |  |
| Reset Grid Origin |  |  |
| Grid Origin |  | 그리드 원점 배치 |
| Hide Library Tree |  |  |
| Inactive Layer View Mode |  | 비활성 레이어를 normal/dimmed 간 토글 |
| Inactive Layer View Mode (3-state) | `H` | 비활성 레이어를 normal/dimmed/hidden 간 순환 |
| Inches |  |  |
| Left Justify |  | 필드·텍스트 항목 좌측 정렬 |
| Focus Library Tree Search Field | `Ctrl`+`L` |  |
| Snap to Objects on the Active Layer Only |  | 활성 레이어 객체에만 스내핑 활성화 |
| Snap to Objects on All Layers |  | 모든 가시 레이어 객체에 스내핑 활성화 |
| Toggle Snapping Between Active and All Layers | `Shift`+`S` | 모든 가시 레이어 스내핑과 활성 영역만 스내핑 간 토글 |
| Millimeters |  |  |
| Mils |  |  |
| New…​ | `Ctrl`+`N` | 에디터에서 새 문서 생성 |
| New Library… |  | 새 라이브러리 폴더 생성 |
| Open…​ | `Ctrl`+`O` | 기존 문서 열기 |
| Open in file explorer…​ |  | 시스템 파일 탐색기로 라이브러리 파일 열기 |
| Edit in a Text Editor…​ |  | 텍스트 에디터로 라이브러리 파일 열기 |
| Page Settings…​ |  | 용지 크기·title block 정보 설정 |
| Pan Down | `Shift`+`Down` |  |
| Pan Left | `Shift`+`Left` |  |
| Pan Right | `Shift`+`Right` |  |
| Pan Up | `Shift`+`Up` |  |
| Pin Library |  | 라이브러리를 목록 상단에 유지 |
| Plot…​ |  |  |
| Print…​ | `Ctrl`+`P` |  |
| Quit |  | 현재 에디터 닫기 |
| Redo Last Zoom |  | 마지막 zoom undo 이전 레벨로 줌 복귀 |
| Reset Local Coordinates | `Space` |  |
| Revert |  | 변경 사항 버리기 |
| Right Justify |  | 필드·텍스트 항목 우측 정렬 |
| Save | `Ctrl`+`S` | 변경 사항 저장 |
| Save All |  | 모든 변경 사항 저장 |
| Save As… | `Ctrl`+`Shift`+`S` | 현재 문서를 다른 위치에 저장 |
| Save a Copy…​ |  | 현재 문서 사본을 다른 위치에 저장 |
| Select Columns…​ |  |  |
| 3D Viewer | `Alt`+`3` | 3D viewer 창 표시 |
| Calculator Tools |  | 부품 계산·트랙 폭 계산 등 실행 |
| Show Context Menu |  | 우클릭 동작 수행 |
| Show Datasheet | `D` | 브라우저에서 datasheet 열기 |
| Footprint Library Browser |  |  |
| Footprint Editor |  | 보드 풋프린트 생성·삭제·편집 |
| Library Tree |  |  |
| Switch to Project Manager |  | 프로젝트 창 표시 |
| Properties |  | properties 매니저 표시/숨김 |
| Symbol Library Browser |  |  |
| Symbol Editor |  | 회로도 심볼 생성·삭제·편집 |
| Draw Bounding Boxes |  |  |
| Always Show Crosshairs |  | 객체를 그리지 않을 때도 십자선 표시 |
| Show Grid |  | 편집 창에 배경 그리드 표시 |
| Grid Overrides | `Ctrl`+`Shift`+`G` | 현재 그리드를 재정의하는 항목별 그리드 활성화 |
| Polar Coordinates |  | 극좌표·직교좌표계 간 전환 |
| Switch units | `Ctrl`+`U` | imperial·metric 단위 간 전환 |
| Undo Last Zoom |  | 마지막 zoom 동작 이전 레벨로 줌 복귀 |
| Unpin Library |  | 라이브러리를 더 이상 목록 상단에 유지하지 않음 |
| Update PCB from Schematic… | `F8` | 회로도 변경 사항으로 PCB 업데이트 |
| Update Schematic from PCB…​ |  | PCB 변경 사항으로 회로도 업데이트 |
| Center on Cursor | `F4` |  |
| Zoom to All Objects | `Ctrl`+`Home` | 화면의 모든 객체에 줌 |
| Zoom to Fit | `Home` | worksheet 영역(있으면) 또는 편집 객체에 줌 |
| Zoom to Selected Objects |  | 현재 선택 항목에 줌 |
| Zoom In at Cursor | `F1` |  |
| Zoom In |  |  |
| Zoom In Horizontally |  | plot 영역을 수평으로 줌 인 |
| Zoom In Vertically |  | plot 영역을 수직으로 줌 인 |
| Zoom Out at Cursor | `F2` |  |
| Zoom Out |  |  |
| Zoom Out Horizontally |  | plot 영역을 수평으로 줌 아웃 |
| Zoom Out Vertically |  | plot 영역을 수직으로 줌 아웃 |
| Refresh | `F5` |  |
| Zoom to Selection Area | `Ctrl`+`F5` | 마우스 드래그로 만든 영역 선택에 줌 |
| Embedded Files |  | 임베드된 파일 관리 |
| Extract File |  | 임베드된 파일 추출 |
| Remove File |  | 임베드된 파일 제거 |
| Add Items |  | 그룹에 항목 추가 |
| Cancel |  | 현재 도구 취소 |
| Copy | `Ctrl`+`C` | 선택 항목을 클립보드에 복사 |
| Copy as Text | `Ctrl`+`Shift`+`C` | 선택 항목을 텍스트로 클립보드에 복사 |
| Cut | `Ctrl`+`X` | 선택 항목을 클립보드로 잘라내기 |
| Cycle Arc Editing Mode | `Ctrl`+`Space` | 다른 호 편집 방식으로 전환 |
| Delete | `Del` | 선택 항목 삭제 |
| Interactive Delete Tool |  | 클릭한 항목 삭제 |
| Duplicate | `Ctrl`+`D` | 선택 항목 복제 |
| Find | `Ctrl`+`F` |  |
| Find and Replace | `Ctrl`+`Alt`+`F` |  |
| Find Next | `F3` |  |
| Find Next Marker | `Ctrl`+`Shift`+`F3` |  |
| Find Previous | `Shift`+`F3` |  |
| Finish | `End` | 현재 도구 완료 |
| Group Items |  | 선택 항목을 단일 항목으로 다루도록 그룹화 |
| Enter Group |  | 그룹에 진입해 항목 편집 |
| Leave Group |  | 현재 그룹에서 나가기 |
| Measure Tool | `Ctrl`+`Shift`+`M` | 점 간 거리를 대화형으로 측정 |
| Paste | `Ctrl`+`V` | 클립보드에서 항목 붙여넣기 |
| Paste Special…​ | `Ctrl`+`Shift`+`V` | 옵션과 함께 클립보드에서 항목 붙여넣기 |
| Redo | `Ctrl`+`Y` |  |
| Remove Items |  | 그룹에서 항목 제거 |
| Replace All |  |  |
| Replace and Find Next |  |  |
| Search | `Ctrl`+`G` | search 패널 표시/숨김 |
| Select All | `Ctrl`+`A` | 화면의 모든 항목 선택 |
| Lasso |  | 선택 모드를 폴리곤 lasso로 설정 |
| Rectangle |  | 선택 모드를 rectangle로 설정 |
| Undo | `Ctrl`+`Z` |  |
| Ungroup Items |  | 선택 그룹 해제 |
| Unselect All | `Ctrl`+`Shift`+`A` | 화면의 모든 항목 선택 해제 |
| Select Row(s) |  | 현재 선택 셀이 포함된 행 전체 선택 |
| Select Column(s) |  | 현재 선택 셀이 포함된 열 전체 선택 |
| Select Table |  | 선택 셀의 부모 테이블 선택 |
| Select item(s) |  |  |
| About KiCad |  |  |
| Configure Paths… |  | 경로 구성 환경 변수 편집 |
| Donate |  | 웹 브라우저에서 "Donate to KiCad" 열기 |
| Get Involved |  | 웹 브라우저에서 "Contribute to KiCad" 열기 |
| Getting Started with KiCad |  | 초보자용 "Getting Started in KiCad" 가이드 열기 |
| Help |  | 웹 브라우저에서 제품 문서 열기 |
| List Hotkeys…​ | `Ctrl`+`F1` | 현재 단축키 테이블·대응 명령 표시 |
| Preferences…​ | `Ctrl`+`,` | 열려 있는 모든 도구의 preferences 표시 |
| Report Bug |  | KiCad 문제 보고 |
| Manage Design Block Libraries…​ |  | 전역·프로젝트 design block 라이브러리 목록 편집 |
| Manage Footprint Libraries…​ |  | 전역·프로젝트 풋프린트 라이브러리 목록 편집 |
| Manage Symbol Libraries… |  | 전역·프로젝트 심볼 라이브러리 목록 편집 |
| Add Column After |  | 선택 셀 뒤에 새 테이블 열 삽입 |
| Add Column Before |  | 선택 셀 앞에 새 테이블 열 삽입 |
| Add Row Above |  | 선택 셀 위에 새 테이블 행 삽입 |
| Add Row Below |  | 선택 셀 아래에 새 테이블 행 삽입 |
| Delete Column(s) |  | 현재 선택 셀이 포함된 열 삭제 |
| Delete Row(s) |  | 현재 선택 셀이 포함된 행 삭제 |
| Merge Cells |  | 선택 테이블 셀을 단일 셀로 합치기 |
| Unmerge Cells |  | 합쳐진 테이블 셀을 개별 셀로 되돌리기 |

> 💡 자주 쓰는 공용 단축키: `Ctrl`+`S` Save, `Ctrl`+`Z`/`Ctrl`+`Y` Undo/Redo, `Ctrl`+`C`/`Ctrl`+`X`/`Ctrl`+`V` Copy/Cut/Paste, `Ctrl`+`A` Select All, `Ctrl`+`F` Find, `Del` Delete, `Home` Zoom to Fit, `Alt`+`3` 3D Viewer, `F8` Update PCB from Schematic, `Ctrl`+`U` 단위 전환, `Ctrl`+`F1` List Hotkeys, `Ctrl`+`,` Preferences.

> ⚠️ `D`(Show Datasheet)와 같은 단일 키는 컨텍스트에 따라 다른 동작이 매핑될 수 있다(3D Viewer의 `D`는 Show 3D Models marked DNP). 충돌 시 활성 도구·창의 컨텍스트가 우선한다.
