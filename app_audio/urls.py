from django.urls import path
from . import views

urlpatterns = [
    path('create_audio/', views.create_audio, name='create_audio')
]