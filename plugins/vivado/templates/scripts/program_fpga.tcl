# ==============================================================
# Program FPGA via JTAG (batch mode)
# Usage: cd build && vivado -mode batch -source ../scripts/program_fpga.tcl
# ==============================================================

set BIT_FILE "output/top.bit"

if {![file exists $BIT_FILE]} {
    puts "ERROR: Bitstream not found: $BIT_FILE"
    puts "Run bitstream generation first."
    exit 1
}

open_hw_manager
connect_hw_server
open_hw_target

set device [lindex [get_hw_devices] 0]
puts "Programming device: $device"
puts "Bitstream: $BIT_FILE"

set_property PROGRAM.FILE $BIT_FILE $device
program_hw_devices $device

puts "=== Programming Complete ==="

close_hw_target
close_hw_server
close_hw_manager
