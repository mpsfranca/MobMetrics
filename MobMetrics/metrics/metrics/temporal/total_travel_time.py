import logging
from ..utils.abs_metric import AbsMetric


class TotalTravelTime(AbsMetric):
    """
    A class to calculate the total travel time from a given trace.

    Attributes:
        trace (pd.DataFrame): A DataFrame containing the trace with a 'time' column.
    """

    def __init__(self, trace):
        """
        Initialize the TotalTravelTime instance.

        Args:
            trace (pd.DataFrame): A DataFrame containing the trace with a 'time' column.
        """
        self.trace = trace

    def extract(self):
        """
        Calculate the total travel time from the trace.

        Returns:
            float: The total travel time in the same units as the 'time' column.
        """

        start_time = self.trace.iloc[0]['time']
        end_time = self.trace.iloc[-1]['time']

        total_travel_time = end_time - start_time
        
        return total_travel_time
