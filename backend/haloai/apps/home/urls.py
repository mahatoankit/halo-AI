from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.public_landing, name="public_landing"),
    path("index/", views.public_landing, name="index"),  # Add missing index pattern
    path("dashboard/", views.home, name="home"),
]
