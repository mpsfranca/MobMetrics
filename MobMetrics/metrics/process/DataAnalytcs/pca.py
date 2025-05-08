# Related third party imports.
import pandas as pd
from sklearn.decomposition import PCA as SKPCA
from sklearn.preprocessing import StandardScaler

# Local application/library specific imports.
from ...utils.abs_data import AbsData

class PCA(AbsData):
    """
    Wrapper class for performing Principal Component Analysis (PCA)
    on a specified subset of a DataFrame.
    """

    def __init__(self, n_components, data, columns):
        """
        Initializes the PCA extractor.

        Args:
            n_components (int): Number of principal components to retain.
            data (pd.DataFrame): Input dataset.
            columns (list): List of column names to apply PCA on.
        """
        self.data = data
        self.columns = columns
        self.n_components = n_components

    def extract(self):
        """
        Executes the PCA process and returns the results.

        Returns:
            dict: A dictionary containing:
                - 'explained_variance': List of explained variance ratios.
                - 'pca_json': JSON representation of principal components.
                - 'loadings_pca_json': JSON representation of loadings.
        """
        self.n_components = min(self.n_components, len(self.data))

        if self.n_components > 0:
            pca_result = self._pca()
            explained_variance = pca_result['explained_variance'].tolist()
        else:
            pca_result = None
            explained_variance = None

        # Optionally label the PCA components with original labels
        pca_result = self._label_dataframe(pca_result)

        # Convert to JSON format
        pca_json = pca_result['components'].to_json(orient='records') if pca_result else None
        loadings_pca_json = pca_result['loadings'].to_json(orient='records') if pca_result else None

        return {
            'explained_variance': explained_variance,
            'pca_json': pca_json,
            'loadings_pca_json': loadings_pca_json,
            'top_contributors': pca_result['top_contributors']
        }

    def _pca(self):
        """
        Applies PCA on standardized selected columns.

        Returns:
            dict: Contains the PCA components, explained variance,
                  fitted model, feature loadings and top contributors.
        """
        # Select and standardize the data
        selected_data = self.data[self.columns]
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(selected_data)

        # Fit PCA
        pca = SKPCA(n_components=self.n_components)
        principal_components = pca.fit_transform(scaled_data)

        # Loadings: contribution of each feature to each PC
        loadings = pd.DataFrame(
            pca.components_.T,
            index=self.columns,
            columns=[f'PC{i+1}' for i in range(self.n_components)]
        )

        top_contributors = self._get_top_contributors(loadings)

        component_names = [f'PC{i+1}' for i in range(self.n_components)]
        components_df = pd.DataFrame(principal_components, columns=component_names)

        return {
            'components': components_df,
            'explained_variance': pca.explained_variance_ratio_,
            'pca_model': pca,
            'loadings': loadings,
            'top_contributors': top_contributors,
        }

    def _label_dataframe(self, result):
        """
        Adds original labels to the PCA components if present.

        Args:
            result (dict): Dictionary containing PCA result DataFrames.

        Returns:
            dict: Updated dictionary with labels added to 'components', if available.
        """
        if result and 'label' in self.data.columns:
            result['components']['label'] = self.data['label'].reset_index(drop=True)

        return result

    def _get_top_contributors(self, loadings):
        """
        Finds the top contributing feature (highest absolute loading) for each principal component.

        Args:
            loadings (pd.DataFrame): DataFrame containing PCA loadings with features as rows
                                     and principal components as columns.

        Returns:
            top_contributors (list): A list containing the feature name (str) 
            that has the highest absolute loading for each principal component.
        """
        top_contributors = []

        for component in loadings.columns:
            # Find the feature with the maximum absolute loading for this component
            top_feature = loadings[component].abs().idxmax()
            top_contributors.append(top_feature)

        return top_contributors

