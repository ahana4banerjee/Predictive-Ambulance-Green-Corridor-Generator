# System Architecture Design Document
### Predictive Ambulance Green Corridor Generator using Traffic-Aware Signal Coordination

---

## 1. Executive Vision & Objectives

Traditional smart traffic signals deploy localized, reactive preemption: they switch signal states only when an emergency vehicle physically passes an intersection detector. This approach results in significant delays under heavy congestion as queue clearance time is neglected.

This project implements a **simulation-first embedded digital twin** that shifts signal control from reactive preemption to **predictive preemption**. The system models a 9-junction urban grid where:
1.  Dynamic congestion is continuously updated via vehicle count classifications.
2.  The ambulance's location and speed are tracked to compute an optimized shortest path using Dijkstra's algorithm.
3.  Per-junction crossing times are calculated.
4.  Traffic signals are sequentially prepared and green-locked *before* the ambulance arrives, clearing queues.
5.  All processing is split across hardware-mapped subsystems (STM32 CPU, FPGA RTL, and Arduino displays) communicating via virtualized registers and serial channels.

---

## 2. Integrated Digital Twin Pipeline

The system routes logic sequentially across three physical domains using virtualized hardware protocols:

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │                           SCENARIO GENERATOR                           │
  └──────────────────────────────────┬─────────────────────────────────────┘
                                     │ (Traffic Volume count changes)
                                     ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                       STM32 TRAFFIC INTELLIGENCE                       │
  │                  - traffic_monitor.c  - route_optimizer.c             │
  │                  - ambulance_tracker.c - eta_calculator.c             │
  └──────────────────────────────────┬─────────────────────────────────────┘
                                     │ (Virtual SPI Frame: PA4, PA5, PA7)
                                     ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                         VIVADO FPGA CONTROLLER                         │
  │                  - spi_slave_receiver.v  - corridor_controller.v       │
  │                  - emergency_fsm.v      - signal_fsm.v                │
  └──────────────────────────────────┬─────────────────────────────────────┘
                                     │ (Virtual UART Console Output: JB1)
                                     ▼
  ┌──────────────────────────────────┴─────────────────────────────────────┐
  │                     VISUALIZATION & ANALYTICS LAYER                     │
  │     - Tinkercad LCD & LEDs     - Python Performance Dashboard          │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Subsystem Allocation & Boundary Rules

To ensure hardware equivalence, strict rules enforce subsystem boundaries and data ownership:

### A. STM32 Intelligence Tier (Brain)
*   **Ownership:** Dynamic route computation (Dijkstra), speed-congestion calculations, time-to-node arrival estimations, SPI frame composition, and error check generation.
*   **Constraint:** The STM32 must not write signals directly to pins or manage FSM transitions. All output must be serialized into the 32-bit SPI transaction frame.

### B. Vivado FPGA Tier (Control Coordinator)
*   **Ownership:** De-serializing SPI packets, running clock-synchronized data checks, executing normal traffic signal FSM cycles (RED/GREEN/YELLOW), and coordinate emergency preemption overrides.
*   **Constraint:** The FPGA must not compute shortest paths or dynamic ETAs. It executes overrides based strictly on the `AMB_NODE` and `TGT_NODE` values latched from the SPI register.

### C. Tinkercad Arduino Tier (Output Driver)
*   **Ownership:** Driving signal LEDs, writing status strings on the 16x2 LCD, and forwarding button counts.
*   **Constraint:** The Arduino **MUST NOT** perform route calculations, duplicate signal FSM logic, or compute ETAs. It must behave purely as an I/O expander driven by the UART stream.

---

## 4. Virtual Peripheral Port & Packet Definitions

### A. Virtual SPI Master-to-Slave Port Interface
*   **Clock Polarity (CPOL) = 0, Clock Phase (CPHA) = 0:** Data is driven on SCLK falling edge and sampled on the rising edge.
*   **Chip Select (NSS/CS):** Active-LOW. De-asserted (HIGH) between transactions.

#### 32-Bit Frame Bit Allocation
```
 31  30      27 26      23 22                  11 10   8 7          0
┌───┬──────────┬──────────┬──────────────────────┬──────┬────────────┐
│ E │ AMB_NODE │ TGT_NODE │      ETA_SECONDS     │ DIST │  CHECKSUM  │
└───┴──────────┴──────────┴──────────────────────┴──────┴────────────┘
```

