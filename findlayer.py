import numpy as np

def findlayer(mesh, ilayer1):
    ilayer1 = np.asarray(ilayer1).flatten()
    
    if len(ilayer1) == 0:
        return np.array([], dtype=int)
    
    ilayer1howm = mesh['lhowm'][ilayer1]
    
    # Calculate maximum possible size for the next layer array
    total_elements = np.sum(ilayer1howm) * 3
    ilayerall = np.zeros(total_elements, dtype=int)
    
    k = 0
    
    for node, num_elems in zip(ilayer1, ilayer1howm):
        if node >= len(mesh['lwhere']):
            continue
        
        where = mesh['lwhere'][node]
        
        # Avoid out-of-bounds access
        end = min(where + num_elems, len(mesh['conelem']))
        elems = mesh['conelem'][where:end]
        
        # Collect nodes from connectivity
        elems_nodes = mesh['connec'][elems].flatten()
        if k + len(elems_nodes) > len(ilayerall):
            ilayerall = np.resize(ilayerall, k + len(elems_nodes))
        
        ilayerall[k:k + len(elems_nodes)] = elems_nodes
        k += len(elems_nodes)
    
    ilayerall = ilayerall[:k]
    ilayer = np.unique(np.setdiff1d(ilayerall, ilayer1))
    
    return ilayer
