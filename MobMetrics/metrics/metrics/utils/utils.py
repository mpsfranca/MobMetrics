# Related third party imports.
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from django.db.models import Avg, Sum

# Local application/library specific imports.
from ...models import (
    GlobalMetricsModel,
    MetricsModel,
    StayPointModel,
    QuadrantEntropyModel,
    ContactModel
)

def distance(point_a, point_b, is_geo_coords):
    """
    Computes the distance between two 3D points.
    Uses Haversine formula for horizontal distance if coordinates are geographical.

    Args:
        point_a (dict): Dictionary with keys 'x', 'y', 'z' representing the first point.
        point_b (dict): Dictionary with keys 'x', 'y', 'z' representing the second point.
        is_geo_coords (bool): Whether the coordinates are geographical (latitude/longitude).

    Returns:
        float: The 3D distance between the two points.
    """
    if is_geo_coords:
        earth_radius = 6371000  # in meters

        lat1 = radians(point_a['y'])
        lon1 = radians(point_a['x'])
        lat2 = radians(point_b['y'])
        lon2 = radians(point_b['x'])

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        horizontal_distance = earth_radius * c

        delta_z = point_b['z'] - point_a['z']
        return sqrt(horizontal_distance ** 2 + delta_z ** 2)

    return sqrt(
        (point_b['x'] - point_a['x']) ** 2 +
        (point_b['y'] - point_a['y']) ** 2 +
        (point_b['z'] - point_a['z']) ** 2
    )

def compute_global_metrics(file_name):
    """
    Aggregates and stores global mobility metrics for a given file.

    Args:
        file_name (str): Name of the file to compute metrics for.
    """
    metrics_qs = MetricsModel.objects.filter(file_name=file_name)
    staypoints_qs = StayPointModel.objects.filter(file_name=file_name)
    quadrants_qs = QuadrantEntropyModel.objects.filter(file_name=file_name)
    contacts_qs = ContactModel.objects.filter(file_name=file_name)

    metrics_agg = metrics_qs.aggregate(
        avg_travel_time = Avg('travel_time'),
        avg_travel_distance = Avg('travel_distance'),
        avg_travel_avg_speed = Avg('travel_avg_speed'),
        avg_x_center = Avg('x_center'),
        avg_y_center = Avg('y_center'),
        avg_z_center = Avg('z_center'),
        avg_radius_of_gyration = Avg('radius_of_gyration'),
        total_num_journeys = Sum('num_journeys'),
        total_avg_journey_time = Avg('avg_journey_time'),
        total_avg_journey_distance = Avg('avg_journey_distance'),
        total_avg_journey_avg_speed = Avg('avg_journey_avg_speed'),
        avg_num_stay_points_visits = Avg('stay_points_visits'),
    )

    staypoints_agg = staypoints_qs.aggregate(
        stay_points_visits = Sum('num_visits'),
        avg_stay_point_entropy = Avg('entropy'),
    )

    quadrants_agg = quadrants_qs.aggregate(
        avg_quadrant_entropy = Avg('entropy')
    )

    label = metrics_qs.first().label if metrics_qs.exists() else ''
    num_contacts = contacts_qs.count()

    GlobalMetricsModel.objects.update_or_create(
        file_name = file_name,
        defaults = {
            'label': label,
            'avg_travel_time': metrics_agg['avg_travel_time'] or 0.0,
            'avg_travel_distance': metrics_agg['avg_travel_distance'] or 0.0,
            'avg_travel_avg_speed': metrics_agg['avg_travel_avg_speed'] or 0.0,
            'avg_x_center': metrics_agg['avg_x_center'] or 0.0,
            'avg_y_center': metrics_agg['avg_y_center'] or 0.0,
            'avg_z_center': metrics_agg['avg_z_center'] or 0.0,
            'avg_radius_of_gyration': metrics_agg['avg_radius_of_gyration'] or 0.0,
            'total_num_journeys': metrics_agg['total_num_journeys'] or 0,
            'total_avg_journey_time': metrics_agg['total_avg_journey_time'] or 0.0,
            'total_avg_journey_distance': metrics_agg['total_avg_journey_distance'] or 0.0,
            'total_avg_journey_avg_speed': metrics_agg['total_avg_journey_avg_speed'] or 0.0,
            'avg_num_stay_points_visits': metrics_agg['avg_num_stay_points_visits'] or 0.0,
            'num_stay_points': staypoints_qs.count(),
            'stay_points_visits': staypoints_agg['stay_points_visits'] or 0,
            'avg_stay_point_entropy': staypoints_agg['avg_stay_point_entropy'] or 0.0,
            'avg_quadrant_entropy': quadrants_agg['avg_quadrant_entropy'] or 0.0,
            'num_contacts': num_contacts,
            'mobility_profile': _calculate_mobility_profile(metrics_qs)
        }
    )

def _calculate_mobility_profile(metrics_qs):
    """
    Computes a normalized mobility profile score for a set of mobility metrics.

    Args:
        metrics_qs (QuerySet): Django QuerySet of MetricsModel instances.

    Returns:
        float: Normalized scalar score representing the mobility profile.
    """
    vectors = []

    for metrics in metrics_qs:
        raw_values = [
            getattr(metrics, 'travel_time', 0.0) or 0.0,
            getattr(metrics, 'travel_distance', 0.0) or 0.0,
            getattr(metrics, 'travel_avg_speed', 0.0) or 0.0,
            getattr(metrics, 'num_journeys', 0.0) or 0.0,
            getattr(metrics, 'avg_journey_time', 0.0) or 0.0,
            getattr(metrics, 'avg_journey_distance', 0.0) or 0.0,
            getattr(metrics, 'avg_journey_avg_speed', 0.0) or 0.0,
            getattr(metrics, 'stay_points_visits', 0.0) or 0.0,
        ]

        min_val = min(raw_values)
        max_val = max(raw_values)
        if max_val == min_val:
            normalized = [0.0] * len(raw_values)
        else:
            normalized = [(val - min_val) / (max_val - min_val) for val in raw_values]

        vectors.append(normalized)

    if not vectors:
        return 0.0

    avg_vector = np.mean(vectors, axis=0)
    profile_score = float(np.mean(avg_vector))

    return round(profile_score, 4)
