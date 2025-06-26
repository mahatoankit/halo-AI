from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from typing import Dict, Any

# Import our enhanced services
from services.iot_data_service import iot_data_service
from services.enhanced_weather_service import enhanced_weather_service
from services.real_ml_prediction_service import real_ml_service


# Create your views here.
def crop_prediction_dashboard(request):
    """
    Crop prediction dashboard view that renders the dashboard page.
    """
    return render(request, "crops/dashboard.html")
    # return render(request, "crops/prediction.html")


def crop_prediction(request):
    """
    Crop prediction view that renders the crop prediction page.
    """
    return render(request, "crops/prediction.html")
    # return render(request, "crops/dashboard.html")



@csrf_exempt
@require_http_methods(["POST"])
def crop_prediction_api(request):
    """
    API endpoint for real crop prediction using IoT sensors, weather data, and ML models.
    """
    try:
        # Parse request data
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST.dict()

        # Collect real-time data
        prediction_input = collect_real_time_data(data)

        # Make prediction using real ML models
        prediction_result = real_ml_service.get_prediction_with_rationale(
            prediction_input
        )

        # Format response
        response_data = format_prediction_response(prediction_result, prediction_input)

        return JsonResponse({"status": "success", "data": response_data})

    except Exception as e:
        return JsonResponse(
            {
                "status": "error",
                "message": f"Prediction failed: {str(e)}",
                "data": None,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def get_real_time_data(request):
    """
    API endpoint to fetch real-time IoT sensor and weather data
    """
    try:
        region = request.GET.get("region", "Bhairahawa-Butwal")
        sensor_id = request.GET.get("sensor_id", "bhairahawa_farm_1")

        # Get IoT sensor data
        iot_data = iot_data_service.get_latest_sensor_data(sensor_id)

        # Get weather data
        weather_data = enhanced_weather_service.get_current_weather_data(region)

        # Get regional NPK averages (as specified in requirements)
        npk_defaults = {
            "nitrogen": 30,  # Bhairahawa regional average
            "phosphorus": 22.5,  # Regional average
            "potassium": 60,  # Regional average
        }

        real_time_data = {
            # IoT sensor data (ph, temperature)
            "ph": iot_data.get("ph", 6.5),
            "temperature": iot_data.get("temperature", 29.6),
            # Weather API data (rainfall, humidity)
            "rainfall": weather_data.get("rainfall", 22.5),
            "humidity": weather_data.get("humidity", 60.0),
            # Regional averages (N, P, K)
            "nitrogen": npk_defaults["nitrogen"],
            "phosphorus": npk_defaults["phosphorus"],
            "potassium": npk_defaults["potassium"],
            # Metadata
            "region": region,
            "sensor_id": sensor_id,
            "data_sources": {
                "iot_sensors": "Firebase Realtime Database",
                "weather": weather_data.get("source", "open-meteo"),
                "npk": "Regional averages",
            },
            "timestamp": iot_data.get("timestamp"),
        }

        return JsonResponse({"status": "success", "data": real_time_data})

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"Failed to fetch real-time data: {str(e)}"},
            status=500,
        )


def collect_real_time_data(user_input: Dict[str, Any]) -> Dict[str, float]:
    """
    Collect real-time data from various sources and merge with user input
    Priority: User Input > IoT Sensors > Weather API > Regional Defaults
    """
    # Start with regional defaults
    region = user_input.get("location", "Bhairahawa-Butwal")

    # Regional NPK averages for Bhairahawa as specified
    npk_defaults = {"nitrogen": 30.0, "phosphorus": 22.5, "potassium": 60.0}

    # Get IoT sensor data
    try:
        iot_data = iot_data_service.get_latest_sensor_data("bhairahawa_farm_1")
    except Exception as e:
        print(f"IoT data fetch error: {e}")
        iot_data = {}

    # Get weather data
    try:
        season = user_input.get("season", "kharif")
        weather_data = enhanced_weather_service.get_crop_season_weather(region, season)
    except Exception as e:
        print(f"Weather data fetch error: {e}")
        weather_data = {"rainfall": 22.5, "humidity": 60.0}

    # Build final input with priority order
    prediction_input = {}

    # NPK values - use user input or regional defaults
    prediction_input["nitrogen"] = float(
        user_input.get("nitrogen", npk_defaults["nitrogen"])
    )
    prediction_input["phosphorus"] = float(
        user_input.get("phosphorus", npk_defaults["phosphorus"])
    )
    prediction_input["potassium"] = float(
        user_input.get("potassium", npk_defaults["potassium"])
    )

    # pH and temperature - use user input or IoT sensor data
    prediction_input["ph"] = float(user_input.get("ph", iot_data.get("ph", 6.5)))
    prediction_input["temperature"] = float(
        user_input.get("temperature", iot_data.get("temperature", 29.6))
    )

    # Rainfall and humidity - use user input or weather API data
    prediction_input["rainfall"] = float(
        user_input.get("rainfall", weather_data.get("rainfall", 22.5))
    )
    prediction_input["humidity"] = float(
        user_input.get("humidity", weather_data.get("humidity", 60.0))
    )

    return prediction_input


def format_prediction_response(
    prediction_result: Dict[str, Any], input_data: Dict[str, float]
) -> Dict[str, Any]:
    """
    Format the ML prediction result for frontend consumption
    """
    recommended_crops = []

    # Primary recommendation
    primary_crop = {
        "name": prediction_result["recommended_crop"].title(),
        "confidence": int(prediction_result["confidence"] * 100),
        "reason": prediction_result["rationale"],
        "type": "primary",
    }
    recommended_crops.append(primary_crop)

    # Alternative recommendations
    for alt_crop in prediction_result.get("alternative_crops", []):
        alt_recommendation = {
            "name": alt_crop["crop"].title(),
            "confidence": int(alt_crop["confidence"] * 100),
            "reason": f"Good alternative choice with suitable growing conditions.",
            "type": "alternative",
        }
        recommended_crops.append(alt_recommendation)

    return {
        "recommended_crops": recommended_crops,
        "input_analysis": prediction_result.get("input_analysis", {}),
        "model_details": prediction_result.get("model_details", {}),
        "prediction_summary": {
            "primary_crop": prediction_result["recommended_crop"].title(),
            "confidence": prediction_result["confidence"],
            "total_recommendations": len(recommended_crops),
            "data_sources_used": [
                "IoT Sensors",
                "Weather API",
                "Regional Data",
                "ML Models",
            ],
        },
        "input_parameters": input_data,
    }
