import logging
from ..utils.abs_metric import AbsMetric
from ..utils.utils import distance


class TotalTravelDistance(AbsMetric):
    """
    A class to calculate the total travel distance between consecutive points in the trace.

    Attributes:
        trace (pd.DataFrame): A DataFrame containing the trace with coordinates.
    """

    def __init__(self, trace):
        """
        Initialize the TotalTravelDistance instance.

        Args:
            trace (pd.DataFrame): A DataFrame containing the trace with coordinates.
        """
        self.trace = trace

    def extract(self):
        """
        Calculate the total travel distance by summing the distances between consecutive points.

        Returns:
            float: The total travel distance, rounded to 5 decimal places.
        """

        total_travel_distance = 0

        # Calculate the distance between consecutive points
        for prev_row, curr_row in zip(self.trace.iloc[:-1].iterrows(), self.trace.iloc[1:].iterrows()):
            _, prev_row = prev_row
            _, curr_row = curr_row
            total_travel_distance += distance(prev_row, curr_row)

        return round(total_travel_distance, 5)
