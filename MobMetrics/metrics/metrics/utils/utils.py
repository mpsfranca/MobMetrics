from math import sqrt,radians, sin, cos, sqrt, atan2
from django.db.models import Avg, Sum
from ...models import (
    GlobalMetricsModel,
    MetricsModel,
    StayPointModel,
    QuadrantEntropyModel,
    ContactModel
)

def distance(first_point, second_point, is_geographical_coordinates):

    if is_geographical_coordinates:
        R = 6371000

        lat1 = radians(first_point['y'])
        lon1 = radians(first_point['x'])
        lat2 = radians(second_point['y'])
        lon2 = radians(second_point['x'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        horizontal_distance = R * c

        dz = second_point['z'] - first_point['z']

        return sqrt(horizontal_distance**2 + dz**2)
    
    else:
        return sqrt(
            (second_point['x'] - first_point['x']) ** 2 +
            (second_point['y'] - first_point['y']) ** 2 +
            (second_point['z'] - first_point['z']) ** 2
        )

def globalMetrics(file_name):
    metrics_qs = MetricsModel.objects.filter(fileName=file_name)
    staypoints_qs = StayPointModel.objects.filter(fileName=file_name)
    quadrants_qs = QuadrantEntropyModel.objects.filter(fileName=file_name)
    contacts_qs = ContactModel.objects.filter(fileName=file_name)

    metrics_agg = metrics_qs.aggregate(
        avgTTrvT=Avg('TTrvT'),
        avgTTrvD=Avg('TTrvD'),
        avgTTrvAS=Avg('TTrvAS'),
        avgX_center=Avg('x_center'),
        avgY_center=Avg('y_center'),
        avgZ_center=Avg('z_center'),
        avgRadius=Avg('radius'),
        num_travels=Sum('num_travels'),
        avg_travel_time=Avg('avg_travel_time'),
        avg_travel_distance=Avg('avg_travel_distance'),
        avg_travel_avg_speed=Avg('avg_travel_avg_speed'),
        avgNumStayPointsVisitsPerEtity=Avg('numStayPointsVisits'),
    )

    sp_agg = staypoints_qs.aggregate(
        NumStayPointsVisits=Sum('numVisits'),
        avgStayPointEntropy=Avg('entropy')
    )

    quadrants_agg = quadrants_qs.aggregate(
        avgQuadrantEntropy=Avg('entropy')
    )

    label = metrics_qs.first().label if metrics_qs.exists() else ''
    num_contacts = contacts_qs.count()

    GlobalMetricsModel.objects.update_or_create(
        fileName=file_name,
        defaults={
            'label': label,
            'avgTTrvT': metrics_agg['avgTTrvT'] or 0.0,
            'avgTTrvD': metrics_agg['avgTTrvD'] or 0.0,
            'avgTTrvAS': metrics_agg['avgTTrvAS'] or 0.0,
            'avgX_center': metrics_agg['avgX_center'] or 0.0,
            'avgY_center': metrics_agg['avgY_center'] or 0.0,
            'avgZ_center': metrics_agg['avgZ_center'] or 0.0,
            'avgRadius': metrics_agg['avgRadius'] or 0.0,
            'num_travels': metrics_agg['num_travels'] or 0,
            'avg_travel_time': metrics_agg['avg_travel_time'] or 0.0,
            'avg_travel_distance': metrics_agg['avg_travel_distance'] or 0.0,
            'avg_travel_avg_speed': metrics_agg['avg_travel_avg_speed'] or 0.0,
            'avgNumStayPointsVisitsPerEtity': metrics_agg['avgNumStayPointsVisitsPerEtity'] or 0.0,
            'numStayPoints': staypoints_qs.count(),
            'NumStayPointsVisits': sp_agg['NumStayPointsVisits'] or 0,
            'avgStayPointEntropy': sp_agg['avgStayPointEntropy'] or 0.0,
            'avgQuadrantEntropy': quadrants_agg['avgQuadrantEntropy'] or 0.0,
            'numContacts': num_contacts,
        }
    )
