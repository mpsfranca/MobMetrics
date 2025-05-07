import pandas as pd
from sklearn.decomposition import PCA as SKPCA
from sklearn.preprocessing import StandardScaler
from ...utils.abs_data import AbsData


class PCA(AbsData):
    """
    PCA wrapper class to apply Principal Component Analysis
    on selected columns of a dataset.
    """

    def __init__(self, n_components, data, columns):
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
        self.n_components = min(self.n_components, len(self.columns))  # Ensures the number of components does not exceed the number of columns

        if self.n_components > 0:
            # Perform PCA
            pca_result = self.pca()

            explained_variance = pca_result['explained_variance'].tolist()
        else:
            pca_result = explained_variance = None
        
        # Label the PCA results (presumably adds the components to the data frame)
        pca_result = self.label_dataframe(pca_result)

        # Convert the components and loadings to JSON
        pca_json = pca_result['components'].to_json(orient='records') if pca_result else None
        loadings_pca_json = pca_result['loadings'].to_json(orient='records') if pca_result else None

        return {
            'explained_variance': explained_variance, 
            'pca_json': pca_json, 
            'loadings_pca_json': loadings_pca_json
            }
    

    def pca(self):
        """
        Performs PCA on the selected columns of the dataset.

        Returns:
        dict: A dictionary containing:
            - 'components': DataFrame with principal components.
            - 'explained_variance': Array of explained variance ratio.
            - 'pca_model': The fitted PCA model object.
            - 'loadings': DataFrame where each row corresponds to an original feature and each column to a principal component,
                        representing the contribution (weight) of each original feature to each component.
        """
        # Select only the specified columns
        selected_data = self.data[self.columns]

        # Standardize the data before applying PCA
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(selected_data)

        # Apply PCA
        pca = SKPCA(n_components=self.n_components)
        principal_components = pca.fit_transform(scaled_data)

        # Get the PCA components (loadings) as a DataFrame
        loadings = pd.DataFrame(
            pca.components_.T,
            index=self.columns,
            columns=[f'PC{i+1}' for i in range(self.n_components)]
        )


        component_names = [f'PC{i+1}' for i in range(self.n_components)]

        # Criar DataFrame com os componentes principais renomeados
        components_df = pd.DataFrame(principal_components, columns=component_names)

        return {
            'components': components_df,
            'explained_variance': pca.explained_variance_ratio_,
            'pca_model': pca,
            'loadings': loadings
        }

    
    def label_dataframe(self, result):
        """
        Function to add labels on the results from data frame analysis
        """

        if 'label' in self.data.columns:
            if result: result['components']['label'] = self.data['label'].reset_index(drop=True)

        return result
