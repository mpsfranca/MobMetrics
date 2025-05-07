import pandas as pd
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from ...utils.abs_data import AbsData


class tSNE(AbsData):
    def __init__(self, n_components, perplexity ,data, columns):
        self.data = data
        self.columns = columns
        self.n_components = n_components
        self.perplexity = perplexity

    def extract(self):
        """
        Function to perform t-SNE (t-Distributed Stochastic Neighbor Embedding).

        Parameters:
        n_components (int): The number of components to embed.
        perplexity (float): The perplexity parameter for t-SNE.
        data (DataFrame): The input data for the analysis.
        columns (list): The list of columns from the data to be considered for t-SNE.

        Returns:
        str: JSON representation of the t-SNE components.
        """
        self.n_components = min(self.n_components, len(self.columns))  # Ensures the number of components does not exceed the number of columns

        if self.n_components > 0:
            # Perform t-SNE
            tsne_result = self.tsne()
        else:
            tsne_result = None
        
        # Label the t-SNE results (presumably adds the components to the data frame)
        tsne_result = self.label_dataframe(tsne_result)

        # Convert the components to JSON
        tsne_json = tsne_result['components'].to_json(orient='records') if tsne_result else None

        return tsne_json             

    def tsne(self):
        print("Colunas no DataFrame:", self.data.columns.tolist())
        print("Colunas requisitadas:", self.columns)

        selected_data = self.data[self.columns]
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(selected_data)

        n_samples = scaled_data.shape[0]
        effective_perplexity = min(self.perplexity, max(1, n_samples - 1))

        tsne = TSNE(n_components=self.n_components, perplexity=effective_perplexity, random_state=42)
        tsne_components = tsne.fit_transform(scaled_data)

        component_names = [f'TSNE{i+1}' for i in range(tsne_components.shape[1])]
        components_df = pd.DataFrame(tsne_components, columns=component_names)

        return {
            'components': components_df
        }

    def label_dataframe(self, result):
        """
        Function to add labels on the results from data frame analysis
        """

        if 'label' in self.data.columns:
            if result: result['components']['label'] = self.data['label'].reset_index(drop=True)

        return result