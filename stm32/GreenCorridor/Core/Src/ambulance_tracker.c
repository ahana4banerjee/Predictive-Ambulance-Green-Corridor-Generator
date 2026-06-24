/**
 * @file ambulance_tracker.c
 * @brief Implementation of the Ambulance Tracker module on STM32.
 */

#include "ambulance_tracker.h"
#include <stdio.h>
#include <stddef.h>

void AmbulanceTracker_Init(AmbulanceState* state, NodeId start_node) {
    if (state == NULL) {
        return;
    }

    state->current_node = start_node;
    state->destination = NODE_I;
    state->speed = 1.0f; // Default speed: 1.0 segment per step
    state->distance_remaining = 0;
    state->emergency_active = (start_node != NODE_I);
}

void AmbulanceTracker_SetRoute(AmbulanceState* state, const RouteDetails* route) {
    if (state == NULL || route == NULL) {
        return;
    }

    int current_index = -1;
    for (int i = 0; i < route->path_length; i++) {
        if (route->path[i] == state->current_node) {
            current_index = i;
            break;
        }
    }

    if (current_index != -1) {
        state->distance_remaining = route->path_length - 1 - current_index;
    } else {
        // If current position isn't in route, assume full path length
        state->distance_remaining = (route->path_length > 0) ? (route->path_length - 1) : 0;
    }

    state->emergency_active = (state->current_node != state->destination);
}

void AmbulanceTracker_MoveToNext(AmbulanceState* state, NodeId next_node) {
    if (state == NULL || next_node >= NODE_NONE) {
        return;
    }

    if (state->current_node == next_node) {
        return; // Already at the node
    }

    state->current_node = next_node;

    if (state->distance_remaining > 0) {
        state->distance_remaining--;
    }

    if (state->current_node == state->destination) {
        state->emergency_active = false;
        state->distance_remaining = 0;
    }
}

static char node_to_char(NodeId node) {
    if (node >= NODE_A && node <= NODE_I) {
        return 'A' + node;
    }
    return '?';
}

void AmbulanceTracker_PrintStatus(const AmbulanceState* state) {
    if (state == NULL) {
        return;
    }

    printf("=========================================\n");
    printf("        Ambulance Tracker Status         \n");
    printf("=========================================\n");
    printf("Current Position   : %c\n", node_to_char(state->current_node));
    printf("Destination        : %c\n", node_to_char(state->destination));
    printf("Remaining Distance : %d segments\n", state->distance_remaining);
    printf("Current Speed      : %.2f units/sec\n", state->speed);
    printf("Emergency Status   : %s\n", state->emergency_active ? "ACTIVE [EMERGENCY]" : "INACTIVE [ARRIVED]");
    printf("=========================================\n");
}

