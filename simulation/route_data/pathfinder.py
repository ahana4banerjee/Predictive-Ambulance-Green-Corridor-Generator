#!/usr/bin/env python3
"""
pathfinder.py
Implements Dijkstra-based traffic-aware route optimization and simulates
step-by-step ambulance movement, reporting current position, remaining distance, and ETA.
"""

import os
import json
import heapq

def load_map_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Traffic Density Classifications and Penalties
def get_traffic_penalty(vehicle_count):
    if vehicle_count <= 10:
        return 0.0     # LOW density
    elif vehicle_count <= 25:
        return 2.0     # MEDIUM density
    else:
        return 5.0     # HIGH density

def get_traffic_label(vehicle_count):
    if vehicle_count <= 10:
        return "LOW"
    elif vehicle_count <= 25:
        return "MEDIUM"
    else:
        return "HIGH"

# Dijkstra Algorithm taking traffic penalties into account
def dijkstra_route_optimizer(nodes, edges, traffic_counts, start_node, dest_node):
    # Build graph adj list with distances
    graph = {node['id']: [] for node in nodes}
    for edge in edges:
        u, v, dist = edge['from'], edge['to'], edge['distance']
        graph[u].append((v, dist))
        graph[v].append((u, dist))
        
    # Priority Queue: (cost, current_node, path)
    queue = [(0.0, start_node, [start_node])]
    visited = set()
    
    while queue:
        cost, node, path = heapq.heappop(queue)
        
        if node == dest_node:
            return path, cost
            
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor, base_dist in graph[node]:
            if neighbor not in visited:
                # Penalty is based on traffic at the destination node
                vehicles = traffic_counts.get(neighbor, 0)
                penalty = get_traffic_penalty(vehicles)
                edge_cost = base_dist + penalty
                
                heapq.heappush(queue, (cost + edge_cost, neighbor, path + [neighbor]))
                
    return None, float('inf')

# Calculate travel time for a single segment based on movement equations
def get_segment_travel_time(target_node, traffic_counts, base_speed=0.5):
    # Base travel time for 1.0 unit distance at 0.5 speed is 2.0 seconds
    base_time = 1.0 / base_speed 
    
    vehicles = traffic_counts.get(target_node, 0)
    density = get_traffic_label(vehicles)
    
    # Traffic multiplier factor alpha
    if density == "LOW":
        alpha = 0.0
    elif density == "MEDIUM":
        alpha = 0.5
    else:
        alpha = 1.5
        
    return base_time * (1.0 + alpha)

# Simulates ambulance movement along a route step-by-step
def simulate_ambulance_traversal(route, traffic_counts, base_speed=0.5):
    print("\n--------------------------------------------------")
    print(f"Ambulance Traversal Simulation (Start: {route[0]} -> Destination: {route[-1]})")
    print("--------------------------------------------------")
    
    total_steps = len(route)
    current_position = route[0]
    
    # Calculate ETA array from each node to destination I
    eta_by_node = {}
    cumulative_time = 0.0
    
    # Work backwards from I to compute remaining travel times
    eta_by_node[route[-1]] = 0.0
    for idx in range(total_steps - 2, -1, -1):
        next_node = route[idx+1]
        segment_time = get_segment_travel_time(next_node, traffic_counts, base_speed)
        cumulative_time += segment_time
        eta_by_node[route[idx]] = cumulative_time

    # Simulate junction-by-junction movement
    for idx in range(total_steps):
        current_node = route[idx]
        distance_remaining = total_steps - 1 - idx
        remaining_eta = eta_by_node[current_node]
        
        minutes = int(remaining_eta) // 60
        seconds = int(remaining_eta) % 60
        
        print(f"Status Update - Node {idx+1}/{total_steps}:")
        print(f"  Current Position   : Junction {current_node}")
        print(f"  Distance Remaining : {distance_remaining} segment(s)")
        print(f"  Local Traffic      : {get_traffic_label(traffic_counts.get(current_node, 0))} ({traffic_counts.get(current_node, 0)} vehicles)")
        print(f"  Remaining Path     : {' -> '.join(route[idx:])}")
        print(f"  Predicted ETA      : {minutes:02d}m {seconds:02d}s (Total: {remaining_eta:.1f} sec)")
        print("  ................................................")
        
    print("Ambulance has safely arrived at Hospital (Junction I).")
    print("--------------------------------------------------")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Load JSON map from simulation/city_map/city_map.json
    map_path = os.path.join(script_dir, '..', 'city_map', 'city_map.json')
    map_data = load_map_data(map_path)
    
    # Define a sample traffic density counts at each node
    # Junction B has HIGH traffic, forcing the router to bypass it.
    traffic_scenario = {
        "A": 5,   # LOW
        "B": 35,  # HIGH (Avoid this!)
        "C": 12,  # MEDIUM
        "D": 8,   # LOW
        "E": 22,  # MEDIUM
        "F": 6,   # LOW
        "G": 4,   # LOW
        "H": 10,  # LOW
        "I": 0    # Hospital (Clear)
    }
    
    print("==================================================")
    print("      Dijkstra Traffic-Aware Route Optimization   ")
    print("==================================================")
    print("Active Traffic Density State:")
    for k, v in sorted(traffic_scenario.items()):
        print(f"  Junction {k}: {v:2d} vehicles -> Class: {get_traffic_label(v)}")
        
    start_node = "A"
    dest_node = "I"
    
    print(f"\nRequesting Optimal Route from {start_node} to {dest_node}...")
    
    route, cost = dijkstra_route_optimizer(
        map_data['nodes'], 
        map_data['edges'], 
        traffic_scenario, 
        start_node, 
        dest_node
    )
    
    if route:
        print("\nOptimization Result:")
        print(f"  Optimal Path: {' -> '.join(route)}")
        print(f"  Calculated Path Cost (Distance + Penalties): {cost:.1f}")
        
        # Verify the optimizer bypassed Junction B (congested)
        if "B" in route:
            print("  [WARNING] Route passes through highly congested Junction B.")
        else:
            print("  [SUCCESS] Route correctly bypassed highly congested Junction B.")
            
        # Simulate ambulance traversal
        simulate_ambulance_traversal(route, traffic_scenario)
    else:
        print("  [ERROR] No path could be resolved to the hospital.")

if __name__ == "__main__":
    main()
