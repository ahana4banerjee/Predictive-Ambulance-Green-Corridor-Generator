# Development Roadmap

**Predictive Ambulance Green Corridor Generator using Traffic-Aware Signal Coordination**

---

## Project Timeline

| Parameter | Value |
|---|---|
| **Total Duration** | 6 Weeks |
| **Daily Effort** | 2 – 3 hours |
| **Weekly Effort** | ~15 – 18 hours |
| **Target** | Working demonstration by Week 3; polished deliverable by Week 6 |
| **Scope** | Single ambulance · Single hospital (Junction I) · 9-junction network |

### Milestone Overview

```
Week 1 ──── Week 2 ──── Week 3 ──── Week 4 ──── Week 5 ──── Week 6
  │            │            │            │            │            │
  ▼            ▼            ▼            ▼            ▼            ▼
Foundation  STM32       Vivado      Tinkercad   Integration   Final
& Design    Intelligence Signal      Smart City  & Analytics   Polish
            Modules     Control     Simulation
```

| Milestone | Week | Gate Criteria |
|---|---|---|
| **M1 — Design Complete** | End of Week 1 | City network finalized, all documents written, tools installed |
| **M2 — Intelligence Working** | End of Week 2 | STM32 console outputs traffic status, route, ETA, and ambulance position |
| **M3 — Signal Control Verified** | End of Week 3 | Vivado waveforms prove normal operation, emergency override, and corridor generation |
| **M4 — Visual Demo Ready** | End of Week 4 | Tinkercad circuit demonstrates signal changes on ambulance trigger |
| **M5 — Analytics Complete** | End of Week 5 | Dashboard shows time saved, efficiency, and comparison graphs |
| **M6 — Project Deliverable** | End of Week 6 | All screenshots captured, report written, presentation prepared |

---

## Dependencies

Understanding dependencies prevents blocked progress. Each week builds on the previous one.

```
Week 1 (Foundation)
  └──▶ Week 2 (STM32) — Requires: city network, density thresholds, route definitions
         └──▶ Week 3 (Vivado) — Requires: understanding of signal states and emergency flow
         │     └──▶ Week 5 (Integration) — Requires: STM32 + Vivado outputs for logging
         └──▶ Week 4 (Tinkercad) — Requires: signal mapping, ambulance trigger definition
               └──▶ Week 5 (Integration) — Requires: Tinkercad simulation for visual validation
                      └──▶ Week 6 (Polish) — Requires: all components working
```

| Dependency | From | To | Risk if Delayed |
|---|---|---|---|
| City network topology | Week 1 | Week 2, 3, 4 | All routing and signal logic is built on the 9-junction grid |
| Traffic density thresholds | Week 1 | Week 2 | Classification logic depends on LOW/MEDIUM/HIGH definitions |
| STM32 route + ETA data | Week 2 | Week 3 | Corridor controller needs predicted arrival times |
| FSM state definitions | Week 3 | Week 4 | Tinkercad LED mapping must match Vivado signal states |
| All module outputs | Week 2–4 | Week 5 | Analytics requires travel logs and signal state data |

---

## Risk Areas

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Vivado FSM simulation not producing expected waveforms | Medium | High | Start with the simplest FSM (signal_fsm.v) and verify before adding emergency logic |
| Route optimizer logic producing incorrect paths | Medium | Medium | Test with hardcoded scenarios before dynamic input; validate against hand-calculated routes |
| Tinkercad circuit becoming too complex for the simulator | Low | Medium | Limit to 3 intersections (9 LEDs) and 4 buttons; avoid unnecessary components |
| STM32 and Vivado integration mismatch | Medium | High | Define data interface (signal commands format) in Week 1 before implementation |
| Time overrun on Vivado testbench | Medium | Medium | Reuse test patterns; start with the 5 documented test cases only |
| Scope creep (adding multiple ambulances too early) | Low | High | Strictly follow single-ambulance scope; defer multi-ambulance to stretch goals |

---

## Stretch Goals

If the core scope is completed ahead of schedule (likely in Week 6), the following enhancements add significant value:

