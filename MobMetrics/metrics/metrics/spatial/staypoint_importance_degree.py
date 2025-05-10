import tqdm

from ...models import StayPointModel
from ..utils.abs_metric import AbsMetric

class StaypointImportanceDegree(AbsMetric):
    def __init__(self, parameters):
        """
        Class that represents the Stay Point Importance Degree metric. It is calculated based on the total number of
        visits, total visits time and entropy level of each stay point.
        """
        self.parameters = parameters

    def extract(self):
        self.computeImportanceDegree()

    def normalize(self, value, min_val, max_val):
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val)

    def computeImportanceDegree(self):
        stay_points = StayPointModel.objects.filter(fileName=self.parameters[4])

        visits_list = [sp.numVisits for sp in stay_points]
        visit_time_list = [sp.totalVisitsTime for sp in stay_points]
        entropy_list = [sp.entropy for sp in stay_points]

        min_visits, max_visits = min(visits_list), max(visits_list)
        min_time, max_time = min(visit_time_list), max(visit_time_list)
        min_entropy, max_entropy = min(entropy_list), max(entropy_list)

        # Weights
        alpha, beta, gamma = 0.4, 0.4, 0.2

        for sp in tqdm.tqdm(stay_points, desc="Stay Point Importance Degree"):
            norm_visits = self.normalize(sp.numVisits, min_visits, max_visits)
            norm_time = self.normalize(sp.totalVisitsTime, min_time, max_time)
            norm_entropy = self.normalize(sp.entropy, min_entropy, max_entropy)

            importance = (
                alpha * norm_visits +
                beta * norm_time +
                gamma * (1 - norm_entropy)
            )

            sp.importanceDegree = importance
            sp.save()
