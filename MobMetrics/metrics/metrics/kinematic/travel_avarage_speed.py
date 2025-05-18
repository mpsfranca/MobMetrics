# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric


class TravelAverageSpeed(AbsMetric):
    """
    Class responsible for calculating the average speed of the  travel.

    Attributes:
        time (float):  travel time.
        distance (float):  travel distance.
    """

    def __init__(self, time, distance):
        """
        Initialize the TravelAverageSpeed class.

        Args:
            time (float):  time taken for the travel.
            distance (float):  distance covered during the travel.
        """
        self.time = time
        self.distance = distance

    def extract(self):
        """
        Calculate the average speed of the entire travel.

        Returns:
            float: The average speed rounded to 5 decimal places. Returns 0 if time is zero.
        """
        if self.time != 0.0:
            average_speed = self.distance / self.time
        else:
            average_speed = 0

        return round(average_speed, 5)
