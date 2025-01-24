import math
import tqdm

from ...models import StayPointModel
from ..utils.abs_metric import AbsMetric

class Entropy(AbsMetric):
    def __init__(self, name, total_visits):
        self.name = name  # File name associated with the stay points
        self.total_visits = total_visits  # Total number of visits across all stay points for this file

    def extract(self):
        """
        Calculate entropy for all stay points associated with the specified file.
        Updates the `entropy` field in the StayPointModel.
        """
        if self.total_visits == 0:  # Avoid division by zero
            return

        for sp in tqdm.tqdm(StayPointModel.objects.filter(fileName=self.name), desc="Entropy Metrics"):
            probability = sp.numVisits / self.total_visits
            if probability > 0:  # To avoid log(0), which is undefined
                entropy = -probability * math.log2(probability)
                
                # Update the entropy field in the StayPointModel
                sp.entropy = entropy
                sp.save()