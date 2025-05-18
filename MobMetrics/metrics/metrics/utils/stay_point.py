# Local application/library specific imports.
from .visits import Visit
from .journeys import Journey
from ...models import StayPointModel
from .utils import distance


class StayPoints:
    def __init__(self, trace, entity_id, parameters):
        """
        Class that detects Stay Points from a mobility trace and configuration parameters.
        Also invokes the Visit and Journey processing modules.
        """
        # Defensive copy to avoid SettingWithCopyWarning
        self.trace = trace.copy()

        self.entity_id = entity_id
        self.parameters = parameters
        self.distance_threshold = parameters[0]
        self.time_threshold = parameters[1]
        self.file_name = parameters[4]
        self.is_geographical_coordinates = parameters[6]

        self.visit_processor = Visit(self.trace, self.entity_id, self.parameters)
        self.journey_processor = Journey(self.trace, self.entity_id, self.parameters)

    def extract(self):
        """
        Extracts stay points and computes journey metrics.

        Returns:
            visit_count (int): number of registered visits
            time_visit_count (float): total visit time
            num_journeys (int): total number of journeys
            avg_journey_time (float): average journey duration
            avg_journey_distance (float): average journey distance
            avg_journey_avg_speed (float): average journey speed
        """
        # Safe assignment without chained warning
        self.trace.loc[:, 'spId'] = 0

        last_sp = StayPointModel.objects.filter(file_name=self.file_name).order_by('stay_point_id').last()
        stay_point_id = last_sp.stay_point_id + 1 if last_sp else 1

        start_idx = 0
        visit_count = 0
        time_visit_count = 0

        while start_idx < len(self.trace):
            result = self._detect_stay_point(start_idx, stay_point_id)
            if result:
                end_idx, updated_sp_id, duration, created_new = result
                self.trace.iloc[start_idx:end_idx, self.trace.columns.get_loc('spId')] = updated_sp_id
                if created_new:
                    stay_point_id += 1
                visit_count += 1
                time_visit_count += duration
                start_idx = end_idx
            else:
                start_idx += 1

        num_journeys, avg_journey_time, avg_journey_distance, avg_journey_avg_speed = self.journey_processor.process_journey()

        return visit_count, time_visit_count, num_journeys, avg_journey_time, avg_journey_distance, avg_journey_avg_speed

    def _detect_stay_point(self, start_idx, stay_point_id):
        arrival_time = self.trace.iloc[start_idx]['time']
        x_total = self.trace.iloc[start_idx]['x']
        y_total = self.trace.iloc[start_idx]['y']
        z_total = self.trace.iloc[start_idx]['z']
        point_count = 1

        end_idx = start_idx + 1
        while (
            end_idx < len(self.trace) and
            distance(self.trace.iloc[start_idx], self.trace.iloc[end_idx], self.is_geographical_coordinates) <= self.distance_threshold
        ):
            x_total += self.trace.iloc[end_idx]['x']
            y_total += self.trace.iloc[end_idx]['y']
            z_total += self.trace.iloc[end_idx]['z']
            point_count += 1
            end_idx += 1

        leave_time = self.trace.iloc[end_idx - 1]['time']
        duration = leave_time - arrival_time

        if duration >= self.time_threshold:
            x_avg = round(x_total / point_count, 5)
            y_avg = round(y_total / point_count, 5)
            z_avg = round(z_total / point_count, 5)

            return self.visit_processor.process_visit(
                x_avg, y_avg, z_avg,
                arrival_time, leave_time,
                duration, stay_point_id, end_idx
            )

        return None
