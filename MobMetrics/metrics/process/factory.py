import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from django.db import transaction
from ..models import MetricsModel
from ..models import StayPointModel
from ..models import TraceModel
from ..models import TravelsModel

# from utils
from ..metrics.utils.stay_point import StayPoints
#from temporal
from ..metrics.temporal.travel_time import TravelTime
from ..metrics.temporal.total_travel_time import TotalTravelTime
#from spatial
from ..metrics.spatial.travel_distance import TravelDistance
from ..metrics.spatial.total_travel_distance import TotalTravelDistance
from ..metrics.spatial.center_of_mass import CenterOfMass
from ..metrics.spatial.radios_of_gyration import RadiusOfGyration
#from social

#from cinematic
from ..metrics.kinematic.travel_avarage_speed import TravelAverageSpeed
from ..metrics.kinematic.total_travel_avarage_speed import TotalTravelAverageSpeed

class Factory:
    def __init__(self, trace, parameters, id):
        self.trace_file = trace
        self.parameters = parameters
        self.id = id

    @transaction.atomic
    def extract(self):
        self.metrics()
        self.stayPoints()

    def metrics(self):
        if self.trace_file.empty:
            return

        total_travel_time = TotalTravelTime(self.trace_file).extract()
        total_travel_distance = TotalTravelDistance(self.trace_file).extract()
        total_travel_average_speed = TotalTravelAverageSpeed(total_travel_time, total_travel_distance).extract()
        center_of_mass = CenterOfMass(self.trace_file).extract()
        radius_of_gyration = RadiusOfGyration(self.trace_file, center_of_mass).extract()
        
        MetricsModel.objects.create(
            entityId=self.id,
            TTrvT=total_travel_time,
            TTrvD=total_travel_distance,
            TTrvAS=total_travel_average_speed,
            x=center_of_mass[0],
            y=center_of_mass[1],
            z=center_of_mass[2],
            radius=radius_of_gyration
        )

    def stayPoints(self):
        if not self.parameters or len(self.parameters) < 2:
            raise ValueError("Insufficient parameters for StayPoints.")
        
        stay_point, trace = StayPoints(self.trace_file, self.parameters[0], self.parameters[1]).extract()
        
        if not stay_point.empty:

            StayPointModel.objects.bulk_create([
                StayPointModel(
                    entityId=self.id,
                    spId=row['spId'],
                    x=row['x'],
                    y=row['y'],
                    z=row['z'],
                    arvT=row['arvT'],
                    levT=row['levT'],
                    visitTime=row['visit_time']
                )
                for _, row in stay_point.iterrows()
            ])
        
        self.trace(trace)
        self.travels(trace, stay_point)

    
    def trace(self, trace):
        TraceModel.objects.all().delete()
        TraceModel.objects.bulk_create([
            TraceModel(
                entityId=row['id'],
                x=row['x'],
                y=row['y'],
                z=row['z'],
                time = row['time'],
                spId=row['spId']
            )
            for _, row in trace.iterrows()
        ])

    def travels(self, trace, stay_point):
        if trace.empty or stay_point.empty:
            return
        
        travel_time = TravelTime(stay_point, trace.head(1), trace.tail(1)).extract()
        travel_distance = TravelDistance(trace, travel_time).extract()
        travels = TravelAverageSpeed(travel_distance).extract()
        
        TravelsModel.objects.all().delete()
        TravelsModel.objects.bulk_create([
            TravelsModel(
                entityId=self.id,
                arvId=row['arvId'],
                levId=row['levId'],
                TrvT=row['travel_time'],
                TrvD=row['travel_distance'],
                TrvAS=row['average_speed']
            )
            for _, row in travels.iterrows()
        ])
