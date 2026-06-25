/**
 * @file green_corridor_top.v
 * @brief Top-Level Integration module for the FPGA Green Corridor Controller.
 *        Connects the Corridor Controller and the individual junction Signal
 *        and Emergency FSM instances.
 */

module green_corridor_top (
    input clk,
    input rst,
    input ambulance_trigger,
    input [3:0] current_node,
    input [3:0] target_node,
    input [11:0] eta_seconds,
    output [1:0] signal_a,
    output [1:0] signal_b,
    output [1:0] signal_c,
    output emergency_active,
    output [2:0] mode_a,
    output [2:0] mode_b,
    output [2:0] mode_c
);

    // Internal command wires from Corridor Controller to Emergency FSMs
    wire prep_a, act_a, rec_a;
    wire prep_b, act_b, rec_b;
    wire prep_c, act_c, rec_c;

    // Internal control wires from Emergency FSMs to Signal FSMs
    wire override_a, suspend_a;
    wire override_b, suspend_b;
    wire override_c, suspend_c;

    // 1. Central Corridor Controller Instantiation
    corridor_controller ctrl_inst (
        .clk(clk),
        .rst(rst),
        .ambulance_trigger(ambulance_trigger),
        .current_node(current_node),
        .target_node(target_node),
        .eta_seconds(eta_seconds),
        .prep_a(prep_a),
        .act_a(act_a),
        .rec_a(rec_a),
        .prep_b(prep_b),
        .act_b(act_b),
        .rec_b(rec_b),
        .prep_c(prep_c),
        .act_c(act_c),
        .rec_c(rec_c),
        .emergency_active(emergency_active)
    );

    // ========================================================================
    // JUNCTION A INSTANTIATIONS
    // ========================================================================
    emergency_fsm emg_fsm_a (
        .clk(clk),
        .rst(rst),
        .ambulance_trigger(ambulance_trigger),
        .prepare_cmd(prep_a),
        .active_cmd(act_a),
        .recovery_cmd(rec_a),
        .emergency_state(mode_a),
        .override_green(override_a),
        .suspend(suspend_a)
    );

    signal_fsm sig_fsm_a (
        .clk(clk),
        .rst(rst),
        .override_green(override_a),
        .suspend(suspend_a),
        .signal_state(signal_a)
    );

    // ========================================================================
    // JUNCTION B INSTANTIATIONS
    // ========================================================================
    emergency_fsm emg_fsm_b (
        .clk(clk),
        .rst(rst),
        .ambulance_trigger(ambulance_trigger),
        .prepare_cmd(prep_b),
        .active_cmd(act_b),
        .recovery_cmd(rec_b),
        .emergency_state(mode_b),
        .override_green(override_b),
        .suspend(suspend_b)
    );

    signal_fsm sig_fsm_b (
        .clk(clk),
        .rst(rst),
        .override_green(override_b),
        .suspend(suspend_b),
        .signal_state(signal_b)
    );

    // ========================================================================
    // JUNCTION C INSTANTIATIONS
    // ========================================================================
    emergency_fsm emg_fsm_c (
        .clk(clk),
        .rst(rst),
        .ambulance_trigger(ambulance_trigger),
        .prepare_cmd(prep_c),
        .active_cmd(act_c),
        .recovery_cmd(rec_c),
        .emergency_state(mode_c),
        .override_green(override_c),
        .suspend(suspend_c)
    );

    signal_fsm sig_fsm_c (
        .clk(clk),
        .rst(rst),
        .override_green(override_c),
        .suspend(suspend_c),
        .signal_state(signal_c)
    );

endmodule
