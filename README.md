# 🚑 Predictive Ambulance Green Corridor Generator
### Traffic-Aware Signal Coordination via Embedded Digital Twin

<p align="center">
  <img src="https://img.shields.io/badge/Platform-STM32%20%7C%20Vivado%20%7C%20Tinkercad-blue?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/Language-C%20%7C%20Verilog%20%7C%20Python-green?style=for-the-badge" alt="Language">
  <img src="https://img.shields.io/badge/Type-Embedded%20Digital%20Twin-orange?style=for-the-badge" alt="Type">
</p>

---

## 📋 Project Overview

This repository hosts the **Predictive Ambulance Green Corridor Generator**, developed as a **Simulation-First Embedded Digital Twin**. 

Unlike reactive preemption systems that trigger traffic light changes only when an emergency vehicle reaches an intersection, this system **predicts path ETAs** and **coordinates multi-signal preemption waves** ahead of time.

To ensure realistic, hardware-equivalent validation, each component operates as an independent embedded subsystem. Communication between subsystems is executed using **Virtual SPI** and **Virtual UART** interfaces that exactly match physical chip registers, clock phases, and serial lines.

```
       SIMULATION-FIRST DIGITAL TWIN FLOW
 ┌──────────────────────┐         Virtual SPI         ┌─────────────────────┐
 │    STM32 (C Code)    ├────────────────────────────▶│ Vivado FPGA (RTL)   │
 │ Dijkstra/ETA/Packets │    (32-bit register file)  │ Dynamic FSM Cycles  │
 └──────────────────────┘                             └──────────┬──────────┘
                                                                 │
                                                    Virtual UART │ (ASCII logs)
                                                                 ▼
 ┌──────────────────────┐                             ┌─────────────────────┐
 │   Tinkercad Output   │◀────────────────────────────┤  Python Dashboard   │
 │ (LED / LCD Drivers)  │       (Serial Playback)     │ (Analytics Engine)  │
 └──────────────────────┘                             └─────────────────────┘
```

---

## 🏗️ Architecture Summary

*   **Intelligence Tier (STM32 CubeIDE):** The "brain." Takes traffic density counts, runs Dijkstra routing search, estimates node crossings, packs registers, and computes XOR checksums.
*   **Control Tier (Vivado FPGA):** The "safety gate." Receives SPI packets, validates checksum logic, clocks data through CDC synchronizers, runs traffic signal cycles, and generates dynamic green corridor preemption signals.
*   **Visualization Tier (Tinkercad Arduino):** The "display." Demoted from computing routes locally; parses serial stream inputs from the FPGA to toggle LEDs and print status reports to the 16x2 LCD display.
*   **Analytics Tier (Python / CSV):** Bridges virtual log files, runs execution loops, and generates comparative plots showing travel metrics with and without preemption.

---

## 📁 Repository Structure

The project folders are organized into distinct functional domains:

```
Predictive-Ambulance-Green-Corridor-Generator/
│
├── README.md                          ← You are here
├── ARCHITECTURE.md                    ← Global system architecture mapping
├── STM32_DESIGN.md                    ← Dijkstra pathfinding & register packing design
├── VIVADO_DESIGN.md                   ← FPGA shift registers & FSM control design
├── TINKERCAD_DESIGN.md                ← Arduino Serial LCD/LED driver design
├── MIGRATION_PLAN.md                  ← Silicon migration guide (pins, constraints, CDC)
│
├── shared/
│   └── protocols/                    # Common SPI register maps and UART schemas
├── stm32/                            # Traffic Intelligence C Code
│   ├── include/                      # Headers with SPI frame structures
│   └── tests/                        # Dijkstra, ETA, and Checksum unit tests
├── vivado/                           # FPGA RTL Controller Subsystem
│   ├── rtl/                          # Synthesizable RTL (SPI, dynamic controllers, FSMs)
│   └── testbench/                    # Verification simulation testbenches
├── tinkercad/                        # Arduino Display Driver
│   └── arduino_code/                 # Minimal I/O expander sketch
├── simulation/
│   ├── scenarios/                    # Scenario input traffic counts (JSON/CSV)
│   ├── virtual_bus/                  # spi_bus.txt and uart_bus.txt log streams
│   └── orchestrator/                 # Python runner driving log execution loops
└── results/                          # Output logs and analytics graphs
```

---

## 🚀 Getting Started

To compile and execute the simulation loop:
1.  **Generate SPI Packets:** Compile and run `stm32/tests/test_interfaces.c` to verify register packing outputs.
2.  **Simulate HDL Controller:** Open `vivado/` in Vivado, launch behavioral simulation, and verify preemption waveforms on GTKWave/ILA.
3.  **Animate Visuals:** Paste generated ASCII UART log bytes into the Tinkercad serial terminal.
4.  **Run Orchestrated Loop:** Run `python simulation/orchestrator/run_digital_twin.py` to automate log processing between compilation systems.

*Refer to [docs/IMPLEMENTATION_GUIDE.md](file:///d:/Projects/Personal/Predictive-Ambulance-Green-Corridor-Generator/docs/IMPLEMENTATION_GUIDE.md) for detailed execution scripts.*

---

## 📜 Technical Documents Directory

*   [Software Requirements Specification (docs/SRS.md)](file:///d:/Projects/Personal/Predictive-Ambulance-Green-Corridor-Generator/docs/SRS.md)
*   [System Architecture Design (docs/SYSTEM_ARCHITECTURE.md)](file:///d:/Projects/Personal/Predictive-Ambulance-Green-Corridor-Generator/docs/SYSTEM_ARCHITECTURE.md)
*   [Development Roadmap & Milestones (docs/ROADMAP.md)](file:///d:/Projects/Personal/Predictive-Ambulance-Green-Corridor-Generator/docs/ROADMAP.md)
*   [Compilation & Simulation Guide (docs/IMPLEMENTATION_GUIDE.md)](file:///d:/Projects/Personal/Predictive-Ambulance-Green-Corridor-Generator/docs/IMPLEMENTATION_GUIDE.md)
*   [Hardware Silicon Migration Plan (MIGRATION_PLAN.md)](file:///d:/Projects/Personal/Predictive-Ambulance-Green-Corridor-Generator/MIGRATION_PLAN.md)
