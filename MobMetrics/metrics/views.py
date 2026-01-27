# Standard library imports.
from io import BytesIO
import os
import shutil
import zipfile
import json
import subprocess

# Related third party imports.
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
from django.conf import settings

# Local application/library specific imports.
from .forms import UploadForm, FileNameForm, DataAnalytcsParamsForm,ModelSelectForm,BonnmotionMobmetricsForm,BonnmotionScenarioForm,BonnmotionRandomSpeedBase,BoundlessForm,ColumnForm,DisasterAreaForm,OriginalGaussMarkovForm,GaussMarkovForm,ManhattanGridForm,RandomStreetForm,MSLAWForm,NomadicForm,ProbRandomWalkForm,PursueForm,RandomDirectionForm,RandomWalkForm,RandomWaypointForm,RPGMForm,SLAWForm,SMOOTHForm,StaticForm,StaticDriftForm,SteadyStateRandomWaypointForm,SWIMForm,TIMMForm,TLWForm
from .utils.csv_converter import convert
from .utils.model_params import functions
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
    plot_trace_in_time,
    plot_stay_points
)

from .visualizations.metrics.global_metrics import (
    plot_radar_chart,
    plot_travel_distance_comparison,
    plot_metric_histogram,
    plot_metric_boxplot
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
    select_form = ModelSelectForm()
    bm_mobmetrics_form = BonnmotionMobmetricsForm()
    bm_scenario_form = BonnmotionScenarioForm()
    bm_randomspeedbase_form = BonnmotionRandomSpeedBase()
    boundless_form = BoundlessForm()
    column_form = ColumnForm()
    disasterarea_form = DisasterAreaForm()
    originalgaussmarkov_form = OriginalGaussMarkovForm()
    gaussmarkov_form = GaussMarkovForm()
    manhattangrid_form = ManhattanGridForm()
    randomstreet_form = RandomStreetForm()
    mslaw_form = MSLAWForm()
    nomadic_form = NomadicForm()
    probrandomwalk_form = ProbRandomWalkForm()
    pursue_form = PursueForm()
    randomdirection_form = RandomDirectionForm()
    randomwalk_form = RandomWalkForm()
    randomwaypoint_form = RandomWaypointForm()
    rpgm_form = RPGMForm()
    slaw_form = SLAWForm()
    smooth_form = SMOOTHForm()
    static_form = StaticForm()
    staticdrift_form = StaticDriftForm()
    steadystaterandomwaypoint_form = SteadyStateRandomWaypointForm()
    swim_form = SWIMForm()
    timm_form = TIMMForm()
    tlw_form = TLWForm()


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
        elif 'create' in request.POST:
            _handle_bonnmotion(request)

    last_config = ConfigModel.objects.last()

    entity_id = request.GET.get('entity_id')
    stay_point_id = request.GET.get('stay_point_id')
    trace_in_time_html = None

    if last_config:
        file_name = last_config.file_name
        metrics = MetricsModel.objects.filter(file_name=file_name).order_by("entity_id")
        global_metrics = GlobalMetricsModel.objects.filter(file_name=file_name).first()
        staypoints = StayPointModel.objects.filter(file_name=file_name).order_by("stay_point_id")
        trace_plot_html = plot_trace_entities(file_name=file_name, max_points=5000)
        radar_chart_html = plot_radar_chart(file_name=file_name)
        stay_points_html = plot_stay_points(file_name=file_name)

        if entity_id is not None:
            try:
                entity_id = int(entity_id)
                trace_in_time_html = plot_trace_in_time(file_name=file_name, entity_id=entity_id)
                travel_distance_compare_plot_html = plot_travel_distance_comparison(file_name=file_name, entity_id=entity_id)
                metric_histogram_html = plot_metric_histogram(file_name=file_name)
                metric_boxplot_html = plot_metric_boxplot(file_name=file_name)
            except ValueError:
                trace_in_time_html = plot_trace_in_time(file_name=file_name)
        else:
            trace_in_time_html = plot_trace_in_time(file_name=file_name)
            travel_distance_compare_plot_html = plot_travel_distance_comparison(file_name=file_name, entity_id=0)
            metric_histogram_html = plot_metric_histogram(file_name=file_name)
            metric_boxplot_html = plot_metric_boxplot(file_name=file_name)
        
        if stay_point_id is not None:
            try:
                stay_point_id = int(stay_point_id)
                stay_points_html = plot_stay_points(file_name=file_name, highlight_spId=stay_point_id)
            except ValueError:
                stay_points_html = plot_stay_points(file_name=file_name)
        else:
            stay_points_html = plot_stay_points(file_name=file_name)

    else:
        metrics = None
        global_metrics = None
        staypoints = None
        trace_plot_html = None
        radar_chart_html = None
        travel_distance_compare_plot_html = None
        metric_histogram_html = None
        metric_boxplot_html = None
        stay_points_html = None

    return render(request, 'base.html', {
        'upload_form': upload_form,
        'file_form': file_form,
        'select_form': select_form,
        'bm_mobmetrics_form': bm_mobmetrics_form,
        'bm_scenario_form': bm_scenario_form,
        'bm_randomspeedbase_form': bm_randomspeedbase_form,
        'boundless_form':boundless_form,
        'column_form':column_form,
        'disasterarea_form':disasterarea_form,
        'originalgaussmarkov_form': originalgaussmarkov_form,
        'gaussmarkov_form': gaussmarkov_form,
        'manhattangrid_form': manhattangrid_form,
        'randomstreet_form': randomstreet_form,
        'mslaw_form': mslaw_form,
        'nomadic_form': nomadic_form,
        'probrandomwalk_form': probrandomwalk_form,
        'pursue_form': pursue_form,
        'randomdirection_form': randomdirection_form,
        'randomwalk_form': randomwalk_form,
        'randomwaypoint_form': randomwaypoint_form,
        'rpgm_form': rpgm_form,
        'slaw_form': slaw_form,
        'smooth_form': smooth_form,
        'static_form': static_form,
        'staticdrift_form': staticdrift_form,
        'steadystaterandomwaypoint_form': steadystaterandomwaypoint_form,
        'swim_form': swim_form,
        'timm_form': timm_form,
        'tlw_form': tlw_form,

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
        'travel_distance_compare_plot': travel_distance_compare_plot_html,
        'metric_histogram': metric_histogram_html,
        'metric_boxplot': metric_boxplot_html,
        'stay_point_scatter_plot': stay_points_html,
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
    skip_contact_detection = form.cleaned_data['skip_contact_detection']

    parameters = (
        distance_threshold, time_threshold, radius_threshold,
        quadrant_parts, name, label, is_geographical_coordinates,
        contact_time_threshold, skip_contact_detection
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

def _handle_bonnmotion(request):
    data = request.POST
    scenario_name = data.get('scenario_name')
    model = data.get('model')
    random_seed = data.get('random_seed')
    area_depth = data.get('area_depth')
    use_circular_shape = data.get('use_circular_shape') #TODO Check why it isn't being sent
    attraction_points = data.get('attraction_points')
    dimension_select = data.get('dimension_select')
    max_speed = data.get('max_speed')
    min_speed = data.get('min_speed')
    max_pause_time = data.get('max_pause_time')

    # Scenario Params
    args = [
    "-f", scenario_name,
    model,
    "-n", data.get('nodes'),
    "-d", data.get('scenario_duration'),
    "-x", data.get('area_width'),
    "-y", data.get('area_height'),
    "-i", data.get('skip_time')
]
    if attraction_points:
        args += ["-a", attraction_points]
    if use_circular_shape:
        args += ["-c"]
    if random_seed:
        args += ["-R", random_seed]
    if area_depth:
        args += ["-z", area_depth]
    if dimension_select:
        args += ["-J", dimension_select]
    if max_speed:
        args += ["-h",max_speed]
    if min_speed:
        args += ["-l",min_speed]
    if max_pause_time:
        args += ["-p",max_pause_time]

    args += functions[model](data)

    subprocess.run([settings.BONNMOTION_DIR,*args])

    subprocess.run([settings.BONNMOTION_DIR,"CSVFile",'-f',scenario_name])
    
    convert(scenario_name)

    csvFile = open(f"{scenario_name}.csv",'r')

    data_frame = pd.read_csv(csvFile)
    data_frame = Format(data_frame).extract()

    output_path = f"{settings.AUX_PATH}/generated_scenarios/{model}/{scenario_name}"
    os.makedirs(output_path, exist_ok=True)
    [shutil.move(f, f"{output_path}/{f}") for f in [f"{scenario_name}.params", f"{scenario_name}.movements.gz", f"{scenario_name}.csv"]]

    distance_threshold = data.get('distance_threshold')
    time_threshold = data.get('time_threshold')
    radius_threshold = data.get('radius_threshold')
    quadrant_divisions = data.get('quadrant_divisions')
    contact_time_threshold = data.get('contact_time_threshold')

    parameters = [
        float(distance_threshold) if distance_threshold else "",
        float(time_threshold) if time_threshold else "",
        float(radius_threshold) if radius_threshold else "",
        float(quadrant_divisions) if quadrant_divisions else "",
        scenario_name,
        f"{scenario_name}-{model}",
        True if data.get('geo_coord') else False,
        float(contact_time_threshold) if contact_time_threshold else "",
        True if data.get('skip_contact_detection') else False
    ]

    _create_config_model(parameters)
    _create_trace_model(parameters, data_frame)
    
    Factory(data_frame, parameters).extract()

