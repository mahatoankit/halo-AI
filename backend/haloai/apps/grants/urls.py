from django.urls import path
from . import views

app_name = "grants"
urlpatterns = [
    path("", views.grants_and_offers, name="grants_and_offers"),
]
