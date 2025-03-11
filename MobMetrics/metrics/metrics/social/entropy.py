import math
import tqdm  # type: ignore

from ...models import StayPointModel, QuadrantEntropyModel
from ..utils.abs_metric import AbsMetric

class Entropy(AbsMetric):
    def __init__(self, name, total_visits, parameters, trace_file):
        self.name = name  # File name associated with the stay points
        self.total_visits = total_visits  # Total number of visits across all stay points for this file
        self.quadrant_size = parameters[3]
        self.trace = trace_file

    def extract(self):
        self.stayPointEntropy()
        self.quadrantEntropy()
        

    def stayPointEntropy(self):
        stay_points = StayPointModel.objects.filter(fileName=self.name)

        for sp in tqdm.tqdm(stay_points, desc="Entropy Metrics"):
            probability = sp.numVisits / self.total_visits
            if probability > 0:  # To avoid log(0), which is undefined
                entropy = -probability * math.log2(probability)
                
                # Update the entropy field in the StayPointModel
                sp.entropy = entropy
                sp.save()
    


    def quadrantEntropy(self):
        # Remove NaN values from the DataFrame
        self.trace.dropna(subset=['x', 'y', 'z'], inplace=True)

        # Determine min and max values for x, y, and z
        min_x, max_x = self.trace['x'].min(), self.trace['x'].max()
        min_y, max_y = self.trace['y'].min(), self.trace['y'].max()
        min_z, max_z = self.trace['z'].min(), self.trace['z'].max()

        # Compute quadrant size based on given multiplier, avoiding division by zero
        delta_x = (max_x - min_x) * self.quadrant_size if max_x > min_x else 1
        delta_y = (max_y - min_y) * self.quadrant_size if max_y > min_y else 1
        delta_z = (max_z - min_z) * self.quadrant_size if max_z > min_z else 1

        # Dictionary to store quadrant visit counts
        quadrant_visits = {}

        # Iterate through trace data and determine quadrant index
        for _, row in self.trace.iterrows():
            qx = int((row['x'] - min_x) / delta_x)
            qy = int((row['y'] - min_y) / delta_y)
            qz = int((row['z'] - min_z) / delta_z)
            quadrant_index = (qx, qy, qz)

            if quadrant_index in quadrant_visits:
                quadrant_visits[quadrant_index] += 1
            else:
                quadrant_visits[quadrant_index] = 1

        # Total visits in all quadrants
        total_visits = sum(quadrant_visits.values())
        
        # Save quadrant entropy values to the database
        for quadrant_index, visit_count in quadrant_visits.items():
            probability = visit_count / total_visits
            entropy = -probability * math.log2(probability) if probability > 0 else 0
            
            # Save to database
            QuadrantEntropyModel.objects.create(
                fileName=self.name,
                x=quadrant_index[0],
                y=quadrant_index[1],
                z=quadrant_index[2],
                entropy=entropy
            )
