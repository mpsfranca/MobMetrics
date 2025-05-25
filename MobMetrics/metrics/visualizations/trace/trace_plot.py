import plotly.express as px
import pandas as pd

from  ...models import TraceModel


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
        width=800,
        height=600,
        legend_title="Entity ID",
        template="plotly_white"
    )

    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return html_str

def plot_trace_in_time(file_name, entity_id):
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
        width=800,
        height=600,
        template="plotly_white",
        coloraxis_colorbar=dict(
            title="Timestamp",
            tickformat=".0f"
        )
    )

    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return html_str
