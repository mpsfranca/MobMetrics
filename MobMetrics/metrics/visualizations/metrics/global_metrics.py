import pandas as pd
import plotly.graph_objects as go

from  ...models import GlobalMetricsModel, MetricsModel


def plot_radar_chart(file_name):
    queryset = GlobalMetricsModel.objects.filter(file_name=file_name).values(
        'avg_travel_time',
        'avg_travel_distance',
        'avg_radius_of_gyration',
        'avg_quadrant_entropy',
        'avg_stay_point_entropy',
        'trajectory_correlation',
        'speed_variation_coefficient'
    )

    if not queryset.exists():
        return "<h3>No data available for this file</h3>"

    df = pd.DataFrame.from_records(queryset)

    metrics = [
        'avg_travel_time',
        'avg_travel_distance',
        'avg_radius_of_gyration',
        'avg_quadrant_entropy',
        'avg_stay_point_entropy',
        'trajectory_correlation',
        'speed_variation_coefficient'
    ]

    labels = [
        "Avg. Trav. Time",
        "Avg. Trav. Dist.",
        "Rad. of Gyration",
        "Quad. Entropy",
        "Stay Point Entropy",
        "Traj. Correlation",
        "Spd. Var. Coef."
    ]

    normalized_values = (df[metrics] - df[metrics].min()) / (df[metrics].max() - df[metrics].min())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=normalized_values.iloc[0].tolist(),
        theta=labels,
        fill='toself',
        name=file_name
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        width=480,
        height=480,
        title=f"Mobility Profile for {file_name}"
    )

    return fig.to_html(full_html=False)

def plot_count_bars(file_name):
    queryset = GlobalMetricsModel.objects.filter(file_name=file_name).values(
        'num_stay_points',
        'num_contacts',
        'total_num_journeys',
        'total_spatial_cover'
    )

    if not queryset.exists():
        return "<h3>No data available for this file</h3>"

    df = pd.DataFrame.from_records(queryset)

    labels = ['Stay Points', 'Contacts', 'Journeys', 'Spatial Cover']
    values = [
        df['num_stay_points'].iloc[0],
        df['num_contacts'].iloc[0],
        df['total_num_journeys'].iloc[0],
        df['total_spatial_cover'].iloc[0] if df['total_spatial_cover'].notnull().iloc[0] else 0
    ]

    fig = go.Figure([go.Bar(x=labels, y=values)])
    fig.update_layout(title=f"Count Metrics for {file_name}")

    return fig.to_html(full_html=False)

import plotly.express as px

def plot_correlation_heatmap(file_name):
    queryset = GlobalMetricsModel.objects.filter(file_name=file_name).values(
        'avg_travel_time',
        'avg_travel_distance',
        'avg_radius_of_gyration',
        'avg_quadrant_entropy',
        'avg_stay_point_entropy',
        'trajectory_correlation',
        'speed_variation_coefficient'
    )

    if not queryset.exists():
        return "<h3>No data available for this file</h3>"

    df = pd.DataFrame.from_records(queryset)

    corr = df.corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        title=f"Correlation Heatmap for {file_name}",
        aspect="auto"
    )

    return fig.to_html(full_html=False)

def plot_metric_histogram(file_name, metric='avg_travel_distance'):
    queryset = GlobalMetricsModel.objects.filter(file_name=file_name).values(metric)

    if not queryset.exists():
        return f"<h3>No data available for {metric}</h3>"

    df = pd.DataFrame.from_records(queryset)

    fig = go.Figure(data=[go.Histogram(x=df[metric])])
    fig.update_layout(title=f"Distribution of {metric} for {file_name}")

    return fig.to_html(full_html=False)

def plot_travel_distance_comparison(file_name, entity_id):
    """
    Generates a bar plot comparing avg_travel_distance for a given eplot_travel_distance_comparisonntity_id
    against four sequential entity_ids (entity_id + 1 to entity_id + 4).

    The selected entity_id is highlighted with a different color.

    Args:
        df (pd.DataFrame): DataFrame containing columns ['entityId', 'avg_travel_distance']
        entity_id (int): The target entity_id to highlight.

    Returns:
        plotly.graph_objects.Figure: Plotly bar chart figure.
    """
    queryset = MetricsModel.objects.filter(file_name=file_name).values(
        'entity_id',
        'travel_distance'
    )

    if not queryset.exists():
        return "<h3>No data available for this file</h3>"

    df = pd.DataFrame.from_records(queryset)

    selected_ids = [entity_id + i for i in range(5)]
    df_plot = df[df['entity_id'].isin(selected_ids)].copy()

    if df_plot.empty:
        raise ValueError(f"No data available for entity_id {entity_id} and nearby entities.")

    df_plot['color'] = df_plot['entity_id'].apply(
        lambda x: 'rgba(31, 119, 180, 1)' if x == entity_id else 'rgba(200, 200, 200, 0.8)'
    )

    fig = px.bar(
        df_plot,
        x='entity_id',
        y='travel_distance',
        title=f'Average Travel Distance - Entity {entity_id} vs Others',
        labels={'entity_id': 'Entity ID', 'travel_distance': 'Avg Travel Distance'},
    )

    fig.update_traces(
        marker_color=df_plot['color'],
        text=df_plot['travel_distance'].round(2),
        textposition='outside'
    )

    fig.update_layout(
        template='plotly_white',
        width=500,
        height=500,
        font=dict(color='black'),
        showlegend=False,
        uniformtext_minsize=8,
        uniformtext_mode='show',
        yaxis=dict(title='Avg Travel Distance'),
        xaxis=dict(title='Entity ID')
    )

    return fig.to_html(full_html=False)
