# kicad-cli — 명령행 인터페이스 레퍼런스 — KiCad 10.0 사용 다이제스트

> **원문**: https://docs.kicad.org/10.0/en/cli/cli.html

> **범위**: kicad-cli 전체: 서브커맨드 fp / jobset / pcb / sch / sym / version 와 각 명령의 Usage·옵션/플래그

> 한국어 요약 다이제스트. 섹션 제목의 #anchor로 원문 핀포인트: https://docs.kicad.org/10.0/en/cli/cli.html#<anchor>

## 목차

- [Introduction · #introduction_to_the_kicad_command_line_interface](#introduction_to_the_kicad_command_line_interface) — kicad-cli 개요, 6개 서브커맨드, --help 사용법
- [Footprint commands · #fp](#fp) — `fp` 서브커맨드 개요
- [Footprint export · #footprint_export](#footprint_export) — `fp export svg` 풋프린트 → SVG
- [Footprint upgrade · #footprint_upgrade](#footprint_upgrade) — `fp upgrade` 풋프린트 라이브러리 포맷 변환
- [Jobset commands · #jobset](#jobset) — `jobset run` 사전 정의 잡셋 실행
- [PCB commands · #pcb](#pcb) — `pcb` 서브커맨드 개요
- [PCB DRC · #pcb_drc](#pcb_drc) — `pcb drc` 디자인 룰 체크
- [PCB export: 3D PDF · #pcb_export_3d_pdf](#pcb_export_3d_pdf) — `pcb export 3dpdf`
- [PCB export: BREP (OCCT) · #pcb_export_brep_occt](#pcb_export_brep_occt) — `pcb export brep`
- [PCB export: drill file · #pcb_export_drill_file](#pcb_export_drill_file) — `pcb export drill` 드릴 파일
- [PCB export: DXF · #pcb_export_dxf](#pcb_export_dxf) — `pcb export dxf`
- [PCB export: GenCAD · #pcb_export_gencad](#pcb_export_gencad) — `pcb export gencad`
- [PCB export: Gerber · #pcb_export_gerber](#pcb_export_gerber) — `pcb export gerbers` 거버 파일
- [PCB export: GLB · #pcb_export_glb](#pcb_export_glb) — `pcb export glb`
- [PCB export: HPGL · #pcb_export_hpgl](#pcb_export_hpgl) — `pcb export hpgl` (10.0 비활성)
- [PCB export: IPC-2581 · #pcb_export_ipc_2581](#pcb_export_ipc_2581) — `pcb export ipc2581`
- [PCB export: IPC-D-356 · #pcb_export_ipc_d_356](#pcb_export_ipc_d_356) — `pcb export ipcd356` 넷리스트
- [PCB export: ODB++ · #pcb_export_odb](#pcb_export_odb) — `pcb export odb`
- [PCB export: PDF · #pcb_export_pdf](#pcb_export_pdf) — `pcb export pdf`
- [PCB export: PLY · #pcb_export_ply](#pcb_export_ply) — `pcb export ply`
- [PCB export: position file · #pcb_export_position_file](#pcb_export_position_file) — `pcb export pos` 부품배치 파일
- [PCB export: PostScript · #pcb_export_postscript](#pcb_export_postscript) — `pcb export ps`
- [PCB export: statistics · #pcb_export_statistics](#pcb_export_statistics) — `pcb export stats` 보드 통계
- [PCB export: STEP · #pcb_export_step](#pcb_export_step) — `pcb export step`
- [PCB export: STL · #pcb_export_stl](#pcb_export_stl) — `pcb export stl`
- [PCB export: STEPZ · #pcb_export_stepz](#pcb_export_stepz) — `pcb export stpz`
- [PCB export: U3D · #pcb_export_u3d](#pcb_export_u3d) — `pcb export u3d`
- [PCB export: SVG · #pcb_export_svg](#pcb_export_svg) — `pcb export svg`
- [PCB export: VRML · #pcb_export_vrml](#pcb_export_vrml) — `pcb export vrml`
- [PCB export: XAO · #pcb_export_xao](#pcb_export_xao) — `pcb export xao`
- [PCB import · #pcb_import](#pcb_import) — `pcb import` 비-KiCad 보드 가져오기
- [PCB render · #pcb_render](#pcb_render) — `pcb render` 3D 레이트레이싱 렌더링
- [PCB upgrade · #pcb_upgrade](#pcb_upgrade) — `pcb upgrade` 보드 포맷 변환
- [Schematic commands · #schematic](#schematic) — `sch` 서브커맨드 개요
- [Schematic ERC · #schematic_erc](#schematic_erc) — `sch erc` 전기 룰 체크
- [Schematic export: BOM · #schematic_export_bill_of_materials](#schematic_export_bill_of_materials) — `sch export bom`
- [Schematic export: DXF · #schematic_export_dxf](#schematic_export_dxf) — `sch export dxf`
- [Schematic export: HPGL · #schematic_export_hpgl](#schematic_export_hpgl) — `sch export hpgl` (10.0 비활성)
- [Schematic export: netlist · #schematic_export_netlist](#schematic_export_netlist) — `sch export netlist`
- [Schematic export: PDF · #schematic_export_pdf](#schematic_export_pdf) — `sch export pdf`
- [Schematic export: PostScript · #schematic_export_postscript](#schematic_export_postscript) — `sch export ps`
- [Schematic export: BOM (legacy) · #schematic_export_bill_of_materials_legacy_bom_scripts](#schematic_export_bill_of_materials_legacy_bom_scripts) — `sch export python-bom`
- [Schematic export: SVG · #schematic_export_svg](#schematic_export_svg) — `sch export svg`
- [Schematic upgrade · #schematic_upgrade](#schematic_upgrade) — `sch upgrade`
- [Symbol commands · #symbol](#symbol) — `sym` 서브커맨드 개요
- [Symbol export · #symbol_export](#symbol_export) — `sym export svg`
- [Symbol upgrade · #symbol_upgrade](#symbol_upgrade) — `sym upgrade`
- [Version commands · #version](#version) — `version` 버전 출력

---

## Introduction to the KiCad Command-Line Interface · #introduction_to_the_kicad_command_line_interface

- `kicad-cli` 바이너리로 회로도·PCB·심볼·풋프린트에 대한 작업을 자동화 수행 (예: PCB → Gerber 플롯, 레거시 라이브러리를 최신 포맷으로 업그레이드).
- 6개 서브커맨드: `fp`, `jobset`, `pcb`, `sch`, `sym`, `version`. 각 서브커맨드는 자체 하위 명령·인자를 가질 수 있다. 예: `kicad-cli pcb export gerbers example.kicad_pcb`.
- `--help`/`-h` 플래그로 각 서브커맨드 사용법 확인. 예: `kicad-cli pcb -h`, `kicad-cli pcb export gerbers -h`.
- ⚠️ **NOTE (macOS):** `kicad-cli` 실행 파일 경로는 `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`.

> 💡 **공통 옵션 메모 (이 다이제스트 전체 적용):**
> - 거의 모든 명령에 `-h`, `--help`가 있다 (해당 명령의 도움말 출력).
> - `-D <name>=<value>`, `--define-var <name>=<value>`: 프로젝트 변수 정의 추가/재정의. 여러 번 사용 가능.
> - `--variant <name>`: 출력할 어셈블리 variant 이름. 출력 경로에 `${VARIANT}` 사용 시 variant별 파일명 생성. 미지정 시 기본 variant 출력.
> - 레이어명은 canonical(`F.Cu`, `In.1`, `F.Fab` 등) 또는 사용자 정의명 지정 가능 — 사용자 정의명이 먼저 매칭됨.

---

## Footprint commands · #fp

- `fp` 서브커맨드: 풋프린트를 다른 포맷으로 export 하거나 풋프린트 라이브러리를 현재 KiCad 풋프린트 파일 포맷으로 업그레이드.

### Footprint export · #footprint_export

- **용도:** `fp export svg` — 지정 라이브러리의 풋프린트 하나/여럿을 SVG 파일로 export. 라이브러리의 각 풋프린트의 각 레이어마다 파일 1개 출력.
- **Usage:** `kicad-cli fp export svg [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--define-var KEY=VALUE]…​ [--theme VAR] [--footprint FOOTPRINT_NAME] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--black-and-white] INPUT_FILE_OR_DIR`
- **Positional:** `INPUT_FILE_OR_DIR` — 풋프린트(`.kicad_mod`) 또는 풋프린트 라이브러리 디렉토리(`.pretty`).

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | 풋프린트 SVG export 도움말. |
| `-o <output dir>` | `--output <output dir>` | export 출력 폴더. 라이브러리 내 각 풋프린트의 각 레이어마다 파일 1개. 미사용 시 현재 디렉토리. |
| `-l <layer list>` | `--layers <layer list>` | export할 레이어명 쉼표 구분 목록 (예: `F.Cu,B.Cu`). 미지정 시 전 레이어 export. |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. 여러 번 사용 가능. |
| `-t <theme name>` | `--theme <theme name>` | export에 사용할 테마. 미지정 시 풋프린트 에디터의 현재 선택 테마. |
| `--fp <footprint>` | `--footprint <footprint>` | export할 특정 풋프린트명. 미사용 시 라이브러리 내 전체 풋프린트 export. |
| `--sp` | `--sketch-pads-on-fab-layers` | front/back fab 레이어에 패드 외곽선과 번호를 그림. |
| `--hdnp` | `--hide-DNP-footprints-on-fab-layers` | DNP 풋프린트의 텍스트·그래픽을 fab 레이어에 플롯하지 않음. |
| `--sdnp` | `--sketch-DNP-footprints-on-fab-layers` | fab 레이어에 DNP 풋프린트 그래픽을 sketch 모드로 플롯. |
| `--cdnp` | `--crossout-DNP-footprints-on-fab-layers` | fab 레이어의 DNP 풋프린트 courtyard 위에 "X" 표시, refdes에 취소선. |
|  | `--black-and-white` | 흑백으로 export. |

### Footprint upgrade · #footprint_upgrade

- **용도:** `fp upgrade` — 지정 풋프린트 라이브러리를 레거시 KiCad/비-KiCad 포맷에서 현재 KiCad 네이티브 포맷으로 변환. 이미 현재 포맷이면 아무 작업 안 함.
- **지원 입력 포맷:** KiCad(`.pretty`+`.kicad_mod`), KiCad pre-5.0(`.mod`, `.emp`), Altium 풋프린트(`.PcbLib`), Altium 통합(`.IntLib`), CADSTAR PCB archive(`.cpa`), EAGLE XML(`.lbr`), EasyEDA(JLCEDA) Std(`.json`), EasyEDA(JLCEDA) Pro(`.elibz`, `.epro`, `.zip`), GEDA/PCB(`.fp` 파일 폴더).
- **Usage:** `kicad-cli fp upgrade [--help] [--output OUTPUT_DIR] [--force] INPUT_FILE_OR_DIR`
- **Positional:** `INPUT_FILE_OR_DIR` — 업그레이드할 풋프린트/라이브러리. KiCad 포맷이면 `.kicad_mod` 파일 또는 `.pretty` 디렉토리.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | upgrade 도움말. |
| `-o <output dir>` | `--output <output dir>` | 업그레이드 출력 디렉토리. 미사용 시 원본 풋프린트 위에 덮어쓰기. |
|  | `--force` | 이미 현재 포맷이어도 입력 라이브러리를 재저장. |

---

## Jobset commands · #jobset

- **용도:** `jobset run` — 사전 정의된 잡셋(`.kicad_jobset`)을 실행.
- **Usage:** `kicad-cli jobset run [--help] [--stop-on-error] [--file JOB_FILE] [--output OUTPUT] INPUT_FILE`
- **Positional:** `INPUT_FILE` — 잡셋과 함께 사용할 프로젝트 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | jobset 도움말. |
|  | `--stop-on-error` | 잡을 순서대로 실행하다 잡 하나가 실패하면 중단. 미지정 시 실패 후에도 계속 실행. |
| `-f <jobset file>` | `--file <jobset file>` | 실행할 잡셋 파일(`.kicad_jobset`). |
|  | `--output <destination description or ID>` | 생성할 잡셋 destination. 미지정 시 모든 destination 생성. description 또는 고유 ID로 지정. description은 고유해야 함(중복 시 아무것도 실행 안 됨). ID는 본질적으로 고유하며 `--output` 미사용 시 `jobset run`이 각 destination ID를 출력함. ID는 `.kicad_jobset` 파일의 destination `id` 키에도 있음. |

---

## PCB commands · #pcb

- `pcb` 명령: 디자인 룰 체크 실행, 또는 보드를 다양한 포맷(팹·3D 포함)으로 export.

### PCB DRC · #pcb_drc

- **용도:** `pcb drc` — 보드에 디자인 룰 체크를 실행하고 리포트 생성. (kicad-analyze 스킬 핵심 명령)
- **Usage:** `kicad-cli pcb drc [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--format FORMAT] [--all-track-errors] [--schematic-parity] [--units UNITS] [--severity-all] [--severity-error] [--severity-warning] [--severity-exclusions] [--exit-code-violations] [--refill-zones] [--save-board] INPUT_FILE`
- **Positional:** `INPUT_FILE` — DRC 실행할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | DRC 도움말. |
| `-o <output filename>` | `--output <output filename>` | DRC 리포트 출력 파일명. 미사용 시 입력 파일명 + 포맷에 따른 `.rpt`/`.json` 확장자. |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
|  | `--format <format>` | 리포트 포맷. `report`(기본) 또는 `json`. |
|  | `--all-track-errors` | 각 트랙의 모든 오류 리포트. |
|  | `--schematic-parity` | PCB와 회로도 간 parity(일치) 테스트. |
|  | `--units <unit>` | 리포트 단위. `mm`(기본), `in`, `mils`. |
|  | `--severity-all` | 모든 DRC 위반 리포트 (다른 severity 옵션 전부 사용과 동등). |
|  | `--severity-error` | error 레벨 위반 리포트. 다른 severity 옵션과 조합 가능. |
|  | `--severity-warning` | warning 레벨 위반 리포트. 조합 가능. |
|  | `--severity-exclusions` | 제외된(excluded) 위반 리포트. 조합 가능. |
|  | `--exit-code-violations` | 위반 존재 여부에 따라 종료 코드 반환. 위반 없으면 0, 있으면 5. |
|  | `--refill-zones` | DRC 실행 전 모든 존 재충진. `--save-board`도 같이 쓰지 않으면 보드는 저장되지 않음. |
|  | `--save-board` | DRC 실행 후 보드 저장. `--refill-zones`도 같이 쓰지 않으면 저장되지 않음. |

---

> 💡 **3D 모델 export 공통 옵션 (3dpdf, brep, glb, ply, step, stl, stpz, u3d, xao 공유):** 아래 명령들은 동일한 옵션 세트를 가진다. 각 명령 섹션에서는 출력 확장자·고유 옵션만 명시하고 이 표를 참조한다.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | 해당 export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + 포맷별 확장자(명령별 상이). |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
| `-f` | `--force` | 출력 파일 덮어쓰기. |
|  | `--no-unspecified` | "unspecified" 풋프린트 타입 부품의 3D 모델 제외. |
|  | `--no-dnp` | "Do not populate" 속성 부품의 3D 모델 제외. |
|  | `--variant <name>` | 출력할 variant 이름. `${VARIANT}` 경로 치환 지원. |
|  | `--grid-origin` | grid origin을 출력 파일 원점으로 사용. |
|  | `--drill-origin` | drill origin을 출력 파일 원점으로 사용. |
|  | `--subst-models` | 풋프린트의 VRML 모델을 동일 이름의 STEP/IGS 모델로 교체(존재 시). |
|  | `--board-only` | 보드 자체만 포함, 모든 부품 모델 제외. |
|  | `--cut-vias-in-body` | conductor 레이어를 export 안 해도 보드 바디에 비아 홀을 절단. |
|  | `--no-board-body` | 보드 바디 제외. |
|  | `--no-components` | 부품 3D 모델 제외. |
|  | `--component-filter <refdes list>` | 이 refdes 목록(쉼표 구분, 와일드카드 지원)에 매칭되는 부품 3D 모델만 포함. |
|  | `--include-tracks` | 외층 conductor의 트랙·비아 포함 (시간 소요). |
|  | `--include-pads` | 패드 포함 (시간 소요). |
|  | `--include-zones` | 존 포함 (시간 소요). |
|  | `--include-inner-copper` | 내층 conductor 요소 포함. |
|  | `--include-silkscreen` | 실크스크린 그래픽을 flat face 집합으로 포함. |
|  | `--include-soldermask` | 솔더마스크 레이어를 flat face 집합으로 포함. |
|  | `--fuse-shapes` | 겹치는 geometry를 융합 (시간 소요). |
|  | `--fill-all-vias` | conductor 레이어의 비아 홀을 절단하지 않음. |
|  | `--no-extra-pad-thickness` | 패드에 추가 금속 두께 부여 비활성. 미사용 시 패드에 0.005mm 추가되어 주변 금속과 분리된 face가 됨. |
|  | `--min-distance <min distance>` | 두 점을 동일 위치로 간주할 허용오차. 기본 `0.01mm`. |
|  | `--net-filter <net filter>` | 이 와일드카드에 매칭되는 넷에 속한 copper 항목만 포함. |
|  | `--user-origin <output origin>` | 출력 파일의 커스텀 원점(X,Y). 예 `1x1in`, `1x1inch`, `25.4x25.4mm`. 기본 단위 mm. |

### PCB export: 3D PDF · #pcb_export_3d_pdf

- **용도:** `pcb export 3dpdf` — 보드의 3D 모델을 임베드한 PDF로 export.
- **Usage:** `kicad-cli pcb export 3dpdf [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--user-origin VAR] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.
- **기본 출력 확장자:** `.pdf`.
- **옵션:** 위 "3D 모델 export 공통 옵션" 표와 동일.

### PCB export: BREP (OCCT) · #pcb_export_brep_occt

- **용도:** `pcb export brep` — 보드를 BREP(OCCT 네이티브 boundary representation) 3D 모델 파일로 export.
- **Usage:** `kicad-cli pcb export brep [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--user-origin VAR] INPUT_FILE`
- **기본 출력 확장자:** `.brep`.
- **옵션:** "3D 모델 export 공통 옵션" 표와 동일.

### PCB export: drill file · #pcb_export_drill_file

- **용도:** `pcb export drill` — 보드에서 드릴 파일 export.
- **Usage:** `kicad-cli pcb export drill [--help] [--output OUTPUT_DIR] [--format FORMAT] [--drill-origin DRILL_ORIGIN] [--excellon-zeros-format ZEROS_FORMAT] [--excellon-oval-format OVAL_FORMAT] [--excellon-units UNITS] [--excellon-mirror-y] [--excellon-min-header] [--excellon-separate-th] [--generate-map] [--generate-report] [--report-path REPORT_FILE] [--generate-tenting] [--map-format MAP_FORMAT] [--gerber-precision VAR] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | 드릴 파일 export 도움말. |
| `-o <output dir>` | `--output <output dir>` | 드릴 파일 출력 디렉토리. 미사용 시 현재 디렉토리. |
|  | `--format <format>` | 드릴 파일 포맷. `excellon`(기본) 또는 `gerber`. |
|  | `--drill-origin <origin>` | 드릴 파일 좌표 원점. `absolute`(기본, 보드 절대 원점) 또는 `plot`(보드 drill/placement 원점). |
|  | `--excellon-zeros-format <format>` | zeros 포맷. `decimal`(기본), `suppressleading`, `suppresstrailing`, `keep`. Excellon 전용. |
|  | `--excellon-oval-format <format>` | oval 홀 드릴 모드. `route` 또는 `alternate`(기본). Excellon 전용. |
| `-u <units>` | `--excellon-units <units>` | 드릴 파일 단위. `mm`(기본) 또는 `in`. Excellon 전용. |
|  | `--excellon-mirror-y` | Y 방향으로 드릴 파일 미러. Excellon 전용. |
|  | `--excellon-min-header` | 최소 헤더 사용. Excellon 전용. |
|  | `--excellon-separate-th` | plated/non-plated through hole별 별도 드릴 파일 생성. Excellon 전용. |
|  | `--generate-map` | 드릴 파일 외에 맵 파일도 생성. |
|  | `--generate-report` | 모든 드릴 히트를 나열한 리포트 파일 생성. |
|  | `--report-path <report filename>` | 드릴 리포트 출력 파일명. 미사용 시 입력 파일명 + `-drill.rpt`. |
|  | `--generate-tenting` | tented 드릴 히트용 별도 드릴 파일 생성. Gerber X2 포맷 전용. |
|  | `--map-format <format>` | 맵 파일 포맷. `pdf`(기본), `gerberx2`, `ps`, `dxf`, `svg`. |
|  | `--gerber-precision <precision>` | 드릴 파일 정밀도(자릿수). `5` 또는 `6`(기본). Gerber 포맷 전용. |

### PCB export: DXF · #pcb_export_dxf

- **용도:** `pcb export dxf` — 보드를 DXF 파일로 export.
- **Usage:** `kicad-cli pcb export dxf [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--common-layers COMMON_LAYER_LIST] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--exclude-refdes] [--exclude-value] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--subtract-soldermask] [--use-contours] [--use-drill-origin] [--include-border-title] [--output-units UNITS] [--drill-shape-opt VAR] [--mode-single] [--mode-multi] [--scale SCALE] [--check-zones] [--variant VAR] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | DXF export 도움말. |
| `-o <output dir>` | `--output <output dir>` | 출력 폴더/파일명. `--mode-single` 시 출력 파일명(미지정 시 입력+`.pdf`(원문 표기 그대로)). `--mode-multi` 시 출력 디렉토리(미지정 시 현재 디렉토리). |
| `-l <layer list>` | `--layers <layer list>` | export할 레이어명 쉼표 목록 (예: `F.Cu,B.Cu`). 최소 1개 필수. |
| `--cl <layer list>` | `--common-layers <layer list>` | 모든 레이어 파일에 함께 플롯할 공통 레이어 목록. |
|  | `--drawing-sheet <sheet path>` | 보드 파일 지정 도면 시트를 덮어쓸 도면 시트 경로. |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
| `--erd` | `--exclude-refdes` | refdes 제외. |
| `--ev` | `--exclude-value` | 풋프린트 값 제외. |
| `--sp` | `--sketch-pads-on-fab-layers` | fab 레이어에 패드 외곽선·번호 표시. |
| `--hdnp` | `--hide-DNP-footprints-on-fab-layers` | DNP 풋프린트 텍스트·그래픽 미플롯. |
| `--sdnp` | `--sketch-DNP-footprints-on-fab-layers` | DNP 풋프린트 그래픽 sketch 모드 플롯. |
| `--cdnp` | `--crossout-DNP-footprints-on-fab-layers` | DNP courtyard "X" + refdes 취소선. |
|  | `--subtract-soldermask` | 솔더마스크 없는 영역의 실크 제거. |
| `--uc` | `--use-contours` | 그래픽 항목을 contour로 플롯. |
| `--udo` | `--use-drill-origin` | drill/place 파일 원점 사용. |
| `--ibt` | `--include-border-title` | 시트 테두리·타이틀 블록 포함. |
| `--ou <unit>` | `--output-units <unit>` | 출력 단위. `mm` 또는 `in`(기본). |
|  | `--drill-shape-opt <shape>` | 드릴 마크 형태. `0` 없음, `1` 작게, `2` 실제 크기(기본). |
|  | `--mode-single` | 단일 파일 생성. output 경로 = 전체 경로+파일명. `COMMON_LAYER_LIST` 미작동, `LAYER_LIST`가 전 레이어 제어. |
|  | `--mode-multi` | 레이어별 DXF 파일 생성(`LAYER_LIST` 각 레이어 = 파일 1개). output 경로 = 디렉토리. |
|  | `--scale <scale>` | 플롯 스케일 팩터. 테두리·타이틀 블록은 미스케일. `0`이면 autoscale. |
|  | `--check-zones` | export 전 존 채움 확인·필요 시 재충진. 변경분은 보드에 저장 안 됨. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |

### PCB export: GenCAD · #pcb_export_gencad

- **용도:** `pcb export gencad` — 보드를 GenCAD 파일로 export.
- **Usage:** `kicad-cli pcb export gencad [--help] [--output OUTPUT_DIR] [--define-var KEY=VALUE]…​ [--flip-bottom-pads] [--unique-pins] [--unique-footprints] [--use-drill-origin] [--store-origin-coord] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | (원문 표기상 "DXF export 도움말") GenCAD export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `.cad`. |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
| `-f` | `--flip-bottom-pads` | bottom 풋프린트 padstack 뒤집기. |
|  | `--unique-pins` | 고유 핀 이름 생성. |
|  | `--unique-footprints` | 풋프린트 인스턴스마다 새 shape 생성(shape 재사용 안 함). |
|  | `--use-drill-origin` | drill/place 파일 원점을 원점으로 사용. |
|  | `--store-origin-coord` | 원점 좌표를 파일에 저장. |

### PCB export: Gerber · #pcb_export_gerber

- **용도:** `pcb export gerbers` — 보드를 Gerber 파일로 export, 레이어당 파일 1개. (kicad-analyze 스킬 핵심 명령)
- **Usage:** `kicad-cli pcb export gerbers [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--common-layers COMMON_LAYER_LIST] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--exclude-refdes] [--exclude-value] [--include-border-title] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--no-x2] [--no-netlist] [--subtract-soldermask] [--disable-aperture-macros] [--use-drill-file-origin] [--precision PRECISION] [--no-protel-ext] [--check-zones] [--variant VAR] [--board-plot-params] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.
- 💡 단일 레이어 export는 `kicad-cli pcb export gerber`(단수)도 별도 존재(원문 미수록 — 이 명령은 복수형 `gerbers`로 전 레이어 플롯).

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | Gerber export 도움말. |
| `-o <output dir>` | `--output <output dir>` | 출력 폴더. 레이어당 파일 1개. 미사용 시 현재 디렉토리. |
| `-l <layer list>` | `--layers <layer list>` | 플롯할 레이어명 쉼표 목록. 미지정 시 전 레이어 플롯, 레이어당 파일 1개. |
| `--cl <layer list>` | `--common-layers <layer list>` | 모든 출력 파일에 포함할 공통 레이어 목록. |
|  | `--drawing-sheet <sheet path>` | 도면 시트 경로(보드 파일 설정 덮어씀). |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
| `--erd` | `--exclude-refdes` | refdes 제외. |
| `--ev` | `--exclude-value` | 풋프린트 값 제외. |
| `--ibt` | `--include-border-title` | 시트 테두리·타이틀 블록 포함. |
| `--sp` | `--sketch-pads-on-fab-layers` | fab 레이어 패드 외곽선·번호. |
| `--hdnp` | `--hide-DNP-footprints-on-fab-layers` | DNP 풋프린트 텍스트·그래픽 미플롯. |
| `--sdnp` | `--sketch-DNP-footprints-on-fab-layers` | DNP 풋프린트 그래픽 sketch 플롯. |
| `--cdnp` | `--crossout-DNP-footprints-on-fab-layers` | DNP courtyard "X" + refdes 취소선. |
|  | `--no-x2` | 확장 X2 포맷 사용 안 함. |
|  | `--no-netlist` | 넷리스트 속성 미포함. |
|  | `--subtract-soldermask` | 솔더마스크 없는 영역의 실크 제거. |
|  | `--disable-aperture-macros` | aperture 매크로 비활성. |
|  | `--use-drill-file-origin` | 절대 원점 대신 drill/place 파일 원점 사용. |
|  | `--precision <precision>` | Gerber 정밀도(자릿수). `5` 또는 `6`(기본). |
|  | `--no-protel-ext` | Protel 확장자(`.gbl`, `.gtl` 등) 대신 `.gbr` 사용. |
|  | `--check-zones` | export 전 존 확인·재충진. 변경분 미저장. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |
|  | `--board-plot-params` | 보드 파일에 이미 설정된 Gerber 플롯 설정 사용. |

### PCB export: GLB · #pcb_export_glb

- **용도:** `pcb export glb` — 보드를 GLB(binary glTF) 3D 모델 파일로 export.
- **Usage:** `kicad-cli pcb export glb [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--user-origin VAR] INPUT_FILE`
- **기본 출력 확장자:** `.glb`.
- **옵션:** "3D 모델 export 공통 옵션" 표와 동일.

### PCB export: HPGL · #pcb_export_hpgl

- ⚠️ **NOTE:** `kicad-cli pcb export hpgl`는 KiCad 10.0에서 **비활성(non-functional)**. KiCad는 더 이상 HPGL 출력을 지원하지 않음. 호환성 목적의 비기능 명령으로 포함되어 있으며 향후 버전에서 제거 예정.
- **Usage:** `kicad-cli pcb export hpgl [--help] [--output OUTPUT_DIR] INPUT_FILE`

### PCB export: IPC-2581 · #pcb_export_ipc_2581

- **용도:** `pcb export ipc2581` — 보드를 IPC-2581 포맷으로 export.
- **Usage:** `kicad-cli pcb export ipc2581 [--help] [--output OUTPUT_FILE] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--precision PRECISION] [--compress] [--version VAR] [--units VAR] [--bom-col-int-id FIELD_NAME] [--bom-col-mfg-pn FIELD_NAME] [--bom-col-mfg FIELD_NAME] [--bom-col-dist-pn FIELD_NAME] [--bom-col-dist FIELD_NAME] [--bom-rev REVISION] [--variant VAR] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | IPC-2581 export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `.xml`. |
|  | `--drawing-sheet <sheet path>` | 도면 시트 경로(덮어씀). |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
|  | `--precision <precision>` | 소수 구분자 이후 자릿수 정밀도. 기본 `6`. |
|  | `--compress` | 출력 파일을 ZIP으로 압축. |
|  | `--version <version>` | IPC-2581 표준 버전. `B` 또는 `C`(기본). |
|  | `--units <unit>` | export 단위. `mm`(기본) 또는 `in`. |
|  | `--bom-col-int-id <field>` | BOM Internal ID 컬럼에 쓸 파트 필드명. 임의 풋프린트 필드 가능, 공백이면 컬럼 생략. |
|  | `--bom-col-mfg-pn <field>` | BOM Manufacturer Part Number 컬럼 필드명. |
|  | `--bom-col-mfg <field>` | BOM Manufacturer 컬럼 필드명. |
|  | `--bom-col-dist-pn <field>` | BOM Distributor Part Number 컬럼 필드명. |
|  | `--bom-col-dist <field>` | BOM Distributor 컬럼 필드명. |
|  | `--bom-rev <revision>` | BOM Revision 필드 값. 미지정 시 회로도 루트 시트의 `Revision` 필드 사용. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |

### PCB export: IPC-D-356 · #pcb_export_ipc_d_356

- **용도:** `pcb export ipcd356` — 보드에서 IPC-D-356 넷리스트 생성.
- **Usage:** `kicad-cli pcb export ipcd356 [--help] [--output OUTPUT_FILE] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | IPC-D-356 export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `.d356`. |

### PCB export: ODB++ · #pcb_export_odb

- **용도:** `pcb export odb` — 보드를 ODB++ 포맷으로 export.
- **Usage:** `kicad-cli pcb export odb [--help] [--output OUTPUT_FILE] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--precision PRECISION] [--compression VAR] [--units VAR] [--variant VAR] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | ODB++ export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명(압축 없으면 폴더명). |
|  | `--drawing-sheet <sheet path>` | 도면 시트 경로(덮어씀). |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
|  | `--precision <precision>` | 소수 구분자 이후 자릿수. 기본 `2`. |
|  | `--compression <mode>` | 압축 모드. `none`, `zip`(기본), `tgz`. |
|  | `--units <unit>` | 출력 단위. `mm`(기본) 또는 `in`. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |

### PCB export: PDF · #pcb_export_pdf

- **용도:** `pcb export pdf` — 보드를 PDF로 export. 레이어를 각각 파일로 또는 단일 파일 내 시트로 플롯.
- **Usage:** `kicad-cli pcb export pdf [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--common-layers COMMON_LAYER_LIST] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--mirror] [--exclude-refdes] [--exclude-value] [--include-border-title] [--subtract-soldermask] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--negative] [--black-and-white] [--theme THEME_NAME] [--drill-shape-opt VAR] [--mode-single] [--mode-separate] [--mode-multipage] [--scale SCALE] [--bg-color COLOR] [--check-zones] [--variant VAR] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | PDF export 도움말. |
| `-o <output dir>` | `--output <output dir>` | 출력 폴더/파일명. `--mode-single`/`--mode-multipage` 시 파일명(미지정 시 입력+`.pdf`). `--mode-separate` 시 디렉토리(미지정 시 현재 디렉토리). |
| `-l <layer list>` | `--layers <layer list>` | export할 레이어명 쉼표 목록. 최소 1개 필수. |
| `--cl <layer list>` | `--common-layers <layer list>` | 모든 레이어에 함께 플롯할 공통 레이어. |
|  | `--drawing-sheet <sheet path>` | 도면 시트 경로(덮어씀). |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
| `-m` | `--mirror` | 보드 미러(bottom 레이어 표시에 유용). |
| `--erd` | `--exclude-refdes` | refdes 제외. |
| `--ev` | `--exclude-value` | 풋프린트 값 제외. |
| `--ibt` | `--include-border-title` | 시트 테두리·타이틀 블록 포함. |
|  | `--subtract-soldermask` | 솔더마스크 없는 영역 실크 제거. |
| `--sp` | `--sketch-pads-on-fab-layers` | fab 레이어 패드 외곽선·번호. |
| `--hdnp` | `--hide-DNP-footprints-on-fab-layers` | DNP 풋프린트 미플롯. |
| `--sdnp` | `--sketch-DNP-footprints-on-fab-layers` | DNP sketch 플롯. |
| `--cdnp` | `--crossout-DNP-footprints-on-fab-layers` | DNP "X" + 취소선. |
| `-n` | `--negative` | 네거티브 플롯. |
|  | `--black-and-white` | 흑백 플롯. |
| `-t <theme name>` | `--theme <theme name>` | 사용할 테마. 미지정 시 보드 에디터 현재 테마. |
|  | `--drill-shape-opt` | 드릴 마크 형태. `0` 없음, `1` 작게, `2` 실제 크기(기본). |
|  | `--mode-single` | 단일 파일, 전 레이어를 한 페이지에 플롯. `COMMON_LAYER_LIST` 미작동, `LAYER_LIST`가 전체 제어. |
|  | `--mode-separate` | 레이어별 PDF 파일. output 경로 = 디렉토리. |
|  | `--mode-multipage` | 다중 페이지 단일 PDF(`LAYER_LIST` 각 레이어 = 페이지). output 경로 = 전체 경로+파일명. |
|  | `--scale <scale>` | 플롯 스케일. `0`이면 autoscale. 테두리·타이틀 블록 미스케일. |
|  | `--bg-color <color>` | 플롯 배경색. hex(`#rrggbb`/`#rrggbbaa`) 또는 CSS(`rgb()`/`rgba()`). |
|  | `--check-zones` | export 전 존 확인·재충진. 변경분 미저장. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |

### PCB export: PLY · #pcb_export_ply

- **용도:** `pcb export ply` — 보드를 PLY 3D 모델 파일로 export.
- **Usage:** `kicad-cli pcb export ply [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--user-origin VAR] INPUT_FILE`
- **기본 출력 확장자:** `.ply`.
- **옵션:** "3D 모델 export 공통 옵션" 표와 동일.

### PCB export: position file · #pcb_export_position_file

- **용도:** `pcb export pos` — 보드에서 부품 배치(position/centroid) 파일 export.
- **Usage:** `kicad-cli pcb export pos [--help] [--output OUTPUT_FILE] [--side VAR] [--format FORMAT] [--units UNITS] [--bottom-negate-x] [--use-drill-file-origin] [--smd-only] [--exclude-fp-th] [--exclude-dnp] [--gerber-board-edge] [--variant VAR] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | position 파일 export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `.pos`. |
|  | `--side <side>` | export할 보드 면. `front`, `back`, `both`(기본). Gerber 포맷은 `both` 미지원. |
|  | `--format <format>` | position 파일 포맷. `ascii`(기본), `csv`, `gerber`. |
|  | `--units <unit>` | position 파일 단위. `in`(기본) 또는 `mm`. Gerber 포맷에는 효과 없음. |
|  | `--bottom-negate-x` | bottom 레이어 풋프린트 X 좌표 음수화. Gerber 효과 없음. |
|  | `--use-drill-file-origin` | 절대 원점 대신 drill/place 파일 원점 사용. Gerber 효과 없음. |
|  | `--smd-only` | SMD 부품만 포함. Gerber 효과 없음. |
|  | `--exclude-fp-th` | through-hole 패드 가진 풋프린트 모두 제외. Gerber 효과 없음. |
|  | `--exclude-dnp` | "Do not populate" 속성 풋프린트 모두 제외. |
|  | `--gerber-board-edge` | board edge 레이어 포함(Gerber 포맷 전용). |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |

### PCB export: PostScript · #pcb_export_postscript

- **용도:** `pcb export ps` — 보드를 PostScript 파일로 export.
- **Usage:** `kicad-cli pcb export ps [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--common-layers COMMON_LAYER_LIST] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--mirror] [--exclude-refdes] [--exclude-value] [--include-border-title] [--subtract-soldermask] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--negative] [--black-and-white] [--theme THEME_NAME] [--drill-shape-opt VAR] [--mode-single] [--mode-multi] [--track-width-correction TRACK_COR] [--x-scale-factor X_SCALE] [--y-scale-factor Y_SCALE] [--force-a4] [--scale SCALE] [--check-zones] [--variant VAR] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.
- 💡 공통 플로팅 옵션(`-l/--layers`, `--cl/--common-layers`, `--drawing-sheet`, `-D`, `-m/--mirror`, `--erd`, `--ev`, `--ibt`, `--subtract-soldermask`, `--sp`, `--hdnp`, `--sdnp`, `--cdnp`, `-n/--negative`, `--black-and-white`, `-t/--theme`, `--drill-shape-opt`, `--mode-single`, `--mode-multi`, `--scale`, `--check-zones`, `--variant`)는 PDF/DXF와 동일 의미. PS 전용 추가 옵션:

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | PS export 도움말. |
| `-o <output dir>` | `--output <output dir>` | 출력 폴더/파일명. `--mode-single` 시 파일명(미지정 시 입력+`.ps`), `--mode-multi` 시 디렉토리(미지정 시 현재 디렉토리). |
| `-C` | `--track-width-correction` | 트랙·비아·패드 크기에 더할 전역 보정(mm). PostScript 출력 장치 오차 보정용. |
| `-X` | `--x-scale-factor` | exact scale용 X 스케일 조정. |
| `-Y` | `--y-scale-factor` | exact scale용 Y 스케일 조정. |
| `-A` | `--force-a4` | A4 용지 강제. |

### PCB export: statistics · #pcb_export_statistics

- **용도:** `pcb export stats` — 보드 디자인 통계 리포트 export.
- **Usage:** `kicad-cli pcb export stats [--help] [--output OUTPUT_FILE] [--format FORMAT] [--units UNITS] [--exclude-footprints-without-pads] [--subtract-holes-from-board] [--subtract-holes-from-copper] INPUT_FILE`
- **Positional:** `INPUT_FILE` — 통계를 뽑을 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | statistics 도움말. |
| `-o <output filename>` | `--output <output filename>` | 통계 리포트 출력 파일명. 미사용 시 입력 파일명 + `_statistics` 접미 + 포맷별 `.rpt`/`.json`. |
|  | `--format <format>` | 리포트 포맷. `report`(기본) 또는 `json`. |
|  | `--units <unit>` | 리포트 단위. `mm`(기본) 또는 `in`. |
|  | `--exclude-footprints-without-pads` | 패드 없는 풋프린트를 부품 카운트에서 제외. |
|  | `--subtract-holes-from-board` | 전체 보드 면적에서 홀 면적 차감. |
|  | `--subtract-holes-from-copper` | 전체 copper 면적에서 홀 면적 차감. |

### PCB export: STEP · #pcb_export_step

- **용도:** `pcb export step` — 보드를 STEP 파일로 export.
- **Usage:** `kicad-cli pcb export step [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--no-optimize-step] [--user-origin VAR] INPUT_FILE`
- **기본 출력 확장자:** `.step`.
- **옵션:** "3D 모델 export 공통 옵션" 표와 동일 + 아래 STEP 전용 옵션:

| 긴 플래그 | 설명 |
| --- | --- |
| `--no-optimize-step` | STEP 파일 최적화 안 함. parametric curve 작성이 활성화되어 파일 크기·읽기/쓰기 시간이 줄지만 타 소프트웨어 호환성이 떨어질 수 있음. |

### PCB export: STL · #pcb_export_stl

- **용도:** `pcb export stl` — 보드를 STL 3D 모델 파일로 export.
- **Usage:** `kicad-cli pcb export stl [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--user-origin VAR] INPUT_FILE`
- **기본 출력 확장자:** `.stl`.
- **옵션:** "3D 모델 export 공통 옵션" 표와 동일.

### PCB export: STEPZ · #pcb_export_stepz

- **용도:** `pcb export stpz` — 보드를 STEPZ(GZIP 압축 STEP) 파일로 export.
- **Usage:** `kicad-cli pcb export stpz [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--no-optimize-step] [--user-origin VAR] INPUT_FILE`
- **기본 출력 확장자:** `.stpz`.
- **옵션:** "3D 모델 export 공통 옵션" 표 + `--no-optimize-step`(STEP과 동일 의미).

### PCB export: U3D · #pcb_export_u3d

- **용도:** `pcb export u3d` — 보드의 3D 모델을 임베드한 PDF로 export.
- **Usage:** `kicad-cli pcb export u3d [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--user-origin VAR] INPUT_FILE`
- **기본 출력 확장자:** `.pdf`.
- **옵션:** "3D 모델 export 공통 옵션" 표와 동일.

### PCB export: SVG · #pcb_export_svg

- **용도:** `pcb export svg` — 보드를 SVG 파일로 export.
- **Usage:** `kicad-cli pcb export svg [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--common-layers COMMON_LAYER_LIST] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--subtract-soldermask] [--mirror] [--theme THEME_NAME] [--negative] [--black-and-white] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--page-size-mode MODE] [--fit-page-to-board] [--exclude-drawing-sheet] [--drill-shape-opt SHAPE_OPTION] [--mode-single] [--mode-multi] [--scale SCALE] [--check-zones] [--variant VAR] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.
- 💡 `-o/-l/--cl/--drawing-sheet/-D/--subtract-soldermask/-m/-t/-n/--black-and-white/--sp/--hdnp/--sdnp/--cdnp/--drill-shape-opt/--mode-single/--mode-multi/--scale/--check-zones/--variant`는 PDF/PS와 동일 의미(`-o` 미지정 시 입력+`.pdf` 원문 표기, `--mode-single`=파일명/`--mode-multi`=디렉토리). SVG 전용 추가:

| 긴 플래그 | 설명 |
| --- | --- |
| `--page-size-mode <mode>` | 페이지 크기 모드. `0`(기본) 전체 시트(도면 프레임·타이틀 포함)에 맞춤, `1` 현재 페이지 크기, `2` 보드 자체 크기. |
| `--fit-page-to-board` | SVG 크기를 보드 외곽에 맞춤(= `--page-size-mode 2`). |
| `--exclude-drawing-sheet` | 도면 시트 없이 SVG 플롯. |

### PCB export: VRML · #pcb_export_vrml

- **용도:** `pcb export vrml` — 보드를 VRML 3D 모델 파일로 export.
- **Usage:** `kicad-cli pcb export vrml [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--user-origin VAR] [--units VAR] [--models-dir VAR] [--models-relative] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 보드 파일.
- ⚠️ VRML은 다른 3D export와 옵션 세트가 다르다(`--grid-origin`·`--include-*` 등 없음).

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | VRML export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `.wrl`. |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
| `-f` | `--force` | 출력 파일 덮어쓰기. |
|  | `--no-unspecified` | "unspecified" 풋프린트 타입 부품 모델 제외. |
|  | `--no-dnp` | "Do not populate" 부품 모델 제외. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |
|  | `--user-origin <output origin>` | 커스텀 원점(X,Y). 예 `1x1in`, `25.4x25.4mm`. 기본 단위 mm. 미지정 시 보드 중심 사용. |
|  | `--units <units>` | 출력 단위. `mm`, `m`, `in`(기본), `tenths`(1/10인치). |
|  | `--models-dir <output model directory>` | 부품 모델을 복사할 출력 디렉토리. 미사용 시 출력 파일에 임베드. |
|  | `--models-relative` | `--models-dir`와 함께, 출력 파일에 상대 경로 사용. |

### PCB export: XAO · #pcb_export_xao

- **용도:** `pcb export xao` — 보드를 XAO(SALOME/Gmsh) 3D 모델 파일로 export.
- **Usage:** `kicad-cli pcb export xao [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--user-origin VAR] INPUT_FILE`
- **기본 출력 확장자:** `.xao`.
- **옵션:** "3D 모델 export 공통 옵션" 표와 동일.

### PCB import · #pcb_import

- **용도:** `pcb import` — 비-KiCad PCB 파일을 KiCad 포맷으로 가져옴. 입력 보드의 레이어는 KiCad 레이어로 자동 매핑.
- **Usage:** `kicad-cli pcb import [--help] [--output OUTPUT_FILE] [--format FORMAT] [--report-format FORMAT] [--report-file FILE] INPUT_FILE`
- **Positional:** `INPUT_FILE` — 가져올 비-KiCad 포맷 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | import 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `.kicad_pcb`. |
|  | `--format <format>` | 입력 보드 포맷. `auto`(기본), `pads`, `altium`, `eagle`, `cadstar`, `fabmaster`, `pcad`, `solidworks`. `auto`/미지정 시 자동 판별 시도. |
|  | `--report-format <format>` | 리포트 포맷. `none`(기본), `json`, `text`. |
|  | `--report-file <report filename>` | 가져오기 리포트 출력 파일명. 미사용 시 stdout으로 출력. |

### PCB render · #pcb_render

- **용도:** `pcb render` — 보드 3D 모델의 레이트레이싱 렌더링을 생성해 PNG/JPEG로 저장.
- **Usage:** `kicad-cli pcb render [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--variant VAR] [--width WIDTH] [--height HEIGHT] [--side SIDE] [--background BG] [--quality QUALITY] [--preset PRESET] [--use-board-stackup-colors VAR] [--floor] [--perspective] [--zoom ZOOM] [--pan VECTOR] [--pivot PIVOT] [--rotate ANGLES] [--light-top COLOR] [--light-bottom COLOR] [--light-side COLOR] [--light-camera COLOR] [--light-side-elevation ANGLE] INPUT_FILE`
- **Positional:** `INPUT_FILE` — 렌더링할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | render 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. **필수.** 확장자가 포맷 결정: `.png` 또는 `.jpg`/`.jpeg`. |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |
| `-w <width>` | `--width <width>` | 이미지 폭(px). 기본 `1600`. |
| `-h <height>` | `--height <height>` | 이미지 높이(px). 기본 `900`. (주: `-h`가 height와 help에 중복 표기) |
|  | `--side <side>` | 렌더할 보드 면. `top`(기본), `bottom`, `left`, `right`, `front`, `back`. |
|  | `--background <background>` | 배경. `default`(기본), `transparent`, `opaque`. PNG 기본=transparent, JPG 기본=opaque. |
|  | `--quality <quality>` | 렌더 품질. `basic`(기본), `high`, `user`. `user`면 프로젝트 저장 렌더 설정 사용. |
|  | `--preset <color preset>` | 색상 프리셋. `follow_pcb_editor`, `follow_plot_settings`(기본), `legacy_preset_flag`. |
|  | `--use-board-stackup-colors` | 보드 stackup 정의 색상이 프리셋 색상을 덮어씀. |
|  | `--floor` | 품질 프리셋에서 비활성이어도 바닥·그림자·후처리 활성. |
|  | `--perspective` | orthogonal 대신 perspective 투영 사용. |
|  | `--zoom <zoom level>` | 카메라 줌 팩터(정수). 기본 `1`. |
|  | `--pan <camera pan>` | 카메라 pan 위치(mm), 형식 `'X,Y,Z'`. 예 `'3,0,0'`. |
|  | `--pivot <pivot>` | 보드 중심 기준 pivot(cm), 형식 `'X,Y,Z'`. 예 `'-10,2,0'`. |
|  | `--rotate <rotation>` | pivot 기준 보드 회전(도), 형식 `'X,Y,Z'`. 예 isometric `'-45,0,45'`. |
|  | `--light-top <intensity>` | top 라이트 강도. `'R,G,B'` 또는 단일 수, 범위 0-1. |
|  | `--light-bottom <intensity>` | bottom 라이트 강도. 0-1. |
|  | `--light-side <intensity>` | side 라이트 강도. 0-1. |
|  | `--light-camera <intensity>` | camera 라이트 강도. 0-1. |
|  | `--light-side-elevation <elevation>` | side 라이트 고도각(도), 범위 0-90. |

### PCB upgrade · #pcb_upgrade

- **용도:** `pcb upgrade` — 이전 KiCad 보드 포맷을 현재 KiCad 네이티브 포맷으로 변환. 이미 현재 포맷이면 무작업.
- **Usage:** `kicad-cli pcb upgrade [--help] [--force] INPUT_FILE`
- **Positional:** `INPUT_FILE` — 업그레이드할 보드 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | upgrade 도움말. |
|  | `--force` | 이미 현재 포맷이어도 입력 보드 파일 재저장. |

---

## Schematic commands · #schematic

- `sch` 명령: 전기 룰 체크 실행, 회로도를 다양한 포맷으로 export, 또는 BOM/넷리스트 export. 각 하위 명령은 자체 옵션을 가짐.

### Schematic ERC · #schematic_erc

- **용도:** `sch erc` — 회로도에 전기 룰 체크를 실행하고 리포트 생성. (kicad-analyze 스킬 핵심 명령)
- **Usage:** `kicad-cli sch erc [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--format VAR] [--units VAR] [--severity-all] [--severity-error] [--severity-warning] [--severity-exclusions] [--exit-code-violations] INPUT_FILE`
- **Positional:** `INPUT_FILE` — ERC 실행할 회로도 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | ERC 도움말. |
| `-o <output filename>` | `--output <output filename>` | ERC 리포트 출력 파일명. 미사용 시 입력 파일명 + 포맷별 `.rpt`/`.json`. |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
|  | `--format <format>` | 리포트 포맷. `report`(기본) 또는 `json`. |
|  | `--units <unit>` | 리포트 단위. `mm`(기본), `in`, `mils`. |
|  | `--severity-all` | 모든 ERC 위반 리포트(다른 severity 옵션 전부 사용과 동등). |
|  | `--severity-error` | error 레벨 위반 리포트. 조합 가능. |
|  | `--severity-warning` | warning 레벨 위반 리포트. 조합 가능. |
|  | `--severity-exclusions` | 제외된 위반 리포트. 조합 가능. |
|  | `--exit-code-violations` | 위반 존재 여부에 따라 종료 코드 반환. 없으면 0, 있으면 5. |

### Schematic export: bill of materials · #schematic_export_bill_of_materials

- **용도:** `sch export bom` — 회로도에서 BOM export. 포맷·포함 필드 제어 옵션 다수. 심볼 필드 테이블에서 BOM export하는 것과 동등.
- ⚠️ **NOTE:** 레거시 XML + Python BOM 스크립트 워크플로로 BOM을 뽑으려면 `sch export python-bom` 사용.
- **Usage:** `kicad-cli sch export bom [--help] [--output OUTPUT_FILE] [--variant VAR] [--preset PRESET] [--format-preset FMT_PRESET] [--fields FIELDS] [--labels LABELS] [--group-by GROUP_BY] [--sort-field SORT_BY] [--sort-asc VAR] [--filter FILTER] [--exclude-dnp] [--include-excluded-from-bom] [--field-delimiter FIELD_DELIM] [--string-delimiter STR_DELIM] [--ref-delimiter REF_DELIM] [--ref-range-delimiter REF_RANGE_DELIM] [--keep-tabs] [--keep-line-breaks] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 회로도 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | 도움말 출력 후 종료. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `.csv`. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |
|  | `--preset <preset>` | 회로도의 이름붙은 BOM 프리셋 설정 사용. 예 `"Grouped By Value"`. |
|  | `--format-preset <format preset>` | 이름붙은 BOM 포맷 프리셋 사용. 예 `CSV`. |
|  | `--fields <fields>` | export할 필드 순서 목록. `*`는 전 필드. DNP·Exclude from board 등 가상 필드는 `${DNP}`/`${EXCLUDE_FROM_BOARD}`로 접근(`${}` 유무 모두 허용). 기본 `"Reference,Value,Footprint,QUANTITY,DNP"`. |
|  | `--labels <labels>` | export 필드에 적용할 라벨 순서 목록. 기본 `"Refs,Value,Footprint,Qty,DNP"`. |
|  | `--group-by <fields>` | 값이 일치할 때 reference를 그룹화할 필드. |
|  | `--sort-field <fields>` | 정렬 기준 필드명. 기본 `"Reference"`. |
|  | `--sort-asc` | 지정 시 오름차순, 미지정 시 내림차순 정렬. |
|  | `--filter <filter>` | 지정 시 refdes가 필터에 매칭되는 부품만 출력. 와일드카드 `*`(0개 이상 임의 문자), `?`(임의 단일 문자) 지원. |
|  | `--exclude-dnp` | "Do not populate" 속성 심볼 제외. |
|  | `--include-excluded-from-bom` | "Exclude from BOM" 표시 심볼 포함. ⚠️ KiCad 10.0부터 deprecated, 효과 없음. |
|  | `--field-delimiter <delimiter>` | 필드/컬럼 구분자. 기본 `","`. |
|  | `--string-delimiter <delimiter>` | 필드를 감쌀 문자(기본 없음). |
|  | `--ref-delimiter <delimiter>` | 개별 reference 사이 문자. 기본 `","`. |
|  | `--ref-range-delimiter <delimiter>` | reference 범위 사이 문자. 기본 `"-"`. 공백이면 범위 표기 안 함. |
|  | `--keep-tabs` | 입력 필드의 탭 문자 유지(기본은 제거). |
|  | `--keep-line-breaks` | 입력 필드의 줄바꿈 유지(기본은 제거). |

### Schematic export: DXF · #schematic_export_dxf

- **용도:** `sch export dxf` — 회로도를 DXF로 export. 디자인의 각 시트가 자체 파일로 출력.
- **Usage:** `kicad-cli sch export dxf [--help] [--output OUTPUT_DIR] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--variant VAR] [--theme THEME_NAME] [--black-and-white] [--exclude-drawing-sheet] [--default-font VAR] [--draw-hop-over] [--pages PAGE_LIST] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 회로도 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | DXF export 도움말. |
| `-o <output dir>` | `--output <output dir>` | 출력 폴더. 시트당 파일 1개. 미사용 시 현재 디렉토리. |
|  | `--drawing-sheet <sheet path>` | 회로도 파일 지정 도면 시트 덮어쓸 경로. |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |
| `-t <theme name>` | `--theme <theme name>` | 사용할 테마. 미지정 시 회로도 에디터 현재 테마. |
| `-b` | `--black-and-white` | 흑백 export. |
| `-e` | `--exclude-drawing-sheet` | 도면 시트 없이 DXF 플롯. |
|  | `--default-font <font name>` | 기본 폰트명. 기본 `"KiCad Font"`. |
|  | `--draw-hop-over` | 와이어 교차점에 hop-over 그림. |
|  | `--pages <page list>` | export할 페이지 쉼표 목록. 공백/미지정=전 페이지. 특정 페이지 플롯 시 루트 시트를 `INPUT_FILE`로 주고 `--pages` 지정. |

### Schematic export: HPGL · #schematic_export_hpgl

- ⚠️ **NOTE:** `kicad-cli sch export hpgl`는 KiCad 10.0에서 **비활성(non-functional)**. KiCad는 HPGL 출력을 더 이상 지원하지 않음. 호환성 목적 비기능 명령으로 포함, 향후 제거 예정.
- **Usage:** `kicad-cli sch export hpgl [--help] [--output OUTPUT_DIR] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--variant VAR] [--theme THEME_NAME] [--black-and-white] [--exclude-drawing-sheet] [--default-font VAR] [--draw-hop-over] [--pages PAGE_LIST] [--pen-size PEN_SIZE] [--origin ORIGIN] INPUT_FILE`

### Schematic export: netlist · #schematic_export_netlist

- **용도:** `sch export netlist` — 회로도에서 다양한 포맷의 넷리스트 export. (kicad-analyze 스킬 핵심 명령)
- **Usage:** `kicad-cli sch export netlist [--help] [--output OUTPUT_FILE] [--variant VAR] [--format FORMAT] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 회로도 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | netlist export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `.net`. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |
|  | `--format <format>` | 넷리스트 출력 포맷. `kicadsexpr`(기본), `kicadxml`, `cadstar`, `orcadpcb2`, `spice`, `spicemodel`, `pads`, `allegro`. |

### Schematic export: PDF · #schematic_export_pdf

- **용도:** `sch export pdf` — 회로도를 PDF로 export. 각 시트가 PDF의 자체 페이지로 출력.
- **Usage:** `kicad-cli sch export pdf [--help] [--output OUTPUT_FILE] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--variant VAR] [--theme THEME_NAME] [--black-and-white] [--exclude-drawing-sheet] [--default-font VAR] [--draw-hop-over] [--exclude-pdf-property-popups] [--exclude-pdf-hierarchical-links] [--exclude-pdf-metadata] [--no-background-color] [--pages PAGE_LIST] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 회로도 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | PDF export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `.pdf`. |
|  | `--drawing-sheet <sheet path>` | 도면 시트 경로(덮어씀). |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |
| `-t <theme name>` | `--theme <theme name>` | 사용할 테마. 미지정 시 회로도 에디터 현재 테마. |
| `-b` | `--black-and-white` | 흑백 export. |
| `-e` | `--exclude-drawing-sheet` | 도면 시트 없이 PDF 플롯. |
|  | `--default-font <font name>` | 기본 폰트명. 기본 `"KiCad Font"`. |
|  | `--draw-hop-over` | 와이어 교차점에 hop-over 그림. |
|  | `--exclude-pdf-property-popups` | PDF에 property 팝업 미생성. |
|  | `--exclude-pdf-hierarchical-links` | PDF에 계층 요소 클릭 링크 미생성. |
|  | `--exclude-pdf-metadata` | AUTHOR·SUBJECT 변수로부터 PDF 메타데이터 미생성. |
| `-n` | `--no-background-color` | 테마와 무관하게 배경색 없이 export. |
|  | `--pages <page list>` | export할 페이지 쉼표 목록. 공백/미지정=전 페이지. 특정 페이지 시 루트 시트를 `INPUT_FILE`로. |

### Schematic export: PostScript · #schematic_export_postscript

- **용도:** `sch export ps` — 회로도를 PostScript로 export. 각 시트가 자체 파일로 출력.
- **Usage:** `kicad-cli sch export ps [--help] [--output OUTPUT_DIR] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--variant VAR] [--theme THEME_NAME] [--black-and-white] [--exclude-drawing-sheet] [--default-font VAR] [--draw-hop-over] [--no-background-color] [--pages PAGE_LIST] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 회로도 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | PS export 도움말. |
| `-o <output dir>` | `--output <output dir>` | 출력 폴더. 시트당 파일 1개. 미사용 시 현재 디렉토리. |
|  | `--drawing-sheet <sheet path>` | 도면 시트 경로(덮어씀). |
| `-D <name>=<value>` | `--define-var <name>=<value>` | 프로젝트 변수 정의 추가/재정의. |
|  | `--variant <name>` | 출력 variant 이름. `${VARIANT}` 지원. |
| `-t <theme name>` | `--theme <theme name>` | 사용할 테마. 미지정 시 회로도 에디터 현재 테마. |
| `-b` | `--black-and-white` | 흑백 export. |
| `-e` | `--exclude-drawing-sheet` | 도면 시트 없이 PS 플롯. |
|  | `--default-font <font name>` | 기본 폰트명. 기본 `"KiCad Font"`. |
|  | `--draw-hop-over` | 와이어 교차점에 hop-over 그림. |
| `-n` | `--no-background-color` | 테마 무관 배경색 없이 export. |
|  | `--pages <page list>` | export할 페이지 쉼표 목록. 공백/미지정=전 페이지. |

### Schematic export: bill of materials (legacy BOM scripts) · #schematic_export_bill_of_materials_legacy_bom_scripts

- **용도:** `sch export python-bom` — 회로도에서 XML BOM 파일 export. 이후 커스텀 스크립트나 회로도 BOM export 문서에 설명된 스크립트로 원하는 BOM 포맷으로 처리.
- **Usage:** `kicad-cli sch export python-bom [--help] [--output OUTPUT_FILE] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 회로도 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | BOM export 도움말. |
| `-o <output filename>` | `--output <output filename>` | 출력 파일명. 미사용 시 입력 파일명 + `-bom.xml`. |

### Schematic export: SVG · #schematic_export_svg

- **용도:** `sch export svg` — 회로도를 SVG로 export. 각 시트가 자체 파일로 출력.
- **Usage:** `kicad-cli sch export svg [--help] [--output OUTPUT_DIR] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--variant VAR] [--theme THEME_NAME] [--black-and-white] [--exclude-drawing-sheet] [--default-font VAR] [--draw-hop-over] [--no-background-color] [--pages PAGE_LIST] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export할 회로도 파일.
- **옵션:** `sch export ps`와 동일한 옵션 세트(`-h`, `-o <output dir>`(미사용 시 현재 디렉토리), `--drawing-sheet`, `-D`, `--variant`, `-t/--theme`, `-b/--black-and-white`, `-e/--exclude-drawing-sheet`, `--default-font`(기본 `"KiCad Font"`), `--draw-hop-over`, `-n/--no-background-color`, `--pages`).

### Schematic upgrade · #schematic_upgrade

- **용도:** `sch upgrade` — 이전 KiCad 회로도 포맷을 현재 네이티브 포맷으로 변환. 이미 현재 포맷이면 무작업.
- ⚠️ **NOTE:** 지정된 회로도 파일만 업그레이드됨. 자식 시트가 있어도 자식 시트는 업그레이드되지 않음.
- **Usage:** `kicad-cli sch upgrade [--help] [--force] INPUT_FILE`
- **Positional:** `INPUT_FILE` — 업그레이드할 회로도 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | upgrade 도움말. |
|  | `--force` | 이미 현재 포맷이어도 입력 회로도 파일 재저장. |

---

## Symbol commands · #symbol

- `sym` 서브커맨드: 심볼을 다른 포맷으로 export 하거나 심볼 라이브러리를 현재 KiCad 심볼 파일 포맷으로 업그레이드.

### Symbol export · #symbol_export

- **용도:** `sym export svg` — 지정 라이브러리의 심볼 하나/여럿을 SVG 파일로 export.
- **Usage:** `kicad-cli sym export svg [--help] [--output OUTPUT_DIR] [--theme THEME_NAME] [--symbol SYMBOL] [--black-and-white] [--include-hidden-pins] [--include-hidden-fields] INPUT_FILE`
- **Positional:** `INPUT_FILE` — export에 사용할 심볼 라이브러리 파일.

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | 심볼 SVG export 도움말. |
| `-o <output dir>` | `--output <output dir>` | 출력 폴더. 입력 라이브러리의 각 심볼이 별도 파일로 출력. 미사용 시 현재 디렉토리. |
| `-t <theme name>` | `--theme <theme name>` | 사용할 테마. 미지정 시 심볼 에디터 현재 테마. |
| `-s <symbol name>` | `--symbol <symbol name>` | export할 특정 심볼. 미사용 시 전 심볼 export. |
|  | `--black-and-white` | 흑백 export. |
|  | `--include-hidden-pins` | 숨겨진 핀을 SVG에 export. |
|  | `--include-hidden-fields` | 숨겨진 심볼 필드를 SVG에 export. |

### Symbol upgrade · #symbol_upgrade

- **용도:** `sym upgrade` — 지정 심볼 라이브러리를 레거시 KiCad/비-KiCad 포맷에서 현재 KiCad 네이티브 포맷으로 변환. 이미 현재 포맷이면 무작업.
- **지원 입력 포맷:** KiCad(`.kicad_sym`), KiCad pre-6.0(`.lib`), Altium 회로도(`.SchLib`), Altium 통합(`.IntLib`), CADSTAR parts(`.lib`), EAGLE XML(`.lbr`), EasyEDA(JLCEDA) Std(`.json`), EasyEDA(JLCEDA) Pro(`.elibz`, `.epro`, `.zip`).
- **Usage:** `kicad-cli sym upgrade [--help] [--output OUTPUT_FILE_OR_DIR] [--force] INPUT_FILE_OR_DIR`
- **Positional:** `INPUT_FILE_OR_DIR` — 업그레이드할 심볼/라이브러리. unpacked 심볼(`.kicad_sym` 단일 심볼), unpacked 라이브러리(`.kicad_sym` 파일 든 폴더), 또는 packed 라이브러리(`.kicad_sym` 다중 심볼).

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | upgrade 도움말. |
| `-o <output file or dir>` | `--output <output file or dir>` | 업그레이드된 심볼 라이브러리 출력. 출력 경로가 파일이면 단일 파일("packed") `.kicad_sym`로 저장, 폴더면 심볼당 1파일("unpacked")로 저장. 미사용 시 원본 라이브러리에 덮어쓰기. |
|  | `--force` | 이미 현재 포맷이어도 입력 라이브러리 재저장. |

---

## Version commands · #version

- **용도:** `version` — KiCad 버전 출력. 인자 없이 실행하면 버전 번호만 출력(예 `7.0.7`). `--format`으로 여러 형식 가능.
- ⚠️ **NOTE:** Gitlab에 버그 리포트/기능 요청 제출 시 포함할 버전 정보는 `kicad-cli version --format about`로 확인.
- **Usage:** `kicad-cli version [--help] [--format VAR]`

| 짧은 플래그 | 긴 플래그 | 설명 |
| --- | --- | --- |
| `-h` | `--help` | version 도움말. |
|  | `--format <format>` | 버전 번호 형식. `plain`(기본, 예 `7.0.7`), `commit`(빌드 git 커밋 해시), `about`(라이브러리 버전·기본 시스템 정보 포함 전체 정보 — 버그 리포트용). |
