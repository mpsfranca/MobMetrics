import pandas as pd
import plotly.graph_objects as go

from  ...models import GlobalMetricsModel


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
