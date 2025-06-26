from django.urls import path
from . import views

app_name = "sensors"

urlpatterns = [
    # Main dashboard
    path("", views.sensor_dashboard, name="dashboard"),
    # Device management
    path("device/<str:device_id>/", views.device_detail, name="device_detail"),
    path("group/<int:group_id>/", views.device_group_detail, name="group_detail"),
    # Map and alerts
    path("map/", views.map_view, name="map"),
    path("alerts/", views.alerts_view, name="alerts"),
    # API endpoints
    path("api/device/<str:device_id>/", views.api_device_data, name="api_device_data"),
    path(
        "api/device/<str:device_id>/history/",
        views.api_device_history,
        name="api_device_history",
    ),
    path("api/region/", views.api_region_devices, name="api_region_devices"),
    path("api/alerts/", views.api_alerts, name="api_alerts"),
]
