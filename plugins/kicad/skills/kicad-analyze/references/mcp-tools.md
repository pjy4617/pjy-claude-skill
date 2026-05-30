# Seeed kicad-mcp-server 도구 카탈로그 + 엔진별 매핑

이 스킬의 1순위 분석 엔진인 **Seeed-Studio/kicad-mcp-server**의 MCP 도구 목록과,
미등록 시 폴백(kicad-cli / 직접 파싱) 매핑을 정리한다.

- 저장소: https://github.com/Seeed-Studio/kicad-mcp-server (MIT)
- 등록 시 도구는 `mcp__<서버명>__<도구>` 형태로 노출된다. 본 문서는 서버명을 `kicad`로 가정(`mcp__kicad__run_drc` 등). 다른 이름으로 등록했다면 prefix를 맞춰 읽는다.
- **도구명 검증 필수**: Seeed 서버는 정식 릴리스 태그 없이 활발히 개발 중이라 아래 카탈로그의 도구명/시그니처가 버전에 따라 바뀔 수 있다. 사용 전 `claude mcp list`로 연결(Connected)을 확인하고, 실제 노출된 도구 이름을 도구 탐색으로 대조한 뒤 호출한다. 카탈로그에 없거나 이름이 다르면 해당 분석은 kicad-cli/직접 파싱 폴백으로 처리한다.

---

## 도구 카탈로그 (약 23개)

### 회로(schematic) 분석
| 도구 | 기능 |
|------|------|
| `list_schematic_components` | 회로도 부품 나열 |
| `list_schematic_nets` | 넷 나열 |
| `get_schematic_info` | 계층 시트/메타 정보 |
| `search_symbols` | 심볼 라이브러리 검색 |
| `get_symbol_details` | 심볼 핀/속성 상세 |

### PCB 분석
| 도구 | 기능 |
|------|------|
| `list_pcb_footprints` | 풋프린트 나열 (레이어 필터) |
| `get_pcb_statistics` | 레이어/트랙/비아/넷/외곽 통계 |
| `find_tracks_by_net` | 넷별 트랙 세그먼트/레이어/폭 |
| `analyze_pcb_nets` | 넷 라우팅 상태/품질 |
| `analyze_pcb_signal_integrity` | 신호 무결성(임피던스/길이/레이어 전환) |
| `analyze_pcb_power_integrity` | 전원 무결성(평면/IR drop/디커플링) |

### 넷리스트
| 도구 | 기능 |
|------|------|
| `generate_netlist` | 넷리스트 생성 |
| `trace_netlist_connection` | 넷 ↔ 핀 연결 추적 |
| `get_netlist_nets` | 넷 목록 |
| `get_netlist_components` | 부품 목록 |

### 검증
| 도구 | 기능 |
|------|------|
| `run_erc` | Electrical Rules Check |
| `run_drc` | Design Rules Check |
| `detect_pin_conflicts` | 핀 타입 충돌 탐지 |

### 편집 (experimental — 이 스킬은 사용하지 않음, 참고용)
`create_kicad_project`, `add_component_from_library`, `add_wire`, `add_label`, `setup_pcb_layout`, `export_gerber`

> 회로도 편집은 KiCad에 회로도 Python API가 없어 S-expression 직접 조작 방식이라 **experimental**이다. 이 분석 스킬은 **읽기/분석 도구만** 사용한다. 회로도 *생성*은 `kicad-design` 스킬 담당.

---

## 엔진별 매핑 (폴백 체인)

| 분석 | Seeed MCP | kicad-cli | 직접 파싱 |
|------|-----------|-----------|-----------|
| 넷리스트 생성 | `generate_netlist` | `sch export netlist --format kicadxml` | `(label)`/`(global_label)`/`(wire)` 추론 |
| 넷 연결 추적 | `trace_netlist_connection` | netlist XML 파싱 | 넷리스트 XML/직접 추론 |
| ERC | `run_erc` | `sch erc --format json` | ✗ 미수행 |
| 핀 충돌 | `detect_pin_conflicts` | netlist 핀타입 집계 | 넷별 핀타입 규칙 |
| 풋프린트 목록 | `list_pcb_footprints` | — | `(footprint ...)` 파싱 |
| 보드 통계 | `get_pcb_statistics` | — | `(segment)`/`(via)`/`(net)` 카운트 |
| 넷별 트랙 | `find_tracks_by_net` / `analyze_pcb_nets` | — | `(segment ... (net N))` 파싱 |
| DRC | `run_drc` | `pcb drc --format json` | ✗ 미수행 |
| 신호 무결성 | `analyze_pcb_signal_integrity` | ✗ | heuristic(좌표 기반 길이/폭만) |
| 전원 무결성 | `analyze_pcb_power_integrity` | ✗ | heuristic(평면/폭만) |
| Gerber export | `export_gerber` | `pcb export gerbers` | ✗ |

**핵심**: ERC/DRC는 MCP 또는 kicad-cli 중 하나면 정밀하게 가능. **SI/PI는 Seeed MCP(pcbnew)** 가 사실상 유일한 정밀 경로.

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

## Seeed MCP 설치 / 등록

> 전제: 로컬에 **KiCad 9.0+** 설치 + `kicad-cli`가 PATH. 정밀 PCB/SI/PI 분석은 **KiCad 번들 Python**에 설치해야 `pcbnew`를 쓴다. (Seeed 서버 자체는 KiCad 8+도 지원하나, 이 플러그인은 9.0+ 기준.)

```bash
# 1) 저장소 클론 + (KiCad 번들 Python에) editable 설치
git clone https://github.com/Seeed-Studio/kicad-mcp-server
cd kicad-mcp-server
# Windows (KiCad 9):
#   "C:\Program Files\KiCad\9.0\bin\python.exe" -m pip install fastmcp
#   "C:\Program Files\KiCad\9.0\bin\python.exe" -m pip install -e .
#   (KiCad 10이면 경로의 9.0 → 10.0)
# Linux (배포판 패키지 / KiCad 9):
#   python3 -m pip install fastmcp -e .   # 시스템 python에 pcbnew가 함께 설치된 경우
# macOS:
#   /Applications/KiCad/KiCad.app/Contents/Frameworks/python3 -m pip install fastmcp -e .
# 시스템 Python 폴백(pcbnew 없으면 기능 제한): pip install -e .

# 2) Claude Code에 MCP 등록 (서버명 kicad)
claude mcp add kicad -s user -- "<KiCad python 경로>" -m kicad_mcp_server
#   시스템 python 폴백: claude mcp add kicad -s user -- python -m kicad_mcp_server

# 3) 세션 재시작 후 mcp__kicad__* 도구 활성화 확인
claude mcp list | grep kicad
```

자동 안내는 `kicad-setup` 스킬에서 제공한다(`--with-mcp` 옵션). 등록 후 **Claude Code 재시작** 필요.

### 주의

- pip/npm 패키지 배포가 아니라 **git clone + editable install**가 공식 경로.
- 정식 릴리스 태그 없음(활발히 개발 중). 회로도 편집은 experimental — 이 스킬은 읽기/분석만 사용하므로 영향 없음.
- KiCad 미설치 환경에서는 MCP가 동작하지 않으므로 자동으로 kicad-cli/직접 파싱 폴백으로 내려간다.
