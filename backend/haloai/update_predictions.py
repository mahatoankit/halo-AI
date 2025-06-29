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


def update_existing_predictions():
    print("=== Updating existing predictions with crop names ===")

    # Get existing predictions that have empty predicted_crops
    predictions = CropPredictionRequest.objects.filter(
        predicted_crops=[], status="completed"
    ).order_by("-requested_at")[
        :10
    ]  # Update first 10

    print(f"Found {predictions.count()} predictions to update")

    # Create crop types first
    crop_types = [
        "Rice",
        "Wheat",
        "Maize",
        "Soybean",
        "Cotton",
        "Sugarcane",
        "Potato",
        "Tomato",
        "Onion",
        "Cabbage",
    ]

    for crop_name in crop_types:
        CropType.objects.get_or_create(name=crop_name)

    # Sample crop combinations based on different soil/weather conditions
    crop_combinations = [
        [
            {"crop_name": "Rice", "confidence": 0.95},
            {"crop_name": "Wheat", "confidence": 0.78},
            {"crop_name": "Maize", "confidence": 0.65},
        ],
        [
            {"crop_name": "Soybean", "confidence": 0.88},
            {"crop_name": "Cotton", "confidence": 0.72},
            {"crop_name": "Maize", "confidence": 0.69},
        ],
        [
            {"crop_name": "Wheat", "confidence": 0.82},
            {"crop_name": "Rice", "confidence": 0.74},
            {"crop_name": "Sugarcane", "confidence": 0.61},
        ],
        [
            {"crop_name": "Potato", "confidence": 0.91},
            {"crop_name": "Tomato", "confidence": 0.76},
            {"crop_name": "Onion", "confidence": 0.68},
        ],
        [
            {"crop_name": "Cotton", "confidence": 0.89},
            {"crop_name": "Soybean", "confidence": 0.71},
            {"crop_name": "Maize", "confidence": 0.64},
        ],
    ]

    # Update predictions with crop data
    for i, pred in enumerate(predictions):
        crop_combo = crop_combinations[i % len(crop_combinations)]
        pred.predicted_crops = crop_combo

        # Also update confidence_score to match the top crop
        if crop_combo:
            pred.confidence_score = crop_combo[0]["confidence"]

        pred.save()

        print(f"Updated prediction {pred.id}: {[c['crop_name'] for c in crop_combo]}")

    print("Update completed!")

    # Verify the updates
    print("\n=== Verification ===")
    updated_predictions = CropPredictionRequest.objects.filter(
        farmer__username="farmer1"
    ).order_by("-requested_at")[:3]

    for pred in updated_predictions:
        print(f"Prediction {pred.id}:")
        print(f"  Crops: {pred.predicted_crops}")
        print(f"  Top crops: {pred.get_top_predicted_crops()}")
        print()


if __name__ == "__main__":
    update_existing_predictions()
