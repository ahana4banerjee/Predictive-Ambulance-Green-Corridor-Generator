# System Execution Sequence Specification (SYSTEM_SEQUENCE.md)
### Executable Simulation Sequence for Scenario 2 (Bypass Route A ➔ D ➔ G ➔ H ➔ I)

---

## 1. Sequence Diagram Overview

This document defines the timeline execution specification. The Simulation Engine schedules timing steps, updates virtual transport lines, and advances ambulance coordinates.

```
 [Sim Engine] ──(Trigger scenario)──▶ [STM32]
                                         │
                                         ▼ (Virtual SPI Packet Output)
 [Sim Engine] ──(Forward packet)────▶ [Vivado FPGA]
                                         │
                                         ▼ (Virtual UART Telemetry Output)
 [Sim Engine] ──(Forward log data)──▶ [Arduino / Tinkercad]
                                         │
                                         ▼ (Console Log Parser)
                                      [Python Dashboard]
```

---

## 2. Dynamic Preemption Execution Timeline

### Time T = 0.0s: Simulation Start & Initialization
*   **Active Subsystem:** Simulation Engine
*   **Current State:** `BOOT_UP`
*   **Inputs:** `simulation/scenarios/scenario_bypass.json` (Junction B vehicle count = 35 [HIGH], Junction C vehicle count = 48 [HIGH]).
*   **Internal Processing:** 
    *   Initializes the simulation global clock ($T_{sim} = 0.0$).
    *   Fires virtual sensor registers to STM32 Traffic Density Monitor.
    *   Registers emergency switch pulse at Junction A (Ambulance departs from PA0).
*   **Outputs Generated:** Raw count arrays parsed to RAM.
*   **Packets Produced:** None.
*   **Logs Generated:** `simulation/logs/sim_run_init.json`
*   **State Transitions:** `IDLE` ➔ `ACTIVE_RUN`
*   **Trigger for Next Subsystem:** Timer interrupt fires STM32 intelligence loop.

---

### Time T = 0.2s: STM32 Path & ETA Calculation
*   **Active Subsystem:** STM32 Traffic Intelligence (Dijkstra Core)
*   **Current State:** `RUNNING_ROUTE_CALCULATION`
*   **Inputs Received:** Density arrays (B=HIGH, C=HIGH), Ambulance start node = `NODE_A`.
*   **Internal Processing:**
    *   Dijkstra cost evaluation: Penalizes path A-B-C due to HIGH density. Selects route `A ➔ D ➔ G ➔ H ➔ I`.
    *   ETA Calculator computes crossing times: Segment A-D (4.0s), D-G (8.0s), G-H (12.0s), H-I (16.0s).
    *   SPI Packet compiler packs bit fields for target node D.
*   **Outputs Generated:** Packed 32-bit register variables.
*   **Packets Produced:** `simulation/virtual_bus/packets/spi_tx_001.bin` (Hex payload: `0x808300F4` -> EMG=1, AMB=A, TGT=D, ETA=4s, DIST=4, Checksum=0xF4).
*   **Logs Generated:** `simulation/logs/stm32_route.log` (Route selected: A-D-G-H-I).
*   **State Transitions:** `ROUTE_CALCULATION` ➔ `SPI_FRAME_READY`
*   **Trigger for Next Subsystem:** Simulation Engine reads binary packet and clocks it to the FPGA SPI Slave receiver.

---

### Time T = 0.3s: FPGA SPI Receive & Deserialization
*   **Active Subsystem:** Vivado FPGA SPI Slave Receiver
*   **Current State:** `SPI_SHIFT_REGISTER`
*   **Inputs Received:** Serial stream (`mosi`, `sclk`, `nss`) driven by the Simulation Engine from `spi_tx_001.bin`.
*   **Internal Processing:**
    *   Shifts bits into the 32-bit registers.
    *   Validates XOR checksum: `0x80 ^ 0x83 ^ 0x00 == 0x03` (checks match!).
    *   Latches parallel register flags: `current_node=NODE_A`, `target_node=NODE_D`, `emg_active=1`.
