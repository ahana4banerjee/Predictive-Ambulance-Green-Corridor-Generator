# System Interface Design

**Predictive Ambulance Green Corridor Generator — Interfaces Layer**

---

This document outlines the inputs and outputs of the software modules, the register-level SPI data interface between the STM32 intelligence tier and the FPGA control tier, and the binary representation of the traffic signal states.

## 1. STM32 Module I/O Interfaces

The embedded software on the STM32 central controller is split into 4 logical modules. Below are the inputs and outputs defined for each module.

```
       [Vehicle Sensor Inputs] ──────────▶ [Traffic Monitor] ──────────┐
                                                                       ▼
    [Ambulance Trigger Switch] ──────────▶ [Ambulance Tracker] ──▶ [Route Optimizer]
                                                                       │
                                                                       ▼
                               [ETA Predictions] ◀────────────── [ETA Calculator]
```

### A. Traffic Density Monitor (`traffic_monitor.c`)
* **Inputs:**
  * Virtual vehicle counter pulses from raw junction sensors (simulated registers).
  * Sampling period timer interrupts.
* **Outputs:**
  * Active vehicle count array `uint8_t junction_counts[9]` (Junctions A–I).
  * Categorized traffic density array `DensityClass density_states[9]` (LOW, MEDIUM, HIGH).

### B. Ambulance Tracker (`ambulance_tracker.c`)
* **Inputs:**
  * System start/trigger interrupt (indicates ambulance has departed).
  * Selected start junction ID (Nodes A–H).
  * Segment arrival pulses (triggers when ambulance passes a junction).
* **Outputs:**
  * Current position `char current_node`.
  * Destination node `char destination_node` (fixed at 'I').
  * Traversal speed `float current_speed`.
  * Segment distance remaining `uint8_t distance_remaining`.

### C. Route Optimizer (`route_optimizer.c`)
* **Inputs:**
  * Map network topology lookup (fixed edges and distances).
  * Current position `char current_node` (from Tracker).
  * Traffic density array `density_states[9]` (from Monitor).
* **Outputs:**
  * Selected optimal path array `char optimal_route[9]` (sequence of junctions to Hospital I).

### D. ETA Calculator (`eta_calculator.c`)
* **Inputs:**
  * Selected path `optimal_route[9]`.
  * Ambulance speed `current_speed`.
  * Junction traffic congestion weights along the route.
* **Outputs:**
  * Cumulative ETA remaining `uint16_t global_eta_seconds` (time to reach I).
  * Per-junction arrival times list `uint16_t node_eta_seconds[9]`.

---

## 2. STM32-to-FPGA Hardware Interface

The STM32 CubeIDE firmware communicates the routing intelligence directly to the Vivado FPGA controller using a Serial Peripheral Interface (**SPI**) connection. 

* **SPI Role:** STM32 acts as the **SPI Master**; the FPGA acts as the **SPI Slave**.
* **Communication Frame:** 32-bit SPI transaction frame sent from STM32 to FPGA.

### 32-Bit Register Map (SPI Transmit Frame)

```
 31  30      27 26      23 22                  11 10   8 7          0
┌───┬──────────┬──────────┬──────────────────────┬──────┬────────────┐
│ E │ AMB_NODE │ TGT_NODE │      ETA_SECONDS     │ DIST │  CHECKSUM  │
└───┴──────────┴──────────┴──────────────────────┴──────┴────────────┘
```

| Bit Range | Field Name | Width | Type | Description |
|---|---|---|---|---|
| **31** | `EMG_ACTIVE` | 1 bit | bool | Active emergency override flag (1 = active, 0 = normal). |
| **30 – 27** | `AMB_NODE` | 4 bits | enum | Current ambulance position node code (0000=A, 0001=B, ..., 1000=I). |
| **26 – 23** | `TGT_NODE` | 4 bits | enum | Next corridor intersection node that needs to turn GREEN. |
| **22 – 11** | `ETA_SECONDS` | 12 bits | uint16 | Estimated time of arrival (in seconds) to `TGT_NODE` (0–4095s). |
| **10 – 8** | `DIST_REMAIN` | 3 bits | uint8 | Number of remaining segment nodes to hospital (0–7). |
| **7 – 0** | `CHECKSUM` | 8 bits | uint8 | Error correction check (XOR of the first 3 bytes). |

---

## 3. Traffic Signal State Mappings

The FPGA traffic signal controllers (normal FSM and emergency overrides) represent and map the signal states using a 2-bit binary structure. 

This mapping drives the output lines connecting to the physical light-emitting diodes (LEDs).

### 2-Bit Binary Map

| Binary Code | State Name | LED Outputs (Red, Yellow, Green) | Description |
|---|---|---|---|
| `00` | **STATE_RED** | Red = HIGH, Yellow = LOW, Green = LOW | Cross-street traffic flows. Ambulance path is blocked. |
| `01` | **STATE_YELLOW** | Red = LOW, Yellow = HIGH, Green = LOW | Transition state. Warning to clear the intersection. |
| `10` | **STATE_GREEN** | Red = LOW, Yellow = LOW, Green = HIGH | Normal traffic flows on ambulance path. |
| `11` | **STATE_EMG_GREEN** | Red = LOW, Yellow = LOW, Green = HIGH (Override) | Emergency corridor override. Signal is locked to GREEN. |

### Node Encoding Mappings (for SPI Frame)

```
0000 = A    0001 = B    0010 = C
0011 = D    0100 = E    0101 = F
0110 = G    0111 = H    1000 = I
```
