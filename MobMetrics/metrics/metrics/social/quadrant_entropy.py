# Standard library imports.
from math import log2

# Local application/library specific imports.
from ...models import QuadrantEntropyModel, GlobalMetricsModel, MetricsModel
from ..utils.abs_metric import AbsMetric


class QuadrantEntropy(AbsMetric):
    """
    Class to compute quadrant-based entropy of spatial traces.
    This metric evaluates how spread out visits are in a 2D space partitioned into quadrants.

    Attributes:
        trace (pd.DataFrame): Data containing spatial coordinates and entity IDs.
        parameters (list): Configuration parameters for processing.
        quadrant_size (int): Number of divisions along each axis to form quadrants.
    """

    def __init__(self, trace, parameters):
        """
        Initialize the QuadrantEntropy class.

        Args:
            trace (pd.DataFrame): DataFrame containing 'x', 'y', and 'id' columns.
            parameters (list): List of parameters, where index 3 is the quadrant size.
        """
        self.trace = trace
        self.parameters = parameters
        self.quadrant_size = parameters[3]

    def extract(self):
        """
        Extract both total and per-entity quadrant entropy metrics.
        """
        self._total_quadrant_entropy()
        self._entity_quadrant_entropy()

    def _total_quadrant_entropy(self):
        """
        Compute total entropy over all points in the trace using spatial quadrants.
        Save results to the QuadrantEntropyModel and update the GlobalMetricsModel.
        """
        min_x, max_x = self.trace['x'].min(), self.trace['x'].max()
        min_y, max_y = self.trace['y'].min(), self.trace['y'].max()

        delta_x = (max_x - min_x) / self.quadrant_size
        delta_y = (max_y - min_y) / self.quadrant_size

        quadrant_visits = {}

        for _, row in self.trace.iterrows():
            qx = int((row['x'] - min_x) / delta_x)
            qy = int((row['y'] - min_y) / delta_y)
            quadrant_index = (qx, qy)
            quadrant_visits[quadrant_index] = quadrant_visits.get(quadrant_index, 0) + 1

        total_visits = sum(quadrant_visits.values())
        occupied_quadrants = len(quadrant_visits)

        for quadrant_index, visit_count in quadrant_visits.items():
            probability = visit_count / total_visits
            entropy = -probability * log2(probability)

            QuadrantEntropyModel.objects.create(
                file_name=self.parameters[4],
                x=quadrant_index[0],
                y=quadrant_index[1],
                visit_count=visit_count,
                entropy=entropy,
                entity_id=None,
                spatial_cover=occupied_quadrants
            )

        global_metric = GlobalMetricsModel.objects.get(file_name=self.parameters[4])
        global_metric.total_spatial_cover = occupied_quadrants
        global_metric.save()

    def _entity_quadrant_entropy(self):
        """
        Compute entropy per entity using quadrant-based partitioning.
        Save results to the QuadrantEntropyModel and update the MetricsModel.
        """
        min_x, max_x = self.trace['x'].min(), self.trace['x'].max()
        min_y, max_y = self.trace['y'].min(), self.trace['y'].max()

        delta_x = (max_x - min_x) / self.quadrant_size
        delta_y = (max_y - min_y) / self.quadrant_size

        grouped = self.trace.groupby('id')

        for entity_id, group in grouped:
            quadrant_visits = {}

            for _, row in group.iterrows():
                qx = int((row['x'] - min_x) / delta_x)
                qy = int((row['y'] - min_y) / delta_y)
                quadrant_index = (qx, qy)
                quadrant_visits[quadrant_index] = quadrant_visits.get(quadrant_index, 0) + 1

            total_visits = sum(quadrant_visits.values())
            occupied_quadrants = len(quadrant_visits)

            for quadrant_index, visit_count in quadrant_visits.items():
                probability = visit_count / total_visits
                entropy = -probability * log2(probability)

                QuadrantEntropyModel.objects.create(
                    file_name=self.parameters[4],
                    x=quadrant_index[0],
                    y=quadrant_index[1],
                    visit_count=visit_count,
                    entropy=entropy,
                    entity_id=entity_id,
                    spatial_cover=occupied_quadrants
                )

            metric = MetricsModel.objects.get(file_name=self.parameters[4], entity_id=entity_id)
            metric.spatial_cover = occupied_quadrants
            metric.save()