*   **Outputs Generated:** Parallel internal control wires: `emg_active_wire = 1`, `current_node_wire = 4'd0`, `target_node_wire = 4'd3`.
*   **Packets Consumed:** `spi_tx_001.bin`
*   **Logs Generated:** Checksum validation PASS flag.
*   **State Transitions:** `SPI_RX_IDLE` ➔ `REGISTERS_LATCHED`
*   **Trigger for Next Subsystem:** Data ready flag triggers the FPGA Corridor Controller.

---

### Time T = 0.4s: FPGA Corridor Preemption Override
*   **Active Subsystem:** Vivado FPGA Corridor Controller & Junction FSMs
*   **Current State:** `CORRIDOR_PREEMPTION_ACTIVE`
*   **Inputs Received:** Latched registers (`current_node = NODE_A`, `target_node = NODE_D`, `emg_active = 1`).
*   **Internal Processing:**
    *   Dynamic routing match: `current_node == NODE_A` asserts `act_a = 1`. `target_node == NODE_D` asserts `prep_d = 1` (Junction B is bypassed!).
    *   FSM A transitions to `STATE_ACTIVE` ➔ overrides Signal A state to `SIGNAL_EMG_GREEN`.
    *   FSM D transitions to `STATE_PREPARE` ➔ overrides Signal D state to `SIGNAL_RED` (holds cross-street traffic).
    *   UART serializer packages current light configurations.
*   **Outputs Generated:** Light output states: `signal_a = 2'b11` (EMG_GREEN), `signal_d = 2'b00` (RED).
*   **Packets Produced:** Virtual UART ASCII string: `$3002D04\n` (EMG_GREEN on A, RED on D, Normal on C, Mode=Corridor, Position=A, ETA=4s).
*   **Logs Generated:** `simulation/virtual_bus/logs/signal_state_001.json`
*   **State Transitions:** Normal Traffic Cycling ➔ Emergency Override.
*   **Trigger for Next Subsystem:** Simulation Engine routes the UART string to Tinkercad and the Dashboard.

---

### Time T = 0.5s: Dashboard & Tinkercad Update
*   **Active Subsystem:** Tinkercad Arduino Visualizer & Python Dashboard
*   **Current State:** `DISPLAY_UPDATE`
*   **Inputs Received:** UART Serial string: `$3002D04\n`.
*   **Internal Processing:**
    *   Arduino parses ASCII stream. Maps state A (3) to D4 (Green LED ON), state D (0) to Red LED ON. LCD prints `AMB@A  ETA:00:04`.
    *   Python parser reads JSON log. Updates analytics display metrics.
*   **Outputs Generated:** LED illumination, LCD character updates, dashboard GUI redraw.
*   **Packets Consumed:** `$3002D04\n`
*   **Logs Generated:** Terminal refresh reports.
*   **State Transitions:** Idle display ➔ Preemption display.
*   **Trigger for Next Subsystem:** Clock advances.

---

### Time T = 4.0s: Ambulance Arrives at Junction D
*   **Active Subsystem:** Simulation Engine & STM32 Tracker
*   **Current State:** `SEGMENT_PROGRESSION`
*   **Inputs Received:** Clock timer = 4.0s (segment boundary reached).
*   **Internal Processing:**
    *   Simulation Engine updates ambulance position to Junction D.
    *   Fires tracker update interrupt.
    *   STM32 updates position index, computes remaining ETA (to G=4s, H=8s, I=12s).
    *   SPI compiler packs new target node G.
*   **Outputs Generated:** Packed 32-bit registers.
*   **Packets Produced:** `simulation/virtual_bus/packets/spi_tx_002.bin` (EMG=1, AMB=D, TGT=G, ETA=4s, DIST=3).
*   **Logs Generated:** Position update log.
*   **State Transitions:** Node progression.
*   **Trigger for Next Subsystem:** SPI transmission triggers FPGA receiver.

---

