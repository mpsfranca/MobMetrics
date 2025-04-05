from ..utils.abs_metric import AbsMetric
from ..utils.utils import distance


class TotalTravelDistance(AbsMetric):

    def __init__(self, trace):
        self.trace = trace

    def extract(self):
        total_travel_distance = 0

        for prev_row, curr_row in zip(self.trace.iloc[:-1].iterrows(), self.trace.iloc[1:].iterrows()):
            _, prev_row = prev_row
            _, curr_row = curr_row
            total_travel_distance += distance(prev_row, curr_row)

        return round(total_travel_distance, 5)
