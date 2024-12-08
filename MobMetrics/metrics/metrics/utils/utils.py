from math import sqrt


def distance(first_point, second_point):
    """
    Calculate the Euclidean distance between two points in 3D space.

    Args:
        first_point (dict): A dictionary with keys 'x', 'y', 'z' representing the coordinates of the first point.
        second_point (dict): A dictionary with keys 'x', 'y', 'z' representing the coordinates of the second point.

    Returns:
        float: The Euclidean distance between the two points.
    """
    return sqrt(
        (second_point['x'] - first_point['x']) ** 2 +
        (second_point['y'] - first_point['y']) ** 2 +
        (second_point['z'] - first_point['z']) ** 2
    )
