from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from io import BytesIO
import zipfile
import pandas as pd
import json

from .models import (
    ConfigModel, MetricsModel, TravelsModel, StayPointModel, VisitModel,
    ContactModel, QuadrantEntropyModel, GlobalMetricsModel
)
from .forms import UploadForm, FileNameForm
from .process.factory import Factory
from .process.format import Format
from .process.DataAnalytcs.pca import PCA
from .process.DataAnalytcs.tSNE import tSNE


def dashboard_view(request):
    upload_form = UploadForm()
    file_form = FileNameForm()
    file_names = ConfigModel.objects.values_list('fileName', flat=True).distinct()

    pca_metrics_json, pca_global_json = None, None
    tsne_metrics_json, tsne_global_json = None, None
    explained_metrics, explained_global = [], []

    # Handle form actions
    if request.method == 'POST':
        if 'upload' in request.POST:
            upload_form = UploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                trace_file, parameters = get_data(upload_form)

                if ConfigModel.objects.filter(fileName=parameters[4]).exists():
                    messages.warning(request, "A file with the same name already exists.")
                else:
                    df = pd.read_csv(trace_file)
                    df = Format(df).extract()

                    create_config_model(parameters)
                    Factory(df, parameters).extract()
                    messages.success(request, "Upload and processing completed.")

                    file_names = ConfigModel.objects.values_list('fileName', flat=True).distinct()
        elif 'delete' in request.POST:
            file_name = request.POST.get('fileName')
            if file_name:
                for model in [
                    ConfigModel, MetricsModel, TravelsModel, StayPointModel,
                    VisitModel, ContactModel, QuadrantEntropyModel, GlobalMetricsModel
                ]:
                    model.objects.filter(fileName=file_name).delete()
                messages.success(request, f"Data for '{file_name}' deleted.")
            else:
                messages.error(request, "No file name provided.")

            file_names = ConfigModel.objects.values_list('fileName', flat=True).distinct()

        elif 'download' in request.POST:
            file_name = request.POST.get('fileName')
            if file_name:
                zip_buffer = BytesIO()
                
                # Dicionário de modelos a serem incluídos no zip
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

                # Criando o arquivo ZIP com os dados dos modelos
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for model_name, queryset in models.items():
                        if queryset.exists():
                            df = pd.DataFrame.from_records(queryset.values())
                            csv_buffer = BytesIO()
                            df.to_csv(csv_buffer, index=False)
                            csv_buffer.seek(0)  # Voltando o cursor do buffer para o início
                            zip_file.writestr(f'{model_name}.csv', csv_buffer.read())

                zip_buffer.seek(0)  # Voltando o cursor do buffer para o início
                response = HttpResponse(zip_buffer, content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename={file_name}.zip'
                return response


        elif 'generate_graphs' in request.POST:
            # Perform PCA and t-SNE
            metrics_df = pd.DataFrame.from_records(MetricsModel.objects.all().values())
            global_metrics_df = pd.DataFrame.from_records(GlobalMetricsModel.objects.all().values())

            if not metrics_df.empty and not global_metrics_df.empty:
                columns_metrics = [
                    'TTrvT', 'TTrvD', 'TTrvAS', 'radius', 'numStayPointsVisits', 'avgTimeVisit',
                    'num_travels', 'avg_travel_time', 'avg_travel_distance', 'avg_travel_avg_speed'
                ]
                columns_global = [
                    'avgTTrvT', 'avgTTrvD', 'avgTTrvAS', 'numStayPoints', 'avgNumStayPointsVisitsPerEtity',
                    'NumStayPointsVisits', 'avgStayPointEntropy', 'avgQuadrantEntropy', 'numContacts',
                    'num_travels', 'avg_travel_time', 'avg_travel_distance', 'avg_travel_avg_speed'
                ]

                # PCA
                result_metrics = PCA(metrics_df, columns_metrics, 2).extract()
                result_global = PCA(global_metrics_df, columns_global, 2).extract()
                explained_metrics = result_metrics['explained_variance'].tolist()
                explained_global = result_global['explained_variance'].tolist()

                # t-SNE
                tsne_metrics = tSNE(metrics_df, columns_metrics, n_components=2).extract()
                tsne_global = tSNE(global_metrics_df, columns_global, n_components=2).extract()

                # Add labels
                if 'label' in metrics_df.columns:
                    result_metrics['components']['label'] = metrics_df['label'].reset_index(drop=True)
                    tsne_metrics['components']['label'] = metrics_df['label'].reset_index(drop=True)
                if 'label' in global_metrics_df.columns:
                    result_global['components']['label'] = global_metrics_df['label'].reset_index(drop=True)
                    tsne_global['components']['label'] = global_metrics_df['label'].reset_index(drop=True)

                pca_metrics_json = result_metrics['components'].to_json(orient='records')
                pca_global_json = result_global['components'].to_json(orient='records')
                tsne_metrics_json = tsne_metrics['components'].to_json(orient='records')
                tsne_global_json = tsne_global['components'].to_json(orient='records')

    return render(request, 'dashboard.html', {
        'upload_form': upload_form,
        'file_form': file_form,
        'file_names': file_names,
        'pca_metrics': pca_metrics_json,
        'pca_global': pca_global_json,
        'explained_metrics': json.dumps(explained_metrics),
        'explained_global': json.dumps(explained_global),
        'tsne_metrics': tsne_metrics_json,
        'tsne_global': tsne_global_json,
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

    parameters = (
        distance_threshold, time_threshold, radius_threshold,
        quadrant_size, name, label, is_geographical_coordinates
    )

    return trace_file, parameters


def create_config_model(parameters):
    ConfigModel.objects.create(
        fileName=parameters[4],
        label=parameters[5],
        isGeographicalCoordinates=parameters[6],
        distanceThreshold=parameters[0],
        timeThreshold=parameters[1],
        radiusThreshold=parameters[2],
        quadrantSize=parameters[3],
    )