| Stretch Goal | Effort | Impact on Evaluators |
|---|---|---|
| **Adaptive Route Switching During Transit** — ambulance changes route mid-journey if traffic increases on the current path | ~4–6 hours | Very High — demonstrates dynamic decision-making |
| **Multiple Test Scenarios** — run 5+ different ambulance starting positions with varying traffic patterns | ~2–3 hours | High — shows system robustness |
| **Animated City Map** — simple Python visualization showing ambulance moving through the grid | ~3–4 hours | High — strong visual impact for presentations |

> **Recommendation:** Adaptive Route Switching will impress evaluators far more than adding a second ambulance. Prioritize it if time remains.

---

## Week 1 — Project Foundation

**Objective:** Understand the system, finalize the design, and prepare the development environment.

### Goals

- [ ] Establish complete project design and documentation
- [ ] Finalize the 9-junction city network with all road connections
- [ ] Define all system inputs, outputs, and data interfaces
- [ ] Install and verify all development tools

### Tasks

**Day 1 — Environment Setup**

- [x] Create project folder structure (all directories and placeholder files)
- [x] Create GitHub repository and push initial structure
- [x] Install and verify Vivado is operational
- [x] Install and verify STM32CubeIDE is operational
- [x] Create and verify Tinkercad account access

**Day 2 — City Network Design**

- [x] Define the 3×3 junction grid (A through I)
- [x] Document all road connections (bidirectional edges)
- [x] Assign Hospital to Junction I
- [x] Define possible ambulance starting positions (any junction except I)

**Day 3 — Route and Intersection Definitions**

- [x] List all possible routes from every junction to Hospital (I)
- [x] Define road distances between adjacent junctions
- [x] Identify which junctions have traffic signals (all 9)
- [x] Define ambulance movement model (junction-to-junction traversal)

**Day 4 — Traffic Density Model**

- [x] Define density thresholds: LOW (0–10), MEDIUM (11–25), HIGH (26+)
- [x] Create sample traffic scenarios for testing
- [x] Document how density affects route selection weighting

**Day 5 — System Interface Design**

- [ ] Define inputs for each module (Traffic Monitor, Tracker, Optimizer, ETA)
- [ ] Define outputs for each module
- [ ] Define data interface between STM32 layer and FPGA layer
- [ ] Define signal states and their mappings

**Day 6–7 — Documentation**

- [ ] Complete SRS document
- [ ] Complete System Architecture document
- [ ] Create architecture diagrams
- [ ] Review all documents for internal consistency

### Expected Outputs

- [ ] Finalized city network topology document
- [ ] Traffic density classification table
- [ ] Complete SRS with all 10 functional requirements
- [ ] System Architecture document with module definitions and FSM designs
- [ ] All development tools installed and verified

### Validation Checks

- [ ] Can you draw the 9-junction grid from memory with all connections?
- [ ] Can you list at least 3 different routes from Junction A to Hospital (I)?
- [ ] Are density thresholds documented and unambiguous?
- [ ] Do all documents reference the same junction labels, module names, and signal states?
- [ ] Does every module have clearly defined inputs and outputs?

---

## Week 2 — STM32 Traffic Intelligence

**Objective:** Build the brain of the system — traffic monitoring, ambulance tracking, route optimization, and ETA calculation.

### Goals

- [ ] Implement all 4 STM32 modules
- [ ] Produce console output showing traffic status, selected route, ETA, and ambulance position
- [ ] Validate route selection against hand-calculated expected results

### Tasks

**Day 1 — Project Setup and Traffic Monitor**

- [ ] Create STM32CubeIDE project (STM32F103C8 or equivalent)
- [ ] Create `traffic_monitor.c` and `traffic_monitor.h`
- [ ] Implement vehicle count simulation for all 9 junctions
- [ ] Implement density classification: LOW / MEDIUM / HIGH

**Day 2 — Traffic Simulation Testing**

- [ ] Test with known vehicle counts (e.g., A=35, B=12, C=48)
- [ ] Verify classification output: A=HIGH, B=MEDIUM, C=HIGH
- [ ] Test edge cases: exactly 10, 11, 25, 26 vehicles

**Day 3 — Ambulance Tracker**

- [ ] Create `ambulance_tracker.c`
- [ ] Implement variables: `current_position`, `destination`, `speed`, `distance_remaining`
- [ ] Implement junction-to-junction movement logic
- [ ] Test ambulance moving A → B → C → F → I

**Day 4 — Route Optimizer**

