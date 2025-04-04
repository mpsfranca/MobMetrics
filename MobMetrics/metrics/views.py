from django.shortcuts import render, redirect
from django.core.serializers import serialize
from django.contrib import messages

import pandas as pd

from .models import ConfigModel, MetricsModel, TravelsModel, StayPointModel, VisitModel, ContactModel, QuadrantEntropyModel, GlobalMetricsModel
from .forms import UploadForm, FileNameForm
from .process.factory import Factory
from .process.format import Format

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
    return render(request, 'success/success.html', {'form': FileNameForm()})

def get_data(form):
    trace_file = form.cleaned_data['trace']
    time_threshold = form.cleaned_data['time_threshold']
    distance_threshold = form.cleaned_data['distance_threshold']
    radius_threshold = form.cleaned_data['radius_threshold']
    quadrant_size = form.cleaned_data['quadrant_size']

    name = form.cleaned_data['name']
    label = form.cleaned_data['label']

    parameters = (distance_threshold, time_threshold, radius_threshold, quadrant_size, name, label)

    return trace_file, parameters

def create_config_model(parameters):
    ConfigModel.objects.create(
        fileName=parameters[4],
        label=parameters[5],
        distanceThreshold=parameters[0],
        timeThreshold=parameters[1],
        radiusThreshold=parameters[2],
        quadrantSize=parameters[3],
    )