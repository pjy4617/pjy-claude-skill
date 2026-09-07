# KiCAD-MCP-Server 도구 카탈로그 + 엔진별 매핑

이 스킬의 1순위 분석 엔진인 **KiCAD-MCP-Server**의 MCP 도구 목록과,
미등록 시 폴백(kicad-cli / 직접 파싱) 매핑을 정리한다.

- 저장소: https://github.com/mixelpixx/KiCAD-MCP-Server (MIT)
- 구조: Node(TypeScript) 서버가 창구, 파이썬 브리지(`pcbnew`)가 실제 KiCad 조작. 서버가 파이썬을 자식 프로세스로 띄운다.
- 기준 버전: **2.7.0** — 도구 **233개** 등록(그중 173개가 16개 카테고리로 키워드 탐색 인덱싱).
- 등록 시 도구는 `mcp__<서버명>__<도구>` 형태로 노출된다. 본 문서는 서버명을 `kicad`로 가정(`mcp__kicad__run_drc` 등). 다른 이름으로 등록했다면 prefix를 맞춰 읽는다.
- **도구명 검증 필수**: 233개 전부를 외워 쓰지 않는다. 사용 전 `claude mcp list`로 연결(Connected)을 확인하고, `get_backend_state`로 파이썬 브리지까지 살아 있는지 본 뒤 호출한다. 이름의 정본은 서버 저장소의 `docs/TOOL_INVENTORY.md`다 — **`search_tools`로 안 잡힌다고 도구가 없는 것이 아니다**(아래 "탐색 미검출 도구" 참조). 정본에도 없는 이름이면 해당 분석은 kicad-cli/직접 파싱 폴백으로 처리한다.
- **버전 기준 3줄**: 서버 최소 요구 KiCad 9.0 / 이 플러그인 검증 기준 KiCad 10.0 / `kicad-cli sch erc`·`pcb drc`는 KiCad 8.0부터 존재. 세 표기는 서로 모순이 아니다.

---

## 도구 탐색 (이름을 모를 때 먼저 쓴다)

도구가 233개라 이름을 기억하는 대신 서버에 물어보는 쪽이 확실하다.

| 도구 | 쓸 때 |
|------|------|
| `list_tool_categories` | 16개 카테고리 전체 지도를 본다 |
| `get_category_tools` | 한 카테고리 안의 도구를 다 본다 (예: `drc`, `board`, `schematic`) |
| `search_tools` | 이름·설명에서 키워드로 찾는다 (예: "zone", "clearance") |

카테고리별 인덱싱 도구 수: schematic 26, export 27, symbol_library 17, board 15,
component 15, drc 7, library 7, schematic_batch 6, schematic_hierarchy 5,
schematic_layout 5, autoroute 4, routing 3, symbol_pins 3, parts-registry 3,
digikey 3, validation 2.

> 인덱싱되지 않은 도구(60개)는 `search_tools`로 찾지 못하지만 **이름을 알면 호출된다**.

**탐색 미검출 도구 (이 문서가 인용하는 것 중 23개)** — `search_tools`에 안 나와도 정상이다. 그대로 호출한다:
`check_courtyard_overlaps`, `find_orphaned_wires`, `find_overlapping_elements`, `find_wires_crossing_symbols`,
`get_category_tools`, `get_component_list`, `get_component_pads`, `get_net_at_point`, `get_nets_list`,
`get_pad_position`, `get_schematic_component`, `get_schematic_pin_locations`, `list_floating_labels`,
`list_tool_categories`, `query_traces`, `query_zones`, `run_erc`, `search_jlcpcb_parts`, `get_jlcpcb_part`,
`suggest_jlcpcb_alternatives`, `enrich_datasheets`, `get_datasheet_url`, `search_tools`.

**연결 확인은 `get_backend_state`로 한다.** `list_tool_categories`는 Node 서버만 확인하고 파이썬 브리지·pcbnew는 확인하지 못한다.
`get_backend_state`는 브리지를 실제로 타며 `backend`/`loadedBoard`/`boardPath`/`dirty`/`diskChangedExternally`를 돌려주므로
"보드가 로드됐는가", "사용자가 KiCad에서 저장한 뒤 바뀌었는가"(그러면 `reload_board`)까지 한 번에 안다.

**23개 동적 리소스(`kicad://board/...`, `kicad://project/...` 등)는 쓰지 않는다.** 같은 파이썬 명령을 감싼 것이라 도구와 데이터가 같고, Claude Code에서는 `ReadMcpResourceTool`을 거쳐야 해 도구 호출보다 번거롭다.

---

## 분석용 도구 카탈로그 (읽기 전용 중심)

이 스킬은 **읽기/분석 도구만** 사용한다. 서버에는 편집·생성 도구가 훨씬 많지만
(회로도 작성 233개 중 다수), 회로도 *생성*은 `kicad-design` 스킬 담당이다.

