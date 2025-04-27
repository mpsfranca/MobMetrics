import math
import tqdm

from ...models import StayPointModel, QuadrantEntropyModel
from ..utils.abs_metric import AbsMetric

class Entropy(AbsMetric):
    def __init__(self, total_visits, parameters, trace_file): 
        self.total_visits = total_visits 
        self.trace = trace_file
        self.parameters = parameters

    def extract(self):
        self.stayPointEntropy()

    def stayPointEntropy(self):
        stay_points = StayPointModel.objects.filter(fileName=self.parameters[4])

        for sp in tqdm.tqdm(stay_points, desc="Stay Point Entropy"):
            probability = sp.numVisits / self.total_visits
            if probability > 0:
                entropy = -probability * math.log2(probability)
                
                sp.entropy = entropy
                sp.save()
