/**
 * @file system_interfaces.h
 * @brief Master protocol design, packet formats, and system-wide enums
 *        for the Predictive Ambulance Green Corridor Digital Twin.
 *        Shared across STM32 firmware and simulation scripts.
 */

#ifndef SYSTEM_INTERFACES_H
#define SYSTEM_INTERFACES_H

#include <stdint.h>
#include <stdbool.h>

// ============================================================================
// HARDWARE / PERIPHERAL CONSTANTS (Migration Mappings)
// ============================================================================
#define SPI_CPOL            0       // SPI Clock Idle state = LOW
#define SPI_CPHA            0       // SPI Data latched on 1st edge (rising)
#define SPI_CLK_MAX_HZ      4000000 // SPI Clock frequency constraint: 4 MHz
#define UART_BAUDRATE       9600    // Serial line speed: 9600 Baud
#define TIM_PERIOD_MS       200     // Master control loop refresh period: 200ms

// ============================================================================
// SHARED SYSTEM ENUMS
// ============================================================================

/**
 * @brief 3x3 City Grid Junction Nodes (4-bit encoding)
 */
typedef enum {
    NODE_A = 0x00, // 0000
    NODE_B = 0x01, // 0001
    NODE_C = 0x02, // 0010
    NODE_D = 0x03, // 0011
    NODE_E = 0x04, // 0100
    NODE_F = 0x05, // 0101
    NODE_G = 0x06, // 0110
    NODE_H = 0x07, // 0111
    NODE_I = 0x08, // 1000 (Hospital Node)
    NODE_NONE = 0x0F // 1111 (Null position)
} NodeId;

/**
 * @brief Traffic Density Classification categories
 */
typedef enum {
    DENSITY_LOW = 0,    // 0 to 10 vehicles
    DENSITY_MEDIUM = 1, // 11 to 25 vehicles
    DENSITY_HIGH = 2    // 26+ vehicles
} DensityClass;

/**
 * @brief Traffic Signal Phase States (2-bit binary mapping)
 */
typedef enum {
    SIGNAL_RED = 0x00,       // 00: Red light active
    SIGNAL_YELLOW = 0x01,    // 01: Yellow light active
    SIGNAL_GREEN = 0x02,     // 10: Green light active
    SIGNAL_EMG_GREEN = 0x03  // 11: Emergency preemption Green override active
} SignalState;

/**
 * @brief Central Controller System execution modes
 */
typedef enum {
    MODE_NORMAL = 0,
    MODE_EMERGENCY_ROUTE = 1,
    MODE_EMERGENCY_CORRIDOR = 2,
    MODE_ARRIVAL = 3,
    MODE_RECOVERY = 4
} SystemMode;

// ============================================================================
// VIRTUAL / PHYSICAL SPI PACKET DEFINITION
// ============================================================================

/**
 * @union SpiFrame
 * @brief 32-bit SPI transaction frame mapping variables to direct register lines.
 *        Compatible with little-endian MCU byte packing.
 */
typedef union {
    struct {
        uint32_t checksum     : 8;   // Bits 0-7:   XOR checksum byte
        uint32_t dist_remain  : 3;   // Bits 8-10:  Distance remaining (0-7 segments)
        uint32_t eta_seconds  : 12;  // Bits 11-22: ETA to target node (0-4095s)
        uint32_t target_node  : 4;   // Bits 23-26: Target preemption node ID (0-8)
        uint32_t current_node : 4;   // Bits 27-30: Active ambulance position node ID (0-8)
        uint32_t emg_active   : 1;   // Bit 31:     Emergency preemption flag (1=active, 0=normal)
    } fields;
    uint32_t raw_data;               // 32-bit word for direct register transmission
} SpiFrame;

// ============================================================================
// DATA STRUCTURE FOR MODULE INTERCHANGES
// ============================================================================

typedef struct {
    uint8_t vehicle_counts[9];
    DensityClass density_levels[9];
} TrafficState;

typedef struct {
    NodeId current_node;
    NodeId destination;
    float speed;
    uint8_t distance_remaining;
    bool emergency_active;
} AmbulanceState;

typedef struct {
    NodeId path[9];
    uint8_t path_length;
    float total_cost;
} RouteDetails;

// ============================================================================
// CHECKSUM UTILITY FUNCTION
// ============================================================================

/**
 * @brief Computes byte-wise XOR parity check of the top 3 bytes of the SPI frame.
 * @param frame Pointer to the SPI transaction frame
 * @return Computed checksum byte
 */
static inline uint8_t compute_spi_checksum(SpiFrame* frame) {
    uint32_t val = frame->raw_data;
    uint8_t b3 = (val >> 24) & 0xFF;
    uint8_t b2 = (val >> 16) & 0xFF;
    uint8_t b1 = (val >> 8) & 0xFF;
    return (b3 ^ b2 ^ b1);
}

#endif // SYSTEM_INTERFACES_H
