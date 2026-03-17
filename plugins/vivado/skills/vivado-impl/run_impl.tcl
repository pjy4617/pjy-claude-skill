# ==============================================================
# Vivado Implementation Script (Non-Project Mode)
# Usage: vivado -mode batch -source run_impl.tcl
# Requires: checkpoints/post_synth.dcp from synthesis
# ==============================================================

set OUT_DIR "."

# --- Create output directories ---
file mkdir ${OUT_DIR}/reports
file mkdir ${OUT_DIR}/checkpoints

# --- Load synthesis checkpoint ---
set synth_dcp "${OUT_DIR}/checkpoints/post_synth.dcp"
if {![file exists ${synth_dcp}]} {
    puts "ERROR: Synthesis checkpoint not found: ${synth_dcp}"
    puts "  Run synthesis first (run_synth.tcl)"
    exit 1
}

puts "=== Loading Synthesis Checkpoint ==="
open_checkpoint ${synth_dcp}

# --- Logic Optimization ---
puts "=== Running Optimization ==="
if {[catch {opt_design} errmsg]} {
    puts "ERROR: Optimization failed - $errmsg"
    exit 1
}

# --- Place ---
puts "=== Running Placement ==="
if {[catch {place_design} errmsg]} {
    puts "ERROR: Placement failed - $errmsg"
    exit 1
}
write_checkpoint -force ${OUT_DIR}/checkpoints/post_place.dcp
report_timing_summary -file ${OUT_DIR}/reports/timing_place.rpt

# --- Physical Optimization (improves timing) ---
puts "=== Running Physical Optimization ==="
if {[catch {phys_opt_design} errmsg]} {
    puts "WARNING: Physical optimization failed - $errmsg"
    puts "  Continuing with routing..."
}

# --- Route ---
puts "=== Running Routing ==="
if {[catch {route_design} errmsg]} {
    puts "ERROR: Routing failed - $errmsg"
    exit 1
}
write_checkpoint -force ${OUT_DIR}/checkpoints/post_route.dcp

# --- Final Reports ---
puts "=== Generating Reports ==="
report_timing_summary -file ${OUT_DIR}/reports/timing_route.rpt
report_utilization    -file ${OUT_DIR}/reports/utilization_route.rpt
report_power          -file ${OUT_DIR}/reports/power_route.rpt
report_drc            -file ${OUT_DIR}/reports/drc_route.rpt

# --- Print Summary ---
puts "=== Implementation Summary ==="
puts "Reports: ${OUT_DIR}/reports/"
puts "Checkpoint: ${OUT_DIR}/checkpoints/post_route.dcp"

# --- Check final timing (Setup + Hold) ---
set wns [get_property SLACK [get_timing_paths -max_paths 1 -setup]]
set whs [get_property SLACK [get_timing_paths -max_paths 1 -hold]]

if {$wns < 0} {
    puts "CRITICAL: Setup timing NOT met after routing! WNS = ${wns} ns"
    puts "  Consider: phys_opt_design iterations or RTL pipeline insertion"
} else {
    puts "OK: Setup timing met. WNS = ${wns} ns"
}

if {$whs < 0} {
    puts "CRITICAL: Hold timing NOT met after routing! WHS = ${whs} ns"
    puts "  Consider: Check clock constraints and I/O delays"
} else {
    puts "OK: Hold timing met. WHS = ${whs} ns"
}
