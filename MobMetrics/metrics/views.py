from django.shortcuts import render
from django.core.serializers import serialize

import pandas as pd

from .models import MetricsModel, TraceModel, TravelsModel, StayPointModel
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

            parameters = (distance_threshold, time_threshold, radius_threshold)

            trace_file = pd.read_csv(trace_file)
            trace_file = Format(trace_file).extract()

            

            Factory(trace_file, parameters, name).extract()
            

            metrics = serialize('json', MetricsModel.objects.all())
            traces = serialize('json', TraceModel.objects.all())
            travels = serialize('json', MetricsModel.objects.all())
            stay_points = serialize('json', StayPointModel.objects.all())

            return render(request, 'upload/success.html', {
                'metrics': metrics,
                'traces': traces,
                'travels': travels,
                'stay_points': stay_points
            })
    else:
        form = UploadForm()

    return render(request, 'upload/form.html', {'form': form})
