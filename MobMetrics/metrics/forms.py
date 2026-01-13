# Related third party imports.
from django import forms

class UploadForm(forms.Form):
    """ Form to upload parameters and file to executes """
    # File data
    trace = forms.FileField(label='Trace')
    name = forms.CharField(label='Name')
    label = forms.CharField(label='Trace Label')
    is_geographical_coordinates = forms.BooleanField(label='Is Geographical Coordinates?', required=False)

    # Stay Point parameters
    distance_threshold = forms.FloatField(label='Distance Threshold')
    time_threshold = forms.FloatField(label='Time Threshold')

    # Contact parameters
    radius_threshold = forms.FloatField(label='Radius Threshold')
    contact_time_threshold = forms.FloatField(label='Contact Time Threshold')
    skip_contact_detection = forms.BooleanField(required=False, label="Don't detect contacts")

    #Quadrant Entropy Parameters
    quadrant_parts = forms.FloatField(label='Quadrant Parts')
    
class FileNameForm(forms.Form):
    """ Form to upload file name to delete or download """
    file_name = forms.CharField(label='File Name', max_length=255, required=True)

class DataAnalytcsParamsForm(forms.Form):
    """ Form to upload paramters to data analytics """
    # PCA
    PCA_n_components = forms.IntegerField(
        label='PCA N Components', initial=2  
    )

    #TSNE
    tSNE_n_components = forms.IntegerField(
        label='tSNE N Components', initial=2  
    )
    tSNE_perplexity = forms.IntegerField(
        label='Perplexity N Components', initial=30  
    )

    #BDscan
    dbscan_eps = forms.FloatField(
        label='BDscan epslon', initial=0.5 
    )
    
    dbscan_min_samples = forms.IntegerField(
        label='BDscan Min Samples', initial=5 
    )
