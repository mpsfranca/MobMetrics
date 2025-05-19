# Local application/library specific imports.
from ...models import VisitModel, JourneyModel
from ..spatial.journey_distance import JourneyDistance
from ..temporal.journey_time import JourneyTime
from ..kinematic.journay_avarage_speed import JourneyAverageSpeed


class Journey:
    def __init__(self, trace, entity_id, parameters):
        """
        Initializes the Journey processor.

        Args:
            trace (pd.DataFrame): DataFrame with trace data.
            entity_id (int): Identifier for the entity.
            parameters (list): List of parameters; index 4 should contain file_name.
        """
        self.trace = trace
        self.entity_id = entity_id
        self.parameters = parameters
        self.file_name = parameters[4]

    def process_journey(self):
        """
        Processes journeys between visits and calculates summary statistics.

        Returns:
            tuple: (num_journeys, avg_journey_time, avg_journey_distance, avg_journey_avg_speed)
        """
        visits = list(
            VisitModel.objects.filter(file_name=self.file_name).order_by('arv_time')
        )

        num_journeys = 0
        total_journey_time = 0
        total_journey_distance = 0
        total_journey_avg_speed = 0

        if not visits:
            return 0, 0.0, 0.0, 0.0

        # Before first visit
        first_visit = visits[0]
        journey_traces = self._get_traces_between(
            self.trace, self.trace['time'].min(), first_visit.arv_time
        )

        if len(journey_traces) >= 2:
            num_journeys += 1
            j_time, j_dist, j_speed = self._create_journey(journey_traces, first_visit.entity_id)
            total_journey_time += j_time
            total_journey_distance += j_dist
            total_journey_avg_speed += j_speed

        # Between visits
        for i in range(len(visits) - 1):
            current_visit = visits[i]
            next_visit = visits[i + 1]

            journey_traces = self._get_traces_between(
                self.trace, current_visit.lev_time, next_visit.arv_time
            )

            if len(journey_traces) >= 2:
                num_journeys += 1
                j_time, j_dist, j_speed = self._create_journey(journey_traces, current_visit.entity_id)
                total_journey_time += j_time
                total_journey_distance += j_dist
                total_journey_avg_speed += j_speed

        # After last visit
        last_visit = visits[-1]
        journey_traces = self._get_traces_between(
            self.trace, last_visit.lev_time, self.trace['time'].max()
        )

        if len(journey_traces) >= 2:
            num_journeys += 1
            j_time, j_dist, j_speed = self._create_journey(journey_traces, last_visit.entity_id)
            total_journey_time += j_time
            total_journey_distance += j_dist
            total_journey_avg_speed += j_speed

        if num_journeys == 0:
            return 0, 0.0, 0.0, 0.0

        
        avg_time = total_journey_time / num_journeys
        avg_distance = total_journey_distance / num_journeys
        avg_speed = total_journey_avg_speed / num_journeys

        return num_journeys, avg_time, avg_distance, avg_speed

    def _get_traces_between(self, trace_df, start_time, end_time):
        """
        Filters trace data between two timestamps.

        Args:
            trace_df (pd.DataFrame): The full trace data.
            start_time: Start timestamp.
            end_time: End timestamp.

        Returns:
            pd.DataFrame: Filtered traces.
        """
        return trace_df[(trace_df['time'] >= start_time) & (trace_df['time'] <= end_time)]

    def _create_journey(self, traces, entity_id):
        """
        Creates a journey entry in the database and calculates metrics.

        Args:
            traces (pd.DataFrame): Trace segment.
            entity_id (int): Entity identifier.

        Returns:
            tuple: (journey_time, journey_distance, journey_speed)
        """
        journey_distance = JourneyDistance(traces, self.parameters).extract()
        journey_time = JourneyTime(traces.iloc[-1]['time'], traces.iloc[0]['time']).extract()
        journey_speed = JourneyAverageSpeed(journey_distance, journey_time).extract()

        JourneyModel.objects.create(
            file_name = self.file_name,
            entity_id = entity_id,
            lev_id = traces.iloc[0]['spId'],
            arv_id = traces.iloc[-1]['spId'],
            journey_distance = journey_distance,
            journey_time = journey_time,
            journey_avg_speed = journey_speed
        )

        return journey_time, journey_distance, journey_speed
