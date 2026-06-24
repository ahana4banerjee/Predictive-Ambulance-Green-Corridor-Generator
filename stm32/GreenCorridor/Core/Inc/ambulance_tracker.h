/**
 * @file ambulance_tracker.h
 * @brief API for the Ambulance Tracker module on STM32.
 */

#ifndef AMBULANCE_TRACKER_H
#define AMBULANCE_TRACKER_H

#include "system_interfaces.h"

/**
 * @brief Initializes the ambulance state at the starting node.
 * @param state Pointer to the ambulance tracker state struct
 * @param start_node Starting node ID for the emergency run
 */
void AmbulanceTracker_Init(AmbulanceState* state, NodeId start_node);

/**
 * @brief Sets the path details and updates the remaining distance segments.
 * @param state Pointer to the ambulance tracker state struct
 * @param route Pointer to the optimized route details
 */
void AmbulanceTracker_SetRoute(AmbulanceState* state, const RouteDetails* route);

/**
 * @brief Simulates the movement of the ambulance to the next node in the path.
 * @param state Pointer to the ambulance tracker state struct
 * @param next_node Next junction node ID to move to
 */
void AmbulanceTracker_MoveToNext(AmbulanceState* state, NodeId next_node);

/**
 * @brief Prints the status of the ambulance tracking to standard output.
 * @param state Pointer to the ambulance tracker state struct
 */
void AmbulanceTracker_PrintStatus(const AmbulanceState* state);

#endif // AMBULANCE_TRACKER_H

