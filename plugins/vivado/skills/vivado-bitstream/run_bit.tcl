# ==============================================================
# Vivado Bitstream Script (Non-Project Mode)
# Usage: vivado -mode batch -source run_bit.tcl
# Requires: checkpoints/post_route.dcp from implementation
# ==============================================================

set OUT_DIR "."

# --- Create output directory ---
file mkdir ${OUT_DIR}/output
file mkdir ${OUT_DIR}/reports

# --- Load routed checkpoint ---
set route_dcp "${OUT_DIR}/checkpoints/post_route.dcp"
if {![file exists ${route_dcp}]} {
    puts "ERROR: Routed checkpoint not found: ${route_dcp}"
    puts "  Run implementation first (run_impl.tcl)"
    exit 1
}

puts "=== Loading Routed Checkpoint ==="
open_checkpoint ${route_dcp}

# --- Final DRC check ---
puts "=== Running Final DRC ==="
report_drc -file ${OUT_DIR}/reports/drc_final.rpt

# --- Bitstream options ---
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]

# --- Generate Bitstream ---
puts "=== Generating Bitstream ==="
if {[catch {write_bitstream -force ${OUT_DIR}/output/top.bit} errmsg]} {
    puts "ERROR: Bitstream generation failed - $errmsg"
    exit 1
}

# --- (Optional) Generate MCS for SPI Flash ---
# Uncomment and adjust for your board's flash:
# write_cfgmem -format mcs -interface SPIx4 \
#   -size 16 -loadbit "up 0x0 ${OUT_DIR}/output/top.bit" \
#   -force -file ${OUT_DIR}/output/top.mcs

# --- Summary ---
puts "=== Bitstream Generation Complete ==="
puts "Bitstream: ${OUT_DIR}/output/top.bit"

set bit_size [file size ${OUT_DIR}/output/top.bit]
puts "File size: ${bit_size} bytes"

if {$bit_size == 0} {
    puts "ERROR: Bitstream file is empty!"
    exit 1
} else {
    puts "OK: Bitstream generated successfully"
}
