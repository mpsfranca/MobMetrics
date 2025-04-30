from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('delete/', views.delete_view, name='delete'),
    path('download/', views.download_zip_view, name='download'),
    path('DataAnalytics/', views.data_analytics_view, name='DataAnalytics'),
]
