from django.urls import path
from . import views
from . import enhanced_api_views

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
    # Legacy API endpoints
    path("api/device/<str:device_id>/", views.api_device_data, name="api_device_data"),
    path(
        "api/device/<str:device_id>/history/",
        views.api_device_history,
        name="api_device_history",
    ),
    path("api/region/", views.api_region_devices, name="api_region_devices"),
    path("api/alerts/", views.api_alerts, name="api_alerts"),
    # Enhanced IoT API endpoints
    path(
        "api/enhanced/sensor/",
        enhanced_api_views.get_sensor_data,
        name="api_enhanced_sensor",
    ),
    path(
        "api/enhanced/sensors/all/",
        enhanced_api_views.get_all_sensors_data,
        name="api_enhanced_all_sensors",
    ),
    path(
        "api/enhanced/regional/",
        enhanced_api_views.get_regional_data,
        name="api_enhanced_regional",
    ),
    path(
        "api/enhanced/health/",
        enhanced_api_views.get_sensor_health,
        name="api_enhanced_health",
    ),
    path(
        "api/enhanced/history/",
        enhanced_api_views.get_sensor_history,
        name="api_enhanced_history",
    ),
    path(
        "api/enhanced/realtime/",
        enhanced_api_views.get_enhanced_realtime_data,
        name="api_enhanced_realtime",
    ),
    # NEW: Real-time endpoints that bypass cache
    path(
        "api/enhanced/live/",
        enhanced_api_views.get_realtime_sensor_data,
        name="api_enhanced_live",
    ),
    path(
        "api/enhanced/stream/",
        enhanced_api_views.get_continuous_sensor_stream,
        name="api_enhanced_stream",
    ),
    path(
        "api/enhanced/demo/",
        enhanced_api_views.create_demo_data,
        name="api_enhanced_demo",
    ),
    path(
        "api/enhanced/diagnostics/",
        enhanced_api_views.system_diagnostics,
        name="api_enhanced_diagnostics",
    ),
    # Real-time dashboard
    path(
        "dashboard/realtime/",
        enhanced_api_views.realtime_dashboard,
        name="realtime_dashboard",
    ),
]
