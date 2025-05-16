# Standard library imports.
from io import BytesIO
import zipfile
import json

# Related third party imports.
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse

# Local application/library specific imports.
from .forms import UploadForm, FileNameForm, DataAnalytcsParamsForm
from .process.factory import Factory
from .process.format import Format
from .process.DataAnalytcs.pca import PCA
from .process.DataAnalytcs.tSNE import tSNE
from .process.DataAnalytcs.clustering.DBscan import DBscan
from .models import (ConfigModel, MetricsModel, 
                     JurnayModel, StayPointModel, 
                     VisitModel,ContactModel, 
                     QuadrantEntropyModel, GlobalMetricsModel)

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
    pca_metrics = pca_global_metrics = {'pca_json': None, 'explained_variance': None, 'n_components': None, 'top_contributors': None}
    tsne_metrics = tsne_global_metrics = {'components': None}
 
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
            (pca_metrics, pca_global_metrics, tsne_metrics, tsne_global_metrics) = _handle_generate_graphs(request)

    return render(request, 'dashboard.html', {
        'upload_form': upload_form,
        'file_form': file_form,
        'analytcs_form': analytcs_form,
        'file_names': file_names,

        'pca_metrics': pca_metrics['pca_json'],
        'pca_explained_metrics': json.dumps(pca_metrics['explained_variance']),
        'n_components_metrics': pca_metrics['n_components'],
        'pca_contributors_metrics': json.dumps(pca_metrics['top_contributors']),

        'pca_global': pca_global_metrics['pca_json'],
        'pca_explained_global': json.dumps(pca_global_metrics['explained_variance']),
        'n_components_global': pca_global_metrics['n_components'],
        'pca_contributors_global': pca_global_metrics['top_contributors'],

        'tsne_metrics': tsne_metrics,

        'tsne_global': tsne_global_metrics,
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

        if ConfigModel.objects.filter(file_name=file_name).exists():
            messages.warning(request, "A file with the same name already exists.")
        else:
            data_frame = pd.read_csv(trace_file)
            data_frame = Format(data_frame).extract()

            _create_config_model(parameters)
            Factory(data_frame, parameters).extract()

            messages.success(request, "Upload and processing completed.")

    file_names = ConfigModel.objects.values_list('file_name', flat=True).distinct()

    return file_names

def _handle_delete(request):
    """
        Function is responsable to delete all data from a especific file.

        Return:
            file_names (list): List of uploaded file names.
    """

    file_name = request.POST.get('file_name')
    models_list = [
            ConfigModel, MetricsModel, 
            JurnayModel, StayPointModel,
            VisitModel, ContactModel, 
            QuadrantEntropyModel, GlobalMetricsModel
        ]
    
    if file_name:
        for model in models_list:
            # Delet data from that file name for each Model
            model.objects.filter(file_name=file_name).delete()
        messages.success(request, f"Data for '{file_name}' deleted.")
    else:
        messages.error(request, "No file name provided.")
    
    file_names = ConfigModel.objects.values_list('file_name', flat=True).distinct()
    return file_names

def _handle_download(request):
    """
        Function is responsable to download all data from a especific file.
    """
    file_name = request.POST.get('file_name')

    if file_name:
        zip_buffer = BytesIO()

        # Get all models data
        models = {
            'ConfigModel': ConfigModel.objects.filter(file_name=file_name),
            'MetricsModel': MetricsModel.objects.filter(file_name=file_name),
            'JurnayModel': JurnayModel.objects.filter(file_name=file_name),
            'StayPointModel': StayPointModel.objects.filter(file_name=file_name),
            'VisitModel': VisitModel.objects.filter(file_name=file_name),
            'ContactModel': ContactModel.objects.filter(file_name=file_name),
            'QuadrantEntropyModel': QuadrantEntropyModel.objects.filter(file_name=file_name),
            'GlobalMetricsModel': GlobalMetricsModel.objects.filter(file_name=file_name),
        }

        # Transfor in a Zip Folder
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
        response['Content-Disposition'] = f'attachment; file_name={file_name}.zip'
        return response
    else:
        messages.error(request, "No file name provided.")
        return HttpResponse("File name not provided", status=400)

def _handle_generate_graphs(request):
    """
    Function to process data for the graphs


    Returns:
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
        dbscan_eps = float(request.POST.get('dbscan_eps'))  # Adicionando o parâmetro DBSCAN
        dbscan_min_samples = int(request.POST.get('dbscan_min_samples'))  # Adicionando o parâmetro DBSCAN

        dbscan_paramters = (dbscan_eps, dbscan_min_samples)

        # Load data
        metrics_df = pd.DataFrame.from_records(MetricsModel.objects.all().values())
        global_metrics_df = pd.DataFrame.from_records(GlobalMetricsModel.objects.all().values())

        columns_metrics, columns_global = _columns_analytics(metrics_df, global_metrics_df)

        # Perform PCA for metrics and global data
        pca_metrics = PCA(pca_n_components, metrics_df, columns_metrics, dbscan_paramters).extract()
        pca_global_metrics = PCA(pca_n_components, global_metrics_df, columns_global, dbscan_paramters).extract()

        # Perform t-SNE for metrics and global data
        tsne_metrics = tSNE(tsne_n_components, tsne_perplexity, metrics_df, columns_metrics, dbscan_paramters).extract()
        tsne_global_metrics = tSNE(tsne_n_components, tsne_perplexity, global_metrics_df, columns_global, dbscan_paramters).extract()

        # Return the results
        return (pca_metrics, pca_global_metrics, 
            tsne_metrics, tsne_global_metrics)
    
def _columns_analytics(metrics_df, global_metrics_df):
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

def _get_data(form):
    """
        Get all data from Upload Form

        Parameters:
            - form (UploadForm): form with all data extract from frontend
        
        Return:
            - trace_file (file): trace file
            - parameters (list): list with all parameters
    """

    trace_file = form.cleaned_data['trace']
    distance_threshold = form.cleaned_data['distance_threshold']
    radius_threshold = form.cleaned_data['radius_threshold']
    is_geographical_coordinates = form.cleaned_data['is_geographical_coordinates']
    time_threshold = form.cleaned_data['time_threshold']
    quadrant_parts = form.cleaned_data['quadrant_parts']
    name = form.cleaned_data['name']
    label = form.cleaned_data['label']

    parameters = (
        distance_threshold, time_threshold, radius_threshold,
        quadrant_parts, name, label, is_geographical_coordinates
    )

    return trace_file, parameters

def _create_config_model(parameters):
    """ Function Responsable to create ConfigModel with all parameters"""
    ConfigModel.objects.create(
        file_name=parameters[4],
        label=parameters[5],
        is_geographical_coordinates=parameters[6],
        distance_threshold=parameters[0],
        time_threshold=parameters[1],
        radius_threshold=parameters[2],
        quadrant_parts=parameters[3],
    )
