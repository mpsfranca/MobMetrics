import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def generate_pca_plot_html(data_frame, contributors, n_components, title, color_by='label'):
    """
    Gera um plot de PCA (2D ou 3D) com Plotly e retorna o HTML.
    
    Args:
        data_frame (list of dict): Processed data.
        contributors (list): Names of the main components.
        n_components (int): Number of PCA components.
        title (str): Graph title.
        color_by (str): Column to color the data.
    
    Returns:
        str: Plotly chart HTML code.
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
    Generates a bar chart of the explained variance with Plotly and returns the HTML.
    
    Args:
        explained_variance_ratio (list): List of explained variance values.
        title (str): Graph title.
        
    Returns:
        str: Plotly chart HTML code.
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
    Generates a PCA plot with DBSCAN results (2D or 3D) with Plotly and returns the HTML.
    
    Args:
        data_frame (list of dict): Processed data.
        contributors (list): Names of main components.
        n_components (int): Number of PCA components (2 or 3).
        title (str): Graph title.
        color_by (str): Column to color the dots (defaults as 'dbscan_cluster').
    
    Returns:
        str: Plotly chart HTML code.
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
