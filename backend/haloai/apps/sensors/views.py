from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Max
from django.utils import timezone
from datetime import timedelta
from apps.users.models import FarmerProfile
from .models import IoTDevice, SensorData, DeviceGroup, DataAlert
import json


def get_user_accessible_devices(user):
    """Get devices accessible to a user based on their role"""
    if user.is_admin:
        return IoTDevice.objects.all()
    elif user.is_community_admin:
        return IoTDevice.objects.filter(region=user.assigned_region)
    else:
        return IoTDevice.objects.filter(assigned_to=user)


def check_device_access(user, device):
    """Check if user can access a specific device"""
    return device.can_be_accessed_by(user)


@login_required
def sensor_dashboard(request):
    """Main sensor dashboard view with role-based access control"""

    # Get devices accessible to the current user
    devices_queryset = get_user_accessible_devices(request.user)

    # Add statistics
    total_devices = devices_queryset.count()
    active_devices = devices_queryset.filter(status="active").count()
    offline_devices = devices_queryset.filter(status="offline").count()
    maintenance_devices = devices_queryset.filter(status="maintenance").count()

    # Get recent devices with their latest readings
    recent_devices = devices_queryset.select_related("assigned_to").order_by(
        "-updated_at"
    )[:10]

    # Get device groups accessible to user
    if request.user.is_admin:
        device_groups = DeviceGroup.objects.all()
    elif request.user.is_community_admin:
        device_groups = DeviceGroup.objects.filter(
            Q(owner=request.user) | Q(region=request.user.assigned_region)
        )
    else:
        device_groups = DeviceGroup.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        )

    # Get recent alerts
    if request.user.is_admin:
        recent_alerts = DataAlert.objects.filter(status="active").select_related(
            "device"
        )[:10]
    elif request.user.is_community_admin:
        recent_alerts = DataAlert.objects.filter(
            device__region=request.user.assigned_region, status="active"
        ).select_related("device")[:10]
    else:
        recent_alerts = DataAlert.objects.filter(
            device__assigned_to=request.user, status="active"
        ).select_related("device")[:10]

    # Location-based statistics for admins
    region_stats = []
    if request.user.is_admin:
        region_stats = (
            IoTDevice.objects.values("region")
            .annotate(
                total=Count("id"),
                active=Count("id", filter=Q(status="active")),
                offline=Count("id", filter=Q(status="offline")),
            )
            .order_by("region")
        )

    context = {
        "page_title": "IoT Sensor Dashboard",
        "user_role": request.user.role,
        "total_devices": total_devices,
        "active_devices": active_devices,
        "offline_devices": offline_devices,
        "maintenance_devices": maintenance_devices,
        "recent_devices": recent_devices,
        "device_groups": device_groups,
        "recent_alerts": recent_alerts,
        "region_stats": region_stats,
    }

    return render(request, "sensors/dashboard.html", context)


@login_required
def device_detail(request, device_id):
    """Detailed view of a specific IoT device"""
    device = get_object_or_404(IoTDevice, device_id=device_id)

    # Check access permissions
    if not check_device_access(request.user, device):
        return HttpResponseForbidden("You don't have permission to access this device.")

    # Get recent sensor data
    recent_readings = SensorData.objects.filter(device=device).order_by("-timestamp")[
        :50
    ]

    # Get device alerts
    device_alerts = DataAlert.objects.filter(device=device).order_by("-created_at")[:10]

    # Calculate statistics
    last_24h = timezone.now() - timedelta(hours=24)
    recent_stats = SensorData.objects.filter(
        device=device, timestamp__gte=last_24h
    ).aggregate(
        avg_temp=Avg("temperature"),
        avg_humidity=Avg("humidity"),
        avg_ph=Avg("ph"),
        avg_nitrogen=Avg("nitrogen"),
        avg_phosphorus=Avg("phosphorus"),
        avg_potassium=Avg("potassium"),
        last_reading=Max("timestamp"),
    )

    context = {
        "device": device,
        "recent_readings": recent_readings,
        "device_alerts": device_alerts,
        "recent_stats": recent_stats,
        "page_title": f"Device: {device.name}",
    }

    return render(request, "sensors/device_detail.html", context)


