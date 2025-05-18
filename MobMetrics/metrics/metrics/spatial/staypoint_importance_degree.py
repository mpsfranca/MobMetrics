# Related third party imports.
import tqdm

# Local application/library specific imports.
from ...models import StayPointModel
from ..utils.abs_metric import AbsMetric


class StaypointImportanceDegree(AbsMetric):
    """
    A metric class to calculate the importance degree of stay points based on:
    - Number of visits
    - Total visit time
    - Entropy

    Attributes:
        parameters (list): Configuration parameters for processing.
    """

    def __init__(self, parameters):
        """
        Initialize the StaypointImportanceDegree class.

        Args:
            parameters (list): A list of configuration parameters where index 4 is expected to be the file name.
        """
        self.parameters = parameters

    def extract(self):
        """
        Entry point to extract the metric by computing the importance degree.
        """
        self._compute_importance_degree()

    def _normalize(self, value, min_val, max_val):
        """
        Normalize a given value within a specified range.

        Args:
            value (float): Value to be normalized.
            min_val (float): Minimum value in the dataset.
            max_val (float): Maximum value in the dataset.

        Returns:
            float: Normalized value between 0 and 1. Returns 0 if min_val == max_val.
        """
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val)

    def _compute_importance_degree(self):
        """
        Compute the importance degree for each stay point based on normalized values
        of visit count, total visit time, and entropy.
        """
        stay_points = StayPointModel.objects.filter(file_name=self.parameters[4])

        visits_list = [sp.num_visits for sp in stay_points]
        visit_time_list = [sp.total_visits_time for sp in stay_points]
        entropy_list = [sp.entropy for sp in stay_points]

        min_visits, max_visits = min(visits_list), max(visits_list)
        min_time, max_time = min(visit_time_list), max(visit_time_list)
        min_entropy, max_entropy = min(entropy_list), max(entropy_list)

        # Weights for the importance calculation
        alpha, beta, gamma = 0.4, 0.4, 0.2

        for sp in tqdm.tqdm(stay_points, desc="Stay Point Importance Degree"):
            norm_visits = self._normalize(sp.num_visits, min_visits, max_visits)
            norm_time = self._normalize(sp.total_visits_time, min_time, max_time)
            norm_entropy = self._normalize(sp.entropy, min_entropy, max_entropy)

            importance = (
                alpha * norm_visits +
                beta * norm_time +
                gamma * (1 - norm_entropy)
            )

            sp.importance_degree = importance
            sp.save()
