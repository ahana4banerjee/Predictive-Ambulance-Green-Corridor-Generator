# Scenario Testing and Performance Evaluation Report

This report summarizes the multi-scenario testing and performance verification of the **Predictive Ambulance Green Corridor Generator** completed during Week 5.

---

## 1. Executive Summary

To validate the robustness of the route optimization, ETA prediction, and predictive preemption systems, the integration layers were tested across **five distinct scenarios** representing varying traffic conditions, start positions, and override contexts. 

The coordinated green corridor consistently yielded **0 red-light stops** for the ambulance across all transit scenarios, achieving **100% Corridor Efficiency** and saving up to **40 seconds** of critical travel time per emergency run.

---

## 2. Test Environment & Network State

The city is represented by a 3×3 junction grid (A through I), where Node I is the destination Hospital. Traffic density classifications are defined as:
*   **LOW (0–10 vehicles):** +0s cost penalty, 60s traversal base time
*   **MEDIUM (11–25 vehicles):** +2s cost penalty, 90s traversal base time
*   **HIGH (26+ vehicles):** +5s cost penalty, 150s traversal base time

### Traffic Densities for Scenarios

| Scenario | Start Node | Route Optimization Goal | Traffic Density Mapping (A–I) |
|---|---|---|---|
| **Scenario 1** | Node A | Pathfinding with low traffic | A: 0, B: 0, C: 0, D: 0, E: 0, F: 0, G: 0, H: 0, I: 0 |
| **Scenario 2** | Node A | Bypass high congestion on standard path | A: 0, B: 35 (H), C: 48 (H), D: 0, E: 15 (M), F: 0, G: 0, H: 0, I: 0 |
| **Scenario 3** | Node G | Mixed traffic route and ETA accuracy | A: 0, B: 0, C: 0, D: 12 (M), E: 2 (L), F: 35 (H), G: 0, H: 22 (M), I: 0 |
| **Scenario 4** | Node D | Preemption override in city-wide high traffic | A: 35 (H), B: 35 (H), C: 35 (H), D: 35 (H), E: 35 (H), F: 35 (H), G: 35 (H), H: 35 (H), I: 35 (H) |
| **Scenario 5** | N/A | Normal operations baseline verification | A: 0, B: 0, C: 0, D: 0, E: 0, F: 0, G: 0, H: 0, I: 0 (No ambulance) |

---

## 3. Results Analysis

### Scenario 1: Standard Route / Low Traffic
*   **Start Node:** A (0)
*   **Selected Path:** `A ➔ B ➔ C ➔ F ➔ I` (4 segments)
*   **Corridor Travel Time:** 240 seconds (4.0 minutes)
*   **Normal Travel Time:** 280 seconds (4.67 minutes)
*   **Performance Metrics:**
    *   *Travel Time Saved:* 40 seconds
    *   *Delay Reduction:* 14.29%
    *   *Red-Light Stops Avoided:* 4 (Normal mode required stops at A, B, F, and I)
    *   *Corridor Efficiency:* 100.00% (5/5 signals green on arrival)

### Scenario 2: Congested Route Bypass
*   **Start Node:** A (0)
*   **Selected Path:** `A ➔ D ➔ G ➔ H ➔ I` (4 segments, bypassing congested B and C)
*   **Corridor Travel Time:** 240 seconds (4.0 minutes)
*   **Normal Travel Time:** 270 seconds (4.50 minutes)
*   **Performance Metrics:**
    *   *Travel Time Saved:* 30 seconds
    *   *Delay Reduction:* 11.11%
    *   *Red-Light Stops Avoided:* 3 (Normal mode required stops at A, G, and I)
    *   *Corridor Efficiency:* 100.00% (5/5 signals green on arrival)

