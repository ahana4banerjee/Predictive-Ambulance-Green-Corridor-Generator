/**
 * @file tb_signal_fsm.v
 * @brief Independent simulation testbench for signal_fsm.
 *        Verifies normal cycling, suspend, green override, and resume behaviors.
 */

`timescale 1ns / 1ps

module tb_signal_fsm;

    // Inputs
    reg clk;
    reg rst;
    reg override_green;
    reg suspend;

    // Output
    wire [1:0] signal_state;

    // Instantiate Unit Under Test (UUT)
    signal_fsm uut (
        .clk(clk),
        .rst(rst),
        .override_green(override_green),
        .suspend(suspend),
        .signal_state(signal_state)
    );

    // Clock Generator (100MHz clock: 10ns period)
    always #5 clk = ~clk;

    // State name decoding helper
    function [55:0] get_sig_name(input [1:0] sig);
        case (sig)
            2'b00: get_sig_name = "RED";
            2'b01: get_sig_name = "GREEN";
            2'b10: get_sig_name = "YELLOW";
            default: get_sig_name = "UNKNOWN";
        endcase
    endfunction

    // Monitor transitions
    always @(signal_state or rst or override_green or suspend) begin
        $display("[TIME: %04d ns] | RST: %b | OVR: %b | SUS: %b | SIGNAL: %s",
                 $time, rst, override_green, suspend, get_sig_name(signal_state));
    end

    initial begin
        // Setup waveform dumping
        $dumpfile("tb_signal_fsm.vcd");
        $dumpvars(0, tb_signal_fsm);

        // Initialize inputs
        clk = 0;
        rst = 1;
        override_green = 0;
        suspend = 0;

        $display("\n=========================================================");
        $display("          STARTING INDEPENDENT SIGNAL FSM SIMULATION      ");
        $display("=========================================================\n");

        // Apply reset
        #20;
        rst = 0;
        $display("--- Reset released. Starting normal cycling. ---");

        // --------------------------------------------------------------------
        // TEST CASE 1: Normal cycling (RED 30c -> GREEN 25c -> YELLOW 5c -> RED)
        // --------------------------------------------------------------------
        // We let it cycle from RED to GREEN, YELLOW, and back to RED.
        // Total cycle duration is 60 clock cycles = 600ns.
        #700; 

        // --------------------------------------------------------------------
        // TEST CASE 2: Suspend Logic
        // --------------------------------------------------------------------
        // When suspend is active, the FSM must freeze its current state and timer.
        #30; // Let it enter RED or cycle a bit
        $display("--- Activating Suspend (freeze signal) ---");
        @(posedge clk);
        suspend = 1;
        
        #100; // Let it run for 10 cycles while suspended
        
        $display("--- Releasing Suspend ---");
        @(posedge clk);
        suspend = 0;
        #100; // Observe normal cycling resumed

        // --------------------------------------------------------------------
        // TEST CASE 3: Green Override Logic
        // --------------------------------------------------------------------
        // If override_green is high, the signal must jump to GREEN immediately.
        #100; // Let it run a bit
        $display("--- Activating Green Override (force to GREEN) ---");
        @(posedge clk);
        override_green = 1;
        
        #150; // Let it run in override GREEN

        $display("--- Releasing Green Override ---");
        @(posedge clk);
        override_green = 0;
        
        #400; // Let it run and verify it cycles starting fresh from GREEN

        $display("\n=========================================================");
        $display("         SIGNAL FSM INDEPENDENT SIMULATION COMPLETE      ");
        $display("=========================================================\n");
        $finish;
    end

endmodule
