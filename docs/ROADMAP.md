# Development Roadmap
## Embedded Digital Twin Model

---

## 1. Project Timeline & Milestones

The project is structured into a 6-week timeline, prioritizing the integration of virtual communication interfaces (SPI/UART) and establishing a strict boundary between intelligence, control, and display layers.

### Milestone Overview
```
Week 1 ──── Week 2 ──── Week 3 ──── Week 4 ──── Week 5 ──── Week 6
  │            │            │            │            │            │
  ▼            ▼            ▼            ▼            ▼            ▼
Protocol    STM32       Vivado SPI   Arduino      Closed-Loop  Final
Design &    Dijkstra &  Slave &      Serial       Integration  Polish &
Hierarchy   Register    Dynamic      Receiver     & Python     Migration
            Packing     FSMs         Display      Analytics    Plan
```

| Milestone | Target | Gate Criteria |
|---|---|---|
| **M1 — Architecture Complete** | End of Week 1 | Folder layout set, SPI/UART protocol frame structures defined, SRS and System Architecture docs complete. |
| **M2 — Master Intelligence** | End of Week 2 | STM32 simulator executes Dijkstra routing and packs/transmits valid 32-bit SPI frames with checksums to log. |
| **M3 — Hardware FSM Verified** | End of Week 3 | Vivado RTL includes the SPI slave receiver and dynamic corridor controller. Waveforms verify checksum checks and preemption shifts. |
| **M4 — Serial Display Ready** | End of Week 4 | Tinkercad Arduino code is stripped of routing calculations and operates purely as an ASCII serial frame display driver. |
| **M5 — Closed-Loop Testing** | End of Week 5 | Python orchestrator runs loopback simulations: parses STM32 logs, feeds Vivado HDL, and streams outputs to Tinkercad. |
| **M6 — Hardware Migration Guide** | End of Week 6 | All test cases documented, dashboard graphs compiled, and `MIGRATION_PLAN.md` finalized. |

---

## 2. Dependencies & Critical Path

```
Week 1 (Protocols & Folder Layout)
  └──▶ Week 2 (STM32 Dijkstra & SPI Register Packing)
         └──▶ Week 3 (Vivado SPI Slave & Dynamic FSMs) ──┐
         │                                               ├──▶ Week 5 (Python closed-loop & Dashboard)
         └──▶ Week 4 (Tinkercad Serial Display Driver) ──┘
                                                         └──▶ Week 6 (Polish & Migration Guide)
```

---

## 3. Week-by-Week Implementation Plan

### Week 1 — Project Foundation & Interface Design (Completed)
**Objective:** Set up the digital twin directory structure, define registers, and complete core specifications.
*   **Tasks:**
    *   Set up directories: `shared/protocols/`, `simulation/virtual_bus/`, `simulation/orchestrator/`.
    *   Draft `docs/SRS.md` and `docs/SYSTEM_ARCHITECTURE.md` mapping register allocations.
    *   Define the 32-bit SPI frame and XOR checksum logic.
    *   Define the 9-byte UART ASCII string format.

### Week 2 — STM32 Traffic Intelligence & Register Packing (Completed)
**Objective:** Build the Dijkstra pathfinder, ETA calculator, and the SPI Master packet transmitter.
*   **Tasks:**
    *   Create STM32 project and write `traffic_monitor.c`, `ambulance_tracker.c`.
    *   Code `route_optimizer.c` (Dijkstra algorithm with LOW/MED/HIGH traffic cost factors).
    *   Code `eta_calculator.c` mapping node arrival times.
    *   Code `spi_master.c` packing bits and generating the 8-bit XOR checksum.
    *   Verify transmission records in `simulation/virtual_bus/spi_bus.txt`.

### Week 3 — Vivado SPI Receiver & Dynamic Controller (Completed)
**Objective:** Implement synthesizable SPI receiver logic, dynamic signal preemption, and UART state logs in Verilog.
*   **Tasks:**
    *   Code `spi_slave_receiver.v` implementing serial shifting, CDC registers, and XOR check validation.
    *   Code `corridor_controller.v` using SPI `target_node` registers dynamically to clear paths.
    *   Code `emergency_fsm.v` (Normal, Prepare, Active, Recovery states) and `signal_fsm.v`.
    *   Code `uart_tx.v` compiling and writing the ASCII state outputs to `simulation/virtual_bus/uart_bus.txt`.
    *   Write testbench `tb_green_corridor.v` and inspect preemption waveforms.

### Week 4 — Tinkercad Arduino Serial Display (Active)
**Objective:** Strip route-finding logic from Arduino UNO and code a serial message parser to drive display interfaces.
*   **Tasks:**
    *   Create a Tinkercad breadboard schematic layout.
    *   Write `smart_city_traffic_controller.ino` implementing a serial state receiver.
    *   Code character matching: scan for `$`, read LED inputs, extract modes, and parse remaining ETAs.
    *   Map parsed values to output pins D2-D10 (LEDs) and LiquidCrystal LCD coordinates.
    *   Verify that feed-forward serial text strings dynamically refresh the Tinkercad dashboard.

### Week 5 — Closed-Loop Integration & Dashboard Analytics (Scheduled)
**Objective:** Deploy the Python orchestrator to bridge the systems and run the analytics dashboard.
*   **Tasks:**
    *   Write Python runner scripts in `simulation/orchestrator/` to move logs from STM32 ➔ Vivado xsim ➔ Tinkercad serial terminal.
    *   Write `verify_csv_logging.py` parsing signal states and recording logs.
    *   Generate comparative statistics: Travel Time Saved, Corridor Preemption Success rate, and plot Matplotlib efficiency curves.
    *   Verify edge cases: corrupted SPI packet rejection.

### Week 6 — Final Polish & Migration Review (Scheduled)
**Objective:** Compile system verification files and document the hardware bring-up strategy.
*   **Tasks:**
    *   Write `MIGRATION_PLAN.md` documenting STM32 PA5/PA7 registers, Artix-7 XDC pins, and level shifters.
    *   Compile the project report matching simulated runs against expected hardware constraints.