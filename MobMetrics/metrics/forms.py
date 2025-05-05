from django import forms

class UploadForm(forms.Form):
    trace = forms.FileField(label='Trace')

    is_geographical_coordinates = forms.BooleanField(label='Is Geographical Coordinates?', required=False)
    distance_threshold = forms.FloatField(label='Distance Threshold')
    radius_threshold = forms.FloatField(label='Radius Threshold')
    time_threshold = forms.FloatField(label='Time Threshold')
    
    
    quadrant_size = forms.FloatField(label='Quadrant Size')
    
    name = forms.CharField(label='Name')
    label = forms.CharField(label='Trace Label')

class FileNameForm(forms.Form):
    file_name = forms.CharField(label='File Name', max_length=255, required=True)


class DataAnalytcsParamsForm(forms.Form):
    PCA_n_components = forms.IntegerField(
        label='PCA N Components',
        initial=2  # valor padrão
    )
    tSNE_n_components = forms.IntegerField(
        label='tSNE N Components',
        initial=2  # valor padrão
    )
    tSNE_perplexity = forms.IntegerField(
        label='Perplexity N Components',
        initial=30  # valor padrão
    )
