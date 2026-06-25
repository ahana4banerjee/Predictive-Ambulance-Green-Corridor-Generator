/**
 * @file signal_fsm.v
 * @brief Normal Traffic Signal cycling finite state machine.
 *        Cycles RED -> GREEN -> YELLOW -> RED autonomously.
 *        Supports override_green and suspend triggers.
 */

module signal_fsm (
    input clk,
    input rst,
    input override_green,
    input suspend,
    output reg [1:0] signal_state
);

    // State Encodings
    localparam STATE_RED    = 2'b00;
    localparam STATE_GREEN  = 2'b01;
    localparam STATE_YELLOW = 2'b10;

    // State Durations (clock cycles)
    localparam DUR_RED    = 6'd30;
    localparam DUR_GREEN  = 6'd25;
    localparam DUR_YELLOW = 6'd5;

    reg [1:0] state;
    reg [5:0] timer;

    // Output Mapping
    always @(*) begin
        signal_state = state;
    end

    // State transition and timer logic
    always @(posedge clk) begin
        if (rst) begin
            state <= STATE_RED;
            timer <= 6'b0;
        end else if (override_green) begin
            state <= STATE_GREEN;
            timer <= 6'b0; // Reset timer so it starts green cycle fresh on release
        end else if (suspend) begin
            // Hold current state and timer
            state <= state;
            timer <= timer;
        end else begin
            // Normal cycling
            case (state)
                STATE_RED: begin
                    if (timer >= DUR_RED - 6'd1) begin
                        state <= STATE_GREEN;
                        timer <= 6'b0;
                    end else begin
                        timer <= timer + 6'd1;
                    end
                end
                
                STATE_GREEN: begin
                    if (timer >= DUR_GREEN - 6'd1) begin
                        state <= STATE_YELLOW;
                        timer <= 6'b0;
                    end else begin
                        timer <= timer + 6'd1;
                    end
                end
                
                STATE_YELLOW: begin
                    if (timer >= DUR_YELLOW - 6'd1) begin
                        state <= STATE_RED;
                        timer <= 6'b0;
                    end else begin
                        timer <= timer + 6'd1;
                    end
                end
                
                default: begin
                    state <= STATE_RED;
                    timer <= 6'b0;
                end
            endcase
        end
    end

endmodule
