from ...models import StayPointModel, VisitModel
from .utils import distance

class Visit:
    def __init__(self, trace, entity_id, parameters):
        self.trace = trace
        self.entity_id = entity_id
        self.parameters = parameters
        self.file_name = parameters[4]
        self.distance_threshold = parameters[0]
        self.is_geographical_coordinates = parameters[6]

    def process_visit(self, x_avg, y_avg, z_avg, arrival_time, leave_time, duration, stay_point_id, end_idx):
        for existing_sp in StayPointModel.objects.filter(fileName=self.file_name):
            if distance(
                {'x': existing_sp.x, 'y': existing_sp.y, 'z': existing_sp.z},
                {'x': x_avg, 'y': y_avg, 'z': z_avg},
                self.is_geographical_coordinates
            ) <= self.distance_threshold:
                existing_sp.numVisits += 1
                existing_sp.save()

                VisitModel.objects.create(
                    entityId=self.entity_id,
                    spId=existing_sp.spId,
                    fileName=self.file_name,
                    arvT=arrival_time,
                    levT=leave_time,
                    visitT=duration
                )
                return end_idx, existing_sp.spId, duration, False

        StayPointModel.objects.create(
            spId=stay_point_id,
            x=x_avg,
            y=y_avg,
            z=z_avg,
            numVisits=1,
            fileName=self.file_name
        )

        VisitModel.objects.create(
            entityId=self.entity_id,
            spId=stay_point_id,
            fileName=self.file_name,
            arvT=arrival_time,
            levT=leave_time,
            visitT=duration
        )

        return end_idx, stay_point_id, duration, True
