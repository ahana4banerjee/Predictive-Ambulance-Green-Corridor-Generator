# Predictive Ambulance Green Corridor Generator

**Traffic-Aware Signal Coordination for Emergency Response**

---

## 1. Project Introduction

The **Predictive Ambulance Green Corridor Generator** is an ECE mini-project that designs and simulates an intelligent traffic management system capable of creating a predictive green corridor for ambulances.

Unlike conventional emergency traffic systems that react _after_ an ambulance reaches an intersection, this system **predicts the ambulance's future path** and **proactively coordinates traffic signals ahead of time** — clearing the route before the ambulance arrives.

The project operates entirely within a simulated environment using industry-standard ECE tools: **STM32CubeIDE**, **Vivado**, and **Tinkercad**, with an optional **Python-based analytics dashboard**.

> **Current Scope:**  Single ambulance · Single hospital · 9-junction city network

---

## 2. Problem Statement

Emergency vehicles frequently experience critical delays due to traffic congestion and the limitations of conventional traffic signal systems.

During patient transport, every second counts. Yet ambulances are forced to navigate through signals that have no awareness of their presence until they physically arrive at an intersection — resulting in preventable delays that can directly impact patient outcomes.

This project addresses the gap between **emergency urgency** and **traffic infrastructure intelligence** by building a system that anticipates, plans, and acts _before_ the ambulance reaches each signal.

---

## 3. Why Current Traffic Systems Fail

| Limitation | Impact |
|---|---|
| Signals operate on **fixed timing schedules** | No adaptation to emergency situations |
| Response occurs **only when the ambulance reaches an intersection** | Delays are unavoidable by design |
| **No coordination** among neighboring signals | Each intersection treats the ambulance as a new, unexpected event |
| **No route optimization** based on live traffic | Ambulances may travel through heavily congested corridors |

The result is a fundamentally **reactive** system in a situation that demands **proactive** intelligence.

---

## 4. Proposed Solution

This project creates a **virtual city traffic network** where:

- Traffic conditions at intersections change dynamically.
- Ambulance location and speed are tracked continuously.
- The optimal route to the hospital is calculated based on road distances and current traffic density.
- Future signal crossings are predicted using ambulance position, speed, and selected route.
- Traffic signals along the corridor coordinate **automatically and in advance**.
- Performance improvements are measured and reported through analytics.

### City Network Model

The system simulates a realistic **3×3 grid of 9 junctions** connected by bidirectional roads:

```
A --- B --- C
|         |         |
D --- E --- F
|         |         |
G --- H --- I

Hospital = Junction I
```

The ambulance can start at any junction and must reach **Hospital (I)** via the most efficient route.

---

## 5. Core Innovation

> **Most emergency traffic systems:**
> Ambulance arrives → Signal changes
>
> **This project:**
> Signal changes → _Then_ ambulance arrives

The system does not wait for the ambulance to request a green signal. Instead, it:

1. Knows where the ambulance is.
2. Knows where the ambulance is going.
3. Calculates which signals the ambulance will encounter next.
4. Prepares those signals **before the ambulance reaches them**.

This transforms traffic signal control from a **reactive mechanism** into a **predictive coordination system**.

---

## 6. Project Objectives

### Primary Objectives

- Develop a predictive ambulance corridor generation system.
- Reduce ambulance travel delays through proactive signal coordination.
- Coordinate multiple traffic signals automatically along the selected route.
- Simulate a smart-city emergency traffic network.

### Secondary Objectives

- Display real-time traffic conditions across all junctions.
- Estimate ambulance arrival time (ETA) at the hospital.
- Provide route optimization based on distance and traffic density.
- Generate performance analytics measuring corridor effectiveness.
- Demonstrate FPGA-based traffic signal control using FSM design.

---

## 7. System Workflow

The end-to-end operation of the system follows this sequence:

