/**
 * @file spi_master.c
 * @brief Implementation of the SPI Master Packet Encoder on STM32.
 */

#include "../include/spi_master.h"
#include <stdio.h>
#include <stddef.h>

void SPIMaster_PackFrame(SpiFrame* frame, bool emg_active, NodeId current_node, NodeId target_node, uint16_t eta_seconds, uint8_t dist_remain) {
    if (frame == NULL) {
        return;
    }
    
    // Clear register word
    frame->raw_data = 0;
    
    // Map control flags to register bitfields
    frame->fields.emg_active = emg_active ? 1 : 0;
    frame->fields.current_node = (uint32_t)current_node;
    frame->fields.target_node = (uint32_t)target_node;
    frame->fields.eta_seconds = (uint32_t)eta_seconds;
    frame->fields.dist_remain = (uint32_t)dist_remain;
    
    // Compute error-correcting XOR checksum and write to register
    uint8_t chk = compute_spi_checksum(frame);
    frame->fields.checksum = chk;
}

bool SPIMaster_WriteFrame(const SpiFrame* frame, const char* filepath) {
    if (frame == NULL || filepath == NULL) {
        return false;
    }
    
    FILE* file = fopen(filepath, "w");
    if (!file) {
        printf("ERROR: SPI Master - Cannot write to register file %s!\n", filepath);
        return false;
    }
    
    // Write packed raw 32-bit register word as standard hex string
    fprintf(file, "0x%08X\n", frame->raw_data);
    fclose(file);
    return true;
}
