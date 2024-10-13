import numpy as np

def make_input(xy, bound_data):
    """
    Takes coordinates and edge connectivity (bound_data) and produces input data for the mesh generator.

    Parameters:
    xy (numpy.ndarray): Array of shape (n, 2) containing the x and y coordinates.
    bound_data (numpy.ndarray): Array containing the connectivity of boundary data (1-based indexing).

    Returns:
    numpy.ndarray: Input array with x, y coordinates and calculated spacing.
    """
    # Initialize input array with xy coordinates and an extra column for spacing
    input_data = np.zeros((xy.shape[0], 3))
    input_data[:, :2] = xy

    # Loop around edges to find spacing
    for i in range(len(bound_data)):
        point1 = bound_data[i, 0] - 1  # Convert 1-based to 0-based index
        point2 = bound_data[i, 1] - 1  # Convert 1-based to 0-based index
        
        s = np.linalg.norm(xy[point1, :] - xy[point2, :])
        input_data[point1, 2] += s
        input_data[point2, 2] += s

    # Average the spacing values
    input_data[:, 2] /= 2

    return input_data
