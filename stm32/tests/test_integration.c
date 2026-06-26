/**
 * @file test_integration.c
 * @brief Integration testing for the 4 STM32 intelligence modules.
 */

#include <stdio.h>
#include <stdbool.h>
#include "../include/system_interfaces.h"
#include "../include/traffic_monitor.h"
#include "../include/ambulance_tracker.h"
#include "../include/route_optimizer.h"
#include "../include/eta_calculator.h"

static char node_to_char(NodeId node) {
    if (node >= NODE_A && node <= NODE_I) {
        return 'A' + node;
    }
    return '?';
}

const char* get_normal_signal_state_c(uint32_t time_sec, NodeId node_id) {
    uint32_t offset = 0;
    switch (node_id) {
        case NODE_A: offset = 0; break;
        case NODE_B: offset = 10; break;
        case NODE_C: offset = 20; break;
        case NODE_D: offset = 30; break;
        case NODE_E: offset = 40; break;
        case NODE_F: offset = 50; break;
        case NODE_G: offset = 0; break;
        case NODE_H: offset = 15; break;
        case NODE_I: offset = 30; break;
        default: offset = 0; break;
    }
    uint32_t phase_time = (time_sec + offset) % 60;
    if (phase_time < 30) {
        return "RED";
    } else if (phase_time < 55) {
        return "GREEN";
    } else {
        return "YELLOW";
    }
}

uint32_t get_segment_base_time_c(uint8_t count) {
    if (count <= 10) {
        return 60;
    } else if (count <= 25) {
        return 90;
    } else {
        return 150;
    }
}

