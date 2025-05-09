from ..utils.abs_metric import AbsMetric
from ...models import GlobalMetricsModel
from sklearn.metrics.pairwise import cosine_similarity

import numpy as np
import tqdm

class TrajectoryCorrelationDegree(AbsMetric):
    def __init__(self, trace, parameters):
        """
        Class that represents the Trajectory Correlation Degree metric. The more similar the trajectories
        of the entities present in the trace are, the higher the index represented by this measure will be.

        Attributes:
            `trace` (DataFrame): trace data with coordinates, timestamp and identifier
            `parameters` (list): configuration parameters for processing
            `fraction` (float): fraction of points at which trajectories will be reduced
            `min_points` (int): minimal number of points at which trajectories will be reduced
        """
        self.trace = trace
        self.parameters = parameters

        self.fraction = 0.5
        self.min_points = 20

    def _uniform_sample_traj(self, df_id):
        df_id_sorted = df_id.sort_values('time')

        n_points_id = max(
            self.min_points,
            int(self.fraction * len(df_id_sorted))
        )

        if len(df_id_sorted) < n_points_id:
            return None
        
        sampled = df_id_sorted.iloc[
            np.linspace(0, len(df_id_sorted) - 1, n_points_id, dtype=int)
        ]
        
        return sampled[['x', 'y']].to_numpy().flatten()

    def extract(self):
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

        global_metric = GlobalMetricsModel.objects.get(fileName=self.parameters[4])
        global_metric.trajectory_correlation = correlation_degree

        global_metric.save()