### 프로젝트 열기 (보드 도구 전용)
| 도구 | 기능 |
|------|------|
| `open_project` | `.kicad_pro` 열기 — 같은 이름의 `.kicad_pcb`를 함께 로드 |
| `open_board` | 특정 `.kicad_pcb` 열기 + 보드 상태 갱신 |
| `get_project_info` | 프로젝트 메타 정보 (**보드 로드 필요**) |
| `reload_board` | 디스크에서 보드 재로드 (사용자가 KiCad GUI에서 저장한 뒤 재분석할 때) |
| `get_backend_state` | 브리지 헬스체크 + 로드 상태 (`loadedBoard`, `dirty`, `diskChangedExternally`) |

> **"열어야 하는가"는 도구군에 따라 정반대다.**
> - **보드 도구(board/component/routing/DRC)는 전부 로드 필요** — 안 열면 `{"success": false, "message": "No board is loaded"}`.
> - **회로도 도구(schematic/validation/린트/심볼 라이브러리)는 `open_project`와 무관** — 전부 `schematicPath`(또는 `symbol`) 파라미터로 파일을 직접 받는다. `schematicPath`를 빠뜨리면 스키마 검증에서 실패한다. 계층 설계는 **루트 `.kicad_sch` 경로**를 넘겨야 전체 ERC가 된다.
> - `get_board_2d_view`, `export_*`는 `pcbPath`/`boardPath`를 주면 열지 않아도 된다.

### 회로(schematic) 분석
| 도구 | 기능 |
|------|------|
| `list_schematic_components` | 회로도 부품 나열 |
| `list_schematic_nets` | 넷 나열 |
| `get_schematic_component` | 부품 상세(속성/필드) |
| `get_net_connections` | 넷 하나의 모든 연결 (넷 → 핀) |
| `get_wire_connections` | 와이어 연결 관계 |
| `get_schematic_pin_locations` | 심볼 핀 좌표 |
| `generate_netlist` | 회로도에서 넷리스트 생성 |
| `run_erc` | Electrical Rules Check — **내부에서 kicad-cli `sch erc`를 실행**한다. kicad-cli가 없으면 MCP 경로도 실패 |
| `validate_schematic` | `.kicad_sch` 구조 무결성 — 결함 라인/컬럼 보고 |
| `get_schematic_view` | 회로도를 이미지(PNG/SVG)로 렌더 — 눈으로 확인 |

### 회로도 린트 (연결 오류 탐지)
| 도구 | 기능 |
|------|------|
| `list_floating_labels` | 어디에도 안 붙은 라벨 |
| `find_orphaned_wires` | 양끝이 뜬 와이어 |
| `find_wires_crossing_symbols` | 심볼을 관통하는 와이어(오접속 후보) |
| `find_overlapping_elements` | 겹친 요소 |
| `lint_offgrid` | 그리드에서 벗어난 연결 좌표 — 보이지 않는 미접속의 주원인. **`fix` 파라미터를 넘기지 않는다**(기본 false; true면 파일을 고친다) |
| `get_net_at_point` | 특정 좌표의 넷 조회 |

**린트 5종은 넘긴 시트 파일 하나만 검사한다.** 계층 설계는 `get_sheet_properties`로 서브시트를 받아 시트마다 반복 호출한다.
**`get_sheet_properties`는 직접 자식 1단계만 돌려준다** — 중첩 서브시트가 있으면 반환된 시트마다 다시 호출해 **재귀**해야 한다.
디렉토리의 `.kicad_sch` 목록과도 대조해 계층 어디에서도 참조되지 않는 **고아 시트**를 찾는다
(실측 보드: 파일 9개 대 계층 8개 — 한 개가 고아였다).
**린트가 잡고 ERC 가 침묵하면** 결함으로 올리지 않고 "판정 불일치 — 육안 확인 필요" 로 적는다(ERC 가 정본).

