# Related third party imports.
from django.db import models

class ConfigModel(models.Model):
    """ Model responsable to save all parameters used"""
    # FIle
    fileName          = models.TextField()
    label             = models.TextField()
    isGeographicalCoordinates = models.BooleanField()

    # Stay Point
    distanceThreshold = models.FloatField()
    timeThreshold     = models.FloatField()

    # Detect Contact
    radiusThreshold   = models.FloatField()

    # Quadrant Entropy
    quadrantSize      = models.FloatField()
    
class MetricsModel(models.Model):
    """ Model responsable to save all metrics data from each entity"""
    # File
    fileName = models.TextField()
    label = models.TextField()
    entityId = models.IntegerField()

    # Total Travel Metrics
    TTrvT = models.FloatField()
    TTrvD = models.FloatField()
    TTrvAS = models.FloatField()
    x_center = models.FloatField()
    y_center = models.FloatField()
    z_center = models.FloatField()
    radius = models.FloatField()
    occupied_quadrants = models.IntegerField(null=True, blank=True)

    # Stay Point Metrics
    numStayPointsVisits = models.IntegerField(null=True, blank=True)
    avgTimeVisit = models.FloatField(null=True, blank=True)

    # Travel Metrics
    num_travels = models.IntegerField(null=True, blank=True)
    avg_travel_time = models.FloatField(null=True, blank=True)
    avg_travel_distance = models.FloatField(null=True, blank=True)
    avg_travel_avg_speed = models.FloatField(null=True, blank=True)

class GlobalMetricsModel(models.Model):
    """ Model responsable to save all metrics data from the trace"""
    # File
    fileName = models.TextField()
    label = models.TextField()

    # Total Travel Metrics
    avgTTrvT = models.FloatField()
    avgTTrvD = models.FloatField()
    avgTTrvAS = models.FloatField()
    avgX_center = models.FloatField()
    avgY_center = models.FloatField()
    avgZ_center = models.FloatField()
    avgRadius = models.FloatField()
    occupied_quadrants = models.IntegerField(null=True, blank=True)

    # Stay Point Metrics
    numStayPoints = models.IntegerField()
    avgNumStayPointsVisitsPerEtity  = models.FloatField()
    NumStayPointsVisits = models.IntegerField()
    avgStayPointEntropy = models.FloatField()
    
    # Quadrant Metrics
    avgQuadrantEntropy = models.FloatField()

    # Contact Metrics
    numContacts = models.IntegerField()

    # Travel Metrics
    num_travels = models.IntegerField()
    avg_travel_time = models.FloatField()
    avg_travel_distance = models.FloatField()
    avg_travel_avg_speed = models.FloatField()

    occupied_quadrants = models.IntegerField(null=True, blank=True)
    mobility_profile = models.FloatField(null=True, blank=True)

    # Other Spatial Metrics
    trajectory_correlation = models.FloatField(null=True, blank=True)

    # Other Temporal Metric
    visit_time_variation_coefficient = models.FloatField(null=True, blank=True)

class StayPointModel(models.Model):
    """ Model responsable to save all Stay Points"""
    # File
    fileName = models.TextField()

    # Stay Point
    spId        = models.IntegerField()
    x           = models.FloatField()
    y           = models.FloatField()
    z           = models.FloatField()

    # Metrics
    numVisits   = models.IntegerField()
    entropy = models.FloatField(null=True, blank=True)
    totalVisitsTime = models.FloatField(null=True, blank=True)
    importanceDegree = models.FloatField(null=True, blank=True)

class TravelsModel(models.Model):
    """ Model responsable to save all Travels"""
    #File
    fileName = models.TextField()

    # Entity
    entityId= models.IntegerField()

    # Travel
    arvId   = models.IntegerField()
    levId   = models.IntegerField()
    
    # Metrics
    TrvD    = models.FloatField()
    TrvT    = models.FloatField()
    TrvAS   = models.FloatField()

class VisitModel(models.Model):
    """ Model responsable to save all Stay Point Visits"""
    #File
    fileName = models.TextField()

    # Entity
    entityId= models.IntegerField()

    # Visit
    spId    = models.IntegerField()
    arvT    = models.FloatField()
    levT    = models.FloatField()
    
    # Metrics
    visitT  = models.FloatField()

class ContactModel(models.Model):
    """ Model responsable to save all contacts detected"""
    # File
    fileName = models.TextField()

    #Contacts Entity and Position
    id1 = models.IntegerField()
    x_id_1 = models.FloatField()
    y_id_1 = models.FloatField()
    z_id_1 = models.FloatField()

    id2 = models.IntegerField()
    x_id_2 = models.FloatField()
    y_id_2 = models.FloatField()
    z_id_2 = models.FloatField()

    contact_timestamp = models.FloatField()

class QuadrantEntropyModel(models.Model):
    """ Model responsable to save all quadrants"""
    # File
    fileName = models.TextField()

    # Entity (None represents all entities from a trace)
    entity_id = models.IntegerField(null=True, blank=True)

    # Quadrant
    x        = models.IntegerField()
    y        = models.IntegerField()

    # Metrics
    visit_count = models.IntegerField()
    entropy  = models.FloatField()
    occupied_quadrants = models.IntegerField(null=True)
