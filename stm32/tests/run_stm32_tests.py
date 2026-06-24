#!/usr/bin/env python3
"""
run_stm32_tests.py
Mocks the C logic for the STM32 Traffic Monitor module and runs the test suite
to verify correctness of the classification algorithm.
"""

# Enum representations
DENSITY_LOW = 0
DENSITY_MEDIUM = 1
DENSITY_HIGH = 2

NODE_A = 0
NODE_B = 1
NODE_C = 2
NODE_D = 3
NODE_E = 4
NODE_F = 5
NODE_G = 6
NODE_H = 7
NODE_I = 8

class TrafficState:
    def __init__(self):
        self.vehicle_counts = [0] * 9
        self.density_levels = [DENSITY_LOW] * 9

def traffic_monitor_init(state):
    state.vehicle_counts = [0] * 9
    state.density_levels = [DENSITY_LOW] * 9

def traffic_monitor_set_vehicle_count(state, node, count):
    if 0 <= node < 9:
        state.vehicle_counts[node] = count

def traffic_monitor_update_density(state):
    for i in range(9):
        count = state.vehicle_counts[i]
        if count <= 10:
            state.density_levels[i] = DENSITY_LOW
        elif count <= 25:
            state.density_levels[i] = DENSITY_MEDIUM
        else:
            state.density_levels[i] = DENSITY_HIGH

def density_to_string(density):
    if density == DENSITY_LOW:
        return "LOW"
    elif density == DENSITY_MEDIUM:
        return "MEDIUM"
    elif density == DENSITY_HIGH:
        return "HIGH"
    return "UNKNOWN"

def traffic_monitor_print_report(state):
    print("=========================================")
    print("        Traffic Monitor Report           ")
    print("=========================================")
    print("Junction | Vehicle Count | Density Class")
    print("---------|---------------|---------------")
    for i in range(9):
        junction_label = chr(ord('A') + i)
        print(f"    {junction_label}    |      {state.vehicle_counts[i]:3d}      | {density_to_string(state.density_levels[i])}")
    print("=========================================")

# Tests
failed_tests = 0

def run_test(name, func):
    global failed_tests
    print(f"Running {name}... ", end="")
    if func():
        print("PASS")
    else:
        print("FAIL")
        failed_tests += 1

def test_init():
    state = TrafficState()
    traffic_monitor_init(state)
    for i in range(9):
        if state.vehicle_counts[i] != 0: return False
        if state.density_levels[i] != DENSITY_LOW: return False
    return True

def test_typical_classification():
    state = TrafficState()
    traffic_monitor_init(state)
    
    traffic_monitor_set_vehicle_count(state, NODE_A, 35)
    traffic_monitor_set_vehicle_count(state, NODE_B, 12)
    traffic_monitor_set_vehicle_count(state, NODE_C, 48)
    traffic_monitor_set_vehicle_count(state, NODE_D, 5)
    traffic_monitor_set_vehicle_count(state, NODE_E, 18)
    traffic_monitor_set_vehicle_count(state, NODE_F, 8)
    traffic_monitor_set_vehicle_count(state, NODE_G, 3)
    traffic_monitor_set_vehicle_count(state, NODE_H, 22)
    traffic_monitor_set_vehicle_count(state, NODE_I, 0)
    
    traffic_monitor_update_density(state)
    
    if state.density_levels[NODE_A] != DENSITY_HIGH: return False
    if state.density_levels[NODE_B] != DENSITY_MEDIUM: return False
    if state.density_levels[NODE_C] != DENSITY_HIGH: return False
    if state.density_levels[NODE_D] != DENSITY_LOW: return False
    if state.density_levels[NODE_E] != DENSITY_MEDIUM: return False
    if state.density_levels[NODE_F] != DENSITY_LOW: return False
    if state.density_levels[NODE_G] != DENSITY_LOW: return False
    if state.density_levels[NODE_H] != DENSITY_MEDIUM: return False
    if state.density_levels[NODE_I] != DENSITY_LOW: return False
    
    print()
    traffic_monitor_print_report(state)
    return True

def test_boundary_classification():
    state = TrafficState()
    traffic_monitor_init(state)
    
    traffic_monitor_set_vehicle_count(state, NODE_A, 10)
    traffic_monitor_set_vehicle_count(state, NODE_B, 11)
    traffic_monitor_set_vehicle_count(state, NODE_C, 25)
    traffic_monitor_set_vehicle_count(state, NODE_D, 26)
    
    traffic_monitor_update_density(state)
    
    if state.density_levels[NODE_A] != DENSITY_LOW: return False
    if state.density_levels[NODE_B] != DENSITY_MEDIUM: return False
    if state.density_levels[NODE_C] != DENSITY_MEDIUM: return False
    if state.density_levels[NODE_D] != DENSITY_HIGH: return False
    
    return True

def main():
    print("=========================================")
    print("     Traffic Monitor Unit Test Suite     ")
    print("=========================================")
    
    run_test("test_init", test_init)
    run_test("test_typical_classification", test_typical_classification)
    run_test("test_boundary_classification", test_boundary_classification)
    
    print("\nTest Suite Completed: ", end="")
    if failed_tests == 0:
        print("ALL TESTS PASSED")
        print("=========================================")
        return True
    else:
        print(f"{failed_tests} TEST(S) FAILED")
        print("=========================================")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
