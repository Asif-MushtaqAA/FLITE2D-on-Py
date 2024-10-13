import numpy as np
from scipy.spatial import Delaunay, cKDTree
from scipy.interpolate import LinearNDInterpolator
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from multiprocessing import Pool
from shapely.strtree import STRtree

from make_input import make_input
from getspace import getspace
from conelem import conelem
from laplacian_smooth import laplacian_smooth

def plot_mesh(mesh_xy, mesh_connec, airfoil_points, outer_points):
    plt.figure(figsize=(10, 8))
    plt.triplot(mesh_xy[:, 0], mesh_xy[:, 1], mesh_connec, linestyle='-', color='gray', alpha=0.6)
    plt.plot(airfoil_points[:, 0], airfoil_points[:, 1], 'ro', markersize=5, label='Airfoil Points')
    plt.plot(outer_points[:, 0], outer_points[:, 1], 'bo', markersize=5, label='Outer Points')
    
    plt.xlim(-0.2, 1.5)
    plt.ylim(-0.5, 0.5)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.title('Mesh Visualization')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

def plot_mesh_full(mesh_xy, mesh_connec, airfoil_points, outer_points):
    plt.figure(figsize=(10, 8))
    plt.triplot(mesh_xy[:, 0], mesh_xy[:, 1], mesh_connec, linestyle='-', color='gray', alpha=0.6)
    plt.plot(airfoil_points[:, 0], airfoil_points[:, 1], 'ro', markersize=5, label='Airfoil Points')
    plt.plot(outer_points[:, 0], outer_points[:, 1], 'bo', markersize=5, label='Outer Points')
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.title('Mesh Visualization')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

def in_out_status(tri, points, outer_boundary, inner_boundary):
    """
    Determines which simplices in `tri` are inside the `outer_boundary` and outside the `inner_boundary`.

    Parameters:
    tri (Delaunay): Delaunay triangulation object.
    points (np.ndarray): Coordinates of the points.
    outer_boundary (np.ndarray): Coordinates of the outer boundary polygon.
    inner_boundary (np.ndarray): Coordinates of the inner boundary polygon.

    Returns:
    list: Boolean list indicating which simplices are inside the outer boundary and outside the inner boundary.
    """
    # Create polygons
    outer_polygon = Polygon(outer_boundary)
    inner_polygon = Polygon(inner_boundary)

    # Create R-trees for faster spatial querying
    outer_tree = STRtree([outer_polygon])
    inner_tree = STRtree([inner_polygon])

    # Prepare results list
    in_status = []

    for simplex in tri.simplices:
        # Compute the centroid of the simplex
        center = np.mean(points[simplex], axis=0)
        point = Point(center)

        # Check if the point is within the outer polygon and not within the inner polygon
        is_in_outer = outer_tree.query(point, predicate='intersects')
        is_in_inner = inner_tree.query(point, predicate='intersects')

        # Append result
        in_status.append(len(is_in_outer) > 0 and len(is_in_inner) == 0)

    return in_status

def adjust_indices(connec):
    return connec + 1

def compute_distances(xx, xy, tree):
    distances, _ = tree.query(xx, k=3)
    return distances.min(axis=1)

def process_mesh_iteration(mesh_data):
    mesh_xy, mesh_connec, psource, alpha, spacing_interpolator, tree = mesh_data
    ip = len(mesh_xy)
    oldnp = ip
    flag1 = False

    new_points = []

    for ie in range(len(mesh_connec)):
        x1, y1 = mesh_xy[mesh_connec[ie, 0]]
        x2, y2 = mesh_xy[mesh_connec[ie, 1]]
        x3, y3 = mesh_xy[mesh_connec[ie, 2]]
        xx = np.array([(x1 + x2 + x3) / 3, (y1 + y2 + y3) / 3])

        distances = compute_distances([xx], mesh_xy, tree)
        si = distances.min()

        if ip - oldnp > 0:
            new_points = mesh_xy[oldnp:]
            distances = np.linalg.norm(xx - new_points, axis=1)
            si = min(si, distances.min())

        is_spacing = spacing_interpolator(xx[0], xx[1]) if psource is None else min(spacing_interpolator(xx[0], xx[1]), getspace(psource, xx))
        ds = si - is_spacing

        if ds >= -alpha * si:
            new_points.append(xx)
            flag1 = True

    if flag1:
        mesh_xy = np.vstack([mesh_xy] + new_points)
        tree = cKDTree(mesh_xy)

    return mesh_xy, tree, flag1

def mesh_gen(xy, bound_data, alpha, psource):
    input_data = make_input(xy, bound_data)
    no_bound = len(bound_data)
    outerprofile = input_data[174:no_bound, :2]
    innerprofile = input_data[0:174, :2]
    profile = input_data[0:no_bound, :2]

    mesh = {'xy': input_data[:no_bound, :2]}
    dt = Delaunay(profile)
    inside = in_out_status(dt, profile, outerprofile, innerprofile)
    mesh['connec'] = dt.simplices[inside]

    spacing_interpolator = LinearNDInterpolator(input_data[:, :2], input_data[:, 2])
    max_elements = 30000
    flag = True

    tree = cKDTree(mesh['xy'])

    # Convergence parameters
    convergence_threshold = 0.02  # 2% change threshold
    previous_num_elements = len(mesh['connec'])

    while flag:
        mesh_data = (mesh['xy'], mesh['connec'], psource, alpha, spacing_interpolator, tree)
        with Pool() as pool:
            mesh['xy'], tree, flag1 = pool.apply(process_mesh_iteration, (mesh_data,))

        dt = Delaunay(mesh['xy'])
        inside = in_out_status(dt, mesh['xy'], outerprofile, innerprofile)
        mesh['connec'] = dt.simplices[inside]

        if len(mesh['connec']) > max_elements:
            print("Max elements reached. Exiting loop.")
            break

        mesh = conelem(mesh)
        mesh = laplacian_smooth(mesh, bound_data, 1, 1.0)

        dt = Delaunay(mesh['xy'])
        inside = in_out_status(dt, mesh['xy'], outerprofile, innerprofile)
        mesh['connec'] = dt.simplices[inside]
        mesh = conelem(mesh)

        current_num_elements = len(mesh['connec'])
        change_ratio = abs(current_num_elements - previous_num_elements) / previous_num_elements

        if change_ratio < convergence_threshold:
            print(f"Change ratio {change_ratio:.4f} below threshold. Exiting loop.")
            break

        previous_num_elements = current_num_elements

        print("Number of elements:", len(mesh['connec']))

    print('Outside of loop now')
    dt = Delaunay(mesh['xy'])
    inside = in_out_status(dt, mesh['xy'], outerprofile, innerprofile)
    mesh['connec'] = dt.simplices[inside]
    mesh = conelem(mesh)
    mesh = laplacian_smooth(mesh, bound_data, 5, 0.75)

    plot_mesh(mesh['xy'], mesh['connec'], innerprofile, outerprofile)
    plot_mesh_full(mesh['xy'], mesh['connec'], innerprofile, outerprofile)

    mesh['connec'] = adjust_indices(mesh['connec'])
    return mesh
