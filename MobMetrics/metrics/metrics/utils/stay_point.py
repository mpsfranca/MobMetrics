import logging
import pandas as pd

from .utils import distance

class StayPoints:
    def __init__(self, trace, distance_threshold, time_threshold):
 
        self.trace = trace
        self.distance_threshold = distance_threshold
        self.time_threshold = time_threshold

    def extract(self):

        logging.info("Calculating Stay Points")

        stay_points = []
        self.trace['spId'] = 0
        stay_point_id = 1
        exist = True

        m = 0
        while m < len(self.trace):
            if self.trace.iloc[m]['spId'] != 0:
                m += 1
                continue

            arvT = self.trace.iloc[m]['time']
            lat_sum = self.trace.iloc[m]['x']
            lgnt_sum = self.trace.iloc[m]['y']
            alt_sum = self.trace.iloc[m]['z']
            buffer = 1

            i = m + 1
            while i < len(self.trace) and distance(self.trace.iloc[m], self.trace.iloc[i]) <= self.distance_threshold:
                lat_sum += self.trace.iloc[i]['x']
                lgnt_sum += self.trace.iloc[i]['y']
                alt_sum += self.trace.iloc[i]['z']
                buffer += 1
                i += 1

            levT = self.trace.iloc[i - 1]['time']

            if (levT - arvT) >= self.time_threshold:
                
                stay_point = ({
                    'spId': stay_point_id,
                    'x': round((lat_sum / buffer), 5),
                    'y': round((lgnt_sum / buffer), 5),
                    'z': round((alt_sum / buffer), 5),
                    'arvT': arvT,
                    'levT': levT,
                    'visit_time': levT - arvT
                })

                for aux in stay_points:
                    if distance(aux, stay_point) <= self.distance_threshold:
                        stay_point['spId'] = aux['spId']
                        self.trace.iloc[m:i, self.trace.columns.get_loc('spId')] = aux['spId']
                        exist = False
                        break
                
                if exist:
                    exist = True
                    self.trace.iloc[m:i, self.trace.columns.get_loc('spId')] = stay_point_id
                    stay_point_id += 1

                stay_points.append(stay_point)
                

            m = i

        stay_points = pd.DataFrame(stay_points)

        logging.info("Stay Points Calculated Successfully")
        return stay_points, self.trace