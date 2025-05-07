#Standard library imports.
from io import BytesIO
import zipfile
import json

#Related third party imports.
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse

#ocal application/library specific imports.
from .forms import UploadForm, FileNameForm, DataAnalytcsParamsForm
from .process.factory import Factory
from .process.format import Format
from .process.DataAnalytcs.pca import PCA
from .process.DataAnalytcs.tSNE import tSNE
from .models import (ConfigModel, MetricsModel, 
                     TravelsModel, StayPointModel, 
                     VisitModel,ContactModel, 
                     QuadrantEntropyModel, GlobalMetricsModel
                    )


def dashboard_view(request):
    """
        This view is responsable to process all POST and calculate metrics and analytic functions.

        Returns:
            upload_form (UploadForm): Django form for file upload.
            file_form (FileForm): Django form for file selection or metadata.
            analytics_form (AnalyticsForm): Django form for analytics/method options.
            file_names (list): List of uploaded file names.
            pca_metrics (String): JSON String with the result from PCA coleted from MetricsModel.
            pca_global (String): JSON String with the result from PCA coleted from GlobalMetricsModel.
            explained_metrics (dict): Explained variance from MetricsModel.
            explained_global (dict): Explained variance from GlobalMetricsModel.
            tsne_metrics (dict): JSON String with the result from TSNE coleted from MetricsModel.
            tsne_global (dict): JSON String with the result from TSNE coleted from GlobalMetricsModel.

    """

    # Start Variables.
    file_names = ConfigModel.objects.values_list('fileName', flat=True).distinct()
    pca_metrics_json, pca_global_json = None, None
    tsne_metrics_json, tsne_global_json = None, None
    explained_metrics, explained_global = [], []

    # Get forms.
    upload_form = UploadForm()
    file_form = FileNameForm()
    analytcs_form = DataAnalytcsParamsForm()
    
    #Identify wich POST method was requested
    if request.method == 'POST':
        if 'upload' in request.POST:
            file_names = _handle_upload(request)
        elif 'delete' in request.POST:
            file_names = _handle_delete(request)
        elif 'download' in request.POST:
            return _handle_download(request)
        elif 'generate_graphs' in request.POST:
            (pca_metrics_json, pca_global_json, 
             tsne_metrics_json, tsne_global_json, 
             explained_metrics, explained_global) = _handle_generate_graphs(request, 
                                                                            analytcs_form)

    return render(request, 'dashboard.html', {
        'upload_form': upload_form,
        'file_form': file_form,
        'analytcs_form': analytcs_form,
        'file_names': file_names,
        'pca_metrics': pca_metrics_json,
        'pca_global': pca_global_json,
        'explained_metrics': json.dumps(explained_metrics),
        'explained_global': json.dumps(explained_global),
        'tsne_metrics': tsne_metrics_json,
        'tsne_global': tsne_global_json,
    })

def _handle_upload(request):
    """
        Function responsable to get the UploadForm and process all metrics

        Return:
            file_names (list): List of uploaded file names.
    """

    # Get uploaded data
    upload_form = UploadForm(request.POST, request.FILES)
    if upload_form.is_valid():
        trace_file, parameters = _get_data(upload_form)
        file_name = parameters[4]

        if ConfigModel.objects.filter(fileName=file_name).exists():
            messages.warning(request, "A file with the same name already exists.")
        else:
            data_frame = pd.read_csv(trace_file)
            data_frame = Format(data_frame).extract()

            _create_config_model(parameters)
            Factory(data_frame, parameters).extract()

            messages.success(request, "Upload and processing completed.")

    file_names = ConfigModel.objects.values_list('fileName', flat=True).distinct()

    return file_names


def _handle_delete(request):
    """
        Function is responsable to delete all data from a especific file.

        Return:
            file_names (list): List of uploaded file names.
    """

    file_name = request.POST.get('fileName')
    models_list = [
            ConfigModel, MetricsModel, 
            TravelsModel, StayPointModel,
            VisitModel, ContactModel, 
            QuadrantEntropyModel, GlobalMetricsModel
        ]
    
    if file_name:
        for model in models_list:
            # Delet data from that file name for each Model
            model.objects.filter(fileName=file_name).delete()
        messages.success(request, f"Data for '{file_name}' deleted.")
    else:
        messages.error(request, "No file name provided.")
    
    file_names = ConfigModel.objects.values_list('fileName', flat=True).distinct()
    return file_names

