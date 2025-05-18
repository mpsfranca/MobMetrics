# Standard library imports.
from math import sqrt

# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric
from ...models import MetricsModel, VisitModel


class VisitTimeVariationCoefficient(AbsMetric):
    """
    Class to compute the coefficient of variation of visit times for a given file.
    Inherits from AbsMetric.
    """

    def __init__(self, file_name):
        """
        Initialize the class with the provided file name.

        Args:
            file_name (str): The name of the file to process.
        """
        self.file_name = file_name

    def extract(self):
        """
        Extract and compute the visit time variation coefficient for each metric entry
        associated with the file name. The coefficient is calculated as the standard 
        deviation of visit durations divided by the average visit time.
        """
        metrics = MetricsModel.objects.filter(file_name=self.file_name)

        for metric in metrics:
            metric_id = metric.entity_id
            metric_avg_time_visit = metric.avg_time_visit

            visits = VisitModel.objects.filter(
                file_name=self.file_name,
                entity_id=metric_id
            )

            deviation_sum = 0
            num_visits = 0

            for visit in visits:
                num_visits += 1
                deviation_sum += (visit.visit_time - metric_avg_time_visit) ** 2

            if num_visits > 0 and metric_avg_time_visit != 0:
                standard_deviation = sqrt(deviation_sum / num_visits)
                visit_time_variation_coefficient = standard_deviation / metric_avg_time_visit
                metric.visit_time_variation_coefficient = visit_time_variation_coefficient
