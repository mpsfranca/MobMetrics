from django import forms

class UploadForm(forms.Form):
    trace = forms.FileField(label='Trace')
    time_threshold = forms.FloatField(label='Time Threshold')
    distance_threshold = forms.FloatField(label='Distance Threshold')
