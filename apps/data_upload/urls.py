"""
Data Upload App URL Configuration

Provides unified file upload interface
"""
from django.urls import path
from . import views

app_name = 'data_upload'

urlpatterns = [
    path('upload/', views.upload_csv_view, name='upload_csv'),
]
