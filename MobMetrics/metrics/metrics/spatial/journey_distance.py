# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric
from ..utils.utils import distance


class JourneyDistance(AbsMetric):
    """
    A metric class to calculate the total distance of a journey based on 
    a sequence of trace points.

    Attributes:
        traces (pd.DataFrame): The input sequence of traces, each representing a point.
        is_geographical_coordinates (bool): Flag indicating if coordinates are geographical.
    """

    def __init__(self, traces, parameters):
        """
        Initialize the JourneyDistance class.

        Args:
            traces (pd.DataFrame): The sequential traces of a journey.
            parameters (list): A list of parameters where the 7th element (index 6)
                               indicates if the coordinates are geographical.
        """
        self.traces = traces
        self.is_geographical_coordinates = parameters[6]

    def extract(self):
        """
        Calculate the total distance between the sequential trace points.

        Returns:
            float: The total journey distance.
        """
        total_distance = 0.0

        if len(self.traces) < 2:
            return total_distance

        previous_trace = self.traces.iloc[0]

        for i in range(1, len(self.traces)):
            current_trace = self.traces.iloc[i]

            first_point = {
                'x': previous_trace['x'],
                'y': previous_trace['y'],
                'z': previous_trace['z']
            }
            second_point = {
                'x': current_trace['x'],
                'y': current_trace['y'],
                'z': current_trace['z']
            }

            total_distance += distance(first_point, second_point, self.is_geographical_coordinates)
            previous_trace = current_trace

        return total_distance
