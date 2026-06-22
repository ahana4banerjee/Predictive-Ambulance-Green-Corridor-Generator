**Software Requirements Specification (SRS)**

**Predictive Ambulance Green Corridor Generator using Traffic-Aware Signal Coordination**

**1\. Introduction**

**1.1 Purpose**

The purpose of this project is to design and simulate an intelligent traffic management system capable of generating a predictive green corridor for ambulances. The system aims to reduce emergency response time by dynamically coordinating traffic signals based on ambulance location, route, speed, and current traffic conditions.

The project will be implemented using STM32CubeIDE, Vivado, and Tinkercad in a fully simulated environment before any hardware deployment.

**1.2 Scope**

The system will:

- Monitor traffic density at multiple intersections.
- Track ambulance movement in real time.
- Determine the optimal route to a hospital.
- Predict future ambulance positions.
- Coordinate traffic signals ahead of ambulance arrival.
- Measure performance improvements through analytics.

The project is intended as a smart-city traffic management solution that can later be extended to real-world deployments.

**2\. Problem Statement**

Emergency vehicles frequently experience delays due to traffic congestion and conventional traffic signal systems.

Current traffic systems typically:

- Operate on fixed timing schedules.
- Respond only when emergency vehicles reach an intersection.
- Lack coordination among neighboring traffic signals.
- Do not optimize routes based on current traffic conditions.

As a result, ambulances may lose valuable time during patient transport.

This project proposes a predictive traffic management system capable of proactively generating green corridors before the ambulance reaches intersections, thereby reducing delays and improving emergency response efficiency.

**3\. Objectives**

**Primary Objectives**

- Develop a predictive ambulance corridor generation system.
- Reduce ambulance travel delays.
- Coordinate multiple traffic signals automatically.
- Simulate a smart-city emergency traffic network.

**Secondary Objectives**

- Display real-time traffic conditions.
- Estimate ambulance arrival time.
- Provide route optimization.
- Generate performance analytics.
- Demonstrate FPGA-based traffic signal control.

**4\. Functional Requirements**

**FR-1 Traffic Monitoring**

The system shall monitor vehicle density at all intersections.

**Input**

- Vehicle count data

**Output**

- Traffic density classification:
  - Low
  - Medium
  - High

**FR-2 Ambulance Detection**

The system shall detect ambulance activation and initiate emergency mode.

**Input**

- Ambulance start command

**Output**

- Emergency mode enabled

**FR-3 Ambulance Tracking**

The system shall continuously track ambulance location and speed.

**Output**

- Current position
- Current speed
- Distance remaining

**FR-4 Route Selection**

The system shall determine the most efficient route to the hospital.

**Inputs**

- Road network
- Traffic density

**Output**

- Selected route

**FR-5 ETA Calculation**

The system shall estimate ambulance arrival time.

**Output**

- Estimated Time of Arrival (ETA)

**FR-6 Future Intersection Prediction**

The system shall predict future signal crossings based on ambulance movement.

**Output**

- Predicted arrival time at each intersection

**FR-7 Green Corridor Generation**

The system shall automatically coordinate traffic signals ahead of ambulance arrival.

**Output**

- Dynamic signal states

**FR-8 Emergency Signal Override**

The system shall override normal signal operation during emergency conditions.

**Output**

- Emergency green path

**FR-9 Signal Recovery**

The system shall restore normal signal operation after ambulance passage.

**Output**

- Normal traffic operation resumed

**FR-10 Analytics Generation**

The system shall calculate performance metrics.

**Metrics**

- Travel time saved
- Number of signals cleared
- Corridor efficiency
- Delay reduction percentage

**5\. Non-Functional Requirements**

**NFR-1 Reliability**

The system shall consistently generate correct signal decisions during simulations.

**NFR-2 Scalability**

The system architecture shall support future expansion to:

- More intersections
- More ambulances
- Larger city maps

**NFR-3 Maintainability**

Modules shall be independently designed and tested.

Examples:

- Traffic Module
- Tracking Module
- FPGA Module
- Dashboard Module

**NFR-4 Usability**

The system shall provide clear visualization of:

- Ambulance location
- Signal states
- Traffic conditions

**NFR-5 Performance**

Signal decisions should be generated immediately after receiving ambulance updates.

**NFR-6 Modularity**

The design shall allow independent modification of:

- Route optimization logic
- Traffic simulation
- Signal controller

without affecting the entire system.

**NFR-7 Portability**

The design shall support future migration to:

- STM32 hardware
- FPGA boards
- Real sensors

without major redesign.

**6\. Use Cases**

**Use Case 1: Normal Traffic Operation**

**Actor**

Traffic Management System

**Description**

Signals operate using normal traffic cycles.

**Outcome**

Normal city traffic flow maintained.

**Use Case 2: Ambulance Emergency Activation**

**Actor**

Emergency Operator

**Description**

Ambulance begins emergency route.

**Outcome**

Emergency mode activated.

**Use Case 3: Route Optimization**

**Actor**

System

**Description**

System evaluates traffic conditions and selects the fastest route.

**Outcome**

Optimal route generated.

**Use Case 4: Green Corridor Creation**

**Actor**

System

**Description**

Signals are coordinated ahead of ambulance movement.

**Outcome**

Continuous green path created.

**Use Case 5: Ambulance Arrival**

**Actor**

Ambulance

**Description**

Ambulance reaches destination hospital.

**Outcome**

Emergency mode terminated.

**Use Case 6: Analytics Generation**

**Actor**

Traffic Administrator

**Description**

System calculates corridor performance.

**Outcome**

Performance report generated.

**7\. Constraints**

**Technical Constraints**

- Project must initially operate entirely in simulation.
- No physical sensors are required.
- FPGA implementation limited to Vivado simulation.
- STM32 implementation limited to STM32CubeIDE simulation.

**Resource Constraints**

- Zero hardware cost during initial development.
- Development based on available tools:
  - Vivado
  - STM32CubeIDE
  - Tinkercad

**Time Constraints**

- Target completion period:
  - 5-6 weeks
  - 2-3 hours daily effort

**Project Constraints**

- Focus on a single-city simulation.
- Single ambulance support in first version.
- Advanced features may be added later.

**8\. Success Criteria**

The project shall be considered successful if:

- Ambulance route is generated successfully.
- Traffic conditions are monitored.
- Signals coordinate automatically.
- Green corridor is created before ambulance arrival.
- Travel time reduction is demonstrated.
- Analytics are displayed correctly.
- Complete simulation runs without manual signal intervention.