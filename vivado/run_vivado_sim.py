#!/usr/bin/env python3
"""
run_vivado_sim.py
Automates the compilation and simulation of Verilog modules using Xilinx Vivado tools (xelab/xsim).
"""

import os
import subprocess
import sys
import glob

def find_vivado_bin():
    # Check if they are in the environment PATH
    try:
        subprocess.run(["xelab", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "" # Means they are in PATH already
    except FileNotFoundError:
        pass

    # Common Windows installation directories
    paths = [
        r"C:\Xilinx\Vivado\*\bin",
        r"D:\Xilinx\Vivado\*\bin"
    ]
    
    for path_pattern in paths:
        matching_dirs = glob.glob(path_pattern)
        if matching_dirs:
            # Sort to get the latest version
            matching_dirs.sort(reverse=True)
            return matching_dirs[0]
            
    return None

def main():
    print("=========================================")
    print("      Vivado Simulation Runner Script    ")
    print("=========================================")

    vivado_bin = find_vivado_bin()
    if vivado_bin is None:
        print("[ERROR] Vivado installation not found in PATH or standard folders.")
        print("Please ensure Vivado is installed and 'xelab' / 'xsim' are available.")
        print("\nManual Steps:")
        print("1. Open Vivado Tcl Shell or Command Prompt.")
        print("2. Navigate to: " + os.getcwd())
        print("3. Run the following commands:")
        print("   xelab -s sim -relax -prj green_corridor.prj -top tb_green_corridor")
        print("   xsim sim -runall")
        sys.exit(1)

    # Set up command paths
    xelab_cmd = os.path.join(vivado_bin, "xelab") if vivado_bin else "xelab"
    xsim_cmd = os.path.join(vivado_bin, "xsim") if vivado_bin else "xsim"

    # Define source files relative to vivado dir
    vivado_dir = os.path.dirname(os.path.abspath(__file__))
    rtl_files = [
        "rtl/signal_fsm.v",
        "rtl/emergency_fsm.v",
        "rtl/corridor_controller.v",
        "rtl/green_corridor_top.v"
    ]
    tb_file = "testbench/tb_green_corridor.v"

    # Convert paths to absolute
    rtl_abs = [os.path.join(vivado_dir, f) for f in rtl_files]
    tb_abs = os.path.join(vivado_dir, tb_file)

    # Create prj file for xelab
    prj_path = os.path.join(vivado_dir, "green_corridor.prj")
    print(f"Creating project definition: {prj_path}")
    with open(prj_path, "w") as f:
        for r in rtl_abs:
            # Replace backslashes with forward slashes for Vivado compatibility
            r_fs = r.replace('\\', '/')
            f.write(f"verilog xil_defaultlib \"{r_fs}\"\n")
        tb_fs = tb_abs.replace('\\', '/')
        f.write(f"verilog xil_defaultlib \"{tb_fs}\"\n")

    print("\nCompiling Verilog files with xelab...")
    compile_cmd = [
        xelab_cmd,
        "-prj", prj_path,
        "-s", "sim_snapshot",
        "-relax",
        "-top", "tb_green_corridor",
        "-L", "xil_defaultlib"
    ]
    
    # Run xelab compilation
    result = subprocess.run(compile_cmd, cwd=vivado_dir, text=True)
    if result.returncode != 0:
        print("[ERROR] Compilation failed. See compiler output above.")
        sys.exit(1)

    print("\nRunning simulation with xsim...")
    sim_run_cmd = [
        xsim_cmd,
        "sim_snapshot",
        "-runall"
    ]
    
    # Run xsim simulation
    subprocess.run(sim_run_cmd, cwd=vivado_dir)
    print("\nSimulation complete.")

if __name__ == "__main__":
    main()