def _handle_download(request):
    """
        Function is responsable to download all data from a especific file.
    """
    file_name = request.POST.get('fileName')

    if file_name:
        zip_buffer = BytesIO()

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

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for model_name, queryset in models.items():
                if queryset.exists():
                    df = pd.DataFrame.from_records(queryset.values())
                    csv_buffer = BytesIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    zip_file.writestr(f'{model_name}.csv', csv_buffer.read())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={file_name}.zip'
        return response
    else:
        messages.error(request, "No file name provided.")
        return HttpResponse("File name not provided", status=400)


def _handle_generate_graphs(request, analytics_form):
    analytics_form = DataAnalytcsParamsForm(request.POST, request.FILES)

    if analytics_form.is_valid():
        # Captura dos parâmetros
        PCA_n_components = int(request.POST.get('PCA_n_components'))
        tSNE_n_components = int(request.POST.get('tSNE_n_components'))
        tSNE_perplexity = float(request.POST.get('tSNE_perplexity'))

        # Carrega dados
        metrics_df = pd.DataFrame.from_records(MetricsModel.objects.all().values())
        global_metrics_df = pd.DataFrame.from_records(GlobalMetricsModel.objects.all().values())

        if metrics_df.empty or global_metrics_df.empty:
            return None, None, None, None, [], []

        # Colunas que queremos excluir
        exclude_columns_metrics = ['id', 'fileName', 'label', 'entityId', 'x_center', 'y_center', 'z_center']
        exclude_columns_global = ['id', 'fileName', 'label', 'entityId', 'avgX_center', 'avgY_center', 'avgZ_center']

        # Detecta colunas interessantes dinamicamente
        columns_metrics = [col for col in metrics_df.columns if col not in exclude_columns_metrics]
        columns_global = [col for col in global_metrics_df.columns if col not in exclude_columns_global]

        PCA_n_components = min(PCA_n_components, len(columns_metrics), len(metrics_df))
        tSNE_n_components = min(tSNE_n_components, len(columns_metrics), len(metrics_df))

        if PCA_n_components > 0:
            result_metrics = PCA(metrics_df, columns_metrics, PCA_n_components).extract()
            result_global = PCA(global_metrics_df, columns_global, PCA_n_components).extract()
            explained_metrics = result_metrics['explained_variance'].tolist()
            explained_global = result_global['explained_variance'].tolist()
        else:
            result_metrics = result_global = explained_metrics = explained_global = None

        # t-SNE
        if tSNE_n_components > 0:
            tsne_metrics = tSNE(metrics_df, columns_metrics, tSNE_n_components, tSNE_perplexity).extract()
            tsne_global = tSNE(global_metrics_df, columns_global, tSNE_n_components, tSNE_perplexity).extract()
        else:
            tsne_metrics = tsne_global = None

        # Labels
        if 'label' in metrics_df.columns:
            if result_metrics: result_metrics['components']['label'] = metrics_df['label'].reset_index(drop=True)
            if tsne_metrics: tsne_metrics['components']['label'] = metrics_df['label'].reset_index(drop=True)

        if 'label' in global_metrics_df.columns:
            if result_global: result_global['components']['label'] = global_metrics_df['label'].reset_index(drop=True)
            if tsne_global: tsne_global['components']['label'] = global_metrics_df['label'].reset_index(drop=True)

        # JSON
        pca_metrics_json = result_metrics['components'].to_json(orient='records') if result_metrics else None
        pca_global_json = result_global['components'].to_json(orient='records') if result_global else None
        tsne_metrics_json = tsne_metrics['components'].to_json(orient='records') if tsne_metrics else None
        tsne_global_json = tsne_global['components'].to_json(orient='records') if tsne_global else None

        return (
            pca_metrics_json, pca_global_json,
            tsne_metrics_json, tsne_global_json,
            explained_metrics or [], explained_global or []
        )

    return None, None, None, None, [], []



def _get_data(form):
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


def _create_config_model(parameters):
    ConfigModel.objects.create(
        fileName=parameters[4],
        label=parameters[5],
        isGeographicalCoordinates=parameters[6],
        distanceThreshold=parameters[0],
        timeThreshold=parameters[1],
        radiusThreshold=parameters[2],
        quadrantSize=parameters[3],
    )
