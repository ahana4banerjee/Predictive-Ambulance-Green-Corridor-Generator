# City Network Design Documentation

**Predictive Ambulance Green Corridor Generator — City Map Layer**

---

This document defines the layout, connections, nodes, and topology of the simulated smart city traffic network. This topology serves as the single source of truth for the STM32 route optimization algorithm, the Vivado FSM signal controllers, and the Tinkercad visualization layer.

## 1. City Layout (3×3 Grid)

The city is structured as a standard 3×3 grid of 9 junctions labelled **A** through **I**. Each junction has a unique coordinate and set of adjacent roads.

```
          Junction A ───────── Junction B ───────── Junction C
              │                    │                    │
              │                    │                    │
              │                    │                    │
          Junction D ───────── Junction E ───────── Junction F
              │                    │                    │
              │                    │                    │
              │                    │                    │
          Junction G ───────── Junction H ───────── Junction I  [🏥 Hospital]
```

---

## 2. Nodes & Assignments

| Junction | Label | Role | Coordinates (X, Y) | Details |
|---|---|---|---|---|
| **A** | Junction A | Normal Intersection | (0, 2) | Corner node, possible starting position |
| **B** | Junction B | Normal Intersection | (1, 2) | Edge node, possible starting position |
| **C** | Junction C | Normal Intersection | (2, 2) | Corner node, possible starting position |
| **D** | Junction D | Normal Intersection | (0, 1) | Edge node, possible starting position |
| **E** | Junction E | Normal Intersection | (1, 1) | Center node, possible starting position |
| **F** | Junction F | Normal Intersection | (2, 1) | Edge node, possible starting position |
| **G** | Junction G | Normal Intersection | (0, 0) | Corner node, possible starting position |
| **H** | Junction H | Normal Intersection | (1, 0) | Edge node, possible starting position |
| **I** | Junction I | **Hospital Location** | (2, 0) | Destination node for all ambulance runs |

### Node Roles Summary:
- **Normal Intersections (A–H):** Act as traffic junctions with independent signal controllers. Each is a valid starting position for the ambulance.
- **Hospital (I):** The final destination for the ambulance. The green corridor terminates once the ambulance reaches Junction I.

---

## 3. Road Connections (Bidirectional Edges)

The city network contains **12 bidirectional roads** (edges) connecting adjacent junctions. Each connection is bidirectional, allowing vehicles and the ambulance to travel in either direction.

Each segment represents one unit of base distance (`1.0` segment length).

| Edge ID | Source Junction | Destination Junction | Base Distance |
|---|---|---|---|
| **1** | Junction A | Junction B | 1.0 segment |
| **2** | Junction B | Junction C | 1.0 segment |
| **3** | Junction D | Junction E | 1.0 segment |
| **4** | Junction E | Junction F | 1.0 segment |
| **5** | Junction G | Junction H | 1.0 segment |
| **6** | Junction H | Junction I | 1.0 segment |
| **7** | Junction A | Junction D | 1.0 segment |
| **8** | Junction D | Junction G | 1.0 segment |
| **9** | Junction B | Junction E | 1.0 segment |
| **10** | Junction E | Junction H | 1.0 segment |
| **11** | Junction C | Junction F | 1.0 segment |
| **12** | Junction F | Junction I | 1.0 segment |

---

## 4. Possible Routes to Hospital (I)

To demonstrate the routing intelligence, there are multiple alternative routes from starting positions to the hospital (Junction I). For example, from Junction A:

1. **Shortest Route (Option 1):** `A → B → C → F → I` (Length = 4)
2. **Shortest Route (Option 2):** `A → D → G → H → I` (Length = 4)
3. **Alternative Route (Option 3):** `A → D → E → H → I` (Length = 4)
4. **Alternative Route (Option 4):** `A → B → E → H → I` (Length = 4)
5. **Longer Alternative:** `A → D → E → F → I` (Length = 4)
6. **Indirect Alternative:** `A → B → E → F → I` (Length = 4)

If there is heavy traffic on Route 1 (e.g. at Junction B or C), the STM32 Route Optimizer will automatically divert the ambulance to Route 2 or Route 3.

---

## 5. Implementation Rules

1. **Traffic Density:** Vehicle counts at junctions dynamically affect route costs.
   - **LOW Traffic (0–10 vehicles):** Weight penalty = 0.
   - **MEDIUM Traffic (11–25 vehicles):** Weight penalty = +2 distance equivalents.
   - **HIGH Traffic (26+ vehicles):** Weight penalty = +5 distance equivalents.
   - **Route Cost Calculation:** $\text{Cost} = \sum \text{Base Distance} + \sum \text{Traffic Penalty}$.
2. **Ambulance Traversal:** The ambulance moves step-by-step from its starting node along the calculated optimal route until it reaches Junction I.
