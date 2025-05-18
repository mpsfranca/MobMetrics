# Standard library imports.
from math import sqrt

# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric
from ...models import MetricsModel, GlobalMetricsModel


class SpeedVariationCoefficient:
    """
    Computes the speed variation coefficient for a given file and stores it in the GlobalMetricsModel.
    """

    def __init__(self, file_name):
        """
        Initialize the SpeedVariationCoefficient class with a file name.

        Args:
            file_name (str): The name of the file to be used in metric calculations.
        """
        self.file_name = file_name

    def extract(self):
        """
        Extracts the speed variation coefficient and saves it to the GlobalMetricsModel.
        """
        metric_global = GlobalMetricsModel.objects.filter(file_name=self.file_name).first()

        if not metric_global:
            return  # or raise an exception

        avg_speed = metric_global.avg_travel_avg_speed

        if avg_speed == 0:
            metric_global.speed_variation_coefficient = 0
        else:
            std_dev = self._standard_deviation(avg_speed)
            variation = round(std_dev / avg_speed, 5)
            metric_global.speed_variation_coefficient = variation

        metric_global.save()

    def _standard_deviation(self, avg_speed):
        """
        Calculates the standard deviation of travel average speeds.

        Args:
            avg_speed (float): The average speed across all travels.

        Returns:
            float: The standard deviation of travel speeds.
        """
        metrics = MetricsModel.objects.filter(file_name=self.file_name)

        squared_diffs = 0
        count = 0

        for metric in metrics:
            squared_diffs += (metric.travel_avg_speed - avg_speed) ** 2
            count += 1

        if count == 0:
            return 0

        return sqrt(squared_diffs / count)
