# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric
from ..utils.utils import distance


class TravelDistance(AbsMetric):
    """
    A metric class to calculate the travel distance of a trace.

    Attributes:
        trace (pd.DataFrame): The input trace containing spatial coordinates.
        is_geographical_coordinates (bool): Flag indicating if coordinates are geographical.
    """

    def __init__(self, trace, parameters):
        """
        Initialize the TravelDistance class.

        Args:
            trace (pd.DataFrame): The trajectory data.
            parameters (list): A list of parameters where the 7th element (index 6) 
                               indicates if the coordinates are geographical.
        """
        self.trace = trace
        self.is_geographical_coordinates = parameters[6]

    def extract(self):
        """
        Calculate the total travel distance along the trace.

        Returns:
            float: The total travel distance rounded to 5 decimal places.
        """
        travel_distance = 0.0

        for prev_row, curr_row in zip(self.trace.iloc[:-1].iterrows(), self.trace.iloc[1:].iterrows()):
            _, prev_row = prev_row
            _, curr_row = curr_row

            travel_distance += distance(prev_row, curr_row, self.is_geographical_coordinates)

        return round(travel_distance, 5)
