from django.db import models

class ConfigModel(models.Model):
    fileName          = models.TextField()
    label             = models.TextField()

    distanceThreshold = models.FloatField()
    timeThreshold     = models.FloatField()
    radiusThreshold   = models.FloatField()
    quadrantSize      = models.FloatField()

class MetricsModel(models.Model):
    fileName               = models.TextField()
    label                  = models.TextField()
    entityId               = models.IntegerField()

    TTrvT                  = models.FloatField()
    TTrvD                  = models.FloatField()
    TTrvAS                 = models.FloatField()
    x_center               = models.FloatField()
    y_center               = models.FloatField()
    z_center               = models.FloatField()
    radius                 = models.FloatField()

    numStayPointsVisits  = models.IntegerField(null=True, blank=True)
    avgTimeVisit     = models.FloatField(null=True, blank=True)

    num_travels           = models.IntegerField(null=True, blank=True)
    avg_travel_time       = models.FloatField(null=True, blank=True)
    avg_travel_distance   = models.FloatField(null=True, blank=True)
    avg_travel_avg_speed  = models.FloatField(null=True, blank=True)

class GlobalMetricsModel(models.Model):
    fileName               = models.TextField()
    label                  = models.TextField()

    avgTTrvT                  = models.FloatField()
    avgTTrvD                  = models.FloatField()
    avgTTrvAS                 = models.FloatField()
    avgX_center               = models.FloatField()
    avgY_center               = models.FloatField()
    avgZ_center               = models.FloatField()
    avgRadius                 = models.FloatField()

    numStayPoints = models.IntegerField()
    avgNumStayPointsVisitsPerEtity  = models.FloatField()
    NumStayPointsVisits = models.IntegerField()
    avgStayPointEntropy = models.FloatField()
    
    avgQuadrantEntropy = models.FloatField()

    numContacts = models.IntegerField()

    num_travels           = models.IntegerField()
    avg_travel_time       = models.FloatField()
    avg_travel_distance   = models.FloatField()
    avg_travel_avg_speed  = models.FloatField()

class StayPointModel(models.Model):
    fileName    = models.TextField()

    spId        = models.IntegerField()
    x           = models.FloatField()
    y           = models.FloatField()
    z           = models.FloatField()
    numVisits   = models.IntegerField()
    entropy = models.FloatField(null=True, blank=True)


class TravelsModel(models.Model):
    fileName = models.TextField()

    entityId= models.IntegerField()
    arvId   = models.IntegerField()
    levId   = models.IntegerField()
    TrvD    = models.FloatField()
    TrvT    = models.FloatField()
    TrvAS   = models.FloatField()

class VisitModel(models.Model):
    fileName = models.TextField()

    entityId= models.IntegerField()
    spId    = models.IntegerField()
    arvT    = models.IntegerField()
    levT    = models.IntegerField()
    visitT  = models.FloatField()

class ContactModel(models.Model):
    fileName = models.TextField()

    id1 = models.IntegerField()
    id2 = models.IntegerField()

    contact_timestamp = models.FloatField()

    start_x_id_1 = models.FloatField()
    start_x_id_2 = models.FloatField()
    start_y_id_1 = models.FloatField()
    start_y_id_2 = models.FloatField()
    start_z_id_1 = models.FloatField()
    start_z_id_2 = models.FloatField()

    end_x_id_1 = models.FloatField()
    end_x_id_2 = models.FloatField()
    end_y_id_1 = models.FloatField()
    end_y_id_2 = models.FloatField()
    end_z_id_1 = models.FloatField()
    end_z_id_2 = models.FloatField()

class QuadrantEntropyModel(models.Model):
    fileName = models.TextField()

    x        = models.IntegerField()
    y        = models.IntegerField()
    entropy  = models.FloatField()