### Time T = 4.4s: FPGA Preemption Wave Shift
*   **Active Subsystem:** Vivado FPGA Corridor Controller & Junction FSMs
*   **Current State:** `CORRIDOR_PREEMPTION_SHIFT`
*   **Inputs Received:** SPI registers (`current_node = NODE_D`, `target_node = NODE_G`).
*   **Internal Processing:**
    *   Corridor Controller matches: `current_node == NODE_D` asserts `act_d = 1`. `target_node == NODE_G` asserts `prep_g = 1`.
    *   FSM A transitions to `STATE_RECOVERY` (initiates recovery timer).
    *   FSM D transitions to `STATE_ACTIVE` ➔ Signal D to `SIGNAL_EMG_GREEN` (ambulance passes).
    *   FSM G transitions to `STATE_PREPARE` ➔ Signal G to `SIGNAL_RED`.
*   **Outputs Generated:** Signal state lines: `signal_a` (normal cycle), `signal_d = 2'b11` (EMG_GREEN), `signal_g = 2'b00` (RED).
*   **Packets Produced:** UART frame: `$0302G03\n` (Mode=Corridor, Position=D, ETA=3s).
*   **Logs Generated:** `simulation/virtual_bus/logs/signal_state_002.json`
*   **State Transitions:** Preemption wave shifts from A-D to D-G.
*   **Trigger for Next Subsystem:** Forward to display blocks.

---

### Time T = 16.0s: Ambulance Arrives at Hospital Node I
*   **Active Subsystem:** Simulation Engine & STM32 Tracker
*   **Current State:** `DESTINATION_ARRIVAL`
*   **Inputs Received:** Clock timer = 16.0s (hospital node reached).
*   **Internal Processing:**
    *   Ambulance halts. Tracker clears emergency run status (`emergency_active = 0`).
    *   SPI packet generator compiles final shutdown frame.
*   **Outputs Generated:** 32-bit register variables.
*   **Packets Produced:** `simulation/virtual_bus/packets/spi_tx_005.bin` (EMG=0, AMB=I, TGT=I, ETA=0s, DIST=0).
*   **Logs Generated:** Journey completed log.
*   **State Transitions:** Active run ➔ Arrived.
*   **Trigger for Next Subsystem:** SPI packet sent to FPGA.

---

### Time T = 16.4s: FPGA Preemption Shutdown
*   **Active Subsystem:** Vivado FPGA Corridor Controller
*   **Current State:** `RECOVERY_INITIATED`
*   **Inputs Received:** SPI registers (`emg_active = 0`, `current_node = NODE_I`).
*   **Internal Processing:**
    *   Corridor Controller clears preemption. Sets `emergency_active = 0`.
    *   FSM D and G transition to `STATE_RECOVERY`. All intersection overrides are released.
    *   Recovery timers run (10 clock cycles / 2 seconds).
*   **Outputs Generated:** Signal state lines: normal default phases.
*   **Packets Produced:** UART frame: `$0003I00\n` (Mode=Arrival, Position=I).
*   **Logs Generated:** `simulation/virtual_bus/logs/signal_state_005.json`
*   **State Transitions:** Preemption active ➔ Recovery mode.
*   **Trigger for Next Subsystem:** UART logs read by Arduino and Dashboard.

---

### Time T = 18.4s: Recovery Complete & Reset
*   **Active Subsystem:** Vivado FPGA & Tinkercad Arduino
*   **Current State:** `SYSTEM_RESET_COMPLETE`
*   **Inputs Received:** Recovery timers expire (T=18.4s).
*   **Internal Processing:**
    *   FSMs release lock, returning junctions to default cycle clocks.
    *   UART output states signal return to normal.
    *   Arduino LCD switches display back to normal traffic updates: `A:LOW B:MED C:LOW`.
*   **Outputs Generated:** Default LED cycles resume.
*   **Packets Produced:** UART frame: `$0200-00\n` (Mode=Normal, Position=-).
*   **Logs Generated:** `simulation/virtual_bus/logs/signal_state_006.json`
*   **State Transitions:** Recovery mode ➔ Normal cycling.
*   **Trigger for Next Subsystem:** Dashboard parses execution runs, compiles statistics, and generates comparative matplotlib report charts.
