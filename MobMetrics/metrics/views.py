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
from .forms import UploadForm, FileNameForm, DataAnalytcsParamsForm
from .process.factory import Factory
from .process.format import Format
from .process.DataAnalytcs.pca import PCA
from .process.DataAnalytcs.tSNE import tSNE

def dashboard_view(request):
    upload_form = UploadForm()
    file_form = FileNameForm()
    analytcs_form = DataAnalytcsParamsForm()
    file_names = ConfigModel.objects.values_list('fileName', flat=True).distinct()

    pca_metrics = {'pca_json': None, 'explained_variance': None}
    pca_global_metrics = {'pca_json': None, 'explained_variance': None}
    tsne_metrics = {'components': None}
    tsne_global_metrics = {'components': None}


    if request.method == 'POST':
        if 'upload' in request.POST:
            file_names = handle_upload(request, upload_form)
        elif 'delete' in request.POST:
            file_names = handle_delete(request)
        elif 'download' in request.POST:
            return handle_download(request)
        elif 'generate_graphs' in request.POST:
            pca_metrics, pca_global_metrics, tsne_metrics, tsne_global_metrics = handle_generate_graphs(request, analytcs_form)

    return render(request, 'dashboard.html', {
        'upload_form': upload_form,
        'file_form': file_form,
        'analytcs_form': analytcs_form,
        'file_names': file_names,

        'pca_metrics': pca_metrics['pca_json'],
        'pca_explained_metrics': json.dumps(pca_metrics['explained_variance']),

        'pca_global': pca_global_metrics['pca_json'],
        'pca_explained_global': json.dumps(pca_global_metrics['explained_variance']),

        'tsne_metrics': tsne_metrics,

        'tsne_global': tsne_global_metrics,
    })

def handle_upload(request, upload_form):
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

    return ConfigModel.objects.values_list('fileName', flat=True).distinct()

def handle_delete(request):
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
    return ConfigModel.objects.values_list('fileName', flat=True).distinct()

def handle_download(request):
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

def handle_generate_graphs(request, analytics_form):
    """
    Function to process data for the graphs

    Parameters:
    request (HttpRequest): The request containing the form data and files.
    analytics_form (DataAnalytcsParamsForm): The form containing the analytics parameters.

    Returns:
    tuple: A tuple containing:
        - pca_metrics (dict): a dict with all content extract from PCA from MetricsModel
        - pca_global_metrics (dict): a dict with all content extract from PCA from GlobalMetricsModel
        - tsne_metrics (dict): a dict with all content extract from tSNE from MetricsModel
        - tsne_global_metrics (dict): a dict with all content extract from tSNE from GlobalMetricsModel
    """
    
    analytics_form = DataAnalytcsParamsForm(request.POST, request.FILES)

    if analytics_form.is_valid():
        # Get parameters from the form
        pca_n_components = int(request.POST.get('PCA_n_components'))
        tsne_n_components = int(request.POST.get('tSNE_n_components'))
        tsne_perplexity = float(request.POST.get('tSNE_perplexity'))

        # Load data
        metrics_df = pd.DataFrame.from_records(MetricsModel.objects.all().values())
        global_metrics_df = pd.DataFrame.from_records(GlobalMetricsModel.objects.all().values())

        columns_metrics, columns_global = columns_analytics(metrics_df, global_metrics_df)

        # Perform PCA for metrics and global data
        pca_metrics = PCA(pca_n_components, metrics_df, columns_metrics).extract()
        pca_global_metrics = PCA(pca_n_components, global_metrics_df, columns_global).extract()

        # Perform t-SNE for metrics and global data
        tsne_metrics = tSNE(tsne_n_components, tsne_perplexity, metrics_df, columns_metrics).extract()
        tsne_global_metrics = tSNE(tsne_n_components, tsne_perplexity, global_metrics_df, columns_global).extract()

        # Return the results
        return (
            pca_metrics, pca_global_metrics, tsne_metrics, tsne_global_metrics
        )

def columns_analytics(metrics_df, global_metrics_df):
    """
    Function to define wich metrics will be analysed

    Parameters:
        - metrics_df (pd.DataFrame): Metrics DataFrame colected from MetricsModel.
        - global_metrics_df (pd.DataFrame): Global Metrics DataFrame GlobalMetricsModel.
    """

    # Columns that should be excluded
    exclude_columns_metrics = ['id', 'fileName', 'label', 'entityId', 'x_center', 'y_center', 'z_center']
    exclude_columns_global = ['id', 'fileName', 'label', 'entityId', 'avgX_center', 'avgY_center', 'avgZ_center']

    # Remove those columns from dataframe
    columns_metrics = [col for col in metrics_df.columns if col not in exclude_columns_metrics]
    columns_global = [col for col in global_metrics_df.columns if col not in exclude_columns_global]

    return columns_metrics, columns_global

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
