/**
 * @file route_optimizer.c
 * @brief Implementation of the Dijkstra-based Traffic-Aware Route Optimizer.
 */

#include "../include/route_optimizer.h"
#include <stdio.h>
#include <stdbool.h>
#include <stddef.h>

#define INF 1e9f

typedef struct {
    NodeId from;
    NodeId to;
    float distance;
} Edge;

static const Edge edges[] = {
    {NODE_A, NODE_B, 1.0f},
    {NODE_B, NODE_C, 1.0f},
    {NODE_D, NODE_E, 1.0f},
    {NODE_E, NODE_F, 1.0f},
    {NODE_G, NODE_H, 1.0f},
    {NODE_H, NODE_I, 1.0f},
    {NODE_A, NODE_D, 1.0f},
    {NODE_D, NODE_G, 1.0f},
    {NODE_B, NODE_E, 1.0f},
    {NODE_E, NODE_H, 1.0f},
    {NODE_C, NODE_F, 1.0f},
    {NODE_F, NODE_I, 1.0f}
};
#define NUM_EDGES 12

static float get_traffic_penalty(uint8_t count) {
    if (count <= 10) {
        return 0.0f; // LOW
    } else if (count <= 25) {
        return 2.0f; // MEDIUM
    } else {
        return 5.0f; // HIGH
    }
}

void RouteOptimizer_FindPath(const TrafficState* traffic, NodeId start, RouteDetails* route) {
    if (traffic == NULL || route == NULL || start >= NODE_NONE) {
        return;
    }

    float dist[9];
    bool visited[9];
    NodeId prev[9];

    // Initialize Dijkstra tables
    for (int i = 0; i < 9; i++) {
        dist[i] = INF;
        visited[i] = false;
        prev[i] = NODE_NONE;
    }

    dist[start] = 0.0f;

    for (int step = 0; step < 9; step++) {
        // Find unvisited node with minimum distance
        int u = -1;
        float min_dist = INF;
        for (int i = 0; i < 9; i++) {
            if (!visited[i] && dist[i] < min_dist) {
                min_dist = dist[i];
                u = i;
            }
        }

        if (u == -1 || u == NODE_I) {
            break; // All reachable nodes visited or target reached
        }

        visited[u] = true;

        // Relax neighbors
        for (int e = 0; e < NUM_EDGES; e++) {
            NodeId v = NODE_NONE;
            float base_dist = edges[e].distance;

            if (edges[e].from == (NodeId)u) {
                v = edges[e].to;
            } else if (edges[e].to == (NodeId)u) {
                v = edges[e].from;
            }

            if (v != NODE_NONE && !visited[v]) {
                float penalty = get_traffic_penalty(traffic->vehicle_counts[v]);
                float weight = base_dist + penalty;

                if (dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    prev[v] = (NodeId)u;
                }
            }
        }
    }

    // Path Reconstruction
    if (dist[NODE_I] >= INF) {
        route->path_length = 0;
        route->total_cost = INF;
        return;
    }

    route->total_cost = dist[NODE_I];

    // Reconstruct path backward
    NodeId temp_path[9];
    int temp_len = 0;
    NodeId curr = NODE_I;

    while (curr != NODE_NONE) {
        temp_path[temp_len++] = curr;
        curr = prev[curr];
    }

    // Reverse path to store: start -> ... -> hospital
    route->path_length = temp_len;
    for (int i = 0; i < temp_len; i++) {
        route->path[i] = temp_path[temp_len - 1 - i];
    }
}

static char node_to_char(NodeId node) {
    if (node >= NODE_A && node <= NODE_I) {
        return 'A' + node;
    }
    return '?';
}

void RouteOptimizer_PrintRoute(const RouteDetails* route) {
    if (route == NULL) {
        return;
    }

    if (route->path_length == 0) {
        printf("=========================================\n");
        printf("         No Route Available             \n");
        printf("=========================================\n");
        return;
    }

    printf("=========================================\n");
    printf("         Optimized Route Details         \n");
    printf("=========================================\n");
    printf("Optimal Path       : ");
    for (int i = 0; i < route->path_length; i++) {
        printf("%c", node_to_char(route->path[i]));
        if (i < route->path_length - 1) {
            printf(" -> ");
        }
    }
    printf("\n");
    printf("Total Cost         : %.2f\n", route->total_cost);
    printf("=========================================\n");
}
