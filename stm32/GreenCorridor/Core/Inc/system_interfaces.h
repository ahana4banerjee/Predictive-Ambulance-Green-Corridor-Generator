/**
 * @file system_interfaces.h
 * @brief System interface design, data structures, and state enums
 *        for the Predictive Ambulance Green Corridor Generator.
 *        Shared between stm32 firmware modules.
 */

#ifndef SYSTEM_INTERFACES_H
#define SYSTEM_INTERFACES_H

#include <stdint.h>
#include <stdbool.h>

// ============================================================================
// ENUMS & CONFIGURATIONS
// ============================================================================

/**
 * @brief Traffic density classification states
 */
typedef enum {
    DENSITY_LOW = 0,    ///< 0 - 10 vehicles
    DENSITY_MEDIUM = 1, ///< 11 - 25 vehicles
    DENSITY_HIGH = 2    ///< 26+ vehicles
} DensityClass;

/**
 * @brief Traffic signal light binary states (2-bit mapping)
 */
typedef enum {
    SIGNAL_RED = 0x00,       ///< 00: Red light active
    SIGNAL_YELLOW = 0x01,    ///< 01: Yellow light active
    SIGNAL_GREEN = 0x02,     ///< 10: Green light active
    SIGNAL_EMG_GREEN = 0x03  ///< 11: Emergency override Green active
} SignalState;

/**
 * @brief 3x3 Grid Node indices and encoding values (4-bit encoding)
 */
typedef enum {
    NODE_A = 0x00,
    NODE_B = 0x01,
    NODE_C = 0x02,
    NODE_D = 0x03,
    NODE_E = 0x04,
    NODE_F = 0x05,
    NODE_G = 0x06,
    NODE_H = 0x07,
    NODE_I = 0x08,  ///< Destination Hospital node
    NODE_NONE = 0x0F
} NodeId;

/**
 * @brief General system execution modes
 */
typedef enum {
    MODE_NORMAL = 0,
    MODE_EMERGENCY_ROUTE = 1,
    MODE_EMERGENCY_CORRIDOR = 2,
    MODE_ARRIVAL = 3,
    MODE_RECOVERY = 4
} SystemMode;

// ============================================================================
// SPI FRAME STRUCTURE DEFINITION (32-bit)
// ============================================================================

/**
 * @union SpiFrame
 * @brief Represents the 32-bit SPI transaction frame sent from the STM32 to the FPGA.
 *        Uses bit-fields for register-level hardware pin mapping on little-endian MCU.
 */
typedef union {
    struct {
        uint32_t checksum     : 8;   ///< Bits 0-7:   Frame validation XOR checksum
        uint32_t dist_remain  : 3;   ///< Bits 8-10:  Distance remaining (segments: 0-7)
        uint32_t eta_seconds  : 12;  ///< Bits 11-22: Remaining path ETA to target node (seconds)
        uint32_t target_node  : 4;   ///< Bits 23-26: Next intersection target node ID (0-8)
        uint32_t current_node : 4;   ///< Bits 27-30: Current ambulance node position ID (0-8)
        uint32_t emg_active   : 1;   ///< Bit 31:     Emergency active flag (1 = active, 0 = normal)
    } fields;
    uint32_t raw_data;               ///< Combined 32-bit word for direct SPI register transfer
} SpiFrame;

// ============================================================================
// DATA STRUCTURE FOR MODULE INTERCHANGES
// ============================================================================

/**
 * @struct TrafficState
 * @brief Structure containing the traffic snapshots collected by the Traffic Monitor
 */
typedef struct {
    uint8_t vehicle_counts[9];      ///< Raw counts of vehicles at junctions A-I
    DensityClass density_levels[9]; ///< Density classifications for junctions A-I
} TrafficState;

/**
 * @struct AmbulanceState
 * @brief Structure containing active tracker variables
 */
typedef struct {
    NodeId current_node;            ///< Current junction ID
    NodeId destination;             ///< Destination hospital node (NODE_I)
    float speed;                    ///< Ambulance speed (segments/sec)
    uint8_t distance_remaining;     ///< Path segments left to Hospital
    bool emergency_active;          ///< Active emergency run status
} AmbulanceState;

/**
 * @struct RouteDetails
 * @brief Route optimizer output path definitions
 */
typedef struct {
    NodeId path[9];                 ///< Sequence of nodes representing optimal path
    uint8_t path_length;            ///< Total nodes in path
    float total_cost;               ///< Dynamic weighted route cost
} RouteDetails;

// ============================================================================
// INTERFACE PROTOYPES (STM32 API definitions)
// ============================================================================

/**
 * @brief Generates the XOR checksum for the SPI Frame to ensure transmission integrity.
 * @param frame Pointer to the SPI frame struct
 * @return Computed checksum byte
 */
static inline uint8_t compute_spi_checksum(SpiFrame* frame) {
    uint32_t val = frame->raw_data;
    uint8_t b1 = (val >> 24) & 0xFF;
    uint8_t b2 = (val >> 16) & 0xFF;
    uint8_t b3 = (val >> 8) & 0xFF;
    return (b1 ^ b2 ^ b3);
}

#endif // SYSTEM_INTERFACES_H

