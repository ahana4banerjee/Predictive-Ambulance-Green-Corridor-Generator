#!/usr/bin/env python3
"""
verify_map.py
Validates the 3x3 city grid topology, assigns hospital at Junction I,
identifies ambulance starting positions, and prints all possible paths to verify routing options.
"""

import os
import json

def load_map_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def build_adjacency_list(nodes, edges):
    adj = {node['id']: [] for node in nodes}
    for edge in edges:
        u = edge['from']
        v = edge['to']
        dist = edge['distance']
        # Since edges are bidirectional
        adj[u].append((v, dist))
        adj[v].append((u, dist))
    return adj

def find_all_paths(adj, start, end, path=None):
    if path is None:
        path = []
    
    path = path + [start]
    
    if start == end:
        return [path]
    
    paths = []
    for node, dist in adj[start]:
        if node not in path:
            newpaths = find_all_paths(adj, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
                
    return paths

def calculate_path_distance(path, adj):
    dist_sum = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        for neighbor, d in adj[u]:
            if neighbor == v:
                dist_sum += d
                break
    return dist_sum

def print_ascii_grid():
    grid = """
         [A] --------- [B] --------- [C]
          |             |             |
          |             |             |
         [D] --------- [E] --------- [F]
          |             |             |
          |             |             |
         [G] --------- [H] --------- [I]  <- [Hospital]
    """
    print(grid)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'city_map.json')
    
    print("==================================================")
    print("       City Map Verification Tool (Week 1 Day 2)   ")
    print("==================================================")
    
    # 1. Load JSON file
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return
        
    map_data = load_map_data(json_path)
    print(f"Loaded Map: {map_data['map_name']}")
    print(f"Grid Layout: {map_data['dimensions']['rows']}x{map_data['dimensions']['columns']}")
    
    # 2. Print ASCII Grid
    print("\nNetwork Layout Diagram:")
    print_ascii_grid()
    
    # 3. Build Graph
    nodes = map_data['nodes']
    edges = map_data['edges']
    adj = build_adjacency_list(nodes, edges)
    
    # 4. Perform Validations
    print("Running Map Verifications:")
    
    # Check node count
    expected_nodes = {"A", "B", "C", "D", "E", "F", "G", "H", "I"}
    loaded_nodes = {node['id'] for node in nodes}
    
    if loaded_nodes == expected_nodes:
        print("  [OK] All 9 nodes (A through I) defined correctly.")
    else:
        print(f"  [ERROR] Node mismatch! Expected A-I, got: {loaded_nodes}")
        return
        
    # Check Hospital Assignment
    hospital_node = next((node for node in nodes if node['is_hospital']), None)
    if hospital_node and hospital_node['id'] == map_data['destination_node'] and hospital_node['id'] == 'I':
        print(f"  [OK] Hospital correctly assigned to node '{hospital_node['id']}' ({hospital_node['label']}).")
    else:
        print("  [ERROR] Hospital assignment error! Must be at Junction I.")
        return
        
    # Check Ambulance Start Nodes
    start_nodes = map_data['ambulance_start_nodes']
    expected_starts = ["A", "B", "C", "D", "E", "F", "G", "H"]
    if sorted(start_nodes) == sorted(expected_starts):
        print("  [OK] Ambulance start nodes defined correctly (Junctions A through H, excluding Hospital I).")
    else:
        print(f"  [ERROR] Invalid ambulance start nodes: {start_nodes}")
        return

    # Check Connectivity and Path Count
    print("\nRouting Analysis (Possible paths to Hospital I):")
    all_starts_have_paths = True
    
    # Route Options verification for starting positions
    for start in expected_starts:
        paths = find_all_paths(adj, start, 'I')
        path_count = len(paths)
        print(f"  - From {start} to I: Found {path_count} unique paths")
        
        # Sort paths by length
        paths_with_dists = [(p, calculate_path_distance(p, adj)) for p in paths]
        paths_with_dists.sort(key=lambda x: (x[1], len(x[0])))
        
        # Print top 3 shortest paths
        print("    Shortest options:")
        for idx, (path, dist) in enumerate(paths_with_dists[:3]):
            path_str = " -> ".join(path)
            print(f"      Option {idx+1}: {path_str} (Distance: {dist:.1f} segments)")
            
        if path_count < 3:
            all_starts_have_paths = False
            
    if all_starts_have_paths:
        print("\n  [OK] Validation passed: Every starting position has at least 3 distinct routing options to Junction I.")
    else:
        print("\n  [ERROR] Validation failed: Some junctions have less than 3 paths to Junction I.")
        return
        
    print("\nVerification Complete. The city network layout is valid and ready for firmware/HDL implementation.")
    print("==================================================")

if __name__ == "__main__":
    main()
