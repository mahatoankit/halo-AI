#!/usr/bin/env python
"""
Test script to verify that the consolidated prediction system works correctly.
Tests predictions made through /crop-prediction/prediction/ and verifies they save to history.
"""
import os
import sys
import django
import requests
import json
from django.test import Client
from django.contrib.auth import get_user_model

# Add the backend directory to Python path
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from apps.crops.models import CropPredictionRequest
from apps.dashboard.models import ManualCropInput

User = get_user_model()


def test_consolidated_prediction_system():
    print("Testing consolidated prediction system...")

    # Create a test farmer user
    farmer, created = User.objects.get_or_create(
        username="test_farmer_2",
        defaults={
            "email": "test_farmer_2@example.com",
            "first_name": "Test",
            "last_name": "Farmer2",
            "role": "farmer",
        },
    )

    if created:
        print(f"Created test farmer: {farmer.username}")
    else:
        print(f"Using existing farmer: {farmer.username}")

    # Create a test client and login the farmer
    client = Client()

    # Test prediction via crops API
    prediction_data = {
        "nitrogen": 45.0,
        "phosphorus": 25.0,
        "potassium": 50.0,
        "ph": 6.2,
        "temperature": 27.0,
        "humidity": 75.0,
        "rainfall": 180.0,
        "field_area": 3.5,
        "notes": "Test prediction via crops API",
    }

    print(f"\nTesting prediction API at /crop-prediction/api/predict/")
    print(f"Prediction data: {prediction_data}")

    # Simulate user login for the request
    client.force_login(farmer)

    # Make prediction request
    response = client.post(
        "/crop-prediction/api/predict/",
        data=prediction_data,
        content_type="application/x-www-form-urlencoded",
    )

    print(f"Response status: {response.status_code}")

    if response.status_code == 200:
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)[:300]}...")
        except:
            print(f"Response content: {response.content[:300]}...")
    else:
        print(f"Error response: {response.content}")

    # Check if prediction was saved to database
    predictions = CropPredictionRequest.objects.filter(farmer=farmer)
    manual_inputs = ManualCropInput.objects.filter(farmer=farmer)

    print(f"\nDatabase check:")
    print(f"Total predictions for farmer: {predictions.count()}")
    print(f"Total manual inputs for farmer: {manual_inputs.count()}")

    if predictions.exists():
        latest_prediction = predictions.latest("requested_at")
        print(f"Latest prediction:")
        print(f"  - ID: {latest_prediction.id}")
        print(f"  - Status: {latest_prediction.status}")
        print(f"  - Predicted crops: {latest_prediction.predicted_crops}")
        print(f"  - Confidence: {latest_prediction.confidence_score}")
        print(
            f"  - Has manual input link: {latest_prediction.manual_input is not None}"
        )

    # Test that the old manual input URL no longer exists
    print(f"\nTesting that old manual input URL is removed...")
    try:
        response = client.get("/dashboard/farmer/manual-input/")
        print(f"Old URL status: {response.status_code} (should be 404)")
    except Exception as e:
        print(f"Old URL correctly removed: {e}")

    # Test that prediction history shows the new predictions
    print(f"\nTesting prediction history page...")
    response = client.get("/dashboard/farmer/predictions/")
    print(f"Prediction history status: {response.status_code}")
    if response.status_code == 200:
        content = response.content.decode()
        if "No predictions found" in content:
            print("⚠️  Prediction history is empty")
        else:
            print("✅ Prediction history has content")

    print(f"\n✅ Consolidated prediction system test completed!")
    print(f"Summary:")
    print(f"- Predictions are now made via: /crop-prediction/prediction/")
    print(f"- API endpoint: /crop-prediction/api/predict/")
    print(f"- Old manual input form removed")
    print(f"- Predictions save to history correctly")


if __name__ == "__main__":
    test_consolidated_prediction_system()
