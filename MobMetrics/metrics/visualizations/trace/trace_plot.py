import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from  ...models import TraceModel, StayPointModel


def plot_trace_entities(file_name, max_points=5000):
    """
    Generates an interactive scatterplot of traces using Plotly (with colors differentiating the entities).

    Args:
        file_name (str): The file_name filter to retrieve traces.
        max_points (int): Maximum number of points to plot.

    Returns:
        str: HTML string of the Plotly figure to embed in a webpage.
    """
    queryset = TraceModel.objects.filter(file_name=file_name).values(
        'entity_id', 'x', 'y', 'timestamp'
    )

    df = pd.DataFrame.from_records(queryset)

    if df.empty:
        return "<p>No data available for this file.</p>"

    if len(df) > max_points:
        df = df.sample(n=max_points, random_state=42)

    fig = px.scatter(
        df,
        x='x',
        y='y',
        color=df['entity_id'].astype(str),
        hover_data=['entity_id', 'timestamp'],
        title=f"Trace Scatter Plot - {file_name}",
        labels={'x': 'X', 'y': 'Y', 'entity_id': 'Entity ID'}
    )

    fig.update_layout(
        width=480,
        height=480,
        legend_title="Entity ID",
        template="plotly_white"
    )

    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return html_str

def plot_trace_in_time(file_name, entity_id=0):
    """
    Generates an interactive scatterplot for a single entity,
    with color representing the timestamp (time progression).

    Args:
        file_name (str): The file_name to filter the trace data.
        entity_id (int): The entity ID to plot.

    Returns:
        str: HTML string of the Plotly figure to embed in a webpage.
    """
    queryset = TraceModel.objects.filter(
        file_name=file_name,
        entity_id=entity_id
    ).values('x', 'y', 'timestamp')

    df = pd.DataFrame.from_records(queryset)

    if df.empty:
        return f"<p>No data available for entity {entity_id} in file {file_name}.</p>"

    df = df.sort_values('timestamp')

    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='timestamp',
        color_continuous_scale='Viridis',
        hover_data=['timestamp'],
        title=f"Entity {entity_id} - Trace Over Time",
        labels={'x': 'X', 'y': 'Y', 'timestamp': 'Time'}
    )

    fig.update_layout(
        width=480,
        height=480,
        template="plotly_white",
        coloraxis_colorbar=dict(
            title="Timestamp",
            tickformat=".0f"
        )
    )

    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return html_str

def plot_stay_points(file_name, highlight_spId=1):
    """
    Generates a scatter plot of stay points, highlighting a selected spId.

    Args:
        df (pd.DataFrame): DataFrame with columns ['spId', 'x', 'y'].
        highlight_spId (int): The spId to highlight.

    Returns:
        plotly.graph_objects.Figure: Scatter plot figure.
    """
    queryset = StayPointModel.objects.filter(file_name=file_name).values(
        'stay_point_id', 'x_center', 'y_center'
    )

    df_plot = pd.DataFrame.from_records(queryset)

    if df_plot.empty:
        raise ValueError("DataFrame is empty or does not contain enough points.")

    # Separa os pontos destacados e não destacados
    df_highlight = df_plot[df_plot['stay_point_id'] == highlight_spId]
    df_others = df_plot[df_plot['stay_point_id'] != highlight_spId]

    fig = go.Figure()

    # Plot dos outros stay points (cinza)
    fig.add_trace(go.Scatter(
        x=df_others['x_center'],
        y=df_others['y_center'],
        mode='markers',
        marker=dict(
            color='lightgray',
            size=10,
            line=dict(width=0)
        ),
        hovertext=df_others['stay_point_id'],
        hoverinfo='text',
        name='Other Stay Points'
    ))

    # Plot do stay point destacado (vermelho)
    fig.add_trace(go.Scatter(
        x=df_highlight['x_center'],
        y=df_highlight['y_center'],
        mode='markers',
        marker=dict(
            color='red',
            size=12,
            line=dict(width=0)
        ),
        hovertext=df_highlight['stay_point_id'],
        hoverinfo='text',
        name=f'Stay Point {highlight_spId}'
    ))

    fig.update_layout(
        width=480,
        height=480,
        template="plotly_white",
        title=f'Stay Points Scatter Plot - Highlight spId {highlight_spId}',
        xaxis=dict(title='X'),
        yaxis=dict(title='Y'),
        showlegend=False,
        font=dict(color='black')
    )

    return fig.to_html(full_html=False)
