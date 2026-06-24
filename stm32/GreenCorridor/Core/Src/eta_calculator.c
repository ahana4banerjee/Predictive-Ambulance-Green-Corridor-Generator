/**
 * @file eta_calculator.c
 * @brief Implementation of the ETA Calculator module on STM32.
 */

#include "eta_calculator.h"
#include <stdio.h>
#include <stddef.h>

#define BASE_TIME_LOW    60.0f  // 1 minute (60 seconds)
#define BASE_TIME_MED    90.0f  // 1.5 minutes (90 seconds)
#define BASE_TIME_HIGH   150.0f // 2.5 minutes (150 seconds)

static float get_segment_base_time(uint8_t count) {
    if (count <= 10) {
        return BASE_TIME_LOW;
    } else if (count <= 25) {
        return BASE_TIME_MED;
    } else {
        return BASE_TIME_HIGH;
    }
}

uint32_t ETACalculator_CalculateETA(const AmbulanceState* state, const RouteDetails* route, const TrafficState* traffic) {
    if (state == NULL || route == NULL || traffic == NULL) {
        return 0;
    }

    if (state->current_node == state->destination) {
        return 0; // Already arrived
    }

    int current_index = -1;
    for (int i = 0; i < route->path_length; i++) {
        if (route->path[i] == state->current_node) {
            current_index = i;
            break;
        }
    }

    if (current_index == -1 || current_index >= route->path_length - 1) {
        return 0;
    }

    float total_seconds = 0.0f;
    float speed = (state->speed > 0.0f) ? state->speed : 1.0f;

    for (int i = current_index; i < route->path_length - 1; i++) {
        NodeId target = route->path[i + 1];
        float base_time = get_segment_base_time(traffic->vehicle_counts[target]);
        total_seconds += (base_time / speed);
    }

    return (uint32_t)total_seconds;
}

void ETACalculator_PredictArrivalTimes(const AmbulanceState* state, const RouteDetails* route, const TrafficState* traffic, uint32_t arrival_times[9]) {
    if (state == NULL || route == NULL || traffic == NULL || arrival_times == NULL) {
        return;
    }

    // Initialize all to 0
    for (int i = 0; i < 9; i++) {
        arrival_times[i] = 0;
    }

    if (state->current_node == state->destination) {
        return;
    }

    int current_index = -1;
    for (int i = 0; i < route->path_length; i++) {
        if (route->path[i] == state->current_node) {
            current_index = i;
            break;
        }
    }

    if (current_index == -1) {
        return;
    }

    float running_sum = 0.0f;
    float speed = (state->speed > 0.0f) ? state->speed : 1.0f;

    for (int i = current_index; i < route->path_length - 1; i++) {
        NodeId target = route->path[i + 1];
        float base_time = get_segment_base_time(traffic->vehicle_counts[target]);
        running_sum += (base_time / speed);
        arrival_times[target] = (uint32_t)running_sum;
    }
}

void ETACalculator_PrintETA(uint32_t eta_seconds) {
    uint32_t minutes = eta_seconds / 60;
    uint32_t seconds = eta_seconds % 60;

    printf("=========================================\n");
    printf("            Estimated ETA Report         \n");
    printf("=========================================\n");
    printf("Remaining Time     : %02d min %02d sec\n", minutes, seconds);
    printf("Total Seconds      : %d s\n", eta_seconds);
    printf("=========================================\n");
}



