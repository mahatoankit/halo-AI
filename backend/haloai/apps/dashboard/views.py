from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, Avg
from datetime import timedelta, datetime
from .models import (
    SubscriptionPlan,
    FarmerSubscription,
    PaymentRecord,
    ManualCropInput,
    FarmerFieldProfile,
    SoilHealthReport,
    ExpertConsultation,
)
from apps.crops.models import CropPredictionRequest, CropRecommendation, WeatherData
from apps.sensors.models import SensorReading
from apps.users.models import FarmerProfile
from .regional_config import (
    RegionalConfig,
    get_regional_defaults,
    validate_soil_parameters,
)
import json


@login_required
def role_based_dashboard_redirect(request):
    """
    Redirects users to their appropriate dashboard based on their role
    """
    user_role = request.user.role

    if user_role == "farmer":
        return redirect("dashboard:farmer_dashboard")
    elif user_role == "community_admin":
        return redirect("dashboard:home")  # Community dashboard
    elif user_role == "admin":
        return redirect("dashboard:home")  # Admin dashboard
    elif user_role == "technician":
        return redirect("dashboard:home")  # Technician dashboard
    else:
        # Default to farmer dashboard for any undefined roles
        return redirect("dashboard:farmer_dashboard")


@login_required
def farmer_dashboard(request):
    """
    Enhanced Farmer Dashboard with comprehensive features
    """
    if not request.user.is_farmer:
        return render(request, "dashboard/access_denied.html")

    # Get farmer's subscription
    try:
        subscription = FarmerSubscription.objects.get(farmer=request.user)
    except FarmerSubscription.DoesNotExist:
        subscription = None

    # Get field profile
    try:
        field_profile = FarmerFieldProfile.objects.get(farmer=request.user)
    except FarmerFieldProfile.DoesNotExist:
        field_profile = None

    # Recent crop predictions (last 30 days)
    recent_predictions = CropPredictionRequest.objects.filter(
        community_admin__managed_farmers__user=request.user
    ).order_by("-requested_at")[:5]

    # Sensor readings if available - get readings from sensor sets managed by the farmer's community admin
    # Temporarily disable sensor readings to fix the immediate issue
    sensor_readings = []
    # try:
    #     # Try to get the farmer profile to find their community admin
    #     farmer_profile = FarmerProfile.objects.select_related('community_admin').get(user=request.user)
    #     sensor_readings = SensorReading.objects.filter(
    #         sensor_set__community_admin=farmer_profile.community_admin
    #     ).order_by("-timestamp")[:10]
    # except FarmerProfile.DoesNotExist:
    #     # If no farmer profile, get no sensor readings
    #     sensor_readings = SensorReading.objects.none()

    # Soil health reports
    soil_reports = SoilHealthReport.objects.filter(farmer=request.user).order_by(
        "-test_date"
    )[:3]

    # Expert consultations
    consultations = ExpertConsultation.objects.filter(farmer=request.user).order_by(
        "-created_at"
    )[:5]

    # Payment history
    payments = (
        PaymentRecord.objects.filter(
            subscription__farmer=request.user, status="completed"
        ).order_by("-payment_date")[:5]
        if subscription
        else []
    )

    # Calculate statistics
    total_predictions = recent_predictions.count()
    success_rate = 94  # This would be calculated based on actual feedback
    monthly_savings = 45000  # This would be calculated based on recommendations

    # Weather data for the region
    if field_profile:
        weather_data = WeatherData.objects.filter(
            region__icontains=field_profile.region
        ).order_by("-date")[:7]
    else:
        weather_data = WeatherData.objects.filter(region="Bhairahawa-Butwal").order_by(
            "-date"
        )[:7]

    context = {
        "title": "Farmer Dashboard",
        "user": request.user,
        "subscription": subscription,
        "field_profile": field_profile,
        "recent_predictions": recent_predictions,
        "sensor_readings": sensor_readings,
        "soil_reports": soil_reports,
        "consultations": consultations,
        "payments": payments,
        "weather_data": weather_data,
        # Statistics
        "total_predictions": total_predictions,
        "farm_area": field_profile.total_area if field_profile else 12.5,
        "success_rate": success_rate,
        "monthly_savings": monthly_savings,
        # Quick access flags
        "can_create_prediction": subscription
        and subscription.predictions_remaining > 0,
        "has_expert_access": subscription and subscription.plan.expert_consultation,
    }

    return render(request, "dashboard/farmer_dashboard.html", context)


@login_required
def community_dashboard(request):
    """
    Community Dashboard view that renders the community dashboard page.
    """
    context = {
        "title": "Community Dashboard",
        "description": "Connect with fellow farmers, share insights, and grow together.",
        "user": request.user,
    }
    return render(request, "dashboard/index.html", context)


@login_required
def prediction_history(request):
    """Detailed view of farmer's prediction history"""
    if not request.user.is_farmer:
        return JsonResponse({"error": "Access denied"}, status=403)

    predictions = CropPredictionRequest.objects.filter(
        community_admin__managed_farmers__user=request.user
    ).order_by("-requested_at")

    context = {
        "title": "Prediction History",
        "predictions": predictions,
        "user": request.user,
    }

    return render(request, "dashboard/prediction_history.html", context)


