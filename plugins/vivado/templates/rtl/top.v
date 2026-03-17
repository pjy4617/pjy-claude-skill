`timescale 1ns / 1ps

// ============================================================
// top — UART TX Demo Top Module (Arty A7)
// ============================================================
// Button press → sends a fixed byte via UART
// ============================================================

module top (
    input  wire clk,
    input  wire rst_n,
    output wire tx_out
);

    // =========================================
    // Internal Signals
    // =========================================
    wire       tx_ready;
    wire       tx_done;
    reg  [7:0] tx_data_r;
    reg        tx_valid_r;

    // =========================================
    // Simple: send 0x41 ('A') once after reset
    // =========================================
    reg sent_r;

    always @(posedge clk) begin
        if (!rst_n) begin
            tx_data_r  <= 8'h41;  // 'A'
            tx_valid_r <= 1'b0;
            sent_r     <= 1'b0;
        end else begin
            tx_valid_r <= 1'b0; // default

            if (!sent_r && tx_ready) begin
                tx_valid_r <= 1'b1;
                sent_r     <= 1'b1;
            end
        end
    end

    // =========================================
    // UART TX Instance
    // =========================================
    uart_tx #(
        .CLKS_PER_BIT (868)  // 100MHz / 115200
    ) u_uart_tx (
        .clk      (clk),
        .rst_n    (rst_n),
        .tx_data  (tx_data_r),
        .tx_valid (tx_valid_r),
        .tx_ready (tx_ready),
        .tx_out   (tx_out),
        .tx_done  (tx_done)
    );

endmodule
