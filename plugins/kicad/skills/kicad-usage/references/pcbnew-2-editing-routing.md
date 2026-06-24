# PCB 에디터 ② — 편집·배치·배선 — KiCad 10.0 사용 다이제스트

> **원문**: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html

> **범위**: 배치/그리기, 그리드/스냅, 객체 속성 편집, 보드 외곽(Edge Cuts), 풋프린트 작업, 패드 작업, Zone(구리 채움), 트랙/비아 배선, 차동쌍 배선, 길이 튜닝, Teardrops, Backdrill/홀 후가공, 그래픽/텍스트, Rule areas(keepout), Locking, Groups, 정렬/분배, Arrays, 레퍼런스 이미지, 핀/게이트 스왑

> 한국어 요약 다이제스트. 섹션 제목의 #anchor로 원문 핀포인트: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#<anchor>

## 목차

- [Editing a board (개요)](#editing_a_board) — 보드 편집 챕터 개요
- [Placement and drawing operations](#placement-and-drawing-operations) — 우측 툴바 배치/그리기 도구 일람
- [Grids and snapping](#grids-and-snapping) — 그리드/객체 스냅, 모디파이어 키
- [Snapping to graphical shapes](#snapping_to_graphical_shapes) — 그래픽 형상 스냅 포인트
- [Grid settings](#grid_settings) — 그리드 설정·오버라이드·원점
- [Editing object properties](#editing-object-properties) — `E` 속성 편집, Properties Manager
- [Board outlines (Edge Cuts)](#board-outlines) — `Edge.Cuts` 보드 외곽
- [Working with footprints](#working-with-footprints) — 풋프린트 추가/이동/편집/갱신/비교
- [Working with pads](#working_with_pads) — 개별 패드 속성/네트 편집
- [Working with zones](#working-with-zones) — 구리 채움(Zone) 개요·우선순위
- [Drawing zones](#drawing_zones) — Zone 그리기·편집·병합·컷아웃
- [Zone properties](#zone-properties) — Zone 속성(레이어/네트/클리어런스/패드연결/해칭)
- [Zone manager](#zone-manager) — 전체 Zone 일괄 관리·우선순위
- [Routing tracks and vias](#routing-tracks) — 인터랙티브 라우터 개요·모드
- [Interactive router settings](#interactive-router-settings) — 라우터 설정 표
- [Track posture](#track-posture) / [Track corner mode](#track_corner_mode) / [Track width](#track_width) — 자세·코너모드·폭
- [Placing vias](#placing-vias) / [Layer Pairs](#layer_pairs) / [Placing free vias](#placing-free-vias) — 비아 배치
- [Modifying tracks](#modifying-tracks) / [Editing track and via properties](#track-and-via-properties) — 트랙/비아 수정·속성
- [Via padstack/protection/backdrill/post-machining](#via_size_position_and_layers) — 비아 패드스택·IPC-4761·백드릴·후가공
- [Bulk/Remove/Cleanup tracks and vias](#bulk-editing-tracks-and-vias) — 일괄편집·미사용패드·정리
- [Routing convenience / Auto-complete](#routing_convenience_functions) — Route Selected, Autoroute
- [Routing differential pairs](#routing-differential-pairs) — 차동쌍 배선
- [Length tuning](#length-tuning) — 사행(serpentine) 길이/스큐 튜닝
- [Time-domain tuning](#time-domain-tuning) — 전파지연 기반 튜닝
- [Teardrops](#editing-teardrops) — 티어드롭
- [Backdrills and hole post-machining](#backdrills_and_hole_post_machining_counterborescountersinks) — 백드릴·카운터보어/싱크
- [Graphics and text](#pcb-graphical-objects) — 그래픽 형상/텍스트/표/치수/바코드/포인트
- [Rule areas (keepouts)](#pcb-rule-areas) — 룰 영역(keepout)
- [Locking](#locking) / [Groups](#groups) — 잠금/그룹
- [Aligning](#aligning_objects) / [Distributing](#distributing_objects) / [Arrays](#creating-arrays) — 정렬/분배/배열
- [Using reference images](#pcb-reference-images) — 레퍼런스 이미지
- [Pin and gate swapping](#pin-and-gate-swapping) — 핀/게이트 스왑

---

## Editing a board (개요) · #editing_a_board

보드 **편집** 전반(배치·그리기·그리드/스냅·풋프린트·패드·Zone·트랙/비아 배선·차동쌍·길이 튜닝·그래픽·Rule area·Group/Array·핀/게이트 스왑)을 다루는 챕터. 세부 작업은 아래 섹션 참조.

## Placement and drawing operations · #placement-and-drawing-operations

- 배치/그리기 도구는 **우측 툴바**에 위치. 도구를 활성화하면 다른 도구 선택 또는 `Esc`로 취소할 때까지 유지된다. 다른 도구를 취소하면 항상 Selection 도구가 활성화된다.
- 버튼 우하단 작은 화살표 = **팔레트**(여러 도구 묶음). 버튼을 클릭·홀드하거나 드래그하면 팔레트가 열리고, 닫을 때 마지막 사용 도구가 표시된다.
- 💡 툴바 구성은 **PCB Editor Preferences → Toolbar** 페이지에서 편집 가능.

| 도구 | 기능 |
| --- | --- |
| Selection tool (기본) | 사각형 모드: 클릭·드래그로 사각 선택. Lasso 모드: 클릭·드래그로 올가미 선택. 팔레트로 모드 전환. |
| Local ratsnest tool | 보드 ratsnest가 숨겨졌을 때, 선택한 풋프린트의 ratsnest만 표시. 같은 풋프린트 재선택 시 숨김. 도구를 끈 뒤에도 풋프린트별 설정 유지. |
| Footprint placement tool | 보드 클릭 → footprint chooser 열림 → 선택 후 다시 클릭해 위치 확정. (`A`) |
| Route tracks / Route differential pairs | 인터랙티브 라우터 활성화. 트랙·비아 배치. 팔레트로 라우터 종류 전환. (Routing 섹션 참조) |
| Tune length | 라우팅 후 단일 트랙 길이, 또는 차동쌍 길이/스큐 튜닝. 팔레트로 튜너 종류 전환. |
| Add vias | 트랙 없이 독립("free") 비아 배치. |
| Add filled zone | 클릭으로 시작점 → 속성 설정 후 외곽 그리기. |
| Add rule area | 룰 영역(구 keepout). 객체 배치·zone fill 제한, 명명 영역 + 커스텀 DRC 규칙 적용. |
| Draw lines | 선 그리기. **Note:** 라인은 그래픽 객체이며 Route Tracks의 트랙과 다름. |
| Draw arcs | 중심점 → 시작·끝점. 우클릭으로 호 편집 모드 변경(중심/끝점/각도/반경 유지 방식). |
| Draw rectangles | 사각형. 채움 또는 외곽선. |
| Draw circles | 원. 채움 또는 외곽선. |
| Draw graphical polygons | 그래픽 다각형. 채움/외곽선. **Note:** 채워진 그래픽 폴리곤 ≠ filled zone(네트 할당·클리어런스 유지 안 됨). |
| Draw bezier curves | 베지어 곡선. 클릭마다 노드 고정/제어 핸들 고정 교대. |
| Add bitmap image | 참조용 비트맵 이미지. 제조 출력에 미포함. |
| Add text / Add a textbox / Add a table | 텍스트 / 텍스트박스 / 표. |
| Add dimensions | 치수(orthogonal/aligned/center/radial/leader). 팔레트로 종류 전환. |
| Add barcode | 바코드 추가. |
| Deletion tool | 클릭한 객체 삭제. |
| Set grid origin / drill·place origin | 제조 출력용 원점 설정. 팔레트로 종류 전환. |
| Add a point | 비물리·무차원 객체. 스냅·문서화용. |
| Measurement | 두 지점 간 거리 인터랙티브 측정. |

## Grids and snapping · #grids-and-snapping

- 이동/드래그/그리기 시 그리드 또는 패드·기타 객체의 스냅 포인트에 스냅됨. 복잡한 설계에서 스냅점이 너무 가까우면 모디파이어 키로 임시 비활성화.
- ⚠️ Apple 키보드에서는 `Ctrl` 대신 `Cmd` 사용.

| Modifier Key | Effect |
| --- | --- |
| `Ctrl` | Disable grid snapping. (그리드 스냅 끔) |
| `Shift` | Disable object snapping. (객체 스냅 끔) |

- 보이는 레이어의 객체에만 스냅됨. 불필요한 레이어를 숨기거나 single-layer view 모드로 스냅점 감소.
- `Shift`+`S`: 모든 레이어 스냅 ↔ 현재 레이어만 스냅 토글.
- 패드/트랙/그래픽 스냅 종류는 **Preferences → PCB Editor → Editing Options**에서 설정.

### Snapping to graphical shapes · #snapping_to_graphical_shapes

- 사각형·호 등 그래픽 형상 작업 시 추가 스냅 포인트 제공: **Endpoints/corners(끝점/모서리), Midpoints(중점), Centers(중심), Intersection points(교차점)**.
- 스냅 포인트에 호버하면 아이콘으로 스냅 종류 표시, 클릭으로 사용. 일부 형상은 보조 스냅선 표시(라인 세그먼트는 연장선, 호는 원주를 완성하는 보조원). 보조 형상에도 스냅 가능(보라색 실선).
- 스냅 포인트에서 커서를 이동하면 수평/수직 점선(보라색 점선)이 나타나 해당 스냅점과 수평/수직 정렬을 유지하는 투영 위치를 표시.

### Grid settings · #grid_settings

- 인터랙티브 편집은 활성 그리드에 스냅. 상단 툴바 grid 드롭다운 또는 우클릭 **Grid** 서브메뉴로 변경. `n`/`N`: 다음/이전 그리드 순환.
- **Preferences → Grids** 패널에서 활성 그리드 선택·재정렬·추가/삭제/편집. 좌측 툴바 grid 버튼 우클릭 → **Edit Grids…**가 단축 경로.
- 그리드는 X/Y 간격을 다르게 줄 수 있고 선택적 이름 지정 가능.
- **Fast Grids**: 목록에서 두 그리드를 지정해 `Alt`+`1`, `Alt`+`2`로 빠르게 선택.
- **Grid overrides**: 객체 종류별로 기본 그리드 대신 사용할 그리드 지정(예: 풋프린트/패드는 100 mil, 트랙/비아/텍스트는 미세 그리드). 개별 토글 또는 좌측 툴바 버튼(`Ctrl`+`Shift`+`G`)으로 전역 토글.
- 그리드 원점 변경: **Place → Grid Origin** 클릭 배치(우측 툴바 grid origin 버튼), 또는 **Edit → Grid Origin…**로 좌표 직접 입력.
- ⚠️ KiCad의 여러 원점 구분:
  - **Grid origin**: 그리드 정렬 기준점. 이동 시 모든 그리드점 이동.
  - **Page origin**: 절대 원점. 항상 시트 좌상단.
  - **Drill/place file origin**: 제조 출력용 설정 가능 점(**Place → Drill/Place File Origin**).
  - **Local origin**: `Space`로 현재 커서 위치에 설정하는 상대 원점. 상태바에 로컬 원점 기준 좌표 표시.
- 그리드 외형: **Display Options** 페이지에서 두께·모양(dots/lines/crosses)·최소 표시 간격 설정, **Colors** 페이지에서 색상. 좌측 툴바 show grid 버튼으로 표시/숨김. 기본은 숨겨도 활성 유지(Display Options에서 숨김 시 비활성 또는 완전 비활성 설정 가능).

## Editing object properties · #editing-object-properties

- 모든 객체는 다이얼로그로 속성 편집 가능. `E` 또는 우클릭 **Properties**.
- 선택 객체가 **모두 같은 타입**일 때만 다이얼로그 열림. 풋프린트 등 다수 타입은 한 번에 하나만 편집. 여러 객체(다른 타입 포함) 동시 편집은 **Properties Manager** 사용.
- **Properties Manager**: 도킹 패널. 선택 객체 속성 표시·편집. 다중 타입 선택 시 공통 속성만 표시. 편집 즉시 적용. 다중 선택 시 각 객체에 개별 적용(예: 회전은 각 객체 자체 원점 기준). 열기: **View → Panels → Properties** 또는 좌측 툴바 버튼.
- 벌크 편집 도구: 텍스트/그래픽(풋프린트 필드·치수 포함) → **Edit Text and Graphics Properties**, 트랙/비아 → **Edit Track and Via Properties**, 티어드롭 → **Edit Teardrops**.
- 💡 숫자 입력 필드는 **기본 수식** 허용: `2 * 2mm` → 4mm. 사칙연산·괄호·단위 지원, 단위 자동 변환(`1in + 1mm` → 26.4mm).

## Board outlines (Edge Cuts) · #board-outlines

- KiCad는 `Edge.Cuts` 레이어의 그래픽 객체로 보드 외곽을 정의. 외곽은 연속(닫힌) 형상이어야 하며, 라인·호 조합 또는 사각형·폴리곤 단일 객체 가능.
- ⚠️ 외곽이 없거나 무효면 3D 뷰어·일부 DRC가 동작하지 않음.
- **Board area shadow**(음영): 닫힌 외곽 내부를 음영 표시 → 외곽이 제대로 닫혔는지/솔리드 영역인지 확인. **Appearance 패널 → Objects 탭**에서 색상 조정·숨김.
- 유효 외곽 조건: 형상 끝점이 **정확히** 일치해야 닫힘으로 인정. 불일치 시 닫히지 않음. 외곽 형상끼리 교차·중첩 금지. 위반 시 DRC가 **"Board has malformed outline"** 보고.
- 💡 그리드/스냅으로 끝점 정확히 일치시키기. **Heal Shapes** 도구로 작은 틈 보정 가능.
- `Edge.Cuts`에 닫힌 형상이 여러 개면 각각 독립 외곽. 한 외곽이 다른 외곽을 완전히 둘러싸면 바깥쪽이 보드 외곽선, 안쪽 닫힌 형상은 내부 컷아웃(interior cutout). 외곽끼리 교차·중첩 불가.
- Zone은 보드 외곽 내부에서만 채워짐. 외곽 밖(내부 컷아웃 포함)은 채워지지 않음.

## Working with footprints · #working-with-footprints

### 풋프린트 추가 · #adding_footprints_to_the_board

- 스키매틱에서 PCB 갱신(Update from schematic) 시 풋프린트 자동 추가. 심볼 핀 번호 ↔ 패드 번호로 매칭되어 네트 할당. 스키매틱 시트·지리적 위치별로 클러스터되어 커서에 부착됨 → 클릭 배치.
- 수동 추가: Add Footprint 도구(`A`).
- ⚠️ 수동 추가 풋프린트는 심볼·네트 미연결 상태. 다음 스키매틱 갱신 시 제거됨(풋프린트가 locked이거나 **Delete footprints with no symbols** 옵션을 끄지 않는 한). 일반적으로 비권장하나 PCB-only 워크플로, 로고 등에는 유용.

### 풋프린트 배치/이동 · #placing_and_moving_footprints

- **Move (`M`)**: 선택 풋프린트 이동, 비선택 연결 트랙 무시. DRC 미검사(코트야드 충돌만 하이라이트). 참조점은 Move 시작 시 커서 위치로 결정 — 패드 위면 패드 중심, 아니면 풋프린트 anchor. 임의 참조점은 우클릭 **Move with Reference**.
- **Drag (`D`)**: 라우터로 이동, 모든 트랙 연결 유지(Highlight Collisions 동작: 회피·shove 없이 하이라이트만). DRC 위반 위치에서 커밋하면 원위치 복귀. `Ctrl`-클릭으로 위반 무시 커밋. ⚠️ 패드 origin에서 끝나는 트랙만 드래그됨(통과하거나 origin 외 위치에서 끝나는 트랙은 제외).
- **Flip (`F`)**: 반대 면으로 이동. 앞/뒤 레이어 스왑.
- **Rotate**: `R`(반시계), `Shift`+`R`(시계). 기본 90° 단위. 회전 각도 step은 **Preferences → PCB Editor → Editing Options**에서 설정.
- 정확한 절대 위치·각도·면: Footprint Properties 또는 Properties 패널에서 직접 설정.
- **Move Exactly (`Shift`+`M`** 또는 우클릭 **Position → Move Exactly…)**: X/Y 이동 + 회전. 회전 기준은 anchor/local origin/drill·place origin 선택. 극좌표 가능.
- **Position Relative (`Shift`+`P`** 또는 우클릭 **Position → Position Relative To…)**: 참조점 + 오프셋. 참조점: local origin(`Space`로 설정) / grid origin / 임의 보드 객체(**Select Item…**) / 임의 점(**Select Point…**, 객체 스냅 가능).
- **Interactive Offset (우클릭 → Position → Interactive Offset Tool…)**: 두 점(풋프린트 내 참조점 + 고정 참조점)으로 위치 벡터를 만들고 X/Y(또는 극좌표) 치수를 입력해 거리 조정.
- **Swap (`Alt`+`S`)**: 두 풋프린트의 위치·회전·면 교환. 3개 이상이면 위치를 순환.
- **Get and Move Footprint (`T`)**: 목록/레퍼런스 입력으로 풋프린트 선택해 커서에 부착.
- **Select All Unconnected Footprints (`O`)**: 선택 풋프린트와 ratsnest로 연결된 모든 풋프린트 선택(반복 실행 시 확장).
- **Grab Nearest Unconnected Footprint (`Shift`+`O`)**: 가장 가까운 미배선 풋프린트 선택 + 이동 시작.
- 우클릭 **Select → Items in Same Hierarchical Sheet**: 같은 스키매틱 시트 풋프린트 선택.
- **Move Individually (`Ctrl`+`M`)**: 선택 풋프린트를 선택 순서대로 하나씩 이동. `Tab`=스킵, 더블클릭=현재 커밋+나머지 스킵, `Esc`=전체 취소(완료분 포함).
- **Pack and Move Footprints (`P`)**: 선택 풋프린트를 한 블록으로 밀집해 함께 이동.
- 💡 Move Individually / Pack and Move는 스키매틱 크로스셀렉션, Select All Unconnected 등과 조합하면 효율적.
- 자동 배치: **Place → Auto-Place Footprints → Place Selected Footprints** / **Place Off-Board Footprints**(보드 밖 풋프린트 전체).

### 보드 내 풋프린트 편집 · #board-editing-footprints

- 보드 내 풋프린트는 속성(필드·속성·클리어런스 등)과 물리적 형태(패드·그래픽) 모두 편집 가능. 편집은 **해당 인스턴스에만** 적용(다른 사본·라이브러리 미영향).
- 속성 다이얼로그: `E`. 대부분 footprint editor와 동일하나, 여기서는 위치·방향·면도 설정 가능. 라이브러리에서 갱신·교체·footprint editor에서 편집 가능.
- 물리적 형태 편집:
  - **Edit Footprint…**(우클릭 **Open in footprint editor**, `Ctrl`+`E`): 보드 내 특정 인스턴스만 편집.
  - **Edit Library Footprint…**: 라이브러리 사본 편집(보드 인스턴스는 즉시 미반영, Update Footprint from Library로 갱신).

### 풋프린트 필드 편집 · #editing_footprint_fields

- 개별 텍스트 필드는 `E`(필드 선택 상태) 또는 더블클릭으로 직접 편집. 옵션은 전체 Footprint Properties와 동일하나 단일 필드 한정.
- 보드 에디터에서는 **풋프린트 필드만** 편집 가능. Footprint text는 그래픽 객체로 footprint editor에서만 편집/이동 가능.
- ⚠️ KiCad 8.0 이전에는 풋프린트 필드가 없고 footprint text를 보드 에디터에서 직접 편집했음. 8.0+부터 footprint text는 보드 에디터에서 편집 불가.

### 풋프린트 갱신/교환 · #updating-and-exchanging-footprints

- 보드에 추가된 풋프린트는 라이브러리 사본을 임베드(보드가 시스템 라이브러리와 독립). 라이브러리 변경은 **수동** 동기화.
- 💡 **Compare Footprint with Library** 도구로 차이 확인.
- 갱신: **Tools → Update Footprints from Library…** 또는 우클릭 **Update Footprint…**(속성 다이얼로그에서도 접근).
  - 상단: 갱신 대상 선택(전체/선택/레퍼런스·값·라이브러리 ID 매칭). 레퍼런스·값은 와일드카드(`*`=0개 이상, `?`=단일 문자) 지원.
  - 중단: 갱신 항목 제어(필드 선택, 갱신 속성=text/visibility/size·style/position, 누락·빈 필드 처리, 클리어런스 오버라이드, 풋프린트 attributes).
  - 하단: 수행 결과 메시지.
- 교체: **Edit → Change Footprints…** 또는 우클릭 **Change Footprint…**. 옵션은 Update와 유사.

### 보드↔라이브러리 풋프린트 비교 · #comparing-footprints

- **Inspect → Compare Footprint With Library**.
- **Summary 탭**: 풋프린트명·라이브러리·레퍼런스 + 차이 목록.
- **Visual 탭**: 시각 비교(visual diff). 기본은 두 버전 중첩. 하단 슬라이더로 보드/라이브러리 버전 강조(투명도 조절), 양끝에서 한쪽 완전 숨김. **A/B** 버튼 또는 `/` 단축키로 빠른 토글.
- **Update Footprint from Library…** 버튼으로 갱신 도구 열기.

## Working with pads · #working_with_pads

- 보드에 배치한 풋프린트의 개별 패드 속성을 검사·편집(특정 인스턴스의 패드 디자인 오버라이드). 예: 특정 패드의 솔더 페이스트 개구 제거, 축리드 저항의 스루홀 패드 위치 이동.
- ⚠️ 기본적으로 모든 패드 위치는 **잠김** — 속성 편집은 되나 풋프린트 내 위치 이동은 불가. 언락하면 자유 이동 가능(스루홀의 리드 위치 가변 등에 유용, SMD는 일반적으로 비권장).
- 패드 속성 다이얼로그: 컨텍스트 메뉴 또는 `E`(패드 선택 시). KiCad는 패드 근처 클릭 시 전체 풋프린트 선택을 가정 → 단일 패드 선택은 패드 영역 **안쪽** 클릭하거나, selection filter에서 Footprints 끄고 Pads 켜기.
- 물리 속성(크기·형상), 연결 방식(클리어런스·teardrops·thermal relief) 편집. footprint editor의 패드 속성과 동일하되, 여기서는 **net name** 셀렉터로 패드에 네트 수동 할당 가능.
- ⚠️ 패드 네트 수동 할당은 일반적 워크플로 아님 — 보통 스키매틱에서 정의되어 PCB로 전달됨.

## Working with zones · #working-with-zones

- **Copper zone(구리 채움/pour/fill)**: 특정 네트에 할당된 솔리드/해치 구리 영역. 다른 구리 객체와 자동 클리어런스 유지. GND/전원 플레인, 고전류, 차폐용.
- ⚠️ 다른 EDA의 "plane layer"와 signal layer copper zone을 KiCad는 모두 **Copper Zone 도구** 하나로 처리.
- Zone은 **outline**(최대 채움 범위; 물리적 구리 아님, 제조 데이터 미포함)으로 정의되고 **fill**(실제 구리)은 outline/내부 객체 변경 시마다 다시 채워야 함.
- 채우기: 전체 `B`, 개별 우클릭 **Zones → Draft Fill Selected Zone(s)**. 언채우기: `Ctrl`+`B`(성능·시각 정리).
- ⚠️ 기본적으로 zone fill은 **수동**(자동 아님 — 큰 설계·구형 PC에서 느림). 출력·DRC 전 zone fill이 최신인지 확인 필요(KiCad가 경고). 자동 채움: **Preferences → PCB Editor → Editing Options → Miscellaneous → Automatically refill zones**.
- fill은 outline 내 빈 공간을 채우며 보드 외곽·홀·다른 네트 구리와 클리어런스 자동 유지. 외곽 밖·내부 컷아웃은 안 채움.
- **Priority(우선순위)**: 같은 레이어 다중 zone의 채움 순서. 높은 우선순위가 먼저 채워지고, 낮은 우선순위는 높은 zone의 채움 영역과 클리어런스 유지. 주 설정은 **Zone Manager**의 상대 순서(위=높음), 우클릭 **Zones → Zone Priority** 서브메뉴, 또는 properties 패널의 Priority 값.

### Drawing zones · #drawing_zones

- 그리기: Add Filled Zone 도구 또는 `Ctrl`+`Shift`+`Z`. 첫 점 클릭 → Zone Properties 다이얼로그(네트 등; 나중에 변경 가능) → 점 추가로 outline 정의 → 더블클릭으로 마지막 점 설정.
- 💡 신규 zone 기본 속성은 **Board Setup → Defaults** 페이지에서 설정.
- outline 수정: 선택 후 편집 핸들 드래그. 모서리 핸들=코너 이동(인접 두 코너 각도 표시), 엣지 핸들=엣지를 수직 방향 이동. 보통 드래그는 인접 코너 각도 유지·엣지 길이 가변, `Ctrl` 홀드 시 엣지 길이 유지·각도 가변.
- 코너 정밀 위치: 우클릭 핸들 **Shape Modification → Move Corner To…**(X/Y 입력). 전체 코너: 우클릭 zone **Shape Modification → Edit Corners…**(좌표 표, 편집 즉시 반영).
- 💡 그래픽 형상을 zone으로 변환 가능(원 등 어려운 형상): 우클릭 **Create from Selection → Create Zone from Selection…**.
- 기타 **Zones** 서브메뉴 도구(Preferences에서 단축키 추가 가능):
  - **Merge Zones**: 두 zone 병합(겹치고, 같은 레이어, 같은 네트여야 함). 병합 우선순위는 원래 중 최고값.
  - **Add a Zone Cutout**: zone에 컷아웃 추가 → 채움 시 미채움 영역.
  - **Duplicate Zone onto Layer…**: zone 복사 + 레이어 등 속성 변경. (단순 레이어 추가는 기존 zone 속성에서 레이어 추가로도 가능.)
  - **Add a Similar Zone**: 기존 zone과 동일 설정으로 새 zone 그리기.

### Zone properties · #zone-properties

- 편집: `E` 또는 컨텍스트 메뉴 **Properties**.
- ⚠️ KiCad 10+에서 zone priority는 Zone Manager의 상대 순서로 설정(이전 버전의 다이얼로그 숫자 방식 변경). properties 패널에서 명시적 priority 값도 설정 가능.
- **Layers**: 한 zone 객체가 여러 구리 레이어에 채움 가능(각 레이어 독립 채움, 동일 네트 공유).
- **Zone name**: 선택적 이름. 커스텀 DRC 규칙에서 참조.
- **Net name**: 연결 네트 선택. 네트 없음도 가능(모든 네트 구리와 클리어런스 유지).
- **Locked**: 잠금. 잠긴 객체는 조작·이동 불가, selection filter의 **Locked Items** 켜야 선택.
- **Corner smoothing**: outline 코너 처리 — chamfer/fillet/없음. 크기 설정 가능. ⚠️ 기본적으로 **내부 코너**에는 chamfer/fillet 미적용(외곽 밖으로 구리가 나가므로). 원하면 **Board Setup → Constraints → Allow fillets outside zone outline** 활성화.
- **Remove islands**: 고립 구리(island) 처리 — **always**(제거), **never**(유지, 미연결 구리), **below area limit**(**minimum island size** 미만 제거). ⚠️ 전기적 미연결 zone(연결 패드 0개)에서는 island 제거 안 됨.
- **Open Zone Manager…**: Zone Manager 열기.

#### Clearances & pad connections · #clearances_pad_connections

- **Clearance**: 다른 구리와의 최소 클리어런스. 충돌 시 더 큰 값 사용(zone 0.2mm vs netclass 0.3mm → 0.3mm).
- **Minimum width**: zone 내부 좁은 넥(neck)의 최소 폭. 미만 영역은 채움 중 제거.
- **Pad connection**: 같은 네트 패드 연결 방식 — **Solid**(완전 중첩), **Thermal reliefs**(스포크로 연결, 열저항↑, 핸드 솔더링 유리), **Reliefs for PTH**(PTH는 thermal, SMD는 solid), **None**(미연결).
- **Thermal relief gap**: thermal relief 시 패드와 zone 간 거리.
- **Thermal spoke width**: 스포크 폭.

#### Display overrides · #display_overrides

- **Outline display**: **Line**(테두리만), **Hatched**(테두리 안쪽 짧은 해치), **Fully Hatched**(전체 해치).
- **Outline hatch pitch**: Hatched/Fully Hatched 해치선 간격.

#### Hatched fill · #zone-hatching

- **Hatched fill**: 솔리드 대신 해치 패턴으로 채움(구리량↓; 플렉시블 PCB 등).
- **Orientation**: 해치 라인 각도. 0°=수평·수직.
- **Hatch width / Hatch gap**: 해치 선폭 / 선 간격.
- **Smoothing effort**: 0(없음)~3(최고). 높을수록 처리시간↑·Gerber 크기↑.
- **Smoothing amount**: smoothing chamfer/fillet 크기 비율. 0.0(없음)~1.0(최대=해치 gap의 절반).
- **Hatch offset overrides**: 레이어별 해치 X/Y 오프셋 표(레이어 간 해치 격자 오프셋 강제). 💡 기본값은 **Board Setup → Zone Hatch Offsets** 페이지.

### Zone manager · #zone-manager

- 모든 zone을 한 번에 보기·편집·우선순위 설정. 실행: **Tools → Zone Manager**.

#### Zone list · #zone_list
- 좌측: 전체 zone 목록(이름·네트·레이어). 목록 순서 = 우선순위(위=높음). 드래그/위·아래/맨위·맨아래 버튼으로 변경.
- 자동 우선순위 버튼(sort): 겹치는 zone 쌍마다 overlap 영역에서 연결 패드·비아가 많은 zone에 높은 우선순위. 비슷하면 작은 zone이 높은 우선순위.
- 필터 박스(이름/네트, 옵션 의존) + **Layer** 드롭다운으로 필터.

#### Zone preview · #zone_preview
- 우하단 미리보기(줌·팬은 캔버스와 동일 조작). 💡 우클릭 **Zoom to Fit**로 전체 리셋. 멀티 레이어 zone은 레이어 탭으로 개별 미리보기.

#### Zone settings · #zone_settings
- 우측: 선택 zone 설정(위 zone properties와 동일). **Update Displayed Zones** 버튼으로 보드 미반영 미리보기. 변경은 **OK** 전까지 보드 미반영. **Refill zones** 활성 시 OK 시 전체 refill.

## Routing tracks and vias · #routing-tracks

- 인터랙티브 라우터: 단일 트랙·차동쌍 수동/반자동 배선, 드래그 시 재배선, 풋프린트 드래그 시 부착 트랙 재배선, 사행(serpentine) 길이·스큐 튜닝.
- 기본적으로 design rules 준수(트랙 폭·copper clearance). Highlight Collisions 모드 + Allow DRC Violations로 비활성화 가능.
- **라우터 3모드** (Interactive Router Settings, 신규 배선 + `D` Drag 공통):
  - **Highlight Collisions**: 대부분 기능 비활성, 완전 수동. 충돌(clearance 위반)은 녹색 하이라이트, Allow DRC Violations 꺼져 있으면 충돌 시 고정 불가. 한 번에 최대 2 세그먼트(예: 수평+대각).
  - **Shove**: 트랙이 못 움직이는 장애물(패드·잠긴 트랙·비아)은 우회, 움직일 수 있는 것은 밀어냄(shove). DRC 위반 방지(불가능하면 트랙 미생성).
  - **Walk Around**: Shove와 같으나 장애물을 밀지 않음.
- 권장: 대부분 Shove(효율), 비배선 트랙 보존 원하면 Walk Around. ⚠️ Shove/Walk Around는 항상 H/V/45 세그먼트만. 다른 각도는 Highlight Collisions + Free Angle Mode 필요.
- 4대 라우팅 기능: Route Single Track, Route Differential Pair, Tune length(single), Tune skew(diff pair). **Route** 메뉴 + 우측 툴바 오버로드 아이콘 2개(Route용/Tune용). Route 메뉴엔 Set Layer Pair, Interactive Router Settings도 있음.
- 배선 시작: Route Tracks 아이콘 또는 `X`. 시작점 클릭 → 네트 선택·배선 시작. 배선 네트는 하이라이트, 허용 클리어런스는 회색 외곽으로 표시(Display Options의 Clearance Outlines로 끔). ⚠️ 클리어런스 외곽은 현재 레이어 다른 구리와의 **최대** 클리어런스만 시각 표시.
- 배선 중: 시작점→커서로 **unfixed**(밝은 색) 임시 트랙이 그려짐. 좌클릭/`Enter`로 **fix**, `Esc`/다른 도구 시 fixed만 저장. **Finish Route (`End`)**: 전체 fix + 라우터 종료. **Undo Last Segment (`Backspace`)**: 최근 fix 세그먼트 되돌리기(반복 가능).
- ⚠️ KiCad 6+ 기본은 커서 위치 세그먼트까지 **포함** fix(이전엔 미포함). "Fix all segments on click" 옵션으로 복원.
- 배선 중 `Ctrl`=그리드 스냅 끔, `Shift`=객체 스냅 끔. 💡 객체 스냅은 Editing Options의 Magnetic Points로도 끄나, 일반적으로 켜둘 것을 권장(패드/비아 살짝 빗나감 방지).

### Interactive router settings · #interactive-router-settings

- 접근: **Route** 메뉴 또는 Route Tracks 버튼 우클릭. 신규 배선 + 기존 트랙 드래그 모두에 적용.

| Setting | Description |
| --- | --- |
| Mode | 라우터 동작 모드(신규+드래그). |
| Free angle mode | 45° 증분 대신 임의 각도. Highlight collisions 모드에서만. |
| Allow DRC violations | DRC 위반 트랙·비아 허용. Highlight collisions에서만. |
| Shove vias | 비아도 함께 shove. Shove 모드에서만. |
| Jump over obstacles | 충돌 트랙을 솔리드 장애물(패드 등) 뒤로 이동 시도. Shove에서만. |
| Remove redundant tracks | 현재 배선 트랙에 생긴 루프 자동 제거(가장 최근 구간 유지). |
| Optimize pad connections | 패드·비아 진출 시 예각 등 회피. |
| Smooth dragged segments | 드래그 시 세그먼트 결합으로 방향 변화 최소화. |
| Optimize entire track being dragged | 드래그 시 화면에 보이는 트랙 전체 최적화(불필요 코너 제거·예각 회피·최단경로). 끄면 드래그 구간만. |
| Use mouse path to set track posture | 시작점부터 마우스 경로로 posture 선택. |
| Fix all segments on click | 켜면 커서 끝 세그먼트 포함 전체 fix + 새 세그먼트 시작. 끄면 마지막 세그먼트 미고정(추가 이동으로 조정 가능). |

### Track posture · #track-posture

- H/V/45 모드에서 단일 세그먼트로 못 잇는 두 점은 (수평/수직 1 + 대각 1) 세그먼트로 연결. **posture** = 그 순서(직선 먼저 vs 대각 먼저).
- KiCad가 자동 선택(코너 최소화·예각 회피, 패드 진출 시 가장 긴 엣지에 정렬).
- **Switch Track Posture (`/`)**: posture 전환. via 시작 등 모호할 때는 마우스 이동 방향으로 결정(수평/수직 이동=직선 먼저, 대각 이동=대각 먼저). Interactive Router Settings에서 마우스 감지 끔.
- ⚠️ `/`로 수동 override 시 해당 배선 동안 마우스 자동 감지 비활성.

### Track corner mode · #track_corner_mode

- 4모드: **45 degree(기본)**, **45 degree rounded**, **90 degree**, **90 degree rounded**. **Track Corner Mode (`Ctrl`+`/`)**로 순환. Free angle 모드에선 미적용.
- 45도: 수평/수직/45° 대각, 45·135° 결합(기본·최일반).
- 90도: 대각 불가, 90° 결합.
- rounded: 각 스텝에 직선/단일 호/직선+호 배치. posture가 호/직선 순서 결정.
- 라우팅 후 **Fillet Tracks** 명령으로도 코너 라운딩(코너 양쪽 트랙 선택; 연속 선택의 다중 코너 모두 fillet). ⚠️ 호 포함 트랙 드래그 미지원(shove 라우터가 호를 불변으로 취급).

### Track width · #track_width

- 폭 결정 3가지: ① 시작점이 기존 트랙 끝 + 상단 auto track width 버튼 켜짐 → 기존 트랙 폭. ② track width 드롭다운 "use netclass width" → 네트클래스(또는 neckdown 등 커스텀 규칙) 폭. ③ Board Setup의 pre-defined 사이즈 선택 → 그 폭.
- ⚠️ 폭은 Board Setup → Constraints의 최소 트랙 폭 미만 불가(미만 사전정의 시 최소값 사용).
- 활성 배선 중 단일 폭만. 중간 폭 변경은 배선 종료 후 재시작. 활성 배선 폭 변경: `W`/`Shift`+`W`(Board Setup 사이즈 순환).

### Placing vias · #placing-vias

- 배선 중 레이어 전환 시 현재 unfixed 트랙 끝에 through via 삽입 → 새 레이어 계속 배선. 레이어 선택·비아 삽입 방법:
  - 특정 레이어 단축키: `PgUp`=`F.Cu`, `PgDn`=`B.Cu`.
  - Next/Previous Layer: `+`/`-`.
  - **Place Via (`V`)**: 활성 layer pair의 다음 레이어로. 끝점이 다른 레이어 항목으로 ratsnest 있으면 그 레이어로.
  - **Select Layer and Place Through Via (`<`)**: 다이얼로그로 타겟 레이어 선택.
- 비아 추가 후 fix 전 `V`로 취소(비아 제거, 원 레이어 계속).
- 레이어 변경 없이 비아 + 트랙 종료: `V` 후 더블클릭.
- 비아 크기: 상단 Via Size 드롭다운, Increase(`'`)/Decrease(`\`). "use netclass sizes"면 Net Classes 설정(커스텀 규칙 override 가능).
- 마이크로비아 `Ctrl`+`V`, 블라인드/베리드 `Alt`+`Shift`+`V`. 일반 비아는 전 레이어 관통, 마이크로/블라인드/베리드는 임의 레이어 시작·종료.
- ⚠️ DRC상 마이크로비아는 레이저 드릴이라 드릴 홀로 미간주.
- 라우터 배치 비아는 트랙 일부로 간주 → 네트 자동 갱신(스키매틱 변경 시). stitching via 등 미원할 시 via properties의 "automatically update via nets" 끔(Add Free-standing Vias 도구 비아는 기본 끔).

### Layer Pairs · #layer_pairs

- Place Via(`V`)는 현재 layer pair의 다른 레이어로 활성 레이어 스왑.
- **Set Layer Pair** 다이얼로그(select layer pair 버튼)에서 활성 쌍 + preset 목록 정의(프로젝트 파일에 저장). 각 preset 개별 활성/비활성 + 이름.
- **Cycle Layer Pair Presets (`Shift`+`V`)**로 활성 preset 순환. 현재 쌍이 preset 아니면 "Manual"로 목록 포함.

### Placing free vias · #placing-free-vias

- 독립(standalone) 비아: 배치 시 접촉 항목에 연결. via stitching/shielding/thermal 등에 유용.
- 배치: add via 버튼 또는 `Ctrl`+`Shift`+`X` → 위치 클릭. 트랙 위면 트랙처럼 연결(네트 취득·joint 생성·드래그 시 트랙 동반).
- 네트 결정: 트랙/패드 위면 그 네트(+ Automatically update via nets 켜짐). 아니면 비아 아래 zone 네트(여러 zone이면 선택 프롬프트). zone 없으면 네트 없음.

### Modifying tracks · #modifying-tracks

- 라우팅 후 이동/드래그/삭제·재배선. 단일 세그먼트 선택 후 `U`: 1회=패드/비아 junction 사이 세그먼트, 2회=모든 레이어 연결 세그먼트 전체(네트 전체 빠른 삭제에 유용).
- 드래그 2종:
  - **Drag (45도, `D`)**: 라우터로 드래그. Shove 모드면 shove, Walk Around면 우회/정지. 다중 트랙 동시 가능.
  - **Drag Free Angle (`G`)**: 세그먼트를 둘로 쪼개 새 코너를 임의 위치로(Highlight Collisions처럼 하이라이트만).
- ⚠️ 호 포함 트랙 드래그는 아직 불가(시도 시 호 제거될 수 있음). 호 리사이즈는 호 선택 후 `D`(DRC 미검사).
- **Move (`M`)**: 비선택 부착 트랙·비아 무시하고 픽업. DRC 미검사.
- 풋프린트 + 부착 트랙 이동: 풋프린트 선택 후 `D`. 패드 origin에서 끝나는 트랙만 동반. Highlight Collisions만 동작(우회·shove 없음). DRC 위반은 하이라이트되고 커밋 막힘 → `Ctrl`+클릭으로 무시 커밋.
- 삭제: `Del`. `Backspace`=세그먼트 삭제 + 다음 세그먼트 선택(연속 삭제, 배선 중 동작과 동일).
- **Break Track**(우클릭): 커서 위치에서 트랙을 둘로 분할. 재결합은 드래그 또는 Cleanup의 merge co-linear tracks.

### Editing track and via properties · #track-and-via-properties

- 재배선 없이 트랙 폭·비아 크기를 속성 다이얼로그에서 수정(선택 전체에 적용). 선택 타입에 맞는 속성만 표시.
- ⚠️ Properties Manager로도 수정 가능.

#### Track and via nets · #track_and_via_nets
- Common 섹션: **Net** 드롭다운으로 네트 변경. **Automatically update via nets** 체크 시 비아 네트 수동 변경 불가(접촉 zone/패드 네트로 할당). Lock 가능.

#### Track size, position, and layers · #track_size_position_and_layers
- Tracks 섹션: 시작/끝 위치, 레이어, 트랙 폭(사전정의 또는 임의).
- **Solder mask** 체크: 외층 트랙 위 솔더마스크 제거(트랙 형상대로 개구). **Expansion**은 양측에 더해짐(1mm 트랙 + 1mm expansion → 3mm 개구).

#### Via size, position, and layers · #via_size_position_and_layers
- Vias 섹션: 위치, 타입(through/micro/blind/buried), span 레이어. through는 항상 앞·뒤 외층, micro/blind/buried는 임의 레이어.
- annulus·hole 직경 수정(사전정의/임의). 레이어별 정의 가능 = **padstack**. **Padstack mode**:
  - **Normal**: 전 레이어 동일.
  - **Front/Inner/Back**: 앞/뒤/내층(내층 동일) 분리. **Edit layer** 드롭다운으로 표시·편집.
  - **Custom**: 각 레이어 완전 독립.
- **Annular rings**(annular ring 보유 레이어):
  - **All copper layers**: 전 레이어.
  - **Start, end, and connected layers**: 시작·끝 + 트랙/zone 연결 레이어.
  - **Connected layers only**: 연결 레이어만.
  - **Start and end layers only**: 시작·끝만(= *skip vias*, zone은 시작·끝만 연결).
- 미연결 레이어 annular ring 제거 → 내층 라우팅 공간 확보, 인접 트레이스와 기생 커패시턴스↓.
- 💡 고밀도 고속 설계는 Start/end/connected 또는 Connected only로 내층 채널 확보. ⚠️ 일부 팹은 미연결 레이어에도 최소 annular ring 요구.
- 일괄: Edit Track and Via Properties 또는 Unused Pads 도구.

#### Via protection (IPC-4761) · #via-treatment-properties
- **Protection features** 드롭다운(IPC-4761): Tenting(솔더마스크 덮음), Covering(추가 보호층 epoxy/resin), Plugging(비전도 충전, 솔더 wicking 방지, via-in-pad 중요), Filling(전도성 충전, 최대 열·전기 전도), Capping(전도성 캡, 평탄 솔더 표면).

| Type | Description |
| --- | --- |
| **From rules** | Board Setup 기본값 상속. |
| **None** | 보호 없음. |
| **Type I** | Tented(솔더마스크만), 한쪽/양쪽. |
| **Type II** | Covered + tented, 한쪽/양쪽. |
| **Type III** | Plugged, 한쪽/양쪽. |
| **Type IV** | Plugged + tented, 한쪽/양쪽. |
| **Type V** | Filled(전도성). |
| **Type VI** | Filled + tented, 한쪽/양쪽. |
| **Type VII** | Filled + capped. |

- 💡 Via-in-pad는 보통 Type IV(plugged+tented) 또는 Type VII(filled+capped) 이상. 팹과 사전 협의(비용·리드타임 영향).

#### Via backdrilling and post-machining · #via_backdrilling_and_post_machining_counterbores_and_countersinks
- 비아는 이 다이얼로그, 스루홀 패드는 Pad Properties에서 백드릴·후가공(카운터보어/싱크) 설정.

##### Back-drilling · #via-back-drilling
- 제조 후 공정으로 비아 stub(미사용 배럴) 제거 → 고주파 신호 반사·공진 방지(SI 개선). 한쪽/양쪽에서 지정 레이어까지 재드릴.

| Mode | Description |
| --- | --- |
| **No back-drill** | 백드릴 안 함(기본). |
| **Back-drill from bottom** | 뒷면(bottom)에서 stub 드릴. |
| **Back-drill from top** | 앞면(top)에서 stub 드릴. |
| **Back-drill from both** | 양쪽(내층 연결 + 양방향 stub 시). |

- **Back-drill must-cut**: 백드릴이 통과하는 마지막 구리 레이어(마지막 연결 신호층 바로 너머로 설정).
- **Back-drill size**: 백드릴 홀 직경(원 홀보다 커야 배럴 도금 완전 제거).
- 💡 고속 디지털(멀티 기가비트)에서 stub > 수 mm 시 사용. 팹의 백드릴 깊이 공차 확인.
- 캔버스 표시: 백드릴 직경 링(절반은 outer layer 색, 절반은 must-cut layer 색).

##### Post-machining (counterbore/countersink) · #via-post-machining
- 드릴 홀 앞/뒤에 카운터싱크/보어 추가 → 패스너 헤드 클리어런스. 카운터싱크=원뿔(각진 측면), 카운터보어=직선 측면·평바닥. 앞/뒤 독립 설정.

| Mode | Description |
| --- | --- |
| **Not post-machined** | 후가공 없음(기본). |
| **Counterbore** | 평바닥 원통 리세스(볼트 헤드 리세스·평탄 시팅). |
| **Countersink** | 원뿔 리세스(평두 나사 flush). |

- 파라미터: **Size**(직경/표면 외경), **Depth**(counterbore만, 표면 기준 깊이), **Angle**(countersink만, 원뿔 포함각 — 흔히 82/90/100°).
- ⚠️ 모든 팹이 후가공 지원하는 것은 아님.
- 캔버스 표시: 추가 dashed 링(각 구리 레이어 교차, 레이어 색).

#### Via teardrops · #via_teardrops
- 비아 teardrop은 이 다이얼로그에서 설정(Teardrops 섹션 참조).

### Bulk editing tracks and vias · #bulk-editing-tracks-and-vias
- **Edit → Edit Track & Via Properties…**.
- **Scope**: 트랙/비아/둘 다 제한. 비아는 타입별 추가 필터. scope 미선택 시 아무것도 편집 안 됨.
- **Filter Items**(모든 활성·해당 필터 만족 객체만; via diameter는 트랙에 미적용; 와일드카드 `*`/`?`):
  - by net / by net class / by layer / tracks by width / vias by diameter / **Selected items only**.
- **Action**:
  - **Set to net class / custom rule values**: 네트클래스·커스텀 규칙 값으로 조정.
  - **Set to specified values**: 속성별 `-- leave unchanged --` 또는 새 값 — Layer / Track width(Pre-defined Sizes) / Via size / Via annular rings / Via protection features.

### Removing unused pads · #removing-unused-pads
- **Tools → Remove Unused Pads…**: 사용 레이어 annular ring 유지, 미사용 제거(트랙/zone 연결 없는 레이어 = 미사용).
- **Remove Unused Layers** / **Restore All Layers**(필터 만족 객체 대상).
- 필터: **Vias** / **Pads**(annular ring 수정 대상) / **Selected only**(Vias·Pads와 조합) / **Keep outside layers**(미사용이어도 시작·끝 레이어 유지).

### Cleaning up tracks and vias · #cleaning-up-tracks-and-vias
- **Tools → Cleanup Tracks & Vias…**. 선택 액션 수행:
  - **Refill zones before and after cleanup** / **Delete tracks connecting different nets**(네트 쇼트 제거) / **Delete redundant vias**(중복·스루홀 위) / **Delete vias connected on only one layer** / **Merge co-linear tracks** / **Delete tracks unconnected at one end**(댕글링) / **Delete tracks fully inside pads**.
- 필터: by net / netclass / layer / Selected items only.
- **Build Changes**로 변경 미리보기 → **Update PCB**로 적용(누르기 전엔 미적용).

### Routing Convenience Functions · #routing_convenience_functions
- **Route Selected (`Shift`+`X`)**: 선택 패드(또는 풋프린트의 미배선 패드)에서 순서대로 배선. 이미 트랙 있는 패드는 스킵. **Cancel Current Item**=현재 스킵, `Esc`=나머지 스킵(완료분 유지).
- **Route Selected From Other End (`Shift`+`E`)**: 선택 패드를 끝점으로, ratsnest 반대편을 시작점으로 배선.
- 개별 배선 중 `Ctrl`+`E`: 현재 세그먼트 커밋 후 ratsnest 반대편에서 배선 시작.
- **Unroute Selected**(우클릭): 선택 객체(풋프린트/패드/트랙)에 연결된 트랙 제거(다른 패드 만날 때까지).

### Automatically completing tracks · #automatically_completing_tracks
- 스키매틱 연결 기반 단일 트랙 자동 배선(현재 레이어만, 비아·레이어 변경 없음).
- 배선 중 `F`: 마지막 fix 끝→가장 가까운 ratsnest anchor 자동 완성(실패 시 수동). **Attempt Finish**(컨텍스트 메뉴).
- 라우터 비활성 시: 객체 선택 후 우클릭 **Attempt Finish Selected (Autoroute) (`Shift`+`F`)**. 선택 순서대로 라우팅, 실패 시 라우터 활성 일시정지(수동 완성). **Cancel Current Item**=현재 스킵, `Esc`=나머지 스킵.

## Routing differential pairs · #routing-differential-pairs

- 차동쌍 = 공통 **base name** + 양/음 suffix. suffix는 `+`/`-` 또는 `P`/`N`. 예: `USB+`/`USB-`(base `USB`), `USB_P`/`USB_N`(base `USB_`). ⚠️ suffix 스타일 혼용 불가(`USB+`/`USB_N`은 차동쌍 아님). 스키매틱에서 네트명 올바르게 지정 필요.
- 배선: Route Differential Pairs 아이콘 또는 `6`. 패드·비아·기존 차동쌍 트랙 끝 클릭(양/음 어디서나 시작).
- 갭은 design rules에서(Net Classes 또는 커스텀 규칙). 시작/끝 간격이 다르면 짧은 "fan out" 생성(비결합 구간 최소화).
- 레이어 전환·Place Via(`V`) 시 두 비아를 나란히 생성(copper·hole-to-hole 클리어런스 준수하며 최대한 가깝게).

## Length tuning · #length-tuning

- 라우팅 후 사행(serpentine) 튜닝 형상 추가. 지속 객체로 사후 수정 가능. 길이 + 시간영역(지연) 튜닝 모두 동일 도구.
  - 단일 트랙 길이: 아이콘 또는 `7`.
  - 차동쌍 길이: 아이콘 또는 `8`.
  - 차동쌍 스큐(위상): 아이콘 또는 `9`(짧은 쪽에 길이 추가해 스큐 제거).
- 절차:
  1. (선택) 커스텀 DRC 규칙으로 target length/skew 설정. 미설정 시 패턴 생성 후 수동 입력.
  2. 적절한 튜닝 도구 활성화.
  3. 트랙 호버 → 현재/목표 길이·스큐 상태창.
  4. 트랙 클릭으로 튜닝 시작.
  5. 커서를 트랙 따라 이동 → meander 추가(라이브 측정 팝업).
  6. 튜닝 중 spacing `1`/`2`(증/감), amplitude `3`/`4`(증/감).
  7. target length 설정 시 도달하면 meander 중단.
  8. 캔버스 클릭으로 커밋(사후 수정 가능, 동일 트랙에 다중 패턴 가능).
- ⚠️ 길이 튜너는 두 패드 간 **point-to-point** 네트만 지원. 다른 토폴로지 미지원.
- ⚠️ 차동쌍 길이 튜닝은 결합(coupled) 구간만. 비결합 구간은 single-track 튜너 사용.

### Editing tuning patterns · #editing-tuning-patterns
- 선택 시 메시지 패널에 target/routed length 표시, 편집 핸들 등장:
  - 끝 핸들 드래그: 트랙 따라 확장/축소.
  - 코너 핸들 트랙쪽/반대: 최대 meander amplitude 감소/증가.
  - 마지막 핸들: meander spacing 조정.
- 선택 박스 = 최대 허용 범위. 줄이면 패턴 축소(목표보다 짧아져도), 늘리면 목표 도달까지 확장.
- 이동: 선택 후 드래그 또는 Move(`M`). 삭제(`Del`): 패턴 제거 + 원 트랙 복원. **Ungroup**: 구성 트랙으로 분해(재그룹 불가).
- 속성 다이얼로그(또는 Properties Manager): 인터랙티브에 없는 파라미터 — 최소/최대 amplitude, spacing, corner style(**filleted**/**chamfered**)와 **radius**(% of max), **single-sided**(baseline 한쪽만).
- 💡 기본값: **Board Setup → Design Rules → Length-tuning Patterns**(패턴 종류별).

### Setting target length and skew · #setting-target-length-and-skew
- 2가지 방법: ① 튜닝 패턴 속성 다이얼로그(**Target Length**/**Target Delay**, 스큐는 **Target Skew**/**Target Delay Skew**) — 패턴별 개별 설정, 생성 후만 접근. ② 커스텀 DRC 규칙(`length`/`skew` constraint).
- 커스텀 규칙은 패턴 속성 target을 override(패턴 속성의 **override custom rules** 체크 시 예외). 사전 설정·netclass/네트명별 차등·범위 위반 시 DRC 가능.
- 커스텀 규칙 변경 후 기존 패턴 미자동 갱신 → **Edit → Update All Tuning Patterns**로 재계산.
- 예시:

```
(rule "target length and skew"
      (condition "A.hasNetclass('high_speed')")
      (constraint length (min 95mm) (opt 100mm) (max 105mm))
      (constraint skew (max 0.1mm)))
```

### Length tuning pitfalls and tips · #length_tuning_pitfalls_and_tips
- point-to-point만 튜닝, 분기(branch) 시 분기점에서 멈춤. stub 트랙이 분기를 만들면 튜닝 방해 → outline 모드(pad/via/track sketch 버튼)로 stub 찾기 또는 Cleanup Tracks and Vias로 자동 제거.
- 기본적으로 비아 길이를 포함(layer-to-layer 길이만; 정확도는 stackup 설정 의존). **Board Setup → Constraints → include stackup height in track length calculations** 해제 시 비아 무시.
- 길이 튜너는 분기·미사용 비아 구간 제외 + 패드 내 최단경로 최적화 → Net Inspector(단순 구리 세그먼트 합산)와 계산 방식 다름. 둘 다 정확하나 목적이 다름.

### Time-domain tuning (propagation delay) · #time-domain-tuning
- 물리 길이 대신 **전파 지연(propagation delay)**을 매칭. 동일 레이어·지오메트리면 길이 매칭으로 충분하나, 다층(microstrip vs stripline)은 유효 유전율이 달라 속도가 달라짐 → 길이만으로 동시 도착 보장 안 됨.
- 길이 튜너가 트랙·비아·pad-to-die 지연을 레이어별 전파 파라미터(튜닝 프로파일)로 계산, 목표 delay까지 meander 조정.

#### When to use each mode · #when_to_use_each_mode
- **Length-domain**: 같은 레이어, 단순 stackup(2층 등), 길이 매칭 요구.
- **Time-domain**: 다층 라우팅(비아 전환), stackup상 레이어 간 속도차 큼(microstrip+stripline), delay/flight time 매칭 요구(DDR/PCIe/USB 등).
- 💡 한 레이어처럼 보여도 비아 전환·pad-to-die 지연 고려를 위해 고속 버스는 time-domain 권장.

#### How time-domain tuning works · #how_time_domain_tuning_works
- 전파 지연 = 3성분 합:
  - **Track delay**: 세그먼트 물리 길이 × 레이어별 **unit delay**.
  - **Via delay**: 비아 통과 거리(stackup) × via unit delay. 프로파일에 **global via unit delay** + layer-pair별 override.
  - **Pad-to-die delay**: 패드 padstack의 pad-to-die length/delay 포함.
- 호버 시 상태창에 총 지연(ps) + 목표 표시.

#### Board stackup and delay calculations · #board_stackup_and_delay_calculations
- 정확한 stackup 필수. **Board Setup → Physical Stackup**: 구리 레이어 수, 유전체 재질·두께, prepreg·core 두께 정확히(임피던스·전파지연 직결).
- 프로파일 내장 계산기가 stackup으로 레이어별 unit delay 자동 산출. ⚠️ stackup 변경 후 프로파일 delay 재계산 필요.

#### Propagation delay calculation details · #propagation_delay_calculation_details
- 비아 경로는 실제 사용 레이어 구간만 계산(F.Cu↔In1.Cu면 그 사이만, 전체 via 높이 아님).
- 동일 레이어 연속 세그먼트는 단일 line chain으로 병합(경계 아티팩트 방지).
- 패드 진입은 패드 형상 내 최단거리로 clip(패드 중심까지 전체 길이 아님).

#### Per-layer delay tracking · #per_layer_delay_tracking
- time-domain 활성 시 레이어별 지연 기여 추적. **View → Panels → Net Inspector**에서 **Show Time Domain Details** 켜면 컬럼이 길이→지연으로 전환 → 어느 레이어 전환이 스큐 기여 큰지 파악.

#### Setting target delay · #setting_target_delay
- 2가지: ① 패턴 속성에서 **Delay** 라디오 + **Target Delay**(ps). ② 커스텀 DRC 규칙 `length`/`skew` + 시간 단위(`ps` 등).
- 시간 단위 사용 시 자동으로 time-domain 모드 전환. 예:

```
(rule "DDR data delay matching"
      (condition "A.hasNetclass('DDR_DATA')")
      (constraint length (min 450ps) (opt 500ps) (max 550ps)))
```

```
(rule "DDR differential skew"
      (condition "A.hasNetclass('DDR_CLK')")
      (constraint skew (max 5ps)))
```

- ⚠️ 단일 constraint의 min/opt/max에서 시간·길이 단위 혼용 불가.

#### Practical example: DDR4 memory bus · #practical_example_ddr4_memory_bus
- 시나리오: 데이터 `F.Cu`(microstrip)·`In1.Cu`(stripline), F.Cu→In1.Cu 비아, 목표 500 ps ±50 ps.
  1. **Board Setup → Physical Stackup** 정확히 구성(예: 6층, In1.Cu·In4.Cu에 GND).
  2. **Board Setup → Design Rules → Tuning Profiles**에서 `DDR4_Data` 생성, **Single** 선택, **Enable time domain tuning** 체크.
  3. **Track Propagation** 표에 `F.Cu`·`In2.Cu` 행 추가, reference layer 선택 후 refresh로 unit delay 자동 계산.
  4. **Via Propagation**에서 global via unit delay 또는 `F.Cu`→`In2.Cu` override.
  5. **Net Classes**에서 DDR 데이터 넷클래스에 `DDR4_Data` 프로파일 할당.
  6. 커스텀 DRC 규칙으로 target delay 설정.
  7. 길이 튜닝 도구로 튜닝(ps 표시, 목표까지 meander).

#### DRC integration · #drc_integration
- DRC가 길이·시간영역 튜닝 constraint 모두 검증. 시간 단위 `length`/`skew`면 계산된 전파 지연을 검사.
- 튜닝 프로파일은 암묵적 DRC 규칙 생성(레이어별 width·diff pair gap 검증). 심각도는 **Board Setup → Violation Severity → Tuning profile track geometries**(기본 **Ignore**; Warning/Error로 활성화).
- 넷클래스가 없는 프로파일 참조 시 **Missing tuning profile** 위반.

## Teardrops · #editing-teardrops

- **Teardrop**: 트랙과 패드/비아/다른 폭 트랙 간 전이를 매끄럽게 하는 추가 구리. 기계적 강건성↑, 드릴 오정렬로 인한 단선 위험↓.
- 추가 방법 2가지: Edit Teardrops 다이얼로그(일괄), 또는 개별 패드/비아 속성.

### Adding teardrops in bulk · #adding_teardrops_in_bulk
- **Edit → Edit Teardrops…**. 필터 + 형상 설정 + 기존 teardrop 편집·제거.
- **Scope**: PTH pads / SMD pads / vias / track-to-track.
- **Filter Items**: net / net class / layer, round pads만 / 기존 teardrop만 / selection만.
- **Action**:
  - **Remove Teardrops**(scope·필터 매칭) / **Remove All Teardrops**(전체).
  - **Add teardrops with default values for shape**: Board Setup의 기본 teardrop 설정 적용(round/rectangular/track 간 별도 구성, **Edit default values in Board Setup** 링크).
  - **Add teardrops with specified values**(커스텀):
    - **Prefer zone connection**: zone에도 연결 시 teardrop 미생성.
    - **Allow teardrops to span 2 track segments**: 첫 세그먼트가 짧으면 두 번째까지 확장.
    - **Maximum track width**: 패드 폭(최소 치수)의 %를 초과하는 트랙은 미생성.
    - **Best length / Maximum length**: 이상 길이(부착 객체 최소 치수의 %) / 최대 길이(절대값).
    - **Best width / Maximum width**: 이상 폭(%) / 최대 폭(절대값).
    - **Curved edges**: 곡선 엣지.
  - 기존 teardrop 있는 객체에 추가 시 갱신. `-- leave unchanged --`(텍스트박스) 또는 체크박스 3-state로 기존값 보존.

### Adding teardrops to individual objects · #adding_teardrops_to_individual_objects
- 개별 비아는 via 속성, 개별 패드는 패드 속성 **Connections** 탭. 설정은 Edit Teardrops와 동일. Properties Manager로도 편집.

### Other details about teardrops · #other_details_about_teardrops
- Teardrop은 작은 zone — refill 시 다른 네트 구리와 단락 회피. 추가 시 채워지나 Unfill/Refill All Zones·DRC·출력 시 다른 zone과 함께 unfill/refill. 좌측 툴바 zone 표시 컨트롤로 filled/outline 표시.
- 모든 패드(커스텀 포함)에 추가 가능. 일부 커스텀 패드 형상은 바람직하지 않은 teardrop을 만들 수 있어 해당 패드는 teardrop 비활성화가 나을 수 있음.

## Backdrills and hole post-machining · #backdrills_and_hole_post_machining_counterborescountersinks

- 비아·스루홀 패드에 적용하는 제조 후 공정.
- **Backdrilling**: 도금 홀 배럴의 미사용 stub 제거(고주파 반사·공진 → SI 저하 방지). 한쪽/양쪽에서 지정 레이어까지 재드릴. 확대 직경은 홀 벽 도금을 완전 제거할 만큼 커야 함.
- **Post-machining**: 기존 패드/비아 홀 앞/뒤에 countersink/counterbore 추가(패스너 헤드 클리어런스). 카운터싱크=원뿔, 카운터보어=직선 측면·평바닥.

### Backdrills · #backdrills
- 비아는 Via Properties(#via-back-drilling 참조), 패드는 Pad Properties의 **Backdrill** 탭.

| Mode | Description |
| --- | --- |
| **No back-drill** | 안 함(기본). |
| **Back-drill from bottom** | 뒷면에서 드릴. |
| **Back-drill from top** | 앞면에서 드릴. |
| **Back-drill from both** | 양쪽(내층 연결 + 양방향 stub). |

- **Back-drill must-cut**: 백드릴 통과 마지막 구리 레이어(마지막 연결 신호층 바로 너머).
- **Back-drill size**: 백드릴 홀 직경(원 홀보다 커야).
- 캔버스 표시: 백드릴 직경 링(절반 outer layer 색, 절반 must-cut 색). 패드는 must-cut 다음 패드 레이어를 링 아래 표시.

### Post-machining holes · #post-machining
- 비아는 Via Properties(#via-post-machining 참조), 패드는 Pad Properties **Backdrill** 탭. 앞/뒤 독립 설정.

| Mode | Description |
| --- | --- |
| **Not post-machined** | 없음(기본). |
| **Counterbore** | 평바닥 원통 리세스(볼트 헤드·평탄 시팅). |
| **Countersink** | 원뿔 리세스(평두 나사 flush). |

- 파라미터: **Size**(직경/표면 외경), **Depth**(counterbore만), **Angle**(countersink만, 흔히 82/90/100°).
- 캔버스 표시: 추가 dashed 링(각 구리 레이어 교차, 레이어 색).

## Graphics and text · #pcb-graphical-objects

- 그래픽 객체(lines/arcs/rectangles/circles/polygons/text/tables/dimensions/barcodes/points)는 임의 레이어에 존재. 주로 미관·문서화용이나, 구리 레이어의 형상은 전기 연결 + 네트 할당 가능.

### Graphical shapes · #graphical-shapes
- 구리 레이어의 그래픽은 네트 할당·연결 가능(트랙·zone과 유사). 차이:
  - 형상은 자체 속성으로 정의(주변 객체 무영향). zone은 outline 내 채우며 다른 네트 구리 회피.
  - 라인·호는 단순 형상으로 편집(라우터 미사용) → 충돌 인터랙티브 미감지(DRC에선 감지).
- 생성 버튼/단축키:
  - Lines (`Ctrl`+`Shift`+`L`), Arcs (`Ctrl`+`Shift`+`A`), Bezier (`Ctrl`+`Shift`+`B`), Rectangles/rounded rectangles, Circles (`Ctrl`+`Shift`+`C`), Polygons (`Ctrl`+`Shift`+`P`).
- 배치: 도구 선택 → 클릭으로 점 배치. 사각형·원은 2점으로 완성. 호=3점, 라인·폴리곤·베지어=임의 점 + 더블클릭 완료.
- 수정: 선택 후 핸들 드래그(코너/엣지). 보통 인접 코너 각도 유지·엣지 길이 가변, `Ctrl`=길이 유지·각도 가변.
- 코너 정밀: 우클릭 **Shape Modification → Move Corner To…**. 폴리곤은 **Edit Corners…**(좌표 표). `U`로 연속 그래픽 라인 선택 확장.

#### Arc editing modes · #arc-editing-modes
- **Preferences → PCB Editor → Editing Options** 또는 arc 버튼 우클릭, `Ctrl`+`Space`로 순환:
  - **Keep arc center, adjust radius**: 중심 유지, 반경 변경.
  - **Keep arc endpoints or direction of starting point**: 끝점·곡률 방향 유지(midpoint/center 드래그).
  - **Keep arc radius and center, adjust angle**: 반경·중심 유지, 각도 변경.

#### Editing shape properties · #editing_shape_properties
- 속성 다이얼로그 또는 Properties Manager:
  - 상단: 위치·형상(객체별 편집 방식 탭 — 라인은 start/end, start+length+angle, start+mid 등).
  - **Locked**: 잠금(selection filter Locked Items로만 선택).
  - **Rounded rectangle** + **Corner radius**(비파괴, 사후 조정 가능).
  - **Line width**: 외곽 폭(채움 객체에도). 이상 형상 양측으로 확장(2mm 반경·0.2mm 폭 원 → 외경 2.1/내경 1.9mm; 폭 0 + 채움 = 2mm 솔리드 원). **Line style**: solid/dashed/dotted/dash-dot/dash-dot-dot.
  - 💡 신규 그래픽 기본 스타일: **Board Setup → Text & Graphics Defaults**.
  - **Filled shape**: 닫힌 형상(rect/circle/polygon) 채움 여부.
  - **Layer**: 레이어. 구리 레이어 형상은 네트 할당 가능(트랙/zone처럼 연결, 단 형상 유지·클리어런스 미유지).
  - **Solder mask**(외층 구리): 동측 솔더마스크에도 그려져 개구 생성. **Expansion**은 양측에 더해짐(1mm 세그먼트 + 1mm → 3mm 개구).

#### Shape modification tools · #shape-modification-tools
- 형상/코너 선택 → 우클릭 **Shape Modification** 서브메뉴(선택 조합별로 다른 도구):
  - **Heal Shapes**(두 선/호 불연속 보정), **Simplify Polygons**(불필요 코너 제거), **Fillet Lines**(코너 호 라운딩), **Chamfer Lines**(모따기), **Dogbone Corners**(원형 릴리프, 라운딩보다 큰 — 원 코너 감싸 둘러쌈; 내부 코너의 라운드 공구 가공용, 보드 외곽 기준 보드 내부를 향하는 코너만; **Add slots to acute corners** 옵션), **Extend Lines to Meet**(두 선 연장해 교차), **Move Corner To** / **Move Midpoint To**(좌표 이동), **Create Corner** / **Remove Corner** / **Chamfer Corner**, **Edit Corners**(좌표 다이얼로그), **Merge Polygons**(합집합), **Subtract Polygons**(차집합; 먼저 선택한 것을 마지막 선택에서 뺌), **Intersect Polygons**(교집합).

#### Converting objects to and from graphic shapes · #create-from-selection
- 선택 → 우클릭 **Create From Selection** 서브메뉴. 폴리곤/룰 영역/zone 변환 시 outline 생성 방식:
  - **copy line width of first object**(폴리곤 변환만, 닫힌 형상; 미채움 폴리곤, 첫 객체 선폭).
  - **use centerlines**(선폭 0, 닫힌 형상; 폴리곤이면 채움).
  - **create bounding hull**(지정 **line width**, **gap** 오프셋; 닫힌 형상 불필요).
- 대부분 **delete source objects after conversion** 옵션. 미선택 시 원본 유지(변환 후 선택 상태 → `Delete`로 수동 삭제).
- 변환 종류:
  - **Create Polygon From Selection**(그래픽/텍스트/zone/룰영역/트랙 → 폴리곤; 텍스트를 형상으로).
  - **Create Zone From Selection** / **Create Rule Area From Selection**(복잡 형상 zone/룰 영역).
  - **Create Lines From Selection**(폴리곤/사각형 → 라인).
  - **Create Outsets From Selection**(원본 둘러싸는 사각형: **Outset** 거리(±), **Round corners**, **Round outwards to grid multiples**, **Copy item layers**, **Copy item thickness**).
  - **Create Tracks From Selection**(그래픽/zone/룰영역 → 트랙; 비구리면 타겟 구리 레이어 선택; 원본 유지).
  - **Create Arc From Selection**(라인/트랙 세그먼트 → 호; 원본 유지).

#### Importing vector graphics · #importing_vector_graphics
- DXF·SVG 가져오기. **File → Import → Graphics… (`Ctrl`+`Shift`+`F`)**. 💡 캔버스에 드래그앤드롭도 가능.
- 가져온 그래픽은 일반 그래픽처럼 레이어 할당·제조 출력 포함·구리 레이어 연결 가능.
- 옵션: **File**, **Import Scale**, **DXF default line width**, **DXF default units**(DXF만), **Place At**(지정 위치 vs 인터랙티브), **Layer**(지정 vs 활성), **Group imported items**, **Fix discontinuities**(**tolerance** 미만 불연속 보정).

### Text objects · #text-objects
- 텍스트: text 버튼 또는 `Ctrl`+`Shift`+`T` → 속성 다이얼로그 → 캔버스 클릭. 텍스트박스: 테두리 + 자동 reflow, 두 코너 클릭.
  - **Locked**: 잠금.
  - **Layer**: 임의 레이어. ⚠️ 구리 레이어 텍스트는 네트 미할당·연결 불가. zone은 텍스트 바운딩 박스 주위로 채움.
  - 포맷: bold/italic, 좌·우·중앙 정렬, 상·하·중앙 정렬, reversed.
  - **knockout**(텍스트 객체만, 텍스트박스 불가): 둘러싼 솔리드 사각형 + 텍스트를 음각 컷아웃.
  - **Font**: 시스템 TTF 또는 KiCad stroke font. ⚠️ 사용자 폰트는 기본 미임베드 → 타 PC에서 대체될 수 있음. **Board Setup → Embedded Files**로 임베드, 또는 KiCad 폰트 사용, 또는 텍스트를 폴리곤으로 변환(우클릭 **Create from Selection → Create Polygon from Selection…**; 편집 불가하나 동일 렌더).
  - **Text width / Text height / Thickness**(KiCad 폰트). 자동 두께 버튼: normal=size/8, bold=size/5.
  - **Position X/Y**(텍스트박스 불가), **Orientation**(90° 증분 또는 임의 각).
- 텍스트박스: **border** 체크 + **border width** + **border style**(solid/dashed/dotted/dash-dot/dash-dot-dot). **margins**는 Properties Manager에서만(다이얼로그 불가).
- 💡 신규 텍스트 기본 스타일: **Board Setup → Text & Graphics Defaults**.
- 마크업:

| Feature | Markup Syntax | Result |
| --- | --- | --- |
| Superscript | `text^{superscript}` | 위첨자 |
| Subscript | `text_{subscript}` | 아래첨자 |
| Overbar | `~{text}` | 윗줄 |
| Project text variables | `${variable}` | 변수값 |
| Built-in text variables | `${refdes:field}` | refdes 심볼의 field 값 |

- ⚠️ 프로젝트 text variable은 Board Setup에서 사전 정의 필요(built-in 변수도 존재).

### Tables · #tables
- 표: 커스텀 테두리·셀 크기·헤더, 임의 레이어. table 버튼 → 좌상단 클릭 → 우하단 클릭(클 수록 기본 행/열↑, 사후 추가·삭제 가능).
- 전체 편집 또는 셀 개별 편집. 신규 생성 시 Table Properties 자동 오픈. 우클릭 **Export Table to CSV…**.

#### Editing a whole table · #table-properties
- 열기: 신규 생성, 셀 선택 + 우클릭 **Edit Table (`Ctrl`+`E`)**, 전체 선택 + **Properties… (`E`)**(드래그 또는 셀 선택 후 **Select Table**), Cell Properties의 **Edit Table…** 버튼.
- 좌측: 편집 가능 그리드(셀 클릭 편집, 스프레드시트 붙여넣기). 우측: **Layer**, **Locked**, **External border**·**Header border**(Width·Style 솔리드/dashed/dotted/dash-dot/dash-dot-dot), **Row Lines**·**Column lines**.
- ⚠️ 셀 텍스트는 마크업 지원(위/아래첨자 등). Properties Manager로도 편집.

#### Editing individual table cells · #table-cell-properties
- 더블클릭 또는 셀 선택 + 우클릭 **Properties… (`E`)**. 다중 셀 동시 적용.
- 행/열 전체 선택: 셀 선택 + 우클릭 **Select Row(s)/Column(s)**.
- 좌측: 셀 내용. 우측: **Font**, bold/italic·좌·우·중앙·상·하·중앙 정렬, **Text width/height/Thickness**(자동: normal=/8, bold=/5), **Cell margins**(상하좌우). **Edit Table…** 버튼.

#### Editing table layout · #table-layout
- 행/열 크기: 셀 선택 후 우측(열 폭)/하단(행 높이) 핸들 드래그.
- 추가: 셀 선택 + 우클릭 **Add Row Above/Below**, **Add Column Before/After**.
- 삭제: **Delete Row(s)/Column(s)**(다중은 선택 범위).
- 병합/해제: **Merge Cells** / **Unmerge Cells**.

### Dimensions · #dimensions
- 치수: 측정·마킹 표시. 임의 드로잉 레이어(보통 User 레이어). 5종:
  - **Aligned**: 두 점 거리, 측정축은 두 점 연결선과 평행.
  - **Orthogonal**: X 또는 Y 축 거리(수평/수직 성분). 배치 위치로 축 선택.
  - **Center**: 점/원·호 중심 십자.
  - **Radial**: 중심점↔원·호 외곽 거리(중심 십자).
  - **Leader**: 화살표 + 리더선 + 텍스트(선택적 원/사각 프레임). 팹 노트 참조용.
- 생성 후 `E`로 숫자 포맷·텍스트·라인 스타일 편집. 💡 기본 스타일: **Board Setup → Text & Graphics Defaults**.

#### Dimension format options · #dimension_format_options
- **Override value**(직접 값 입력), **Prefix**/**Suffix**, **Layer**, **Units**(Automatic=에디터 단위 추종), **Units format**, **Precision**, **Suppress trailing zeroes**.

#### Dimension text options · #dimension_text_options
- 대부분 그래픽 텍스트와 동일. 추가: **Position mode**(수동 vs 측정선 정렬), **Keep aligned with dimension**(측정축 평행 자동).

#### Dimension line options · #dimension_line_options
- **Line thickness**, **Arrow length**(음수=방향 반전), **Arrow direction**(안쪽/바깥쪽; 그리는 중 우클릭 **Switch Dimension Arrows**), **Extension line offset**, **Extension line overshoot**.

#### Leader options · #leader_options
- **Value**(리더선 끝 텍스트), **Text frame**(circle/rectangle/none).

### Barcodes · #barcodes
- 바코드(QR 포함 5종), 임의 레이어. barcode 버튼 → 클릭 → Barcode Properties(우측 미리보기).
- **Text**(인코딩 데이터; **Show text** 시 아래 표기), **Locked**, **Knockout**(음각 + **Min margin X/Y**), **Layer**, **Position X/Y**, **Size X/Y**, **Orientation**(°), **Text size**.
- **Code**: Code 39(ISO 16388), Code 128(ISO 15417), Data Matrix(ECC 200), QR Code(ISO 18004), Micro QR Code.
- **Error Correction**: QR·Micro QR에만 적용.

### Points · #points
- 비물리·0차원 객체. 참조·문서화·스냅용(제조 출력 미포함). 스냅 타겟(풋프린트 정렬 등).
- 특정 레이어에 속함(레이어 표시 컨트롤로 표시·선택·스냅 제어; 원 색은 레이어 색). size 속성(표시 크기).
- 추가: add point 버튼 → 클릭(현재 레이어). 레이어·크기 변경은 Properties 패널.

### Bulk editing text and graphics · #pcbnew-edit-text-and-graphics-properties
- **Edit → Edit Text & Graphic Properties…**(풋프린트 필드·치수 포함).

#### Scope and Filters · #scope_and_filters
- **Scope**: 객체 타입 제한(미선택 시 편집 안 됨).
- **Filters**(모든 활성·해당 필터 만족; parent footprint 필터는 그래픽엔 무시; 와일드카드 `*`/`?`): **By layer**, **By parent reference designator**, **By parent footprint library link**, **Selected items only**.

#### Action · #action
- **set to specified values**(임의 값) 또는 **set to layer default values**. 드롭다운·텍스트박스 `-- leave unchanged --`, 체크박스 3-state.
- 가능 속성: 모든 항목 **layer**; 그래픽 **line thickness**; 텍스트 **font**, **text width/height**, **text thickness**(KiCad 폰트), **bold**/**italic**, **keep upright**, **center on footprint**; 풋프린트 필드 **visibility**.

### Cleaning up graphics · #cleaning_up_graphics
- **Tools → Cleanup Graphics…**. 액션:
  - **Merge lines into rectangles**, **Delete redundant graphics**(중복·degenerate), **Fix discontinuities in board outlines**(tolerance 내).
- **Update PCB** 누르기 전엔 미적용.

### Sheet title block · #sheet-title-block
- **Page Settings** 도구(또는 시트 더블클릭). 각 필드 + 용지 크기·방향 편집.
- **Issue Date** 옆 왼쪽 화살표로 오늘/임의 날짜 설정. ⚠️ 타이틀블록 날짜는 자동 갱신 안 됨(이 다이얼로그에서만 변경).
- 기본 드로잉 시트 교체 가능. 파일 브라우저 **Embed File** 체크 시 시트를 보드에 임베드(타 PC에서도 동일 표시).

## Rule areas (keepouts) · #pcb-rule-areas

- 룰 영역(keepout): 특정 DRC 규칙을 정의하는 보드 영역. 기본 규칙(특정 객체가 영역 내면 DRC 에러) + 커스텀 DRC 규칙. 멀티채널 레이아웃 채널 정의에도 사용.
- 추가: add keepout area 버튼(`Ctrl`+`Shift`+`K`) → 첫 코너 클릭 → Rule Area Properties → OK 후 코너 계속 배치(임의 폴리곤; 시작 코너 클릭 또는 더블클릭으로 완료).
- 수정: 선택 후 핸들 드래그(코너/엣지; `Ctrl`=길이 유지). 정밀: 우클릭 **Shape Modification → Move Corner To… / Edit Corners…**.
- 💡 그래픽 형상 → 룰 영역 변환: 우클릭 **Create from Selection → Create Rule Area from Selection…**(원 등 어려운 형상).
- Rule Area Properties:
  - **layers**: 적용 레이어(최소 1개; 기본 활성 레이어 선택).
  - **area name**(선택): DRC 메시지·커스텀 규칙 식별자.
  - **locked**(사후 잠금/해제 가능).
  - **Keepouts 탭**: tracks/vias/pads/zone fills/footprints 차단 기본 규칙. 영역 내 해당 객체 시 DRC 에러. zone fill은 zone keepout 설정 시 자동 회피. ⚠️ 기본 규칙 0개여도 커스텀 DRC 적용 영역으로 사용 가능.
  - **Placement 탭**: 멀티채널 레이아웃 설정.
  - **outline display**: hatched outline / fully hatched / outline only, **outline hatch pitch**.

## Locking · #locking

- 잠금 → 선택·이동·수정 어렵게(의도치 않은 변경 방지). 속성 다이얼로그·우클릭·**Toggle Lock (`L`)**.
- 제약: 잠긴 객체는 selection filter **Locked items** 켜야 선택 가능. 선택해도 상단 툴바 **Override locks** 꺼져 있으면 이동 불가(잠긴 항목 포함 이동 시 잠긴 항목 deselect, 나머지만 이동).
- 잠긴 항목은 컬러 그림자 표시(color scheme 커스텀, Appearance **Objects** 탭에서 숨김). ⚠️ 기본적으로 Locked items·Override locks 모두 꺼짐.

## Groups · #groups

- 그룹 = 다수 객체를 하나처럼 이동·회전(상대 위치 유지). 이름 표시 가능.
- 그룹 가능: footprints, tracks, zones, graphic items, 다른 그룹(중첩). 혼합 가능.
- 생성: 선택 → 우클릭 **Grouping → Group Items** 또는 상단 group 버튼. 해제: **Grouping → Ungroup Items** 또는 ungroup 버튼.
- 그룹 내 객체 선택 시 그룹 전체 선택. 개별 편집: 그룹 선택 후 우클릭 **Enter Group**(또는 더블클릭). 종료: **Leave Group** / 그룹 밖 객체 선택 / `Esc`.
- 멤버 수정: 제거는 Enter Group 후 객체 선택 + 우클릭 **Grouping → Remove Items**. 추가는 ungroup 후 새 항목 선택에 더해 재그룹(미ungroup 시 중첩 그룹 생성됨).
- 속성 다이얼로그(`E` 또는 우클릭 **Properties…**): 멤버 목록, + 버튼(캔버스 클릭 추가) / trash(목록 선택 제거), 이름·잠금.
- **Library link** 필드: 디자인 블록용. `<library>:<block>` 형식(스키매틱·디자인 블록 라이브러리 연결).

## Aligning objects · #aligning_objects

- 정렬 도구: 선택 객체를 기준 객체에 맞춰 이동(한 방향만, 다른 축 위치 유지). 6종: 수평(left/center/right), 수직(top/center/bottom). 우클릭 **Align/Distribute → Align to Left** 등.
- 기준 객체: 커서가 선택 내 객체 위면 그 객체, 아니면 정렬 방향 최외곽(left 정렬=최좌측, top=최상단; vertical center=최상단, horizontal center=최좌측).

## Distributing objects · #distributing_objects

- 분배 도구: 객체를 균등 간격으로(우클릭 **Align/Distribute → Distribute Horizontally/Vertically**). 양 끝 두 객체 미이동(vertical=상·하단, horizontal=좌·우측), 나머지를 균등 분배(상대 순서 유지, 한 방향만).

## Arrays · #creating-arrays

- 배열 도구: 사각형/원형 배열(footprints, vias, 그래픽 등). 선택 → 우클릭 **Create from Selection → Array… (`Ctrl`+`T`)**. 2종: **Grid**(사각), **Circular**.

### Grid arrays · #grid_arrays
- **Horizontal count**(열 수), **Vertical count**(행 수), **Horizontal/Vertical spacing**(열/행 간격), **Horizontal offset**(행마다 수평 시프트), **Vertical offset**(열마다 수직 시프트).
- **Stagger**: 패턴 반복 전 오프셋되는 행/열 수(**Rows**/**Columns**). 예: 2행 stagger → 각 행이 수평 간격의 절반 오프셋, 다음 행은 원위치. stagger 오프셋은 기존 offset에 더해짐.
- **Grid Position**: **Source items remain in place**(원본 유지, 한 코너) 또는 **Center on source items**(원위치 중심).

### Circular arrays · #circular_arrays
- **Center pos X/Y**(중심 절대 위치; **Select Point…** 또는 **Select Item…**), **Item count**(원본 포함 개수), **Angle between items**(각 간격), **Full circle**(완전 원, 간격 자동 계산), **Clockwise/Anti-clockwise**(음수 각이면 반대), **Rotate items**(중심 따라 회전 vs 방향 유지).

### Common array options · #common_array_options
- **Item Source**: **Duplicate selection**(부족분 복제 추가) 또는 **Arrange selection**(추가 없음, 선택 항목만 배치 — 부족 시 불완전).
- Duplicate 시 **Footprint Annotation**: **Keep existing reference designators**(중복 레퍼런스) 또는 **assign unique reference designators**(고유 자동 할당).
- ⚠️ Duplicate로 풋프린트 배열 시 스키매틱에 없는 풋프린트 발생 → 보드↔스키매틱 동기화 주의.

## Using reference images · #pcb-reference-images

- 캔버스 배경 참조 이미지(레이아웃 보조용, 제조 출력 미포함).
- 추가: image 버튼 → 파일 선택 → 캔버스 클릭.
- 이동: Move(`M`) 또는 드래그. 5개 핸들 — 4코너=스케일(reference point 기준), 5번째=reference point(드래그로 이동, 초기 중심).
- 속성(`E`): **Position X/Y**, **Associated layer**(레이어 숨김 시 이미지도 숨김), **Height/Width/Scale**(비례 유지), **Convert to Greyscale**.
- ⚠️ 비물리 — 레이어 plot해도 제조 출력 미포함.
- Appearance Manager **Objects 탭**의 **Image** 가시성으로 전체 표시/숨김 + opacity 조정.

## Pin and gate swapping · #pin-and-gate-swapping

- 핀/게이트 스왑: 풋프린트 패드 간 네트 교환. PCB에서 편집 후 스키매틱으로 back-annotate.
- ⚠️ 도구는 패드에 동작(핀 아님). 핀 네트는 스키매틱 갱신(Update Schematic from PCB) 전엔 미스왑.
- **Pin swapping**: 선택 핀(패드) 간 네트 교환(예: MCU GPIO 핀 2개).
- **Gate swapping**: 한 심볼 유닛(gate)의 모든 핀 단위 교환(예: dual opamp 유닛, 저항 어레이).
- ⚠️ 스왑은 **unconstrained** — 등가성 미검사. 설계자가 유효성 보장 책임.
- PCB 스왑은 보드 즉시 반영, 스키매틱은 Update Schematic from PCB로 동기화. 스키매틱에서 스왑하면 반대(Update PCB From Schematic).

### Pin swaps · #pin_swaps
- 같은 풋프린트 패드 간 네트 교환(그 외 제약 없음). ⚠️ 새 연결 유효성은 사용자 책임.
- 연결 트랙·비아·기타 구리 네트도 스왑. 연결 zone은 원 네트 유지. 미선택이지만 연결된 패드(타 부품)는 프롬프트로 포함/무시 선택.
- 실행: 패드 선택 → 우클릭 **Swap Pad Nets**.

### Gate (unit) swaps · #gate_unit_swaps
- 같은 다중유닛 심볼의 2+ 유닛 연결 교환. 조건: 같은 심볼 + 같은 핀 수.
- 핀은 유닛 내 위치로 매칭(동일 위치 = 등가). 트랙·비아·구리 네트 스왑, zone 유지, 미선택 연결 패드 프롬프트.
- 실행 2방법:
  - 한 유닛 패드 선택 → 우클릭 **Swap Gate Nets** 서브메뉴에서 타겟 유닛 선택.
  - 서로 다른 유닛 패드 2+ 선택 → 우클릭 **Swap Gate Nets**(첫 유닛 ↔ 둘째 유닛).

### Swapping more than two items · #swapping_more_than_two_items
- 2개: 일대일 교환. 3개+: 선택 순서로 순환(첫→둘째, 둘째→셋째, …, 마지막→첫). 핀=네트 전달, 게이트=유닛 패드 네트 전달.

### Syncing pin and gate swaps to the schematic · #syncing_pin_and_gate_swaps_to_the_schematic
- PCB는 즉시, 스키매틱은 **Update Schematic from PCB**로 back-annotate.
- 중요 back-annotation 옵션:
  - **Net Names**: 핀/게이트 스왑 동기화에 필수.
  - **Prefer symbol unit swaps over label swaps**: PCB 게이트 스왑의 스키매틱 반영 방식.
  - **Prefer symbol pin swaps over label swaps**: PCB 핀 스왑의 스키매틱 반영 방식.
