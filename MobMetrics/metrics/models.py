from django.db import models

class MetricsModel(models.Model):
    entityId= models.IntegerField()
    TTrvT   = models.FloatField()
    TTrvD   = models.FloatField()
    TTrvAS  = models.FloatField()
    x       = models.FloatField()
    y       = models.FloatField()
    z       = models.FloatField()
    radius  = models.FloatField()

class StayPointModel(models.Model):
    entityId    = models.IntegerField()
    spId        = models.IntegerField()
    x           = models.FloatField()
    y           = models.FloatField()
    z           = models.FloatField()
    arvT        = models.FloatField()
    levT        = models.FloatField()
    visitTime   = models.FloatField()

class TraceModel(models.Model):
    entityId= models.IntegerField()
    x       = models.FloatField()
    y       = models.FloatField()
    z       = models.FloatField()
    time    = models.FloatField()
    spId    = models.IntegerField()


class TravelsModel(models.Model):
    entityId= models.IntegerField()
    arvId   = models.IntegerField()
    levId   = models.IntegerField()
    TrvD    = models.FloatField()
    TrvT    = models.FloatField()
    TrvAS   = models.FloatField()