| Fields | Bits | Data Type | Value Range | Description |
|---|---|---|---|---|
| `EMG_ACTIVE` | Bit 31 | Boolean | `0` or `1` | Asserted (1) if emergency preemption is running. |
| `AMB_NODE` | Bits 30-27 | 4-bit Enum | `0000` (A) to `1000` (I) | Current ambulance position junction node. |
| `TGT_NODE` | Bits 26-23 | 4-bit Enum | `0000` (A) to `1000` (I) | Next coordinate targeted for preemption. |
| `ETA_SECONDS`| Bits 22-11 | 12-bit UInt | `0` to `4095` | Est. arrival time (sec) to `TGT_NODE`. |
| `DIST_REMAIN`| Bits 10-8 | 3-bit UInt | `0` to `7` | Remaining hops to hospital destination. |
| `CHECKSUM` | Bits 7-0 | 8-bit Byte | `0x00` to `0xFF` | XOR of bytes 3, 2, and 1 of the frame. |

---

### B. Virtual UART Output Port Interface
*   **Transmission Mode:** Simplex Transmit-only from FPGA.
*   **Parameters:** 9600 Baud equivalent, 8 data bits, 1 stop bit, no parity.
*   **ASCII Protocol String Format:** `$` `[Junction_A_State]` `[Junction_B_State]` `[Junction_C_State]` `[System_Mode]` `[Ambulance_Pos]` `[ETA_Min_MSB]` `[ETA_Min_LSB]` `\n`

#### Valid Frame Characters
*   `$` (Start Marker)
*   Junction States: `0` (RED), `1` (YELLOW), `2` (GREEN), `3` (EMG_GREEN)
*   System Modes: `0` (NORMAL), `1` (ROUTE_DISPLAY), `2` (CORRIDOR_ACTIVE), `3` (ARRIVAL), `4` (RECOVERY)
*   Ambulance Pos: `A` to `I` or `-` (no active run)
*   ETA Min: `00` to `99`
*   `\n` (End Marker)

---

## 5. Subsystem Folder Structure Design

To maintain strict structural isolation, the repository uses the following directory layout:

```
Predictive-Ambulance-Green-Corridor-Generator/
├── docs/                             # Engineering documents (SRS, Guides, Roadmap)
├── shared/
│   └── protocols/                    # Master protocol definitions (C headers, Verilog definitions)
├── stm32/                            # Traffic Intelligence C Code
│   ├── include/                      # Hardware register mocks and headers
│   └── tests/                        # Dijkstra, ETA, and Checksum unit tests
├── vivado/                           # FPGA RTL Controller Subsystem
│   ├── rtl/                          # Synthesizable RTL (SPI, dynamic controllers, FSMs)
│   └── testbench/                    # Verification simulation testbenches
├── tinkercad/                        # Arduino Display Driver
│   └── arduino_code/                 # Minimal I/O expander sketch
└── simulation/
    ├── scenarios/                    # Scenario input traffic counts (JSON/CSV)
    ├── virtual_bus/                  # Logs mimicking physical SPI/UART channels
    └── orchestrator/                 # Python runner driving log execution loops
```

---

## 6. Development & Verification Milestones

1.  **Phase 1 — Protocol and Interface Verification:** Design and run loopback tests verifying the virtual SPI frame pack/unpack routines and XOR checksum calculations on the STM32 simulator.
2.  **Phase 2 — FPGA SPI Receiver and Dynamic Controller Verification:** Implement the `spi_slave_receiver.v` Shift register and the dynamic `corridor_controller.v` in Vivado. Validate preemption switches against multiple routes via Vivado simulation waves.
3.  **Phase 3 — Serial display driver loop:** Demote the Tinkercad Arduino script to parse the serial protocol string. Confirm that LCD messages and LED light cycles match the simulated state logs.
4.  **Phase 4 — Closing the loop (Integrated execution):** Execute the Python orchestrator script to run a full scenario run, moving logs from STM32 through Vivado into Tinkercad.

*Refer to [MIGRATION_PLAN.md](file:///d:/Projects/Personal/Predictive-Ambulance-Green-Corridor-Generator/MIGRATION_PLAN.md) for instructions on physical PA5/PA7 SPI pins, Artix-7 constraints, clock domain crossings, and hardware transceiver setups.*