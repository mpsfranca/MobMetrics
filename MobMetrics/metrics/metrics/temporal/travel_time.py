import logging
import pandas as pd


class TravelTime:
    """
    A class to calculate travel times between stay points and other points in the trace.

    Attributes:
        stay_points (pd.DataFrame): DataFrame of stay points with arrival and departure times.
        first_point (pd.DataFrame): DataFrame containing the first trace point.
        last_point (pd.DataFrame): DataFrame containing the last trace point.
    """

    def __init__(self, stay_points, first_point, last_point):
        self.travel_times = []
        self.stay_points = stay_points
        self.first_point = first_point
        self.last_point = last_point

    def extract(self):
        """
        Calculate travel times and return a DataFrame with the results.

        Returns:
            pd.DataFrame: DataFrame with travel times between stay points, including columns:
                          ['arvId', 'levId', 'travel_time'].
        """
        logging.info('Calculating Travel Time')

        if self.stay_points.empty:
            return pd.DataFrame([], columns=['arvId', 'levId', 'travel_time'])

        # Travel time from the first point to the first stay point
        self._calculate_travel_time(self.first_point.iloc[0]['time'], self.stay_points.iloc[0]['arvT'], 0, self.stay_points.iloc[0]['spId'])

        # Travel times between consecutive stay points
        for i in range(1, len(self.stay_points)):
            self._calculate_travel_time(
                self.stay_points.iloc[i - 1]['levT'],
                self.stay_points.iloc[i]['arvT'],
                self.stay_points.iloc[i - 1]['spId'],
                self.stay_points.iloc[i]['spId']
            )

        # Travel time from the last stay point to the last point
        self._calculate_travel_time(self.stay_points.iloc[-1]['levT'], self.last_point.iloc[0]['time'], self.stay_points.iloc[-1]['spId'], 0)

        logging.info('Travel Time Calculated Successfully')
        return pd.DataFrame(self.travel_times)

    def _calculate_travel_time(self, start_time, end_time, arv_id, lev_id):
        """
        Calculate and add a travel time entry if the travel time is valid.

        Args:
            start_time (float): Start time of the travel.
            end_time (float): End time of the travel.
            arv_id (int): Arrival ID.
            lev_id (int): Departure ID.
        """
        if end_time > start_time:
            travel_time = end_time - start_time
            self.travel_times.append({
                'arvId': arv_id,
                'levId': lev_id,
                'travel_time': travel_time
            })