@login_required
def device_group_detail(request, group_id):
    """Detailed view of a device group"""
    group = get_object_or_404(DeviceGroup, id=group_id)

    # Check access permissions
    can_access = (
        request.user.is_admin
        or group.owner == request.user
        or request.user in group.members.all()
        or (
            request.user.is_community_admin
            and group.region == request.user.assigned_region
        )
    )

    if not can_access:
        return HttpResponseForbidden(
            "You don't have permission to access this device group."
        )

    # Get devices in the group
    group_devices = group.devices.all().select_related("assigned_to")

    # Get group statistics
    group_stats = {
        "total_devices": group_devices.count(),
        "active_devices": group_devices.filter(status="active").count(),
        "offline_devices": group_devices.filter(status="offline").count(),
    }

    context = {
        "group": group,
        "group_devices": group_devices,
        "group_stats": group_stats,
        "page_title": f"Device Group: {group.name}",
    }

    return render(request, "sensors/group_detail.html", context)


@login_required
@require_http_methods(["GET"])
def api_device_data(request, device_id):
    """API endpoint to get latest sensor data for a device"""
    device = get_object_or_404(IoTDevice, device_id=device_id)

    if not check_device_access(request.user, device):
        return JsonResponse({"success": False, "error": "Access denied"}, status=403)

    try:
        # Get latest reading
        latest_reading = SensorData.objects.filter(device=device).first()

        if latest_reading:
            data = {
                "device_id": device.device_id,
                "device_name": device.name,
                "timestamp": latest_reading.timestamp.isoformat(),
                "location": device.full_location,
                "status": device.status,
                "readings": {
                    "temperature": latest_reading.temperature,
                    "humidity": latest_reading.humidity,
                    "ph": latest_reading.ph,
                    "nitrogen": latest_reading.nitrogen,
                    "phosphorus": latest_reading.phosphorus,
                    "potassium": latest_reading.potassium,
                    "soil_moisture": latest_reading.soil_moisture,
                    "light_intensity": latest_reading.light_intensity,
                },
                "data_quality": latest_reading.data_quality,
                "battery_level": latest_reading.battery_level,
            }

            return JsonResponse({"success": True, "data": data})
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "No sensor data found",
                    "device_id": device_id,
                }
            )

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": str(e), "device_id": device_id}, status=500
        )


