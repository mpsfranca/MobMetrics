# Related third party imports.
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

# Local application/library specific imports.
from ...utils.abs_data import AbsData
from .clustering.DBscan import DBscan

class tSNE(AbsData):
    """
    Class to perform t-Distributed Stochastic Neighbor Embedding (t-SNE)
    on selected columns of a DataFrame.
    """

    def __init__(self, n_components, perplexity, data, columns, dbscan_paramters):
        """
        Initializes the TSNEEmbedding extractor.

        Args:
            n_components (int): Number of dimensions to embed into.
            perplexity (float): Perplexity parameter for t-SNE.
            data (pd.DataFrame): Input dataset.
            columns (list): List of column names to apply t-SNE on.
        """
        self.data = data
        self.columns = columns
        self.n_components = n_components
        self.perplexity = perplexity
        self.dbscan_paramters = dbscan_paramters

    def extract(self):
        """
        Executes the t-SNE transformation and returns the result as JSON.

        Returns:
            str or None: JSON string with t-SNE components, or None if invalid.
        """
        self.n_components = min(self.n_components, len(self.columns))

        if self.n_components > 0:
            tsne_result = self._tsne()
        else:
            tsne_result = None

        tsne_result = self._label_dataframe(tsne_result)

        tsne = self._clustering(tsne_result['components'])

        tsne_json = tsne.to_json(orient='records') if tsne_result else None

        return tsne_json

    def _tsne(self):
        """
        Applies t-SNE on the standardized selected columns.

        Returns:
            dict: Contains the transformed components as a DataFrame.

        Raises:
            ValueError: If n_components is not 2 or 3.
        """
        selected_data = self.data[self.columns]

        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(selected_data)

        # Validate n_components
        if self.n_components not in [2, 3]:
            raise ValueError("t-SNE currently supports only 2 or 3 components for visualization.")

        # Validate and adjust perplexity
        n_samples = scaled_data.shape[0]
        effective_perplexity = min(self.perplexity, max(1, n_samples - 1))

        # Fit t-SNE
        tsne = TSNE(n_components=self.n_components, perplexity=effective_perplexity, random_state=42)
        tsne_components = tsne.fit_transform(scaled_data)

        component_names = [f'TSNE{i+1}' for i in range(tsne_components.shape[1])]
        components_df = pd.DataFrame(tsne_components, columns=component_names)

        return {
            'components': components_df
        }


    def _label_dataframe(self, result):
        """
        Adds original labels to the t-SNE components if present.

        Args:
            result (dict): Dictionary containing 'components' DataFrame.

        Returns:
            dict: Updated result dictionary with labels added (if applicable).
        """
        if result and 'label' in self.data.columns:
            result['components']['label'] = self.data['label'].reset_index(drop=True)

        return result

    def _clustering(self, result):

        dbscan_result = DBscan(self.dbscan_paramters, result).extract()
        result['dbscan_cluster'] = dbscan_result['cluster_labels']

        return result