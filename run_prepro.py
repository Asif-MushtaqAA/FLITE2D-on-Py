import os
import subprocess

# Define paths to executable and input file
prepro_exe = r'PrePro.exe'
input_file = r'runPrePro.inp'

# Check if the executable exists
if not os.path.exists(prepro_exe):
    raise FileNotFoundError(f"PrePro.exe not found at {prepro_exe}")

# Function to run PrePro.exe
def run_prepro():
    # Open PrePro.exe process
    with subprocess.Popen([prepro_exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        # Read inputs from input file and feed them sequentially
        with open(input_file, 'r') as f:
            for line in f:
                input_value = line.strip()  
                process.stdin.write(input_value + '\n')
                process.stdin.flush() 

        process.stdin.close()

        stdout, stderr = process.communicate() 

        # Check if process exited successfully
        if process.returncode != 0:
            print(f"PrePro.exe terminated with error: {stderr}") 
        else:
            print("PrePro.exe execution completed successfully.")
            print("Output:\n", stdout) 

