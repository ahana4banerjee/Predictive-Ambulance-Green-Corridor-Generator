#!/usr/bin/env python3
"""
run_stm32_tests.py
Mocks the C logic for the STM32 Traffic Monitor and Ambulance Tracker modules,
running the automated test suite to verify correctness of both modules.
"""

# ============================================================================
# ENUMS & CONFIGURATIONS
# ============================================================================
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
NODE_NONE = 15

# ============================================================================
# MODULE 1: TRAFFIC MONITOR MOCK
# ============================================================================
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

# ============================================================================
# MODULE 2: AMBULANCE TRACKER MOCK
# ============================================================================
class AmbulanceState:
    def __init__(self):
        self.current_node = NODE_NONE
        self.destination = NODE_I
        self.speed = 1.0
        self.distance_remaining = 0
        self.emergency_active = False

class RouteDetails:
    def __init__(self):
        self.path = [NODE_NONE] * 9
        self.path_length = 0
        self.total_cost = 0.0

def ambulance_tracker_init(state, start_node):
    state.current_node = start_node
    state.destination = NODE_I
    state.speed = 1.0
    state.distance_remaining = 0
    state.emergency_active = (start_node != NODE_I)

def ambulance_tracker_set_route(state, route):
    current_index = -1
    for i in range(route.path_length):
        if route.path[i] == state.current_node:
            current_index = i
            break
            
    if current_index != -1:
        state.distance_remaining = route.path_length - 1 - current_index
    else:
        state.distance_remaining = route.path_length - 1 if route.path_length > 0 else 0
        
    state.emergency_active = (state.current_node != state.destination)

def ambulance_tracker_move_to_next(state, next_node):
    if next_node >= NODE_NONE:
        return
        
    if state.current_node == next_node:
        return
        
    state.current_node = next_node
    
    if state.distance_remaining > 0:
        state.distance_remaining -= 1
        
    if state.current_node == state.destination:
        state.emergency_active = False
        state.distance_remaining = 0

def node_to_char(node):
    if 0 <= node <= 8:
        return chr(ord('A') + node)
    return '?'

def ambulance_tracker_print_status(state):
    print("=========================================")
    print("        Ambulance Tracker Status         ")
    print("=========================================")
    print(f"Current Position   : {node_to_char(state.current_node)}")
    print(f"Destination        : {node_to_char(state.destination)}")
    print(f"Remaining Distance : {state.distance_remaining} segments")
    print(f"Current Speed      : {state.speed:.2f} units/sec")
    status_str = "ACTIVE [EMERGENCY]" if state.emergency_active else "INACTIVE [ARRIVED]"
    print(f"Emergency Status   : {status_str}")
    print("=========================================")

# ============================================================================
# RUNNER LOGIC
# ============================================================================
failed_tests = 0

def run_test(name, func):
    global failed_tests
    print(f"Running {name}... ", end="")
    if func():
        print("PASS")
    else:
        print("FAIL")
        failed_tests += 1

# Traffic Monitor tests
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

# Ambulance Tracker tests
def test_tracker_init():
    state = AmbulanceState()
    ambulance_tracker_init(state, NODE_A)
    if state.current_node != NODE_A: return False
    if state.destination != NODE_I: return False
    if state.speed != 1.0: return False
    if state.emergency_active != True: return False
    
    ambulance_tracker_init(state, NODE_I)
    if state.emergency_active != False: return False
    return True

def test_tracker_movement():
    state = AmbulanceState()
    ambulance_tracker_init(state, NODE_A)
    
    route = RouteDetails()
    route.path = [NODE_A, NODE_B, NODE_C, NODE_F, NODE_I]
    route.path_length = 5
    route.total_cost = 4.0
    
    ambulance_tracker_set_route(state, route)
    if state.distance_remaining != 4: return False
    if state.emergency_active != True: return False
    
    # Step B
    ambulance_tracker_move_to_next(state, NODE_B)
    if state.current_node != NODE_B: return False
    if state.distance_remaining != 3: return False
    
    # Step C
    ambulance_tracker_move_to_next(state, NODE_C)
    if state.current_node != NODE_C: return False
    if state.distance_remaining != 2: return False
    
    # Step F
    ambulance_tracker_move_to_next(state, NODE_F)
    if state.current_node != NODE_F: return False
    if state.distance_remaining != 1: return False
    
    print()
    ambulance_tracker_print_status(state)
    
    # Step I (Arrive)
    ambulance_tracker_move_to_next(state, NODE_I)
    if state.current_node != NODE_I: return False
    if state.distance_remaining != 0: return False
    if state.emergency_active != False: return False
    
    print()
    ambulance_tracker_print_status(state)
    return True

def main():
    print("=========================================")
    print("     STM32 Modules Unified Test Suite    ")
    print("=========================================")
    
    print("\n--- 1. Traffic Monitor Module ---")
    run_test("test_init", test_init)
    run_test("test_typical_classification", test_typical_classification)
    run_test("test_boundary_classification", test_boundary_classification)
    
    print("\n--- 2. Ambulance Tracker Module ---")
    run_test("test_tracker_init", test_tracker_init)
    run_test("test_tracker_movement", test_tracker_movement)
    
    print("\n=========================================")
    print("Test Suite Completed: ", end="")
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
