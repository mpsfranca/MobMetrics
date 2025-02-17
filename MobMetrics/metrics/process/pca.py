from sklearn.decomposition import PCA  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt #type: ignore
import seaborn as sns #type: ignore
from ..models import MetricsModel

class CalculatePCA:
    def __init__(self):
        pass

    def extract(self):
        # Calcula o PCA
        pca_result, explained_variance = self.calculo()
 
        return pca_result

    def calculo(self):
        # Obtendo os dados numéricos do modelo, incluindo a label
        metrics_data = MetricsModel.objects.all().values(
            'label', 'TTrvT', 'TTrvD', 'TTrvAS', 
            'x_center', 'y_center', 'z_center', 'radius', 
            'avg_travel_time', 'avg_travel_distance', 'avg_travel_avg_speed'
        )

        # Convertendo os dados para um DataFrame
        df = pd.DataFrame(metrics_data)

        # Preenchendo valores nulos com a média das colunas
        df.fillna(df.mean(), inplace=True)

        # Separando as variáveis numéricas (sem a label) e a label
        features = df.drop('label', axis=1)
        labels = df['label']

        # Normalizando os dados (apenas as variáveis numéricas)
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(features)

        # Aplicando PCA
        pca = PCA(n_components=2)  # Número de componentes principais desejados
        pca_result = pca.fit_transform(scaled_data)

        # Criando um DataFrame para os resultados do PCA, incluindo a label
        pca_df = pd.DataFrame(pca_result, columns=['PC1', 'PC2'])
        pca_df['label'] = labels  # Adicionando as labels de volta

        print(pca_df)
        # Retornando os resultados
        return pca_df, pca.explained_variance_ratio_