```
┌─────────────────────────────────────────────────────────────┐
│                    NORMAL OPERATION                         │
│  All 9 junctions cycle through RED → GREEN → YELLOW → RED  │
│  Traffic density is monitored at each intersection          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    Emergency Triggered
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  AMBULANCE ACTIVATED                        │
│  Starting junction identified                               │
│  Destination: Hospital (Junction I)                         │
│  Speed and position tracking begins                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  ROUTE OPTIMIZATION                         │
│  All possible routes to Hospital evaluated                  │
│  Traffic density at each junction considered                 │
│  Shortest + least congested route selected                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              GREEN CORRIDOR GENERATION                      │
│  Future intersections along route predicted                  │
│  Signals begin transitioning to GREEN before arrival        │
│  Corridor opens progressively ahead of ambulance            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               AMBULANCE REACHES HOSPITAL                    │
│  Emergency mode terminated                                  │
│  Signals return to normal operation (Recovery Mode)         │
│  Performance analytics generated                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Tool Responsibilities

The project is divided across four tools, each handling a distinct layer of the system.

### STM32CubeIDE — The City's Brain

STM32 acts as the **central traffic management computer**, responsible for all intelligence and decision-making.

| Responsibility | Description |
|---|---|
| Traffic Density Monitoring | Collects and classifies vehicle counts at each junction (Low / Medium / High) |
| Ambulance Tracking | Continuously tracks ambulance position, speed, and distance remaining |
| Route Optimization | Evaluates all routes and selects the fastest path based on distance and traffic |
| ETA Calculation | Estimates time of arrival at the hospital |

---

### Vivado — The Signal Controller

Vivado handles the **digital logic** of traffic signal control through FSM (Finite State Machine) design in Verilog.

| Responsibility | Description |
|---|---|
| Normal Traffic FSM | Cycles each signal through RED → GREEN → YELLOW → RED |
| Emergency Override FSM | Detects emergency, transitions through PREPARE → ACTIVE → RECOVERY states |
| Corridor Controller | Synchronizes multiple signals to open a green path ahead of the ambulance |

This component directly showcases **RTL design** and **digital logic** skills.

---

### Tinkercad — The Visual Demonstration

Tinkercad provides a **physical-world simulation** of the smart city using an Arduino UNO, LEDs, push buttons, and an LCD display.

| Responsibility | Description |
|---|---|
| Traffic Light Simulation | LEDs represent RED, YELLOW, and GREEN states at each intersection |
| Vehicle Density Sensors | Push buttons simulate vehicle arrivals at junctions |
| Ambulance Detection | A dedicated push button triggers emergency mode |
| Status Display | LCD shows ETA, corridor status, and active signal states |

---

### Dashboard — The Analytics Layer

An optional Python-based dashboard provides **performance measurement and visualization**.

| Responsibility | Description |
|---|---|
| Traffic Visualization | Displays current density at all junctions |
| Corridor Monitoring | Shows which signals are in emergency green mode |
| Performance Analytics | Reports travel time saved, signals cleared, delay reduction, and corridor efficiency |

---

## 9. Major Modules Overview

The system is organized into **six functional modules**, each with a clearly defined purpose.

| # | Module | Purpose |
|---|---|---|
| 1 | **Traffic Density Monitor** | Determines congestion levels (Low / Medium / High) at each of the 9 junctions based on vehicle counts |
| 2 | **Ambulance Tracking Module** | Tracks the ambulance's current position, speed, distance remaining, and ETA throughout its journey |
| 3 | **Route Optimization Module** | Selects the fastest route to Hospital (I) by evaluating road distances and current traffic densities |
| 4 | **Green Corridor Prediction Engine** | Predicts which intersections the ambulance will cross next and calculates preparation timing for each signal |
| 5 | **Signal Control Engine** | Controls traffic signal states through FSMs — managing Normal, Prepare Corridor, Emergency Green, and Recovery modes |
| 6 | **Analytics Engine** | Measures system effectiveness through metrics: travel time saved, average delay reduction, corridor efficiency, and signals cleared |

---

## 10. Expected Outcomes

Upon completion, the system will demonstrate:

- ✅ **Automatic route generation** — Ambulance route selected based on traffic conditions
- ✅ **Predictive signal coordination** — Signals turn green _before_ ambulance arrival, not after
- ✅ **Measurable time savings** — Comparison between normal travel time and corridor-assisted travel time
- ✅ **Complete simulation** — End-to-end operation without manual signal intervention
- ✅ **Visual demonstration** — Working Tinkercad circuit showing signal changes in response to ambulance activation
- ✅ **FPGA waveform verification** — Vivado simulation waveforms proving correct FSM operation under normal and emergency conditions
- ✅ **Performance analytics** — Dashboard displaying travel time saved, delay reduction, and corridor efficiency

---

## 11. Future Expansion Possibilities

The current system is designed with modularity and scalability in mind. Potential future enhancements include:

| Expansion | Description |
|---|---|
| **Multiple Ambulances** | Support for concurrent emergencies with priority assignment between ambulances |
| **Adaptive Route Switching** | Ambulance changes route mid-transit if traffic conditions shift unexpectedly |
| **Larger City Networks** | Expansion beyond the 9-junction grid to more complex city maps |
| **Multiple Hospitals** | Route optimization across several destination hospitals based on proximity and availability |
| **Hardware Deployment** | Migration from simulation to physical STM32 boards, FPGA hardware, and real sensors |

> **Note:** These are documented possibilities for future work. The current project scope is limited to a single ambulance, single hospital, and 9-junction network in a fully simulated environment.

---

## 12. Key Learning Outcomes for ECE Students

This project provides hands-on experience across multiple core ECE disciplines:

| Discipline | What You Learn |
|---|---|
| **Embedded Systems** | Designing modular firmware in STM32CubeIDE — traffic monitoring, tracking, route optimization, and ETA calculation |
| **Digital Logic Design** | Building FSMs in Verilog using Vivado — state transitions, signal synchronization, and emergency override logic |
| **Circuit Simulation** | Creating functional circuit prototypes in Tinkercad — LED signal mapping, button-based sensor simulation, and LCD interfacing |
| **System Architecture** | Decomposing a complex problem into independent, interacting modules with clearly defined inputs and outputs |
| **Algorithm Design** | Implementing route selection based on weighted parameters (distance + traffic density) |
| **Data Analytics** | Measuring and visualizing system performance through quantitative metrics |
| **Technical Documentation** | Writing professional SRS, architecture documents, implementation guides, and project reports |
| **Version Control** | Managing a multi-component project through a structured GitHub repository |

---

## Project Constraints

- The project operates **entirely in simulation** — no physical sensors or hardware are required.
- FPGA implementation is limited to **Vivado behavioral simulation**.
- STM32 implementation is limited to **STM32CubeIDE simulation**.
- Target completion: **6 weeks** at 2–3 hours of daily effort.
- **Zero hardware cost** during initial development.

---

## Quick Links

| Document | Description |
|---|---|
| [Software Requirements Specification](SRS.md) | Functional and non-functional requirements, use cases, and constraints |
| [System Architecture](SYSTEM_ARCHITECTURE.md) | Module design, FPGA architecture, tool allocation, and network topology |
| [Implementation Guide](IMPLEMENTATION_GUIDE.md) | Step-by-step build instructions for each tool and module |
| [Development Roadmap](ROADMAP.md) | Week-by-week development plan with daily task breakdowns |

---

> **Predictive Ambulance Green Corridor Generator** — Turning traffic signals from obstacles into allies during emergencies.
