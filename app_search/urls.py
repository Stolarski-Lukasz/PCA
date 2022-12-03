from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search, name='search'),
    path('pagination/', views.pagination, name='pagination'),
    path('create_audio/', views.create_audio, name='create_audio')
]