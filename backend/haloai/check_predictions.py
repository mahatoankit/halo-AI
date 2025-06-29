#!/usr/bin/env python
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from apps.crops.models import CropPredictionRequest, CropType
from django.contrib.auth import get_user_model

User = get_user_model()


def check_predictions():
    print("=== Checking CropPredictionRequest data ===")

    # Get all predictions
    predictions = CropPredictionRequest.objects.all()
    print(f"Total predictions: {predictions.count()}")

    if predictions.count() == 0:
        print("No predictions found. Let's create some sample data.")
        create_sample_data()
        predictions = CropPredictionRequest.objects.all()

    # Check first few predictions
    for i, pred in enumerate(predictions[:3]):
        print(f"\n--- Prediction {i+1} ---")
        print(f"ID: {pred.id}")
        print(f"Farmer: {pred.farmer}")
        print(f"Status: {pred.status}")
        print(f"Predicted crops (raw): {pred.predicted_crops}")
        print(f"Predicted crops type: {type(pred.predicted_crops)}")

        # Try the new method
        try:
            parsed_crops = pred.parsed_predicted_crops
            print(f"Parsed crops: {parsed_crops}")
            top_crops = pred.get_top_predicted_crops()
            print(f"Top crops: {top_crops}")
        except Exception as e:
            print(f"Error parsing crops: {e}")

        print(f"Confidence score: {pred.confidence_score}")
        print(f"Requested at: {pred.requested_at}")


def create_sample_data():
    print("Creating sample prediction data...")

    # Get or create a farmer user
    farmer, created = User.objects.get_or_create(
        username="testfarmer",
        defaults={
            "email": "testfarmer@example.com",
            "first_name": "Test",
            "last_name": "Farmer",
            "role": "farmer",
        },
    )

    # Create sample crop types
    crop_types = ["Rice", "Wheat", "Maize", "Soybean", "Cotton", "Sugarcane"]

    for crop_name in crop_types:
        CropType.objects.get_or_create(name=crop_name)

    # Create sample predictions with proper crop data
    sample_predictions = [
        {
            "nitrogen": 90,
            "phosphorus": 42,
            "potassium": 43,
            "temperature": 20.8,
            "humidity": 82,
            "ph": 6.5,
            "rainfall": 202.9,
            "predicted_crops": [
                {"crop_name": "Rice", "confidence": 0.95},
                {"crop_name": "Wheat", "confidence": 0.78},
                {"crop_name": "Maize", "confidence": 0.65},
            ],
            "confidence_score": 0.95,
            "status": "completed",
        },
        {
            "nitrogen": 85,
            "phosphorus": 58,
            "potassium": 41,
            "temperature": 25.2,
            "humidity": 75,
            "ph": 6.8,
            "rainfall": 145.5,
            "predicted_crops": [
                {"crop_name": "Soybean", "confidence": 0.88},
                {"crop_name": "Cotton", "confidence": 0.72},
                {"crop_name": "Maize", "confidence": 0.69},
            ],
            "confidence_score": 0.88,
            "status": "completed",
        },
        {
            "nitrogen": 78,
            "phosphorus": 35,
            "potassium": 52,
            "temperature": 22.5,
            "humidity": 68,
            "ph": 7.1,
            "rainfall": 180.3,
            "predicted_crops": [
                {"crop_name": "Wheat", "confidence": 0.82},
                {"crop_name": "Rice", "confidence": 0.74},
                {"crop_name": "Sugarcane", "confidence": 0.61},
            ],
            "confidence_score": 0.82,
            "status": "completed",
        },
    ]

    for data in sample_predictions:
        pred = CropPredictionRequest.objects.create(farmer=farmer, **data)
        print(f"Created prediction: {pred.id}")

    print("Sample data created successfully!")


if __name__ == "__main__":
    check_predictions()
