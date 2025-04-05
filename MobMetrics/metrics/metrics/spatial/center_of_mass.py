import logging
from ..utils.abs_metric import AbsMetric


class CenterOfMass(AbsMetric):

    def __init__(self, trace):
        self.trace = trace

    def extract(self):
        x, y, z = 0, 0, 0

        for _, row in self.trace.iterrows():
            x += row['x']
            y += row['y']
            z += row['z']

        num_points = len(self.trace)
        
        x_center = x / num_points
        y_center = y / num_points
        z_center = z / num_points

        return round(x_center, 5), round(y_center, 5), round(z_center, 5)
