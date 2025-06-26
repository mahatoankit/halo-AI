#!/usr/bin/env python
"""
Create demo users and data for the HaloAI pitch presentation
"""

import os
import sys
import django

# Add the backend directory to path
sys.path.insert(
    0, "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")

django.setup()

from apps.users.models import CustomUser, FarmerProfile
from apps.sensors.models import IoTSensorSet, SensorReading
from apps.crops.models import CropType, CropPredictionRequest, CropRecommendation
from django.contrib.auth.hashers import make_password
from datetime import datetime, timezone, timedelta
import random


def create_demo_users():
    """Create demo users for pitch presentation"""

    # Community Admin for Bhairahawa-Butwal
    community_admin, created_ca = CustomUser.objects.get_or_create(
        username="community_admin_bhairahawa",
        defaults={
            "email": "admin.bhairahawa@halo-ai.demo",
            "password": make_password("demo123"),
            "role": "community_admin",
            "first_name": "Ramesh",
            "last_name": "Sharma",
            "assigned_region": "Bhairahawa-Butwal",
            "is_active": True,
            "is_approved": True,
        },
    )
    if created_ca:
        print(f"✅ Created Community Admin: {community_admin.username}")

    # Demo farmers
    farmers_data = [
        {
            "username": "farmer_krishna",
            "first_name": "Krishna",
            "last_name": "Adhikari",
            "assigned_region": "Bhairahawa",
        },
        {
            "username": "farmer_sita",
            "first_name": "Sita",
            "last_name": "Poudel",
            "assigned_region": "Butwal",
        },
        {
            "username": "farmer_ram",
            "first_name": "Ram",
            "last_name": "Bahadur",
            "assigned_region": "Bhairahawa",
        },
    ]

    created_farmers = []
    for farmer_data in farmers_data:
        farmer, created_f = CustomUser.objects.get_or_create(
            username=farmer_data["username"],
            defaults={
                "email": f"{farmer_data['username']}@halo-ai.demo",
                "password": make_password("demo123"),
                "role": "farmer",
                "first_name": farmer_data["first_name"],
                "last_name": farmer_data["last_name"],
                "assigned_region": farmer_data["assigned_region"],
                "is_active": True,
            },
        )
        if created_f:
            print(f"✅ Created Farmer: {farmer.username}")

            # Create farmer profile
            profile, created_p = FarmerProfile.objects.get_or_create(
                user=farmer,
                defaults={
                    "community_admin": community_admin,
                    "farm_location": farmer_data["assigned_region"],
                    "farm_size_acres": random.uniform(0.5, 5.0),
                    "primary_crops": random.choice(
                        ["Rice, Wheat", "Maize, Potato", "Sugarcane, Lentils"]
                    ),
                    "has_smartphone": random.choice(
                        [True, True, False]
                    ),  # Most have smartphones
                    "digital_literacy_level": random.choice(["basic", "intermediate"]),
                },
            )
            if created_p:
                print(f"  📋 Created profile for {farmer.username}")

        created_farmers.append(farmer)

    return community_admin, created_farmers


def create_demo_sensor_sets():
    """Create demo IoT sensor sets"""

    community_admin = CustomUser.objects.get(username="community_admin_bhairahawa")

    sensor_sets_data = [
        {
            "name": "Bhairahawa-Field-01",
            "location": "Bhairahawa North Farm",
            "lat": 27.5094,
            "lng": 83.4555,
        },
        {
            "name": "Bhairahawa-Field-02",
            "location": "Bhairahawa Central Farm",
            "lat": 27.5074,
            "lng": 83.4575,
        },
        {
            "name": "Butwal-Field-01",
            "location": "Butwal East Farm",
            "lat": 27.7000,
            "lng": 83.4500,
        },
    ]

    created_sensor_sets = []
    for sensor_data in sensor_sets_data:
        sensor_set, created_s = IoTSensorSet.objects.get_or_create(
            name=sensor_data["name"],
            defaults={
                "community_admin": community_admin,
                "location_name": sensor_data["location"],
                "latitude": sensor_data["lat"],
                "longitude": sensor_data["lng"],
                "status": "active",
                "region": "Bhairahawa-Butwal",
            },
        )
        if created_s:
            print(f"✅ Created Sensor Set: {sensor_set.name}")
        created_sensor_sets.append(sensor_set)

    return created_sensor_sets


def create_demo_sensor_readings(sensor_sets):
    """Create demo sensor readings"""

    sensor_types = ["temperature", "humidity", "ph", "soil_moisture", "light"]

    for sensor_set in sensor_sets:
        # Create readings for the last 7 days
        for i in range(7):
            reading_date = datetime.now(timezone.utc) - timedelta(days=i)

            # Create readings for each sensor type
            for sensor_type in sensor_types:
                value = 0.0  # Default value
                unit = ""  # Default unit

                if sensor_type == "temperature":
                    value = random.uniform(20, 35)
                    unit = "°C"
                elif sensor_type == "humidity":
                    value = random.uniform(60, 90)
                    unit = "%"
                elif sensor_type == "ph":
                    value = random.uniform(6.0, 7.5)
                    unit = "pH"
                elif sensor_type == "soil_moisture":
                    value = random.uniform(30, 80)
                    unit = "%"
                elif sensor_type == "light":
                    value = random.uniform(800, 1200)
                    unit = "lux"

                reading, created_r = SensorReading.objects.get_or_create(
                    sensor_set=sensor_set,
                    sensor_type=sensor_type,
                    timestamp=reading_date,
                    defaults={
                        "value": value,
                        "unit": unit,
                        "quality_score": random.uniform(0.85, 1.0),
                    },
                )
                if created_r:
                    print(
                        f"  📊 Created {sensor_type} reading for {sensor_set.name} on {reading_date.date()}"
                    )


