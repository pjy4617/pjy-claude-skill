# Vivado HDL Project

## 최소 요구 버전
- AMD Vivado: 2020.1 이상 (CLI batch 모드 지원)
- KiCad: 8.0 이상 (kicad-cli 지원, KiCad→XDC 사용 시만 필요, 선택 사항)
- Python: 3.6 이상 (XDC 생성 스크립트용)
- OS: Linux (Ubuntu 20.04+, WSL2 포함)

## 워크플로우: 하이브리드 모드
- **빌드(90%)**: CLI batch 모드 — Claude Code가 TCL 스크립트로 자동 실행
- **시각적 확인(10%)**: GUI — 체크포인트(.dcp)를 열어 확인만
- GUI에서 디자인을 수정하지 않는다. 수정은 항상 RTL/XDC에서 한다
- 프로젝트 파일(.xpr) 없이 Non-Project 모드 사용

## 환경
- OS: Linux (Ubuntu/WSL)
- Tool: AMD Vivado (CLI batch 기본, 필요 시 GUI 전환)
- Language: Verilog HDL / SystemVerilog (.v, .sv 모두 지원)
- 타겟: 여러 FPGA 보드 (보드별 XDC 제약 파일 분리)
- 회로 설계: KiCad (선택 — KiCad 회로도가 있으면 XDC 자동 생성 가능)

## 디렉터리 규칙
- `rtl/` — Verilog 소스 (.v)
- `tb/` — 테스트벤치 (.v), 파일명은 `tb_모듈명.v`
- `constraints/` — 보드별 XDC 파일
- `scripts/` — Vivado TCL 스크립트 + GUI 헬퍼 스크립트
- `build/` — 빌드 출력 (git에 포함하지 않음)
  - `build/checkpoints/` — DCP 체크포인트 (GUI에서 열 수 있음)
  - `build/reports/` — 타이밍, 리소스, 전력 리포트
  - `build/output/` — 비트스트림 (.bit, .mcs)
  - `build/logs/` — 로그, 저널 파일
  - `build/netlist.xml` — KiCad 넷리스트 (XDC 생성 시 임시)
- `*.kicad_sch`, `*.kicad_pro` — KiCad 프로젝트 파일 (있으면)

## GUI 전환 규칙
사용자가 아래 키워드를 말하면 해당 체크포인트를 GUI로 연다:
- "파형 보여줘" / "waveform" → xsim GUI 또는 GTKWave
- "스키매틱" / "schematic" → post_synth.dcp GUI
- "배치 확인" / "Device View" → post_place.dcp GUI
- "라우팅 결과" / "타이밍 경로" → post_route.dcp GUI
- "ILA" / "Hardware Manager" → HW Manager GUI
- GUI 열기: `./scripts/open_gui.sh {synth|place|route|wave|hw}`

## Vivado CLI 사용법
- GUI 대신 항상 `vivado -mode batch -source script.tcl` 사용
- Non-Project 모드 (프로젝트 파일 없음)
- 로그는 `build/logs/`에 저장
- 체크포인트는 `build/checkpoints/`에 저장

## KiCad 연동 (선택 사항)
- KiCad 회로도가 있으면 → kicad-xdc-gen 에이전트가 XDC 자동 생성
- KiCad 회로도가 없으면 → rtl-designer가 XDC 수동 작성
- KiCad 회로 리뷰: kicad-review 스킬로 ERC/DRC/BOM 종합 검토
- kicad-cli 확인: `which kicad-cli && kicad-cli --version`

## 코딩 규칙
- 모듈명은 snake_case
- 클럭: `clk`, 리셋: `rst_n` (active low)
- 파라미터로 데이터 폭 등 설정 가능하게 설계
- 동기식 리셋 권장 (비동기 리셋도 Xilinx에서 합성 가능하나 동기식 선호)
- assign 문 최소화, always 블록 선호

## 보드 설정
- 보드 변경 시 `.claude/skills/vivado-project/boards.json` 참조
- boards.json에 파트넘버, 클럭, bank_vcco(뱅크 전압) 포함
- XDC 파일은 `constraints/보드명.xdc`에 위치

## Vivado CLI 환경 변수
빌드 스크립트는 환경 변수로 보드/모듈을 설정합니다:
- `BOARD` — 보드 이름 (기본: arty_a7) → `constraints/{BOARD}.xdc` 자동 결정
- `TOP` — 톱 모듈 이름 (기본: top)
- `PART_NUM` — FPGA 파트넘버 (기본: xc7a35ticsg324-1L)

## 에이전트/스킬 구성 (6 에이전트 + 12 스킬)
- 에이전트: rtl-designer, rtl-reviewer, tb-reviewer, pin-reviewer, timing-analyst, kicad-xdc-gen
- 빌드 스킬: vivado-project, vivado-sim, vivado-synth, vivado-impl, vivado-bitstream, vivado-build-all, vivado-gui
- 리뷰 스킬: rtl-review, tb-review, pin-review, kicad-xdc, kicad-review
