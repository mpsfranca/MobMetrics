from django import forms

class UploadForm(forms.Form):
    trace = forms.FileField(label='Trace')

    time_threshold = forms.FloatField(label='Time Threshold')
    distance_threshold = forms.FloatField(label='Distance Threshold')
    radius_threshold = forms.FloatField(label='Radius Threshold')
    quadrant_size = forms.FloatField(label='Quadrant Size')
    
    name = forms.CharField(label='Name')
    label = forms.CharField(label='Trace Label')

class FileNameForm(forms.Form):
    file_name = forms.CharField(label='File Name', max_length=255, required=True)
