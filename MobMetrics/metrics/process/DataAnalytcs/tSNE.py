import pandas as pd
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from ...utils.abs_data import AbsData


class tSNE(AbsData):
    def __init__(self, data, columns, n_components=2, perplexity=30):
        self.data = data
        self.columns = columns
        self.n_components = n_components
        self.perplexity = perplexity

    def extract(self):
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
