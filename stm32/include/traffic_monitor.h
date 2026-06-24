/**
 * @file traffic_monitor.h
 * @brief Header file for the Traffic Density Monitor module on STM32.
 */

#ifndef TRAFFIC_MONITOR_H
#define TRAFFIC_MONITOR_H

#include "system_interfaces.h"

/**
 * @brief Initializes the traffic state counts and densities to defaults.
 * @param state Pointer to the TrafficState struct to initialize.
 */
void TrafficMonitor_Init(TrafficState* state);

/**
 * @brief Sets the vehicle count for a specific junction node.
 * @param state Pointer to the active TrafficState struct.
 * @param node NodeId enum representing the target junction (A through I).
 * @param count The number of vehicles (0-255).
 */
void TrafficMonitor_SetVehicleCount(TrafficState* state, NodeId node, uint8_t count);

/**
 * @brief Classifies vehicle counts into LOW, MEDIUM, and HIGH density classes for all 9 junctions.
 *        Thresholds:
 *          - 0 to 10 vehicles -> DENSITY_LOW
 *          - 11 to 25 vehicles -> DENSITY_MEDIUM
 *          - 26+ vehicles -> DENSITY_HIGH
 * @param state Pointer to the active TrafficState struct.
 */
void TrafficMonitor_UpdateDensity(TrafficState* state);

/**
 * @brief Prints a status report of counts and density classifications for all 9 junctions
 *        using standard printf (simulates serial UART log output on STM32 console).
 * @param state Const pointer to the active TrafficState struct.
 */
void TrafficMonitor_PrintReport(const TrafficState* state);

#endif // TRAFFIC_MONITOR_H
