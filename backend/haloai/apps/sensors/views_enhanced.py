"""
Enhanced Sensors Views
Role-based access control for IoT sensor management
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from services.firebase_service_refactored import firebase_service
from services.crop_prediction_service import EnhancedCropPredictionService
from apps.users.models import FarmerProfile
from .models import IoTSensorSet, SensorReading
import json
import uuid


def is_community_admin_or_admin(user):
    """Check if user is community admin or system admin"""
    return (
        user.is_authenticated
        and hasattr(user, "role")
        and user.role in ["community_admin", "admin"]
    )


def is_community_admin(user):
    """Check if user is community admin"""
    return (
        user.is_authenticated
        and hasattr(user, "role")
        and user.role == "community_admin"
    )


@login_required
@user_passes_test(is_community_admin_or_admin)
def sensor_dashboard(request):
    """Enhanced sensor dashboard for community admins"""
    user = request.user

    # Get sensors based on user role
    if user.role == "community_admin":
        managed_sensors = IoTSensorSet.objects.filter(community_admin=user).order_by(
            "-created_at"
        )
        region = user.assigned_region or "Bhairahawa-Butwal"
        page_title = f"My Sensor Dashboard - {region}"
    else:  # admin
        managed_sensors = IoTSensorSet.objects.all().order_by("-created_at")
        region = "All Regions"
        page_title = "System Sensor Dashboard"

    # Get regional analytics
    regional_analytics = firebase_service.get_regional_summary(region)

    # Get recent predictions
    recent_predictions = []
    if user.role == "community_admin":
        recent_predictions = firebase_service.get_admin_predictions(str(user.id), 5)

    # Get alerts (sensors with no recent data)
    alerts = []
    for sensor in managed_sensors.filter(status="active")[:5]:
        latest_readings = firebase_service.get_latest_sensor_readings(
            str(user.id), str(sensor.id)
        )
        if not latest_readings:
            alerts.append(
                {
                    "type": "warning",
                    "message": f"No recent data from {sensor.name} at {sensor.location_name}",
                    "sensor_id": sensor.id,
                }
            )

    context = {
        "page_title": page_title,
        "managed_sensors": managed_sensors[:8],
        "total_sensors": managed_sensors.count(),
        "active_sensors": managed_sensors.filter(status="active").count(),
        "region": region,
        "regional_analytics": regional_analytics,
        "recent_predictions": recent_predictions,
        "alerts": alerts,
        "user": user,
    }

    return render(request, "sensors/dashboard.html", context)


@login_required
@user_passes_test(is_community_admin_or_admin)
def manage_sensors(request):
    """Manage IoT sensor sets"""
    user = request.user

    if user.role == "community_admin":
        sensors = IoTSensorSet.objects.filter(community_admin=user).order_by(
            "-created_at"
        )
    else:
        sensors = IoTSensorSet.objects.all().order_by("-created_at")

    # Pagination
    paginator = Paginator(sensors, 12)
    page_number = request.GET.get("page")
    sensors_page = paginator.get_page(page_number)

    context = {
        "page_title": "Manage Sensors",
        "sensors": sensors_page,
        "user": user,
    }

    return render(request, "sensors/manage_sensors.html", context)


@login_required
@user_passes_test(is_community_admin)
def add_sensor_set(request):
    """Add new IoT sensor set"""
    if request.method == "POST":
        try:
            # Create new sensor set
            sensor_set = IoTSensorSet.objects.create(
                name=request.POST.get("name"),
                community_admin=request.user,
                location_name=request.POST.get("location_name"),
                latitude=(
                    float(request.POST.get("latitude", 0))
                    if request.POST.get("latitude")
                    else None
                ),
                longitude=(
                    float(request.POST.get("longitude", 0))
                    if request.POST.get("longitude")
                    else None
                ),
                region=request.user.assigned_region or "Bhairahawa-Butwal",
                status="active",
                default_nitrogen=float(request.POST.get("default_nitrogen", 85.0)),
                default_phosphorus=float(request.POST.get("default_phosphorus", 50.0)),
                default_potassium=float(request.POST.get("default_potassium", 40.0)),
            )

            # Store metadata in Firebase
            firebase_service.firebase_service.store_sensor_metadata(
                str(request.user.id),
                str(sensor_set.id),
                {
                    "name": sensor_set.name,
                    "location": sensor_set.location_name,
                    "region": sensor_set.region,
                    "status": sensor_set.status,
                },
            )

            # Create demo data for pitch
            firebase_service.create_demo_data(str(request.user.id), sensor_set.region)

            messages.success(
                request, f'Sensor set "{sensor_set.name}" added successfully!'
            )
            return redirect("sensors:manage_sensors")

        except Exception as e:
            messages.error(request, f"Error adding sensor set: {e}")

    context = {
        "page_title": "Add Sensor Set",
        "default_region": request.user.assigned_region or "Bhairahawa-Butwal",
    }

    return render(request, "sensors/add_sensor_set.html", context)


@login_required
@user_passes_test(is_community_admin_or_admin)
def sensor_detail(request, sensor_id):
    """Detailed view of a sensor set with real-time data"""
    user = request.user

    # Get sensor set with permission check
    if user.role == "community_admin":
        sensor_set = get_object_or_404(IoTSensorSet, id=sensor_id, community_admin=user)
    else:
        sensor_set = get_object_or_404(IoTSensorSet, id=sensor_id)

    # Get latest sensor readings
    latest_readings = firebase_service.get_latest_sensor_readings(
        str(sensor_set.community_admin.id), str(sensor_set.id)
    )

    # Get historical data for charts
    historical_data = {}
    for sensor_type in ["temperature", "humidity", "ph"]:
        readings = SensorReading.objects.filter(
            sensor_set=sensor_set, sensor_type=sensor_type
        ).order_by("-timestamp")[
            :24
        ]  # Last 24 readings

        historical_data[sensor_type] = [
            {
                "timestamp": reading.timestamp.isoformat(),
                "value": reading.value,
                "unit": reading.unit,
            }
            for reading in readings
        ]

    context = {
        "page_title": f"Sensor Details - {sensor_set.name}",
        "sensor_set": sensor_set,
        "latest_readings": latest_readings,
        "historical_data": json.dumps(historical_data),
        "user": user,
    }

    return render(request, "sensors/sensor_detail.html", context)


@login_required
@user_passes_test(is_community_admin)
def request_crop_prediction(request, sensor_id):
    """Request crop prediction for a sensor set"""
    sensor_set = get_object_or_404(
        IoTSensorSet, id=sensor_id, community_admin=request.user
    )

    if request.method == "POST":
        try:
            prediction_service = EnhancedCropPredictionService()
            prediction_request = prediction_service.create_prediction_request(
                str(request.user.id), str(sensor_set.id)
            )

            if prediction_request:
                messages.success(
                    request, "Crop prediction request submitted successfully!"
                )
                return redirect("crops:crop_prediction")
            else:
                messages.error(request, "Failed to create prediction request.")

        except Exception as e:
            messages.error(request, f"Error requesting prediction: {e}")

    return redirect("sensors:sensor_detail", sensor_id=sensor_id)


# ==== API ENDPOINTS ====


@login_required
@require_http_methods(["GET"])
def api_sensor_data(request, sensor_id, sensor_type):
    """API endpoint to get latest sensor data"""
    try:
        user = request.user

        # Permission check
        if user.role == "community_admin":
            sensor_set = IoTSensorSet.objects.get(id=sensor_id, community_admin=user)
        else:
            sensor_set = IoTSensorSet.objects.get(id=sensor_id)

        # Get latest reading for specific sensor type
        latest_readings = firebase_service.get_latest_sensor_readings(
            str(sensor_set.community_admin.id), str(sensor_set.id)
        )

        if sensor_type in latest_readings:
            return JsonResponse({"success": True, "data": latest_readings[sensor_type]})
        else:
            return JsonResponse(
                {"success": False, "error": "No data available for this sensor type"}
            )

    except IoTSensorSet.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Sensor not found or access denied"}
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_http_methods(["GET"])
def api_sensor_history(request, sensor_id, sensor_type):
    """API endpoint to get sensor history"""
    try:
        user = request.user

        # Permission check
        if user.role == "community_admin":
            sensor_set = IoTSensorSet.objects.get(id=sensor_id, community_admin=user)
        else:
            sensor_set = IoTSensorSet.objects.get(id=sensor_id)

        # Get historical readings
        readings = SensorReading.objects.filter(
            sensor_set=sensor_set, sensor_type=sensor_type
        ).order_by("-timestamp")[:50]

        history_data = [
            {
                "timestamp": reading.timestamp.isoformat(),
                "value": reading.value,
                "unit": reading.unit,
                "quality_score": reading.quality_score,
            }
            for reading in readings
        ]

        return JsonResponse({"success": True, "data": history_data})

    except IoTSensorSet.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Sensor not found or access denied"}
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@user_passes_test(is_community_admin_or_admin)
def real_time_monitor(request):
    """Real-time monitoring dashboard"""
    user = request.user

    if user.role == "community_admin":
        sensors = IoTSensorSet.objects.filter(
            community_admin=user, status="active"
        ).order_by("name")
        region = user.assigned_region or "Bhairahawa-Butwal"
    else:
        sensors = IoTSensorSet.objects.filter(status="active").order_by("name")
        region = "All Regions"

    context = {
        "page_title": f"Real-time Monitor - {region}",
        "sensors": sensors,
        "region": region,
        "user": user,
    }

    return render(request, "sensors/real_time_monitor.html", context)
