import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def generate_tsne_plot_html(data_frame, tsne_components, n_components, title, color_by='label'):
    """
    Generates a t-SNE plot with Plotly and returns the HTML of the graph.
    
    Args:
        data_frame (list of dict): Processed data.
        tsne_components (list): Names of the t-SNE components).
        n_components (int): Number of t-SNE components.
        title (str): Graph title.
        color_by (str): Column to color the graph.
    
    Returns:
        str: Plotly chart HTML code.
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
    Generates a t-SNE plot with DBSCAN results with Plotly and returns the HTML.
    
    Args:
        data_frame (list of dict): Processed data.
        tsne_components (list): Names of the t-SNE components.
        n_components (int): Number of t-SNE components.
        title (str): Graph title.
        color_by (str): Column to color the graph.
    
    Returns:
        str: Plotly chart HTML code.
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
