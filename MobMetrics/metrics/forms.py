# Related third party imports.
from django import forms

MOBILITY_MODEL_CHOICES = [
    ("", "-- Select a Mobility Model --"),
    ("Boundless", "Boundless Simulation Area Model"),
    # ("ChainScenario", "Chain Model (NOT IMPLEMENTED)"),
    ("Column", "Column Mobility Model"),
    ("DisasterArea", "Disaster Area Model"),
    ("OriginalGaussMarkov", "The Original Gauss-Markov Model"),
    ("GaussMarkov", "The Gauss-Markov Model"),
    ("ManhattanGrid", "The Manhattan Grid Model"),
    # ("RandomStreet", "Random Street Model (NOT IMPLEMENTED)"),
    # ("MSLAW", "Map-based Self-similar Least Action Walk (NOT IMPLEMENTED)"),
    ("Nomadic", "Nomadic Community Mobility Model"),
    ("ProbRandomWalk", "Probabilistic Random Walk Model"),
    ("Pursue", "Pursue Mobility Model"),
    ("RandomDirection", "Random Direction Model"),
    ("RandomWalk", "Random Walk Model"),
    ("RandomWaypoint", "The Random Waypoint Model"),
    ("RPGM", "The Reference Point Group Mobility Model"),
    ("SLAW", "Self-similar Least Action Walk"),
    ("SMOOTH", "SMOOTH Model"),
    ("Static", "Static Scenarios"),
    ("StaticDrift", "Static Scenarios With Drift"),
    ("SteadyStateRandomWaypoint", "Steady-State Random Waypoint Model"),
    ("SWIM", "Small World In Motion"),
    ("TIMM", "Tactical Indoor Mobility Model"),
    ("TLW", "Truncated Lévy Walk"),
]

DIMENSION_OPTIONS=[
    ("2D","2D"),
    ("3D","3D"),
]

RANDOMWAYPOINT_DIMENSIONS = [
    ("","-- Select a Dimension --"),
    ("1","X-Axis only"),
    ("2","X-Axis or Y-Axis"),
    ("3","X-Axis and Y-Axis"),
    ("4","X-Axis or Y-Axis or Z-axis (3D-Only)"),
    ("5","Traditional 3D Movement (3D-Only)"),
]

class UploadForm(forms.Form):
    """ Form to upload parameters and file to executes """
    # File data
    trace = forms.FileField(
        required=True,
        label="Trace file",
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control input-border",
        })
    )

    name = forms.CharField(
        required=True,
        label="Name",
        widget=forms.TextInput(attrs={
            'class':'form-control input-border',
            'placeholder':'e.g., Anglova Tanks'
        })
    )
    label = forms.CharField(
        required=True,
        label="Label",
        widget=forms.TextInput(attrs={
            'class':'form-control input-border',
            'placeholder':'e.g., Tanks'
        })
    )
    is_geographical_coordinates = forms.BooleanField(
        required=False,
        initial=True,
        label='Is Geographical Coordinates?',
        widget=forms.CheckboxInput(attrs={
            'class':'form-check-input input-border'
        })
    )

    # Stay Point parameters
    distance_threshold = forms.FloatField(
    label="Distance Threshold",
    required=True,
    widget=forms.NumberInput(attrs={
        "class": "form-control input-border",
        "step": "0.1",
        "value": "60",
    })
)

    time_threshold = forms.FloatField(
        label="Time Threshold",
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control input-border",
            "value": "20",
        })
    )

    # Contact parameters
    radius_threshold = forms.FloatField(
        label="Radius Threshold",
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control input-border",
            "step": "0.1",
            "value": "10",
        })
    )

    contact_time_threshold = forms.FloatField(
        label="Contact Time Threshold",
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control input-border",
            'value':'20'
        })
    )

    skip_contact_detection = forms.BooleanField(
        required=False,
        label="Don't detect contacts",
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input input-border"
        })
    )

    # Quadrant Entropy Parameters
    quadrant_parts = forms.FloatField(
        label="Quadrant Parts",
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control input-border",
            'value':'10'
        })
    )
    
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

class SelectWithDisabledEmpty(forms.Select):
        def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
            option = super().create_option(
                name, value, label, selected, index, subindex=subindex, attrs=attrs
            )
            if value == "":
                option["attrs"]["disabled"] = "disabled"
            return option    

