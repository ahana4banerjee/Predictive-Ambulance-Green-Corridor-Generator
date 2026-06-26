#!/usr/bin/env python3
"""
verify_csv_logging.py
Tests and verifies that the generated CSV logs meet the schema and logical requirements.
"""

import os
import csv

def verify_csv(filepath):
    print(f"Verifying {filepath}...")
    if not os.path.exists(filepath):
        print(f"FAIL: File does not exist: {filepath}")
        return False
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # 1. Check Schema
            expected_header = ["timestamp", "junction", "signal_state", "ambulance_position", "traffic_density"]
            if header != expected_header:
                print(f"FAIL: Header mismatch. Expected {expected_header}, got {header}")
                return False
                
            rows = list(reader)
            
            # 2. Check Row Count
            if len(rows) == 0:
                print("FAIL: File is empty.")
                return False
                
            # 3. Validate Data Types and Values
            for idx, row in enumerate(rows):
                if len(row) != 5:
                    print(f"FAIL: Row {idx+2} has incorrect column count: {row}")
                    return False
                    
                timestamp_str, junction, signal_state, amb_pos, density = row
                
                # Check timestamp is integer
                try:
                    t = int(timestamp_str)
                    if t < 0:
                        print(f"FAIL: Row {idx+2} has negative timestamp: {t}")
                        return False
                except ValueError:
                    print(f"FAIL: Row {idx+2} has non-integer timestamp: {timestamp_str}")
                    return False
                    
                # Check junction is A-I
                if junction not in [chr(ord('A') + i) for i in range(9)]:
                    print(f"FAIL: Row {idx+2} has invalid junction label: {junction}")
                    return False
                    
                # Check signal state
                if signal_state not in ["RED", "GREEN", "YELLOW"]:
                    print(f"FAIL: Row {idx+2} has invalid signal state: {signal_state}")
                    return False
                    
                # Check ambulance position is A-I
                if amb_pos not in [chr(ord('A') + i) for i in range(9)] + ["-"]:
                    print(f"FAIL: Row {idx+2} has invalid ambulance position: {amb_pos}")
                    return False
                    
                # Check density is LOW/MEDIUM/HIGH
                if density not in ["LOW", "MEDIUM", "HIGH"]:
                    print(f"FAIL: Row {idx+2} has invalid traffic density: {density}")
                    return False
                    
        print(f"PASS: {filepath} verified successfully. ({len(rows)} records found)")
        return True
    except Exception as e:
        print(f"FAIL: Exception while reading file: {e}")
        return False

def main():
    files_to_verify = [
        "dashboard/data/s1_corridor.csv",
        "dashboard/data/s1_normal.csv",
        "dashboard/data/s2_corridor.csv",
        "dashboard/data/s2_normal.csv",
        "dashboard/data/s3_corridor.csv",
        "dashboard/data/s3_normal.csv",
        "dashboard/data/s4_corridor.csv",
        "dashboard/data/s4_normal.csv",
        "dashboard/data/s5_normal.csv"
    ]
    
    all_success = True
    for f in files_to_verify:
        success = verify_csv(f)
        if not success:
            all_success = False
            
    if all_success:
        print("\nAll CSV log files verified successfully. Schema and data parameters match!")
    else:
        print("\nSome verification tests failed. Please review the errors above.")
        
    return all_success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
