/**
 * @file spi_master.h
 * @brief Header file for the SPI Master Packet Encoder module on STM32.
 */

#ifndef SPI_MASTER_H
#define SPI_MASTER_H

#include "system_interfaces.h"

/**
 * @brief Packs state variables into a 32-bit SpiFrame struct with a valid XOR checksum.
 * @param frame Pointer to the output SpiFrame struct.
 * @param emg_active Emergency corridor active flag (1 = active, 0 = normal).
 * @param current_node Current ambulance position node.
 * @param target_node Next coordinate to preempt (target signal).
 * @param eta_seconds Estimated arrival duration in seconds.
 * @param dist_remain Remaining hops to the hospital.
 */
void SPIMaster_PackFrame(SpiFrame* frame, bool emg_active, NodeId current_node, NodeId target_node, uint16_t eta_seconds, uint8_t dist_remain);

/**
 * @brief Writes the raw 32-bit SPI frame word to a virtual serial log file.
 *        Simulates physical SPI transaction.
 * @param frame Const pointer to the packed SpiFrame struct.
 * @param filepath Path to the output virtual register file.
 * @return true if write succeeded, false otherwise.
 */
bool SPIMaster_WriteFrame(const SpiFrame* frame, const char* filepath);

#endif // SPI_MASTER_H
