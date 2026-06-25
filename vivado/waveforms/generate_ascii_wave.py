#!/usr/bin/env python3
"""
generate_ascii_wave.py
Parses tb_signal_fsm.vcd and tb_green_corridor.vcd to generate clean,
text-based ASCII timing diagrams showing FSM state transitions.
Uses high-performance parsing and single-pass sampling.
"""

import os
import re
import sys

def parse_vcd(vcd_path, signals_to_track):
    """
    Parses VCD file and returns a dictionary of:
    {
       'times': [t0, t1, t2, ...],  # sorted timestamps in ps
       'changes': {
           timestamp: { 'signal_name': 'value' }
       }
    }
    """
    if not os.path.exists(vcd_path):
        print(f"[WARNING] VCD file not found: {vcd_path}")
        return None

    var_mappings = {}  # symbol -> signal_name
    timeline = {}
    current_time = 0

    var_pattern = re.compile(r"\$var\s+(?:\w+)\s+(\d+)\s+(\S+)\s+(\w+)(?:\s+\[[^\]]+\])?\s+\$end")

    with open(vcd_path, "r", encoding="utf-8", errors="ignore") as f:
        # Step 1: Read and parse the header only (up to $enddefinitions)
        header_lines = []
        for line in f:
            header_lines.append(line)
            if "$enddefinitions" in line:
                break
        
        header = "".join(header_lines)
        for match in var_pattern.finditer(header):
            width, symbol, name = match.groups()
            for track_name in signals_to_track:
                if name == track_name or track_name.startswith(name + "["):
                    var_mappings[symbol] = track_name
                    break

        # Step 2: Parse value changes from the rest of the file
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Check for time marker (e.g. #20000)
            if line.startswith("#"):
                try:
                    current_time = int(line[1:])
                except ValueError:
                    pass
                continue
            
            # Check for vector changes (starts with 'b' or 'B')
            if line[0] in ('b', 'B'):
                parts = line.split()
                if len(parts) == 2:
                    val = parts[0][1:] # strip 'b'
                    symbol = parts[1]
                    if symbol in var_mappings:
                        sig_name = var_mappings[symbol]
                        if current_time not in timeline:
                            timeline[current_time] = {}
                        timeline[current_time][sig_name] = val
                continue
            
            # Check for 1-bit changes (e.g. 1!, 0!)
            if line[0] in ("0", "1", "x", "X", "z", "Z"):
                val = line[0]
                symbol = line[1:]
                if symbol in var_mappings:
                    sig_name = var_mappings[symbol]
                    if current_time not in timeline:
                        timeline[current_time] = {}
                    timeline[current_time][sig_name] = val

    # Step 3: Return sorted transitions
    all_times = sorted(list(timeline.keys()))
    if not all_times:
        return None

    return {
        'times': all_times,
        'changes': timeline,
        'signals': signals_to_track
    }

def decode_signal_state(val):
    # RED = 2'b00, GREEN = 2'b01, YELLOW = 2'b10
    val_clean = val.zfill(2)
    if val_clean == "00":
        return "RED"
    elif val_clean == "01":
        return "GRN"
    elif val_clean == "10":
        return "YEL"
    else:
        return "UNK"

def decode_emergency_state(val):
    # NORMAL = 0, DETECTED = 1, PREPARE = 2, ACTIVE = 3, RECOVERY = 4
    val_int = int(val, 2) if all(c in '01' for c in val) else -1
    if val_int == 0:
        return "NORMAL"
    elif val_int == 1:
        return "DETECTED"
    elif val_int == 2:
        return "PREPARE"
    elif val_int == 3:
        return "ACTIVE"
    elif val_int == 4:
        return "RECOVERY"
    else:
        return "UNKNOWN"

def decode_node(val):
    # NODE_A = 0, NODE_B = 1, NODE_C = 2, NODE_I = 8
    val_int = int(val, 2) if all(c in '01' for c in val) else -1
    if val_int == 0:
        return "A"
    elif val_int == 1:
        return "B"
    elif val_int == 2:
        return "C"
    elif val_int == 8:
        return "I"
    elif val_int == 15:
        return "-"
    else:
        return str(val_int)

def get_sampled_values(data, signal_name, step_ps):
    """
    Samples signal value at uniform time intervals (step_ps) in a single pass.
    """
    times = data['times']
    changes = data['changes']
    max_time = times[-1]
    
    samples = []
    current_val = "0"
    time_idx = 0
    num_times = len(times)
    
    for t in range(0, max_time + step_ps, step_ps):
        # Advance time_idx to process all changes up to time t
        while time_idx < num_times and times[time_idx] <= t:
            pt = times[time_idx]
            if signal_name in changes[pt]:
                current_val = changes[pt][signal_name]
            time_idx += 1
            
        samples.append(current_val)
        
        # Rewind time_idx by 1 so we re-check the last state next iteration
        if time_idx > 0:
            time_idx -= 1
            
    return samples

def generate_signal_fsm_ascii(data):
    """
    Generates FSM verification report for Signal FSM
    """
    if not data:
        return "No data available."

    lines = []
    lines.append("==================================================================================")
    lines.append("              Independent Signal FSM Waveform Verification Report                 ")
    lines.append("==================================================================================\n")
    lines.append("Sampled Signal States (sampled at time transitions):")
    lines.append("-" * 82)
    lines.append(f"{'Time (ns)':<10} | {'RST':<3} | {'OVR_GRN':<7} | {'SUSPEND':<7} | {'State Hex':<9} | {'State Name':<10}")
    lines.append("-" * 82)

    # Track values
    rst = "0"
    ovr = "0"
    sus = "0"
    state = "00"

    last_state = None
    for t in data['times']:
        changes = data['changes'][t]
        if 'rst' in changes: rst = changes['rst']
        if 'override_green' in changes: ovr = changes['override_green']
        if 'suspend' in changes: sus = changes['suspend']
        if 'signal_state' in changes: state = changes['signal_state']

        curr = (rst, ovr, sus, state)
        if curr != last_state:
            # Print time in nanoseconds (t is in ps, so t // 1000)
            lines.append(f"{t // 1000:<10} | {rst:<3} | {ovr:<7} | {sus:<7} | 2'b{state:<6} | {decode_signal_state(state):<10}")
            last_state = curr

    lines.append("-" * 82)
    
    # Draw simple ASCII graph (sampled every 20,000 ps = 20 ns)
    step_size = 20000
    sampled_state = get_sampled_values(data, 'signal_state', step_size)
    sampled_ovr = get_sampled_values(data, 'override_green', step_size)
    sampled_sus = get_sampled_values(data, 'suspend', step_size)
    
    lines.append("\nSignal Transition Timeline (each column = 20ns):")
    lines.append("RED:    " + "".join("█" if decode_signal_state(val) == "RED" else "_" for val in sampled_state))
    lines.append("GREEN:  " + "".join("█" if decode_signal_state(val) == "GRN" else "_" for val in sampled_state))
    lines.append("YELLOW: " + "".join("█" if decode_signal_state(val) == "YEL" else "_" for val in sampled_state))
    lines.append("OVRG:   " + "".join("█" if val == "1" else "_" for val in sampled_ovr))
    lines.append("SUSP:   " + "".join("█" if val == "1" else "_" for val in sampled_sus))
    lines.append("Time:   " + "".join(str((i*20)//100 % 10) for i in range(len(sampled_state))))
    lines.append("        (Time digit represents hundreds of ns, e.g. 5 = 500ns, 0 = 1000ns)")
    
    return "\n".join(lines)

def generate_green_corridor_ascii(data):
    """
    Generates coordinated Green Corridor wave timeline
    """
    if not data:
        return "No data available."

    lines = []
    lines.append("==================================================================================")
    lines.append("             Top-Level Green Corridor Waveform Verification Report                ")
    lines.append("==================================================================================\n")
    lines.append("Active Transitions Log:")
    lines.append("-" * 105)
    lines.append(f"{'Time (ns)':<10} | {'TRIG':<4} | {'NODE':<4} | {'ETA':<5} | {'SIG A':<5} (Mode)     | {'SIG B':<5} (Mode)     | {'SIG C':<5} (Mode)     | {'EMG_ACT':<7}")
    lines.append("-" * 105)

    # Initialize variables
    trig = "0"
    node = "1111"
    eta = "000"
    sig_a = "00"
    sig_b = "00"
    sig_c = "00"
    mode_a = "000"
    mode_b = "000"
    mode_c = "000"
    emg_act = "0"

    last_state = None
    for t in data['times']:
        changes = data['changes'][t]
        if 'ambulance_trigger' in changes: trig = changes['ambulance_trigger']
        if 'current_node' in changes: node = changes['current_node']
        if 'eta_seconds' in changes: eta = changes['eta_seconds']
        if 'signal_a' in changes: sig_a = changes['signal_a']
        if 'signal_b' in changes: sig_b = changes['signal_b']
        if 'signal_c' in changes: sig_c = changes['signal_c']
        if 'mode_a' in changes: mode_a = changes['mode_a']
        if 'mode_b' in changes: mode_b = changes['mode_b']
        if 'mode_c' in changes: mode_c = changes['mode_c']
        if 'emergency_active' in changes: emg_act = changes['emergency_active']

        # Exclude eta from state comparison to avoid redundant printing on every timer tick
        curr = (trig, node, sig_a, sig_b, sig_c, mode_a, mode_b, mode_c, emg_act)
        if curr != last_state:
            # Print time in nanoseconds
            lines.append(f"{t // 1000:<10} | {trig:<4} | {decode_node(node):<4} | {int(eta, 2) if all(c in '01' for c in eta) else 0:<5} | "
                         f"{decode_signal_state(sig_a):<5} ({decode_emergency_state(mode_a):<8}) | "
                         f"{decode_signal_state(sig_b):<5} ({decode_emergency_state(mode_b):<8}) | "
                         f"{decode_signal_state(sig_c):<5} ({decode_emergency_state(mode_c):<8}) | {emg_act:<7}")
            last_state = curr

    lines.append("-" * 105)

    # Visual representation of Green Light Waves (sampled every 20,000 ps = 20 ns)
    step_size = 20000
    sampled_a = get_sampled_values(data, 'signal_a', step_size)
    sampled_b = get_sampled_values(data, 'signal_b', step_size)
    sampled_c = get_sampled_values(data, 'signal_c', step_size)
    sampled_trig = get_sampled_values(data, 'ambulance_trigger', step_size)
    sampled_node = get_sampled_values(data, 'current_node', step_size)

    lines.append("\nVisual Green Wave Timeline (█ = Green, _ = Red/Yellow):")
    lines.append("Ambulance: " + "".join(decode_node(val) if sampled_trig[i] == "1" else " " for i, val in enumerate(sampled_node)))
    lines.append("Signal A:  " + "".join("█" if decode_signal_state(val) == "GRN" else "_" for val in sampled_a))
    lines.append("Signal B:  " + "".join("█" if decode_signal_state(val) == "GRN" else "_" for val in sampled_b))
    lines.append("Signal C:  " + "".join("█" if decode_signal_state(val) == "GRN" else "_" for val in sampled_c))
    lines.append("Time (ns): " + "".join(str((i*20)//100 % 10) for i in range(len(sampled_a))))
    lines.append("           (Each column represents 20ns. Check that Signal opens sequentially A -> B -> C)")

    return "\n".join(lines)

def main():
    vivado_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    waveforms_dir = os.path.join(vivado_dir, "waveforms")
    os.makedirs(waveforms_dir, exist_ok=True)

    # 1. Parse Signal FSM
    vcd_fsm = os.path.join(vivado_dir, "tb_signal_fsm.vcd")
    print(f"Parsing {vcd_fsm}...")
    fsm_data = parse_vcd(vcd_fsm, ['rst', 'override_green', 'suspend', 'signal_state'])
    if fsm_data:
        report = generate_signal_fsm_ascii(fsm_data)
        report_path = os.path.join(waveforms_dir, "signal_fsm_waves.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Generated Signal FSM Waveform Report: {report_path}")
    else:
        print("[ERROR] Failed to parse Signal FSM VCD.")

    # 2. Parse Green Corridor
    vcd_corridor = os.path.join(vivado_dir, "tb_green_corridor.vcd")
    print(f"Parsing {vcd_corridor}...")
    corridor_data = parse_vcd(vcd_corridor, [
        'ambulance_trigger', 'current_node', 'eta_seconds',
        'signal_a', 'signal_b', 'signal_c',
        'mode_a', 'mode_b', 'mode_c', 'emergency_active'
    ])
    if corridor_data:
        report = generate_green_corridor_ascii(corridor_data)
        report_path = os.path.join(waveforms_dir, "green_corridor_waves.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Generated Green Corridor Waveform Report: {report_path}")
    else:
        print("[ERROR] Failed to parse Green Corridor VCD.")

if __name__ == "__main__":
    main()
