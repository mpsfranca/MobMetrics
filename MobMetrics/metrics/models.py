# Related third party imports.
from django.db import models

class ConfigModel(models.Model):
    """Model responsible for saving all configuration parameters used."""
    
    # File
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
    """Model responsible for saving all metrics data for each entity."""
    
    # File
    file_name = models.TextField()
    label = models.TextField()
    entity_id = models.IntegerField()

    # Utils
    x_center = models.FloatField()
    y_center = models.FloatField()
    z_center = models.FloatField()

    # Travel Metrics
    travel_time = models.FloatField()
    travel_distance = models.FloatField()
    travel_avg_speed = models.FloatField()
    travel_avg_angle_dirct = models.FloatField()
    radius_of_gyration = models.FloatField()
    spatial_cover = models.IntegerField(null=True, blank=True)

    # Variation Coefficients
    angle_variation_coefficient = models.FloatField()
    distance_variation_coefficient = models.FloatField(null=True, blank=True)
    
    # Stay Points Metrics
    stay_points_visits = models.IntegerField(null=True, blank=True)
    avg_time_visit = models.FloatField(null=True, blank=True)
    visit_time_variation_coefficient = models.FloatField(null=True, blank=True)
    
    # Journey Metrics
    num_journeys = models.IntegerField(null=True, blank=True)
    avg_journey_time = models.FloatField(null=True, blank=True)
    avg_journey_distance = models.FloatField(null=True, blank=True)
    avg_journey_avg_speed = models.FloatField(null=True, blank=True)

class GlobalMetricsModel(models.Model):
    """Model responsible for saving all global metrics data from the trace."""

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

    # Journey Metrics
    total_num_journeys = models.IntegerField()
    total_avg_journey_time = models.FloatField()
    total_avg_journey_distance = models.FloatField()
    total_avg_journey_avg_speed = models.FloatField()

    # Other Spatial Metrics
    trajectory_correlation = models.FloatField(null=True, blank=True)
    total_spatial_cover = models.IntegerField(null=True, blank=True)
    mobility_profile = models.FloatField(null=True, blank=True)

    # Other Temporal Metrics
    speed_variation_coefficient = models.FloatField(null=True, blank=True)


class StayPointModel(models.Model):
    """Model responsible for saving all Stay Points."""

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


class JourneyModel(models.Model):
    """Model responsible for saving all Journeys (travels between stay points)."""

    # File
    file_name = models.TextField()

    # Entity
    entity_id = models.IntegerField()

    # Stay Point
    lev_id = models.IntegerField()  # Stay Point that entity left
    arv_id = models.IntegerField()  # Stay Point that entity arrived

    # Metrics
    journey_time = models.FloatField()
    journey_distance = models.FloatField()
    journey_avg_speed = models.FloatField()


class VisitModel(models.Model):
    """Model responsible for saving all Stay Point visits."""

    # File
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
    """Model responsible for saving all detected contacts."""

    # File
    file_name = models.TextField()

    # Contacts Entity
    id1 = models.IntegerField()
    id2 = models.IntegerField()

    initial_timestamp = models.FloatField()
    final_timestamp = models.FloatField()

    contact_time = models.FloatField()


class QuadrantEntropyModel(models.Model):
    """Model responsible for saving all quadrant entropy data."""

    # File
    file_name = models.TextField()

    # Entity (None represents all entities from a trace)
    entity_id = models.IntegerField(null=True, blank=True)

    # Quadrant
    x = models.IntegerField()
    y = models.IntegerField()

    # Metrics
    visit_count = models.IntegerField()
    entropy = models.FloatField()
    spatial_cover = models.IntegerField(null=True)
