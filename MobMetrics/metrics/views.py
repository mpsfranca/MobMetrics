from django.shortcuts import render
from django.core.serializers import serialize

import pandas as pd

from .models import ConfigModel, MetricsModel, TraceModel, TravelsModel, StayPointModel, VisitModel, ContactModel
from .forms import UploadForm

from .process.factory import Factory
from .process.format import Format

def upload_view(request):
    """
    Handles the file upload process. Validates the input form, processes the uploaded file,
    and extracts metrics to display in the front end.

    Args:
        request: HTTP request object.

    Returns:
        Rendered HTML template with metrics or the upload form.
    """
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Collecting input data from the form
            trace_file = form.cleaned_data['trace']
            time_threshold = form.cleaned_data['time_threshold']
            distance_threshold = form.cleaned_data['distance_threshold']
            radius_threshold = form.cleaned_data['radius_threshold']

            name = form.cleaned_data['name']
            label = form.cleaned_data['label']

            parameters = (distance_threshold, time_threshold, radius_threshold)

            # Formatting the input file
            trace_file = pd.read_csv(trace_file)
            trace_file = Format(trace_file).extract()

            # Extracting metrics
            create_config_model(name, label, parameters)
            Factory(trace_file, parameters, name).extract()

            # Serializing metrics to JSON for the front end
            metrics = serialize('json', MetricsModel.objects.all())

            return render(request, 'success/success.html', {
                'metrics': metrics,
            })
    else:
        form = UploadForm()

    return render(request, 'upload/form.html', {'form': form})

def success_view(request):
    """
    Clears all data from the database models and renders the upload form.

    Args:
        request: HTTP request object.

    Returns:
        Rendered HTML template with the upload form.
    """
    ConfigModel.objects.all().delete()
    MetricsModel.objects.all().delete()
    TraceModel.objects.all().delete()
    TravelsModel.objects.all().delete()
    StayPointModel.objects.all().delete()
    VisitModel.objects.all().delete()
    ContactModel.objects.all().delete()

    form = UploadForm()
    return render(request, 'upload/form.html', {'form': form})

def create_config_model(name, label, parameters):
    """
    Creates a new configuration model instance.

    Args:
        name (str): Name of the configuration.
        label (str): Label for the configuration.
        parameters (tuple): Tuple containing distance, time, and radius thresholds.

    Returns:
        None
    """
    ConfigModel.objects.create(
        fileName=name,
        label=label,
        distanceThreshold=parameters[0],
        timeThreshold=parameters[1],
        radiusThreshold=parameters[2],
    )
