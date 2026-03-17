## ============================================================
## Arty A7 — UART TX Example Constraints
## ============================================================

## Clock (100 MHz)
set_property -dict { PACKAGE_PIN E3  IOSTANDARD LVCMOS33 } [get_ports clk]
create_clock -period 10.000 -name sys_clk [get_ports clk]

## Reset (active low, Button 0)
set_property -dict { PACKAGE_PIN D9  IOSTANDARD LVCMOS33 } [get_ports rst_n]

## UART TX (USB-UART, directly to FT2232H)
set_property -dict { PACKAGE_PIN D10 IOSTANDARD LVCMOS33 } [get_ports tx_out]

## ============================================================
## Timing Constraints
## ============================================================
set_false_path -from [get_ports rst_n]
