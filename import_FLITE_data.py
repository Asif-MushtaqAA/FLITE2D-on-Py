import numpy as np
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation

def import_FLITE_data(rsdname, resname, mesh):
    """
    Imports data output by the FLITE 2D solver and preprocessor, and creates various plots.

    Parameters:
    rsdname (str): Path to the residual data file.
    resname (str): Path to the results data file.
    mesh (dict): Dictionary containing mesh data with keys 'connec' (connectivity) and 'xy' (coordinates).

    Returns:
    results (np.ndarray): The results data from the FLITE solver.
    residual (np.ndarray): The residual data from the FLITE solver.
    """
    # Import data from text files
    results = np.loadtxt(resname)
    residual = np.loadtxt(rsdname)

    # Plot convergence plot
    plt.figure()
    plt.plot(residual[:, 0], residual[:, 1])
    plt.title('Convergence Plot')
    plt.xlabel('Iteration Number')
    plt.ylabel('log(residual)')
    plt.grid(True)

    # Plot Lift and Drag
    plt.figure()
    plt.plot(residual[:, 0], residual[:, 2], label='Lift')
    plt.plot(residual[:, 0], residual[:, 3], 'r', label='Drag')
    plt.legend()
    plt.xlabel('Iteration Number')
    plt.ylabel('Force coefficient (Force/q)')
    plt.grid(True)

    # Plot Normalized Density
    plt.figure()
    # Create a Triangulation object for 0-based indexing in Python
    tri = Triangulation(mesh['xy'][:, 0], mesh['xy'][:, 1], mesh['connec'] - 1)
    plt.tripcolor(tri, results[:, 1], shading='gouraud', cmap='jet')
    plt.colorbar(label='Normalised Density (rho/rho_{inf})')
    plt.title('Normalised Density (rho/rho_{inf})')
    plt.gca().set_aspect('equal')

    # Plot Normalized Pressure
    plt.figure()
    gamma = 1.4
    T_star = gamma * (results[:, 4] - (results[:, 2]**2 + results[:, 3]**2))
    p_star = ((gamma - 1) / gamma) * results[:, 1] * T_star
    p_norm = 2.0 * p_star
    #plt.xlim(-0.2, 1.5)
    #plt.ylim(-0.5, 0.5)
    plt.tripcolor(tri, p_norm, shading='gouraud', cmap='jet')
    #plt.tripcolor(tri, p_norm, shading='gouraud', cmap='jet', vmin=3, vmax=7)
    plt.colorbar(label='Normalised Pressure (p/q_{inf})')
    plt.title('Normalised Pressure (p/q_{inf})')
    plt.gca().set_aspect('equal')

    # Plot Velocity Vectors
    plt.figure()
    plt.quiver(mesh['xy'][:, 0], mesh['xy'][:, 1], results[:, 2], results[:, 3], scale=0.1)
    plt.title('Velocity Vectors')
    plt.gca().set_aspect('equal')
    plt.grid(True)

    plt.show()

    return results, residual
