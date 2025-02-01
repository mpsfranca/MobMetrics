import math
import tqdm  # type: ignore

from ...models import StayPointModel
from ..utils.abs_metric import AbsMetric

class Entropy(AbsMetric):
    def __init__(self, name, total_visits):
        self.name = name  # File name associated with the stay points
        self.total_visits = total_visits  # Total number of visits across all stay points for this file

    def extract(self):
        
        stay_points = StayPointModel.objects.filter(fileName=self.name)

        for sp in tqdm.tqdm(stay_points, desc="Entropy Metrics"):
            probability = sp.numVisits / self.total_visits
            if probability > 0:  # To avoid log(0), which is undefined
                entropy = -probability * math.log2(probability)
                
                # Update the entropy field in the StayPointModel
                sp.entropy = entropy
                sp.save()