`timescale 1ns / 1ps

// ============================================================
// uart_tx — UART Transmitter
// ============================================================
// - Configurable baud rate via CLKS_PER_BIT parameter
// - 8N1 format (8 data bits, no parity, 1 stop bit)
// - Active low reset (rst_n), synchronous
// - AXI-Stream-like handshake: tx_valid / tx_ready
// ============================================================

module uart_tx #(
    parameter CLKS_PER_BIT = 868   // 100MHz / 115200 baud = 868
)(
    input  wire       clk,
    input  wire       rst_n,

    // Data interface
    input  wire [7:0] tx_data,
    input  wire       tx_valid,
    output reg        tx_ready,

    // UART output
    output reg        tx_out,

    // Status
    output reg        tx_done
);

    // =========================================
    // FSM States
    // =========================================
    localparam [2:0] S_IDLE  = 3'd0,
                     S_START = 3'd1,
                     S_DATA  = 3'd2,
                     S_STOP  = 3'd3;

    // =========================================
    // Internal Registers
    // =========================================
    reg [2:0]  state_r;
    reg [2:0]  next_state_w;

    reg [15:0] clk_cnt_r;
    reg [2:0]  bit_idx_r;
    reg [7:0]  tx_shift_r;

    // =========================================
    // FSM: State Register (Process 1/3)
    // =========================================
    always @(posedge clk) begin
        if (!rst_n) begin
            state_r <= S_IDLE;
        end else begin
            state_r <= next_state_w;
        end
    end

    // =========================================
    // FSM: Next State Logic (Process 2/3)
    // =========================================
    always @(*) begin
        next_state_w = state_r; // default: hold

        case (state_r)
            S_IDLE: begin
                if (tx_valid)
                    next_state_w = S_START;
            end

            S_START: begin
                if (clk_cnt_r == CLKS_PER_BIT - 1)
                    next_state_w = S_DATA;
            end

            S_DATA: begin
                if (clk_cnt_r == CLKS_PER_BIT - 1) begin
                    if (bit_idx_r == 3'd7)
                        next_state_w = S_STOP;
                    // else stay in S_DATA
                end
            end

            S_STOP: begin
                if (clk_cnt_r == CLKS_PER_BIT - 1)
                    next_state_w = S_IDLE;
            end

            default: next_state_w = S_IDLE;
        endcase
    end

    // =========================================
    // FSM: Output Logic (Process 3/3)
    // =========================================
    always @(posedge clk) begin
        if (!rst_n) begin
            tx_out     <= 1'b1;  // idle high
            tx_ready   <= 1'b1;
            tx_done    <= 1'b0;
            clk_cnt_r  <= 16'd0;
            bit_idx_r  <= 3'd0;
            tx_shift_r <= 8'd0;
        end else begin
            tx_done <= 1'b0; // default: pulse

            case (state_r)
                S_IDLE: begin
                    tx_out    <= 1'b1;
                    clk_cnt_r <= 16'd0;
                    bit_idx_r <= 3'd0;

                    if (tx_valid) begin
                        tx_shift_r <= tx_data;
                        tx_ready   <= 1'b0;
                    end else begin
                        tx_ready <= 1'b1;
                    end
                end

                S_START: begin
                    tx_out <= 1'b0; // start bit = low

                    if (clk_cnt_r == CLKS_PER_BIT - 1) begin
                        clk_cnt_r <= 16'd0;
                    end else begin
                        clk_cnt_r <= clk_cnt_r + 16'd1;
                    end
                end

                S_DATA: begin
                    tx_out <= tx_shift_r[bit_idx_r]; // LSB first

                    if (clk_cnt_r == CLKS_PER_BIT - 1) begin
                        clk_cnt_r <= 16'd0;
                        bit_idx_r <= bit_idx_r + 3'd1;
                    end else begin
                        clk_cnt_r <= clk_cnt_r + 16'd1;
                    end
                end

                S_STOP: begin
                    tx_out <= 1'b1; // stop bit = high

                    if (clk_cnt_r == CLKS_PER_BIT - 1) begin
                        clk_cnt_r <= 16'd0;
                        tx_done   <= 1'b1;
                        tx_ready  <= 1'b1;
                    end else begin
                        clk_cnt_r <= clk_cnt_r + 16'd1;
                    end
                end

                default: begin
                    tx_out   <= 1'b1;
                    tx_ready <= 1'b1;
                end
            endcase
        end
    end

endmodule
