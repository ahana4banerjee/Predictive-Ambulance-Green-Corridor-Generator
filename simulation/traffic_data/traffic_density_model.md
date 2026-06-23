# Traffic Density Model

**Predictive Ambulance Green Corridor Generator — Traffic Layer**

---

This document establishes the traffic density classification system and defines how traffic volume at intersections affects route optimization calculations.

## 1. Traffic Density Thresholds

Traffic density at each of the 9 junctions is monitored by counting virtual vehicles. Based on the vehicle counts, traffic at any intersection is classified into three categories:

| Traffic Classification | Vehicle Count Range | Cost Penalty Weight | Description |
|---|---|---|---|
| 🟢 **LOW Density** | 0 – 10 vehicles | **+0.0** | Free-flowing traffic. No routing penalty is applied. |
| 🟡 **MEDIUM Density**| 11 – 25 vehicles | **+2.0** | Moderate congestion. Adds a minor cost penalty to avoid if alternatives exist. |
| 🔴 **HIGH Density** | 26+ vehicles | **+5.0** | Heavy bottleneck / bumper-to-bumper. Severe routing penalty to force bypass. |

---

## 2. Route Cost Weighting Model

The STM32 Route Optimizer calculates the optimal path using Dijkstra's algorithm. The cost of traversing a road segment between junction $u$ and junction $v$ is modeled as:

$$\text{Cost}(u \to v) = \text{Base Distance}(u, v) + \text{Penalty}(v)$$

Where:
* $\text{Base Distance}(u, v) = 1.0$ segment unit for all adjacent nodes.
* $\text{Penalty}(v)$ is the penalty of the destination junction $v$ based on its traffic density class.

The total cost of a route is the sum of segment costs along the path:

$$\text{Total Cost} = \sum_{i=0}^{N-1} \text{Cost}(Node_i \to Node_{i+1})$$

---

## 3. Cost Calculation Example

Consider two alternative paths from **Junction A to Hospital (I)** where:
* **Route 1:** `A -> B -> C -> F -> I` (4 segments)
* **Route 2:** `A -> D -> G -> H -> I` (4 segments)

### Scenario:
* Junction B is heavily congested (**HIGH** density, count = 30)
* Junction D has low traffic (**LOW** density, count = 5)
* All other junctions (C, E, F, G, H) have low traffic (**LOW** density, count <= 10)

### Cost Analysis:
1. **Route 1 Cost Calculation:**
   $$\text{Cost}(A \to B) = 1.0 (\text{base}) + 5.0 (\text{HIGH penalty at B}) = 6.0$$
   $$\text{Cost}(B \to C) = 1.0 (\text{base}) + 0.0 (\text{LOW penalty at C}) = 1.0$$
   $$\text{Cost}(C \to F) = 1.0 (\text{base}) + 0.0 (\text{LOW penalty at F}) = 1.0$$
   $$\text{Cost}(F \to I) = 1.0 (\text{base}) + 0.0 (\text{LOW penalty at I}) = 1.0$$
   $$\text{Total Cost (Route 1)} = 6.0 + 1.0 + 1.0 + 1.0 = \mathbf{9.0}$$

2. **Route 2 Cost Calculation:**
   $$\text{Cost}(A \to D) = 1.0 (\text{base}) + 0.0 (\text{LOW penalty at D}) = 1.0$$
   $$\text{Cost}(D \to G) = 1.0 (\text{base}) + 0.0 (\text{LOW penalty at G}) = 1.0$$
   $$\text{Cost}(G \to H) = 1.0 (\text{base}) + 0.0 (\text{LOW penalty at H}) = 1.0$$
   $$\text{Cost}(H \to I) = 1.0 (\text{base}) + 0.0 (\text{LOW penalty at I}) = 1.0$$
   $$\text{Total Cost (Route 2)} = 1.0 + 1.0 + 1.0 + 1.0 = \mathbf{4.0}$$

**Decision:** The Route Optimizer selects **Route 2** because it has a significantly lower cost ($\mathbf{4.0 < 9.0}$), successfully routing the ambulance away from the congestion at Junction B.
