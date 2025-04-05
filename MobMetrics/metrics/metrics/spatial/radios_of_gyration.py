from math import sqrt

from ..utils.abs_metric import AbsMetric

class RadiusOfGyration(AbsMetric):

    def __init__(self, trace, center_of_mass):
        self.trace = trace
        self.center_of_mass = center_of_mass

    def extract(self):
        radius_of_gyration = 0

        for _, row in self.trace.iterrows():
            x = (row['x'] - self.center_of_mass[0]) ** 2
            y = (row['y'] - self.center_of_mass[1]) ** 2
            z = (row['z'] - self.center_of_mass[2]) ** 2
            radius_of_gyration += x + y + z

        radius_of_gyration = sqrt(radius_of_gyration / len(self.trace))

        return round(radius_of_gyration, 5)
