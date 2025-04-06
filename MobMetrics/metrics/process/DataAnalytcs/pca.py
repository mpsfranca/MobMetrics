import pandas as pd
from sklearn.decomposition import PCA as SKPCA
from sklearn.preprocessing import StandardScaler
from ...utils.abs_data import AbsData


class PCA(AbsData):
    """
    PCA wrapper class to apply Principal Component Analysis
    on selected columns of a dataset.
    """

    def __init__(self, data, columns, n_components):
        """
        Initialize the PCA extractor.

        Parameters:
        - data (pd.DataFrame): The input DataFrame.
        - columns (list): List of column names to apply PCA on.
        - n_components (int): Number of principal components to retain.
        """
        self.data = data
        self.columns = columns
        self.n_components = n_components

    def extract(self):
        """
        Performs PCA on the selected columns of the dataset.

        Returns:
        dict: A dictionary containing:
            - 'components': DataFrame with principal components.
            - 'explained_variance': Array of explained variance ratio.
            - 'pca_model': The fitted PCA model object.
        """
        # Select only the specified columns
        selected_data = self.data[self.columns]

        # Standardize the data before applying PCA
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(selected_data)

        # Apply PCA
        pca = SKPCA(n_components=self.n_components)
        principal_components = pca.fit_transform(scaled_data)

        # Create a DataFrame for the principal components
        component_names = [f'PC{i+1}' for i in range(principal_components.shape[1])]
        components_df = pd.DataFrame(principal_components, columns=component_names)

        return {
            'components': components_df,
            'explained_variance': pca.explained_variance_ratio_,
            'pca_model': pca
        }