- [ ] Create `route_optimizer.c`
- [ ] Implement road distance data for all junction connections
- [ ] Implement route evaluation using distance + traffic density weighting
- [ ] Output: selected route as a sequence of junctions

**Day 5 — Route Validation**

- [ ] Test: when A–B–C route is congested, optimizer should select A–D–G–H–I
- [ ] Test: when all routes have LOW traffic, optimizer should select shortest path
- [ ] Verify at least 3 different starting positions produce correct routes

**Day 6 — ETA Calculator**

- [ ] Create `eta_calculator.c`
- [ ] Implement ETA = distance remaining ÷ speed
- [ ] Implement per-junction arrival time prediction
- [ ] Output: ETA in minutes and seconds

**Day 7 — Integration Testing**

- [ ] Run complete cycle: traffic simulation → route selection → ambulance tracking → ETA
- [ ] Verify serial monitor output shows all 4 data elements
- [ ] Test with at least 2 different traffic scenarios

### Expected Outputs

- [ ] `traffic_monitor.c` — classifies density at all 9 junctions
- [ ] `ambulance_tracker.c` — tracks position through selected route
- [ ] `route_optimizer.c` — selects optimal route based on distance + traffic
- [ ] `eta_calculator.c` — computes ETA and per-junction arrival times
- [ ] Serial monitor output showing: Traffic Status, Selected Route, Ambulance Position, ETA

### Validation Checks

- [ ] Does the Traffic Monitor correctly classify 0→LOW, 15→MEDIUM, 30→HIGH?
- [ ] Does the Route Optimizer avoid HIGH-density junctions when alternatives exist?
- [ ] Does the Ambulance Tracker update position each cycle and decrease distance remaining?
- [ ] Does the ETA decrease as the ambulance approaches the hospital?
- [ ] Can you run the entire system with different starting junctions and get reasonable results?

---

## Week 3 — Vivado Signal Control

**Objective:** Implement the RTL portion — traffic signal FSMs, emergency override, and corridor controller. This week demonstrates DLD/RTL skills.

### Goals

- [ ] Implement all 3 FSMs in Verilog
- [ ] Create the top-level module connecting all FSMs
- [ ] Write a testbench covering all 5 test cases
- [ ] Generate simulation waveforms proving correct operation

### Tasks

**Day 1 — Vivado Project Setup**

- [ ] Create Vivado project: GreenCorridorController
- [ ] Configure as RTL Project with Verilog language
- [ ] Create all source files: `signal_fsm.v`, `emergency_fsm.v`, `corridor_controller.v`, `green_corridor_top.v`

**Day 2 — Normal Signal FSM**

- [ ] Implement `signal_fsm.v` with states: RED, YELLOW, GREEN
- [ ] Implement state transitions: RED → GREEN → YELLOW → RED
- [ ] Add clock-based timing for each state duration

**Day 3 — Signal FSM Verification**

- [ ] Simulate `signal_fsm.v` independently
- [ ] Verify waveform shows correct state sequence: RED → GREEN → YELLOW → RED
- [ ] Verify timing is consistent across multiple cycles

**Day 4 — Emergency Override FSM**

- [ ] Implement `emergency_fsm.v` with states: NORMAL, EMERGENCY_DETECTED, PREPARE, ACTIVE, RECOVERY
- [ ] Implement transitions triggered by ambulance detection signal
- [ ] Verify NORMAL → EMERGENCY_DETECTED → PREPARE → ACTIVE → RECOVERY → NORMAL

**Day 5 — Corridor Controller**

- [ ] Implement `corridor_controller.v`
- [ ] Implement sequential signal coordination: Signal A → Signal B → Signal C open in order
- [ ] Connect corridor controller to both FSMs

**Day 6 — Top Module and Testbench**

- [ ] Implement `green_corridor_top.v` connecting all three modules
- [ ] Create `tb_green_corridor.v` with test cases:
  - [ ] Test 1: Normal traffic — no ambulance
  - [ ] Test 2: Single ambulance — green corridor generated
  - [ ] Test 3: Heavy traffic — verify signal behavior under load
  - [ ] Test 4: Signal failure — recovery mode activated
  - [ ] Test 5: Corridor completion — normal operation restored

**Day 7 — Waveform Generation and Documentation**

