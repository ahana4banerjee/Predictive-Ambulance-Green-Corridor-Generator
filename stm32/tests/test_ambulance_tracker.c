/**
 * @file test_ambulance_tracker.c
 * @brief Unit test file for the Ambulance Tracker module.
 */

#include <stdio.h>
#include <stdbool.h>
#include "../include/ambulance_tracker.h"

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

// Test Case 1: Initialization
bool test_tracker_init(void) {
    AmbulanceState state;
    AmbulanceTracker_Init(&state, NODE_A);
    
    if (state.current_node != NODE_A) return false;
    if (state.destination != NODE_I) return false;
    if (state.speed != 1.0f) return false;
    if (state.emergency_active != true) return false;
    
    // Test initializing at hospital I
    AmbulanceTracker_Init(&state, NODE_I);
    if (state.emergency_active != false) return false;
    
    return true;
}

// Test Case 2: Ambulance movement and route mapping (A -> B -> C -> F -> I)
bool test_tracker_movement(void) {
    AmbulanceState state;
    AmbulanceTracker_Init(&state, NODE_A);
    
    // Define the path A -> B -> C -> F -> I
    RouteDetails route;
    route.path[0] = NODE_A;
    route.path[1] = NODE_B;
    route.path[2] = NODE_C;
    route.path[3] = NODE_F;
    route.path[4] = NODE_I;
    route.path_length = 5;
    route.total_cost = 4.0f;
    
    // Set route
    AmbulanceTracker_SetRoute(&state, &route);
    
    // Verify initial distance remaining: 4 segments (A-B, B-C, C-F, F-I)
    if (state.distance_remaining != 4) return false;
    if (state.emergency_active != true) return false;
    
    // Move to Node B
    AmbulanceTracker_MoveToNext(&state, NODE_B);
    if (state.current_node != NODE_B) return false;
    if (state.distance_remaining != 3) return false;
    if (state.emergency_active != true) return false;
    
    // Move to Node C
    AmbulanceTracker_MoveToNext(&state, NODE_C);
    if (state.current_node != NODE_C) return false;
    if (state.distance_remaining != 2) return false;
    if (state.emergency_active != true) return false;
    
    // Move to Node F
    AmbulanceTracker_MoveToNext(&state, NODE_F);
    if (state.current_node != NODE_F) return false;
    if (state.distance_remaining != 1) return false;
    if (state.emergency_active != true) return false;
    
    // Print tracker report before arrival for visual check
    printf("\n");
    AmbulanceTracker_PrintStatus(&state);
    
    // Move to Hospital I (Arrival)
    AmbulanceTracker_MoveToNext(&state, NODE_I);
    if (state.current_node != NODE_I) return false;
    if (state.distance_remaining != 0) return false;
    if (state.emergency_active != false) return false;
    
    // Print final report after arrival for visual check
    printf("\n");
    AmbulanceTracker_PrintStatus(&state);
    
    return true;
}

int main(void) {
    printf("=========================================\n");
    printf("     Ambulance Tracker Unit Test Suite   \n");
    printf("=========================================\n");
    
    RUN_TEST(test_tracker_init);
    RUN_TEST(test_tracker_movement);
    
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