class ModelSelectForm(forms.Form):
    model = forms.ChoiceField(
        choices=MOBILITY_MODEL_CHOICES,
        required=True,
        widget=SelectWithDisabledEmpty(attrs={
            'class':'form-select input-border',
            'onchange':'showParams(this.value)'
        })
    )

class BonnmotionMobmetricsForm(forms.Form):
    geo_coord = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class':'form-check-input input-border'
        })
    )

    distance_threshold = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'step':'0.1',
            'value':'60'
        })
    )

    time_threshold = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'20'
        })
    )

    skip_contact_detection = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class':'form-check-input input-border'
        })
    )

    radius_threshold = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'step':'0.1',
            'value':'10'
        })
    )

    contact_time_threshold = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'20'
        })
    )

    quadrant_divisions = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'10'
        })
    )

class BonnmotionScenarioForm(forms.Form):
    scenario_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class':'form-control input-border',
            'placeholder':'e.g., ScenarioName'
        })
    )

    random_seed = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'placeholder':'(Optional)'
        })
    )

    use_circular_shape = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class':'form-check-input input-border'
        })
    )

    scenario_duration = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'7200'
        })
    )

    skip_time = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'3600'
        })
    )

    nodes = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'10'
        })
    )

    area_width = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'50'
        })
    )

    area_height = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'50'
        })
    )

    area_depth = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'placeholder':'(Optional)'
        })
    )

    attraction_points = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class':'form-control input-border',
            'placeholder':'e.g., 50,50,1,10,10 (Optional)'
        })
    )

    dimension_select = forms.ChoiceField(
        choices=DIMENSION_OPTIONS,
        required=False,
        widget=forms.Select(attrs={
            'class':'form-select input-border'
        })
    )

class BonnmotionRandomSpeedBase(forms.Form):
    min_speed = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'placeholder':'(Optional)'
        })
    )

    max_speed = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'placeholder':'(Optional)'
        })
    )

    max_pause_time = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'placeholder':'(Optional)'
        })
    )

class BoundlessForm(forms.Form):
    time_step = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'0.1',
            'step':'0.1'
        })
    )

    max_accel_change = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'1.5'
        })
    )

    alpha = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'placeholder':'If no alpha is given, the default value is \u03C0/2'
        })
    )

class ColumnForm(forms.Form):
    number_of_groups = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'placeholder':'The number of groups must divide the number of nodes.',
            'min':'2'
        })
    )

    reference_point_of_separation = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border'
        })
    )

    max_distance_group_center = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'2.5',
            'step':'0.1'
        })
    )

class DisasterAreaForm(forms.Form):
    avg_nodes_per_group = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'3.0',
            'step':'0.1'
        })
    )

    max_distance_from_group_center = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'2.5',
            'step':'0.1'
        })
    )

    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class OriginalGaussMarkovForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class GaussMarkovForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class ManhattanGridForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class RandomStreetForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class MSLAWForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class NomadicForm(forms.Form):
    avg_nodes_per_group = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'3.0',
            'step':'0.1'
        })
    )

    max_distance_to_group_center = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'2.5',
            'step':'0.1'
        })
    )

    group_size_stdd = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'2.0',
            'step':'0.1'
        })
    )

    ref_point_max_pause = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'60.0',
            'step':'0.1'
        })
    )

class ProbRandomWalkForm(forms.Form):
    time_interval_to_advance = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'1'
        })
    )

class PursueForm(forms.Form):
    max_speed = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'1.5',
            'step':'0.1'
        })
    )

    min_speed = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'0.5',
            'step':'0.1'
        })
    )

    aggressiveness = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'0.5',
            'step':'0.1'
        })
    )

    pursue_randomness = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'0.5',
            'step':'0.1'
        })
    )

class RandomDirectionForm(forms.Form):
    min_pause_time = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'0.0',
            'step':'0.1'
        })
    )

class RandomWalkForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class RandomWaypointForm(forms.Form):
    dimension = forms.ChoiceField(
        choices=RANDOMWAYPOINT_DIMENSIONS,
        required=False,
        widget=SelectWithDisabledEmpty(attrs={
            'class':'form-select input-border'
        })
    )

class RPGMForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class SLAWForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class SMOOTHForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class StaticForm(forms.Form):
    number_of_density_levels = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control input-border',
            'value':'1'
        })
    )

class StaticDriftForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class SteadyStateRandomWaypointForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class SWIMForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class TIMMForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )

class TLWForm(forms.Form):
    parameters = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control input-border',
            'style':'resize:none;',
            'placeholder':'Type in the parameters'
        })
    )