def create_demo_crop_types():
    """Create demo crop types"""

    crops_data = [
        {
            "name": "Rice",
            "scientific_name": "Oryza sativa",
            "season": "Monsoon",
            "success_rate": 0.85,
        },
        {
            "name": "Wheat",
            "scientific_name": "Triticum aestivum",
            "season": "Winter",
            "success_rate": 0.78,
        },
        {
            "name": "Maize",
            "scientific_name": "Zea mays",
            "season": "Spring",
            "success_rate": 0.82,
        },
        {
            "name": "Potato",
            "scientific_name": "Solanum tuberosum",
            "season": "Winter",
            "success_rate": 0.75,
        },
        {
            "name": "Sugarcane",
            "scientific_name": "Saccharum officinarum",
            "season": "Year-round",
            "success_rate": 0.70,
        },
        {
            "name": "Lentils",
            "scientific_name": "Lens culinaris",
            "season": "Winter",
            "success_rate": 0.80,
        },
    ]

    created_crops = []
    for crop_data in crops_data:
        optimal_conditions = {
            "temperature_range": "20-30°C",
            "humidity_range": "60-80%",
            "ph_range": "6.0-7.5",
            "rainfall_range": "150-250mm",
        }

        crop, created_c = CropType.objects.get_or_create(
            name=crop_data["name"],
            defaults={
                "scientific_name": crop_data["scientific_name"],
                "optimal_conditions": optimal_conditions,
                "regional_success_rate": crop_data["success_rate"],
                "growing_season": crop_data["season"],
            },
        )
        if created_c:
            print(f"✅ Created Crop Type: {crop.name}")
        created_crops.append(crop)

    return created_crops


def create_demo_crop_predictions(farmers, crops, sensor_sets):
    """Create demo crop prediction requests"""

    community_admin = CustomUser.objects.get(username="community_admin_bhairahawa")

    for i, farmer in enumerate(farmers[:2]):  # Create predictions for first 2 farmers
        for j in range(3):  # 3 predictions per farmer
            request_date = datetime.now(timezone.utc) - timedelta(
                days=random.randint(1, 30)
            )

            # Assign different sensor sets to different predictions
            sensor_set = sensor_sets[i % len(sensor_sets)]

            prediction_request, created_pr = (
                CropPredictionRequest.objects.get_or_create(
                    community_admin=community_admin,
                    sensor_set=sensor_set,
                    requested_at=request_date,
                    defaults={
                        "nitrogen": random.uniform(80, 90),
                        "phosphorus": random.uniform(45, 55),
                        "potassium": random.uniform(35, 45),
                        "temperature": random.uniform(23, 28),
                        "humidity": random.uniform(70, 80),
                        "ph": random.uniform(6.5, 7.2),
                        "rainfall": random.uniform(180, 220),
                        "status": "completed",
                        "confidence_score": random.uniform(0.75, 0.95),
                        "predicted_crops": [
                            {
                                "crop": random.choice(crops).name,
                                "confidence": random.uniform(0.7, 0.9),
                            }
                            for _ in range(3)
                        ],
                    },
                )
            )

            if created_pr:
                print(f"✅ Created Prediction Request for sensor {sensor_set.name}")

                # Create recommendation
                recommended_crop = random.choice(crops)
                recommendation, created_rec = CropRecommendation.objects.get_or_create(
                    prediction_request=prediction_request,
                    crop_type=recommended_crop,
                    defaults={
                        "recommendation_type": "primary",
                        "confidence_score": random.uniform(0.75, 0.95),
                        "rationale": f"Recommended based on optimal conditions for {recommended_crop.name} in {sensor_set.region}",
                        "expected_yield": f"{random.randint(2000, 5000)} kg/hectare",
                        "risk_factors": [
                            "Weather dependency",
                            "Market price fluctuation",
                        ],
                        "local_market_demand": random.choice(["high", "medium"]),
                    },
                )
                if created_rec:
                    print(f"  🌾 Created recommendation: {recommended_crop.name}")


def main():
    """Main function to create all demo data"""
    print("🚀 Creating demo data for HaloAI pitch presentation...")

    # Create users
    community_admin, farmers = create_demo_users()

    # Create sensor sets
    sensor_sets = create_demo_sensor_sets()

    # Create sensor readings
    create_demo_sensor_readings(sensor_sets)

    # Create crop types
    crops = create_demo_crop_types()

    # Create crop predictions
    create_demo_crop_predictions(farmers, crops, sensor_sets)

    print("\n🎉 Demo data creation completed!")
    print("\n📋 Demo Accounts Created:")
    print("Community Admin: community_admin_bhairahawa / demo123")
    print("Farmers: farmer_krishna, farmer_sita, farmer_ram / demo123")
    print("Super Admin: admin / (existing password)")

    print("\n🌐 Key URLs to demo:")
    print("- Public Landing: http://127.0.0.1:8000/")
    print("- Dashboard (Login Required): http://127.0.0.1:8000/dashboard/")
    print("- Sensors Dashboard (Admin Only): http://127.0.0.1:8000/sensors/")
    print("- Crop Prediction (Login Required): http://127.0.0.1:8000/crop-prediction/")
    print("- Login Page: http://127.0.0.1:8000/auth/login/")
    print("- Signup Page: http://127.0.0.1:8000/auth/signup/")


if __name__ == "__main__":
    main()
