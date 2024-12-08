import logging
from ..utils.abs_metric import AbsMetric
from ..utils.utils import distance

class TravelDistance(AbsMetric):
    """
    A class to calculate travel distances between consecutive points in the trace,
    excluding stay points.

    Attributes:
        trace (pd.DataFrame): A DataFrame containing the trace with the points.
        travels (pd.DataFrame): A DataFrame to store the calculated travel distances.
    """

    def __init__(self, trace, travels):
        """
        Initialize the TravelDistance instance.

        Args:
            trace (pd.DataFrame): A DataFrame containing the trace with coordinates and stay points.
            travels (pd.DataFrame): A DataFrame to store the calculated travel distances.
        """
        self.trace = trace
        self.travels = travels

    def extract(self):
        """
        Calculate the travel distance by summing the distances between consecutive
        points, excluding stay points.

        Returns:
            pd.DataFrame: The DataFrame with the calculated travel distances.
        """
        logging.info("Calculating Total Distance")

        # Initialize the travel_distance column
        self.travels['travel_distance'] = 0.0

        # Variables for calculating distance
        travel = 0
        buffer = 0
        block = False

        # Iterate through the trace to calculate the travel distance
        for n in range(len(self.trace) - 1):
            # Check if the current point is not a stay point (stay_point_id == 0)
            if self.trace.iloc[n]['spId'] == 0:
                travel += distance(self.trace.iloc[n], self.trace.iloc[n + 1])
                block = True
            else:
                # When a stay point is encountered, save the total distance for the previous segment
                if block:
                    self.travels.loc[buffer, 'travel_distance'] = round(travel, 5)
                    buffer += 1
                    travel = 0
                    block = False

        # If the last segment wasn't followed by a stay point, we store the travel distance
        if block:
            self.travels.loc[buffer, 'travel_distance'] = round(travel, 5)

        logging.info("Travel Distance Calculated Successfully")
        return self.travels
