# beacon/urls.py
from django.urls import path
from .views import SetBeaconsView, home

urlpatterns = [
    path('api/setBeacons', SetBeaconsView.as_view(), name='set_beacons'),
    path('', home, name='home'),  # Add home page route
]
