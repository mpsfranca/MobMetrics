# Related third party imports.
from tqdm import tqdm

# Local application/library specific imports.
from ..models import MetricsModel
## from utils
from ..metrics.utils.stay_point import StayPoints
from ..metrics.utils.utils import globalMetrics
## from temporal
from ..metrics.temporal.total_travel_time import TotalTravelTime
## from social
from ..metrics.social.quadrant_entropy import QuadrantEntropy
from ..metrics.social.entropy import Entropy
from ..metrics.social.detect_contact import DetectContact
## from spatial
from ..metrics.spatial.total_travel_distance import TotalTravelDistance
from ..metrics.spatial.center_of_mass import CenterOfMass
from ..metrics.spatial.radios_of_gyration import RadiusOfGyration
from ..metrics.spatial.trajectory_correlation import TrajectoryCorrelationDegree
from ..metrics.spatial.staypoint_importance_degree import StaypointImportanceDegree
## from kinematic
from ..metrics.kinematic.total_travel_avarage_speed import TotalTravelAverageSpeed

class Factory:
    """
    A factory class to extract and compute different types of metrics for an individual trace file.

    Attributes:
        trace_file (DataFrame): The trace data containing the information of movement.
        parameters (list): List of parameters required for metric extraction.
        file_name (String): File name extracted from parameters
        file_label (String): Label extracted from parameters
        total_visits (int): The total number of visits recorded across all individuals.

    Methods:
        extract(): Extracts the metrics for each individual in the trace file.
        metrics(id, filtered_trace): Extracts specific metrics for each individual.
        stayPoint(filtered_trace, id): Extracts stay point-related metrics for an individual.
    """

    def __init__(self, trace_file, parameters):
        """
        Initializes the Factory with the trace file and parameters.

        Args:
            trace_file (DataFrame): The trace data containing movement information.
            parameters (list): List of parameters required for metric extraction.
        """
        self.trace_file = trace_file
        self.parameters = parameters
        self.file_name = parameters[4]
        self.file_label = parameters[5]
        self.total_visits = 0

    def extract(self):
        """
        Extracts metrics for each individual in the trace file.

        This method iterates over each unique individual ID in the trace file, applies filtering 
        to isolate their data, and computes various metrics such as total travel time, distance, 
        average speed, stay points, and entropy. It also calls other global metrics and social metrics.
        """
        ids = self.trace_file['id'].unique()

        for id in tqdm(ids, desc="Individual Metrics"):
            filtered_trace = self.trace_file[self.trace_file['id'] == id]

            self._metrics(id, filtered_trace)
            self._stayPoint(filtered_trace, id)

        # Extracting additional global and social metrics
        Entropy(self.total_visits, self.parameters, self.trace_file).extract()
        StaypointImportanceDegree(self.parameters).extract()
        DetectContact(self.parameters, self.trace_file).extract()

        globalMetrics(self.file_name)
        
        QuadrantEntropy(self.trace_file, self.parameters).extract()
        TrajectoryCorrelationDegree(self.trace_file, self.parameters).extract()

    def _metrics(self, id, filtered_trace):
        """
        Extracts individual-specific metrics and stores them in the database.

        Args:
            id (str): The ID of the individual.
            filtered_trace (DataFrame): The trace data filtered for the specific individual.
        """
        # Extracting temporal and spatial metrics
        travel_time = TotalTravelTime(filtered_trace).extract()
        travel_distance = TotalTravelDistance(filtered_trace, self.parameters).extract()
        travel_average_speed = TotalTravelAverageSpeed(travel_time, travel_distance).extract()
        center_of_mass = CenterOfMass(filtered_trace).extract()
        radius_of_gyration = RadiusOfGyration(filtered_trace, center_of_mass).extract()

        # Creating a new entry in the database for the computed metrics
        MetricsModel.objects.create(
            file_name = self.file_name,
            label = self.file_label,
            entity_id = id,
            travel_time = travel_time,
            travel_distance = travel_distance,
            travel_avg_speed = travel_average_speed,
            x_center = center_of_mass[0],
            y_center = center_of_mass[1],
            z_center = center_of_mass[2],
            radius_of_gyration=radius_of_gyration
        )

    def _stayPoint(self, filtered_trace, id):
        """
        Extracts stay point metrics and updates the database.

        Args:
            filtered_trace (DataFrame): The trace data filtered for the specific individual.
            id (str): The ID of the individual.
        """
        # Extracting stay point metrics
        (visit_count, time_visit_count, 
         num_jurnays, avg_jurnay_time, 
         avg_jurnay_distance, avg_jurnay_avg_speed) = StayPoints(filtered_trace, 
                                                                 id, self.parameters).extract()

        # Fetching the corresponding MetricsModel for the individual
        metric = MetricsModel.objects.get(file_name=self.file_name, entity_id=id)

        # Updating the extracted stay point metrics in the database
        metric.stay_points_visits = visit_count
        metric.avg_time_visit = time_visit_count / visit_count if visit_count != 0 else 0
        metric.num_jurnays = num_jurnays
        metric.avg_jurnay_time = avg_jurnay_time
        metric.avg_jurnay_distance = avg_jurnay_distance
        metric.avg_jurnay_avg_speed = avg_jurnay_avg_speed

        metric.save()

        # Accumulating total visits for global metrics
        self.total_visits += visit_count
