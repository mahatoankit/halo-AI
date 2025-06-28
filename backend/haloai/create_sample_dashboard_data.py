#!/usr/bin/env python3
"""
Script to create sa
farmer = User.obje    # Create subscription plan     # Get or create a community admin for the subscription
    try:
        community_admin = User.objects.filter(role="community_admin").first(    for i, input_data in enumerate(sample_inputs):
        # Just skip if inputs already exist for this farmer
        existing_count = ManualCropInput.objects.filter(farmer=farmer).count()
        if existing_count >= 3:
            print(f"✅ Manual inputs already exist, skipping creation")
            break

        manual_input = ManualCropInput.objects.create(
            farmer=farmer,
            **input_data
        )
        manual_inputs.append(manual_input)
        print(f"✅ Created manual input {i+1}") if not community_admin:
            community_admin = User.objects.create_user(
                email="admin@haloai.com",
                username="community_admin",
                first_name="Community",
                last_name="Admin",
                role="community_admin",
                phone="+977-9876543211",
            )
            community_admin.set_password("adminpass123")
            community_admin.save()
            print("✅ Created community admin")
    except Exception as e:
        print(f"Using existing admin or creating default")
        community_admin = User.objects.filter(role="community_admin").first()

    # Create farmer subscription
    subscription, created = FarmerSubscription.objects.get_or_create(
        farmer=farmer,
        defaults={
            'plan': basic_plan,
            'community_admin': community_admin,
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=30),
            'status': 'active',
            'predictions_used': 3  # Used 3 out of 10
        }
    )'t exist
    basic_plan, created = SubscriptionPlan.objects.get_or_create(
        name="basic",
        defaults={
            'display_name': 'Basic Farmer Plan',
            'description': 'Essential tools for small-scale farming',
            'price': 299.00,
            'monthly_predictions': 10,
            'expert_consultation': True,
            'sensor_data_access': False,
            'soil_health_reports': False,
            'weather_alerts': True,
            'is_active': True
        }
    )r(
            email=farmer_email,
            username="test_farmer",
            first_name="Test",
            last_name="Farmer",
            role="farmer",
            phone="+977-9876543210"
        )hboard data for testing the farmer dashboard
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
import uuid

# Add the project root to Python path
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.crops.models import CropPredictionRequest
from apps.dashboard.models import (
    SubscriptionPlan,
    FarmerSubscription,
    FarmerFieldProfile,
    SoilHealthReport,
    ManualCropInput,
)
from django.utils import timezone

User = get_user_model()


def create_sample_dashboard_data():
    """Create sample data for the farmer dashboard"""

    print("🌾 Creating sample dashboard data...")

    # Get or create test farmer user
    farmer_email = "test.farmer@haloai.com"
    farmer_username = "test_farmer"

    try:
        farmer = User.objects.get(email=farmer_email)
        print(f"✅ Using existing farmer: {farmer.email}")
    except User.DoesNotExist:
        # Try to get by username in case email doesn't match
        try:
            farmer = User.objects.get(username=farmer_username)
            print(f"✅ Using existing farmer by username: {farmer.username}")
        except User.DoesNotExist:
            farmer = User.objects.create_user(
                email=farmer_email,
                username=farmer_username,
                first_name="Test",
                last_name="Farmer",
                role="farmer",
                phone="+977-9876543210",
            )
            farmer.set_password("testpass123")
            farmer.save()
            print(f"✅ Created farmer: {farmer.email}")

    # Create subscription plan if it doesn't exist
    basic_plan, created = SubscriptionPlan.objects.get_or_create(
        name="basic",
        defaults={
            "display_name": "Basic Farmer Plan",
            "description": "Essential tools for small-scale farming",
            "price": 299.00,
            "monthly_predictions": 10,
            "expert_consultation": True,
            "sensor_data_access": False,
            "soil_health_reports": False,
            "weather_alerts": True,
            "is_active": True,
        },
    )
    if created:
        print("✅ Created Basic Farmer Plan")

    # Get or create a community admin for the subscription
    try:
        community_admin = User.objects.filter(role="community_admin").first()
        if not community_admin:
            community_admin = User.objects.create_user(
                email="admin@haloai.com",
                username="community_admin",
                first_name="Community",
                last_name="Admin",
                role="community_admin",
                phone="+977-9876543211",
            )
            community_admin.set_password("adminpass123")
            community_admin.save()
            print("✅ Created community admin")
    except Exception as e:
        print(f"Using existing admin or creating default")
        community_admin = User.objects.filter(role="community_admin").first()

    # Create farmer subscription
    subscription, created = FarmerSubscription.objects.get_or_create(
        farmer=farmer,
        defaults={
            "plan": basic_plan,
            "community_admin": community_admin,
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=30),
            "status": "active",
            "predictions_used": 3,  # Used 3 out of 10
        },
    )
    if created:
        print("✅ Created farmer subscription")

    # Create field profile
    field_profile, created = FarmerFieldProfile.objects.get_or_create(
        farmer=farmer,
        defaults={
            "region": "Lumbini Province",
            "district": "Rupandehi",
            "local_unit": "Bhairahawa",
            "total_area": 15.5,
            "soil_type": "loamy",
            "irrigation_type": "drip",
            "primary_crops": "Rice, Wheat, Maize",
            "secondary_crops": "Tomato, Potato",
            "organic_farming": False,
            "experience_years": 8,
        },
    )
    if created:
        print("✅ Created field profile")

    # Create manual crop inputs for predictions
    manual_inputs = []

    # Sample input data for different crop predictions
    sample_inputs = [
        {
            "nitrogen": 45.2,
            "phosphorus": 32.1,
            "potassium": 28.7,
            "temperature": 28.5,
            "humidity": 65.2,
            "ph": 6.8,
            "rainfall": 85.3,
            "field_area": 2.5,
            "notes": "Good quality soil with adequate moisture",
        },
        {
            "nitrogen": 38.7,
            "phosphorus": 28.9,
            "potassium": 35.2,
            "temperature": 27.2,
            "humidity": 70.1,
            "ph": 7.1,
            "rainfall": 92.7,
            "field_area": 1.8,
            "notes": "Clay soil suitable for wheat cultivation",
        },
        {
            "nitrogen": 52.1,
            "phosphorus": 35.8,
            "potassium": 30.9,
            "temperature": 29.8,
            "humidity": 58.3,
            "ph": 6.5,
            "rainfall": 78.1,
            "field_area": 3.2,
            "notes": "Sandy loam with good drainage for vegetable crops",
        },
    ]

    for i, input_data in enumerate(sample_inputs):
        # Just skip if inputs already exist for this farmer
        existing_count = ManualCropInput.objects.filter(farmer=farmer).count()
        if existing_count >= 3:
            print(f"✅ Manual inputs already exist, skipping creation")
            break

        manual_input = ManualCropInput.objects.create(farmer=farmer, **input_data)
        manual_inputs.append(manual_input)
        print(f"✅ Created manual input {i+1}")

    # Create crop prediction requests
    crop_predictions = [
        {
            "farmer": farmer,
            "manual_input": manual_inputs[0] if manual_inputs else None,
            "nitrogen": 45.2,
            "phosphorus": 32.1,
            "potassium": 28.7,
            "temperature": 28.5,
            "humidity": 65.2,
            "ph": 6.8,
            "rainfall": 85.3,
            "status": "completed",
            "predicted_crops": [
                {"name": "Rice", "confidence": 0.92, "crop_name": "Rice"},
                {"name": "Wheat", "confidence": 0.78, "crop_name": "Wheat"},
                {"name": "Maize", "confidence": 0.65, "crop_name": "Maize"},
            ],
            "confidence_score": 0.92,
            "requested_at": timezone.now() - timedelta(days=2),
        },
        {
            "farmer": farmer,
            "manual_input": manual_inputs[1] if len(manual_inputs) > 1 else None,
            "nitrogen": 38.7,
            "phosphorus": 28.9,
            "potassium": 35.2,
            "temperature": 27.2,
            "humidity": 70.1,
            "ph": 7.1,
            "rainfall": 92.7,
            "status": "completed",
            "predicted_crops": [
                {"name": "Wheat", "confidence": 0.89, "crop_name": "Wheat"},
                {"name": "Barley", "confidence": 0.72, "crop_name": "Barley"},
                {"name": "Mustard", "confidence": 0.61, "crop_name": "Mustard"},
            ],
            "confidence_score": 0.89,
            "requested_at": timezone.now() - timedelta(days=7),
        },
        {
            "farmer": farmer,
            "manual_input": manual_inputs[2] if len(manual_inputs) > 2 else None,
            "nitrogen": 52.1,
            "phosphorus": 35.8,
            "potassium": 30.9,
            "temperature": 29.8,
            "humidity": 58.3,
            "ph": 6.5,
            "rainfall": 78.1,
            "status": "processing",
            "predicted_crops": [],
            "confidence_score": None,
            "requested_at": timezone.now() - timedelta(hours=6),
        },
        {
            "farmer": farmer,
            "nitrogen": 41.5,
            "phosphorus": 30.2,
            "potassium": 33.8,
            "temperature": 26.7,
            "humidity": 68.4,
            "ph": 6.9,
            "rainfall": 88.9,
            "status": "completed",
            "predicted_crops": [
                {"name": "Tomato", "confidence": 0.85, "crop_name": "Tomato"},
                {"name": "Potato", "confidence": 0.79, "crop_name": "Potato"},
                {"name": "Onion", "confidence": 0.68, "crop_name": "Onion"},
            ],
            "confidence_score": 0.85,
            "requested_at": timezone.now() - timedelta(days=12),
        },
        {
            "farmer": farmer,
            "nitrogen": 48.9,
            "phosphorus": 33.7,
            "potassium": 29.1,
            "temperature": 30.2,
            "humidity": 62.8,
            "ph": 6.4,
            "rainfall": 73.5,
            "status": "completed",
            "predicted_crops": [
                {"name": "Maize", "confidence": 0.91, "crop_name": "Maize"},
                {"name": "Sorghum", "confidence": 0.74, "crop_name": "Sorghum"},
                {"name": "Millet", "confidence": 0.63, "crop_name": "Millet"},
            ],
            "confidence_score": 0.91,
            "requested_at": timezone.now() - timedelta(days=18),
        },
    ]

    for i, prediction_data in enumerate(crop_predictions):
        # Check if prediction already exists
        existing = CropPredictionRequest.objects.filter(
            farmer=farmer, requested_at__date=prediction_data["requested_at"].date()
        ).first()

        if not existing:
            prediction = CropPredictionRequest.objects.create(**prediction_data)
            print(f"✅ Created crop prediction {i+1}: {prediction.status}")

    # Create soil health reports
    soil_reports_data = [
        {
            "farmer": farmer,
            "report_type": "lab_test",
            "ph": 6.8,
            "nitrogen": 45.2,
            "phosphorus": 32.1,
            "potassium": 28.7,
            "organic_matter": 1.8,
            "electrical_conductivity": 0.85,
            "zinc": 2.1,
            "iron": 8.7,
            "copper": 1.2,
            "manganese": 4.5,
            "health_score": 82,
            "test_date": timezone.now().date() - timedelta(days=5),
            "recommendations": "Soil health is good. Maintain organic matter levels. Consider adding zinc fertilizer for better crop yield.",
            "lab_name": "Agricultural Research Lab",
        },
        {
            "farmer": farmer,
            "report_type": "field_test",
            "ph": 7.1,
            "nitrogen": 38.7,
            "phosphorus": 28.9,
            "potassium": 35.2,
            "organic_matter": 1.5,
            "electrical_conductivity": 0.92,
            "zinc": 1.8,
            "iron": 9.2,
            "copper": 1.0,
            "manganese": 3.9,
            "health_score": 76,
            "test_date": timezone.now().date() - timedelta(days=45),
            "recommendations": "Soil pH is slightly high. Consider adding organic matter to improve nitrogen levels.",
        },
        {
            "farmer": farmer,
            "report_type": "lab_test",
            "ph": 6.5,
            "nitrogen": 52.1,
            "phosphorus": 35.8,
            "potassium": 30.9,
            "organic_matter": 2.1,
            "electrical_conductivity": 0.78,
            "zinc": 2.4,
            "iron": 7.9,
            "copper": 1.3,
            "manganese": 5.1,
            "health_score": 88,
            "test_date": timezone.now().date() - timedelta(days=90),
            "recommendations": "Excellent soil health. Continue current practices. Optimal for most crop varieties.",
            "lab_name": "Nepal Agricultural Research Center",
        },
    ]

    for i, report_data in enumerate(soil_reports_data):
        report, created = SoilHealthReport.objects.get_or_create(
            farmer=farmer, test_date=report_data["test_date"], defaults=report_data
        )
        if created:
            print(f"✅ Created soil health report {i+1}")

    print("\n🎉 Sample dashboard data created successfully!")
    print(f"📊 Dashboard URL: http://localhost:8000/dashboard/farmer/")
    print(f"👤 Login with: {farmer_email} / testpass123")


if __name__ == "__main__":
    create_sample_dashboard_data()
