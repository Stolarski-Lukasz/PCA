from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='init_home'),
    path('home/', views.home, name='home'),
    path('documentation/', views.documentation, name='documentation'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('contact/', views.contact, name='contact')
]