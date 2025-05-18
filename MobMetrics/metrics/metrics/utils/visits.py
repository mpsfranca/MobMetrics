# Related third party imports.
from .utils import distance

# Local application/library specific imports.
from ...models import StayPointModel, VisitModel

class Visit:
    """
    A class to handle the processing and registration of visits and stay points for a given entity trace.
    """

    def __init__(self, trace, entity_id, parameters):
        """
        Initialize a VisitProcessor instance.

        Args:
            trace (list): A list representing the movement trace of an entity.
            entity_id (int or str): Unique identifier for the entity.
            parameters (list): A list of parameters where:
                parameters[0] - distance threshold for matching stay points
                parameters[4] - file name (str)
                parameters[6] - boolean indicating if coordinates are geographical
        """
        self.trace = trace
        self.entity_id = entity_id
        self.parameters = parameters
        self.file_name = parameters[4]
        self.distance_threshold = parameters[0]
        self.is_geographical_coordinates = parameters[6]

    def process_visit(self, x_avg, y_avg, z_avg, arrival_time, leave_time, duration, stay_point_id, end_idx):
        """
        Process a new visit and associate it with an existing or new stay point.

        Args:
            x_avg (float): Average x coordinate of the stay point.
            y_avg (float): Average y coordinate of the stay point.
            z_avg (float): Average z coordinate of the stay point.
            arrival_time (datetime): Timestamp when the visit started.
            leave_time (datetime): Timestamp when the visit ended.
            duration (float): Duration of the visit in seconds.
            stay_point_id (int or str): Unique identifier for the stay point.
            end_idx (int): Index in the trace where the visit ends.

        Returns:
            tuple: (end_idx, matched_stay_point_id, duration, is_new_stay_point)
        """
        for existing_sp in StayPointModel.objects.filter(file_name=self.file_name):
            dist = distance(
                {'x': existing_sp.x_center, 'y': existing_sp.y_center, 'z': existing_sp.z_center},
                {'x': x_avg, 'y': y_avg, 'z': z_avg},
                self.is_geographical_coordinates
            )

            if dist <= self.distance_threshold:
                existing_sp.num_visits += 1
                existing_sp.total_visits_time += duration
                existing_sp.save()

                VisitModel.objects.create(
                    file_name = self.file_name,
                    entity_id = self.entity_id,
                    stay_point_id = existing_sp.stay_point_id,
                    arv_time = arrival_time,
                    lev_time = leave_time,
                    visit_time = duration
                )

                return end_idx, existing_sp.stay_point_id, duration, False

        # No matching stay point found; create a new one
        StayPointModel.objects.create(
            file_name = self.file_name,
            stay_point_id = stay_point_id,
            x_center = x_avg,
            y_center = y_avg,
            z_center = z_avg,
            num_visits = 1,
            total_visits_time = duration,
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
