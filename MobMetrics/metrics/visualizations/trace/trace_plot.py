import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from  ...models import TraceModel, StayPointModel

def plot_trace_entities(file_name, max_points=5000, is_geographical=False):
    queryset = TraceModel.objects.filter(file_name=file_name).values(
        'entity_id', 'x', 'y', 'timestamp'
    )

    df = pd.DataFrame.from_records(queryset)

    if df.empty:
        return "<p>No data available for this file.</p>"

    if len(df) > max_points:
        df = df.sample(n=max_points, random_state=42)

    if is_geographical:
        fig = px.scatter_mapbox(
            df,
            lat="y",
            lon="x",
            color=df["entity_id"].astype(str),
            hover_data=["entity_id", "timestamp"],
            title=f"Geographical Trace Plot - {file_name}",
            zoom=10,
            height=480,
            width=480
        )
        fig.update_layout(mapbox_style="open-street-map")
    else:
        fig = px.scatter(
            df,
            x="x",
            y="y",
            color=df["entity_id"].astype(str),
            hover_data=["entity_id", "timestamp"],
            title=f"Trace Scatter Plot - {file_name}",
            labels={"x": "X", "y": "Y", "entity_id": "Entity ID"},
            height=480,
            width=480
        )

    fig.update_layout(template="plotly_white", legend_title="Entity ID")

    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def plot_trace_in_time(file_name, entity_id=0, is_geographical=False):
    queryset = TraceModel.objects.filter(
        file_name=file_name,
        entity_id=entity_id
    ).values("x", "y", "timestamp")

    df = pd.DataFrame.from_records(queryset)

    if df.empty:
        return f"<p>No data available for entity {entity_id} in file {file_name}.</p>"

    df = df.sort_values("timestamp")

    if is_geographical:
        fig = px.scatter_mapbox(
            df,
            lat="y",
            lon="x",
            color="timestamp",
            color_continuous_scale="Viridis",
            hover_data=["timestamp"],
            title=f"Entity {entity_id} - Geo Trace Over Time",
            zoom=10,
            height=480,
            width=480
        )
        fig.update_layout(mapbox_style="open-street-map")
    else:
        fig = px.scatter(
            df,
            x="x",
            y="y",
            color="timestamp",
            color_continuous_scale="Viridis",
            hover_data=["timestamp"],
            title=f"Entity {entity_id} - Trace Over Time",
            labels={"x": "X", "y": "Y", "timestamp": "Time"},
            height=480,
            width=480
        )
        fig.update_layout(
            coloraxis_colorbar=dict(title="Timestamp", tickformat=".0f")
        )

    fig.update_layout(template="plotly_white")

    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def plot_stay_points(file_name, highlight_spId=1, is_geographical=False):
    queryset = StayPointModel.objects.filter(file_name=file_name).values(
        "stay_point_id", "x_center", "y_center"
    )

    df_plot = pd.DataFrame.from_records(queryset)

    if df_plot.empty:
        raise ValueError("DataFrame is empty or does not contain enough points.")

    df_highlight = df_plot[df_plot["stay_point_id"] == highlight_spId]
    df_others = df_plot[df_plot["stay_point_id"] != highlight_spId]

    if is_geographical:
        fig = go.Figure()

        fig.add_trace(go.Scattermapbox(
            lat=df_others["y_center"],
            lon=df_others["x_center"],
            mode="markers",
            marker=dict(size=9, color="lightgray"),
            name="Other Stay Points",
            text=df_others["stay_point_id"],
            hoverinfo="text"
        ))

        fig.add_trace(go.Scattermapbox(
            lat=df_highlight["y_center"],
            lon=df_highlight["x_center"],
            mode="markers",
            marker=dict(size=12, color="red"),
            name=f"Stay Point {highlight_spId}",
            text=df_highlight["stay_point_id"],
            hoverinfo="text"
        ))

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=10,
            mapbox_center={"lat": df_plot["y_center"].mean(), "lon": df_plot["x_center"].mean()},
            height=480,
            width=480,
            title=f"Stay Points - Highlight spId {highlight_spId}"
        )
    else:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_others["x_center"],
            y=df_others["y_center"],
            mode="markers",
            marker=dict(color="lightgray", size=10),
            hovertext=df_others["stay_point_id"],
            hoverinfo="text",
            name="Other Stay Points"
        ))

        fig.add_trace(go.Scatter(
            x=df_highlight["x_center"],
            y=df_highlight["y_center"],
            mode="markers",
            marker=dict(color="red", size=12),
            hovertext=df_highlight["stay_point_id"],
            hoverinfo="text",
            name=f"Stay Point {highlight_spId}"
        ))

        fig.update_layout(
            width=480,
            height=480,
            template="plotly_white",
            title=f"Stay Points Scatter Plot - Highlight spId {highlight_spId}",
            xaxis=dict(title="X"),
            yaxis=dict(title="Y"),
            showlegend=False,
            font=dict(color="black")
        )

    return fig.to_html(full_html=False)
