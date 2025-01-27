from django.shortcuts import render, redirect
from django.core.serializers import serialize
import pandas as pd

from .models import ConfigModel, MetricsModel, TravelsModel, StayPointModel, VisitModel, ContactModel
from .forms import UploadForm
from .process.factory import Factory
from .process.format import Format

def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            trace_file = form.cleaned_data['trace']
            time_threshold = form.cleaned_data['time_threshold']
            distance_threshold = form.cleaned_data['distance_threshold']
            radius_threshold = form.cleaned_data['radius_threshold']

            name = form.cleaned_data['name']
            label = form.cleaned_data['label']

            parameters = (distance_threshold, time_threshold, radius_threshold)

            trace_file = pd.read_csv(trace_file)
            trace_file = Format(trace_file).extract()

            create_config_model(name, label, parameters)

            Factory(trace_file, parameters, name).extract()

            return render(request, 'success/success.html')
    else:
        form = UploadForm()

    return render(request, 'upload/form.html', {'form': form})

def create_config_model(name, label, parameters):
    ConfigModel.objects.create(
        fileName=name,
        label=label,
        distanceThreshold=parameters[0],
        timeThreshold=parameters[1],
        radiusThreshold=parameters[2],
    )

def success_view(request):
    ConfigModel.objects.all().delete()
    MetricsModel.objects.all().delete()
    TravelsModel.objects.all().delete()
    StayPointModel.objects.all().delete()
    VisitModel.objects.all().delete()
    ContactModel.objects.all().delete()

    form = UploadForm()
    return render(request, 'upload/form.html', {'form': form})
