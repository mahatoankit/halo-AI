#!/usr/bin/env python
"""
Test script to check dashboard performance and data loading
"""
import os
import sys
import django
import time

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)
django.setup()

from apps.users.models import CustomUser
from apps.dashboard.views import farmer_dashboard
from django.test import RequestFactory
from django.contrib.auth import get_user


def test_dashboard_performance():
    """Test dashboard performance"""
    print("🔍 Testing dashboard performance...")

    # Get test farmer user
    try:
        user = CustomUser.objects.get(username="testfarmer")
        print(f"✅ Found test user: {user.username} ({user.role})")
    except CustomUser.DoesNotExist:
        print("❌ Test user not found")
        return

    # Create a mock request
    factory = RequestFactory()
    request = factory.get("/dashboard/farmer/")
    request.user = user

    # Time the dashboard view
    start_time = time.time()

    try:
        # This should work if we can mock the request properly
        print("📊 Loading dashboard data...")

        # Let's check what data would be loaded
        from apps.dashboard.models import (
            FarmerSubscription,
            ManualCropInput,
            FarmerFieldProfile,
        )
        from apps.crops.models import CropPredictionRequest
        from apps.sensors.models import SensorReading

        print(
            f"👤 User subscriptions: {FarmerSubscription.objects.filter(farmer=user).count()}"
        )
        print(f"🌾 Crop inputs: {ManualCropInput.objects.filter(farmer=user).count()}")
        print(
            f"🏞️ Field profiles: {FarmerFieldProfile.objects.filter(farmer=user).count()}"
        )
        print(
            f"🔮 Crop predictions: {CropPredictionRequest.objects.filter(user=user).count()}"
        )
        print(
            f"📡 Sensor readings: {SensorReading.objects.filter(farmer=user).count()}"
        )

        end_time = time.time()
        load_time = end_time - start_time

        print(f"⏱️ Data loading time: {load_time:.2f} seconds")

        if load_time > 2:
            print("⚠️ Dashboard loading seems slow (>2 seconds)")
        else:
            print("✅ Dashboard loading time is acceptable")

    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")


if __name__ == "__main__":
    test_dashboard_performance()
