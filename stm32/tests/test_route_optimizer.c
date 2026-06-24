/**
 * @file test_route_optimizer.c
 * @brief Unit test file for the Route Optimizer module.
 */

#include <stdio.h>
#include <stdbool.h>
#include "../include/route_optimizer.h"

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

static bool paths_equal(const RouteDetails* route, const NodeId* expected, uint8_t len) {
    if (route->path_length != len) return false;
    for (int i = 0; i < len; i++) {
        if (route->path[i] != expected[i]) return false;
    }
    return true;
}

// Test Case 1: Shortest path with LOW traffic everywhere
bool test_shortest_path_low_traffic(void) {
    TrafficState traffic;
    for (int i = 0; i < 9; i++) {
        traffic.vehicle_counts[i] = 0;
        traffic.density_levels[i] = DENSITY_LOW;
    }
    
    RouteDetails route;
    RouteOptimizer_FindPath(&traffic, NODE_A, &route);
    
    // Expected path: A -> B -> C -> F -> I (Cost 4.0)
    NodeId expected[] = {NODE_A, NODE_B, NODE_C, NODE_F, NODE_I};
    if (!paths_equal(&route, expected, 5)) return false;
    if (route.total_cost != 4.0f) return false;
    
    return true;
}

// Test Case 2: Congested route A-B-C (forces D-G-H-I route)
bool test_bypass_congested_route(void) {
    TrafficState traffic;
    for (int i = 0; i < 9; i++) {
        traffic.vehicle_counts[i] = 0;
        traffic.density_levels[i] = DENSITY_LOW;
    }
    
    // Congest Junction B, C and E to force path G-H-I
    traffic.vehicle_counts[NODE_B] = 35; // HIGH (penalty 5)
    traffic.vehicle_counts[NODE_C] = 48; // HIGH (penalty 5)
    traffic.vehicle_counts[NODE_E] = 15; // MEDIUM (penalty 2)
    
    RouteDetails route;
    RouteOptimizer_FindPath(&traffic, NODE_A, &route);
    
    // Expected path: A -> D -> G -> H -> I (Cost 4.0)
    // Alternate through E would be: A -> D -> E -> F -> I (Cost: A-D=1.0, D-E=1+2=3, E-F=1, F-I=1; Total Cost = 6.0)
    // Alternate through B would be: A -> B -> C -> F -> I (Cost: A-B=1+5=6, B-C=1+5=6, C-F=1, F-I=1; Total Cost = 14.0)
    NodeId expected[] = {NODE_A, NODE_D, NODE_G, NODE_H, NODE_I};
    
    printf("\n");
    RouteOptimizer_PrintRoute(&route);
    
    if (!paths_equal(&route, expected, 5)) return false;
    if (route.total_cost != 4.0f) return false;
    
    return true;
}

// Test Case 3: Verify different starting positions (Start at E and Start at C)
bool test_different_start_positions(void) {
    TrafficState traffic;
    for (int i = 0; i < 9; i++) {
        traffic.vehicle_counts[i] = 0;
        traffic.density_levels[i] = DENSITY_LOW;
    }
    
    // Start at E (Middle node). Let B and F be highly congested.
    traffic.vehicle_counts[NODE_B] = 30; // HIGH (penalty 5)
    traffic.vehicle_counts[NODE_F] = 30; // HIGH (penalty 5)
    
    RouteDetails route1;
    RouteOptimizer_FindPath(&traffic, NODE_E, &route1);
    
    // Expected path from E: E -> H -> I (Cost 2.0)
    NodeId expected1[] = {NODE_E, NODE_H, NODE_I};
    if (!paths_equal(&route1, expected1, 3)) return false;
    if (route1.total_cost != 2.0f) return false;
    
    // Start at C. Reset traffic first, then let F be congested.
    for (int i = 0; i < 9; i++) {
        traffic.vehicle_counts[i] = 0;
        traffic.density_levels[i] = DENSITY_LOW;
    }
    traffic.vehicle_counts[NODE_F] = 35; // HIGH (penalty 5)
    
    RouteDetails route2;
    RouteOptimizer_FindPath(&traffic, NODE_C, &route2);
    
    // Expected path from C (bypassing F): C -> B -> E -> H -> I (Cost 4.0)
    // Cost via F is: C-F (1+5=6) + F-I (1) = 7.0
    NodeId expected2[] = {NODE_C, NODE_B, NODE_E, NODE_H, NODE_I};
    if (!paths_equal(&route2, expected2, 5)) return false;
    if (route2.total_cost != 4.0f) return false;
    
    return true;
}

int main(void) {
    printf("=========================================\n");
    printf("     Route Optimizer Unit Test Suite    \n");
    printf("=========================================\n");
    
    RUN_TEST(test_shortest_path_low_traffic);
    RUN_TEST(test_bypass_congested_route);
    RUN_TEST(test_different_start_positions);
    
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
