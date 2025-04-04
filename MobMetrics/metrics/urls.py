from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_view, name='upload'),
    path('delete/', views.delete_view, name='delete'),
    path('DataAnalytics/', views.data_analytics_view, name='DataAnalytics'),
]
