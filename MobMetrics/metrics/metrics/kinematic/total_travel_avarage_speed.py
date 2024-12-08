import logging
from ..utils.abs_metric import AbsMetric


class TotalTravelAverageSpeed(AbsMetric):
    """
    A class to calculate the total average speed for a journey.

    Attributes:
        time (float): Total time taken for the journey.
        distance (float): Total distance covered during the journey.
    """

    def __init__(self, time, distance):
        """
        Initialize the TotalTravelAverageSpeed instance.

        Args:
            time (float): Total time taken for the journey.
            distance (float): Total distance covered during the journey.
        """
        self.time = time
        self.distance = distance

    def extract(self):
        """
        Calculate the total average speed by dividing the total distance by the total time.

        Returns:
            float: The total average speed, rounded to 5 decimal places.

        Raises:
            ValueError: If time is zero or negative, which is invalid for calculating speed.
        """
        logging.info("Calculating Total Travel Average Speed")

        # Check for invalid time
        if self.time <= 0:
            logging.error("Time is zero or negative, which is invalid for speed calculation.")
            raise ValueError("Time must be greater than zero.")

        # Calculate average speed
        average_speed = self.distance / self.time
        logging.info("Total Travel Average Speed Calculated Successfully")

        return round(average_speed, 5)
