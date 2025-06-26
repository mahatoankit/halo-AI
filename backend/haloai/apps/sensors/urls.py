from django.urls import path
from . import views_enhanced as views

app_name = "sensors"

urlpatterns = [
    # Dashboard and management
    path("", views.sensor_dashboard, name="dashboard"),
    path("manage/", views.manage_sensors, name="manage_sensors"),
    path("add/", views.add_sensor_set, name="add_sensor_set"),
    # Sensor details and monitoring
    path("detail/<uuid:sensor_id>/", views.sensor_detail, name="sensor_detail"),
    path("monitor/", views.real_time_monitor, name="real_time_monitor"),
    # Crop prediction integration
    path(
        "predict/<uuid:sensor_id>/",
        views.request_crop_prediction,
        name="request_crop_prediction",
    ),
    # API endpoints
    path(
        "api/sensor/<uuid:sensor_id>/<str:sensor_type>/",
        views.api_sensor_data,
        name="api_sensor_data",
    ),
    path(
        "api/sensor/<uuid:sensor_id>/<str:sensor_type>/history/",
        views.api_sensor_history,
        name="api_sensor_history",
    ),
]
