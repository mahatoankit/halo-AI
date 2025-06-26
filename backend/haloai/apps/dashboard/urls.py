from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.community_dashboard, name="home"),
    # Add index pattern in case it's needed
    path("index/", views.community_dashboard, name="index"),
]
