import numpy as np

def getspace(psource, xy):
    # Ensure xy is a 1D array
    xy = np.asarray(xy)
    
    # Extract coordinates and parameters
    xys = psource[:, :2]
    d1 = psource[:, 2]
    D = psource[:, 3]
    xc = psource[:, 4]

    # Calculate distances
    distances = np.linalg.norm(xy - xys, axis=1)

    # Compute dpi values
    within_radius = distances <= xc
    dpi = np.where(within_radius, d1, d1 * np.exp(np.abs((distances - xc) / (D - xc)) * np.log(2)))

    # Return the minimum value of dpi array
    return np.min(dpi)
