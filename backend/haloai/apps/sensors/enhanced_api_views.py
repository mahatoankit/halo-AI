"""
Enhanced IoT API Views for Real-time Sensor Data Management
Provides robust endpoints for sensor data, health monitoring, and diagnostics
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from services.enhanced_iot_service import enhanced_iot_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def get_sensor_data(request):
    """Get real-time sensor data with enhanced error handling"""
    try:
        sensor_id = request.GET.get("sensor_id", "bhairahawa_farm_1")
        use_cache = request.GET.get("use_cache", "true").lower() == "true"

        logger.info(f"📡 Fetching sensor data for: {sensor_id}")

        # Get sensor data
        sensor_data = enhanced_iot_service.get_latest_sensor_data(sensor_id, use_cache)

        if not sensor_data:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"No data available for sensor {sensor_id}",
                    "data": None,
                },
                status=404,
            )

        # Add metadata
        response_data = {
            "sensor_id": sensor_id,
            "reading": sensor_data,
            "metadata": {
                "location": enhanced_iot_service.sensor_locations.get(sensor_id, {}),
                "data_source": "enhanced_iot_service",
                "cache_used": use_cache
                and enhanced_iot_service._is_cache_valid(sensor_id),
            },
        }

        return JsonResponse(
            {
                "status": "success",
                "message": f"Sensor data retrieved for {sensor_id}",
                "data": response_data,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in get_sensor_data: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"Failed to retrieve sensor data: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def get_all_sensors_data(request):
    """Get data from all available sensors"""
    try:
        logger.info("📡 Fetching data from all sensors")

        all_sensors = enhanced_iot_service.get_all_sensors_data()

        if not all_sensors:
            return JsonResponse(
                {
                    "status": "warning",
                    "message": "No sensor data available",
                    "data": {"sensors": {}, "count": 0},
                }
            )

        # Calculate summary statistics
        summary = {
            "total_sensors": len(all_sensors),
            "active_sensors": len(
                [s for s in all_sensors.values() if s.get("status") != "default"]
            ),
            "regions": list(
                set(s.get("region", "unknown") for s in all_sensors.values())
            ),
            "sensor_types": list(enhanced_iot_service.sensor_locations.keys()),
        }

        return JsonResponse(
            {
                "status": "success",
                "message": f"Retrieved data from {len(all_sensors)} sensors",
                "data": {"sensors": all_sensors, "summary": summary},
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in get_all_sensors_data: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"Failed to retrieve sensor data: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def get_regional_data(request):
    """Get regional average sensor data"""
    try:
        region = request.GET.get("region", "Bhairahawa-Butwal")

        logger.info(f"📊 Fetching regional data for: {region}")

        regional_data = enhanced_iot_service.get_regional_average_data(region)

        # Determine data quality safely
        active_sensors = regional_data.get("active_sensors", 0)
        data_quality = "simulated"
        try:
            if isinstance(active_sensors, (int, float)) and active_sensors > 0:
                data_quality = "high"
        except (ValueError, TypeError):
            pass

        return JsonResponse(
            {
                "status": "success",
                "message": f"Regional data retrieved for {region}",
                "data": {
                    "region": region,
                    "averages": regional_data,
                    "data_quality": data_quality,
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in get_regional_data: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"Failed to retrieve regional data: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def get_sensor_health(request):
    """Get health status for sensors"""
    try:
        sensor_id = request.GET.get("sensor_id")

        if sensor_id:
            # Get health for specific sensor
            health_status = enhanced_iot_service.get_sensor_health_status(sensor_id)

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Health status retrieved for {sensor_id}",
                    "data": health_status,
                }
            )
        else:
            # Get health for all sensors
            all_health = {}
            for sensor_id in enhanced_iot_service.sensor_locations.keys():
                all_health[sensor_id] = enhanced_iot_service.get_sensor_health_status(
                    sensor_id
                )

            # Calculate overall system health
            healthy_sensors = len(
                [h for h in all_health.values() if h.get("health") == "excellent"]
            )
            total_sensors = len(all_health)
            system_health = (
                "excellent"
                if healthy_sensors == total_sensors
                else (
                    "good"
                    if healthy_sensors > total_sensors * 0.7
                    else "fair" if healthy_sensors > total_sensors * 0.4 else "poor"
                )
            )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "System health status retrieved",
                    "data": {
                        "sensors": all_health,
                        "system_summary": {
                            "overall_health": system_health,
                            "healthy_sensors": healthy_sensors,
                            "total_sensors": total_sensors,
                            "health_percentage": (
                                round((healthy_sensors / total_sensors) * 100, 1)
                                if total_sensors > 0
                                else 0
                            ),
                        },
                    },
                }
            )

    except Exception as e:
        logger.error(f"❌ Error in get_sensor_health: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"Failed to retrieve sensor health: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def get_sensor_history(request):
    """Get historical sensor data"""
    try:
        sensor_id = request.GET.get("sensor_id", "bhairahawa_farm_1")
        hours = int(request.GET.get("hours", 24))

        logger.info(f"📈 Fetching {hours}h history for: {sensor_id}")

        history = enhanced_iot_service.get_sensor_history(sensor_id, hours)

        return JsonResponse(
            {
                "status": "success",
                "message": f"Retrieved {len(history)} historical readings for {sensor_id}",
                "data": {
                    "sensor_id": sensor_id,
                    "time_period_hours": hours,
                    "readings": history,
                    "count": len(history),
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in get_sensor_history: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"Failed to retrieve sensor history: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_demo_data(request):
    """Create demo sensor data for testing (admin only)"""
    try:
        if not request.user.is_staff and not getattr(request.user, "is_admin", False):
            return JsonResponse(
                {"status": "error", "message": "Admin access required", "data": None},
                status=403,
            )

        # Parse request data
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST.dict()

        sensors = data.get(
            "sensors", list(enhanced_iot_service.sensor_locations.keys())
        )

        logger.info(f"🧪 Creating demo data for sensors: {sensors}")

        success = enhanced_iot_service.create_demo_data(sensors)

        if success:
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Demo data created for {len(sensors)} sensors",
                    "data": {
                        "sensors_updated": sensors,
                        "created_at": (
                            enhanced_iot_service._readings_cache.get(
                                sensors[0], {}
                            ).get("timestamp")
                            if sensors
                            else None
                        ),
                    },
                }
            )
        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Failed to create demo data",
                    "data": None,
                },
                status=500,
            )

    except Exception as e:
        logger.error(f"❌ Error in create_demo_data: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"Failed to create demo data: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def get_enhanced_realtime_data(request):
    """
    Enhanced version of the real-time data endpoint with better integration
    This replaces the existing get_real_time_data endpoint
    """
    try:
        region = request.GET.get("region", "Bhairahawa-Butwal")
        sensor_id = request.GET.get("sensor_id", "bhairahawa_farm_1")
        include_health = request.GET.get("include_health", "false").lower() == "true"

        logger.info(f"🔄 Enhanced real-time data request for {sensor_id} in {region}")

        # Get IoT sensor data
        iot_data = enhanced_iot_service.get_latest_sensor_data(sensor_id)

        # Get regional data for context
        regional_data = enhanced_iot_service.get_regional_average_data(region)

        # Get weather data (import here to avoid circular imports)
        try:
            from services.enhanced_weather_service import enhanced_weather_service

            weather_data = enhanced_weather_service.get_current_weather_data(region)
        except Exception as e:
            logger.warning(f"Weather service unavailable: {e}")
            weather_data = {"rainfall": 22.5, "humidity": 60.0, "source": "unavailable"}

        # Regional NPK averages
        npk_defaults = {"nitrogen": 30, "phosphorus": 22.5, "potassium": 60}

        # Safely get humidity values
        iot_humidity = iot_data.get("humidity", 60.0)
        weather_humidity = weather_data.get("humidity", 60.0)

        try:
            iot_humidity_val = float(iot_humidity) if iot_humidity is not None else 60.0
            weather_humidity_val = (
                float(weather_humidity) if weather_humidity is not None else 60.0
            )
            final_humidity = max(iot_humidity_val, weather_humidity_val)
        except (ValueError, TypeError):
            final_humidity = 60.0

        # Build comprehensive response
        enhanced_data = {
            # IoT sensor data
            "ph": iot_data.get("ph", 6.5),
            "temperature": iot_data.get("temperature", 29.6),
            "soil_temperature": iot_data.get("soil_temperature", 25.0),
            # Weather API data
            "rainfall": weather_data.get("rainfall", 22.5),
            "humidity": final_humidity,
            # Regional averages
            "nitrogen": npk_defaults["nitrogen"],
            "phosphorus": npk_defaults["phosphorus"],
            "potassium": npk_defaults["potassium"],
            # Metadata
            "region": region,
            "sensor_id": sensor_id,
            "data_sources": {
                "iot_sensors": "Enhanced Firebase Service",
                "weather": weather_data.get("source", "enhanced-weather-service"),
                "npk": "Regional averages",
                "timestamp": iot_data.get("timestamp"),
            },
            "data_quality": {
                "iot_status": iot_data.get("status", "unknown"),
                "weather_status": (
                    "available"
                    if weather_data.get("source") != "unavailable"
                    else "unavailable"
                ),
                "overall": (
                    "high" if iot_data.get("status") != "default" else "simulated"
                ),
            },
        }

        # Add health information if requested
        if include_health:
            health_status = enhanced_iot_service.get_sensor_health_status(sensor_id)
            enhanced_data["sensor_health"] = health_status

        return JsonResponse(
            {
                "status": "success",
                "message": "Enhanced real-time data retrieved successfully",
                "data": enhanced_data,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in get_enhanced_realtime_data: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"Failed to fetch enhanced real-time data: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def system_diagnostics(request):
    """Get comprehensive system diagnostics for IoT infrastructure"""
    try:
        logger.info("🔧 Running system diagnostics")

        # Firebase connection status
        firebase_status = {
            "realtime_db": enhanced_iot_service.db_ref is not None,
            "firestore": enhanced_iot_service.firestore_client is not None,
            "firebase_service": enhanced_iot_service.firebase_service is not None,
        }

        # Sensor health overview
        sensor_health = {}
        for sensor_id in enhanced_iot_service.sensor_locations.keys():
            sensor_health[sensor_id] = enhanced_iot_service.get_sensor_health_status(
                sensor_id
            )

        # Cache status
        cache_info = {
            "cached_sensors": len(enhanced_iot_service._readings_cache),
            "cache_ttl_seconds": enhanced_iot_service._cache_ttl,
            "cached_sensor_ids": list(enhanced_iot_service._readings_cache.keys()),
        }

        # Regional coverage
        regions = list(
            set(
                location.get("region", "unknown")
                for location in enhanced_iot_service.sensor_locations.values()
            )
        )

        regional_coverage = {}
        for region in regions:
            regional_coverage[region] = enhanced_iot_service.get_regional_average_data(
                region
            )

        diagnostics = {
            "system_status": (
                "operational" if firebase_status["realtime_db"] else "degraded"
            ),
            "firebase_connections": firebase_status,
            "sensor_health": sensor_health,
            "cache_status": cache_info,
            "regional_coverage": regional_coverage,
            "total_sensors": len(enhanced_iot_service.sensor_locations),
            "supported_regions": regions,
            "last_check": enhanced_iot_service._readings_cache.get(
                "system_check", {}
            ).get("timestamp", "never"),
        }

        return JsonResponse(
            {
                "status": "success",
                "message": "System diagnostics completed",
                "data": diagnostics,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in system_diagnostics: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"System diagnostics failed: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def get_realtime_sensor_data(request):
    """Get REAL-TIME sensor data - always fetches fresh data, bypasses cache"""
    try:
        sensor_id = request.GET.get("sensor_id", "bhairahawa_farm_1")

        logger.info(f"🔴 REAL-TIME API: Fetching live data for: {sensor_id}")

        # Always get fresh data - no cache
        sensor_data = enhanced_iot_service.get_realtime_sensor_data(sensor_id)

        if not sensor_data:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"No real-time data available for sensor {sensor_id}",
                    "data": None,
                },
                status=404,
            )

        # Add metadata
        response_data = {
            "sensor_id": sensor_id,
            "reading": sensor_data,
            "metadata": {
                "location": enhanced_iot_service.sensor_locations.get(sensor_id, {}),
                "data_source": "enhanced_iot_service",
                "realtime": True,
                "cache_used": False,  # Always fresh data
                "fetch_timestamp": sensor_data.get("timestamp"),
            },
        }

        return JsonResponse(
            {
                "status": "success",
                "message": f"Real-time sensor data retrieved for {sensor_id}",
                "data": response_data,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in get_realtime_sensor_data: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"Failed to retrieve real-time sensor data: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def get_continuous_sensor_stream(request):
    """Get sensor data with minimal delay for continuous monitoring"""
    try:
        sensor_id = request.GET.get("sensor_id", "bhairahawa_farm_1")
        include_diagnostics = request.GET.get("diagnostics", "false").lower() == "true"

        logger.info(f"📡 CONTINUOUS STREAM: {sensor_id}")

        # Get real-time data
        sensor_data = enhanced_iot_service.get_realtime_sensor_data(sensor_id)

        response_data = {
            "sensor_id": sensor_id,
            "reading": sensor_data,
            "timestamp": sensor_data.get("timestamp") if sensor_data else None,
            "stream_id": f"stream_{sensor_id}_{int(datetime.now().timestamp())}",
            "realtime": True,
        }

        # Add diagnostics if requested
        if include_diagnostics:
            health_data = enhanced_iot_service.get_sensor_health_status(sensor_id)
            response_data["health"] = health_data

        return JsonResponse(
            {
                "status": "success",
                "message": f"Continuous stream data for {sensor_id}",
                "data": response_data,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in get_continuous_sensor_stream: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": f"Stream failed: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def realtime_dashboard(request):
    """Serve the real-time dashboard page"""
    from django.shortcuts import render

    return render(request, "realtime_dashboard.html")
