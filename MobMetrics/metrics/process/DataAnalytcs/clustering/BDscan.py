# Related third party imports.
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# Local application/library specific imports.
from ....utils.abs_data import AbsData

class DBSCANCluster(AbsData):
    """
    Wrapper class for performing DBSCAN clustering
    on a specified subset of a DataFrame.
    """

    def __init__(self, eps, min_samples, data, columns):
        """
        Initializes the DBSCAN clustering extractor.

        Args:
            eps (float): The maximum distance between two samples for one to be considered as in the neighborhood of the other.
            min_samples (int): The number of samples in a neighborhood for a point to be considered as a core point.
            data (pd.DataFrame): Input dataset.
            columns (list, optional): List of column names to apply DBSCAN on, if None, all columns are used.
        """
        self.data = data
        self.columns = columns
        self.eps = eps
        self.min_samples = min_samples

    def extract(self):
        """
        Executes the DBSCAN process and returns the results.

        Returns:
            dict: A dictionary containing:
                - 'dbscan_json': JSON representation of clustered points.
                - 'eps': The epsilon value used in DBSCAN.
                - 'min_samples': The minimum samples required for a point to be considered a core point.
                - 'cluster_labels': Cluster labels for each data point.
        """
        dbscan_result = self._dbscan()

        # Convert to JSON format
        dbscan_json = dbscan_result['clusters'].to_json(orient='records')

        return {
            'dbscan_json': dbscan_json,
            'eps': self.eps,
            'min_samples': self.min_samples,
            'cluster_labels': dbscan_result['cluster_labels'].tolist(),
        }

    def _dbscan(self):
        """
        Applies DBSCAN on the selected or entire dataset.

        Returns:
            dict: Contains the cluster labels and the clustered data.
        """
        # If specific columns are provided, use those, otherwise use all columns
        selected_data = self.data[self.columns] if self.columns else self.data

        # Standardizing the data before applying DBSCAN
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(selected_data)

        # Apply DBSCAN
        dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples)
        cluster_labels = dbscan.fit_predict(scaled_data)

        # Add the cluster labels to the original data
        self.data['cluster'] = cluster_labels

        # Create a DataFrame with the clustered data
        clusters_df = self.data[['cluster'] + self.columns if self.columns else self.data.columns.tolist()]

        return {
            'clusters': clusters_df,
            'cluster_labels': cluster_labels,
        }
