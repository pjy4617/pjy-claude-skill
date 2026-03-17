#!/bin/bash
# ============================================================
# UART TX Simulation Script
# ============================================================
# vivado-sim 스킬이 실제로 실행하는 명령 시퀀스
#
# 사용법: cd build && bash ../scripts/run_sim.sh uart_tx
# ============================================================

MODULE=${1:-uart_tx}

echo "=== Step 1: Compile (xvlog) ==="
echo "  vivado-sim 스킬 → '1. 컴파일 (xvlog)' 섹션 참조"
xvlog ../rtl/${MODULE}.v ../tb/tb_${MODULE}.v
if [ $? -ne 0 ]; then
    echo "ERROR: Compilation failed"
    exit 1
fi

echo ""
echo "=== Step 2: Elaborate (xelab) ==="
echo "  vivado-sim 스킬 → '2. 엘라보레이션 (xelab)' 섹션 참조"
xelab -debug typical tb_${MODULE} -s sim_${MODULE}
if [ $? -ne 0 ]; then
    echo "ERROR: Elaboration failed"
    exit 1
fi

echo ""
echo "=== Step 3: Simulate (xsim) ==="
echo "  vivado-sim 스킬 → '3. 시뮬레이션 실행 (xsim)' 섹션 참조"
xsim sim_${MODULE} -runall -wdb ${MODULE}.wdb 2>&1 | tee xsim_${MODULE}.log
if [ $? -ne 0 ]; then
    echo "ERROR: Simulation failed"
    exit 1
fi

echo ""
echo "=== Step 4: Check Results ==="
echo "  vivado-sim 스킬 → '4. 결과 확인' 섹션 참조"
echo "--- PASS/FAIL Summary ---"
grep -E "(PASS|FAIL|ERROR)" xsim_${MODULE}.log

echo ""
PASS_CNT=$(grep -c "^PASS:" xsim_${MODULE}.log)
FAIL_CNT=$(grep -c "^FAIL:" xsim_${MODULE}.log)
echo "Results: ${PASS_CNT} passed, ${FAIL_CNT} failed"

if [ "$FAIL_CNT" -gt 0 ]; then
    echo "STATUS: SIMULATION FAILED"
    exit 1
else
    echo "STATUS: ALL TESTS PASSED"
fi
