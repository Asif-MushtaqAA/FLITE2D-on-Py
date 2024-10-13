import numpy as np
import os

def save_mesh(mesh, filename, bound_data):
    """
    Save mesh data to a file in a format compatible with the FLITE preprocessor.

    Parameters:
    mesh (dict): Dictionary containing 'connec' and 'xy' arrays.
    filename (str): Path to the output file.
    bound_data (numpy.ndarray): Array containing the boundary data.
    """
    # Delete the file if it exists
    if os.path.exists(filename):
        os.remove(filename)

    # Open file for writing
    with open(filename, 'w') as f:
        # Header
        H = 1
        f.write(f"{H}\n")

        hdr = 'title'
        f.write(f"{hdr}\n")

        ne = len(mesh['connec'])
        np_ = len(mesh['xy'])
        nb = len(bound_data)

        hdr = 'ne\tnp\tnb'
        f.write(f"{hdr}\n")
        f.write(f"{ne}\t{np_}\t{nb}\n")

        hdr = 'connectivities'
        f.write(f"{hdr}\n")

        # Connectivities
        H = np.zeros((ne, 5), dtype=int)
        H[:, 0] = np.arange(1, ne + 1)
        H[:, 1:4] = mesh['connec'][:, :3]
        H[:, 4] = 1
        np.savetxt(f, H, fmt='%11d', delimiter='\t')

        hdr = 'coordinates'
        f.write(f"{hdr}\n")

        # Coordinates
        I = np.zeros((np_, 3), dtype=float)
        I[:, 0] = np.arange(1, np_ + 1)
        I[:, 1:3] = mesh['xy'][:, :2]
        np.savetxt(f, I, fmt='%11d %11.6f %11.6f', delimiter='\t')

        hdr = 'boundaries'
        f.write(f"{hdr}\n")

        # Boundaries
        np.savetxt(f, bound_data, fmt='%11d', delimiter='\t')
