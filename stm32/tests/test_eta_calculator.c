/**
 * @file test_eta_calculator.c
 * @brief Unit test file for the ETA Calculator module.
 */

#include <stdio.h>
#include <stdbool.h>
#include "../include/eta_calculator.h"

#define RUN_TEST(test) \
    do { \
        printf("Running " #test "... "); \
        if (test()) { \
            printf("PASS\n"); \
        } else { \
            printf("FAIL\n"); \
            failed_tests++; \
        } \
    } while (0)

static int failed_tests = 0;

// Test Case 1: Standard low traffic ETA (A -> B -> C -> F -> I)
bool test_eta_low_traffic(void) {
    AmbulanceState ambulance;
    ambulance.current_node = NODE_A;
    ambulance.destination = NODE_I;
    ambulance.speed = 1.0f;
    ambulance.distance_remaining = 4;
    ambulance.emergency_active = true;
    
    RouteDetails route;
    route.path[0] = NODE_A;
    route.path[1] = NODE_B;
    route.path[2] = NODE_C;
    route.path[3] = NODE_F;
    route.path[4] = NODE_I;
    route.path_length = 5;
    route.total_cost = 4.0f;
    
    TrafficState traffic;
    for (int i = 0; i < 9; i++) {
        traffic.vehicle_counts[i] = 0;
        traffic.density_levels[i] = DENSITY_LOW;
    }
    
    uint32_t eta = ETACalculator_CalculateETA(&ambulance, &route, &traffic);
    
    // 4 segments * 60 seconds = 240 seconds (4 min 0 sec)
    if (eta != 240) return false;
    
    uint32_t arrival_times[9];
    ETACalculator_PredictArrivalTimes(&ambulance, &route, &traffic, arrival_times);
    
    if (arrival_times[NODE_B] != 60) return false;
    if (arrival_times[NODE_C] != 120) return false;
    if (arrival_times[NODE_F] != 180) return false;
    if (arrival_times[NODE_I] != 240) return false;
    
    return true;
}

// Test Case 2: Mixed traffic conditions and step-by-step countdown
bool test_eta_mixed_traffic(void) {
    AmbulanceState ambulance;
    ambulance.current_node = NODE_A;
    ambulance.destination = NODE_I;
    ambulance.speed = 1.0f;
    ambulance.distance_remaining = 4;
    ambulance.emergency_active = true;
    
    RouteDetails route;
    route.path[0] = NODE_A;
    route.path[1] = NODE_B;
    route.path[2] = NODE_C;
    route.path[3] = NODE_F;
    route.path[4] = NODE_I;
    route.path_length = 5;
    route.total_cost = 4.0f;
    
    TrafficState traffic;
    for (int i = 0; i < 9; i++) {
        traffic.vehicle_counts[i] = 0;
        traffic.density_levels[i] = DENSITY_LOW;
    }
    
    // Set mixed traffic: B is MEDIUM, C is HIGH, others are LOW
    traffic.vehicle_counts[NODE_B] = 12; // MED -> 90s
    traffic.vehicle_counts[NODE_C] = 48; // HIGH -> 150s
    traffic.vehicle_counts[NODE_F] = 5;  // LOW -> 60s
    traffic.vehicle_counts[NODE_I] = 0;  // LOW -> 60s
    
    // Calculate initial ETA from A
    uint32_t eta_A = ETACalculator_CalculateETA(&ambulance, &route, &traffic);
    
    // Segment A-B (target B MED: 90s)
    // Segment B-C (target C HIGH: 150s)
    // Segment C-F (target F LOW: 60s)
    // Segment F-I (target I LOW: 60s)
    // Total = 90 + 150 + 60 + 60 = 360 seconds (6 min 0 sec)
    if (eta_A != 360) return false;
    
    uint32_t arrival_times_A[9];
    ETACalculator_PredictArrivalTimes(&ambulance, &route, &traffic, arrival_times_A);
    if (arrival_times_A[NODE_B] != 90) return false;
    if (arrival_times_A[NODE_C] != 240) return false; // 90 + 150
    if (arrival_times_A[NODE_F] != 300) return false; // 240 + 60
    if (arrival_times_A[NODE_I] != 360) return false; // 300 + 60
    
    printf("\n");
    ETACalculator_PrintETA(eta_A);
    
    // Step to Node B
    ambulance.current_node = NODE_B;
    ambulance.distance_remaining = 3;
    
    uint32_t eta_B = ETACalculator_CalculateETA(&ambulance, &route, &traffic);
    // Remaining = B-C (150s) + C-F (60s) + F-I (60s) = 270 seconds
    if (eta_B != 270) return false;
    
    uint32_t arrival_times_B[9];
    ETACalculator_PredictArrivalTimes(&ambulance, &route, &traffic, arrival_times_B);
    if (arrival_times_B[NODE_C] != 150) return false;
    if (arrival_times_B[NODE_F] != 210) return false;
    if (arrival_times_B[NODE_I] != 270) return false;
    
    return true;
}

int main(void) {
    printf("=========================================\n");
    printf("     ETA Calculator Unit Test Suite      \n");
    printf("=========================================\n");
    
    RUN_TEST(test_eta_low_traffic);
    RUN_TEST(test_eta_mixed_traffic);
    
    printf("\nTest Suite Completed: ");
    if (failed_tests == 0) {
        printf("ALL TESTS PASSED\n");
        printf("=========================================\n");
        return 0;
    } else {
        printf("%d TEST(S) FAILED\n", failed_tests);
        printf("=========================================\n");
        return 1;
    }
}
