import math
from ...models import StayPointModel
from ..utils.abs_metric import AbsMetric

class Entropy(AbsMetric):
    def __init__(self):
        pass

    def extract(self):
        total_visits = sum(sp.numVisits for sp in StayPointModel.objects.all())

        if total_visits == 0:  # Avoid division by zero and log(0)
            return

        for sp in StayPointModel.objects.all():
            probability = sp.numVisits / total_visits
            if probability > 0:  # To avoid log(0), which is undefined
                entropy = -probability * math.log2(probability)
                sp.entropy = entropy
                sp.save()
