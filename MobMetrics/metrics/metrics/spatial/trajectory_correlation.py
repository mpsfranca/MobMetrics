# Standard library imports.
import numpy as np

# Related third party imports.
import tqdm
from sklearn.metrics.pairwise import cosine_similarity

# Local application/library specific imports.
from ..utils.abs_metric import AbsMetric
from ...models import GlobalMetricsModel


class TrajectoryCorrelationDegree(AbsMetric):
    """
    A metric class to compute the trajectory correlation degree among entities.
    The higher the similarity between trajectories, the higher the correlation degree.

    Attributes:
        trace (pd.DataFrame): Data containing coordinates, timestamp, and entity ID.
        parameters (list): Configuration parameters for processing.
        fraction (float): Fraction of points to sample from the shortest trajectory.
        min_points (int): Minimum number of points required for sampling.
        fixed_n_points (int): Number of points to sample uniformly from each trajectory.
    """

    def __init__(self, trace, parameters):
        """
        Initialize the TrajectoryCorrelationDegree class.

        Args:
            trace (pd.DataFrame): Trajectory data with 'x', 'y', 'time', and 'id' columns.
            parameters (list): A list of configuration parameters.
        """
        self.trace = trace
        self.parameters = parameters

        self.fraction = 0.8
        self.min_points = 20

        group_sizes = self.trace.groupby('id').size()
        self.fixed_n_points = max(self.min_points, int(self.fraction * group_sizes.min()))

    def _uniform_sample_traj(self, df_id):
        """
        Uniformly sample a fixed number of points from a single trajectory.

        Args:
            df_id (pd.DataFrame): Trajectory data for a single entity.

        Returns:
            np.ndarray or None: Flattened array of sampled (x, y) coordinates,
                                or None if trajectory is too short.
        """
        df_id_sorted = df_id.sort_values('time')

        if len(df_id_sorted) < self.fixed_n_points:
            return None

        sampled = df_id_sorted.iloc[
            np.linspace(0, len(df_id_sorted) - 1, self.fixed_n_points, dtype=int)
        ]

        return sampled[['x', 'y']].to_numpy().flatten()

    def extract(self):
        """
        Compute the correlation degree of the trajectories using cosine similarity.
        The result is saved into the GlobalMetricsModel.

        Returns:
            None
        """
        vectors = []

        for ent_id, df_ent in tqdm.tqdm(self.trace.groupby('id'), desc="Trajectory Correlation Degree"):
            traj_vector = self._uniform_sample_traj(df_ent)

            if traj_vector is not None:
                vectors.append(traj_vector)

        if len(vectors) < 2:
            return 0.0

        vectors = np.array(vectors)
        sim_matrix = cosine_similarity(vectors)

        upper_indices = np.triu_indices_from(sim_matrix, k=1)
        sim_values = sim_matrix[upper_indices]

        dist_values = 1 - sim_values
        correlation_degree = 1 - np.std(dist_values)

        global_metric = GlobalMetricsModel.objects.get(file_name=self.parameters[4])
        global_metric.trajectory_correlation = correlation_degree
        global_metric.save()
