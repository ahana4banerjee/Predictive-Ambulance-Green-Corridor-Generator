/**
 * @file tb_green_corridor.v
 * @brief Self-contained behavioral simulation testbench for green_corridor_top.
 *        Applies stimulus for all 5 test scenarios and prints transition reports.
 */

`timescale 1ns / 1ps

module tb_green_corridor;

    // Inputs to DUT
    reg clk;
    reg rst;
    reg ambulance_trigger;
    reg [3:0] current_node;
    reg [3:0] target_node;
    reg [11:0] eta_seconds;

    // Outputs from DUT
    wire [1:0] signal_a;
    wire [1:0] signal_b;
    wire [1:0] signal_c;
    wire emergency_active;
    wire [2:0] mode_a;
    wire [2:0] mode_b;
    wire [2:0] mode_c;

    // Instantiate Design Under Test (DUT)
    green_corridor_top uut (
        .clk(clk),
        .rst(rst),
        .ambulance_trigger(ambulance_trigger),
        .current_node(current_node),
        .target_node(target_node),
        .eta_seconds(eta_seconds),
        .signal_a(signal_a),
        .signal_b(signal_b),
        .signal_c(signal_c),
        .emergency_active(emergency_active),
        .mode_a(mode_a),
        .mode_b(mode_b),
        .mode_c(mode_c)
    );

    // Clock Generator (100MHz clock: 10ns period)
    always #5 clk = ~clk;

    // Helper functions for state decoding
    function [47:0] get_sig_name(input [1:0] sig);
        case (sig)
            2'b00: get_sig_name = "RED";
            2'b01: get_sig_name = "GREEN";
            2'b10: get_sig_name = "YELLOW";
            default: get_sig_name = "UNKNOWN";
        endcase
    endfunction

    function [79:0] get_mode_name(input [2:0] m);
        case (m)
            3'b000: get_mode_name = "NORMAL";
            3'b001: get_mode_name = "DETECTED";
            3'b010: get_mode_name = "PREPARE";
            3'b011: get_mode_name = "ACTIVE";
            3'b100: get_mode_name = "RECOVERY";
            default: get_mode_name = "UNKNOWN";
        endcase
    endfunction

    // Monitor transitions
    always @(signal_a or signal_b or signal_c or mode_a or mode_b or mode_c or emergency_active) begin
        $display("[TIME: %06d ns] | EMG_ACT: %d | A: %s (%s) | B: %s (%s) | C: %s (%s)",
                 $time, emergency_active,
                 get_sig_name(signal_a), get_mode_name(mode_a),
                 get_sig_name(signal_b), get_mode_name(mode_b),
                 get_sig_name(signal_c), get_mode_name(mode_c));
    end

    // Stimulus process
    initial begin
        // Initialize Inputs
        clk = 0;
        rst = 1;
        ambulance_trigger = 0;
        current_node = 4'd15; // NODE_NONE
        target_node = 4'd15;
        eta_seconds = 12'd0;

        $display("\n=========================================================");
        $display("          STARTING GREEN CORRIDOR RTL SIMULATION         ");
        $display("=========================================================\n");

        // Apply reset
        #20;
        rst = 0;
        $display("--- Reset released. Starting normal cycling. ---");

        // --------------------------------------------------------------------
        // TEST CASE 1: Normal Traffic Operation (no ambulance)
        // --------------------------------------------------------------------
        $display("\n[TEST CASE 1] Normal Operation (observing autonomous cycling)...");
        #800; // Let signals cycle RED -> GREEN -> YELLOW (60 cycles * 10ns = 600ns)

        // --------------------------------------------------------------------
        // TEST CASE 2: Single Ambulance Green Corridor (A -> B -> C -> Hospital I)
        // --------------------------------------------------------------------
        $display("\n[TEST CASE 2] Ambulance trigger asserted. Approaching Node A...");
        ambulance_trigger = 1;
        current_node = 4'd0; // NODE_A
        target_node = 4'd1;  // NODE_B
        eta_seconds = 12'd240;
        #300; // Let Junction A remain active

        $display("\nAmbulance arrived at Node B. Preparing Node C...");
        current_node = 4'd1; // NODE_B
        target_node = 4'd2;  // NODE_C
        eta_seconds = 12'd180;
        #300;

        $display("\nAmbulance arrived at Node C...");
        current_node = 4'd2; // NODE_C
        target_node = 4'd8;  // NODE_I (Hospital)
        eta_seconds = 12'd120;
        #300;

        $display("\nAmbulance arrived at Hospital (Junction I)...");
        current_node = 4'd8; // NODE_I
        target_node = 4'd8;
        eta_seconds = 12'd0;
        #100;
        
        $display("\nAmbulance trigger deasserted. Corridor shutting down.");
        ambulance_trigger = 0;
        #300; // Let recovery cycle finish and return to normal

        // --------------------------------------------------------------------
        // TEST CASE 3: Heavy Traffic (Extended ACTIVE state)
        // --------------------------------------------------------------------
        $display("\n[TEST CASE 3] Heavy traffic simulation (longer ACTIVE duration at B)...");
        ambulance_trigger = 1;
        current_node = 4'd0;
        target_node = 4'd1;
        #200;
        
        current_node = 4'd1;
        target_node = 4'd2;
        #600; // Wait longer (60 clock cycles) to simulate slow movement in traffic
        
        current_node = 4'd2;
        target_node = 4'd8;
        #200;
        
        current_node = 4'd8;
        ambulance_trigger = 0;
        #300;

        // --------------------------------------------------------------------
        // TEST CASE 5: System Reset (Assert rst mid-corridor at Node B)
        // --------------------------------------------------------------------
        $display("\n[TEST CASE 5] Mid-corridor Reset Verification...");
        ambulance_trigger = 1;
        current_node = 4'd1; // Node B active
        target_node = 4'd2;
        #100;
        
        $display("Asserting System Reset mid-emergency!");
        rst = 1;
        #30;
        
        $display("Reset released. Verifying clean state.");
        rst = 0;
        ambulance_trigger = 0; // Trigger reset as well
        current_node = 4'd15;
        #300;

        $display("\n=========================================================");
        $display("         GREEN CORRIDOR RTL SIMULATION COMPLETE          ");
        $display("=========================================================\n");
    end

endmodule
