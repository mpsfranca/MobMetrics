from django.shortcuts import render, redirect
from django.core.serializers import serialize
import pandas as pd

from .models import ConfigModel, MetricsModel, TravelsModel, StayPointModel, VisitModel, ContactModel
from .forms import UploadForm, FileNameForm
from .process.factory import Factory
from .process.format import Format
from .process.pca import CalculatePCA

from django.contrib import messages

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

            # Check if a file with the same name already exists
            if ConfigModel.objects.filter(fileName=name).exists():
                messages.warning(request, "A file with the same name already exists.")
                return render(request, 'upload/form.html', {'form': form})

            parameters = (distance_threshold, time_threshold, radius_threshold)

            trace_file = pd.read_csv(trace_file)
            trace_file = Format(trace_file).extract()

            create_config_model(name, label, parameters)

            Factory(trace_file, parameters, name, label).extract()

            return render(request, 'success/success.html', {'form': FileNameForm()})
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
    if request.method == 'POST':
        form = FileNameForm(request.POST)
        if form.is_valid():
            file_name = form.cleaned_data['file_name']
            
            # Deleta todas as instâncias dos modelos onde fileName = 'name'
            models = [ConfigModel, MetricsModel, TravelsModel, StayPointModel, VisitModel, ContactModel]
            for model in models:
                model.objects.filter(fileName=file_name).delete()
            
            return render(request, 'success/success.html', {'form': FileNameForm()})
    
    return render(request, 'success/success.html', {'form': FileNameForm()})

def pca_view(request):
    """
    Calculates PCA and renders a template with the PCA data to be displayed as a plot.
    """
    # Calculando o PCA e retornando o DataFrame e a variância explicada
    pca_df, explained_variance = CalculatePCA().calculo()

    # Convertendo os dados PCA para formato de lista para uso no JavaScript
    pca_data = {
        'PC1': pca_df['PC1'].tolist(),
        'PC2': pca_df['PC2'].tolist(),
        'labels': pca_df['label'].tolist()  # Supondo que 'label' seja uma coluna para rótulos
    }

    # Gerar uma lista de cores únicas para cada label
    labels_unique = pca_df['label'].unique()
    colors = {label: f'rgba({i*50}, {i*30}, {i*80}, 0.7)' for i, label in enumerate(labels_unique)}

    # Atribuindo a cor para cada ponto baseado no label
    pca_data['colors'] = [colors[label] for label in pca_data['labels']]

    return render(request, 'success/success.html', {
        'pca_data': pca_data,  # Passando os dados para o template
        'explained_variance': explained_variance,  # Passando a variância explicada
        'form': FileNameForm()
    })
