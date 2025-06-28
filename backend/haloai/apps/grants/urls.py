from django.urls import path
from . import views

app_name = "grants"
urlpatterns = [
    path("", views.grants_and_offers, name="grants_and_offers"),
    path("grant/<int:grant_id>/", views.grant_detail, name="grant_detail"),
    path("api/grants/", views.grants_api, name="grants_api"),
]