@login_required
def sensor_data_history(request):
    """Detailed view of sensor readings"""
    if not request.user.is_farmer:
        return JsonResponse({"error": "Access denied"}, status=403)

    readings = SensorReading.objects.filter(device__assigned_to=request.user).order_by(
        "-timestamp"
    )

    # Group readings by day for charts
    daily_readings = {}
    for reading in readings[:30]:  # Last 30 readings
        date_key = reading.timestamp.date()
        if date_key not in daily_readings:
            daily_readings[date_key] = []
        daily_readings[date_key].append(reading)

    context = {
        "title": "Sensor Data History",
        "readings": readings[:50],  # Last 50 readings
        "daily_readings": daily_readings,
        "user": request.user,
    }

    return render(request, "dashboard/sensor_history.html", context)


@login_required
def subscription_details(request):
    """Detailed view of subscription and billing"""
    if not request.user.is_farmer:
        return JsonResponse({"error": "Access denied"}, status=403)

    try:
        subscription = FarmerSubscription.objects.get(farmer=request.user)
        payments = PaymentRecord.objects.filter(subscription=subscription).order_by(
            "-payment_date"
        )
    except FarmerSubscription.DoesNotExist:
        subscription = None
        payments = []

    available_plans = SubscriptionPlan.objects.filter(is_active=True)

    context = {
        "title": "Subscription Details",
        "subscription": subscription,
        "payments": payments,
        "available_plans": available_plans,
        "user": request.user,
    }

    return render(request, "dashboard/subscription_details.html", context)


@login_required
def manual_input_form(request):
    """Form for manual crop input by farmers"""
    if not request.user.is_farmer:
        return JsonResponse({"error": "Access denied"}, status=403)

    if request.method == "POST":
        try:
            # Validate soil parameters
            input_params = {
                "nitrogen": request.POST.get("nitrogen"),
                "phosphorus": request.POST.get("phosphorus"),
                "potassium": request.POST.get("potassium"),
                "ph": request.POST.get("ph"),
                "temperature": request.POST.get("temperature"),
                "humidity": request.POST.get("humidity"),
                "rainfall": request.POST.get("rainfall"),
            }

            validation_errors = validate_soil_parameters(input_params)
            if validation_errors:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Validation failed: " + "; ".join(validation_errors),
                    },
                    status=400,
                )

            manual_input = ManualCropInput.objects.create(
                farmer=request.user,
                nitrogen=float(request.POST.get("nitrogen")),
                phosphorus=float(request.POST.get("phosphorus")),
                potassium=float(request.POST.get("potassium")),
                ph=float(request.POST.get("ph")),
                temperature=float(request.POST.get("temperature")),
                humidity=float(request.POST.get("humidity")),
                rainfall=float(request.POST.get("rainfall")),
                field_area=float(request.POST.get("field_area", 0)) or None,
                notes=request.POST.get("notes", ""),
            )

            # Create a prediction request based on manual input
            # This would trigger the ML prediction service

            return JsonResponse(
                {
                    "success": True,
                    "message": "Manual input recorded successfully",
                    "input_id": str(manual_input.id),
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    # Get farmer's field profile for defaults
    try:
        field_profile = FarmerFieldProfile.objects.get(farmer=request.user)
        region = field_profile.region.lower()
    except FarmerFieldProfile.DoesNotExist:
        field_profile = None
        region = "bhairahawa"  # Default region

    # Get regional defaults
    regional_defaults = get_regional_defaults(region)

    context = {
        "title": "New Crop Prediction",
        "field_profile": field_profile,
        "regional_defaults": regional_defaults,
        "user": request.user,
    }

    return render(request, "dashboard/manual_input_form.html", context)


@login_required
def expert_consultation_request(request):
    """Request expert consultation"""
    if not request.user.is_farmer:
        return JsonResponse({"error": "Access denied"}, status=403)

    # Check if farmer has access to expert consultation
    try:
        subscription = FarmerSubscription.objects.get(farmer=request.user)
        if not subscription.plan.expert_consultation:
            return JsonResponse(
                {"error": "Expert consultation not available in your plan"}, status=403
            )
    except FarmerSubscription.DoesNotExist:
        return JsonResponse({"error": "No active subscription found"}, status=403)

    if request.method == "POST":
        try:
            consultation = ExpertConsultation.objects.create(
                farmer=request.user,
                consultation_type=request.POST.get("consultation_type"),
                subject=request.POST.get("subject"),
                description=request.POST.get("description"),
                is_urgent=request.POST.get("is_urgent") == "on",
                preferred_contact_method=request.POST.get("contact_method"),
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Consultation request submitted successfully",
                    "consultation_id": str(consultation.id),
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    context = {
        "title": "Expert Consultation",
        "consultation_types": ExpertConsultation.CONSULTATION_TYPES,
        "contact_methods": ExpertConsultation._meta.get_field(
            "preferred_contact_method"
        ).choices,
        "user": request.user,
    }

    return render(request, "dashboard/expert_consultation.html", context)
