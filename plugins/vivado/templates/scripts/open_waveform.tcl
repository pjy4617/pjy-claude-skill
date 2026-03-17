# ==============================================================
# Open Waveform Database in Vivado GUI
# Usage: vivado -mode gui -source open_waveform.tcl
# Automatically finds the most recent WDB file in build/
# ==============================================================

set wdb_files [glob -nocomplain build/*.wdb]

if {[llength $wdb_files] == 0} {
    puts "ERROR: No .wdb files found in build/"
    puts "Run simulation first with: xsim sim_snapshot -runall -wdb output.wdb"
} elseif {[llength $wdb_files] == 1} {
    set wdb [lindex $wdb_files 0]
    puts "Opening waveform: $wdb"
    open_wave_database $wdb
} else {
    # 여러 WDB 중 가장 최근 파일 선택
    set latest ""
    set latest_time 0
    foreach f $wdb_files {
        set mtime [file mtime $f]
        if {$mtime > $latest_time} {
            set latest_time $mtime
            set latest $f
        }
    }
    puts "Multiple WDB files found. Opening most recent: $latest"
    puts "All WDB files:"
    foreach f $wdb_files { puts "  $f" }
    open_wave_database $latest
}