@login_required
@require_http_methods(["GET"])
def api_device_history(request, device_id):
    """API endpoint to get sensor data history for a device"""
    device = get_object_or_404(IoTDevice, device_id=device_id)

    if not check_device_access(request.user, device):
        return JsonResponse({"success": False, "error": "Access denied"}, status=403)

    try:
        # Get query parameters
        limit = min(int(request.GET.get("limit", 100)), 1000)  # Max 1000 records
        hours = int(request.GET.get("hours", 24))  # Default 24 hours

        start_time = timezone.now() - timedelta(hours=hours)

        # Get historical data
        history = (
            SensorData.objects.filter(device=device, timestamp__gte=start_time)
            .order_by("-timestamp")[:limit]
            .values(
                "timestamp",
                "temperature",
                "humidity",
                "ph",
                "nitrogen",
                "phosphorus",
                "potassium",
                "soil_moisture",
                "light_intensity",
                "data_quality",
                "battery_level",
            )
        )

        # Convert to list and format timestamps
        history_list = []
        for reading in history:
            reading_dict = dict(reading)
            reading_dict["timestamp"] = reading["timestamp"].isoformat()
            history_list.append(reading_dict)

        return JsonResponse(
            {
                "success": True,
                "data": history_list,
                "device_id": device_id,
                "count": len(history_list),
                "hours": hours,
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": str(e), "device_id": device_id}, status=500
        )


@login_required
@require_http_methods(["GET"])
def api_region_devices(request):
    """API endpoint to get devices in a region (for map visualization)"""

    # Only admins and community admins can access this
    if not (request.user.is_admin or request.user.is_community_admin):
        return JsonResponse({"success": False, "error": "Access denied"}, status=403)

    try:
        region = request.GET.get("region")

        # Get devices based on user role
        if request.user.is_admin:
            if region:
                devices = IoTDevice.objects.filter(region=region)
            else:
                devices = IoTDevice.objects.all()
        else:
            # Community admin can only see devices in their region
            devices = IoTDevice.objects.filter(region=request.user.assigned_region)

        # Filter devices with coordinates
        devices = devices.filter(
            latitude__isnull=False, longitude__isnull=False
        ).select_related("assigned_to")

        # Build response data
        device_data = []
        for device in devices:
            latest_reading = SensorData.objects.filter(device=device).first()

            device_info = {
                "device_id": device.device_id,
                "name": device.name,
                "location": {
                    "latitude": float(device.latitude) if device.latitude else 0.0,
                    "longitude": float(device.longitude) if device.longitude else 0.0,
                    "name": device.location_name,
                    "region": device.region,
                },
                "status": device.status,
                "device_type": device.device_type,
                "assigned_to": device.assigned_to.username,
                "last_reading": None,
            }

            if latest_reading:
                device_info["last_reading"] = {
                    "timestamp": latest_reading.timestamp.isoformat(),
                    "temperature": latest_reading.temperature,
                    "humidity": latest_reading.humidity,
                    "ph": latest_reading.ph,
                }

            device_data.append(device_info)

        return JsonResponse(
            {
                "success": True,
                "data": device_data,
                "count": len(device_data),
                "region": region or "all",
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_alerts(request):
    """API endpoint to get alerts for the user"""
    try:
        # Get alerts based on user role
        if request.user.is_admin:
            alerts = DataAlert.objects.all()
        elif request.user.is_community_admin:
            alerts = DataAlert.objects.filter(
                device__region=request.user.assigned_region
            )
        else:
            alerts = DataAlert.objects.filter(device__assigned_to=request.user)

        # Filter by status if provided
        status = request.GET.get("status")
        if status:
            alerts = alerts.filter(status=status)

        # Get recent alerts
        alerts = alerts.select_related("device").order_by("-created_at")[:50]

        alert_data = []
        for alert in alerts:
            alert_info = {
                "alert_id": alert.pk,
                "title": alert.title,
                "description": alert.description,
                "severity": alert.severity,
                "status": alert.status,
                "alert_type": alert.alert_type,
                "device": {
                    "device_id": alert.device.device_id,
                    "name": alert.device.name,
                    "location": alert.device.location_name,
                },
                "created_at": alert.created_at.isoformat(),
                "threshold_value": alert.threshold_value,
                "actual_value": alert.actual_value,
                "parameter": alert.parameter,
            }
            alert_data.append(alert_info)

        return JsonResponse(
            {"success": True, "data": alert_data, "count": len(alert_data)}
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def map_view(request):
    """Map view showing devices geographically"""

    # Only admins and community admins can access the map view
    if not (request.user.is_admin or request.user.is_community_admin):
        return HttpResponseForbidden(
            "You don't have permission to access the map view."
        )

    context = {
        "page_title": "IoT Device Map",
        "user_role": request.user.role,
        "user_region": getattr(request.user, "assigned_region", None),
    }

    return render(request, "sensors/map.html", context)


@login_required
def alerts_view(request):
    """View for managing alerts"""

    context = {
        "page_title": "Device Alerts",
        "user_role": request.user.role,
    }

    return render(request, "sensors/alerts.html", context)
