---
name: vivado-synth
description: Vivado 합성(Synthesis) 실행 시 사용. "합성해줘", "synth", "합성 돌려", "synthesis", "리소스 사용량", "스키매틱", "schematic" 등의 요청에 자동 적용.
---

# Vivado 합성 (Synthesis) — 하이브리드 모드

> 기본: CLI batch로 합성 → 스키매틱/리포트 확인 필요 시 GUI 전환
> 요구: Vivado 2020.1+ (vivado -mode batch)

## CLI 실행 (기본)

### 1. TCL 스크립트 실행
```bash
cd build

# 기본 실행 (arty_a7 보드, top 모듈)
vivado -mode batch -source ../scripts/run_synth.tcl -log logs/synth.log -journal logs/synth.jou

# 보드/모듈 지정 실행 (환경 변수)
BOARD=zedboard TOP=top PART_NUM=xc7z020clg484-1 \
  vivado -mode batch -source ../scripts/run_synth.tcl -log logs/synth.log -journal logs/synth.jou
```

### 2. 환경 변수
| 변수 | 기본값 | 설명 |
|------|--------|------|
| `BOARD` | `arty_a7` | 보드 이름 → `constraints/{BOARD}.xdc` 자동 결정 |
| `TOP` | `top` | 톱 모듈 이름 |
| `PART_NUM` | `xc7a35ticsg324-1L` | FPGA 파트넘버 (boards.json 참조) |

### 3. TCL 스크립트 구조 (`run_synth.tcl` 참조)
```tcl
# 1) 타겟 디바이스 설정 (환경 변수 또는 기본값)
set PART [expr {[info exists env(PART_NUM)] ? $env(PART_NUM) : "xc7a35ticsg324-1L"}]

# 2) 소스 읽기 (Verilog + SystemVerilog 자동 감지)
foreach f [glob ${RTL_DIR}/*.v]  { read_verilog $f }
foreach f [glob -nocomplain ${RTL_DIR}/*.sv] { read_verilog -sv $f }

# 3) 제약 조건 읽기 (BOARD 환경 변수로 경로 결정)
read_xdc ../constraints/${BOARD}.xdc

# 4) 합성 실행 (에러 핸들링 포함)
if {[catch {synth_design -top $TOP -part $PART} errmsg]} {
    puts "ERROR: Synthesis failed - $errmsg"
    exit 1
}

# 5) 리포트 생성 + 체크포인트 저장
report_timing_summary -file reports/timing_synth.rpt
report_utilization -file reports/utilization_synth.rpt
write_checkpoint -force checkpoints/post_synth.dcp

# 6) Setup + Hold 타이밍 체크
set wns [get_property SLACK [get_timing_paths -max_paths 1 -setup]]
set whs [get_property SLACK [get_timing_paths -max_paths 1 -hold]]
```
> glob 패턴으로 `.v`와 `.sv`를 모두 포함하므로 새 모듈 추가 시 TCL 수정이 불필요합니다.

### 4. 결과 확인 (반드시 수행)
```bash
# 타이밍 위반 확인 (Setup + Hold)
grep "WNS" build/reports/timing_synth.rpt
grep "WHS" build/reports/timing_synth.rpt

# 리소스 사용량 확인
grep -A 20 "Slice Logic" build/reports/utilization_synth.rpt

# 에러/경고 확인
grep -c "ERROR" build/logs/synth.log
grep -c "CRITICAL WARNING" build/logs/synth.log
```

## GUI 전환: 스키매틱 / 리포트 시각화

사용자가 "스키매틱 보여줘", "합성 결과 열어", "GUI로 확인" 등을 요청하면 체크포인트를 GUI로 연다.

### 합성 결과를 GUI로 열기
```bash
# 체크포인트를 GUI에서 열기 (프로젝트 파일 불필요)
vivado build/checkpoints/post_synth.dcp &
```
GUI에서 할 수 있는 일:
- **Schematic View**: 합성된 넷리스트를 회로도로 확인
- **Report Timing Summary**: 타이밍 경로를 시각적으로 추적
- **Report Utilization**: 리소스 사용량 파이차트
- **Hierarchy Browser**: 모듈 계층 탐색

### 특정 리포트만 GUI로 열기
```tcl
# TCL에서 GUI 모드로 전환하여 리포트만 확인
open_checkpoint build/checkpoints/post_synth.dcp
start_gui
# GUI에서 Report → Timing Summary 등 선택
```

## 합성 옵션 (자주 사용)
| 옵션 | 용도 |
|------|------|
| `-flatten_hierarchy rebuilt` | 계층 평탄화 후 재구성 (기본값) |
| `-flatten_hierarchy none` | 계층 유지 (디버그 용이, GUI 스키매틱에서 계층 보존) |
| `-retiming` | 레지스터 리타이밍으로 타이밍 개선 |
| `-fsm_extraction auto` | FSM 자동 인식 및 최적화 |
| `-max_dsp 0` | DSP 블록 사용 금지 (순수 로직) |
| `-max_bram 0` | BRAM 사용 금지 |

## 트러블슈팅
| 에러/경고 | 원인 | 해결 |
|-----------|------|------|
| `WNS < 0` (타이밍 위반) | 클럭 속도 대비 로직 깊이 초과 | 파이프라인 추가 또는 클럭 제약 완화 |
| `Inferred latch` | always 블록에서 모든 조건 미커버 | default/else 추가 |
| `Multi-driven net` | 여러 소스가 같은 와이어 구동 | 드라이버 하나로 통합 |
| `Unconnected port` | 인스턴스 포트 미연결 | 포트 매핑 확인 |
| `Black box` | 모듈 정의 없음 | `read_verilog` 누락 확인 |
| GUI 열렸는데 빈 화면 | DCP 경로 오류 | `ls build/checkpoints/` 확인 |