- [ ] Run full simulation
- [ ] Capture waveform screenshots showing normal operation
- [ ] Capture waveform screenshots showing emergency override
- [ ] Capture waveform screenshots showing corridor generation and recovery
- [ ] Save all waveforms to `vivado/waveforms/`

### Expected Outputs

- [ ] `signal_fsm.v` — verified normal traffic signal cycling
- [ ] `emergency_fsm.v` — verified emergency override lifecycle
- [ ] `corridor_controller.v` — verified multi-signal coordination
- [ ] `green_corridor_top.v` — all modules connected and operational
- [ ] `tb_green_corridor.v` — testbench covering all 5 test cases
- [ ] Waveform captures proving correct operation in all modes

### Validation Checks

- [ ] Does the Signal FSM cycle RED → GREEN → YELLOW → RED continuously when no emergency?
- [ ] Does the Emergency FSM transition through all 5 states in correct order?
- [ ] Does the Corridor Controller open signals sequentially (A before B before C)?
- [ ] Do signals return to normal cycling after the ambulance passes (Recovery)?
- [ ] Are all waveforms saved and clearly labeled?

---

## Week 4 — Tinkercad Smart City Simulation

**Objective:** Create a visual demonstration of the system using LEDs, push buttons, an LCD, and Arduino UNO.

### Goals

- [ ] Build a working traffic signal circuit for 3 intersections
- [ ] Implement ambulance detection via push button
- [ ] Display ETA, corridor status, and signal states on LCD
- [ ] Demonstrate complete green corridor activation visually

### Tasks

**Day 1 — Traffic Signal Circuit**

- [ ] Place Arduino UNO on Tinkercad workspace
- [ ] Add 9 LEDs (3 per intersection × 3 intersections)
- [ ] Wire LEDs to Arduino digital pins
- [ ] Add current-limiting resistors

**Day 2 — Signal Mapping**

- [ ] Map Intersection A: Red LED, Yellow LED, Green LED
- [ ] Map Intersection B: Red LED, Yellow LED, Green LED
- [ ] Map Intersection C: Red LED, Yellow LED, Green LED
- [ ] Verify all LEDs light correctly when pins are set HIGH

**Day 3 — Vehicle Density Buttons**

- [ ] Add 3 push buttons (one per intersection) for vehicle count simulation
- [ ] Wire buttons to Arduino input pins with pull-down resistors
- [ ] Program button press counting logic

**Day 4 — Ambulance Trigger**

- [ ] Add 1 dedicated push button for ambulance activation
- [ ] Wire to Arduino input pin
- [ ] Program emergency mode activation on button press

**Day 5 — Arduino Programming**

- [ ] Implement normal signal cycling: RED → GREEN → YELLOW → RED for all 3 intersections
- [ ] Implement emergency override: all corridor signals switch to GREEN on ambulance trigger
- [ ] Implement recovery: signals return to normal after ambulance passes

**Day 6 — LCD Integration**

- [ ] Connect 16×2 LCD display to Arduino
- [ ] Display ETA value
- [ ] Display corridor status (ACTIVE / INACTIVE)
- [ ] Display current signal states

**Day 7 — Complete Simulation Test**

- [ ] Test normal operation: all signals cycle correctly
- [ ] Test ambulance trigger: corridor activates, LEDs change
- [ ] Test recovery: signals return to normal
- [ ] Take screenshots of each state for documentation

### Expected Outputs

- [ ] Working Tinkercad circuit with 9 LEDs, 4 buttons, 1 LCD, 1 Arduino UNO
- [ ] Normal signal cycling demonstration
- [ ] Ambulance trigger → green corridor activation demonstration
- [ ] LCD displaying ETA, corridor status, and signal states
- [ ] Screenshots saved to `tinkercad/screenshots/`

### Validation Checks

- [ ] Do all 3 intersections cycle RED → GREEN → YELLOW → RED during normal mode?
- [ ] Does pressing the ambulance button immediately trigger corridor mode?
- [ ] Do corridor signals turn GREEN in the correct order (A → B → C)?
- [ ] Does the LCD display update correctly during each phase?
- [ ] Do signals recover to normal cycling after the corridor deactivates?

---

## Week 5 — Integration and Analytics

**Objective:** Connect all components, generate performance data, and build the analytics dashboard.

