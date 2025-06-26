from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "dashboard"

urlpatterns = [
    # Role-based dashboard redirect
    path("redirect/", views.role_based_dashboard_redirect, name="redirect"),
    # Community/Admin Dashboard
    path("", views.community_dashboard, name="home"),
    path("index/", views.community_dashboard, name="index"),
    # Farmer Dashboard
    path("farmer/", views.farmer_dashboard, name="farmer_dashboard"),
    path("farmer/predictions/", views.prediction_history, name="prediction_history"),
    path("farmer/sensors/", views.sensor_data_history, name="sensor_history"),
    path(
        "farmer/subscription/", views.subscription_details, name="subscription_details"
    ),
    path("farmer/manual-input/", views.manual_input_form, name="manual_input"),
    path(
        "farmer/expert-consultation/",
        views.expert_consultation_request,
        name="expert_consultation",
    ),
]
