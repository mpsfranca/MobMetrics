import pandas as pd
pd.options.mode.chained_assignment = None
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm # type: ignore
from ..models import MetricsModel

# from utils
from ..metrics.utils.stay_point import StayPoints

# from temporal
from ..metrics.temporal.travel_time import TravelTime
from ..metrics.temporal.total_travel_time import TotalTravelTime

# from social
from ..metrics.social.entropy import Entropy
from ..metrics.social.detect_contact import DetectContact

# from spatial
from ..metrics.spatial.travel_distance import TravelDistance
from ..metrics.spatial.total_travel_distance import TotalTravelDistance
from ..metrics.spatial.center_of_mass import CenterOfMass
from ..metrics.spatial.radios_of_gyration import RadiusOfGyration

# from kinematic
from ..metrics.kinematic.travel_avarage_speed import TravelAverageSpeed
from ..metrics.kinematic.total_travel_avarage_speed import TotalTravelAverageSpeed

class Factory:
    def __init__(self, trace_file, parameters, name, label):
        self.name = name
        self.label = label
        self.trace_file = trace_file
        self.parameters = parameters
        self.total_visits = 0

    def extract(self):
        ids = self.trace_file['id'].unique()

        for id in tqdm(ids, desc="Individual Metrics"):
            filtered_trace = self.trace_file[self.trace_file['id'] == id]


            self.metrics_parallel(id, filtered_trace)
            self.stayPoint(filtered_trace, id)
            
        Entropy(self.name, self.total_visits, self.parameters, self.trace_file).extract()
        DetectContact(self.parameters, self.name, self.trace_file).extract()

    def metrics_parallel(self, id, filtered_trace):
        def compute_temporal():
            total_travel_time = TotalTravelTime(filtered_trace).extract()
            total_travel_distance = TotalTravelDistance(filtered_trace).extract()
            total_travel_average_speed = TotalTravelAverageSpeed(total_travel_time, total_travel_distance).extract()
            return total_travel_time, total_travel_distance, total_travel_average_speed

        def compute_spatial():
            center_of_mass = CenterOfMass(filtered_trace).extract()
            radius_of_gyration = RadiusOfGyration(filtered_trace, center_of_mass).extract()
            return center_of_mass, radius_of_gyration

        with ThreadPoolExecutor() as executor:
            temporal_future = executor.submit(compute_temporal)
            spatial_future = executor.submit(compute_spatial)

            total_travel_time, total_travel_distance, total_travel_average_speed = temporal_future.result()
            center_of_mass, radius_of_gyration = spatial_future.result()

        MetricsModel.objects.create(
            fileName=self.name,

            label=self.label,
            entityId=id,
            TTrvT=total_travel_time,
            TTrvD=total_travel_distance,
            TTrvAS=total_travel_average_speed,
            x_center=center_of_mass[0],
            y_center=center_of_mass[1],
            z_center=center_of_mass[2],
            radius=radius_of_gyration
        )

    def stayPoint(self, filtered_trace, id):
        visit_count, time_visit_count, num_travels, avg_travel_time, avg_travel_distance, avg_travel_avg_speed = StayPoints(filtered_trace, self.parameters[0], self.parameters[1], id, self.name).extract()

        metric = MetricsModel.objects.get(fileName=self.name, entityId=id)
        
        metric.numStayPointsVisits = visit_count
        metric.avgTimeVisit = time_visit_count
        metric.num_travels = num_travels
        metric.avg_travel_time = avg_travel_time
        metric.avg_travel_distance = avg_travel_distance
        metric.avg_travel_avg_speed = avg_travel_avg_speed

        metric.save()

        self.total_visits += visit_count
