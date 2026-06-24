/**
 * @file eta_calculator.h
 * @brief API for the ETA Calculator module on STM32.
 */

#ifndef ETA_CALCULATOR_H
#define ETA_CALCULATOR_H

#include "system_interfaces.h"

/**
 * @brief Computes the estimated time of arrival (ETA) at the hospital in seconds,
 *        taking remaining route path, speed, and traffic densities into account.
 * @param state Pointer to the ambulance tracker state containing position/speed
 * @param route Pointer to the optimized route details
 * @param traffic Pointer to the traffic monitor state
 * @return Total estimated arrival time in seconds
 */
uint32_t ETACalculator_CalculateETA(const AmbulanceState* state, const RouteDetails* route, const TrafficState* traffic);

/**
 * @brief Predicts the estimated arrival time at each subsequent junction in the path.
 * @param state Pointer to the ambulance tracker state
 * @param route Pointer to the optimized route details
 * @param traffic Pointer to the traffic monitor state
 * @param arrival_times Output array where predicted arrival time (in seconds from now) for each node will be stored
 */
void ETACalculator_PredictArrivalTimes(const AmbulanceState* state, const RouteDetails* route, const TrafficState* traffic, uint32_t arrival_times[9]);

/**
 * @brief Prints the formatted ETA report to standard output.
 * @param eta_seconds Total ETA in seconds
 */
void ETACalculator_PrintETA(uint32_t eta_seconds);

#endif // ETA_CALCULATOR_H

