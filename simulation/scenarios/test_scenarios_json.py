# -*- coding: utf-8 -*-
# @file test_scenarios_json.py
# @brief Verifies that all scenario JSON files compile and have correct keys.

import json
import os

def test_json_scenarios():
    scenarios_dir = "simulation/scenarios"
    files = [f for f in os.listdir(scenarios_dir) if f.endswith(".json")]
    
    print("====================================================")
    print("      Verifying Scenario JSON Configurations        ")
    print("====================================================")

    assert len(files) > 0, "No scenario JSON files found!"

    for f in files:
        filepath = os.path.join(scenarios_dir, f)
        print(f"Reading scenario file: {f}")
        
        with open(filepath, "r") as json_file:
            data = json.load(json_file)
            
            # Check structure
            assert "scenario" in data, f"File {f} is missing root 'scenario' block"
            sc = data["scenario"]
            
            # Check keys
            assert "id" in sc, f"File {f} is missing 'id'"
            assert "name" in sc, f"File {f} is missing 'name'"
            assert "description" in sc, f"File {f} is missing 'description'"
            assert "traffic_counts" in sc, f"File {f} is missing 'traffic_counts'"
            assert "expected_route" in sc, f"File {f} is missing 'expected_route'"
            
            # Validate traffic counts (A-I)
            counts = sc["traffic_counts"]
            for node in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
                assert node in counts, f"File {f} traffic_counts is missing node {node}"
                assert isinstance(counts[node], int), f"File {f} count for {node} must be integer"
            
            print(f"SUCCESS: {f} format is valid.")

    print("\nAll JSON configurations are well-formed and valid.")
    print("====================================================")

if __name__ == "__main__":
    test_json_scenarios()
