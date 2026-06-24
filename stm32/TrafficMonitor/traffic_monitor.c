/**
 * @file traffic_monitor.c
 * @brief Implementation of the Traffic Density Monitor module on STM32.
 */

#include "../include/traffic_monitor.h"
#include <stdio.h>

void TrafficMonitor_Init(TrafficState* state) {
    if (state == NULL) {
        return;
    }
    
    for (int i = 0; i < 9; i++) {
        state->vehicle_counts[i] = 0;
        state->density_levels[i] = DENSITY_LOW;
    }
}

void TrafficMonitor_SetVehicleCount(TrafficState* state, NodeId node, uint8_t count) {
    if (state == NULL || node >= NODE_NONE) {
        return;
    }
    
    state->vehicle_counts[node] = count;
}

void TrafficMonitor_UpdateDensity(TrafficState* state) {
    if (state == NULL) {
        return;
    }
    
    for (int i = 0; i < 9; i++) {
        uint8_t count = state->vehicle_counts[i];
        
        if (count <= 10) {
            state->density_levels[i] = DENSITY_LOW;
        } else if (count <= 25) {
            state->density_levels[i] = DENSITY_MEDIUM;
        } else {
            state->density_levels[i] = DENSITY_HIGH;
        }
    }
}

static const char* density_to_string(DensityClass density) {
    switch (density) {
        case DENSITY_LOW:
            return "LOW";
        case DENSITY_MEDIUM:
            return "MEDIUM";
        case DENSITY_HIGH:
            return "HIGH";
        default:
            return "UNKNOWN";
    }
}

void TrafficMonitor_PrintReport(const TrafficState* state) {
    if (state == NULL) {
        return;
    }
    
    printf("=========================================\n");
    printf("        Traffic Monitor Report           \n");
    printf("=========================================\n");
    printf("Junction | Vehicle Count | Density Class\n");
    printf("---------|---------------|---------------\n");
    
    for (int i = 0; i < 9; i++) {
        char junction_label = 'A' + i;
        printf("    %c    |      %3d      | %s\n", 
               junction_label, 
               state->vehicle_counts[i], 
               density_to_string(state->density_levels[i]));
    }
    
    printf("=========================================\n");
}
