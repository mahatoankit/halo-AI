#!/usr/bin/env python3
"""
Test script to verify the farmer dashboard data and UI fixes
"""

import os
import sys
import django
import apps

# Add the Django project to the path
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from apps.crops.models import CropPredictionRequest
from django.contrib.auth import get_user_model

User = get_user_model()


def test_prediction_data():
    """Test that the prediction data is correctly formatted"""
    print("Testing crop prediction data structure...")

    predictions = CropPredictionRequest.objects.all()
    print(f"Found {predictions.count()} crop predictions")

    for prediction in predictions[:3]:  # Test first 3 predictions
        print(f"\nPrediction ID: {prediction.id}")
        print(f"Status: {prediction.status}")
        print(f"Requested at: {prediction.requested_at}")
        print(
            f"Sensor set: {prediction.sensor_set.name if prediction.sensor_set else 'None'}"
        )
        print(f"Predicted crops: {prediction.predicted_crops}")

        # Test the template logic
        if prediction.predicted_crops and len(prediction.predicted_crops) > 0:
            if "crop" in prediction.predicted_crops[0]:
                crop_name = prediction.predicted_crops[0]["crop"]
                confidence = prediction.predicted_crops[0].get("confidence", 0)
                print(f"✅ Crop: {crop_name.title()}, Confidence: {confidence:.2f}")
            else:
                print("❌ Crop field not found in predicted_crops")
        else:
            print("⚠️ No predicted crops or empty list")

        print("-" * 50)


if __name__ == "__main__":
    test_prediction_data()
