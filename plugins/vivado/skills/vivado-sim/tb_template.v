`timescale 1ns / 1ps

module tb_MODULE_NAME;

    // =========================================
    // Parameters
    // =========================================
    parameter CLK_PERIOD = 10; // 100MHz

    // =========================================
    // Signals
    // =========================================
    reg         clk;
    reg         rst_n;
    // TODO: DUT 포트에 맞게 추가
    // reg  [7:0]  data_in;
    // wire [7:0]  data_out;
    // wire        valid;

    // =========================================
    // Clock Generation
    // =========================================
    initial clk = 0;
    always #(CLK_PERIOD/2) clk = ~clk;

    // =========================================
    // DUT Instantiation
    // =========================================
    MODULE_NAME #(
        // .PARAM_NAME (VALUE)
    ) dut (
        .clk    (clk),
        .rst_n  (rst_n)
        // TODO: 포트 연결
    );

    // =========================================
    // Waveform Dump
    // =========================================
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_MODULE_NAME);
    end

    // =========================================
    // Test Sequence
    // =========================================
    integer pass_count = 0;
    integer fail_count = 0;

    task check(input logic expected, input logic actual, input string msg);
        if (expected === actual) begin
            pass_count = pass_count + 1;
        end else begin
            fail_count = fail_count + 1;
            $display("FAIL: %s — expected %0b, got %0b at time %0t", msg, expected, actual, $time);
        end
    endtask

    initial begin
        // Reset
        rst_n = 0;
        repeat(10) @(posedge clk);
        rst_n = 1;
        repeat(5) @(posedge clk);

        // ---- Test Case 1 ----
        $display("--- Test Case 1: Basic Operation ---");
        // TODO: 테스트 시퀀스 작성
        repeat(10) @(posedge clk);

        // ---- Test Case 2 ----
        $display("--- Test Case 2: Edge Case ---");
        // TODO: 엣지 케이스 테스트
        repeat(10) @(posedge clk);

        // ---- Summary ----
        $display("========================================");
        if (fail_count == 0)
            $display("PASS: All %0d tests passed", pass_count);
        else
            $display("FAIL: %0d passed, %0d failed", pass_count, fail_count);
        $display("========================================");

        $finish;
    end

    // =========================================
    // Timeout Watchdog
    // =========================================
    initial begin
        #(CLK_PERIOD * 100000);
        $display("FAIL: Simulation timeout!");
        $finish;
    end

endmodule