### Goals

- [ ] Create CSV logging of travel time, delays, and signal states
- [ ] Calculate performance metrics: time saved, efficiency, signals cleared
- [ ] Build analytics dashboard with comparison graphs
- [ ] Run multiple test scenarios

### Tasks

**Day 1 — CSV Logging**

- [ ] Define CSV format: timestamp, junction, signal_state, ambulance_position, traffic_density
- [ ] Implement logging from STM32 simulation output
- [ ] Log at least one complete ambulance run

**Day 2 — Statistics Generation**

- [ ] Parse CSV logs
- [ ] Calculate total travel time (normal mode vs. corridor mode)
- [ ] Calculate number of red-light stops avoided

**Day 3 — Performance Metrics**

- [ ] Calculate: Travel Time Saved = Normal Time − Corridor Time
- [ ] Calculate: Signals Cleared = count of signals that were green before ambulance arrival
- [ ] Calculate: Corridor Efficiency = (Signals Cleared ÷ Total Signals on Route) × 100%
- [ ] Calculate: Delay Reduction % = (Time Saved ÷ Normal Time) × 100%

**Day 4 — Dashboard**

- [ ] Create `dashboard/analytics.py`
- [ ] Implement data loading from CSV
- [ ] Create bar chart: Normal Travel Time vs. Corridor Travel Time
- [ ] Create metric display: Time Saved, Efficiency %, Signals Cleared

**Day 5 — Comparison Analysis**

- [ ] Run simulation: Ambulance from Junction A without corridor → record travel time
- [ ] Run simulation: Ambulance from Junction A with corridor → record travel time
- [ ] Generate side-by-side comparison

**Day 6–7 — Multi-Scenario Testing**

- [ ] Scenario 1: Ambulance from A, LOW traffic everywhere → verify shortest route
- [ ] Scenario 2: Ambulance from A, HIGH traffic on B–C → verify route avoidance
- [ ] Scenario 3: Ambulance from G, mixed traffic → verify correct route and ETA
- [ ] Scenario 4: Ambulance from D, all HIGH traffic → verify corridor still activates
- [ ] Scenario 5: No ambulance → verify normal operation only
- [ ] Save all results to `results/` and `dashboard/data/`

### Expected Outputs

- [ ] CSV log files for multiple ambulance runs
- [ ] `dashboard/analytics.py` — generates performance graphs
- [ ] Comparison table: Normal vs. Corridor mode
- [ ] Performance metrics: Time Saved, Efficiency, Signals Cleared, Delay Reduction
- [ ] Graphs saved to `dashboard/graphs/` and `results/graphs/`

### Validation Checks

- [ ] Does the corridor mode consistently show lower travel time than normal mode?
- [ ] Is corridor efficiency above 80% for standard scenarios?
- [ ] Do all 5 test scenarios produce reasonable, explainable results?
- [ ] Does the dashboard correctly load and visualize CSV data?
- [ ] Are all results reproducible (same input → same output)?

---

## Week 6 — Final Polish

**Objective:** Turn the project into a presentation-ready, professional deliverable.

### Goals

- [ ] Capture all screenshots and waveforms
- [ ] Prepare result tables and comparison graphs
- [ ] Write final project report
- [ ] Create presentation and demo script
- [ ] Conduct full end-to-end system validation

### Tasks

**Day 1 — Screenshot Capture**

- [ ] Vivado: project setup, RTL schematic view, simulation settings
- [ ] Vivado: waveforms for all 5 test cases
- [ ] STM32: serial monitor output with traffic status, route, ETA, position
- [ ] Tinkercad: circuit overview, normal mode, emergency mode, recovery mode
- [ ] Dashboard: graphs and metrics display
- [ ] Save all to `results/screenshots/`

**Day 2 — Result Tables**

- [ ] Create table: Traffic Density across all 9 junctions (sample scenario)
- [ ] Create table: Route comparison with and without optimization
- [ ] Create table: Signal states during normal vs. emergency mode
- [ ] Create table: Performance metrics summary

**Day 3 — Graphs**

- [ ] Graph: Travel Time Comparison (Normal vs. Corridor)
- [ ] Graph: Delay Reduction across scenarios
- [ ] Graph: Corridor Efficiency per scenario
- [ ] Save all to `results/graphs/`

