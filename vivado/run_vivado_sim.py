#!/usr/bin/env python3
"""
run_vivado_sim.py
Automates the compilation and simulation of Verilog modules using Xilinx/AMD Vivado tools (xelab/xsim).
Supports both the independent Signal FSM testbench and the full Green Corridor testbench.
"""

import os
import subprocess
import sys
import glob
import argparse

def find_vivado_bin():
    # Check if they are in the environment PATH
    try:
        subprocess.run(["xelab", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "" # Means they are in PATH already
    except FileNotFoundError:
        pass

    # Common Windows installation directories (including AMD Design Tools and custom paths)
    paths = [
        r"C:\AMDDesignTools\*\Vivado\bin",
        r"C:\AMDDesignTools\Vivado\*\bin",
        r"C:\AMDDesignTools\*\Vivado\*\bin",
        r"C:\Xilinx\Vivado\*\bin",
        r"D:\Xilinx\Vivado\*\bin"
    ]
    
    for path_pattern in paths:
        matching_dirs = glob.glob(path_pattern)
        if matching_dirs:
            # Sort to get the latest version
            matching_dirs.sort(reverse=True)
            for d in matching_dirs:
                if (os.path.exists(os.path.join(d, "xelab")) or 
                    os.path.exists(os.path.join(d, "xelab.bat")) or 
                    os.path.exists(os.path.join(d, "xelab.exe"))):
                    return d
            
    return None

def compile_and_run(vivado_bin, vivado_dir, tb_name, run_gui=False):
    if sys.platform.startswith("win") and vivado_bin:
        xelab_cmd = os.path.join(vivado_bin, "xelab.bat")
        xsim_cmd = os.path.join(vivado_bin, "xsim.bat")
    else:
        xelab_cmd = os.path.join(vivado_bin, "xelab") if vivado_bin else "xelab"
        xsim_cmd = os.path.join(vivado_bin, "xsim") if vivado_bin else "xsim"

    print(f"\n=========================================")
    print(f" Simulating Testbench: {tb_name}")
    print(f"=========================================")

    # Set up source files depending on testbench
    rtl_files = [
        "rtl/signal_fsm.v",
        "rtl/emergency_fsm.v",
        "rtl/corridor_controller.v",
        "rtl/green_corridor_top.v"
    ]
    
    if tb_name == "tb_signal_fsm":
        # Signal FSM testbench only requires signal_fsm.v and the tb file
        rtl_files = ["rtl/signal_fsm.v"]
        tb_file = "testbench/tb_signal_fsm.v"
        prj_name = "signal_fsm.prj"
        snapshot = "signal_fsm_snapshot"
    else:
        # Full green corridor simulation
        tb_file = "testbench/tb_green_corridor.v"
        prj_name = "green_corridor.prj"
        snapshot = "green_corridor_snapshot"

    rtl_abs = [os.path.join(vivado_dir, f) for f in rtl_files]
    tb_abs = os.path.join(vivado_dir, tb_file)

    # Create prj file for xelab
    prj_path = os.path.join(vivado_dir, prj_name)
    print(f"Creating project definition: {prj_path}")
    with open(prj_path, "w") as f:
        for r in rtl_abs:
            r_fs = r.replace('\\', '/')
            f.write(f"verilog xil_defaultlib \"{r_fs}\"\n")
        tb_fs = tb_abs.replace('\\', '/')
        f.write(f"verilog xil_defaultlib \"{tb_fs}\"\n")

    print(f"Compiling Verilog files with xelab for {tb_name}...")
    compile_cmd = [
        xelab_cmd,
        "-prj", prj_path,
        "-s", snapshot,
        "-relax",
        "-top", f"xil_defaultlib.{tb_name}",
        "-L", "xil_defaultlib"
    ]
    
    # Run xelab compilation
    result = subprocess.run(compile_cmd, cwd=vivado_dir, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Compilation failed for {tb_name}.")
        return False

    print(f"Running simulation with xsim...")
    if run_gui:
        sim_run_cmd = [xsim_cmd, snapshot, "-gui"]
    else:
        sim_run_cmd = [xsim_cmd, snapshot, "-runall"]
    
    # Run xsim simulation
    result = subprocess.run(sim_run_cmd, cwd=vivado_dir)
    if result.returncode != 0:
        print(f"[ERROR] Simulation failed for {tb_name}.")
        return False
        
    print(f"Simulation of {tb_name} complete.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Vivado Simulation Automation Script")
    parser.add_argument(
        "--tb",
        choices=["green_corridor", "signal_fsm", "all"],
        default="all",
        help="Specify the testbench to simulate (default: all)"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Run simulation in Vivado xsim GUI mode"
    )
    args = parser.parse_args()

    vivado_dir = os.path.dirname(os.path.abspath(__file__))
    vivado_bin = find_vivado_bin()
    
    if vivado_bin is None:
        print("[ERROR] Vivado installation not found in PATH or standard AMDDesignTools/Xilinx folders.")
        print("Please ensure Vivado is installed and 'xelab' / 'xsim' are available.")
        sys.exit(1)

    print(f"Found Vivado binaries at: {vivado_bin if vivado_bin else 'System PATH'}")

    success = True
    if args.tb in ("signal_fsm", "all"):
        success &= compile_and_run(vivado_bin, vivado_dir, "tb_signal_fsm", args.gui)
        
    if args.tb in ("green_corridor", "all"):
        success &= compile_and_run(vivado_bin, vivado_dir, "tb_green_corridor", args.gui)

    if success:
        print("\nAll requested simulations completed successfully.")
        sys.exit(0)
    else:
        print("\n[ERROR] One or more simulations failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
