"""
Enhanced Crops Views
Integrated crop prediction with community admin role-based access control
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from services.crop_prediction_service import EnhancedCropPredictionService
from services.firebase_service_refactored import firebase_service
from apps.sensors.models import IoTSensorSet
from .models import CropPredictionRequest, CropRecommendation, CropType
import json


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
def crop_prediction_dashboard(request):
    """Main crop prediction dashboard"""
    user = request.user

    # Get user's predictions
    if user.role == "community_admin":
        predictions = CropPredictionRequest.objects.filter(
            community_admin=user
        ).order_by("-requested_at")[:10]

        sensor_sets = IoTSensorSet.objects.filter(
            community_admin=user, status="active"
        ).order_by("name")

        region = user.assigned_region or "Bhairahawa-Butwal"
    else:
        predictions = CropPredictionRequest.objects.all().order_by("-requested_at")[:10]
        sensor_sets = IoTSensorSet.objects.filter(status="active").order_by("name")
        region = "All Regions"

    # Get statistics
    stats = {
        "total_predictions": (
            predictions.count()
            if user.role == "admin"
            else CropPredictionRequest.objects.filter(community_admin=user).count()
        ),
        "completed_predictions": CropPredictionRequest.objects.filter(
            **({"community_admin": user} if user.role == "community_admin" else {}),
            status="completed",
        ).count(),
        "active_sensors": sensor_sets.count(),
        "region": region,
    }

    # Get recent Firebase predictions for real-time updates
    firebase_predictions = []
    if user.role == "community_admin":
        firebase_predictions = firebase_service.get_admin_predictions(str(user.id), 5)

    context = {
        "page_title": f"Crop Prediction Dashboard - {region}",
        "predictions": predictions,
        "sensor_sets": sensor_sets,
        "stats": stats,
        "firebase_predictions": firebase_predictions,
        "user": user,
    }

    return render(request, "crops/dashboard.html", context)


@login_required
@user_passes_test(is_community_admin)
def create_prediction(request):
    """Create new crop prediction request"""
    user = request.user
    sensor_sets = IoTSensorSet.objects.filter(community_admin=user, status="active")

    if request.method == "POST":
        try:
            sensor_set_id = request.POST.get("sensor_set_id")
            sensor_set = get_object_or_404(
                IoTSensorSet, id=sensor_set_id, community_admin=user
            )

            # Create prediction using enhanced service
            prediction_service = EnhancedCropPredictionService()
            prediction_request = prediction_service.create_prediction_request(
                str(user.id), str(sensor_set.id)
            )

            if prediction_request:
                # Process the prediction
                try:
                    results = prediction_service.predict_crops(prediction_request)
                    if results:
                        messages.success(
                            request,
                            f'Crop prediction completed! Recommended crops: {", ".join([crop["name"] for crop in results["predicted_crops"][:3]])}',
                        )
                    else:
                        messages.warning(
                            request,
                            "Prediction created but processing failed. Please try again.",
                        )
                except Exception as pred_error:
                    messages.warning(
                        request,
                        "Prediction created but processing encountered an issue.",
                    )

                return redirect(
                    "crops:prediction_detail", prediction_id=prediction_request.id
                )
            else:
                messages.error(request, "Failed to create prediction request.")

        except Exception as e:
            messages.error(request, f"Error creating prediction: {e}")

    # Get regional crop recommendations
    region = user.assigned_region or "Bhairahawa-Butwal"
    popular_crops = CropType.objects.filter(
        Q(growing_season__icontains=region) | Q(regional_success_rate__gt=0.5)
    ).order_by("-regional_success_rate")[:5]

    context = {
        "page_title": "Create Crop Prediction",
        "sensor_sets": sensor_sets,
        "popular_crops": popular_crops,
        "region": region,
        "user": user,
    }

    return render(request, "crops/create_prediction.html", context)


@login_required
@user_passes_test(is_community_admin_or_admin)
def prediction_detail(request, prediction_id):
    """Detailed view of a crop prediction"""
    user = request.user

    # Get prediction with permission check
    if user.role == "community_admin":
        prediction = get_object_or_404(
            CropPredictionRequest, id=prediction_id, community_admin=user
        )
    else:
        prediction = get_object_or_404(CropPredictionRequest, id=prediction_id)

    # Get recommendations
    recommendations = CropRecommendation.objects.filter(
        prediction_request=prediction
    ).order_by("-confidence_score")

    # Get sensor data used for prediction
    sensor_data = {
        "N": prediction.nitrogen,
        "P": prediction.phosphorus,
        "K": prediction.potassium,
        "temperature": prediction.temperature,
        "humidity": prediction.humidity,
        "ph": prediction.ph,
        "rainfall": prediction.rainfall,
    }

    # Get historical predictions for this sensor set for comparison
    historical_predictions = (
        CropPredictionRequest.objects.filter(
            sensor_set=prediction.sensor_set, status="completed"
        )
        .exclude(id=prediction.id)
        .order_by("-processed_at")[:5]
    )

    context = {
        "page_title": f"Prediction Details - {prediction.sensor_set.name}",
        "prediction": prediction,
        "recommendations": recommendations,
        "sensor_data": sensor_data,
        "historical_predictions": historical_predictions,
        "user": user,
    }

    return render(request, "crops/prediction_detail.html", context)


@login_required
@user_passes_test(is_community_admin_or_admin)
def prediction_history(request):
    """View prediction history"""
    user = request.user

    # Get user's predictions with search
    search_query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")

    if user.role == "community_admin":
        predictions = CropPredictionRequest.objects.filter(community_admin=user)
    else:
        predictions = CropPredictionRequest.objects.all()

    if search_query:
        predictions = predictions.filter(
            Q(sensor_set__name__icontains=search_query)
            | Q(sensor_set__location_name__icontains=search_query)
            | Q(notes__icontains=search_query)
        )

    if status_filter:
        predictions = predictions.filter(status=status_filter)

    predictions = predictions.order_by("-requested_at")

    # Pagination
    paginator = Paginator(predictions, 15)
    page_number = request.GET.get("page")
    predictions_page = paginator.get_page(page_number)

    context = {
        "page_title": "Prediction History",
        "predictions": predictions_page,
        "search_query": search_query,
        "status_filter": status_filter,
        "user": user,
    }

    return render(request, "crops/prediction_history.html", context)


@login_required
@user_passes_test(is_community_admin_or_admin)
def regional_insights(request):
    """Regional crop insights and analytics"""
    user = request.user

    if user.role == "community_admin":
        region = user.assigned_region or "Bhairahawa-Butwal"
        predictions = CropPredictionRequest.objects.filter(
            community_admin=user, status="completed"
        )
    else:
        region = request.GET.get("region", "Bhairahawa-Butwal")
        predictions = CropPredictionRequest.objects.filter(
            sensor_set__region=region, status="completed"
        )

    # Analyze crop recommendations
    crop_stats = {}
    for prediction in predictions:
        for crop_data in prediction.predicted_crops:
            crop_name = crop_data.get("name", "Unknown")
            if crop_name not in crop_stats:
                crop_stats[crop_name] = {
                    "count": 0,
                    "avg_confidence": 0,
                    "total_confidence": 0,
                }
            crop_stats[crop_name]["count"] += 1
            crop_stats[crop_name]["total_confidence"] += crop_data.get("confidence", 0)
            crop_stats[crop_name]["avg_confidence"] = (
                crop_stats[crop_name]["total_confidence"]
                / crop_stats[crop_name]["count"]
            )

    # Sort by popularity
    popular_crops = sorted(
        crop_stats.items(), key=lambda x: x[1]["count"], reverse=True
    )[:10]

    # Get seasonal trends (placeholder for now)
    seasonal_trends = {
        "spring": ["Wheat", "Barley", "Mustard"],
        "summer": ["Rice", "Maize", "Sugarcane"],
        "autumn": ["Potato", "Vegetables", "Lentils"],
        "winter": ["Wheat", "Chickpea", "Mustard"],
    }

    context = {
        "page_title": f"Regional Insights - {region}",
        "region": region,
        "popular_crops": popular_crops,
        "seasonal_trends": seasonal_trends,
        "total_predictions": predictions.count(),
        "user": user,
    }

    return render(request, "crops/regional_insights.html", context)


# ==== API ENDPOINTS ====


@login_required
@require_http_methods(["POST"])
def api_create_prediction(request):
    """API endpoint to create crop prediction"""
    try:
        user = request.user
        if user.role != "community_admin":
            return JsonResponse({"success": False, "error": "Access denied"})

        data = json.loads(request.body)
        sensor_set_id = data.get("sensor_set_id")

        if not sensor_set_id:
            return JsonResponse({"success": False, "error": "Sensor set ID required"})

        # Verify sensor set ownership
        sensor_set = IoTSensorSet.objects.get(id=sensor_set_id, community_admin=user)

        # Create prediction
        prediction_service = EnhancedCropPredictionService()
        prediction_request = prediction_service.create_prediction_request(
            str(user.id), str(sensor_set.id)
        )

        if prediction_request:
            return JsonResponse(
                {
                    "success": True,
                    "prediction_id": str(prediction_request.id),
                    "status": prediction_request.status,
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Failed to create prediction"}
            )

    except IoTSensorSet.DoesNotExist:
        return JsonResponse({"success": False, "error": "Sensor set not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_http_methods(["GET"])
def api_prediction_status(request, prediction_id):
    """API endpoint to check prediction status"""
    try:
        user = request.user

        if user.role == "community_admin":
            prediction = CropPredictionRequest.objects.get(
                id=prediction_id, community_admin=user
            )
        else:
            prediction = CropPredictionRequest.objects.get(id=prediction_id)

        return JsonResponse(
            {
                "success": True,
                "status": prediction.status,
                "predicted_crops": prediction.predicted_crops,
                "confidence_score": prediction.confidence_score,
                "processed_at": (
                    prediction.processed_at.isoformat()
                    if prediction.processed_at
                    else None
                ),
            }
        )

    except CropPredictionRequest.DoesNotExist:
        return JsonResponse({"success": False, "error": "Prediction not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# Legacy view for backward compatibility
def crop_prediction(request):
    """Legacy crop prediction view - redirect to dashboard"""
    if request.user.is_authenticated:
        return redirect("crops:dashboard")
    else:
        return redirect("users:login")
