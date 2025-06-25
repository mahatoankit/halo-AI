from django.urls import path
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from . import views

app_name = "crops"

urlpatterns = [
    path("", views.crop_prediction, name="crop_prediction"),
]
