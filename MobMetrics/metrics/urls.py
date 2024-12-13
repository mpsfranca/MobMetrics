from django.urls import path
from .views import upload_view, success_view

urlpatterns = [
    path('upload/', upload_view, name='upload'),
    path('success/', success_view, name='success')
]
