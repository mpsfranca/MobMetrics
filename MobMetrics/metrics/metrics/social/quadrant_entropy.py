from math import log2
from ...models import QuadrantEntropyModel, GlobalMetricsModel, MetricsModel
from ..utils.abs_metric import AbsMetric

class QuadrantEntropy(AbsMetric):
    def __init__(self, trace, parameters):
        self.trace = trace
        self.parameters = parameters
        self.quadrantSize = parameters[3]

    def extract(self):
        self.totalQuadrantEntropy()
        self.entityQuadrantEntropy()


    def totalQuadrantEntropy(self):
        min_x, max_x = self.trace['x'].min(), self.trace['x'].max()
        min_y, max_y = self.trace['y'].min(), self.trace['y'].max()

        delta_x = (max_x - min_x) / self.quadrantSize
        delta_y = (max_y - min_y) / self.quadrantSize

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
                fileName=self.parameters[4],
                x=quadrant_index[0],
                y=quadrant_index[1],
                visit_count=visit_count,
                entropy=entropy,
                entity_id=None,  # None para total
                occupied_quadrants=occupied_quadrants
            )

        global_metric = GlobalMetricsModel.objects.get(fileName=self.parameters[4])
        global_metric.occupied_quadrants = occupied_quadrants

        global_metric.save()

    def entityQuadrantEntropy(self):
        min_x, max_x = self.trace['x'].min(), self.trace['x'].max()
        min_y, max_y = self.trace['y'].min(), self.trace['y'].max()

        delta_x = (max_x - min_x) / self.quadrantSize
        delta_y = (max_y - min_y) / self.quadrantSize

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
                    fileName=self.parameters[4],
                    x=quadrant_index[0],
                    y=quadrant_index[1],
                    visit_count=visit_count,
                    entropy=entropy,
                    entity_id=entity_id,
                    occupied_quadrants=occupied_quadrants
                )
            
            metric = MetricsModel.objects.get(fileName=self.parameters[4], entityId = entity_id)
            metric.occupied_quadrants = occupied_quadrants

            metric.save()
