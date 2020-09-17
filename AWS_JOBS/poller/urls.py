
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home-poller"),
    path('createDetails/', views.details, name="create-details"),
    
]
