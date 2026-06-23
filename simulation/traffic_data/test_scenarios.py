#!/usr/bin/env python3
"""
test_scenarios.py
Loads traffic scenarios from JSON, runs Dijkstra route optimization,
and compares actual results with expected routes and path costs.
"""

import os
import json
import heapq

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Traffic Density Penalty
def get_traffic_penalty(vehicle_count):
    if vehicle_count <= 10:
        return 0.0     # LOW
    elif vehicle_count <= 25:
        return 2.0     # MEDIUM
    else:
        return 5.0     # HIGH

# Dijkstra Optimizer
def dijkstra_route_optimizer(nodes, edges, traffic_counts, start_node, dest_node):
    graph = {node['id']: [] for node in nodes}
    for edge in edges:
        u, v, dist = edge['from'], edge['to'], edge['distance']
        graph[u].append((v, dist))
        graph[v].append((u, dist))
        
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
                vehicles = traffic_counts.get(neighbor, 0)
                penalty = get_traffic_penalty(vehicles)
                edge_cost = base_dist + penalty
                heapq.heappush(queue, (cost + edge_cost, neighbor, path + [neighbor]))
                
    return None, float('inf')

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    map_path = os.path.join(script_dir, '..', 'city_map', 'city_map.json')
    scenarios_path = os.path.join(script_dir, 'traffic_scenarios.json')
    
    map_data = load_json(map_path)
    scenarios_data = load_json(scenarios_path)
    
    print("==================================================")
    print("      Traffic Scenario Verification Test Suite    ")
    print("==================================================")
    print(f"Testing optimal routing (A -> I) across {len(scenarios_data['scenarios'])} scenarios.\n")
    
    passed_count = 0
    total_count = len(scenarios_data['scenarios'])
    
    for sc in scenarios_data['scenarios']:
        print(f"Running Test {sc['id']}: {sc['name']}")
        print(f"  Description: {sc['description']}")
        
        # Optimize Route
        actual_route, actual_cost = dijkstra_route_optimizer(
            map_data['nodes'],
            map_data['edges'],
            sc['traffic_counts'],
            "A",
            "I"
        )
        
        expected_route = sc['expected_route']
        expected_cost = sc['expected_cost']
        
        route_match = actual_route == expected_route
        cost_match = abs(actual_cost - expected_cost) < 0.01
        
        if route_match and cost_match:
            print("  Result: [PASS]")
            passed_count += 1
        else:
            print("  Result: [FAIL]")
            if not route_match:
                print(f"    Expected Route: {' -> '.join(expected_route)}")
                print(f"    Actual Route:   {' -> '.join(actual_route) if actual_route else 'None'}")
            if not cost_match:
                print(f"    Expected Cost:  {expected_cost}")
                print(f"    Actual Cost:    {actual_cost}")
                
        print("  ................................................")
        
    print(f"Test Suite Summary: {passed_count}/{total_count} Tests Passed.")
    print("==================================================")
    
    if passed_count == total_count:
        print("System verification successful. Traffic density cost weighting behaves as specified.")
    else:
        print("System verification failed. Please check scenario edge configurations.")

if __name__ == "__main__":
    main()
