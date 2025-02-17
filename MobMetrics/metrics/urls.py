from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_view, name='upload'),
    path('success/', views.success_view, name='success'),
    path('pca/', views.pca_view, name='pca'),
]
