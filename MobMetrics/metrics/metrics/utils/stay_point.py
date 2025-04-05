from .utils import distance
from ...models import StayPointModel, VisitModel, TravelsModel
from ..spatial.travel_distance import TravelDistance
from ..temporal.travel_time import TravelTime
from ..kinematic.travel_avarage_speed import TravelAverageSpeed


class StayPoints:
    def __init__(self, trace, entity_id, parameters):
        self.trace = trace
        self.entity_id = entity_id
        self.distance_threshold = parameters[0]
        self.time_threshold = parameters[1]
        self.file_name = parameters[4]

    def extract(self):
        self.trace['spId'] = 0
        last_sp = StayPointModel.objects.filter(fileName=self.file_name).order_by('spId').last()
        stay_point_id = last_sp.spId + 1 if last_sp else 1

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

        num_travels, avg_travel_time, avg_travel_distance, avg_travel_avg_speed = self.process_travels()
        return visit_count, time_visit_count, num_travels, avg_travel_time, avg_travel_distance, avg_travel_avg_speed

    def _detect_stay_point(self, start_idx, stay_point_id):
        arrival_time = self.trace.iloc[start_idx]['time']
        x_total = self.trace.iloc[start_idx]['x']
        y_total = self.trace.iloc[start_idx]['y']
        z_total = self.trace.iloc[start_idx]['z']
        point_count = 1

        end_idx = start_idx + 1
        while end_idx < len(self.trace) and distance(self.trace.iloc[start_idx], self.trace.iloc[end_idx]) <= self.distance_threshold:
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

            for existing_sp in StayPointModel.objects.filter(fileName=self.file_name):
                if distance({'x': existing_sp.x, 'y': existing_sp.y, 'z': existing_sp.z}, {'x': x_avg, 'y': y_avg, 'z': z_avg}) <= self.distance_threshold:
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

        return None

    def process_travels(self):
        visits = list(VisitModel.objects.filter(fileName=self.file_name).order_by('arvT'))

        num_travels = 0
        total_travel_time = 0
        total_travel_distance = 0
        total_travel_avg_speed = 0

        if visits:
            first_visit = visits[0]
            travel_traces = self._get_traces_between(self.trace, self.trace['time'].min(), first_visit.arvT)

            if len(travel_traces) >= 2:
                num_travels += 1
                travel_time, travel_distance, travel_speed = self._create_travel(
                    travel_traces, first_visit.entityId
                )
                total_travel_time += travel_time
                total_travel_distance += travel_distance
                total_travel_avg_speed += travel_speed

        for i in range(len(visits) - 1):
            current_visit = visits[i]
            next_visit = visits[i + 1]

            travel_traces = self._get_traces_between(self.trace, current_visit.levT, next_visit.arvT)

            if len(travel_traces) >= 2:
                num_travels += 1
                travel_time, travel_distance, travel_speed = self._create_travel(
                    travel_traces, current_visit.entityId
                )
                total_travel_time += travel_time
                total_travel_distance += travel_distance
                total_travel_avg_speed += travel_speed

        if visits:
            last_visit = visits[-1]
            travel_traces = self._get_traces_between(self.trace, last_visit.levT, self.trace['time'].max())

            if len(travel_traces) >= 2:
                num_travels += 1
                travel_time, travel_distance, travel_speed = self._create_travel(
                    travel_traces, last_visit.entityId
                )
                total_travel_time += travel_time
                total_travel_distance += travel_distance
                total_travel_avg_speed += travel_speed

        if num_travels > 0:
            avg_travel_time = total_travel_time / num_travels
            avg_travel_distance = total_travel_distance / num_travels
            avg_travel_avg_speed = total_travel_avg_speed / num_travels
        else:
            avg_travel_time = avg_travel_distance = avg_travel_avg_speed = 0

        return num_travels, avg_travel_time, avg_travel_distance, avg_travel_avg_speed


    def _get_traces_between(self, trace_df, start_time, end_time):
        return trace_df[(trace_df['time'] >= start_time) & (trace_df['time'] <= end_time)]


    def _create_travel(self, traces, entity_id):
        travel_distance = TravelDistance(traces).extract()
        
        travel_time = TravelTime( traces.iloc[-1]['time'], traces.iloc[0]['time']).extract()
        travel_speed = TravelAverageSpeed(travel_distance, travel_time).extract()

        TravelsModel.objects.create(
            entityId=entity_id,
            arvId=traces.iloc[-1]['spId'],
            levId=traces.iloc[0]['spId'],
            TrvD=travel_distance,
            TrvT=travel_time,
            TrvAS=travel_speed,
            fileName=self.file_name
        )

        return travel_time, travel_distance, travel_speed
