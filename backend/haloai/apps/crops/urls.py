from django.urls import path
from . import views_enhanced as views

app_name = "crops"

urlpatterns = [
    # Main dashboard and management
    path("", views.crop_prediction_dashboard, name="dashboard"),
    path("create/", views.create_prediction, name="create_prediction"),
    path("history/", views.prediction_history, name="prediction_history"),
    path("insights/", views.regional_insights, name="regional_insights"),
    # Prediction details
    path(
        "prediction/<uuid:prediction_id>/",
        views.prediction_detail,
        name="prediction_detail",
    ),
    # API endpoints
    path("api/create/", views.api_create_prediction, name="api_create_prediction"),
    path(
        "api/status/<uuid:prediction_id>/",
        views.api_prediction_status,
        name="api_prediction_status",
    ),
    # Legacy redirect
    path("crop_prediction/", views.crop_prediction, name="crop_prediction"),
]
