# meu_projeto/app_name/admin.py
from django.contrib import admin
from .models import ConfigModel ,MetricsModel, StayPointModel, TravelsModel, VisitModel, ContactModel, QuadrantEntropyModel, GlobalMetricsModel

admin.site.register(ConfigModel)
admin.site.register(MetricsModel)
admin.site.register(StayPointModel)
admin.site.register(TravelsModel)
admin.site.register(VisitModel)
admin.site.register(ContactModel)
admin.site.register(QuadrantEntropyModel)
admin.site.register(GlobalMetricsModel)

