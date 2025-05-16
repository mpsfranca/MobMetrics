# Standard library imports.
from math import sqrt

# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric


class RadiusOfGyration(AbsMetric):
    """
    A metric class to calculate the radius of gyration of a 3D trace 
    with respect to its center of mass.

    Attributes:
        trace (pd.DataFrame): The input trace data containing 'x', 'y', and 'z' coordinates.
        center_of_mass (tuple): The center of mass as a tuple (x, y, z).
    """

    def __init__(self, trace, center_of_mass):
        """
        Initialize the RadiusOfGyration class.

        Args:
            trace (pd.DataFrame): The trajectory data with spatial coordinates.
            center_of_mass (tuple): The center of mass of the trace (x, y, z).
        """
        self.trace = trace
        self.center_of_mass = center_of_mass

    def extract(self):
        """
        Calculate the radius of gyration based on the provided trace and center of mass.

        Returns:
            float: The radius of gyration rounded to 5 decimal places.
        """
        radius_of_gyration = 0.0

        for _, row in self.trace.iterrows():
            x = (row['x'] - self.center_of_mass[0]) ** 2
            y = (row['y'] - self.center_of_mass[1]) ** 2
            z = (row['z'] - self.center_of_mass[2]) ** 2
            radius_of_gyration += x + y + z

        radius_of_gyration = sqrt(radius_of_gyration / len(self.trace))

        return round(radius_of_gyration, 5)
