import numpy as np
from conelem import conelem
from findlayer import findlayer

def laplacian_smooth(mesh_in, bound_data, NoSweeps, alpha):
    mesh = mesh_in.copy()
    IndVec = np.arange(len(mesh['xy']))
    BoundIndex = np.intersect1d(IndVec, bound_data[:, 0] - 1)
    FreeInd = np.setdiff1d(IndVec, BoundIndex)

    for _ in range(NoSweeps):
        mesh = conelem(mesh)
        new_xy = mesh['xy'].copy()

        for i in FreeInd:
            neighbours = findlayer(mesh, [i])
            if len(neighbours) > 0:
                centroid = np.mean(mesh['xy'][neighbours], axis=0)
                x_c = centroid - mesh['xy'][i]
                new_xy[i] += alpha * x_c
        
        mesh['xy'] = new_xy
    
    return mesh
