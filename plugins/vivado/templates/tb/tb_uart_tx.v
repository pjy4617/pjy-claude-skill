`timescale 1ns / 1ps

module tb_uart_tx;

    // =========================================
    // Parameters
    // =========================================
    parameter CLK_PERIOD    = 10;   // 100MHz
    parameter CLKS_PER_BIT  = 8;    // 시뮬레이션용 (실제는 868)
    parameter BIT_PERIOD    = CLK_PERIOD * CLKS_PER_BIT;

    // =========================================
    // Signals
    // =========================================
    reg         clk;
    reg         rst_n;
    reg  [7:0]  tx_data;
    reg         tx_valid;
    wire        tx_ready;
    wire        tx_out;
    wire        tx_done;

    // =========================================
    // Clock Generation
    // =========================================
    initial clk = 0;
    always #(CLK_PERIOD/2) clk = ~clk;

    // =========================================
    // DUT Instantiation
    // =========================================
    uart_tx #(
        .CLKS_PER_BIT (CLKS_PER_BIT)
    ) dut (
        .clk      (clk),
        .rst_n    (rst_n),
        .tx_data  (tx_data),
        .tx_valid (tx_valid),
        .tx_ready (tx_ready),
        .tx_out   (tx_out),
        .tx_done  (tx_done)
    );

    // =========================================
    // Waveform Dump
    // =========================================
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_uart_tx);
    end

    // =========================================
    // UART Bit Capture Task
    // =========================================
    // tx_out에서 전송된 바이트를 캡처하는 태스크
    reg [7:0] captured_byte;

    task capture_uart_byte;
        integer i;
        begin
            // Start bit 대기 (tx_out falling edge)
            @(negedge tx_out);
            
            // Start bit 중앙으로 이동
            #(BIT_PERIOD / 2);
            
            // Start bit 확인
            if (tx_out !== 1'b0) begin
                $display("FAIL: Start bit is not 0 at time %0t", $time);
            end

            // 8 data bits 캡처 (LSB first)
            for (i = 0; i < 8; i = i + 1) begin
                #(BIT_PERIOD);
                captured_byte[i] = tx_out;
            end

            // Stop bit 확인
            #(BIT_PERIOD);
            if (tx_out !== 1'b1) begin
                $display("FAIL: Stop bit is not 1 at time %0t", $time);
            end
        end
    endtask

    // =========================================
    // Test Sequence
    // =========================================
    integer pass_count = 0;
    integer fail_count = 0;

    task send_byte(input [7:0] data);
        begin
            @(posedge clk);
            tx_data  = data;
            tx_valid = 1'b1;
            @(posedge clk);
            tx_valid = 1'b0;
        end
    endtask

    task check_byte(input [7:0] expected, input [7:0] actual, input [159:0] msg);
        begin
            if (expected === actual) begin
                pass_count = pass_count + 1;
                $display("PASS: %0s — sent 0x%02h, captured 0x%02h", msg, expected, actual);
            end else begin
                fail_count = fail_count + 1;
                $display("FAIL: %0s — expected 0x%02h, got 0x%02h at time %0t", msg, expected, actual, $time);
            end
        end
    endtask

    initial begin
        // ---- Initialize ----
        rst_n    = 0;
        tx_data  = 8'h00;
        tx_valid = 0;
        repeat(10) @(posedge clk);
        rst_n = 1;
        repeat(5) @(posedge clk);

        // ---- Test 1: Send 0x55 (01010101) ----
        $display("");
        $display("--- Test 1: Send 0x55 ---");
        fork
            send_byte(8'h55);
            capture_uart_byte();
        join
        check_byte(8'h55, captured_byte, "Alternating bits");

        // tx_done 확인
        @(posedge tx_done);
        $display("  tx_done asserted OK");

        repeat(10) @(posedge clk);

        // ---- Test 2: Send 0xA3 (10100011) ----
        $display("");
        $display("--- Test 2: Send 0xA3 ---");
        fork
            send_byte(8'hA3);
            capture_uart_byte();
        join
        check_byte(8'hA3, captured_byte, "Mixed pattern");

        repeat(10) @(posedge clk);

        // ---- Test 3: Send 0x00 (all zeros) ----
        $display("");
        $display("--- Test 3: Send 0x00 ---");
        fork
            send_byte(8'h00);
            capture_uart_byte();
        join
        check_byte(8'h00, captured_byte, "All zeros");

        repeat(10) @(posedge clk);

        // ---- Test 4: Send 0xFF (all ones) ----
        $display("");
        $display("--- Test 4: Send 0xFF ---");
        fork
            send_byte(8'hFF);
            capture_uart_byte();
        join
        check_byte(8'hFF, captured_byte, "All ones");

        repeat(10) @(posedge clk);

        // ---- Test 5: tx_ready handshake ----
        $display("");
        $display("--- Test 5: tx_ready handshake ---");
        if (tx_ready === 1'b1) begin
            pass_count = pass_count + 1;
            $display("PASS: tx_ready is high when idle");
        end else begin
            fail_count = fail_count + 1;
            $display("FAIL: tx_ready should be high when idle");
        end

        // 전송 중 tx_ready 확인
        fork
            begin
                send_byte(8'hAB);
                repeat(3) @(posedge clk);
                if (tx_ready === 1'b0) begin
                    pass_count = pass_count + 1;
                    $display("PASS: tx_ready is low during transmission");
                end else begin
                    fail_count = fail_count + 1;
                    $display("FAIL: tx_ready should be low during transmission");
                end
            end
            capture_uart_byte();
        join

        repeat(10) @(posedge clk);

        // ---- Summary ----
        $display("");
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
