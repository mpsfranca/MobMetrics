from django.db import models

class ConfigModel(models.Model):
    fileName          = models.TextField()
    label             = models.TextField()

    distanceThreshold = models.FloatField()
    timeThreshold     = models.FloatField()
    radiusThreshold   = models.FloatField()

class MetricsModel(models.Model):
    fileName= models.TextField()
    
    entityId= models.IntegerField()
    TTrvT   = models.FloatField()
    TTrvD   = models.FloatField()
    TTrvAS  = models.FloatField()
    x_center= models.FloatField()
    y_center= models.FloatField()
    z_center= models.FloatField()
    radius  = models.FloatField()

    """
    num_stay_points_visits = models.IntegerField()  # Number of Stay Points Visits
    avg_entropy = models.FloatField()  # Average Entropy
    avg_time_of_visit = models.FloatField()  # Average Time of Visit
    num_travels = models.IntegerField()  # Number of Travels
    avg_travel_time = models.FloatField()  # Average Travel Time
    avg_travel_distance = models.FloatField()  # Average Travel Distance
    avg_travel_speed = models.FloatField()  # Average Travel Speed
    num_contacts = models.IntegerField()  # Number of Contacts
    avg_contact_time = models.FloatField()  # Average Contact Time
    """
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

    start_time = models.FloatField()
    end_time = models.FloatField()

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


