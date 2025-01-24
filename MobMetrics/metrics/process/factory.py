import pandas as pd
pd.options.mode.chained_assignment = None
import tqdm
from ..models import MetricsModel, TraceModel

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
    def __init__(self, trace_file, parameters, name):
        self.name = name
        self.trace_file = trace_file
        self.parameters = parameters
        self.total_visits = 0

    def extract(self):
        ids = self.trace_file['id'].unique()

        for id in tqdm.tqdm(ids, desc="Individual Metrics"):


            filtred_trace = self.trace_file[self.trace_file['id'] == id]
            self.metrics(id, filtred_trace)
            self.stayPoint(filtred_trace, id)

        Entropy(self.name, self.total_visits).extract()
        DetectContact(self.parameters, self.name).extract()

    def metrics(self, id, filtred_trace):
        total_travel_time = TotalTravelTime(filtred_trace).extract()
        total_travel_distance = TotalTravelDistance(filtred_trace).extract()
        total_travel_average_speed = TotalTravelAverageSpeed(total_travel_time, total_travel_distance).extract()
        center_of_mass = CenterOfMass(filtred_trace).extract()
        radius_of_gyration = RadiusOfGyration(filtred_trace, center_of_mass).extract()

        MetricsModel.objects.create(
            fileName=self.name,
            entityId=id,
            TTrvT=total_travel_time,
            TTrvD=total_travel_distance,
            TTrvAS=total_travel_average_speed,
            x_center=center_of_mass[0],
            y_center=center_of_mass[1],
            z_center=center_of_mass[2],
            radius=radius_of_gyration
        )

    def stayPoint(self, filtred_trace, id):
        trace, visits = StayPoints(filtred_trace, self.parameters[0], self.parameters[1], id, self.name).extract()

        self.total_visits += visits
        self.trace(trace)

    def trace(self, trace):
        TraceModel.objects.bulk_create([
            TraceModel(
                fileName=self.name,
                entityId=row['id'],
                x=row['x'],
                y=row['y'],
                z=row['z'],
                time=row['time'],
                spId=row['spId']
            )
            for _, row in trace.iterrows()
        ])
