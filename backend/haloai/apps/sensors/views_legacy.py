from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from services.firebase_service import firebase_iot_service, get_farm_sensor_data
from apps.users.models import FarmerProfile
from .models import IoTDevice, SensorData, DeviceGroup, DataAlert
import json


@login_required
def sensor_dashboard(request):
    """Main sensor dashboard view with role-based access control"""
    context = {
        "page_title": "IoT Sensor Dashboard",
        "devices": [],
        "total_devices": 0,
        "active_devices": 0,
        "recent_alerts": [],
        "device_groups": [],
        "user_role": request.user.role,
    }

    # Get devices based on user role
    if request.user.is_admin:
        # Global admin can see all devices
        devices = IoTDevice.objects.filter(is_active=True).select_related("assigned_to")
        device_groups = DeviceGroup.objects.all().select_related("owner")
        recent_alerts = DataAlert.objects.filter(status="active").select_related(
            "device"
        )[:10]

    elif request.user.is_community_admin:
        # Community admin can see devices in their region
        devices = IoTDevice.objects.filter(
            region=request.user.assigned_region, is_active=True
        ).select_related("assigned_to")
        device_groups = DeviceGroup.objects.filter(
            Q(owner=request.user) | Q(region=request.user.assigned_region)
        ).select_related("owner")
        recent_alerts = DataAlert.objects.filter(
            device__region=request.user.assigned_region, status="active"
        ).select_related("device")[:10]

    else:
        # Regular users (farmers, technicians) can only see their own devices
        devices = IoTDevice.objects.filter(
            assigned_to=request.user, is_active=True
        ).select_related("assigned_to")
        device_groups = DeviceGroup.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        ).select_related("owner")
        recent_alerts = DataAlert.objects.filter(
            device__assigned_to=request.user, status="active"
        ).select_related("device")[:10]

    # Add latest sensor readings to devices
    for device in devices:
        latest_reading = SensorData.objects.filter(device=device).first()
        device.latest_reading = latest_reading

    context.update(
        {
            "devices": devices,
            "total_devices": devices.count(),
            "active_devices": devices.filter(status="active").count(),
            "recent_alerts": recent_alerts,
            "device_groups": device_groups,
        }
    )

    return render(request, "sensors/dashboard.html", context)


@login_required
def farm_sensors(request, farm_id):
    """Detailed view of sensors for a specific farm"""
    farm_data = firebase_iot_service.get_farm_analytics(farm_id)

    context = {
        "farm_id": farm_id,
        "farm_data": farm_data,
        "sensor_types": ["soil", "weather", "crop", "irrigation"],
        "page_title": f"Farm {farm_id} Sensors",
    }

    return render(request, "sensors/farm_detail.html", context)


@login_required
@require_http_methods(["GET"])
def api_sensor_data(request, farm_id, sensor_type):
    """API endpoint to get latest sensor data"""
    try:
        sensor_data = get_farm_sensor_data(farm_id, sensor_type)

        if sensor_data:
            return JsonResponse(
                {
                    "success": True,
                    "data": sensor_data,
                    "farm_id": farm_id,
                    "sensor_type": sensor_type,
                }
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "No sensor data found",
                    "farm_id": farm_id,
                    "sensor_type": sensor_type,
                }
            )

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "error": str(e),
                "farm_id": farm_id,
                "sensor_type": sensor_type,
            }
        )


@login_required
@require_http_methods(["GET"])
def api_sensor_history(request, farm_id, sensor_type):
    """API endpoint to get sensor history"""
    try:
        limit = int(request.GET.get("limit", 50))
        history = firebase_iot_service.get_sensor_history(farm_id, sensor_type, limit)

        return JsonResponse(
            {
                "success": True,
                "data": history,
                "farm_id": farm_id,
                "sensor_type": sensor_type,
                "count": len(history),
            }
        )

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "error": str(e),
                "farm_id": farm_id,
                "sensor_type": sensor_type,
            }
        )


@login_required
@require_http_methods(["GET"])
def api_weather_data(request, location):
    """API endpoint to get weather data for a location"""
    try:
        weather_data = firebase_iot_service.get_weather_data(location)

        if weather_data:
            return JsonResponse(
                {"success": True, "data": weather_data, "location": location}
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "No weather data found",
                    "location": location,
                }
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e), "location": location})


@login_required
def real_time_monitor(request):
    """Real-time monitoring view with WebSocket support (future enhancement)"""
    context = {
        "page_title": "Real-time Sensor Monitor",
        "farms": ["farm_001", "farm_002", "farm_003"],  # Demo farms
        "sensor_types": ["soil", "weather", "crop", "irrigation"],
    }

    return render(request, "sensors/real_time.html", context)
