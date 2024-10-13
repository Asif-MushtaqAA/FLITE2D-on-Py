# FLITE2DonPy
Python adaptation of FLITE2D CFD framework

A Python-based Delaunay mesh generator is integrated with FLITE2D framework.  
The Python version leverages functionalities like SciPy's cKDTree, Shapely's STRtree, and Polygon, allowing for a vectorised approach to mesh generation and more efficient computations.  
The Python-based Delaunay mesh generator is designed to meet a 2% convergence threshold, which means that when fewer than 2% of the previous iteration's elements are added in subsequent step, the mesh is considered converged.   

The original MATLAB based framework was developed at Swansea University and can be found at @DrBenEvans Github repository.  
Github Repository Link: https://github.com/DrBenEvans/FLITE2D_MATLAB  

Main Script is titled "FLITE2DPY.py".  
