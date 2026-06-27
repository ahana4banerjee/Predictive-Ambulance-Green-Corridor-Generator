/**
 * @file test_spi_master.c
 * @brief Unit tests for the SPI Master Packet Encoder on STM32.
 */

#include <stdio.h>
#include <assert.h>
#include <stdbool.h>
#include "../include/spi_master.h"

int main() {
    printf("===========================================\n");
    printf("        Running STM32 SPI Master Unit Test  \n");
    printf("===========================================\n");

    SpiFrame frame;
    
    // Test Case 1: EMG=1, Current=0 (A), Target=3 (D), ETA=240, Dist=4
    SPIMaster_PackFrame(&frame, true, NODE_A, NODE_D, 240, 4);
    
    printf("Test Case 1 Output:\n");
    printf("  Raw Data: 0x%08X\n", frame.raw_data);
    printf("  EMG Active: %d\n", frame.fields.emg_active);
    printf("  Current Node: %d (Expected: %d)\n", frame.fields.current_node, NODE_A);
    printf("  Target Node: %d (Expected: %d)\n", frame.fields.target_node, NODE_D);
    printf("  ETA: %d (Expected: 240)\n", frame.fields.eta_seconds);
    printf("  Distance: %d (Expected: 4)\n", frame.fields.dist_remain);
    printf("  Checksum: 0x%02X\n", frame.fields.checksum);
    
    assert(frame.fields.emg_active == 1);
    assert(frame.fields.current_node == NODE_A);
    assert(frame.fields.target_node == NODE_D);
    assert(frame.fields.eta_seconds == 240);
    assert(frame.fields.dist_remain == 4);
    
    // Check checksum XOR
    uint8_t chk = compute_spi_checksum(&frame);
    assert(frame.fields.checksum == chk);
    printf("  [PASS] Checksum matched compute_spi_checksum.\n\n");
    
    // Test writing to a temporary file
    const char* filepath = "simulation/virtual_bus/packets/spi_tx_temp.bin";
    bool success = SPIMaster_WriteFrame(&frame, filepath);
    assert(success);
    printf("  [PASS] SPI frame written to %s.\n\n", filepath);

    printf("===========================================\n");
    printf("       STM32 SPI MASTER TESTS PASSED        \n");
    printf("===========================================\n");
    return 0;
}
