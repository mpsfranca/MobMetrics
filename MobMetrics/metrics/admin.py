# meu_projeto/app_name/admin.py
from django.contrib import admin
from .models import MetricsModel, StayPointModel, TraceModel, TravelsModel

admin.site.register(MetricsModel)
admin.site.register(StayPointModel)
admin.site.register(TraceModel)
admin.site.register(TravelsModel)
