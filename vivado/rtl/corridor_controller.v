/**
 * @file corridor_controller.v
 * @brief System-wide Green Corridor Controller.
 *        Decodes route coordinates, ambulance triggers, and active positions
 *        to sequentially prepare, activate, and recover junction signals.
 */

module corridor_controller (
    input clk,
    input rst,
    input ambulance_trigger,
    input [3:0] current_node,
    input [3:0] target_node,
    input [11:0] eta_seconds,
    output reg prep_a,
    output reg act_a,
    output reg rec_a,
    output reg prep_b,
    output reg act_b,
    output reg rec_b,
    output reg prep_c,
    output reg act_c,
    output reg rec_c,
    output reg emergency_active
);

    // Node definitions matching system_interfaces.h
    localparam NODE_A = 4'd0;
    localparam NODE_B = 4'd1;
    localparam NODE_C = 4'd2;
    localparam NODE_I = 4'd8; // Hospital

    always @(posedge clk) begin
        if (rst) begin
            prep_a <= 1'b0; act_a <= 1'b0; rec_a <= 1'b0;
            prep_b <= 1'b0; act_b <= 1'b0; rec_b <= 1'b0;
            prep_c <= 1'b0; act_c <= 1'b0; rec_c <= 1'b0;
            emergency_active <= 1'b0;
        end else if (!ambulance_trigger) begin
            prep_a <= 1'b0; act_a <= 1'b0; rec_a <= 1'b0;
            prep_b <= 1'b0; act_b <= 1'b0; rec_b <= 1'b0;
            
            // Release C into recovery if it was active
            if (act_c) begin
                rec_c <= 1'b1;
            end else begin
                rec_c <= 1'b0;
            end
            
            act_c <= 1'b0;
            prep_c <= 1'b0;
            emergency_active <= 1'b0;
        end else begin
            emergency_active <= 1'b1;
            
            // Default all signals to inactive
            prep_a <= 1'b0; act_a <= 1'b0; rec_a <= 1'b0;
            prep_b <= 1'b0; act_b <= 1'b0; rec_b <= 1'b0;
            prep_c <= 1'b0; act_c <= 1'b0; rec_c <= 1'b0;
            
            // Progressive wave decoding based on ambulance current position
            case (current_node)
                NODE_A: begin
                    act_a  <= 1'b1; // Junction A is active
                    prep_b <= 1'b1; // Junction B begins preparation
                end
                
                NODE_B: begin
                    rec_a  <= 1'b1; // Junction A is in recovery
                    act_b  <= 1'b1; // Junction B is active
                    prep_c <= 1'b1; // Junction C begins preparation
                end
                
                NODE_C: begin
                    rec_b  <= 1'b1; // Junction B is in recovery
                    act_c  <= 1'b1; // Junction C is active
                end
                
                default: begin
                    // If position is not A, B, or C (e.g. bypassed or arrived at I)
                    if (current_node == NODE_I) begin
                        rec_c <= 1'b1; // Recover Junction C
                    end
                end
            endcase
        end
    end

endmodule
