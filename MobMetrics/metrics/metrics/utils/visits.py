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
        for existing_sp in StayPointModel.objects.filter(file_name=self.file_name):
            if distance(
                {'x': existing_sp.x_center, 'y': existing_sp.y_center, 'z': existing_sp.z_center},
                {'x': x_avg, 'y': y_avg, 'z': z_avg},
                self.is_geographical_coordinates
            ) <= self.distance_threshold:
                existing_sp.num_visits += 1
                existing_sp.total_visits_time += duration
                existing_sp.save()

                VisitModel.objects.create(
                    fileName = self.file_name,
                    entity_id = self.entity_id,
                    stay_point_id = existing_sp.spId,
                    arv_time = arrival_time,
                    lev_time = leave_time,
                    visit_time = duration
                )
                return end_idx, existing_sp.stay_point_id, duration, False

        StayPointModel.objects.create(
            fileName = self.file_name,
            stay_point_id = stay_point_id,
            x_center = x_avg,
            y_center = y_avg,
            z_center = z_avg,
            num_visits = 1,
            total_visits_time = 0,
        )

        VisitModel.objects.create(
            file_name = self.file_name,
            entity_id = self.entity_id,
            stay_point_id = stay_point_id,
            arv_time = arrival_time,
            lev_time = leave_time,
            visit_time = duration
        )

        return end_idx, stay_point_id, duration, True
