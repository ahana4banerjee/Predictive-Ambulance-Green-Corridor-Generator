#!/usr/bin/env python3
"""
analytics.py
Loads CSV logs, calculates system metrics, prints a visual dashboard console report,
and saves comparison charts for report documentation.
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# Adjust path to import stats_parser from the same folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from stats_parser import parse_run_stats

def main():
    # 1. Paths to CSV Files
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    # 2. Parse CSV Statistics
    s1_corr = parse_run_stats(os.path.join(data_dir, "s1_corridor.csv"))
    s1_norm = parse_run_stats(os.path.join(data_dir, "s1_normal.csv"))
    s2_corr = parse_run_stats(os.path.join(data_dir, "s2_corridor.csv"))
    s2_norm = parse_run_stats(os.path.join(data_dir, "s2_normal.csv"))
    s3_corr = parse_run_stats(os.path.join(data_dir, "s3_corridor.csv"))
    s3_norm = parse_run_stats(os.path.join(data_dir, "s3_normal.csv"))
    s4_corr = parse_run_stats(os.path.join(data_dir, "s4_corridor.csv"))
    s4_norm = parse_run_stats(os.path.join(data_dir, "s4_normal.csv"))
    s5_norm = parse_run_stats(os.path.join(data_dir, "s5_normal.csv"))
    
    if not (s1_corr and s1_norm and s2_corr and s2_norm and s3_corr and s3_norm and s4_corr and s4_norm and s5_norm):
        print("Error: Missing Scenario CSV files. Please run run_stm32_tests.py first.")
        sys.exit(1)
        
    # 3. Calculate Performance Metrics
    # Scenario 1 Metrics
    s1_t_saved = s1_norm['travel_time'] - s1_corr['travel_time']
    s1_delay_reduction = (float(s1_t_saved) / s1_norm['travel_time']) * 100.0 if s1_norm['travel_time'] > 0 else 0.0
    s1_total_signals = len(s1_corr['arrivals'])
    s1_signals_cleared = sum(1 for j, (t, sig) in s1_corr['arrivals'].items() if sig == "GREEN")
    s1_efficiency = (float(s1_signals_cleared) / s1_total_signals) * 100.0 if s1_total_signals > 0 else 0.0
    s1_stops_avoided = s1_norm['stops_count'] - s1_corr['stops_count']
    
    # Scenario 2 Metrics
    s2_t_saved = s2_norm['travel_time'] - s2_corr['travel_time']
    s2_delay_reduction = (float(s2_t_saved) / s2_norm['travel_time']) * 100.0 if s2_norm['travel_time'] > 0 else 0.0
    s2_total_signals = len(s2_corr['arrivals'])
    s2_signals_cleared = sum(1 for j, (t, sig) in s2_corr['arrivals'].items() if sig == "GREEN")
    s2_efficiency = (float(s2_signals_cleared) / s2_total_signals) * 100.0 if s2_total_signals > 0 else 0.0
    s2_stops_avoided = s2_norm['stops_count'] - s2_corr['stops_count']
    
    # Scenario 3 Metrics
    s3_t_saved = s3_norm['travel_time'] - s3_corr['travel_time']
    s3_delay_reduction = (float(s3_t_saved) / s3_norm['travel_time']) * 100.0 if s3_norm['travel_time'] > 0 else 0.0
    s3_total_signals = len(s3_corr['arrivals'])
    s3_signals_cleared = sum(1 for j, (t, sig) in s3_corr['arrivals'].items() if sig == "GREEN")
    s3_efficiency = (float(s3_signals_cleared) / s3_total_signals) * 100.0 if s3_total_signals > 0 else 0.0
    s3_stops_avoided = s3_norm['stops_count'] - s3_corr['stops_count']

    # Scenario 4 Metrics
    s4_t_saved = s4_norm['travel_time'] - s4_corr['travel_time']
    s4_delay_reduction = (float(s4_t_saved) / s4_norm['travel_time']) * 100.0 if s4_norm['travel_time'] > 0 else 0.0
    s4_total_signals = len(s4_corr['arrivals'])
    s4_signals_cleared = sum(1 for j, (t, sig) in s4_corr['arrivals'].items() if sig == "GREEN")
    s4_efficiency = (float(s4_signals_cleared) / s4_total_signals) * 100.0 if s4_total_signals > 0 else 0.0
    s4_stops_avoided = s4_norm['stops_count'] - s4_corr['stops_count']
    
    # 4. Print Dashboard Terminal Console Report
    print("=========================================================================================================")
    print("                 PREDICTIVE AMBULANCE GREEN CORRIDOR - SYSTEM PERFORMANCE METRICS                        ")
    print("=========================================================================================================")
    print(f"| Metric                      | S1 (Standard)       | S2 (Bypass)         | S3 (Mixed Traffic)  | S4 (High Traffic)   |")
    print(f"|-----------------------------|---------------------|---------------------|---------------------|---------------------|")
    print(f"| Normal Travel Time          | {s1_norm['travel_time']:4d} s ({s1_norm['travel_time']/60:.2f}m)  | {s2_norm['travel_time']:4d} s ({s2_norm['travel_time']/60:.2f}m)  | {s3_norm['travel_time']:4d} s ({s3_norm['travel_time']/60:.2f}m)  | {s4_norm['travel_time']:4d} s ({s4_norm['travel_time']/60:.2f}m)  |")
    print(f"| Corridor Travel Time        | {s1_corr['travel_time']:4d} s ({s1_corr['travel_time']/60:.2f}m)  | {s2_corr['travel_time']:4d} s ({s2_corr['travel_time']/60:.2f}m)  | {s3_corr['travel_time']:4d} s ({s3_corr['travel_time']/60:.2f}m)  | {s4_corr['travel_time']:4d} s ({s4_corr['travel_time']/60:.2f}m)  |")
    print(f"| Travel Time Saved           | {s1_t_saved:4d} s ({s1_t_saved/60:.2f}m)   | {s2_t_saved:4d} s ({s2_t_saved/60:.2f}m)   | {s3_t_saved:4d} s ({s3_t_saved/60:.2f}m)   | {s4_t_saved:4d} s ({s4_t_saved/60:.2f}m)   |")
    print(f"| Delay Reduction %           | {s1_delay_reduction:5.2f}%             | {s2_delay_reduction:5.2f}%             | {s3_delay_reduction:5.2f}%             | {s4_delay_reduction:5.2f}%             |")
    print(f"| Normal Stops                | {s1_norm['stops_count']:5d} stops          | {s2_norm['stops_count']:5d} stops          | {s3_norm['stops_count']:5d} stops          | {s4_norm['stops_count']:5d} stops          |")
    print(f"| Corridor Stops              | {s1_corr['stops_count']:5d} stops          | {s2_corr['stops_count']:5d} stops          | {s3_corr['stops_count']:5d} stops          | {s4_corr['stops_count']:5d} stops          |")
    print(f"| Stops Avoided               | {s1_stops_avoided:5d} stops          | {s2_stops_avoided:5d} stops          | {s3_stops_avoided:5d} stops          | {s4_stops_avoided:5d} stops          |")
    print(f"| Signals Cleared             | {s1_signals_cleared:2d} / {s1_total_signals:2d}               | {s2_signals_cleared:2d} / {s2_total_signals:2d}               | {s3_signals_cleared:2d} / {s3_total_signals:2d}               | {s4_signals_cleared:2d} / {s4_total_signals:2d}               |")
    print(f"| Corridor Efficiency %       | {s1_efficiency:5.2f}%             | {s2_efficiency:5.2f}%             | {s3_efficiency:5.2f}%             | {s4_efficiency:5.2f}%             |")
    print("=========================================================================================================")
    print(f" Scenario 5 Baseline Check: Simulation duration {s5_norm['travel_time']} seconds, normal signal cycling verified.")
    print("=========================================================================================================")
    
    # 5. Generate Graphical Visualization Charts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle("Predictive Green Corridor System Performance Analytics", fontsize=16, fontweight='bold', y=0.98)
    
    # Chart 1: Travel Time Comparison
    labels = ['S1\n(Standard)', 'S2\n(Bypass)', 'S3\n(Mixed)', 'S4\n(High Traffic)']
    normal_times = [s1_norm['travel_time'], s2_norm['travel_time'], s3_norm['travel_time'], s4_norm['travel_time']]
    corridor_times = [s1_corr['travel_time'], s2_corr['travel_time'], s3_corr['travel_time'], s4_corr['travel_time']]
    
    x = np.arange(len(labels))
    width = 0.35
    
    rects1 = ax1.bar(x - width/2, normal_times, width, label='Normal Mode (No Preemption)', color='#e056fd')
    rects2 = ax1.bar(x + width/2, corridor_times, width, label='Corridor Mode (Active Override)', color='#22a6b3')
    
    ax1.set_ylabel('Travel Time (seconds)', fontsize=12)
    ax1.set_title('Travel Time Savings Comparison', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=11)
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add values on top of bars
    def autolabel(rects, ax):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}s\n({height/60:.1f}m)',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold')
            
    autolabel(rects1, ax1)
    autolabel(rects2, ax1)
    
    # Chart 2: Red-Light Stops Avoided
    normal_stops = [s1_norm['stops_count'], s2_norm['stops_count'], s3_norm['stops_count'], s4_norm['stops_count']]
    corridor_stops = [s1_corr['stops_count'], s2_corr['stops_count'], s3_corr['stops_count'], s4_corr['stops_count']]
    
    rects3 = ax2.bar(x - width/2, normal_stops, width, label='Normal Mode Stops', color='#ff7675')
    rects4 = ax2.bar(x + width/2, corridor_stops, width, label='Corridor Mode Stops', color='#55efc4')
    
    ax2.set_ylabel('Number of Red-Light Stops', fontsize=12)
    ax2.set_title('Red-Light Stops Avoided', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=11)
    ax2.legend(fontsize=10)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    def autolabel_stops(rects, ax):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
            
    autolabel_stops(rects3, ax2)
    autolabel_stops(rects4, ax2)
    
    plt.tight_layout()
    
    # 6. Save Charts to Folders
    dashboard_graphs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs")
    results_graphs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "graphs")
    
    os.makedirs(dashboard_graphs_dir, exist_ok=True)
    os.makedirs(results_graphs_dir, exist_ok=True)
    
    graph_filename = "travel_time_comparison.png"
    plt.savefig(os.path.join(dashboard_graphs_dir, graph_filename), dpi=150)
    plt.savefig(os.path.join(results_graphs_dir, graph_filename), dpi=150)
    
    print(f"\nGraphical analytics chart saved successfully to:")
    print(f"  - {os.path.join(dashboard_graphs_dir, graph_filename)}")
    print(f"  - {os.path.join(results_graphs_dir, graph_filename)}")

if __name__ == "__main__":
    main()
