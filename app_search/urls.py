from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search, name='search'),
    path('previous_button/', views.previous_button, name='previous_button'),
    path('next_button/', views.next_button, name='next_button'),
    path('create_audio/', views.create_audio, name='create_audio')
]