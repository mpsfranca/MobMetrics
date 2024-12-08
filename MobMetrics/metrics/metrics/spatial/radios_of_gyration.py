import logging
from math import sqrt
import pandas as pd

from ..utils.abs_metric import AbsMetric

class RadiusOfGyration(AbsMetric):
    """
    A class to calculate the Radius of Gyration for a set of points in a trace.

    Attributes:
        trace (pd.DataFrame): A DataFrame containing the trace with 'x', 'y', and 'z' coordinates.
        center_of_mass (tuple): A tuple containing the coordinates of the center of mass (x, y, z).
    """

    def __init__(self, trace, center_of_mass):
        """
        Initialize the RadiusOfGyration instance.

        Args:
            trace (pd.DataFrame): A DataFrame containing the trace with 'x', 'y', and 'z' coordinates.
            center_of_mass (tuple): A tuple containing the coordinates of the center of mass (x, y, z).
        """
        self.trace = trace
        self.center_of_mass = center_of_mass

    def extract(self):
        """
        Calculate the Radius of Gyration for the trace based on the center of mass.

        Returns:
            float: The calculated radius of gyration, rounded to 5 decimal places.
        """
        logging.info("Calculating Radius of Gyration")

        if self.trace.empty:
            logging.warning("Trace is empty. Radius of Gyration is 0.")
            return 0

        radius_of_gyration = 0

        for _, row in self.trace.iterrows():
            # Calculate squared distances from the center of mass
            x = (row['x'] - self.center_of_mass[0]) ** 2
            y = (row['y'] - self.center_of_mass[1]) ** 2
            z = (row['z'] - self.center_of_mass[2]) ** 2
            radius_of_gyration += x + y + z

        # Compute the final radius of gyration
        radius_of_gyration = sqrt(radius_of_gyration / len(self.trace))

        logging.info("Radius of Gyration Calculated Successfully")

        return round(radius_of_gyration, 5)
