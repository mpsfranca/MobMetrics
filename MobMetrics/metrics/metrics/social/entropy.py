# Standard library imports.
import math

# Related third party imports.
import tqdm

# Local application/library specific imports.
from ...models import StayPointModel
from ..utils.abs_metric import AbsMetric


class Entropy(AbsMetric):
    """
    Class that calculates the entropy of each stay point based on the number of visits.

    Attributes:
        total_visits (int): Total number of visits across all stay points.
        trace (Any): Trace file reference (not directly used in this implementation).
        parameters (list): Configuration parameters for processing.
    """

    def __init__(self, total_visits, parameters, trace_file):
        """
        Initialize the Entropy class.

        Args:
            total_visits (int): Total number of visits to all stay points.
            parameters (list): Configuration parameters.
            trace_file (Any): Trace file used (not used in this function, but passed for consistency).
        """
        self.total_visits = total_visits
        self.trace = trace_file
        self.parameters = parameters

    def extract(self):
        """
        Public method that triggers entropy calculation for stay points.
        """
        self._stay_point_entropy()

    def _stay_point_entropy(self):
        """
        Compute entropy for each stay point based on its number of visits.
        The entropy is saved to the respective model instance.
        """
        stay_points = StayPointModel.objects.filter(file_name=self.parameters[4])

        for sp in tqdm.tqdm(stay_points, desc="Stay Point Entropy"):
            probability = sp.num_visits / self.total_visits

            if probability > 0:
                entropy = -probability * math.log2(probability)
                sp.entropy = entropy
                sp.save()
