#!/usr/bin/env python3
"""
run_stm32_tests.py
Mocks the C logic for all 4 STM32 modules: Traffic Monitor, Ambulance Tracker,
Route Optimizer, and ETA Calculator, verifying correctness through an automated test suite.
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
# MODULE 3: ROUTE OPTIMIZER MOCK
# ============================================================================
edges_list = [
    (NODE_A, NODE_B, 1.0),
    (NODE_B, NODE_C, 1.0),
    (NODE_D, NODE_E, 1.0),
    (NODE_E, NODE_F, 1.0),
    (NODE_G, NODE_H, 1.0),
    (NODE_H, NODE_I, 1.0),
    (NODE_A, NODE_D, 1.0),
    (NODE_D, NODE_G, 1.0),
    (NODE_B, NODE_E, 1.0),
    (NODE_E, NODE_H, 1.0),
    (NODE_C, NODE_F, 1.0),
    (NODE_F, NODE_I, 1.0)
]

def get_traffic_penalty(count):
    if count <= 10:
        return 0.0
    elif count <= 25:
        return 2.0
    else:
        return 5.0

def route_optimizer_find_path(traffic, start, route):
    dist = [float('inf')] * 9
    visited = [False] * 9
    prev = [NODE_NONE] * 9
    
    dist[start] = 0.0
    
    for _ in range(9):
        u = -1
        min_dist = float('inf')
        for i in range(9):
            if not visited[i] and dist[i] < min_dist:
                min_dist = dist[i]
                u = i
                
        if u == -1 or u == NODE_I:
            break
            
        visited[u] = True
        
        for from_n, to_n, base_dist in edges_list:
            v = NODE_NONE
            if from_n == u:
                v = to_n
            elif to_n == u:
                v = from_n
                
            if v != NODE_NONE and not visited[v]:
                penalty = get_traffic_penalty(traffic.vehicle_counts[v])
                weight = base_dist + penalty
                
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    prev[v] = u
                    
    if dist[NODE_I] == float('inf'):
        route.path_length = 0
        route.total_cost = float('inf')
        return
        
    route.total_cost = dist[NODE_I]
    temp_path = []
    curr = NODE_I
    while curr != NODE_NONE:
        temp_path.append(curr)
        curr = prev[curr]
        
    temp_path.reverse()
    route.path_length = len(temp_path)
    for i in range(route.path_length):
        route.path[i] = temp_path[i]

def route_optimizer_print_route(route):
    if route.path_length == 0:
        print("=========================================")
        print("         No Route Available             ")
        print("=========================================")
        return
        
    print("=========================================")
    print("         Optimized Route Details         ")
    print("=========================================")
    print("Optimal Path       : ", end="")
    path_chars = [node_to_char(route.path[i]) for i in range(route.path_length)]
    print(" -> ".join(path_chars))
    print(f"Total Cost         : {route.total_cost:.2f}")
    print("=========================================")

# ============================================================================
# MODULE 4: ETA CALCULATOR MOCK
# ============================================================================
BASE_TIME_LOW = 60.0
BASE_TIME_MED = 90.0
BASE_TIME_HIGH = 150.0

def get_segment_base_time(count):
    if count <= 10:
        return BASE_TIME_LOW
    elif count <= 25:
        return BASE_TIME_MED
    else:
        return BASE_TIME_HIGH

def eta_calculator_calculate_eta(state, route, traffic):
    if state.current_node == state.destination:
        return 0
        
    current_index = -1
    for i in range(route.path_length):
        if route.path[i] == state.current_node:
            current_index = i
            break
            
    if current_index == -1 or current_index >= route.path_length - 1:
        return 0
        
    total_seconds = 0.0
    speed = state.speed if state.speed > 0.0 else 1.0
    
    for i in range(current_index, route.path_length - 1):
        target = route.path[i + 1]
        base_time = get_segment_base_time(traffic.vehicle_counts[target])
        total_seconds += (base_time / speed)
        
    return int(total_seconds)

def eta_calculator_predict_arrival_times(state, route, traffic, arrival_times):
    # Initialize all to 0
    for i in range(9):
        arrival_times[i] = 0
        
    if state.current_node == state.destination:
        return
        
    current_index = -1
    for i in range(route.path_length):
        if route.path[i] == state.current_node:
            current_index = i
            break
            
    if current_index == -1:
        return
        
    running_sum = 0.0
    speed = state.speed if state.speed > 0.0 else 1.0
    
    for i in range(current_index, route.path_length - 1):
        target = route.path[i + 1]
        base_time = get_segment_base_time(traffic.vehicle_counts[target])
        running_sum += (base_time / speed)
        arrival_times[target] = int(running_sum)

def eta_calculator_print_eta(eta_seconds):
    minutes = eta_seconds // 60
    seconds = eta_seconds % 60
    print("=========================================")
    print("            Estimated ETA Report         ")
    print("=========================================")
    print(f"Remaining Time     : {minutes:02d} min {seconds:02d} sec")
    print(f"Total Seconds      : {eta_seconds} s")
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

# Route Optimizer tests
def test_shortest_path_low_traffic():
    traffic = TrafficState()
    traffic_monitor_init(traffic)
    
    route = RouteDetails()
    route_optimizer_find_path(traffic, NODE_A, route)
    
    expected = [NODE_A, NODE_B, NODE_C, NODE_F, NODE_I]
    if route.path_length != 5: return False
    for i in range(5):
        if route.path[i] != expected[i]: return False
    if route.total_cost != 4.0: return False
    return True

def test_bypass_congested_route():
    traffic = TrafficState()
    traffic_monitor_init(traffic)
    
    # Congest Junction B, C and E to force path G-H-I
    traffic_monitor_set_vehicle_count(traffic, NODE_B, 35)
    traffic_monitor_set_vehicle_count(traffic, NODE_C, 48)
    traffic_monitor_set_vehicle_count(traffic, NODE_E, 15)
    
    route = RouteDetails()
    route_optimizer_find_path(traffic, NODE_A, route)
    
    expected = [NODE_A, NODE_D, NODE_G, NODE_H, NODE_I]
    
    print()
    route_optimizer_print_route(route)
    
    if route.path_length != 5: return False
    for i in range(5):
        if route.path[i] != expected[i]: return False
    if route.total_cost != 4.0: return False
    return True

def test_different_start_positions():
    traffic = TrafficState()
    traffic_monitor_init(traffic)
    
    # Start at E, B and F congested
    traffic_monitor_set_vehicle_count(traffic, NODE_B, 30)
    traffic_monitor_set_vehicle_count(traffic, NODE_F, 30)
    
    route1 = RouteDetails()
    route_optimizer_find_path(traffic, NODE_E, route1)
    
    expected1 = [NODE_E, NODE_H, NODE_I]
    if route1.path_length != 3: return False
    for i in range(3):
        if route1.path[i] != expected1[i]: return False
    if route1.total_cost != 2.0: return False
    
    # Start at C, Reset traffic first, then let F be congested
    traffic_monitor_init(traffic)
    traffic_monitor_set_vehicle_count(traffic, NODE_F, 35)
    
    route2 = RouteDetails()
    route_optimizer_find_path(traffic, NODE_C, route2)
    
    expected2 = [NODE_C, NODE_B, NODE_E, NODE_H, NODE_I]
    if route2.path_length != 5: return False
    for i in range(5):
        if route2.path[i] != expected2[i]: return False
    if route2.total_cost != 4.0: return False
    return True

# ETA Calculator tests
def test_eta_low_traffic():
    state = AmbulanceState()
    state.current_node = NODE_A
    state.destination = NODE_I
    state.speed = 1.0
    state.distance_remaining = 4
    state.emergency_active = True
    
    route = RouteDetails()
    route.path = [NODE_A, NODE_B, NODE_C, NODE_F, NODE_I]
    route.path_length = 5
    route.total_cost = 4.0
    
    traffic = TrafficState()
    traffic_monitor_init(traffic)
    
    eta = eta_calculator_calculate_eta(state, route, traffic)
    if eta != 240: return False  # 4 * 60s = 240 seconds
    
    arrival_times = [0] * 9
    eta_calculator_predict_arrival_times(state, route, traffic, arrival_times)
    
    if arrival_times[NODE_B] != 60: return False
    if arrival_times[NODE_C] != 120: return False
    if arrival_times[NODE_F] != 180: return False
    if arrival_times[NODE_I] != 240: return False
    return True

def test_eta_mixed_traffic():
    state = AmbulanceState()
    state.current_node = NODE_A
    state.destination = NODE_I
    state.speed = 1.0
    state.distance_remaining = 4
    state.emergency_active = True
    
    route = RouteDetails()
    route.path = [NODE_A, NODE_B, NODE_C, NODE_F, NODE_I]
    route.path_length = 5
    route.total_cost = 4.0
    
    traffic = TrafficState()
    traffic_monitor_init(traffic)
    
    # Set mixed: B MED (90s), C HIGH (150s), F LOW (60s), I LOW (60s)
    traffic_monitor_set_vehicle_count(traffic, NODE_B, 12)
    traffic_monitor_set_vehicle_count(traffic, NODE_C, 48)
    traffic_monitor_set_vehicle_count(traffic, NODE_F, 5)
    
    eta = eta_calculator_calculate_eta(state, route, traffic)
    # 90 + 150 + 60 + 60 = 360 seconds
    if eta != 360: return False
    
    arrival_times = [0] * 9
    eta_calculator_predict_arrival_times(state, route, traffic, arrival_times)
    if arrival_times[NODE_B] != 90: return False
    if arrival_times[NODE_C] != 240: return False
    if arrival_times[NODE_F] != 300: return False
    if arrival_times[NODE_I] != 360: return False
    
    print()
    eta_calculator_print_eta(eta)
    
    # Step to B
    state.current_node = NODE_B
    state.distance_remaining = 3
    
    eta_B = eta_calculator_calculate_eta(state, route, traffic)
    # Remaining: B-C (150s) + C-F (60s) + F-I (60s) = 270 seconds
    if eta_B != 270: return False
    
    arrival_times_B = [0] * 9
    eta_calculator_predict_arrival_times(state, route, traffic, arrival_times_B)
    if arrival_times_B[NODE_C] != 150: return False
    if arrival_times_B[NODE_F] != 210: return False
    if arrival_times_B[NODE_I] != 270: return False
    
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
    
    print("\n--- 3. Route Optimizer Module ---")
    run_test("test_shortest_path_low_traffic", test_shortest_path_low_traffic)
    run_test("test_bypass_congested_route", test_bypass_congested_route)
    run_test("test_different_start_positions", test_different_start_positions)
    
    print("\n--- 4. ETA Calculator Module ---")
    run_test("test_eta_low_traffic", test_eta_low_traffic)
    run_test("test_eta_mixed_traffic", test_eta_mixed_traffic)
    
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
