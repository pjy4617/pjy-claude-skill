#!/bin/bash
# ==============================================================
# Vivado GUI 열기 (하이브리드 모드 헬퍼)
# ==============================================================
# Usage:
#   ./scripts/open_gui.sh synth      # 합성 결과 GUI로 열기
#   ./scripts/open_gui.sh place      # 배치 결과 GUI로 열기
#   ./scripts/open_gui.sh route      # 라우팅 결과 GUI로 열기
#   ./scripts/open_gui.sh wave       # 시뮬레이션 파형 열기
#   ./scripts/open_gui.sh hw         # Hardware Manager 열기
# ==============================================================

STAGE=${1:-route}

case $STAGE in
    synth)
        DCP="build/checkpoints/post_synth.dcp"
        if [ -f "$DCP" ]; then
            echo "Opening synthesis checkpoint in GUI..."
            echo "  → Schematic View, Utilization Report"
            vivado $DCP &
        else
            echo "ERROR: $DCP not found. Run synthesis first."
            exit 1
        fi
        ;;
    place)
        DCP="build/checkpoints/post_place.dcp"
        if [ -f "$DCP" ]; then
            echo "Opening placement checkpoint in GUI..."
            echo "  → Device View, Clock Regions"
            vivado $DCP &
        else
            echo "ERROR: $DCP not found. Run implementation first."
            exit 1
        fi
        ;;
    route)
        DCP="build/checkpoints/post_route.dcp"
        if [ -f "$DCP" ]; then
            echo "Opening routed checkpoint in GUI..."
            echo "  → Routing, Critical Path, Power Report"
            vivado $DCP &
        else
            echo "ERROR: $DCP not found. Run implementation first."
            exit 1
        fi
        ;;
    wave|waveform|sim)
        WDB_COUNT=$(find build/ -name "*.wdb" 2>/dev/null | wc -l)
        VCD_COUNT=$(find build/ -name "*.vcd" 2>/dev/null | wc -l)
        if [ "$WDB_COUNT" -gt 0 ]; then
            echo "Opening waveform in Vivado (auto-detect)..."
            vivado -mode gui -source scripts/open_waveform.tcl &
        elif [ "$VCD_COUNT" -gt 0 ]; then
            VCD=$(find build/ -name "*.vcd" -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2)
            if command -v gtkwave &> /dev/null; then
                echo "Opening waveform in GTKWave: $VCD"
                gtkwave "$VCD" &
            else
                echo "VCD file exists at $VCD but GTKWave not installed."
                echo "Install: sudo apt install gtkwave"
                exit 1
            fi
        else
            echo "ERROR: No waveform file (.wdb or .vcd) found in build/."
            echo "Run simulation first."
            exit 1
        fi
        ;;
    hw|hardware|program)
        echo "Opening Hardware Manager..."
        echo "  → Program Device, ILA, VIO"
        vivado -mode gui -source scripts/open_hw_manager.tcl &
        ;;
    *)
        echo "Usage: $0 {synth|place|route|wave|hw}"
        echo ""
        echo "  synth  - Open synthesis checkpoint (Schematic, Utilization)"
        echo "  place  - Open placement checkpoint (Device View)"
        echo "  route  - Open routed checkpoint (Routing, Timing)"
        echo "  wave   - Open simulation waveform (WDB or VCD)"
        echo "  hw     - Open Hardware Manager (Program, ILA, VIO)"
        exit 1
        ;;
esac

echo "GUI launched in background (PID: $!)"
