/**
 * @file emergency_fsm.v
 * @brief Junction-level Emergency Override finite state machine.
 *        Manages transitions between NORMAL, DETECTED, PREPARE, ACTIVE, and RECOVERY.
 *        Outputs override_green and suspend control signals.
 */

module emergency_fsm (
    input clk,
    input rst,
    input ambulance_trigger,
    input prepare_cmd,
    input active_cmd,
    input recovery_cmd,
    output reg [2:0] emergency_state,
    output reg override_green,
    output reg suspend
);

    // State Encodings
    localparam STATE_NORMAL             = 3'b000;
    localparam STATE_EMERGENCY_DETECTED = 3'b001;
    localparam STATE_PREPARE            = 3'b010;
    localparam STATE_ACTIVE             = 3'b011;
    localparam STATE_RECOVERY           = 3'b100;

    reg [2:0] state;
    reg [3:0] recovery_timer;

    // Output Mapping
    always @(*) begin
        emergency_state = state;
        
        // Output control flags based on current state
        case (state)
            STATE_PREPARE: begin
                // In preparation, we force the corridor signal to GREEN to clear traffic
                override_green = 1'b1;
                suspend        = 1'b0;
            end
            
            STATE_ACTIVE: begin
                // In active corridor, force corridor signal to GREEN for ambulance passage
                override_green = 1'b1;
                suspend        = 1'b0;
            end
            
            STATE_RECOVERY: begin
                // In recovery, we can suspend normal cycling momentarily or release
                override_green = 1'b0;
                suspend        = 1'b0;
            end
            
            default: begin
                override_green = 1'b0;
                suspend        = 1'b0;
            end
        endcase
    end

    // State Transition Logic
    always @(posedge clk) begin
        if (rst) begin
            state <= STATE_NORMAL;
            recovery_timer <= 4'b0;
        end else begin
            case (state)
                STATE_NORMAL: begin
                    if (ambulance_trigger) begin
                        state <= STATE_EMERGENCY_DETECTED;
                    end
                    recovery_timer <= 4'b0;
                end

                STATE_EMERGENCY_DETECTED: begin
                    if (prepare_cmd) begin
                        state <= STATE_PREPARE;
                    end else if (active_cmd) begin
                        state <= STATE_ACTIVE;
                    end else if (!ambulance_trigger) begin
                        state <= STATE_NORMAL;
                    end
                end

                STATE_PREPARE: begin
                    if (active_cmd) begin
                        state <= STATE_ACTIVE;
                    end else if (recovery_cmd) begin
                        state <= STATE_RECOVERY;
                        recovery_timer <= 4'b0;
                    end else if (!ambulance_trigger) begin
                        state <= STATE_NORMAL;
                    end
                end

                STATE_ACTIVE: begin
                    if (recovery_cmd) begin
                        state <= STATE_RECOVERY;
                        recovery_timer <= 4'b0;
                    end else if (!ambulance_trigger) begin
                        state <= STATE_NORMAL;
                    end
                end

                STATE_RECOVERY: begin
                    if (recovery_timer >= 4'd10) begin
                        state <= STATE_NORMAL;
                        recovery_timer <= 4'b0;
                    end else begin
                        recovery_timer <= recovery_timer + 4'd1;
                    end
                end

                default: begin
                    state <= STATE_NORMAL;
                end
            endcase
        end
    end

endmodule