### Scenario 3: Mixed Traffic
*   **Start Node:** G (6)
*   **Selected Path:** `G ➔ H ➔ I` (2 segments)
*   **Corridor Travel Time:** 150 seconds (2.50 minutes)
*   **Normal Travel Time:** 150 seconds (2.50 minutes)
*   **Performance Metrics:**
    *   *Travel Time Saved:* 0 seconds (No red-light delays occurred during normal traversal at G and H arrival times)
    *   *Delay Reduction:* 0.00%
    *   *Red-Light Stops Avoided:* 2 (Red lights avoided at G and I)
    *   *Corridor Efficiency:* 100.00% (3/3 signals green on arrival)

### Scenario 4: City-Wide High Traffic
*   **Start Node:** D (3)
*   **Selected Path:** `D ➔ E ➔ F ➔ I` (3 segments)
*   **Corridor Travel Time:** 450 seconds (7.50 minutes)
*   **Normal Travel Time:** 490 seconds (8.17 minutes)
*   **Performance Metrics:**
    *   *Travel Time Saved:* 40 seconds
    *   *Delay Reduction:* 8.16%
    *   *Red-Light Stops Avoided:* 2 (Stops avoided at E and F)
    *   *Corridor Efficiency:* 100.00% (4/4 signals green on arrival)

### Scenario 5: No Ambulance Baseline
*   **Start Node:** N/A (No ambulance)
*   **Active Mode:** Normal cycling only
*   **Duration:** 120 seconds
*   **Verification:** Confirming that all signals cycle autonomously through RED, GREEN, and YELLOW phase times based on their configured junction offsets. Observations registered:
    *   RED state observations: 59
    *   GREEN state observations: 56
    *   YELLOW state observations: 2
    *   No preemption or emergency override commands were activated.

---

## 4. Performance Summary Table

The performance across all scenarios is summarized in the table below:

| Metric | S1 (Standard) | S2 (Bypass) | S3 (Mixed Traffic) | S4 (High Traffic) | S5 (No Ambulance) |
|---|:---:|:---:|:---:|:---:|:---:|
| **Start Junction** | A | A | G | D | None |
| **Optimized Route** | `A➔B➔C➔F➔I` | `A➔D➔G➔H➔I` | `G➔H➔I` | `D➔E➔F➔I` | N/A |
| **Normal Travel Time** | 280 s | 270 s | 150 s | 490 s | N/A |
| **Corridor Travel Time** | 240 s | 240 s | 150 s | 450 s | N/A |
| **Travel Time Saved** | **40 s** | **30 s** | **0 s** | **40 s** | N/A |
| **Delay Reduction %** | **14.29%** | **11.11%** | **0.00%** | **8.16%** | N/A |
| **Normal Stops** | 4 stops | 3 stops | 2 stops | 2 stops | N/A |
| **Corridor Stops** | 0 stops | 0 stops | 0 stops | 0 stops | N/A |
| **Red-Light Stops Avoided** | **4** | **3** | **2** | **2** | N/A |
| **Corridor Efficiency %** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | N/A |

---

## 5. Visual Dashboard Findings

The graphical chart saved at `results/graphs/travel_time_comparison.png` illustrates:
1.  **Travel Time Savings Comparison:** Displays side-by-side travel durations (in seconds) between Normal and Corridor modes. Shows significant reduction of transit time in high traffic (Scenario 4) and bypass conditions (Scenario 2).
2.  **Red-Light Stops Avoided:** Confirms the complete elimination of stops at intersections during emergency runs when the preemption corridor is active, reducing delays, wear-and-tear on vehicle components, and cross-traffic conflict risks.

---

## 6. Conclusion

The testing logs and parsed statistics confirm that the **Predictive Ambulance Green Corridor Generator** behaves exactly as specified:
1.  **Correct Dijkstra Pathfinding:** Integrates traffic densities to choose shorter paths (S1) or bypass highly congested roads (S2).
2.  **Preemptive Coordination:** Actively overrides downstream traffic signals, transitioning them to green sequentially ahead of the ambulance's predicted arrival, preventing red-light halts.
3.  **Autonomous Recovery:** Resets back to baseline signal cycles when the ambulance clears intersections and arrives at the hospital, minimizing disturbance to general traffic flows.
