# Standard library imports.
from math import sqrt

# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric
from ..utils.utils import direction_angle


class AngleVariationCoefficient(AbsMetric):
    """
    Class to calculate the coefficient of variation of directional angles between
    consecutive points in a trace file.
    """

    def __init__(self, trace_file, avg_angle, parameters):
        """
        Initialize the class with required data.

        Args:
            trace_file (DataFrame): The trajectory data as a pandas DataFrame.
            file_name (str): The name of the associated file.
            avg_angle (float): The average direction angle for the trace.
        """
        self.trace_file = trace_file
        self.avg_angle = avg_angle
        self.is_geographical_coordinates = parameters[6]

    def extract(self):
        """
        Calculate and return the angle variation coefficient.

        Returns:
            float: Coefficient of variation of directional angles.
        """
        standard_deviation = self._standard_deviation()
        if self.avg_angle == 0:
            return 0.0  # Prevent division by zero
        
        return standard_deviation / self.avg_angle

    def _standard_deviation(self):
        """
        Compute the standard deviation of direction angles.

        Returns:
            float: Standard deviation of angles between consecutive points.
        """
        sum_squared_diffs = 0
        count = 0

        for prev_row, curr_row in zip(self.trace_file.iloc[:-1].iterrows(),
                                       self.trace_file.iloc[1:].iterrows()):
            _, prev_row = prev_row
            _, curr_row = curr_row

            count += 1
            angle = direction_angle(prev_row, curr_row, self.is_geographical_coordinates)
            sum_squared_diffs += (angle - self.avg_angle) ** 2

        if count == 0:
            return 0.0  # Prevent division by zero
        return sqrt(sum_squared_diffs / count)
