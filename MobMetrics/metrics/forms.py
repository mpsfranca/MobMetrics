from django import forms

LABEL_CHOICES = [
    (1, "Walk"),  
    (2, "Car"),
    (3, "Bus"),
    (4, "Bike"),
]

class UploadForm(forms.Form):
    trace = forms.FileField(label='Trace')

    time_threshold = forms.FloatField(label='Time Threshold')
    distance_threshold = forms.FloatField(label='Distance Threshold')
    radius_threshold = forms.FloatField(label='Radius Threshold')
    
    name = forms.CharField(label='Name')
    label = forms.ChoiceField(label='Trace Label', choices = LABEL_CHOICES)

class FileNameForm(forms.Form):
    file_name = forms.CharField(label='File Name', max_length=255, required=True)
