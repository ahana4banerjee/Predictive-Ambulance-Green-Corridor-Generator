# System Requirements Specification (SRS)
### Predictive Ambulance Green Corridor Generator — Digital Twin Model

---

## 1. Introduction

This document outlines the software and hardware constraints, functional specifications, and protocol requirements for the Predictive Ambulance Green Corridor system. The codebase acts as a **simulation-first embedded digital twin**, modeling independent hardware subsystems bridged by virtual peripheral interfaces (SPI and UART).

---

## 2. General System Architecture Requirements

*   **Subsystem Boundary Isolation:** The system must isolate operations across three distinct domains:
    1.  *Intelligence (STM32 CPU):* Routing algorithms, travel math, packet compiler.
    2.  *Control (FPGA RTL):* Signal FSM transitions, emergency override preemption, UART serial output.
    3.  *Visualization (Arduino UNO):* Passive character display, LED driver.
*   **Virtual Interface Emulation:** Serial bus registers must be mirrored in simulation via shared log buffers.
    *   Virtual SPI Master (STM32) ➔ Virtual SPI Slave (FPGA)
    *   Virtual UART Transmitter (FPGA) ➔ Virtual UART Receiver (Arduino)
*   **Hardware Equivalence:** The protocol, data packing bitfields, and FSM transition parameters must be identical to physical hardware specifications to ensure zero-code changes upon migration to physical silicon.

---

## 3. Detailed Functional Requirements

### A. STM32 Intelligence Subsystem
*   **FR-MCU-001 (Congestion Classification):** The monitor must categorize vehicle counts into LOW (0-10), MEDIUM (11-25), and HIGH (26+) density zones.
*   **FR-MCU-002 (Dijkstra Pathfinder):** The Route Optimizer must compute the shortest path using dynamic weight penalties (1.0 for LOW, 1.5 for MED, 3.0 for HIGH congestion).
*   **FR-MCU-003 (ETA Generator):** The calculator must compute segment arrival ETAs based on distance and travel speeds.
*   **FR-MCU-004 (SPI Register Packer):** The system must pack:
    *   Bit 31: Emergency Active flag
    *   Bits 30-27: Current node ID (0-8)
    *   Bits 26-23: Target preemption node ID (0-8)
    *   Bits 22-11: target node ETA (0-4095s)
    *   Bits 10-8: remaining node hops (0-7)
    *   Bits 7-0: Byte-wise XOR checksum
*   **FR-MCU-005 (Virtual SPI Output):** The SPI Master must serialize and log the packed 32-bit transaction word to `simulation/virtual_bus/spi_bus.txt` every 200ms during an active emergency run.

### B. FPGA Control Subsystem
*   **FR-FPGA-001 (SPI Serial Receiver):** The receiver module must deserialize MOSI bits on SCLK rising edges while NSS is LOW.
*   **FR-FPGA-002 (Checksum Validation):** The SPI slave must compute the XOR parity of the first three bytes of the packet. If it matches the checksum byte, data is latched; otherwise, the packet is discarded and a checksum error is flagged.
*   **FR-FPGA-003 (Clock Domain Synchronization):** Shifted inputs must pass through two stages of flip-flops to prevent metastability when transitioning from SCLK to the internal 100MHz system clock domain.
*   **FR-FPGA-004 (Dynamic Preemption wave):** The `Corridor Controller` must assert `prep_x` (prepare flag for junction X) if `target_node == NODE_X` and `current_node != NODE_X`. It must assert `act_x` (active preemption) if `current_node == NODE_X`.
*   **FR-FPGA-005 (Safety Recovery):** Emergency overrides must remain locked in `STATE_RECOVERY` for 10 system clock cycles after the ambulance leaves a junction to allow cross-street queues to clear before releasing FSM control to normal cycles.
*   **FR-FPGA-006 (UART Output logging):** The serial transmitter must write ASCII telemetry packets (`$` + states + mode + pos + ETA + `\n`) to `simulation/virtual_bus/uart_bus.txt` every 100ms.

### C. Arduino Visualization Subsystem
*   **FR-ARD-001 (Passive Receiver):** The Arduino UNO sketch **must not** calculate routes, duplicate traffic light state machines, or determine ETAs. All outputs must be driven directly by the parsed UART serial string.
*   **FR-ARD-002 (Serial String Parsing):** The Arduino must scan incoming serial inputs at 9600 Baud, detect the `$` start delimiter, unpack signal and mode characters, and check the `\n` stop character.
*   **FR-ARD-003 (LED/LCD Mapping):** The sketch must map:
    *   Signal states to D2-D10 outputs.
    *   Modes, position, and ETAs to character strings on the 16x2 LCD display.
*   **FR-ARD-004 (Sensing Forwarding):** Pressing buttons D11-D13 or A0 must output raw interrupts/signals to the scenario generator.

---

## 4. Hardware Constraints

*   **SPI Bus Timing:** Maximum SCLK frequency = 10 MHz. Master data must be stable at least 15ns before SCLK rising edges.
*   **UART Bus Timing:** Baud rate = 9600, tolerance = +/- 1.5%.
*   **FPGA Clock:** Internal system clock frequency = 100 MHz.
*   **Voltage Levels:** STM32 inputs operate at 3.3V (5V tolerant pins). Arduino UNO operates at 5V logic. Hardware level-shifters (e.g. TXB0104) are required for physical pins.