import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def generate_pca_plot_html(data_frame, contributors, n_components, title, color_by='label'):
    """
    Gera um plot de PCA (2D ou 3D) com Plotly e retorna o HTML.
    
    Args:
        data_frame (list of dict): Dados processados (ex: [{'PC1': 0.1, 'PC2': 0.2, 'label': 'A'}, ...]).
        contributors (list): Nomes dos componentes principais (e.g., ['PC1', 'PC2', 'PC3']).
        n_components (int): Número de componentes do PCA (2 ou 3).
        title (str): Título do gráfico.
        color_by (str): Coluna para colorir os pontos.
    
    Returns:
        str: Código HTML do gráfico Plotly.
    """
    df = pd.DataFrame(data_frame)

    if n_components >= 3:
        fig = px.scatter_3d(
            df,
            x=contributors[0],
            y=contributors[1],
            z=contributors[2],
            color=color_by,
            title=title
        )
        fig.update_layout(
            scene=dict(
                xaxis_title=contributors[0],
                yaxis_title=contributors[1],
                zaxis_title=contributors[2]
            )
        )
    else:
        fig = px.scatter(
            df,
            x=contributors[0],
            y=contributors[1],
            color=color_by,
            title=title
        )
        fig.update_layout(
            xaxis_title=contributors[0],
            yaxis_title=contributors[1]
        )
    
    # Retorna o HTML completo do gráfico Plotly
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def generate_explained_variance_plot_html(explained_variance_ratio, title='Explained Variance Components'):
    """
    Gera um gráfico de barras da variância explicada com Plotly e retorna o HTML.
    
    Args:
        explained_variance_ratio (list): Lista de valores da variância explicada.
        title (str): Título do gráfico.
        
    Returns:
        str: Código HTML do gráfico Plotly.
    """
    components = [f'PC{i + 1}' for i in range(len(explained_variance_ratio))]
    
    fig = go.Figure(data=[
        go.Bar(
            x=components,
            y=explained_variance_ratio,
            marker_color='rgba(100, 149, 237, 0.7)'
        )
    ])
    fig.update_layout(
        title=title,
        xaxis_title='Principal Components',
        yaxis_title='Explained Variance'
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def generate_dbscan_pca_plot_html(data_frame, contributors, n_components, title, color_by='dbscan_cluster'):
    """
    Gera um plot de PCA com resultados de DBSCAN (2D ou 3D) com Plotly e retorna o HTML.
    
    Args:
        data_frame (list of dict): Dados processados (ex: [{'PC1': 0.1, 'PC2': 0.2, 'dbscan_cluster': 0}, ...]).
        contributors (list): Nomes dos componentes principais (e.g., ['PC1', 'PC2', 'PC3']).
        n_components (int): Número de componentes do PCA (2 ou 3).
        title (str): Título do gráfico.
        color_by (str): Coluna para colorir os pontos (geralmente 'dbscan_cluster').
    
    Returns:
        str: Código HTML do gráfico Plotly.
    """
    df = pd.DataFrame(data_frame)

    if n_components >= 3:
        fig = px.scatter_3d(
            df,
            x=contributors[0],
            y=contributors[1],
            z=contributors[2],
            color=color_by,
            title=title
        )
        fig.update_layout(
            scene=dict(
                xaxis_title=contributors[0],
                yaxis_title=contributors[1],
                zaxis_title=contributors[2]
            )
        )
    else:
        fig = px.scatter(
            df,
            x=contributors[0],
            y=contributors[1],
            color=color_by,
            title=title
        )
        fig.update_layout(
            xaxis_title=contributors[0],
            yaxis_title=contributors[1]
        )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')