### 심볼 라이브러리
| 도구 | 기능 |
|------|------|
| `search_symbols` | 심볼 검색 |
| `get_symbol_info` | 심볼 상세 |
| `list_symbol_pins` | 심볼 핀 이름/번호/**타입** — 회로도 없이 라이브러리에서 직접 |
| `batch_list_symbol_pins` | 여러 심볼 핀을 한 번에 |
| `list_symbol_libraries` / `list_library_symbols` | 라이브러리 목록/내용 |

> `list_symbol_pins`의 **핀 타입**이 핀 충돌 판정의 근거다 (output/power_out/bidirectional 등).
> `symbol`('Library:Name') 외에 **`schematicPath`를 항상 함께 넘긴다** — 그래야 프로젝트 로컬 `sym-lib-table`의 벤더 심볼을 찾는다. 빠뜨리면 벤더 심볼 핀 타입이 비어 핀 충돌 판정이 누락된다.
>
> **회로도 도구 실패 모드**: SnapEDA/SamacSys 계열 "flat" 벤더 심볼이 있으면 회로도 도구 전부가
> `{"success": false, "error": "schematic_load_failed", "flatSymbols": [...]}`를 낸다. kicad-cli는 같은 파일을 정상 처리하므로
> 이 에러를 받으면 **해당 시트는 kicad-cli 폴백**으로 내려간다.
> **루트 시트가 flat 심볼을 임베드만 해도** 루트를 대상으로 한 skip 기반 도구가 전부 실패한다 —
> 즉 서브시트를 안 열어도 루트 하나로 회로도 도구 전체가 막힌다.
> 응답의 `flatSymbols`에 문제 심볼 이름이 오므로 그 이름을 리포트에 적고, 사용자에게 `repair_flat_symbols` 실행을 제안한다.
> `repair_flat_symbols`는 쓰기 도구라 읽기 전용 스킬이 직접 부르지는 않고 안내만 한다.

### PCB 보드 분석
| 도구 | 기능 |
|------|------|
| `get_board_info` | 보드 메타/속성 |
| `get_layer_list` | 레이어 목록 |
| `get_board_extents` | 보드 바운딩 박스(외곽 치수) |
| `get_board_2d_view` | 보드를 이미지(PNG/JPG/SVG)로 렌더 — `pcbPath`, `layers[]`, `width/height`, `format`, **`responseMode: inline\|file`**. 큰 보드는 `file`로 받아야 MCP 메시지 크기 한도를 피한다. kicad-cli로 렌더 |
| `get_component_list` | 배치 부품 전체 목록 (**개수 상한이 없다**). **`boundingBox` 필터는 실측(2.7.0)에서 무시되고 전체가 돌아온다** — 356 풋프린트 보드에서 bbox 를 넘겼는데 356개 전부(응답 101,265자)가 와 **토큰 한도 초과로 호출이 실패**했다. 큰 보드는 `layer` 로 앞/뒷면을 나눠 부르고, 좌표 기반 계산이 목적이면 `.kicad_pcb` 의 `(footprint ... (at x y))` 직접 파싱이 더 싸고 확실하다 |
| `find_component` | 레퍼런스/값으로 부품 검색 |
| `get_component_properties` | 부품 속성 |
| `get_component_pads` / `get_pad_position` | 부품 패드 정보/좌표 |
| `get_component_geometry` | 부품 외형 기하 |
| `check_placement_clearance` | 배치 간격 점검 |
| `check_courtyard_overlaps` | 코트야드 겹침 + 외곽 이탈 탐지. **오탐 두 유형을 걸러낸 뒤 보고한다.** (가) **면이 다른 쌍은 겹침이 아니다** — 앞면(`F.Cu`/`F.CrtYd`)과 뒷면(`B.Cu`/`B.CrtYd`) 부품을 2D 좌표만으로 비교해 양면 실장을 간섭으로 센다(실측 보드: 앞 222 / 뒤 134). (나) **중복 레퍼런스는 인스턴스를 하나의 바운딩 박스로 병합**해 허위 겹침·허위 외곽 이탈을 만든다. 필터 후 남은 것이 없으면 KiCad DRC 의 `courtyards_overlap` 을 정본으로 삼는다(실측: 이 도구 305쌍 대 KiCad DRC 0건). 수백 부품 보드는 `refs` 로 나눠 부른다(356 부품에서 한 응답 약 30 KB) |

### 라우팅/넷 분석
| 도구 | 기능 |
|------|------|
| `get_nets_list` | 넷 목록 (`name`/`code`/`class`). 스키마의 `includeStats`는 브리지가 **무시**하므로 통계는 없다 — 넷클래스 대조에만 쓴다. 응답 개수 상한이 없어 넷이 많은 보드는 그대로 다 온다 |
| `query_traces` | **넷/레이어/영역으로 트랙 필터** — 세그먼트 좌표·폭·레이어. **`net` 필터는 필수로 건다**(없으면 보드 전체 트랙이 30초 예산 안에 다 와야 한다). **비아는 돌아오지 않는다**(`includeVias`가 TS 스키마에 없어 항상 제외). 비아를 읽는 MCP 도구는 없다 → `(via ...)` 직접 파싱 |
| `query_zones` | 카퍼 존(플레인) 조회 — 넷/레이어/영역 필터. 반환 `isFilled`가 false면 `filledArea` 없음 → 사용자 동의 후 `kicad-cli pcb drc --refill-zones --save-board <pcb>`로 채워 저장하고 `reload_board` 후 재호출한다. **MCP `refill_zones`는 쓰지 않는다**(SWIG 세그폴트로 브리지가 죽는다). `--save-board`는 파일을 덮어쓰므로 GUI에서 닫힌 상태에서만 |
| `get_net_pads` | 넷에 붙은 모든 PCB 패드 |
| `get_ratsnest` / `estimate_airwire_lengths` | 미라우팅 에어와이어 + 길이 추정(넷별). `maxPadsPerNet`(기본 128) 초과 넷은 **조용히 `skipped`** — GND/전원 넷이 흔히 해당. `skipped`는 "미수행"으로 보고하거나 상한을 올려 재호출 |
| `get_design_rules` | 현재 설계 규칙 |

### 검증(DRC)
| 도구 | 기능 |
|------|------|
| `run_drc` | Design Rules Check 실행 — **내부에서 kicad-cli `pcb drc`를 실행**. 보드 로드 + **디스크에 저장된 파일** 필요. 600초 예산 |
| (kicad-cli `pcb drc`) | JSON 출력의 `unconnected_items` 는 **500에서 잘린다** — 실측 보드에서 499건이 왔지만 실제 에어와이어는 902개였고, 그 499건이 언급한 넷은 10개뿐이었다. `--help` 에 상한을 올리는 플래그는 **없다**(`--all-track-errors` 로도 499 그대로). **499~500이면 "절단됨" 으로 읽고** 실제 수는 `get_ratsnest` 또는 넷별 `Σ(패드 수 − 1)` 로 구한다. `--schematic-parity` 는 **옵트인** 이라 빼면 `schematic_parity` 가 빈 배열로 오는데 그것은 "이상 없음" 이 아니라 "미검사" 다 — 항상 켠다 |
| `get_drc_violations` | DRC 위반 목록 (`severity: error\|warning\|all`). **매 호출마다 내부에서 `run_drc`를 다시 돈다** → `run_drc`와 둘 다 부르지 않는다. **자신은 600초 목록에 없어 30초 예산**으로 돈다. 다만 **보드 규모로 미리 단정하지 말고 실측 후 판단한다** — 356 풋프린트·476 넷 2층 보드에서 4.7초에 514건을 완주했다. 일단 이것으로 돌려 보고 실제로 타임아웃이 나면 그때 `run_drc`(600초)로 바꿔 결과 JSON을 심각도별로 직접 거른다. **응답에 `unconnected` 유형은 없다** — 미배선은 이 도구로 0건이 되므로 `kicad-cli pcb drc` 의 `unconnected_items` 나 `get_ratsnest` 로 따로 본다 |
| `check_clearance` | 두 요소 간 클리어런스 계산 |

**DRC 전 저장 확인**: DRC는 kicad-cli가 **디스크 파일**을 읽는다. 그래서 실행 전에 사용자에게
"KiCad GUI에서 저장(Ctrl+S)했는가"를 묻는다. `is_dirty`는 MCP가 메모리에 든 보드의 상태만 보며
**GUI에서 편집 중인 미저장 상태는 감지하지 못한다** — 저장 확인 수단으로 쓰지 않는다.

### 내보내기 (검증·리포트용)
| 도구 | 기능 |
|------|------|
| `export_netlist` | 넷리스트 (KiCad/Spice/Cadstar/OrcadPCB2) |
| `export_bom` / `export_sch_bom` | BOM (CSV/XML/HTML/JSON) |
| `export_gerbers` / `export_drill` | 거버·드릴 (제조 출력 점검) |
| `export_pcb_pdf` / `export_pcb_svg` | 보드 도면 |
| `export_ipc2581` / `export_ipcd356` | IPC-2581 / IPC-D-356 넷리스트. `export_ipcd356` 은 `outputPath` **필수**(스크래치 경로로 지정). **IPC-D-356 을 파싱할 때 `317` 만 읽지 않는다** — `317`은 관통홀·비아, **SMD 패드는 `327`** 이다(실측 보드 1411행 중 `327` 1394 / `317` 16). 넷 이름은 컬럼 4–17 의 **14자**이고 **앞이 잘려 뒤 14자만** 남으며 **대문자로 변환**된다 — 비교는 `name.upper()[-14:]` 로 정규화한다 |

### 부품 조달 조회 (BOM 검토 시)
| 도구 | 기능 |
|------|------|
| `search_jlcpcb_parts` / `get_jlcpcb_part` | JLCPCB 부품 검색·조회 (로컬 스냅샷 DB, API 키 불필요) |
| `suggest_jlcpcb_alternatives` | 대체 부품 제안 |
| `digikey_search_parts` | Digi-Key 재고·가격 (API 키 필요, Production 앱) |
| `search_parts_registry` / `get_registry_part` | 오픈 부품 레지스트리 |
| `enrich_datasheets` / `get_datasheet_url` | 데이터시트 URL 보강 (LCSC 경유) |

---

## SI/PI 분석 — 전용 도구가 없다 (중요)

**이 서버에는 신호 무결성(SI)·전원 무결성(PI) 전용 분석 도구가 없다.**
임피던스 계산, IR drop, reference plane 연속성을 한 번에 판정해 주는 도구는 존재하지 않는다.

대신 **판정에 필요한 기하 데이터를 정확히 얻을 수 있다.** 계산과 판정은 이 스킬이 한다.

| 필요한 것 | 얻는 방법 |
|-----------|-----------|
| 트랙 길이·폭·레이어 | `query_traces`(넷 필터) 세그먼트 좌표에서 계산 |
| 차동 페어 길이 매칭 | 두 넷을 각각 `query_traces` → 길이 차 계산 |
| 레이어 전환(비아) 수 | `query_traces`로는 비아가 안 온다 → `.kicad_pcb`의 `(via ... (net N))` 직접 파싱으로 카운트 |
| 미라우팅/에어와이어 | `get_ratsnest` (`skipped` 넷은 미수행 표기) |
| 플레인 커버리지 | `query_zones`(레이어별 `filledArea` — `isFilled`일 때만) |
| 디커플링 근접도 | `get_component_list` + `get_net_pads` 좌표 거리 |
| 클리어런스 실측 | `check_clearance`(두 요소 간) |
| 설계 규칙 기준값 | `get_design_rules` |
| 유전율·층 두께·동박 두께 | **MCP 도구 없음** — `.kicad_pcb`의 `(setup (stackup ...))` 직접 파싱 |

**절대 임피던스와 IR drop은 스택업이 파일에 있으면 계산한다.** KiCad는 Board Setup > Physical Stackup을 채우면
그 값을 `.kicad_pcb`의 `(setup (stackup (layer "dielectric 1" (type "core") (thickness ...) (material "FR4")
(epsilon_r ...) (loss_tangent ...)) ...))`에 저장한다. dielectric 층의 `epsilon_r`·`thickness`가 있으면
**외층 마이크로스트립 / 내층 스트립라인 임피던스를 IPC-2141 근사식으로 계산해 판정**하고,
copper 층의 `thickness`(동박 두께)로 트랙 저항을 구해 IR drop도 근사한다.
파싱 스니펫과 근사식은 `references/pcb-analysis.md` 참조.

**서버에 스택업 읽기 도구는 없다.** 이 블록은 MCP 등록 여부와 무관하게 파일에서 직접 파싱한다 —
즉 폴백 모드에서도 같은 계산이 된다.

스택업 블록이 없거나 dielectric 층에 `epsilon_r`이 없으면 보고서에
**"미수행 — Board Setup > Physical Stackup 미설정"**으로 명시하고, 대신 폭/길이/레이어 구성이
`references/pcb-analysis.md`의 목표값 범위에 드는지로 대체 판정한다.

> 이전 버전(Seeed 서버)에는 `analyze_pcb_signal_integrity` / `analyze_pcb_power_integrity`가
> 있었으나 현재 엔진에는 없다. **그 이름으로 호출하지 않는다.**

---

## 엔진별 매핑 (폴백 체인)

| 분석 | KiCAD-MCP-Server | kicad-cli | 직접 파싱 |
|------|------------------|-----------|-----------|
| 넷리스트 생성 | `generate_netlist` / `export_netlist` | `sch export netlist --format kicadxml` | `(label)`/`(global_label)`/`(wire)` 추론 |
| 넷 목록 | `list_schematic_nets` / `get_nets_list` | netlist XML 파싱 | `(net N "이름")` 파싱 |
| 부품 목록 | `list_schematic_components` / `get_component_list` | netlist XML 파싱 | `(symbol ...)` / `(footprint ...)` 파싱 |
| 넷 연결 추적 | `get_net_connections` / `get_net_pads` | netlist XML 파싱 | 넷리스트 XML/직접 추론 |
| ERC | `run_erc` (내부 kicad-cli) | `sch erc --format json` | 미수행 |
| 회로도 구조 검증 | `validate_schematic` | 파싱 실패 여부로 간접 | 괄호 균형 검사 |
| 회로도 연결 린트 | `list_floating_labels` / `find_orphaned_wires` / `lint_offgrid` | 없음 | 좌표 대조 heuristic |
| 핀 충돌 | `get_net_connections` + `list_symbol_pins`(핀타입) 조합 판정 | netlist 핀타입 집계 | 넷별 핀타입 규칙 |
| 풋프린트 목록 | `get_component_list` / `find_component` | 없음 | `(footprint ...)` 파싱 |
| 보드 통계 | `get_board_info` + `get_layer_list` + `get_board_extents` + `query_traces`(트랙) | 없음 | `(segment)`/`(via)`/`(net)` 카운트 |
| 비아 수·레이어 전환 | 읽기 도구 없음 → 직접 파싱 | 없음 | `(via ...)` 카운트 |
| 넷별 트랙 | `query_traces`(넷 필터) | 없음 | `(segment ... (net N))` 파싱 |
| 카퍼 존/플레인 | `query_zones` | 없음 | `(zone ...)` 파싱 |
| 미라우팅 | `get_ratsnest` (`skipped` 주의) | 없음 | 넷별 패드 수 대비 세그먼트 수 |
| DRC | 작은 보드는 `get_drc_violations` 단독, 큰 보드는 `run_drc` (둘 다 내부 kicad-cli) | `pcb drc --format json` | 미수행 |
| 클리어런스 실측 | `check_clearance` | 없음 | 좌표 거리 계산 |
| 코트야드 겹침 | `check_courtyard_overlaps` | 없음 | 미수행 |
| 신호 무결성 | 전용 도구 없음 — `query_traces` 기하로 계산 | 없음 | heuristic(좌표 기반 길이/폭만) |
| 전원 무결성 | 전용 도구 없음 — `query_zones`+`get_net_pads`로 계산 | 없음 | heuristic(평면/폭만) |
| 보드 시각 확인 | `get_board_2d_view` (이미지) | `pcb export svg` | 없음 |
| Gerber export | `export_gerbers` / `export_drill` | `pcb export gerbers` | 없음 |

**핵심**: **ERC/DRC는 두 경로 모두 kicad-cli다.** MCP `run_erc`/`run_drc`도 내부에서 kicad-cli를 subprocess로 부르므로,
kicad-cli가 없으면 MCP를 등록해도 ERC/DRC는 실패한다. 엔진 감지에서 kicad-cli 유무는 MCP 사용 시에도 필수 확인 항목이다
(`KICAD_CLI` 환경변수로 경로 지정 가능).
**트랙/존/패드 기하(SI/PI 판정의 입력)는 MCP(pcbnew)** 가 사실상 유일한 정밀 경로다.
직접 파싱도 좌표는 얻지만 존 채움(fill) 결과와 실제 클리어런스는 pcbnew 없이 재현되지 않는다.

---

## kicad-cli 폴백 명령 모음

```bash
# 넷리스트
kicad-cli sch export netlist --format kicadxml --output /tmp/netlist.xml "$ROOT_SCH"

# ERC (KiCad 8+)
kicad-cli sch erc --output /tmp/erc.json --format json --severity-all "$ROOT_SCH"

# DRC (KiCad 8+)
kicad-cli pcb drc --output /tmp/drc.json --format json --severity-all "$PCB"

# Gerber/드릴 (제조 출력 점검 시)
kicad-cli pcb export gerbers --output /tmp/gerbers "$PCB"
```

---

## 설치 / 등록

> 전제: 로컬에 **KiCad 9.0+** 설치(`pcbnew` 파이썬 모듈 포함) + **Node.js 18+** + **kicad-cli**(ERC/DRC·렌더는 MCP 경로도 이것을 쓴다).
> Linux가 주 지원 플랫폼이고 Windows 지원, macOS는 실험적이다.
> 버전 기준: 서버 최소 KiCad 9.0 / 이 플러그인 검증 기준 KiCad 10.0 / `kicad-cli sch erc`·`pcb drc`는 8.0부터.
> 서버 문서(`docs/PLATFORM_GUIDE.md`)의 예시 경로는 `KiCad\9.0`이므로 10.0 사용자는 경로를 바꿔 읽는다.

### 1) 클론 + 빌드

```bash
git clone https://github.com/mixelpixx/KiCAD-MCP-Server.git
cd KiCAD-MCP-Server
npm install
npm run build          # TypeScript → dist/ (클라이언트가 실행하는 것은 dist/)
pip3 install -r requirements.txt
```

**pcbnew를 찾을 수 있는지 먼저 확인한다.**

```bash
python3 -c "import pcbnew; print(pcbnew.GetBuildVersion())"
```

버전 문자열이 찍히면 준비된 상태다.

### 2) 파이썬 환경 — 설치 방식에 따라 다르다

서버는 이 순서로 파이썬을 고른다:
저장소의 `venv/bin/python`(또는 `.venv/`) → `KICAD_PYTHON` 환경변수 →
KiCad 번들 파이썬 → `which python3` → `/usr/bin/python3`.

| KiCad 설치 방식 | 필요한 조치 |
|------------------|-------------|
| Linux apt/PPA | 시스템 파이썬에 `pcbnew`가 들어가므로 **추가 경로 설정 불필요**. venv를 쓸 거면 `--system-site-packages`로 만든다 |
| Windows 설치본 | `KICAD_PYTHON`을 KiCad 번들 파이썬으로 지정. `setup-windows.ps1`은 전제 점검·빌드·경로 감지까지만 하고 **Claude Code 등록은 해 주지 않는다**(`-ClientType claude-desktop\|cline\|manual`만 지원) — 스크립트가 출력한 `KICAD_PYTHON`/`PYTHONPATH` 값을 `claude mcp add -e ...`에 옮겨 적는다 |
| macOS 앱 | KiCad 번들 파이썬으로 `venv --system-site-packages` 생성 후 `KICAD_PYTHON` 지정. `setup-macos.sh --verify`가 전제 점검 + Claude Code용 `claude mcp add` 힌트를 출력한다 |
| **AppImage** | **고정 경로로 가리킬 수 없다**(실행 시마다 `/tmp`에 풀렸다 사라짐). apt/설치본으로 옮기는 편이 확실하다. 서버 공식 지원 표에는 없는, 이 플러그인의 판단이다 |

### 3) Claude Code에 MCP 등록 (서버명 `kicad`)

```bash
# Linux (apt 설치 — 경로 지정 불필요)
claude mcp add kicad -s user -e KICAD_AUTO_LAUNCH=false -e KICAD_BACKEND=swig -- \
  node /path/to/KiCAD-MCP-Server/dist/index.js

# 파이썬 경로를 명시해야 하는 경우 (Windows/macOS)
claude mcp add kicad -s user \
  -e KICAD_PYTHON=<KiCad 번들 python 경로> \
  -e KICAD_AUTO_LAUNCH=false -e KICAD_BACKEND=swig \
  -- node /path/to/KiCAD-MCP-Server/dist/index.js
```

`--` 앞은 등록 옵션, 뒤는 실제로 실행할 명령이다.
`-s user`면 모든 프로젝트에서, `-s project`면 공유 가능한 `.mcp.json`으로 기록된다.

### 4) 확인

```bash
claude mcp list | grep kicad     # Connected 표시 확인
```

등록 후 **Claude Code 재시작** 시 `mcp__kicad__*` 도구가 활성화된다.
연결 확인은 `get_backend_state`로 한다 — 파이썬 브리지까지 실제로 타므로 `backend`가 돌아오면 pcbnew까지 준비된 것이다.
(`list_tool_categories`는 Node 서버만 확인한다.)

**첫 호출이 느릴 수 있다 — 다만 55~65초는 macOS 한정 비용이다.** 파이썬 쪽 wxApp 초기화 55~65초는
서버 소스가 macOS 조건으로 적고 있고, 서버가 **기동하는 동안** 내부 `_warmup` 커맨드로 그 비용을 미리 지불한다
(`python/kicad_interface.py` 의 pcbnew import 주석과 `_warmup` 핸들러). 즉 첫 *도구 호출* 때 내는 비용이 아니다.
실측(Linux, 서버 기동 후 첫 호출)은 **3.3초**였다.
그래도 `get_backend_state`를 세션의 첫 호출로 두고, **서버를 막 띄운 직후라면 최대 1분까지 기다린다** —
여기서 타임아웃으로 오판해 폴백으로 내려가지 않는다.

자동 안내는 `kicad-setup` 스킬에서 제공한다(`--with-mcp` 옵션).

### 주요 환경변수

| 변수 | 기본값 | 하는 일 |
|------|--------|---------|
| `LOG_LEVEL` | `info` | 로그 상세도. `error`/`warn`/`info`/`debug` |
| `KICAD_AUTO_LAUNCH` | `false` | 작업 시 KiCad GUI 자동 실행 여부. 분석 용도면 `false` 권장 |
| `KICAD_PYTHON` | (없음) | 파이썬 경로 강제 지정. 저장소에 venv가 있으면 무시된다 |
| `KICAD_CLI` | (없음) | `kicad-cli` 경로 강제 지정 (ERC/DRC/렌더가 이것을 쓴다). 여러 KiCad 버전이 깔려 있으면 이것으로 고정한다 |
| `KICAD_CLI_PATH` | (없음) | `KICAD_CLI`의 별칭. 서버는 두 변수를 같은 우선순위로 읽고 먼저 값이 있는 쪽을 쓴다 |
| `KICAD_SKIP_SYMBOL_WARMUP` | (없음) | `1`이면 심볼 라이브러리 전체 사전 파싱(백그라운드 스레드)을 건너뛴다. 기동을 막지는 않으므로 보통 그대로 두고, 심볼 조회를 쓰지 않는 PCB 전용 분석에서 백그라운드 부하를 줄이고 싶을 때만 켠다. 꺼도 `list_symbols`가 필요할 때 캐시를 채운다 |
| `KICAD_BACKEND` | 자동 | `swig` 또는 `ipc`. **분석 용도는 `swig` 고정 권장** — IPC 연결 시도·재접속 대기 없이 파일 기반으로만 동작 |
| `PYTHONPATH` | 자동 유도 | 서버가 site-packages를 자동으로 찾으므로 `import pcbnew`가 되는 환경(Linux apt)에서는 불필요. 서버 문서의 "Required"는 낡은 서술 |
| `KICAD_MCP_LOG_LEVEL` | (없음) | `LOG_LEVEL`보다 우선 |

### KiCad GUI 연동 (참고 — 이 플러그인은 쓰지 않는다)

서버에는 `check_kicad_ui` / `launch_kicad_ui`(`projectPath`, `autoLaunch`)와 `KICAD_AUTO_LAUNCH` / `KICAD_EXECUTABLE` 환경변수가 있어
KiCad GUI를 띄운 채 작업할 수 있다. 실시간 동기화는 **IPC 백엔드 실험 기능**이고(KiCad Preferences > Plugins > Enable KiCad API에서 켬),
SWIG 백엔드에서는 수동 저장 후 File > Revert 리로드가 필요하다. 분석 스킬은 `KICAD_AUTO_LAUNCH=false`, `KICAD_BACKEND=swig`가 기본이다.

### 주의

- **파이썬 브리지가 죽으면 자동으로 되살아나지 않는다.** 도구가 연속으로
  `Python process for KiCAD scripting is not running`을 돌려주면 브리지가 종료된 것이다 —
  서버는 프로세스 핸들만 비우고 재기동하지 않으므로 이후 모든 호출이 같은 에러로 실패한다.
  `/mcp`에서 kicad 서버를 재연결(또는 세션 재시작)한 뒤 `get_backend_state`로 확인하고, 보드는 `open_board`로 다시 연다.
  죽는 대표 계기는 `refill_zones`의 SWIG 세그폴트다 — **세션 중 `refill_zones`는 호출하지 않는다**
  (존 채움은 `kicad-cli pcb drc --refill-zones --save-board`로 우회한다).
- **명령 기본 타임아웃은 30초다.** 600초를 받는 것은
  `run_drc`, `export_gerber`, `export_pdf`, `export_3d`, `sync_schematic_to_board`,
  `list_schematic_nets`, `list_schematic_labels`, `get_schematic_view`,
  `digikey_check_library_availability`, `autoroute` **뿐이고 나머지는 전부 30초**다.
  실무에서 걸리는 것들: `get_drc_violations`(내부 `run_drc`를 30초 예산으로 부른다 → 큰 보드는 `run_drc` 사용),
  `query_traces`(항상 `net` 또는 `layer`/`bbox` 필터를 걸어 응답을 쪼갠다),
  `export_gerbers`(복수형 신형 도구 — 600초 목록에 없어 30초다. 큰 보드는 `kicad-cli pcb export gerbers`를 직접 부른다).
- **MCP 쓰기 도구를 쓰는 동안 같은 파일을 KiCad GUI에서 열어 두지 않는다.** SWIG 백엔드는 파일을 직접 덮어쓰므로,
  GUI가 열려 있으면 "파일이 바뀌었다" 리로드 프롬프트가 뜨거나 GUI에서 먼저 저장한 변경이 다음 MCP 저장에서 지워진다.
  열려 있다면 GUI에서 먼저 저장·닫기, 작업 후 GUI에서 볼 때는 File > Revert가 아니라 **다시 열기**.
  이 분석 스킬은 읽기 전용이라 직접 위험은 낮지만, `--save-board`로 존을 채우거나 `repair_flat_symbols`를 안내할 때는 같은 규칙이 적용된다.
- **한 세션에 보드는 하나다.** 파이썬 브리지가 보드를 하나만 들고 있어, 두 프로젝트를 번갈아 분석하면
  두 번째 `open_board`가 첫 번째를 조용히 대체한다. 보고서 헤더에 `get_backend_state`의 `boardPath`를 찍어
  실제로 분석한 보드를 남기고, 끝나면 `close_project`로 정리한 뒤 다음 보드를 연다.
- **pip/npm 패키지 배포가 아니라 git clone + 빌드가 공식 경로.** `npm run build`를 빠뜨리면
  클라이언트가 실행할 `dist/`가 없다. TypeScript를 고친 뒤에도 매번 빌드해야 한다.
- Node 버전을 올리면(nvm 등) 등록에 절대경로로 박은 node 경로가 깨진다. `claude mcp list`가
  실패하면 이 줄부터 확인한다.
- **JLCPCB/Digi-Key API 키는 선택.** 없어도 동작한다 — JLCPCB는 로컬 스냅샷 DB로 대체된다.
  쓰려면 저장소 루트에 `.env`를 만든다(`.env.example` 참조, gitignore됨).
- 서버가 뜨는데 도구가 전부 실패하면 파이썬 브리지 문제다. 직접 띄워 확인한다:
  `echo '{"command":"list_libraries","params":{}}' | python3 python/kicad_interface.py`
  → `{"type": "ready"}` 뒤에 결과가 나오면 정상.
- `pcbnew` 호출 시 stderr에 섞이는 `assert "m_choices.GetCount() > 0" failed`는 **무해**하다.
  KiCad 자체가 뱉는 것이고 동작에 영향이 없다.
- KiCad 미설치 환경에서는 MCP가 동작하지 않으므로 자동으로 kicad-cli/직접 파싱 폴백으로 내려간다.
- 서버 저장소 `docs/CLIENT_CONFIGURATION.md`의 Claude Code 절(`~/.config/claude-code/mcp_config.json`, `claude-code mcp test`)은
  **낡은 문서**다. 현재 Claude Code는 `claude mcp add`이며 이 문서의 등록 명령이 맞다.
