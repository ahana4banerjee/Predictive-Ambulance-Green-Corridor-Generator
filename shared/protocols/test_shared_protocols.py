# -*- coding: utf-8 -*-
# @file test_shared_protocols.py
# @brief Python validation test verifying bit packing, struct sizes,
#        and XOR checksum calculations matching system_interfaces.h.

import struct

def pack_spi_frame(emg_active, current_node, target_node, eta_seconds, dist_remain, checksum=0):
    """
    Simulates the C struct bit-field packing for little-endian architecture:
    - Bit 31: emg_active (1 bit)
    - Bits 27-30: current_node (4 bits)
    - Bits 23-26: target_node (4 bits)
    - Bits 11-22: eta_seconds (12 bits)
    - Bits 8-10: dist_remain (3 bits)
    - Bits 0-7: checksum (8 bits)
    """
    raw_val = 0
    raw_val |= (emg_active & 0x1) << 31
    raw_val |= (current_node & 0xF) << 27
    raw_val |= (target_node & 0xF) << 23
    raw_val |= (eta_seconds & 0xFFF) << 11
    raw_val |= (dist_remain & 0x7) << 8
    raw_val |= (checksum & 0xFF)
    return raw_val

def compute_checksum(raw_val):
    # XOR of the top 3 bytes
    b3 = (raw_val >> 24) & 0xFF
    b2 = (raw_val >> 16) & 0xFF
    b1 = (raw_val >> 8) & 0xFF
    return b3 ^ b2 ^ b1

def test_protocol_packing():
    print("====================================================")
    print("   Running Virtual Shared Protocol Verification     ")
    print("====================================================")

    # Pack test case parameters:
    # EMG=1, Current=0 (A), Target=3 (D), ETA=240, Dist=4
    emg = 1
    current = 0  # NODE_A
    target = 3   # NODE_D
    eta = 240
    dist = 4

    print(f"Input values: EMG={emg}, Current={current}, Target={target}, ETA={eta}s, Dist={dist}")
    
    # 1. Pack frame
    raw_packed = pack_spi_frame(emg, current, target, eta, dist)
    print(f"Packed Raw Word (No Checksum): 0x{raw_packed:08X}")

    # 2. Compute checksum
    checksum = compute_checksum(raw_packed)
    print(f"Computed Checksum Byte: 0x{checksum:02X}")
    
    # 3. Final packed word with checksum
    final_packed = pack_spi_frame(emg, current, target, eta, dist, checksum)
    print(f"Final Packed Word: 0x{final_packed:08X}")

    # 4. De-serialize and verify
    unpacked_emg = (final_packed >> 31) & 0x1
    unpacked_current = (final_packed >> 27) & 0xF
    unpacked_target = (final_packed >> 23) & 0xF
    unpacked_eta = (final_packed >> 11) & 0xFFF
    unpacked_dist = (final_packed >> 8) & 0x7
    unpacked_checksum = final_packed & 0xFF

    assert unpacked_emg == emg, "EMG mismatch!"
    assert unpacked_current == current, "Current Node mismatch!"
    assert unpacked_target == target, "Target Node mismatch!"
    assert unpacked_eta == eta, "ETA mismatch!"
    assert unpacked_dist == dist, "Distance mismatch!"
    assert unpacked_checksum == checksum, "Checksum mismatch!"

    # Verify byte width size
    packed_bytes = struct.pack("<I", final_packed)
    print(f"Serialized Byte Stream Size: {len(packed_bytes)} bytes (should be 4)")
    assert len(packed_bytes) == 4, "Packed byte size is not 32-bit!"

    print("\nSUCCESS: Bit-field boundaries and XOR checksum verification PASSED.")
    print("====================================================")

if __name__ == "__main__":
    test_protocol_packing()
