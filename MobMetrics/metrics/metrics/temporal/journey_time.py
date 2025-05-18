# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric


class JourneyTime(AbsMetric):
    """
    Computes the duration of a journey based on arrival and departure timestamps.
    """

    def __init__(self, arrival_time, departure_time):
        """
        Initializes the JourneyTime metric.

        Args:
            arrival_time (datetime): The time when the journey ended.
            departure_time (datetime): The time when the journey started.
        """
        self.arrival_time = arrival_time
        self.departure_time = departure_time

    def extract(self):
        """
        Calculates the journey duration.

        Returns:
            timedelta or int: Duration as a timedelta object if arrival_time > departure_time,
                              otherwise returns 0.
        """
        return (
            self.arrival_time - self.departure_time
            if self.arrival_time > self.departure_time
            else 0
        )
