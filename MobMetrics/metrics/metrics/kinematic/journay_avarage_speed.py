# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric


class JourneyAverageSpeed(AbsMetric):
    """
    Class responsible for calculating the average speed of a journey
    given the total distance and total time.

    Attributes:
        distance (float): Total distance of the journey.
        time (float): Total time of the journey.
    """

    def __init__(self, distance, time):
        """
        Initialize the JourneyAverageSpeed class.

        Args:
            distance (float): Total distance covered during the journey.
            time (float): Total time taken during the journey.
        """
        self.distance = distance
        self.time = time

    def extract(self):
        """
        Calculate the average speed as distance divided by time.

        Returns:
            float: Average speed of the journey. Returns 0 if time is zero.
        """
        return self.distance / self.time if self.time > 0 else 0
