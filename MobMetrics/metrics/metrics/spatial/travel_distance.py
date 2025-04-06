from ..utils.abs_metric import AbsMetric
from ..utils.utils import distance

class TravelDistance(AbsMetric):
    def __init__(self, traces, parameters):
        self.traces = traces
        self.is_geographical_coordinates = parameters[6]

    def extract(self):
        distancia_total = 0

        if len(self.traces) < 2:
            return distancia_total

        previous_trace = self.traces.iloc[0]

        for i in range(1, len(self.traces)):
            current_trace = self.traces.iloc[i]

            first_point = {'x': previous_trace['x'], 'y': previous_trace['y'], 'z': previous_trace['z']}
            second_point = {'x': current_trace['x'], 'y': current_trace['y'], 'z': current_trace['z']}

            distancia_total += distance(first_point, second_point, self.is_geographical_coordinates)

            previous_trace = current_trace

        return distancia_total
