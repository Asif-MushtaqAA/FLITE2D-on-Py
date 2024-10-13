import numpy as np
import os
import time
import shutil
from mesh_gen import mesh_gen
from save_mesh import save_mesh
from run_prepro import run_prepro
from run_solver import run_solver
from import_FLITE_data import import_FLITE_data

def move_results_files(coordinates_filename, mach, aoa):
    # Step 5: Move files to Dataset folder
    src_folder = r'E:/SU/Dis/FLITEonPy'
    dataset_folder = r'E:/SU/Dis/FLITEonPy/raw_data'
    airfoil_folder = os.path.join(dataset_folder, os.path.splitext(coordinates_filename)[0], mach, aoa)

    # Create the folder if it does not exist
    os.makedirs(airfoil_folder, exist_ok=True)

    # List of files to move
    files_to_move = [
        'mesh.dat',
        'mesh.sol',
        'solverout.res',
        'solverout.rsd'
    ]

    # Move each file to the destination folder
    for file_name in files_to_move:
        src_path = os.path.join(src_folder, file_name)
        dest_path = os.path.join(airfoil_folder, file_name)
        shutil.move(src_path, dest_path)

    print(f"Files have been moved to {dest_path} successfully.")
    
def read_solver_output_and_compute_cl_cd(alpha, solverout_path = 'solverout.rsd'):
    # Reading the solverout.rsd file
    with open(solverout_path, 'r') as file:
        lines = file.readlines()
    
    # Checking that there are at least two lines
    if len(lines) < 2:
        raise ValueError("The solverout.rsd file does not contain enough data lines.")
    
    # Get the second to last line (last line is empty)
    second_last_line = lines[-1].strip()
    if not second_last_line:
        raise ValueError("The second last line is unexpectedly empty.")
    
    # Split the line into components and extract CY and CX
    parts = second_last_line.split()
    CY = float(parts[2])
    CX = float(parts[3])
    print(f"CY: {CY}, CX: {CX}")
    
    # Compute CL and CD
    # Convert angle of attack from degrees to radians
    alpha_rad = np.radians(alpha)

    # Calculate lift coefficient (CL) and drag coefficient (CD)
    cl = (-CY * np.cos(alpha_rad)) - (CX * np.sin(alpha_rad))
    cd = (-CY * np.sin(alpha_rad)) + (CX * np.cos(alpha_rad))
    print(f"CL: {cl}, CD: {cd}")
    
    return cl, cd
    
def FLITE2DPY(airfoil, mach, aoa, coordinates_path = os.path.join('.', 'data_geometry')):
    # Paths to input data files
    mach = f'{mach:.2f}'
    aoa = f'{aoa:.2f}'
    coordinates_filename = f'{int(airfoil)}.txt'  # This is airfoil number file
    coordinates_filepath = os.path.join(coordinates_path, coordinates_filename)

    # Read coordinates data
    coordinates = np.loadtxt(coordinates_filepath)

    # Read flow field data
    flow_field = np.loadtxt('flow_field.txt')

    # Read bound data
    bound_data = np.loadtxt('bound_data.txt').astype(int)

    # Read psource data
    psource = np.loadtxt('psource.txt')

    # Concatenate coordinates and flow field data
    xy = np.vstack((coordinates, flow_field))

    # Generate the mesh
    start_m= time.time()

    mesh = mesh_gen(xy, bound_data, alpha=0.8, psource=psource)

    end_m = time.time() 
    elapsed = end_m -start_m
    print(f'Time taken for mesh generation: {elapsed:.2f} seconds')

    if mesh is not None:
        save_mesh(mesh, 'mesh.dat', bound_data)
    else:
        print("Mesh generation failed; skipping save.")
        
    # Run preprocessor and Solver
    run_prepro()

    start_s= time.time()

    run_solver(mach, aoa)

    end_s = time.time() 
    elapsed = end_s -start_s
    print(f'Time taken by solver: {elapsed:.2f} seconds')
    
    # Import results using import_FLITE_data function
    results, residual = import_FLITE_data('solverout.rsd', 'solverout.res', mesh) 
    
    aoaf = float(aoa)
    cl, cd = read_solver_output_and_compute_cl_cd(aoaf)
    
    move_results_files(coordinates_filename, mach, aoa) 
    
    return cl, cd
    
#Example Implementation in console
#from FLITE2DPY import FLITE2DPY
#FLITE2DPY(10001,0.5,4)