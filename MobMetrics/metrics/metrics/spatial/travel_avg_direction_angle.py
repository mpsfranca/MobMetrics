# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric
from ..utils.utils import direction_angle


class TravelAvgDirectionAngle(AbsMetric):
    """
    Class to compute the average direction angle between consecutive points
    in a travel trajectory.
    """

    def __init__(self, trace_file, parameters):
        """
        Initialize the class with the trace data and file name.

        Args:
            trace_file (DataFrame): The trajectory data as a pandas DataFrame.

        """
        self.trace_file = trace_file

        # Assuming this attribute is required by direction_angle
        self.is_geographical_coordinates = parameters[6]

    def extract(self):
        """
        Calculate and return the average direction angle of the travel.

        Returns:
            float: The average direction angle rounded to 5 decimal places.
        """
        angle_sum = 0
        count = 0

        for prev_row, curr_row in zip(self.trace_file.iloc[:-1].iterrows(),
                                       self.trace_file.iloc[1:].iterrows()):
            _, prev_row = prev_row
            _, curr_row = curr_row

            count += 1
            angle_sum += direction_angle(prev_row, curr_row, self.is_geographical_coordinates)

        if count == 0:
            return 0.0  # Prevent division by zero

        return round(angle_sum / count, 5)