void SimulateAndLogCSV_C(const uint8_t vehicle_counts[9], NodeId start_node, bool is_corridor, const char* filepath) {
    TrafficState traffic;
    TrafficMonitor_Init(&traffic);
    for (int i = 0; i < 9; i++) {
        TrafficMonitor_SetVehicleCount(&traffic, (NodeId)i, vehicle_counts[i]);
    }
    TrafficMonitor_UpdateDensity(&traffic);
    
    RouteDetails route;
    RouteOptimizer_FindPath(&traffic, start_node, &route);
    
    if (route.path_length == 0) {
        printf("ERROR: C CSV Logger - No route found!\n");
        return;
    }
    
    AmbulanceState ambulance;
    AmbulanceTracker_Init(&ambulance, start_node);
    AmbulanceTracker_SetRoute(&ambulance, &route);
    
    FILE* file = fopen(filepath, "w");
    if (!file) {
        printf("ERROR: C CSV Logger - Cannot open file %s for writing!\n", filepath);
        return;
    }
    
    fprintf(file, "timestamp,junction,signal_state,ambulance_position,traffic_density\n");
    
    uint32_t current_time = 0;
    
    for (int i = 0; i < route.path_length; i++) {
        NodeId node = route.path[i];
        
        if (i > 0) {
            NodeId prev_node = route.path[i-1];
            uint32_t base_travel_time = get_segment_base_time_c(traffic.vehicle_counts[node]);
            
            uint32_t wait_time = 0;
            if (!is_corridor) {
                uint32_t arrival_time_estimate = current_time + base_travel_time;
                uint32_t offset = 0;
                switch (node) {
                    case NODE_A: offset = 0; break;
                    case NODE_B: offset = 10; break;
                    case NODE_C: offset = 20; break;
                    case NODE_D: offset = 30; break;
                    case NODE_E: offset = 40; break;
                    case NODE_F: offset = 50; break;
                    case NODE_G: offset = 0; break;
                    case NODE_H: offset = 15; break;
                    case NODE_I: offset = 30; break;
                    default: offset = 0; break;
                }
                uint32_t phase_time = (arrival_time_estimate + offset) % 60;
                
                if (phase_time < 30) {
                    wait_time = 30 - phase_time;
                } else if (phase_time >= 55) {
                    wait_time = (60 - phase_time) + 30;
                }
            }
            
            uint32_t travel_duration = base_travel_time + wait_time;
            for (uint32_t t_offset = 0; t_offset < travel_duration; t_offset += 10) {
                uint32_t t_sampled = current_time + t_offset;
                char pos_char = node_to_char(prev_node);
                
                for (int j = 0; j < 9; j++) {
                    char junction_char = node_to_char((NodeId)j);
                    const char* sig_state = "GREEN";
                    if (is_corridor) {
                        if (j == prev_node) {
                            sig_state = "GREEN";
                        } else if (j == node) {
                            sig_state = "RED";
                        } else {
                            sig_state = get_normal_signal_state_c(t_sampled, (NodeId)j);
                        }
                    } else {
                        sig_state = get_normal_signal_state_c(t_sampled, (NodeId)j);
                    }
                    
                    const char* density_str = (traffic.density_levels[j] == DENSITY_LOW) ? "LOW" :
                                               (traffic.density_levels[j] == DENSITY_MEDIUM) ? "MEDIUM" : "HIGH";
                    fprintf(file, "%u,%c,%s,%c,%s\n", t_sampled, junction_char, sig_state, pos_char, density_str);
                }
            }
            current_time += travel_duration;
            AmbulanceTracker_MoveToNext(&ambulance, node);
        }
        
        for (int j = 0; j < 9; j++) {
            char junction_char = node_to_char((NodeId)j);
            const char* sig_state = "GREEN";
            if (is_corridor) {
                if (j == node) {
                    sig_state = "GREEN";
                } else if (i < route.path_length - 1 && j == route.path[i+1]) {
                    sig_state = "RED";
                } else {
                    sig_state = get_normal_signal_state_c(current_time, (NodeId)j);
                }
            } else {
                sig_state = get_normal_signal_state_c(current_time, (NodeId)j);
            }
            
            const char* density_str = (traffic.density_levels[j] == DENSITY_LOW) ? "LOW" :
                                       (traffic.density_levels[j] == DENSITY_MEDIUM) ? "MEDIUM" : "HIGH";
            fprintf(file, "%u,%c,%s,%c,%s\n", current_time, junction_char, sig_state, node_to_char(node), density_str);
        }
    }
    
    // Post-arrival logs
    for (uint32_t t_offset = 10; t_offset < 40; t_offset += 10) {
        uint32_t t_sampled = current_time + t_offset;
        for (int j = 0; j < 9; j++) {
            char junction_char = node_to_char((NodeId)j);
            const char* sig_state = get_normal_signal_state_c(t_sampled, (NodeId)j);
            const char* density_str = (traffic.density_levels[j] == DENSITY_LOW) ? "LOW" :
                                       (traffic.density_levels[j] == DENSITY_MEDIUM) ? "MEDIUM" : "HIGH";
            fprintf(file, "%u,%c,%s,%c,%s\n", t_sampled, junction_char, sig_state, node_to_char(NODE_I), density_str);
        }
    }
    
    fclose(file);
    printf("Successfully generated CSV log (C): %s (Duration: %us)\n", filepath, current_time);
}

