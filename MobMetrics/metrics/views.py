from django.shortcuts import render
from django.core.serializers import serialize

from .forms import UploadForm
from .models import MetricsModel, TraceModel, TravelsModel, StayPointModel

from .process.main import main

def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            trace_file = form.cleaned_data['trace']
            time_threshold = form.cleaned_data['time_threshold']
            distance_threshold = form.cleaned_data['distance_threshold']

            parameters = (time_threshold, distance_threshold)

            main(trace_file, parameters)

            metrics = serialize('json', MetricsModel.objects.all())
            traces = TraceModel.objects.all()
            travels = TravelsModel.objects.all()
            stay_points = StayPointModel.objects.all()

            return render(request, 'upload/success.html', {
                'metrics': metrics,
                'traces': traces,
                'travels': travels,
                'stay_points': stay_points
            })
    else:
        form = UploadForm()

    return render(request, 'upload/form.html', {'form': form})
