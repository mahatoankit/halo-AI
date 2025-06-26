from django.urls import path
from . import views

app_name = "crops"

urlpatterns = [
    # Main dashboard - loads the dashboard template without popup
    path("", views.crop_prediction_dashboard, name="dashboard"),
    path("prediction/", views.crop_prediction, name="prediction"),
    # API endpoints
    path("api/predict/", views.crop_prediction_api, name="api_predict"),
    path("api/real-time-data/", views.get_real_time_data, name="api_real_time_data"),
]
