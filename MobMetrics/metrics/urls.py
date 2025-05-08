# Related third party imports.
from django.urls import path

# Local application/library specific imports.
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # Main view
]
