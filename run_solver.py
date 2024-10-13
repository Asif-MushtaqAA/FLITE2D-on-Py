import os
import subprocess

def run_solver(mach, aoa):
    # Define paths to executable and input files
    solver_exe = r'Solver.exe'
    inp_file = r'runSolver.inp'
    solverinp_file = r'solver.inp'
    
    # Check if the executable exists
    if not os.path.exists(solver_exe):
        raise FileNotFoundError(f"Solver.exe not found at {solver_exe}")

    # Modify input file 'solver.inp' based on mach and aoa
    with open(solverinp_file, 'r') as f:
        solver_input = f.readlines()
    
    # Update Mach number and AoA in the input file
    for line_idx, line in enumerate(solver_input):
        if 'ivd%alpha' in line:
            solver_input[line_idx] = f" ivd%alpha = {aoa},\n"
        elif 'ivd%MachNumber' in line:
            solver_input[line_idx] = f" ivd%MachNumber = {mach},\n"  # Use 2 decimal places for mach

    with open(solverinp_file, 'w') as f:
        f.writelines(solver_input)
    
    # Run Solver.exe
    with subprocess.Popen([solver_exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        # Read inputs from input file and feed them sequentially
        with open(inp_file, 'r') as f:
            for line in f:
                input_value = line.strip()  
                process.stdin.write(input_value + '\n')
                process.stdin.flush()  

        process.stdin.close()

        stdout, stderr = process.communicate()

        # Check if process exited successfully
        if process.returncode != 0:
            print(f"Solver.exe terminated with error: {stderr}") 
        else:
            print("Solver.exe execution completed successfully.")
            print("Output:\n", stdout) 

