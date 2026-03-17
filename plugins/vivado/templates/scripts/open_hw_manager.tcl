# ==============================================================
# Open Hardware Manager in Vivado GUI
# Usage: vivado -mode gui -source open_hw_manager.tcl
# ==============================================================

open_hw_manager
connect_hw_server
open_hw_target

puts "=== Hardware Manager Connected ==="
puts "Available devices:"
foreach dev [get_hw_devices] {
    puts "  - $dev"
}
puts ""
puts "Use GUI to: Program Device, Open ILA, VIO Console"
