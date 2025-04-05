import math
import tqdm  # type: ignore

from ...models import StayPointModel, QuadrantEntropyModel
from ..utils.abs_metric import AbsMetric

class Entropy(AbsMetric):
    def __init__(self, total_visits, parameters, trace_file): 
        self.total_visits = total_visits 
        self.trace = trace_file
        self.parameters = parameters

    def extract(self):
        self.stayPointEntropy()
        self.quadrantEntropy()
        

    def stayPointEntropy(self):
        stay_points = StayPointModel.objects.filter(fileName=self.parameters[4])

        for sp in tqdm.tqdm(stay_points, desc="Stay Point Entropy"):
            probability = sp.numVisits / self.total_visits
            if probability > 0:
                entropy = -probability * math.log2(probability)
                
                sp.entropy = entropy
                sp.save()
    


    def quadrantEntropy(self):

        min_x, max_x = self.trace['x'].min(), self.trace['x'].max()
        min_y, max_y = self.trace['y'].min(), self.trace['y'].max()

        delta_x = (max_x - min_x) / self.parameters[3]
        delta_y = (max_y - min_y) / self.parameters[3]

        quadrant_visits = {}

        for _, row in self.trace.iterrows():
            qx = int((row['x'] - min_x) / delta_x)
            qy = int((row['y'] - min_y) / delta_y)
            quadrant_index = (qx, qy)

            if quadrant_index in quadrant_visits:
                quadrant_visits[quadrant_index] += 1
            else:
                quadrant_visits[quadrant_index] = 1

        total_visits = sum(quadrant_visits.values())
        
        for quadrant_index, visit_count in quadrant_visits.items():
            probability = visit_count / total_visits
            entropy = -probability * math.log2(probability)
            
            QuadrantEntropyModel.objects.create(
                fileName=self.parameters[4],
                x=quadrant_index[0],
                y=quadrant_index[1],
                visit_count = visit_count,
                entropy=entropy
            )
