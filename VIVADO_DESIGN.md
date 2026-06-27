# FPGA Corridor Controller Design Document
### Control Tier — Vivado (Verilog HDL)

---

## 1. Subsystem Architecture

The FPGA Control Tier resides in the digital twin framework as a safety-critical **signal hardware arbiter**. It interfaces with the STM32 SPI Master via the virtual/physical SPI port, dynamically schedules overrides, and transmits active signal state blocks to the visualization and analytics layers via UART.

```
       [SPI Interface Inputs] (mosi, sclk, nss)
                 │
                 ▼
    ┌──────────────────────────┐
    │  spi_slave_receiver.v    │ ◄─── Latch registers on NSS rising edge
    └────────────┬─────────────┘
                 │ (32-bit registers: current_node, target_node, emg_active)
                 ▼
    ┌──────────────────────────┐
    │  corridor_controller.v   │ ◄─── Dynamic Preemption Pre-scheduler
    └────────────┬─────────────┘
                 │ (Junction control wires: prep_x, act_x, rec_x)
                 ▼
    ┌──────────────────────────┐
    │     emergency_fsm.v      │ ◄─── Junction-level Preemption Override
    └────────────┬─────────────┘
                 │ (override_green, suspend)
                 ▼
    ┌──────────────────────────┐
    │       signal_fsm.v       │ ◄─── Normal Cycle Traffic Lights (R->G->Y)
    └────────────┬─────────────┘
                 │ (2-bit Signal States: signal_a, signal_b, signal_c)
                 ▼
    ┌──────────────────────────┐
    │         uart_tx.v        │ ◄─── ASCII Protocol Stream Generator
    └────────────┬─────────────┘
                 ▼
          [uart_bus.txt Log]
```

---

## 2. HDL Module Specifications

### A. SPI Slave Receiver (`spi_slave_receiver.v`)
*   **Purpose:** Deserializes incoming serial SPI frames, manages synchronization to prevent clock-domain crossing metastabilities, and executes byte-wise error checking.
*   **Pins:** `mosi` (Input), `sclk` (Input), `nss` (Input/Active-LOW), `miso` (Output).
*   **Registers:** 32-bit shift register, 5-bit shift counter.
*   **Logic Operations:**
    *   Samples `mosi` on rising edges of `sclk` while `nss` is LOW.
    *   Computes XOR parity: `checksum_ok = (byte_3 ^ byte_2 ^ byte_1) == byte_0`.
    *   On `nss` rising edge: if 32 bits are shifted and checksum is verified, raises `data_ready` and latch outputs.

### B. Dynamic Corridor Controller (`corridor_controller.v`)
*   **Purpose:** Resolves the dynamic preemption routing bug by scheduling signal clears based on the SPI `target_node` registers instead of hardcoded paths.
*   **Inputs:** `current_node[3:0]`, `target_node[3:0]`, `emg_active`, `clk`, `rst`.
*   **Outputs:** Prep/Act/Rec override trigger wires for Junctions A, B, C.
*   **Operation:**
    *   `act_x` asserts if `current_node == NODE_X` and `emg_active` is high.
    *   `prep_x` asserts if `target_node == NODE_X` and `current_node != NODE_X`.
    *   `rec_x` asserts once the ambulance current position advances past `NODE_X`.

### C. Junction Emergency FSM (`emergency_fsm.v`)
*   **Purpose:** Safety override controller managing the lifecycle of preemption at each intersection.
*   **States:**
    *   `STATE_NORMAL` (000) - Default. Signals cycle autonomously.
    *   `STATE_EMERGENCY_DETECTED` (001) - Emergency flag raised.
    *   `STATE_PREPARE` (010) - Target node clearing. Forces signal `GREEN` (or holds cross-street red).
    *   `STATE_ACTIVE` (011) - Ambulance passing through. Signal locked `GREEN`.
    *   `STATE_RECOVERY` (100) - Ambulance left. Triggers a 10-clock safety recovery delay before releasing control.

### D. Normal Traffic Signal FSM (`signal_fsm.v`)
*   **Purpose:** Cycles traffic phases RED (30s) ➔ GREEN (25s) ➔ YELLOW (5s) sequentially.
*   **Overrides:**
    *   If `override_green` asserts, the state jumps immediately to `STATE_GREEN` and resets internal timer counters.
    *   If `suspend` asserts, timer increments are locked, holding the current phase.

---

## 3. Communication Channel: Virtual UART Logger (`uart_tx.v`)

For simulation-first execution, the FPGA includes a virtual UART transceiver module that writes state telemetry updates as delimited ASCII log messages.

### A. Telemetry Package Assembly
The module parses the active states of the junction signal FSMs, emergency overrides, position register, and remaining ETA to compile a 9-byte ASCII log packet:
`$` `[SigA]` `[SigB]` `[SigC]` `[Mode]` `[Pos]` `[ETA_1]` `[ETA_0]` `\n`

### B. Simulation Output Routine
During Behavioral RTL Simulation, the testbench writes the UART bitstream directly to a shared text file (`simulation/virtual_bus/uart_bus.txt`) mimicking a physical serial buffer output:

```verilog
integer uart_file;
initial begin
    uart_file = $fopen("simulation/virtual_bus/uart_bus.txt", "w");
end

always @(posedge clk) begin
    if (uart_frame_ready) begin
        $fdisplay(uart_file, "$%d%d%d%d%c%02d", 
                  signal_state_a, signal_state_b, signal_state_c, 
                  system_mode, ambulance_pos_char, eta_minutes);
        $fflush(uart_file);
    end
end
```

---

## 4. Design Verification

*   **Testbench (`tb_green_corridor.v`):** Feeds SPI serial streams into the Top-Level block under varying scenarios (Normal, Standard Route, Bypass Route). Probes signal timings to verify that preemption waves clear cross-street traffic 45s ahead of arrival.
*   **Waveform Logs (`tb_green_corridor.vcd`):** Log files containing digital signal traces. Analyzed via GTKWave or Vivado Waveform Viewer to prove CDC synchronization and FSM transition safety.

*Refer to [MIGRATION_PLAN.md](file:///d:/Projects/Personal/Predictive-Ambulance-Green-Corridor-Generator/MIGRATION_PLAN.md) to inspect physical XDC configurations, Artix-7 PMOD pin assignments, and clock generator dividers.*
