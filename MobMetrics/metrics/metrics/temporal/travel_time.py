# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric


class TotalTravelTime(AbsMetric):
    """
    Computes the total travel time of a trace based on the first and last timestamps.
    """

    def __init__(self, trace):
        """
        Initializes the TotalTravelTime metric.

        Args:
            trace (DataFrame): A pandas DataFrame containing at least a 'time' column,
                               sorted chronologically.
        """
        self.trace = trace

    def extract(self):
        """
        Calculates the total time elapsed between the first and last records in the trace.

        Returns:
            timedelta or int: The total travel time duration.
        """
        start_time = self.trace.iloc[0]['time']
        end_time = self.trace.iloc[-1]['time']
        total_travel_time = end_time - start_time

        return total_travel_time
