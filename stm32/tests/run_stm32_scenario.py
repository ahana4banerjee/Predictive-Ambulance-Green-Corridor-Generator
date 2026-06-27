# -*- coding: utf-8 -*-
# @file run_stm32_scenario.py
# @brief Simulates STM32 Traffic Intelligence on Scenario 2 and outputs virtual SPI packets.

import json
import os

NODE_A = 0
NODE_B = 1
NODE_C = 2
NODE_D = 3
NODE_E = 4
NODE_F = 5
NODE_G = 6
NODE_H = 7
NODE_I = 8

NODE_MAP = {
    "A": NODE_A, "B": NODE_B, "C": NODE_C,
    "D": NODE_D, "E": NODE_E, "F": NODE_F,
    "G": NODE_G, "H": NODE_H, "I": NODE_I
}

DENSITY_LOW = 0
DENSITY_MED = 1
DENSITY_HIGH = 2

def get_density_class(count):
    if count <= 10:
        return DENSITY_LOW
    elif count <= 25:
        return DENSITY_MED
    else:
        return DENSITY_HIGH

# Dijkstra Graph Weights
edges = [
    ("A", "B", 1.0), ("B", "C", 1.0), ("D", "E", 1.0), ("E", "F", 1.0),
    ("G", "H", 1.0), ("H", "I", 1.0), ("A", "D", 1.0), ("D", "G", 1.0),
    ("B", "E", 1.0), ("E", "H", 1.0), ("C", "F", 1.0), ("F", "I", 1.0)
]

def calculate_dijkstra_route(start, destination, traffic_counts):
    # Setup graph weights based on traffic density
    graph = {node: {} for node in NODE_MAP.keys()}
    for u, v, w in edges:
        v_penalty = 5.0 if get_density_class(traffic_counts[v]) == DENSITY_HIGH else (2.0 if get_density_class(traffic_counts[v]) == DENSITY_MED else 0.0)
        u_penalty = 5.0 if get_density_class(traffic_counts[u]) == DENSITY_HIGH else (2.0 if get_density_class(traffic_counts[u]) == DENSITY_MED else 0.0)
        
        graph[u][v] = w + v_penalty
        graph[v][u] = w + u_penalty

    # Standard Dijkstra Search
    queue = {node: float('inf') for node in graph}
    queue[start] = 0.0
    prev = {}
    
    while queue:
        u = min(queue, key=queue.get)
        dist_u = queue[u]
        if u == destination or dist_u == float('inf'):
            break
        del queue[u]
        for v, weight in graph[u].items():
            if v in queue:
                alt = dist_u + weight
                if alt < queue[v]:
                    queue[v] = alt
                    prev[v] = u
                    
    # Reconstruct path
    path = []
    curr = destination
    while curr in prev:
        path.append(curr)
        curr = prev[curr]
    path.append(start)
    path.reverse()
    return path

def pack_spi_frame(emg_active, current_node, target_node, eta_seconds, dist_remain):
    raw_val = 0
    raw_val |= (emg_active & 0x1) << 31
    raw_val |= (current_node & 0xF) << 27
    raw_val |= (target_node & 0xF) << 23
    raw_val |= (eta_seconds & 0xFFF) << 11
    raw_val |= (dist_remain & 0x7) << 8
    
    # Calculate checksum
    b3 = (raw_val >> 24) & 0xFF
    b2 = (raw_val >> 16) & 0xFF
    b1 = (raw_val >> 8) & 0xFF
    checksum = b3 ^ b2 ^ b1
    
    raw_val |= (checksum & 0xFF)
    return raw_val

def run_scenario():
    # Load Scenario 2: Congested Shortest Path
    scenario_path = "simulation/scenarios/scenario_bypass.json"
    with open(scenario_path, "r") as f:
        data = json.load(f)
    sc = data["scenario"]
    
    print("====================================================")
    print(f"      STM32 SIMULATOR: {sc['name']}")
    print("====================================================")
    print(f"Description: {sc['description']}")
    
    traffic_counts = sc["traffic_counts"]
    start_node = "A"
    dest_node = "I"
    
    # Calculate Dijkstra route
    route = calculate_dijkstra_route(start_node, dest_node, traffic_counts)
    print(f"Selected Route: {' -> '.join(route)}")
    assert route == sc["expected_route"], "Dijkstra routing failed to match expected bypass path!"
    print("Dijkstra Route verification: PASS\n")
    
    # Setup directory for virtual packet logs
    packets_dir = "simulation/virtual_bus/packets"
    os.makedirs(packets_dir, exist_ok=True)
    
    # Segment travel cost is 4 seconds per link (nominally)
    sec_per_segment = 4
    
    # Generate sequential SPI packets along the route
    for i in range(len(route)):
        curr_char = route[i]
        curr_id = NODE_MAP[curr_char]
        
        # If at hospital, override is complete
        emg_active = 1 if curr_char != dest_node else 0
        
        # Target node is the next coordinate on the path, or I if arrived
        tgt_char = route[i+1] if i < len(route)-1 else dest_node
        tgt_id = NODE_MAP[tgt_char]
        
        dist_remain = len(route) - 1 - i
        eta_seconds = dist_remain * sec_per_segment
        
        packed_frame = pack_spi_frame(emg_active, curr_id, tgt_id, eta_seconds, dist_remain)
        
        packet_file = os.path.join(packets_dir, f"spi_tx_{i+1:03d}.bin")
        with open(packet_file, "w") as pf:
            pf.write(f"0x{packed_frame:08X}\n")
            
        print(f"Step {i+1}: Ambulance @ {curr_char} -> Target: {tgt_char} | Hops remaining: {dist_remain} | ETA: {eta_seconds}s")
        print(f"        Virtual Register SPI Frame -> File: {packet_file} (Value: 0x{packed_frame:08X})")

    print("\nSUCCESS: Phase 2 STM32 simulation run generated 5 SPI packets successfully.")
    print("====================================================")

if __name__ == "__main__":
    run_scenario()