void RunIntegrationScenario(const char* name, NodeId start_node, const uint8_t vehicle_counts[9]) {
    printf("\n=========================================================\n");
    printf(" RUNNING INTEGRATION SCENARIO: %s\n", name);
    printf("=========================================================\n");
    
    // 1. Initialize and Update Traffic
    TrafficState traffic;
    TrafficMonitor_Init(&traffic);
    for (int i = 0; i < 9; i++) {
        TrafficMonitor_SetVehicleCount(&traffic, (NodeId)i, vehicle_counts[i]);
    }
    TrafficMonitor_UpdateDensity(&traffic);
    TrafficMonitor_PrintReport(&traffic);
    
    // 2. Find Optimized Route
    RouteDetails route;
    RouteOptimizer_FindPath(&traffic, start_node, &route);
    RouteOptimizer_PrintRoute(&route);
    
    if (route.path_length == 0) {
        printf("ERROR: No route found from %c to hospital!\n", node_to_char(start_node));
        return;
    }
    
    // 3. Initialize Ambulance Tracker
    AmbulanceState ambulance;
    AmbulanceTracker_Init(&ambulance, start_node);
    AmbulanceTracker_SetRoute(&ambulance, &route);
    
    // 4. Simulate Ambulance Traversal Step-by-Step
    printf("\n--- SIMULATING AMBULANCE TRAVERSAL ---\n");
    
    for (int i = 0; i < route.path_length; i++) {
        NodeId step_node = route.path[i];
        
        // Move the tracker to the current step (if not the starting node)
        if (i > 0) {
            AmbulanceTracker_MoveToNext(&ambulance, step_node);
        }
        
        // Calculate ETA and predicted arrival times
        uint32_t eta = ETACalculator_CalculateETA(&ambulance, &route, &traffic);
        uint32_t arrival_times[9];
        ETACalculator_PredictArrivalTimes(&ambulance, &route, &traffic, arrival_times);
        
        // Print Live Serial Monitor Display mapping all 4 required data elements
        printf("\n[SERIAL MONITOR OUTPUT - JUNCTION %c]\n", node_to_char(ambulance.current_node));
        printf("-----------------------------------------\n");
        printf("1. Traffic Density (Active Route Nodes):\n");
        for (int k = i; k < route.path_length; k++) {
            NodeId r_node = route.path[k];
            const char* density_label = (traffic.density_levels[r_node] == DENSITY_LOW) ? "LOW" :
                                       (traffic.density_levels[r_node] == DENSITY_MEDIUM) ? "MEDIUM" : "HIGH";
            printf("   Junction %c : %s (%d vehicles)\n", 
                   node_to_char(r_node), density_label, traffic.vehicle_counts[r_node]);
        }
        
        printf("2. Selected Path   : ");
        for (int k = 0; k < route.path_length; k++) {
            printf("%c", node_to_char(route.path[k]));
            if (k < route.path_length - 1) printf(" -> ");
        }
        printf("\n");
        
        printf("3. Active Position : Current: %c | Next Target: %c\n", 
               node_to_char(ambulance.current_node), 
               (i < route.path_length - 1) ? node_to_char(route.path[i + 1]) : 'I');
        printf("   Dist Remaining  : %d segments\n", ambulance.distance_remaining);
        
        uint32_t eta_min = eta / 60;
        uint32_t eta_sec = eta % 60;
        printf("4. Live ETA        : %02d:%02d (%d seconds remaining)\n", eta_min, eta_sec, eta);
        printf("   Emergency Run   : %s\n", ambulance.emergency_active ? "ACTIVE [EMERGENCY OVERRIDE]" : "ARRIVED [RECOVERY]");
        printf("-----------------------------------------\n");
    }
    
    printf("\n=========================================================\n");
    printf(" INTEGRATION SCENARIO COMPLETE: %s\n", name);
    printf("=========================================================\n");
}

int main(void) {
    printf("=========================================================\n");
    printf("       STM32 INTELLIGENCE MODULES INTEGRATION TESTER     \n");
    printf("=========================================================\n");
    
    // Scenario 1: Low traffic conditions on all junctions
    uint8_t scenario1_traffic[9] = {
        0, 0, 0, // A, B, C
        0, 0, 0, // D, E, F
        0, 0, 0  // G, H, I
    };
    RunIntegrationScenario("SCENARIO 1: Standard/Low Traffic (Start at A)", NODE_A, scenario1_traffic);
    
    // Scenario 2: Congested top route (Junctions B, C high traffic, E medium traffic)
    uint8_t scenario2_traffic[9] = {
        0, 35, 48, // A, B=HIGH, C=HIGH
        0, 15, 0,  // D, E=MEDIUM, F
        0, 0, 0    // G, H, I
    };
    RunIntegrationScenario("SCENARIO 2: Congested Route Bypass (Start at A)", NODE_A, scenario2_traffic);
    
    // Generate CSV output logs
    printf("\n--- GENERATING CSV LOGS FOR WEEK 5 DAY 1 ---\n");
    SimulateAndLogCSV_C(scenario1_traffic, NODE_A, true, "dashboard/data/run_corridor_c.csv");
    SimulateAndLogCSV_C(scenario1_traffic, NODE_A, false, "dashboard/data/run_normal_c.csv");
    SimulateAndLogCSV_C(scenario2_traffic, NODE_A, true, "dashboard/data/run_corridor_bypass_c.csv");
    SimulateAndLogCSV_C(scenario2_traffic, NODE_A, false, "dashboard/data/run_normal_bypass_c.csv");
    
    return 0;
}
