# meu_projeto/app_name/admin.py
from django.contrib import admin
from .models import MetricsModel, StayPointModel, TraceModel, TravelsModel, VisitModel

admin.site.register(MetricsModel)
admin.site.register(StayPointModel)
admin.site.register(TraceModel)
admin.site.register(TravelsModel)
admin.site.register(VisitModel)
