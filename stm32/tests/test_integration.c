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
    
    return 0;
}
