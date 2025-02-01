from .utils import distance  # Function to calculate the distance between two points
from ...models import StayPointModel, VisitModel, TravelsModel
from ..spatial.travel_distance import TravelDistance
from ..temporal.travel_time import TravelTime
from ..kinematic.travel_avarage_speed import TravelAverageSpeed

class StayPoints:
    """
    Class to calculate and save stay points, associated visits, and travels.

    This class processes a trajectory (trace) to detect stay points based on distance and time thresholds.
    It then calculates and stores metrics related to the travels between these points.
    """

    def __init__(self, trace, distance_threshold, time_threshold, entity_id, name):
        """
        Initializes the StayPoints class with the provided parameters.

        :param trace: DataFrame containing the dataset with the trajectory.
        :param distance_threshold: Distance threshold to consider nearby points as part of the same stay.
        :param time_threshold: Time threshold to consider points as part of the same stay.
        :param entity_id: Unique identifier for the entity (user, vehicle, etc.).
        :param name: Name or identifier of the file associated with the trajectory.
        """
        self.trace = trace  # Trajectory data (as a DataFrame)
        self.distance_threshold = distance_threshold  # Distance threshold in meters
        self.time_threshold = time_threshold  # Time threshold in seconds
        self.entity_id = entity_id  # ID of the entity (e.g., user or vehicle)
        self.name = name  # File name associated with the trajectory

    def extract(self):
        """
        Extracts stay points from the trajectory, saves them, and processes travels.

        Returns the updated DataFrame with the assigned spId for each point and the total number of visits.
        """
        self.trace['spId'] = 0  # Initialize a new column for stay point IDs
        # Fetch the last stay point ID from the database and start incrementing from there
        last_sp = StayPointModel.objects.filter(fileName=self.name).order_by('spId').last()
        stay_point_id = last_sp.spId + 1 if last_sp else 1  # Start with the next available ID
        m = 0  # Start processing trajectory data
        visit_count = 0  # Count the number of visits

        while m < len(self.trace):

            # Variables to calculate the stay point
            arvT = self.trace.iloc[m]['time']  # Arrival time
            lat_sum = self.trace.iloc[m]['x']  # Sum of latitudes
            lgnt_sum = self.trace.iloc[m]['y']  # Sum of longitudes
            alt_sum = self.trace.iloc[m]['z']  # Sum of altitudes
            buffer = 1  # Buffer to count the number of points in the stay

            i = m + 1  # Start grouping points into the stay
            while i < len(self.trace) and distance(self.trace.iloc[m], self.trace.iloc[i]) <= self.distance_threshold:
                lat_sum += self.trace.iloc[i]['x']
                lgnt_sum += self.trace.iloc[i]['y']
                alt_sum += self.trace.iloc[i]['z']
                buffer += 1  # Increase the number of points in the stay
                i += 1

            levT = self.trace.iloc[i - 1]['time']  # Departure time (last point in the stay)

            # Check if the stay duration exceeds the time threshold
            if (levT - arvT) >= self.time_threshold:
                # Calculate the average coordinates of the stay
                x = round(lat_sum / buffer, 5)
                y = round(lgnt_sum / buffer, 5)
                z = round(alt_sum / buffer, 5)

                exists = False  # Flag to check if the stay point already exists
                # Check if a similar stay point already exists in the database
                for aux in StayPointModel.objects.filter(fileName=self.name):
                    if distance({'x': aux.x, 'y': aux.y, 'z': aux.z}, {'x': x, 'y': y, 'z': z}) <= self.distance_threshold:
                        # If a similar stay point exists, assign the spId to the trajectory points
                        self.trace.iloc[m:i, self.trace.columns.get_loc('spId')] = aux.spId
                        aux.numVisits += 1
                        visit_count += 1
                        aux.save()

                        # Log the visit in VisitModel
                        VisitModel.objects.create(
                            entityId=self.entity_id,
                            spId=aux.spId,
                            fileName=self.name,
                            arvT=arvT,
                            levT=levT,
                            visitT=levT - arvT
                        )
                        exists = True
                        break

                if not exists:
                    visit_count += 1
                    # If the stay point does not exist, create a new one
                    StayPointModel.objects.create(
                        spId=stay_point_id,
                        x=x,
                        y=y,
                        z=z,
                        numVisits=1,
                        fileName=self.name
                    )
                    # Assign the new spId to the trajectory points
                    self.trace.iloc[m:i, self.trace.columns.get_loc('spId')] = stay_point_id

                    # Log the visit in VisitModel
                    VisitModel.objects.create(
                        entityId=self.entity_id,
                        spId=stay_point_id,
                        fileName=self.name,
                        arvT=arvT,
                        levT=levT,
                        visitT=levT - arvT
                    )

                    stay_point_id += 1  # Increment the stay point ID for the next one

            m = i  # Move to the next point in the trajectory

        # Process travels after calculating stay points
        self.process_travels()

        return  visit_count

    def process_travels(self):
        """
        Processes and saves travel metrics based on visits and traces.
        """
        visits = VisitModel.objects.filter(fileName=self.name)

        for visit in visits:
            # Get traces corresponding to the stay point ID
            traces = self.trace[self.trace['spId'] == visit.spId]

            if len(traces) >= 2:
                # Find the trace corresponding to the departure time
                trace_departure = traces[traces['time'] == visit.levT]
                # Find the trace corresponding to the arrival time
                trace_arrival = traces[traces['time'] == visit.arvT]

                if not trace_departure.empty and not trace_arrival.empty:
                    # Use the first matching row for departure and arrival
                    trace_departure = trace_departure.iloc[0]
                    trace_arrival = trace_arrival.iloc[0]

                    # Filter traces between departure and arrival times
                    intermediate_traces = traces[
                        (traces['time'] > trace_departure['time']) & 
                        (traces['time'] < trace_arrival['time'])
                    ]

                    # Calculate travel metrics
                    distance_metric = TravelDistance(intermediate_traces)
                    time_metric = TravelTime(visit.visitT, trace_departure['time'])
                    speed_metric = TravelAverageSpeed(
                        distance_metric.extract(), time_metric.extract()
                    )

                    # Save travel data
                    TravelsModel.objects.create(
                        entityId=visit.entityId,
                        arvId=trace_arrival['spId'],
                        levId=trace_departure['spId'],
                        TrvD=distance_metric.extract(),
                        TrvT=time_metric.extract(),
                        TrvAS=speed_metric.extract(),
                        fileName=self.name
                    )
