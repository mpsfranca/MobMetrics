from django import forms

LABEL_CHOICES = [
    ("walk", "Walk"),  
    ("car", "Car"),
    ("bus", "Bus"),
    ("bike", "Bike"),
]

class UploadForm(forms.Form):
    trace = forms.FileField(label='Trace')

    time_threshold = forms.FloatField(label='Time Threshold')
    distance_threshold = forms.FloatField(label='Distance Threshold')
    radius_threshold = forms.FloatField(label='Radius Threshold')
    
    name = forms.CharField(label='Name')
    label = forms.ChoiceField(label='Trace Label', choices = LABEL_CHOICES)
