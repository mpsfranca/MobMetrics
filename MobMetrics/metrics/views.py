from django.shortcuts import render
from django.contrib import messages

import pandas as pd

import json
from django.core.serializers.json import DjangoJSONEncoder

from .models import ConfigModel, MetricsModel, TravelsModel, StayPointModel, VisitModel, ContactModel, QuadrantEntropyModel, GlobalMetricsModel
from .forms import UploadForm, FileNameForm
from .process.factory import Factory
from .process.format import Format
from .process.DataAnalytcs.pca import PCA
from .process.DataAnalytcs.tSNE import tSNE

def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            trace_file, parameters = get_data(form)

            if ConfigModel.objects.filter(fileName=parameters[4]).exists():
                messages.warning(request, "A file with the same name already exists.")
                return render(request, 'upload/form.html', {'form': form})

            trace_file = pd.read_csv(trace_file)
            trace_file = Format(trace_file).extract()

            create_config_model(parameters)

            Factory(trace_file, parameters).extract()

            return render(request, 'success/success.html', {'form': FileNameForm()})
    else:
        form = UploadForm()

    return render(request, 'upload/form.html', {'form': form})

def delete_view(request):
    if request.method == 'POST':
        form = FileNameForm(request.POST)
        if form.is_valid():
            file_name = form.cleaned_data['file_name']

            models = [ConfigModel, MetricsModel, TravelsModel, StayPointModel, VisitModel, ContactModel, QuadrantEntropyModel, GlobalMetricsModel]
            for model in models:
                model.objects.filter(fileName=file_name).delete()
            
            return render(request, 'success/success.html', {'form': FileNameForm()})
    
    return render(request, 'success/success.html', {'form': FileNameForm()})


def data_analytics_view(request):

    metrics_qs = MetricsModel.objects.filter()
    global_metrics_qs = GlobalMetricsModel.objects.filter()

    metrics_df = pd.DataFrame.from_records(metrics_qs.values())
    global_metrics_df = pd.DataFrame.from_records(global_metrics_qs.values())

    result_metrics = {}
    result_global = {}
    tsne_metrics_result = {}
    tsne_global_result = {}

    if not metrics_df.empty and not global_metrics_df.empty:
        columns_metrics = [
            'TTrvT', 'TTrvD', 'TTrvAS', 'radius', 'numStayPointsVisits', 'avgTimeVisit',
            'num_travels', 'avg_travel_time', 'avg_travel_distance', 'avg_travel_avg_speed'
        ]

        columns_global = [
            'avgTTrvT', 'avgTTrvD', 'avgTTrvAS', 'numStayPoints', 'avgNumStayPointsVisitsPerEtity', 'NumStayPointsVisits',
            'avgStayPointEntropy', 'avgQuadrantEntropy', 'numContacts', 'num_travels', 'avg_travel_time', 'avg_travel_distance', 'avg_travel_avg_speed'
        ]

        # PCA
        pca_metrics = PCA(metrics_df, columns_metrics, 2)
        result_metrics = pca_metrics.extract()

        pca_global = PCA(global_metrics_df, columns_global, 2)
        result_global = pca_global.extract()

        # t-SNE
        tsne_metrics = tSNE(metrics_df, columns_metrics, n_components=2)
        tsne_metrics_result = tsne_metrics.extract()

        tsne_global = tSNE(global_metrics_df, columns_global, n_components=2)
        tsne_global_result = tsne_global.extract()

        if 'label' in metrics_df.columns:
            result_metrics['components']['label'] = metrics_df['label'].reset_index(drop=True)
            tsne_metrics_result['components']['label'] = metrics_df['label'].reset_index(drop=True)

        if 'label' in global_metrics_df.columns:
            result_global['components']['label'] = global_metrics_df['label'].reset_index(drop=True)
            tsne_global_result['components']['label'] = global_metrics_df['label'].reset_index(drop=True)

    return render(request, 'success/success.html', {
        'form': FileNameForm(),
        'pca_metrics': result_metrics.get('components').to_json(orient='records'),
        'pca_global': result_global.get('components').to_json(orient='records'),
        'explained_metrics': json.dumps(result_metrics.get('explained_variance', []).tolist()),
        'explained_global': json.dumps(result_global.get('explained_variance', []).tolist()),
        'tsne_metrics': tsne_metrics_result.get('components').to_json(orient='records'),
        'tsne_global': tsne_global_result.get('components').to_json(orient='records'),
    })




def get_data(form):
    trace_file = form.cleaned_data['trace']
    distance_threshold = form.cleaned_data['distance_threshold']
    radius_threshold = form.cleaned_data['radius_threshold']
    is_geographical_coordinates = form.cleaned_data['is_geographical_coordinates']
    time_threshold = form.cleaned_data['time_threshold']
    quadrant_size = form.cleaned_data['quadrant_size']

    name = form.cleaned_data['name']
    label = form.cleaned_data['label']

    parameters = (distance_threshold, time_threshold, radius_threshold, quadrant_size, name, label, is_geographical_coordinates)

    return trace_file, parameters

def create_config_model(parameters):
    ConfigModel.objects.create(
        fileName=parameters[4],
        label=parameters[5],
        isGeographicalCoordinates = parameters[6],
        distanceThreshold=parameters[0],
        timeThreshold=parameters[1],
        radiusThreshold=parameters[2],
        quadrantSize=parameters[3],
    )

import zipfile
import os
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render
from .models import ConfigModel, MetricsModel, TravelsModel, StayPointModel, VisitModel, ContactModel, QuadrantEntropyModel, GlobalMetricsModel
from .forms import FileNameForm
import pandas as pd

def download_zip_view(request):
    if request.method == 'POST':
        form = FileNameForm(request.POST)
        if form.is_valid():
            file_name = form.cleaned_data['file_name']

            # Filtrando os modelos pela fileName
            models = {
                'ConfigModel': ConfigModel.objects.filter(fileName=file_name),
                'MetricsModel': MetricsModel.objects.filter(fileName=file_name),
                'TravelsModel': TravelsModel.objects.filter(fileName=file_name),
                'StayPointModel': StayPointModel.objects.filter(fileName=file_name),
                'VisitModel': VisitModel.objects.filter(fileName=file_name),
                'ContactModel': ContactModel.objects.filter(fileName=file_name),
                'QuadrantEntropyModel': QuadrantEntropyModel.objects.filter(fileName=file_name),
                'GlobalMetricsModel': GlobalMetricsModel.objects.filter(fileName=file_name),
            }

            # Criando um arquivo zip em memória
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for model_name, queryset in models.items():
                    if queryset.exists():
                        # Convertendo queryset para DataFrame e depois para CSV
                        df = pd.DataFrame.from_records(queryset.values())
                        csv_buffer = BytesIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_buffer.seek(0)

                        # Adicionando o arquivo CSV ao ZIP
                        zip_file.writestr(f'{model_name}.csv', csv_buffer.read())

            # Preparando a resposta HTTP com o arquivo ZIP
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={file_name}.zip'

            return response

    else:
        form = FileNameForm()

    return render(request, 'success/success.html', {'form': form})
