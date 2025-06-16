# Standard library imports.
from io import BytesIO
import zipfile
import json

# Related third party imports.
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction

# Local application/library specific imports.
from .forms import UploadForm, FileNameForm, DataAnalytcsParamsForm
from .process.factory import Factory
from .process.format import Format
from .process.DataAnalytcs.pca import PCA
from .process.DataAnalytcs.tSNE import tSNE
from .process.DataAnalytcs.clustering.DBscan import DBscan # Não será usado diretamente para plot, mas sim para dados

from .visualizations.comparative.pca_plots import (
    generate_pca_plot_html,
    generate_explained_variance_plot_html,
    generate_dbscan_pca_plot_html
)
from .visualizations.comparative.tsne_plots import (
    generate_tsne_plot_html,
    generate_dbscan_tsne_plot_html
)

from .visualizations.trace.trace_plot import (
    plot_trace_entities,
    plot_trace_in_time
)

from .visualizations.metrics.global_metrics import (
    plot_radar_chart
)

from .models import (ConfigModel, MetricsModel,
                      JourneyModel, StayPointModel,
                      VisitModel, ContactModel,
                      QuadrantEntropyModel, GlobalMetricsModel,
                      TraceModel)

def dashboard_view(request):
    """
        This view is responsable to process all POST and calculate metrics and analytic functions.

        Returns:
            upload_form (UploadForm): Django form for file upload.
            file_form (FileForm): Django form for file selection or metadata.
            analytics_form (AnalyticsForm): Django form for analytics/method options.
            file_names (list): List of uploaded file names.
            
            # Novas variáveis para o HTML dos gráficos
            pca_metrics_plot_html (str): HTML do gráfico PCA de MetricsModel.
            pca_explained_plot_html (str): HTML do gráfico de variância explicada de MetricsModel.
            pca_dbscan_metrics_plot_html (str): HTML do gráfico DBSCAN PCA de MetricsModel.
            tsne_metrics_plot_html (str): HTML do gráfico t-SNE de MetricsModel.
            tsne_dbscan_metrics_plot_html (str): HTML do gráfico DBSCAN t-SNE de MetricsModel.
            pca_global_plot_html (str): HTML do gráfico PCA de GlobalMetricsModel.
            tsne_global_plot_html (str): HTML do gráfico t-SNE de GlobalMetricsModel.
    """

    # Start Variables.
    file_names = ConfigModel.objects.values_list('file_name', flat=True).distinct()
    
    pca_metrics_plot_html = ""
    pca_explained_plot_html = ""
    pca_dbscan_metrics_plot_html = ""
    tsne_metrics_plot_html = ""
    tsne_dbscan_metrics_plot_html = ""
    pca_global_plot_html = ""
    tsne_global_plot_html = ""

    # Get forms.
    upload_form = UploadForm()
    file_form = FileNameForm()
    analytcs_form = DataAnalytcsParamsForm()

    # Identify wich POST method was requested
    if request.method == 'POST':
        if 'upload' in request.POST:
            file_names = _handle_upload(request)
        elif 'delete' in request.POST:
            file_names = _handle_delete(request)
        elif 'download' in request.POST:
            return _handle_download(request)
        elif 'generate_graphs' in request.POST:
            (pca_metrics_plot_html, pca_explained_plot_html, pca_dbscan_metrics_plot_html,
             tsne_metrics_plot_html, tsne_dbscan_metrics_plot_html,
             pca_global_plot_html, tsne_global_plot_html) = _handle_generate_graphs(request)      

    last_config = ConfigModel.objects.last()

    entity_id = request.GET.get('entity_id')
    trace_in_time_html = None

    if last_config:
        file_name = last_config.file_name
        metrics = MetricsModel.objects.filter(file_name=file_name).order_by("entity_id")
        global_metrics = GlobalMetricsModel.objects.filter(file_name=file_name).first()
        staypoints = StayPointModel.objects.filter(file_name=file_name).order_by("stay_point_id")
        trace_plot_html = plot_trace_entities(file_name=file_name, max_points=5000)
        radar_chart_html = plot_radar_chart(file_name=file_name)

        if entity_id is not None:
            try:
                entity_id = int(entity_id)
                trace_in_time_html = plot_trace_in_time(file_name=file_name, entity_id=entity_id)
            except ValueError:
                trace_in_time_html = plot_trace_in_time(file_name=file_name)
        else:
            plot_trace_in_time(file_name=file_name)
    else:
        metrics = None
        global_metrics = None
        staypoints = None
        trace_plot_html = None
        radar_chart_html = None

    return render(request, 'dashboard.html', {
        'upload_form': upload_form,
        'file_form': file_form,
        'analytcs_form': analytcs_form,
        'file_names': file_names,

        # Pass HTML variables directly to the context
        'metrics': metrics,
        'staypoints': staypoints,
        'global_metrics': global_metrics,
        'last_file_name': last_config.file_name if last_config else None,
        'trace_plot_html': trace_plot_html,
        'radar_chart_html': radar_chart_html,
        'trace_in_time_html': trace_in_time_html,
        'pca_metrics_plot_html': pca_metrics_plot_html,
        'pca_explained_plot_html': pca_explained_plot_html,
        'pca_dbscan_metrics_plot_html': pca_dbscan_metrics_plot_html,
        'tsne_metrics_plot_html': tsne_metrics_plot_html,
        'tsne_dbscan_metrics_plot_html': tsne_dbscan_metrics_plot_html,
        'pca_global_plot_html': pca_global_plot_html,
        'tsne_global_plot_html': tsne_global_plot_html,
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
            _create_trace_model(parameters, data_frame)

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

    file_name = request.POST.get('fileName')
    models_list = [
            ConfigModel, MetricsModel,
            JourneyModel, StayPointModel,
            VisitModel, ContactModel,
            QuadrantEntropyModel, GlobalMetricsModel,
            TraceModel
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
    file_name = request.POST.get('fileName')

    if file_name:
        zip_buffer = BytesIO()

        # Get all models data
        models = {
            'ConfigModel': ConfigModel.objects.filter(file_name=file_name),
            'MetricsModel': MetricsModel.objects.filter(file_name=file_name),
            'JurnayModel': JourneyModel.objects.filter(file_name=file_name),
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
        response['Content-Disposition'] = f'attachment; filename={file_name}.zip'
        return response
    else:
        messages.error(request, "No file name provided.")
        return HttpResponse("File name not provided", status=400)

def _handle_generate_graphs(request):
    """
    Function to process data for the graphs and generate their HTML.

    Returns:
        tuple: Contains the HTML strings for all generated plots:
            (pca_metrics_plot_html, pca_explained_plot_html, pca_dbscan_metrics_plot_html,
             tsne_metrics_plot_html, tsne_dbscan_metrics_plot_html,
             pca_global_plot_html, tsne_global_plot_html)
    """

    analytics_form = DataAnalytcsParamsForm(request.POST, request.FILES)

    pca_metrics_plot_html = ""
    pca_explained_plot_html = ""
    pca_dbscan_metrics_plot_html = ""
    tsne_metrics_plot_html = ""
    tsne_dbscan_metrics_plot_html = ""
    pca_global_plot_html = ""
    tsne_global_plot_html = ""

    if analytics_form.is_valid():
        # Get parameters from the form
        pca_n_components = int(request.POST.get('PCA_n_components'))
        tsne_n_components = int(request.POST.get('tSNE_n_components'))
        tsne_perplexity = float(request.POST.get('tSNE_perplexity'))
        dbscan_eps = float(request.POST.get('dbscan_eps'))
        dbscan_min_samples = int(request.POST.get('dbscan_min_samples'))

        dbscan_parameters = (dbscan_eps, dbscan_min_samples)

        # Load data
        metrics_df = pd.DataFrame.from_records(MetricsModel.objects.all().values())
        global_metrics_df = pd.DataFrame.from_records(GlobalMetricsModel.objects.all().values())

        columns_metrics, columns_global = _columns_analytics(metrics_df, global_metrics_df)

        # Perform PCA for metrics and global data
        pca_metrics_results = PCA(pca_n_components, metrics_df.copy(), columns_metrics, dbscan_parameters).extract()
        pca_global_metrics_results = PCA(pca_n_components, global_metrics_df.copy(), columns_global, dbscan_parameters).extract()

        # Perform t-SNE for metrics and global data
        tsne_metrics_results = tSNE(tsne_n_components, tsne_perplexity, metrics_df.copy(), columns_metrics, dbscan_parameters).extract()
        tsne_global_metrics_results = tSNE(tsne_n_components, tsne_perplexity, global_metrics_df.copy(), columns_global, dbscan_parameters).extract()

        
        # PCA - MetricsModel

        pca_metrics_plot_html = generate_pca_plot_html(
            data_frame=json.loads(pca_metrics_results['pca_json']),
            contributors=pca_metrics_results['top_contributors'],
            n_components=pca_metrics_results['n_components'],
            title='PCA - MetricsModel',
            color_by='label'
        )

        # PCA - Explained Variance
        pca_explained_plot_html = generate_explained_variance_plot_html(
            explained_variance_ratio=pca_metrics_results['explained_variance'],
            title='Explained Variance Components'
        )

        # DBSCAN - PCA MetricsModel
        pca_dbscan_metrics_plot_html = generate_dbscan_pca_plot_html(
            data_frame=json.loads(pca_metrics_results['pca_json']),
            contributors=pca_metrics_results['top_contributors'],
            n_components=pca_metrics_results['n_components'],
            title='DBSCAN - PCA MetricsModel',
            color_by='dbscan_cluster'
        )

        # t-SNE - MetricsModel
        tsne_metrics_plot_html = generate_tsne_plot_html(
            data_frame=json.loads(tsne_metrics_results['components']),
            tsne_components=[f'TSNE{i+1}' for i in range(tsne_n_components)],
            n_components=tsne_n_components,
            title='t-SNE - MetricsModel',
            color_by='label'
        )

        # DBSCAN - tSNE MetricsModel
        tsne_dbscan_metrics_plot_html = generate_dbscan_tsne_plot_html(
            data_frame=json.loads(tsne_metrics_results['components']),
            tsne_components=[f'TSNE{i+1}' for i in range(tsne_n_components)],
            n_components=tsne_n_components,
            title='DBSCAN - tSNE MetricsModel',
            color_by='dbscan_cluster'
        )

        # PCA - GlobalMetricsModel
        pca_global_plot_html = generate_pca_plot_html(
            data_frame=json.loads(pca_global_metrics_results['pca_json']),
            contributors=pca_global_metrics_results['top_contributors'],
            n_components=pca_global_metrics_results['n_components'],
            title='PCA - GlobalMetricsModel',
            color_by='label'
        )

        # t-SNE - GlobalMetricsModel
        tsne_global_plot_html = generate_tsne_plot_html(
            data_frame=json.loads(tsne_global_metrics_results['components']),
            tsne_components=[f'TSNE{i+1}' for i in range(tsne_n_components)],
            n_components=tsne_n_components,
            title='t-SNE - GlobalMetricsModel',
            color_by='label'
        )

    return (pca_metrics_plot_html, pca_explained_plot_html, pca_dbscan_metrics_plot_html,
            tsne_metrics_plot_html, tsne_dbscan_metrics_plot_html,
            pca_global_plot_html, tsne_global_plot_html)


def _columns_analytics(metrics_df, global_metrics_df):
    """
    Function to define wich metrics will be analysed

    Parameters:
        - metrics_df (pd.DataFrame): Metrics DataFrame colected from MetricsModel.
        - global_metrics_df (pd.DataFrame): Global Metrics DataFrame GlobalMetricsModel.
    """

    # Columns that should be excluded
    exclude_columns_metrics = ['id', 'file_name', 'label', 'entityId', 'x_center', 'y_center', 'z_center']
    exclude_columns_global = ['id', 'file_name', 'label', 'entityId', 'avgX_center', 'avgY_center', 'avgZ_center']

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
    contact_time_threshold = form.cleaned_data['contact_time_threshold']

    parameters = (
        distance_threshold, time_threshold, radius_threshold,
        quadrant_parts, name, label, is_geographical_coordinates,
        contact_time_threshold
    )

    return trace_file, parameters

def _create_config_model(parameters):
    """ Function Responsable to create ConfigModel with all parameters"""
    ConfigModel.objects.create(
        file_name = parameters[4],
        label = parameters[5],
        is_geographical_coordinates = parameters[6],
        distance_threshold = parameters[0],
        time_threshold = parameters[1],
        radius_threshold = parameters[2],
        quadrant_parts = parameters[3],
    )

def _create_trace_model(parameters, df):
    """Function for creating a TraceModel with all the trace data"""
    file_name = parameters[4]

    required_columns = {'id', 'x', 'y', 'time'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    trace_objects = [
        TraceModel(
            file_name=file_name,
            entity_id=int(row['id']),
            x=float(row['x']),
            y=float(row['y']),
            timestamp=int(row['time'])
        )
        for _, row in df.iterrows()
    ]

    with transaction.atomic():
        TraceModel.objects.bulk_create(trace_objects, batch_size=1000)