**Day 4 — Presentation**

- [ ] Create PPT covering: Problem → Solution → Architecture → Demo → Results → Conclusion
- [ ] Include architecture diagrams, waveforms, Tinkercad screenshots, and analytics graphs
- [ ] Keep to 15–20 slides

**Day 5 — Demo Script**

- [ ] Write step-by-step demo script:
  1. Show normal city traffic
  2. Activate ambulance
  3. Show route selection
  4. Show ETA calculation
  5. Show FPGA signal coordination
  6. Show Tinkercad signals changing
  7. Show analytics: Time Saved, Efficiency
- [ ] Practice demo run (target: 5–8 minutes)

**Day 6 — Full System Run**

- [ ] Execute complete end-to-end demonstration
- [ ] Verify all components work together
- [ ] Fix any issues discovered
- [ ] Run stretch goal (Adaptive Route Switching) if time permits

**Day 7 — Final Review**

- [ ] Review all documentation for consistency
- [ ] Verify all files are committed to GitHub
- [ ] Verify README.md is complete and links to all documents
- [ ] Final push to repository

### Expected Outputs

- [ ] All screenshots organized in `results/screenshots/`
- [ ] All waveforms organized in `results/waveforms/`
- [ ] Performance graphs in `results/graphs/`
- [ ] Final project report in `docs/reports/`
- [ ] Presentation file ready
- [ ] Complete GitHub repository with all code, docs, and results

### Validation Checks

- [ ] Can you run the full demo from start to finish without errors?
- [ ] Do all screenshots clearly show the described behavior?
- [ ] Do waveforms match the expected FSM state transitions?
- [ ] Does the analytics dashboard produce the same results on repeated runs?
- [ ] Is every file in the repository meaningful (no empty placeholders remaining)?
- [ ] Would a visitor to the GitHub repository understand the project from the README alone?

---

## Success Criteria

The project is considered **complete and successful** when all of the following are met:

| # | Criterion | Validated By |
|---|---|---|
| 1 | Ambulance route is generated based on traffic conditions | STM32 serial output |
| 2 | Traffic density is monitored and classified at all 9 junctions | STM32 serial output |
| 3 | Traffic signals coordinate automatically without manual intervention | Vivado waveforms |
| 4 | Green corridor is created **before** ambulance arrival at each signal | Vivado waveforms + Tinkercad demo |
| 5 | Signals recover to normal operation after ambulance passes | Vivado waveforms + Tinkercad demo |
| 6 | Travel time reduction is demonstrated with numerical evidence | Analytics dashboard |
| 7 | Complete simulation runs end-to-end without manual signal control | Full system demo |
| 8 | All documentation is complete, consistent, and GitHub-ready | Repository review |

---

## Final Deliverables Checklist

### STM32CubeIDE

- [ ] Traffic Density Monitor (`traffic_monitor.c`)
- [ ] Ambulance Tracker (`ambulance_tracker.c`)
- [ ] Route Optimizer (`route_optimizer.c`)
- [ ] ETA Calculator (`eta_calculator.c`)

### Vivado

- [ ] Signal FSM (`signal_fsm.v`)
- [ ] Emergency Override FSM (`emergency_fsm.v`)
- [ ] Corridor Controller (`corridor_controller.v`)
- [ ] Top Module (`green_corridor_top.v`)
- [ ] Testbench (`tb_green_corridor.v`)
- [ ] Simulation waveforms for all test cases

### Tinkercad

- [ ] Traffic signal circuit (9 LEDs, 3 intersections)
- [ ] Vehicle density buttons (3 buttons)
- [ ] Ambulance trigger button (1 button)
- [ ] LCD status display
- [ ] Working Arduino code

### Analytics

- [ ] CSV logging implementation
- [ ] Performance metrics calculation
- [ ] Dashboard with comparison graphs (`analytics.py`)

### Documentation

- [ ] Software Requirements Specification (SRS)
- [ ] System Architecture Document
- [ ] Implementation Guide
- [ ] Development Roadmap
- [ ] Project Overview
- [ ] Architecture Document (root)
- [ ] README
- [ ] Final Report

---

> **Scope reminder:** Complete the single ambulance, single hospital, 9-junction system first. Only pursue stretch goals after all core deliverables are validated.