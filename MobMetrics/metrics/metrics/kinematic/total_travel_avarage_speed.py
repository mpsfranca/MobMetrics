import logging
from ..utils.abs_metric import AbsMetric


class TotalTravelAverageSpeed(AbsMetric):

    def __init__(self, time, distance):
        self.time = time
        self.distance = distance

    def extract(self):
        if self.time != 0.0:
            average_speed = self.distance / self.time
        else:
            average_speed = 0

        return round(average_speed, 5)
