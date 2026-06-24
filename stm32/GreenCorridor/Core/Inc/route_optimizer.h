/**
 * @file route_optimizer.h
 * @brief API for the Route Optimizer module on STM32.
 */

#ifndef ROUTE_OPTIMIZER_H
#define ROUTE_OPTIMIZER_H

#include "system_interfaces.h"

/**
 * @brief Computes the optimal path from the start node to the destination hospital (NODE_I)
 *        taking edge distances and dynamic traffic density weighting into account.
 * @param traffic Pointer to the traffic monitor state containing vehicle counts
 * @param start NodeId representing starting junction of the ambulance
 * @param route Pointer to RouteDetails where the optimal path and cost will be saved
 */
void RouteOptimizer_FindPath(const TrafficState* traffic, NodeId start, RouteDetails* route);

/**
 * @brief Helper to print the optimized route to standard output.
 * @param route Pointer to RouteDetails to print
 */
void RouteOptimizer_PrintRoute(const RouteDetails* route);

#endif // ROUTE_OPTIMIZER_H

