from ..utils.abs_metric import AbsMetric

class TotalTravelTime(AbsMetric):

    def __init__(self, trace):
        self.trace = trace

    def extract(self):
        start_time = self.trace.iloc[0]['time']
        end_time = self.trace.iloc[-1]['time']

        total_travel_time = end_time - start_time
        
        return total_travel_time
