import pandas as pd
import plotly.graph_objects as go

from  ...models import GlobalMetricsModel, MetricsModel


def plot_radar_chart(file_name):
    """
    Gera um radar chart para um único rastro com as métricas especificadas.
    """
    queryset = GlobalMetricsModel.objects.filter(file_name=file_name).values(
        'num_contacts',
        'avg_travel_time',
        'total_num_journeys',
        'total_avg_journey_distance',
        'total_avg_journey_avg_speed',
        'total_avg_journey_time',
        'avg_radius_of_gyration',
        'avg_quadrant_entropy',
        'avg_stay_point_entropy',
        'trajectory_correlation',
        'total_spatial_cover',
        'speed_variation_coefficient',
        'mobility_profile'
    )

    if not queryset.exists():
        return "<h3>No data available for this file</h3>"

    df = pd.DataFrame.from_records(queryset)

    metrics = {
        'num_contacts': "Num. Cont.",
        'total_num_journeys': "Num. Journeys",
        'total_avg_journey_time': "Avg. Trav. Time",
        'total_avg_journey_distance': "Avg. Trav. Dist.",
        'total_avg_journey_avg_speed': "Avg. Trav. Spd.",
        'total_spatial_cover': "Spt. Cover.",
        'mobility_profile': "Mob. Prof."
    }

    manual_max = {
        'num_contacts': 6,
        'total_num_journeys': 1000,
        'total_avg_journey_time': 1200,
        'total_avg_journey_distance': 300,
        'total_avg_journey_avg_speed': 1,
        'total_spatial_cover': 360,
        'mobility_profile': 0.6
    }

    normalized = []
    for metric in metrics.keys():
        value = df.iloc[0][metric]
        max_value = manual_max.get(metric, 1)

        norm_value = value / max_value if max_value != 0 else 0
        norm_value = min(max(norm_value, 0), 1)
        normalized.append(norm_value)

    labels = list(metrics.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=normalized,
        theta=labels,
        fill='toself',
        name=df.iloc[0]['fileName'] if 'fileName' in df.columns else 'Trace'
    ))

    fig.update_layout(
        width=480,
        height=480,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showticklabels=True,
                tickfont=dict(color="black")
            )
        ),
        showlegend=False,
        title=f"Mobility Profile for {file_name}",
        font=dict(
            color="black"
        )
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
