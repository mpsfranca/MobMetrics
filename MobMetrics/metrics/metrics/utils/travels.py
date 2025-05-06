from ...models import VisitModel, TravelsModel
from ..spatial.travel_distance import TravelDistance
from ..temporal.travel_time import TravelTime
from ..kinematic.travel_avarage_speed import TravelAverageSpeed

class Travel:
    def __init__(self, trace, entity_id, parameters):
        self.trace = trace
        self.entity_id = entity_id
        self.parameters = parameters
        self.file_name = parameters[4]

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
        travel_distance = TravelDistance(traces, self.parameters).extract()
        travel_time = TravelTime(traces.iloc[-1]['time'], traces.iloc[0]['time']).extract()
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
