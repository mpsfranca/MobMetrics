import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def generate_tsne_plot_html(data_frame, tsne_components, n_components, title, color_by='label'):
    """
    Gera um plot de t-SNE (2D ou 3D) com Plotly e retorna o HTML.
    
    Args:
        data_frame (list of dict): Dados processados (ex: [{'TSNE1': 0.1, 'TSNE2': 0.2, 'label': 'A'}, ...]).
        tsne_components (list): Nomes dos componentes t-SNE (e.g., ['TSNE1', 'TSNE2', 'TSNE3']).
        n_components (int): Número de componentes do t-SNE (2 ou 3).
        title (str): Título do gráfico.
        color_by (str): Coluna para colorir os pontos.
    
    Returns:
        str: Código HTML do gráfico Plotly.
    """
    df = pd.DataFrame(data_frame)

    if n_components >= 3:
        fig = px.scatter_3d(
            df,
            x=tsne_components[0],
            y=tsne_components[1],
            z=tsne_components[2],
            color=color_by,
            title=title
        )
        fig.update_layout(
            scene=dict(
                xaxis_title=tsne_components[0],
                yaxis_title=tsne_components[1],
                zaxis_title=tsne_components[2]
            )
        )
    else:
        fig = px.scatter(
            df,
            x=tsne_components[0],
            y=tsne_components[1],
            color=color_by,
            title=title
        )
        fig.update_layout(
            xaxis_title=tsne_components[0],
            yaxis_title=tsne_components[1]
        )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def generate_dbscan_tsne_plot_html(data_frame, tsne_components, n_components, title, color_by='dbscan_cluster'):
    """
    Gera um plot de t-SNE com resultados de DBSCAN (2D ou 3D) com Plotly e retorna o HTML.
    
    Args:
        data_frame (list of dict): Dados processados (ex: [{'TSNE1': 0.1, 'TSNE2': 0.2, 'dbscan_cluster': 0}, ...]).
        tsne_components (list): Nomes dos componentes t-SNE (e.g., ['TSNE1', 'TSNE2', 'TSNE3']).
        n_components (int): Número de componentes do t-SNE (2 ou 3).
        title (str): Título do gráfico.
        color_by (str): Coluna para colorir os pontos (geralmente 'dbscan_cluster').
    
    Returns:
        str: Código HTML do gráfico Plotly.
    """
    df = pd.DataFrame(data_frame)

    if n_components >= 3:
        fig = px.scatter_3d(
            df,
            x=tsne_components[0],
            y=tsne_components[1],
            z=tsne_components[2],
            color=color_by,
            title=title
        )
        fig.update_layout(
            scene=dict(
                xaxis_title=tsne_components[0],
                yaxis_title=tsne_components[1],
                zaxis_title=tsne_components[2]
            )
        )
    else:
        fig = px.scatter(
            df,
            x=tsne_components[0],
            y=tsne_components[1],
            color=color_by,
            title=title
        )
        fig.update_layout(
            xaxis_title=tsne_components[0],
            yaxis_title=tsne_components[1]
        )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')
