from django.http import JsonResponse
from django.shortcuts import render
from . import urls


# Create your views here.
def crop_prediction_dashboard(request):
    """
    Crop prediction dashboard view that renders the dashboard page.
    """
    return render(request, "crops/dashboard.html")


def crop_prediction(request):
    """
    Crop prediction view that renders the crop prediction page.
    """
    return render(request, "crops/prediction.html")


def crop_prediction_api(request):
    """
    API endpoint for crop prediction.
    This is a placeholder function that can be expanded to handle actual prediction logic.
    """
    # Placeholder for future implementation
    return JsonResponse({"message": "Crop prediction API endpoint"})
