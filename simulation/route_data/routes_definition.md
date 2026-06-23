# Route and Intersection Definitions

**Predictive Ambulance Green Corridor Generator — Routing Layer**

---

This document defines the routing layout, intersection characteristics, and ambulance movement model for the Predictive Ambulance Green Corridor simulation.

## 1. Intersection Characteristics & Traffic Signals

All **9 junctions (A through I)** in the 3×3 grid are fully signalized intersections. Each intersection possesses a 3-light traffic signal (RED, YELLOW, GREEN) operating on a local timing controller during normal mode, and subject to override control from the emergency coordinator.

| Intersection | Signal ID | Digital Pin (Tinkercad) | RTL Instance (Vivado) |
|---|---|---|---|
| **Junction A** | SIGNAL_A | D2, D3, D4 | `signal_fsm_inst_A` |
| **Junction B** | SIGNAL_B | D5, D6, D7 | `signal_fsm_inst_B` |
| **Junction C** | SIGNAL_C | D8, D9, D10 | `signal_fsm_inst_C` |
| **Junction D** | SIGNAL_D | — (Virtual) | `signal_fsm_inst_D` |
| **Junction E** | SIGNAL_E | — (Virtual) | `signal_fsm_inst_E` |
| **Junction F** | SIGNAL_F | — (Virtual) | `signal_fsm_inst_F` |
| **Junction G** | SIGNAL_G | — (Virtual) | `signal_fsm_inst_G` |
| **Junction H** | SIGNAL_H | — (Virtual) | `signal_fsm_inst_H` |
| **Junction I** | SIGNAL_I (Hospital) | — (Virtual) | `signal_fsm_inst_I` |

---

## 2. Road Segment Distances

All adjacent roads in the 3×3 grid represent a single, uniform segment of equal base distance.

* **Base Segment Distance ($d_{base}$):** Defined as `1.0` unit (represents 500 meters or 0.5 km in real-world terms).
* **Grid Topology Connections:** 12 bidirectional edges.

$$\text{Distance}(u, v) = 1.0 \quad \text{for any connected } u, v \in \{A, B, C, D, E, F, G, H, I\}$$

---

## 3. Ambulance Movement Model

The ambulance moves through the grid from a starting junction to the hospital (Junction I) using a discrete, junction-to-junction traversal model.

### Traversal States
* **At Node:** The ambulance is currently situated at a specific junction (e.g. Node A).
* **In Transit:** The ambulance is travelling along a bidirectional edge from node $u$ to node $v$.
* **Arrival:** The ambulance enters the destination node (Junction I), terminating emergency status.

### Travel Time & Speed Equations
1. **Base Traversal Time ($T_{base}$):** The time required to travel one segment distance $d_{base}$ at the ambulance's base speed $V_{base}$:
   $$T_{base} = \frac{d_{base}}{V_{base}}$$
   *Standard configuration: $V_{base} = 0.5$ segments/second ($T_{base} = 2.0$ seconds per segment).*
2. **Dynamic Segment Travel Time ($T_{segment}$):** The actual traversal time is adjusted by traffic congestion at the destination junction $v$:
   $$T_{segment}(u \to v) = T_{base} \times (1 + \alpha_{v})$$
   Where $\alpha_{v}$ is the traffic density penalty coefficient at junction $v$:
   * **LOW Density (0–10 vehicles):** $\alpha_{v} = 0.0$ (no delay, $T_{segment} = 2.0$ seconds).
   * **MEDIUM Density (11–25 vehicles):** $\alpha_{v} = 0.5$ (50% delay, $T_{segment} = 3.0$ seconds).
   * **HIGH Density (26+ vehicles):** $\alpha_{v} = 1.5$ (150% delay, $T_{segment} = 5.0$ seconds).
3. **Green Corridor Override Benefit:** If the green corridor override is active at junction $v$ prior to ambulance arrival, the traffic delay is bypassed ($\alpha_v = 0.0$ regardless of density), guaranteeing minimum travel time ($T_{segment} = T_{base}$).

---

## 4. Possible Routes to Hospital (Junction I)

Below are all possible loop-free paths from each starting junction to the Hospital (I), sorted by shortest base path length:

### From Junction A to I:
* **Route A-1:** `A -> B -> C -> F -> I` (Distance: 4.0)
* **Route A-2:** `A -> B -> E -> F -> I` (Distance: 4.0)
* **Route A-3:** `A -> B -> E -> H -> I` (Distance: 4.0)
* **Route A-4:** `A -> D -> E -> F -> I` (Distance: 4.0)
* **Route A-5:** `A -> D -> E -> H -> I` (Distance: 4.0)
* **Route A-6:** `A -> D -> G -> H -> I` (Distance: 4.0)

### From Junction B to I:
* **Route B-1:** `B -> C -> F -> I` (Distance: 3.0)
* **Route B-2:** `B -> E -> F -> I` (Distance: 3.0)
* **Route B-3:** `B -> E -> H -> I` (Distance: 3.0)

### From Junction C to I:
* **Route C-1:** `C -> F -> I` (Distance: 2.0)
* **Route C-2:** `C -> B -> E -> F -> I` (Distance: 4.0)
* **Route C-3:** `C -> B -> E -> H -> I` (Distance: 4.0)

### From Junction D to I:
* **Route D-1:** `D -> E -> F -> I` (Distance: 3.0)
* **Route D-2:** `D -> E -> H -> I` (Distance: 3.0)
* **Route D-3:** `D -> G -> H -> I` (Distance: 3.0)

### From Junction E to I:
* **Route E-1:** `E -> F -> I` (Distance: 2.0)
* **Route E-2:** `E -> H -> I` (Distance: 2.0)
* **Route E-3:** `E -> D -> G -> H -> I` (Distance: 4.0)

### From Junction F to I:
* **Route F-1:** `F -> I` (Distance: 1.0)
* **Route F-2:** `F -> E -> H -> I` (Distance: 3.0)

### From Junction G to I:
* **Route G-1:** `G -> H -> I` (Distance: 2.0)
* **Route G-2:** `G -> D -> E -> F -> I` (Distance: 4.0)
* **Route G-3:** `G -> D -> E -> H -> I` (Distance: 4.0)

### From Junction H to I:
* **Route H-1:** `H -> I` (Distance: 1.0)
* **Route H-2:** `H -> E -> F -> I` (Distance: 3.0)
