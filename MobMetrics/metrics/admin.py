from django.contrib import admin
from .models import (
    ConfigModel,
    MetricsModel,
    StayPointModel,
    TravelsModel,
    VisitModel,
    ContactModel,
    QuadrantEntropyModel,
    GlobalMetricsModel,
)

admin.site.register(ConfigModel)
admin.site.register(MetricsModel)
admin.site.register(StayPointModel)
admin.site.register(TravelsModel)
admin.site.register(ContactModel)
admin.site.register(GlobalMetricsModel)

class VisitsModelAdmin(admin.ModelAdmin):
    actions = ['delete_all_visits']

    @admin.action(description="Delete all visit logs")
    def delete_all_visits(self, request, queryset):
        total = VisitModel.objects.count()
        VisitModel.objects.all().delete()
        self.message_user(request, f"All {total} records were deleted successfully.")

class QuadrantEntropyModelAdmin(admin.ModelAdmin):
    actions = ['delete_all_quadrant_entropy']

    @admin.action(description="Delete all quadrant entropy logs")
    def delete_all_quadrant_entropy(self, request, queryset):
        total = QuadrantEntropyModel.objects.count()
        QuadrantEntropyModel.objects.all().delete()
        self.message_user(request, f"All {total} records were deleted successfully.")

admin.site.register(VisitModel, VisitsModelAdmin)
admin.site.register(QuadrantEntropyModel, QuadrantEntropyModelAdmin)
