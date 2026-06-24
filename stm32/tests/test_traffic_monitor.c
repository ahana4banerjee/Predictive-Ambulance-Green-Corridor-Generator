/**
 * @file test_traffic_monitor.c
 * @brief Unit test file for the Traffic Density Monitor module.
 */

#include <stdio.h>
#include <stdbool.h>
#include "../include/traffic_monitor.h"

// Define a test runner framework
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

// Test Case 1: Initialization verification
bool test_init(void) {
    TrafficState state;
    TrafficMonitor_Init(&state);
    
    for (int i = 0; i < 9; i++) {
        if (state.vehicle_counts[i] != 0) return false;
        if (state.density_levels[i] != DENSITY_LOW) return false;
    }
    return true;
}

// Test Case 2: Standard typical vehicle counts classification
bool test_typical_classification(void) {
    TrafficState state;
    TrafficMonitor_Init(&state);
    
    // Set vehicle counts based on implementation guide example:
    // A=35 (HIGH), B=12 (MEDIUM), C=48 (HIGH), D=5 (LOW), E=18 (MEDIUM), F=8 (LOW), G=3 (LOW), H=22 (MEDIUM), I=0 (LOW)
    TrafficMonitor_SetVehicleCount(&state, NODE_A, 35);
    TrafficMonitor_SetVehicleCount(&state, NODE_B, 12);
    TrafficMonitor_SetVehicleCount(&state, NODE_C, 48);
    TrafficMonitor_SetVehicleCount(&state, NODE_D, 5);
    TrafficMonitor_SetVehicleCount(&state, NODE_E, 18);
    TrafficMonitor_SetVehicleCount(&state, NODE_F, 8);
    TrafficMonitor_SetVehicleCount(&state, NODE_G, 3);
    TrafficMonitor_SetVehicleCount(&state, NODE_H, 22);
    TrafficMonitor_SetVehicleCount(&state, NODE_I, 0);
    
    // Run update
    TrafficMonitor_UpdateDensity(&state);
    
    // Verify
    if (state.density_levels[NODE_A] != DENSITY_HIGH) return false;
    if (state.density_levels[NODE_B] != DENSITY_MEDIUM) return false;
    if (state.density_levels[NODE_C] != DENSITY_HIGH) return false;
    if (state.density_levels[NODE_D] != DENSITY_LOW) return false;
    if (state.density_levels[NODE_E] != DENSITY_MEDIUM) return false;
    if (state.density_levels[NODE_F] != DENSITY_LOW) return false;
    if (state.density_levels[NODE_G] != DENSITY_LOW) return false;
    if (state.density_levels[NODE_H] != DENSITY_MEDIUM) return false;
    if (state.density_levels[NODE_I] != DENSITY_LOW) return false;
    
    // Print report for manual verification visual aid
    printf("\n");
    TrafficMonitor_PrintReport(&state);
    
    return true;
}

// Test Case 3: Boundary edge-cases check
bool test_boundary_classification(void) {
    TrafficState state;
    TrafficMonitor_Init(&state);
    
    // Test boundary numbers: 10 (LOW limit), 11 (MEDIUM start), 25 (MEDIUM limit), 26 (HIGH start)
    TrafficMonitor_SetVehicleCount(&state, NODE_A, 10);
    TrafficMonitor_SetVehicleCount(&state, NODE_B, 11);
    TrafficMonitor_SetVehicleCount(&state, NODE_C, 25);
    TrafficMonitor_SetVehicleCount(&state, NODE_D, 26);
    
    TrafficMonitor_UpdateDensity(&state);
    
    if (state.density_levels[NODE_A] != DENSITY_LOW) return false;
    if (state.density_levels[NODE_B] != DENSITY_MEDIUM) return false;
    if (state.density_levels[NODE_C] != DENSITY_MEDIUM) return false;
    if (state.density_levels[NODE_D] != DENSITY_HIGH) return false;
    
    return true;
}

int main(void) {
    printf("=========================================\n");
    printf("     Traffic Monitor Unit Test Suite     \n");
    printf("=========================================\n");
    
    RUN_TEST(test_init);
    RUN_TEST(test_typical_classification);
    RUN_TEST(test_boundary_classification);
    
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
