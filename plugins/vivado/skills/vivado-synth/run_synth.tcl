# ==============================================================
# Vivado Synthesis Script (Non-Project Mode)
# Usage: vivado -mode batch -source run_synth.tcl
#
# 환경 변수:
#   BOARD    - 보드 이름 (예: arty_a7, zedboard). 미설정 시 기본값 사용
#   TOP      - 톱 모듈 이름. 미설정 시 "top"
#   PART_NUM - FPGA 파트넘버 직접 지정. 미설정 시 기본값 사용
# ==============================================================

# --- Configuration ---
set TOP_MODULE  [expr {[info exists env(TOP)]      ? $env(TOP)      : "top"}]
set PART        [expr {[info exists env(PART_NUM)]  ? $env(PART_NUM) : "xc7a35ticsg324-1L"}]
set RTL_DIR     "../rtl"
set OUT_DIR     "."

# --- 보드 기반 XDC 경로 결정 ---
if {[info exists env(BOARD)]} {
    set XDC_FILE "../constraints/$env(BOARD).xdc"
} else {
    set XDC_FILE "../constraints/arty_a7.xdc"
}

# --- Create output directories ---
file mkdir ${OUT_DIR}/reports
file mkdir ${OUT_DIR}/checkpoints
file mkdir ${OUT_DIR}/logs

# --- Read sources (Verilog + SystemVerilog) ---
set v_files  [glob -nocomplain ${RTL_DIR}/*.v]
set sv_files [glob -nocomplain ${RTL_DIR}/*.sv]

if {[llength $v_files] == 0 && [llength $sv_files] == 0} {
    puts "ERROR: No RTL source files found in ${RTL_DIR}/"
    exit 1
}

foreach f $v_files {
    puts "Reading Verilog: $f"
    read_verilog $f
}
foreach f $sv_files {
    puts "Reading SystemVerilog: $f"
    read_verilog -sv $f
}

# --- Read constraints ---
if {![file exists ${XDC_FILE}]} {
    puts "ERROR: XDC file not found: ${XDC_FILE}"
    exit 1
}
read_xdc ${XDC_FILE}

# --- Run Synthesis ---
puts "=== Starting Synthesis ==="
puts "  TOP: ${TOP_MODULE}, PART: ${PART}, XDC: ${XDC_FILE}"

if {[catch {synth_design -top ${TOP_MODULE} -part ${PART}} errmsg]} {
    puts "ERROR: Synthesis failed - $errmsg"
    exit 1
}
puts "=== Synthesis Complete ==="

# --- Generate Reports ---
report_timing_summary -file ${OUT_DIR}/reports/timing_synth.rpt
report_utilization    -file ${OUT_DIR}/reports/utilization_synth.rpt
report_drc            -file ${OUT_DIR}/reports/drc_synth.rpt

# --- Save Checkpoint ---
write_checkpoint -force ${OUT_DIR}/checkpoints/post_synth.dcp

# --- Print Summary ---
puts "=== Synthesis Summary ==="
puts "Reports: ${OUT_DIR}/reports/"
puts "Checkpoint: ${OUT_DIR}/checkpoints/post_synth.dcp"

# --- Check timing (Setup + Hold) ---
set wns [get_property SLACK [get_timing_paths -max_paths 1 -setup]]
set whs [get_property SLACK [get_timing_paths -max_paths 1 -hold]]

if {$wns < 0} {
    puts "WARNING: Setup timing violation! WNS = ${wns} ns"
} else {
    puts "OK: Setup timing met. WNS = ${wns} ns"
}

if {$whs < 0} {
    puts "WARNING: Hold timing violation! WHS = ${whs} ns"
} else {
    puts "OK: Hold timing met. WHS = ${whs} ns"
}
