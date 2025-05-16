# Related third party imports.
from django.db import models

class ConfigModel(models.Model):
    """ Model responsable to save all parameters used"""
    # FIle
    file_name = models.TextField()
    label = models.TextField()
    is_geographical_coordinates = models.BooleanField()

    # Stay Point
    distance_threshold = models.FloatField()
    time_threshold = models.FloatField()

    # Detect Contact
    radius_threshold = models.FloatField()

    # Quadrant Entropy
    quadrant_parts = models.FloatField()
    
class MetricsModel(models.Model):
    """ Model responsable to save all metrics data from each entity"""
    # File
    file_name = models.TextField()
    label = models.TextField()
    entity_id = models.IntegerField()

    #utils
    x_center = models.FloatField()
    y_center = models.FloatField()
    z_center = models.FloatField()

    # Travel Metrics
    travel_time = models.FloatField()
    travel_distance = models.FloatField()
    travel_avg_speed = models.FloatField()
    radius_of_gyration = models.FloatField()
    spatial_cover = models.IntegerField(null=True, blank=True)

    # Stay Point Metrics
    stay_points_visits = models.IntegerField(null=True, blank=True)
    avg_time_visit = models.FloatField(null=True, blank=True)

    # Jurnay Metrics
    num_jurnays = models.IntegerField(null=True, blank=True)
    avg_jurnay_time = models.FloatField(null=True, blank=True)
    avg_jurnay_distance = models.FloatField(null=True, blank=True)
    avg_jurnay_avg_speed = models.FloatField(null=True, blank=True)

class GlobalMetricsModel(models.Model):
    """ Model responsable to save all metrics data from the trace"""
    # File
    file_name = models.TextField()
    label = models.TextField()

    # Utils
    avg_x_center = models.FloatField()
    avg_y_center = models.FloatField()
    avg_z_center = models.FloatField()

    # Travel Metrics
    avg_travel_time = models.FloatField()
    avg_travel_distance = models.FloatField()
    avg_travel_avg_speed = models.FloatField()
    avg_radius_of_gyration = models.FloatField()

    # Stay Point Metrics
    num_stay_points = models.IntegerField()
    avg_num_stay_points_visits = models.FloatField()
    stay_points_visits = models.IntegerField()
    avg_stay_point_entropy = models.FloatField()
    
    # Quadrant Metrics
    avg_quadrant_entropy = models.FloatField()

    # Contact Metrics
    num_contacts = models.IntegerField()

    # Jurnay Metrics
    total_num_jurnays = models.IntegerField()
    total_avg_jurnay_time = models.FloatField()
    total_avg_jurnay_distance = models.FloatField()
    total_avg_jurnay_avg_speed = models.FloatField()

    # Other Spatial Metrics
    trajectory_correlation = models.FloatField(null=True, blank=True)
    total_spatial_cover = models.IntegerField(null=True, blank=True)
    mobility_profile = models.FloatField(null=True, blank=True)

class StayPointModel(models.Model):
    """ Model responsable to save all Stay Points"""
    # File
    file_name = models.TextField()

    # Stay Point
    stay_point_id = models.IntegerField()
    x_center = models.FloatField()
    y_center = models.FloatField()
    z_center = models.FloatField()

    # Metrics
    num_visits = models.IntegerField()
    total_visits_time = models.FloatField(null=True, blank=True)
    entropy = models.FloatField(null=True, blank=True)
    importance_degree = models.FloatField(null=True, blank=True)

class JurnayModel(models.Model):
    """ Model responsable to save all Travels"""
    #File
    file_name = models.TextField()

    # Entity
    entity_id = models.IntegerField()

    # Stay Point
    lev_id = models.IntegerField()  # Stay Point that entity leave
    arv_id = models.IntegerField()  # Stay Point that entity arrival
    
    # Metrics
    jurnay_time = models.FloatField()
    jurnay_distance = models.FloatField()
    jurnay_avg_speed = models.FloatField()

class VisitModel(models.Model):
    """ Model responsable to save all Stay Point Visits"""
    #File
    file_name = models.TextField()

    # Entity
    entity_id = models.IntegerField()

    # Visit
    stay_point_id = models.IntegerField()
    arv_time = models.FloatField()
    lev_time = models.FloatField()
    
    # Metrics
    visit_time = models.FloatField()

class ContactModel(models.Model):
    """ Model responsable to save all contacts detected"""
    # File
    file_name = models.TextField()

    #Contacts Entity and Position
    id_1 = models.IntegerField()
    x_id_1 = models.FloatField()
    y_id_1 = models.FloatField()
    z_id_1 = models.FloatField()

    id_2 = models.IntegerField()
    x_id_2 = models.FloatField()
    y_id_2 = models.FloatField()
    z_id_2 = models.FloatField()

    contact_timestamp = models.FloatField()

class QuadrantEntropyModel(models.Model):
    """ Model responsable to save all quadrants"""
    # File
    file_name = models.TextField()

    # Entity (None represents all entities from a trace)
    entity_id = models.IntegerField(null=True, blank=True)

    # Quadrant
    x        = models.IntegerField()
    y        = models.IntegerField()

    # Metrics
    visit_count = models.IntegerField()
    entropy  = models.FloatField()
    spatial_cover = models.IntegerField(null=True)
