import logging
from ..utils.abs_metric import AbsMetric


class TravelAverageSpeed(AbsMetric):
    """
    A class to calculate the average speed for each travel segment.

    Attributes:
        travels (pd.DataFrame): A DataFrame containing travel distances and travel times.
    """

    def __init__(self, travels):
        """
        Initialize the TravelAverageSpeed instance.

        Args:
            travels (pd.DataFrame): A DataFrame containing 'travel_distance' and 'travel_time' for each travel segment.
        """
        self.travels = travels

    def extract(self):
        """
        Calculate the average speed for each travel segment by dividing the travel distance by the travel time.

        Returns:
            pd.DataFrame: The original DataFrame with an added column for average speed.
        """
        logging.info("Calculating Travel Average Speed")

        # Ensure the 'average_speed' column is initialized
        self.travels['average_speed'] = 0.0

        # Calculate average speed for each travel segment
        for n in range(len(self.travels)):
            travel_distance = self.travels.iloc[n]['travel_distance']
            travel_time = self.travels.iloc[n]['travel_time']

            # Check for valid travel time and distance
            if travel_time > 0 and travel_distance >= 0:
                average_speed = travel_distance / travel_time
                self.travels.at[n, 'average_speed'] = round(average_speed, 5)
            else:
                logging.warning(f"Invalid data at index {n}: distance={travel_distance}, time={travel_time}")

        logging.info("Travel Average Speed Calculated Successfully")
        return self.travels
