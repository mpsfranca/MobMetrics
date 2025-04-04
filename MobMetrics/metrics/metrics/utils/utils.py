from math import sqrt

from django.db.models import Avg, Sum, Count
from collections import Counter
from ...models import GlobalMetricsModel, MetricsModel, StayPointModel, QuadrantEntropyModel

def distance(first_point, second_point):
    """
    Calculate the Euclidean distance between two points in 3D space.

    Args:
        first_point (dict): A dictionary with keys 'x', 'y', 'z' representing the coordinates of the first point.
        second_point (dict): A dictionary with keys 'x', 'y', 'z' representing the coordinates of the second point.

    Returns:
        float: The Euclidean distance between the two points.
    """
    return sqrt(
        (second_point['x'] - first_point['x']) ** 2 +
        (second_point['y'] - first_point['y']) ** 2 +
        (second_point['z'] - first_point['z']) ** 2
    )


def global_metrics(file_name):
    # Filtrar métricas e stay points por file_name
    metrics = MetricsModel.objects.filter(fileName=file_name)
    staypoints = StayPointModel.objects.filter(fileName=file_name)
    quadrants = QuadrantEntropyModel.objects.filter(fileName=file_name)

    if not metrics.exists() and not staypoints.exists():
        print(f"Nenhum dado encontrado para o arquivo: {file_name}")
        return

    # Cálculos com MetricsModel
    metrics_agg = metrics.aggregate(
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

    quadrants_agg = quadrants.aggregate(
        avgQuadrantEntropy = Avg('entropy')
    )

    # Label mais frequente no MetricsModel (se existir)
    label_list = list(metrics.values_list('label', flat=True))
    most_common_label = Counter(label_list).most_common(1)
    label = most_common_label[0][0] if most_common_label else ''

    # Cálculos com StayPointModel
    sp_count = staypoints.count()
    sp_agg = staypoints.aggregate(
        NumStayPointsVisits=Sum('numVisits'),
        avgStayPointEntropy=Avg('entropy')
    )

    # Criar ou atualizar GlobalMetricsModel
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

            'numStayPoints': sp_count,
            'avgNumStayPointsVisitsPerEtity': metrics_agg['avgNumStayPointsVisitsPerEtity'] or 0.0,
            'NumStayPointsVisits': sp_agg['NumStayPointsVisits'] or 0,
            'avgStayPointEntropy': sp_agg['avgStayPointEntropy'] or 0.0,

            'num_travels': metrics_agg['num_travels'] or 0,
            'avg_travel_time': metrics_agg['avg_travel_time'] or 0.0,
            'avg_travel_distance': metrics_agg['avg_travel_distance'] or 0.0,
            'avg_travel_avg_speed': metrics_agg['avg_travel_avg_speed'] or 0.0,
            
            'avgQuadrantEntropy': quadrants_agg['avgQuadrantEntropy'] or 0.0,
            'numContacts': 0,
        }
    )
