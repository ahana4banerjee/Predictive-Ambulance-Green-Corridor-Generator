#!/usr/bin/env python3
"""
stats_parser.py
Parses the generated CSV logs to calculate:
1. Total travel time (Normal Mode vs. Corridor Mode)
2. Number of red-light stops avoided
"""

import os
import csv

def parse_run_stats(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return None
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            
            rows = list(reader)
            
        # 1. Calculate Total Travel Time
        timestamps = [int(row[0]) for row in rows]
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        # Total duration is from start to arrival at final destination (excluding post-arrival safety logs)
        # Find the last timestamp where ambulance_position is not 'I'
        active_times = [int(row[0]) for row in rows if row[3] != 'I']
        if active_times:
            # The arrival at I is the timestamp immediately after active transit
            arrival_time = max(active_times)
            # Find the actual arrival step in raw rows
            arrival_rows = [int(row[0]) for row in rows if row[3] == 'I']
            if arrival_rows:
                arrival_time = min(arrival_rows)
            travel_time = arrival_time - min_time
        else:
            travel_time = max_time - min_time
            
        # 2. Calculate Red-Light Stops
        # A stop occurs when the ambulance arrives at a junction and the signal is RED or YELLOW.
        # Find arrival timestamp for each junction on the route
        arrivals = {}
        for row in rows:
            t = int(row[0])
            junction = row[1]
            sig_state = row[2]
            amb_pos = row[3]
            
            # If the ambulance is currently at this junction
            if amb_pos == junction:
                if junction not in arrivals:
                    arrivals[junction] = (t, sig_state)
                else:
                    # Keep the earliest timestamp
                    if t < arrivals[junction][0]:
                        arrivals[junction] = (t, sig_state)
                        
        stops_count = 0
        stopped_junctions = []
        for junc, (t, sig) in arrivals.items():
            # If the signal was RED or YELLOW upon arrival, it's a traffic light stop
            if sig in ["RED", "YELLOW"]:
                stops_count += 1
                stopped_junctions.append((junc, t, sig))
                
        return {
            'filepath': filepath,
            'travel_time': travel_time,
            'stops_count': stops_count,
            'stopped_junctions': stopped_junctions,
            'arrivals': arrivals
        }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def main():
    print("=========================================")
    print("      WEEK 5 DAY 3: PERFORMANCE METRICS  ")
    print("=========================================")
    
    # Analyze Scenario 1: Standard/Low Traffic (Start at A)
    corridor_file = "dashboard/data/run_corridor.csv"
    normal_file = "dashboard/data/run_normal.csv"
    
    stats_corr = parse_run_stats(corridor_file)
    stats_norm = parse_run_stats(normal_file)
    
    if stats_corr and stats_norm:
        print("\n=== SCENARIO 1: Standard Route (A -> B -> C -> F -> I) ===")
        # 1. Travel Time Saved
        t_normal = stats_norm['travel_time']
        t_corridor = stats_corr['travel_time']
        time_saved = t_normal - t_corridor
        
        print(f"Normal Mode Travel Time   : {t_normal} seconds ({t_normal/60:.2f} minutes)")
        print(f"Corridor Mode Travel Time : {t_corridor} seconds ({t_corridor/60:.2f} minutes)")
        print(f"Travel Time Saved         : {time_saved} seconds ({time_saved/60:.2f} minutes)")
        
        # 2. Delay Reduction %
        delay_reduction_pct = (float(time_saved) / t_normal) * 100.0 if t_normal > 0 else 0.0
        print(f"Delay Reduction %         : {delay_reduction_pct:.2f}%")
        
        # 3. Signals Cleared
        # A signal is cleared if it is GREEN when the ambulance arrives.
        total_signals = len(stats_corr['arrivals'])
        signals_cleared_corr = sum(1 for j, (t, sig) in stats_corr['arrivals'].items() if sig == "GREEN")
        signals_cleared_norm = sum(1 for j, (t, sig) in stats_norm['arrivals'].items() if sig == "GREEN")
        
        print(f"\nNormal Mode Signals Green : {signals_cleared_norm} / {total_signals}")
        print(f"Corridor Mode Signals Green: {signals_cleared_corr} / {total_signals} (Cleared)")
        
        # 4. Corridor Efficiency %
        corridor_efficiency = (float(signals_cleared_corr) / total_signals) * 100.0 if total_signals > 0 else 0.0
        print(f"Corridor Efficiency %     : {corridor_efficiency:.2f}%")
        
        # 5. Stops avoided
        stops_avoided = stats_norm['stops_count'] - stats_corr['stops_count']
        print(f"\nNormal Mode Stops         : {stats_norm['stops_count']} stops")
        for j, t, sig in stats_norm['stopped_junctions']:
            print(f"  - Stopped at Junction {j} at t={t}s (Signal: {sig})")
        print(f"Corridor Mode Stops       : {stats_corr['stops_count']} stops")
        print(f"Red-Light Stops Avoided   : {stops_avoided}")
        
    # Analyze Scenario 2: Congested Route Bypass (Start at A)
    corridor_bypass_file = "dashboard/data/run_corridor_bypass.csv"
    normal_bypass_file = "dashboard/data/run_normal_bypass.csv"
    
    stats_corr_bp = parse_run_stats(corridor_bypass_file)
    stats_norm_bp = parse_run_stats(normal_bypass_file)
    
    if stats_corr_bp and stats_norm_bp:
        print("\n=== SCENARIO 2: Congested Route Bypass (A -> D -> G -> H -> I) ===")
        # 1. Travel Time Saved
        t_normal_bp = stats_norm_bp['travel_time']
        t_corridor_bp = stats_corr_bp['travel_time']
        time_saved_bp = t_normal_bp - t_corridor_bp
        
        print(f"Normal Mode Travel Time   : {t_normal_bp} seconds ({t_normal_bp/60:.2f} minutes)")
        print(f"Corridor Mode Travel Time : {t_corridor_bp} seconds ({t_corridor_bp/60:.2f} minutes)")
        print(f"Travel Time Saved         : {time_saved_bp} seconds ({time_saved_bp/60:.2f} minutes)")
        
        # 2. Delay Reduction %
        delay_reduction_pct_bp = (float(time_saved_bp) / t_normal_bp) * 100.0 if t_normal_bp > 0 else 0.0
        print(f"Delay Reduction %         : {delay_reduction_pct_bp:.2f}%")
        
        # 3. Signals Cleared
        total_signals_bp = len(stats_corr_bp['arrivals'])
        signals_cleared_corr_bp = sum(1 for j, (t, sig) in stats_corr_bp['arrivals'].items() if sig == "GREEN")
        signals_cleared_norm_bp = sum(1 for j, (t, sig) in stats_norm_bp['arrivals'].items() if sig == "GREEN")
        
        print(f"\nNormal Mode Signals Green : {signals_cleared_norm_bp} / {total_signals_bp}")
        print(f"Corridor Mode Signals Green: {signals_cleared_corr_bp} / {total_signals_bp} (Cleared)")
        
        # 4. Corridor Efficiency %
        corridor_efficiency_bp = (float(signals_cleared_corr_bp) / total_signals_bp) * 100.0 if total_signals_bp > 0 else 0.0
        print(f"Corridor Efficiency %     : {corridor_efficiency_bp:.2f}%")
        
        # 5. Stops avoided
        stops_avoided_bp = stats_norm_bp['stops_count'] - stats_corr_bp['stops_count']
        print(f"\nNormal Mode Stops         : {stats_norm_bp['stops_count']} stops")
        for j, t, sig in stats_norm_bp['stopped_junctions']:
            print(f"  - Stopped at Junction {j} at t={t}s (Signal: {sig})")
        print(f"Corridor Mode Stops       : {stats_corr_bp['stops_count']} stops")
        print(f"Red-Light Stops Avoided   : {stops_avoided_bp}")
        
    print("\n=========================================")

if __name__ == "__main__":
    main()
