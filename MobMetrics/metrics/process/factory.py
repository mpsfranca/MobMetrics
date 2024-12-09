import pandas as pd
from django.db import transaction

from ..models import StayPointModel, VisitModel, MetricsModel, TraceModel, TravelsModel

from ..metrics.utils.stay_point import StayPoints

from ..metrics.temporal.travel_time import TravelTime
from ..metrics.temporal.total_travel_time import TotalTravelTime

from ..metrics.social.entropy import Entropy

from ..metrics.spatial.travel_distance import TravelDistance
from ..metrics.spatial.total_travel_distance import TotalTravelDistance
from ..metrics.spatial.center_of_mass import CenterOfMass
from ..metrics.spatial.radios_of_gyration import RadiusOfGyration

from ..metrics.kinematic.travel_avarage_speed import TravelAverageSpeed
from ..metrics.kinematic.total_travel_avarage_speed import TotalTravelAverageSpeed

# Disable chained assignment warnings
pd.options.mode.chained_assignment = None  # default='warn'


class Factory:
    def __init__(self):
        pass

    def extract(self, trace, parameters, entity_id):
        """Extract metrics and stay points for a given trace."""
        self.metrics(trace, entity_id)
        self.stay_points(trace, parameters, entity_id)

    def reextract(self):
        Entropy().extract()

    def metrics(self, trace_file, entity_id):
        """Calculate and save metrics for the given trace file."""
        if trace_file.empty:
            return

        total_travel_time = TotalTravelTime(trace_file).extract()
        total_travel_distance = TotalTravelDistance(trace_file).extract()
        total_travel_average_speed = TotalTravelAverageSpeed(total_travel_time, total_travel_distance).extract()
        center_of_mass = CenterOfMass(trace_file).extract()
        radius_of_gyration = RadiusOfGyration(trace_file, center_of_mass).extract()

        MetricsModel.objects.create(
            entityId=entity_id,
            TTrvT=total_travel_time,
            TTrvD=total_travel_distance,
            TTrvAS=total_travel_average_speed,
            x=center_of_mass[0],
            y=center_of_mass[1],
            z=center_of_mass[2],
            radius=radius_of_gyration
        )

    def stay_points(self, trace_file, parameters, entity_id):
        """Extract and save stay points from trace file."""
        if not parameters or len(parameters) < 2:
            raise ValueError("Insufficient parameters for StayPoints.")
        
        trace = StayPoints(trace_file, parameters[0], parameters[1], entity_id).extract()
        self.trace(trace)

    def trace(self, trace):
        """Save trace data to the TraceModel."""
        TraceModel.objects.bulk_create([
            TraceModel(
                entityId=row['id'],
                x=row['x'],
                y=row['y'],
                z=row['z'],
                time=row['time'],
                spId=row['spId']
            )
            for _, row in trace.iterrows()
        ])

    def travels(self):
        """Calculate and save travel metrics for all visits."""
        # Retrieve all visits from VisitModel
        visits = VisitModel.objects.all()

        for visit in visits:
            # Get departure and arrival traces for the entity
            traces = TraceModel.objects.filter(
                entityId=visit.entityId, spId=visit.spId
            ).order_by('time')

            # Ensure there are at least two traces (departure and arrival)
            if len(traces) >= 2:
                # Find departure and arrival traces based on time
                trace_departure = traces.filter(time=visit.levT).first()
                trace_arrival = traces.filter(time=visit.arvT).first()

                if trace_departure and trace_arrival:
                    # Create instances of metrics
                    distance_metric = TravelDistance(
                        traces.filter(time__gt=trace_departure.time, time__lt=trace_arrival.time)
                    )
                    time_metric = TravelTime(visit.visitT, trace_departure.time)
                    speed_metric = TravelAverageSpeed(
                        distance_metric.extract(), time_metric.extract()
                    )

                    # Get the calculated values
                    total_distance = distance_metric.extract()
                    travel_time = time_metric.extract()
                    average_speed = speed_metric.extract()

                    # Save the data to the TravelsModel
                    TravelsModel.objects.create(
                        entityId=visit.entityId,
                        arvId=trace_arrival.spId,  # Arrival ID inferred from trace
                        levId=trace_departure.spId,  # Departure ID inferred from trace
                        TrvD=total_distance,  # Total distance
                        TrvT=travel_time,  # Travel time
                        TrvAS=average_speed  # Average speed
                    )
