"""
URL configuration for haloai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from apps.home.views import public_landing

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.home.urls", namespace="home")),
    # Add 'index' pattern to resolve NoReverseMatch errors
    path("index/", public_landing, name="index"),
    path("grants-and-offers/", include("apps.grants.urls", namespace="grants")),
    path("auth/", include("apps.users.urls", namespace="users")),
    path("community/", include("apps.community.urls", namespace="community")),
    path("crop-prediction/", include("apps.crops.urls", namespace="crops")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("sensors/", include("apps.sensors.urls", namespace="sensors")),
]
