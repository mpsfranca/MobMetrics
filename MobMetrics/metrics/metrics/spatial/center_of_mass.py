import logging
from ..utils.abs_metric import AbsMetric


class CenterOfMass(AbsMetric):
    """
    A class to calculate the center of mass of a set of points in a trace.

    Attributes:
        trace (pd.DataFrame): A DataFrame containing the trace with 'x', 'y', and 'z' coordinates.
    """

    def __init__(self, trace):
        """
        Initialize the CenterOfMass instance.

        Args:
            trace (pd.DataFrame): A DataFrame containing the trace with 'x', 'y', and 'z' coordinates.
        """
        self.trace = trace

    def extract(self):
        """
        Calculate the center of mass for the trace based on the mean of the coordinates.

        Returns:
            tuple: A tuple containing the calculated center of mass coordinates (x_center, y_center, z_center), rounded to 5 decimal places.
        """
        logging.info("Calculating Center of Mass")

        if self.trace.empty:
            logging.warning("Trace is empty. Center of Mass is (0, 0, 0).")
            return 0, 0, 0

        # Initialize sums for the coordinates
        x, y, z = 0, 0, 0

        # Sum the coordinates
        for _, row in self.trace.iterrows():
            x += row['x']
            y += row['y']
            z += row['z']

        # Calculate the average for each coordinate
        num_points = len(self.trace)
        x_center = x / num_points
        y_center = y / num_points
        z_center = z / num_points

        logging.info("Center of Mass Calculated Successfully")

        # Return the coordinates rounded to 5 decimal places
        return round(x_center, 5), round(y_center, 5), round(z_center, 5)
