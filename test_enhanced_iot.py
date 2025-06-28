#!/usr/bin/env python
"""
Test script for Enhanced IoT Service
Validates Firebase integration and sensor data functionality
"""

import os
import sys
import django

# Add Django project path
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from services.enhanced_iot_service import enhanced_iot_service
import json


def test_enhanced_iot_service():
    """Test the enhanced IoT service functionality"""

    print("🧪 Testing Enhanced IoT Service")
    print("=" * 50)

    # Test 1: Service initialization
    print("\n1. Service Initialization Test")
    print(
        f"   Firebase DB: {'✅ Connected' if enhanced_iot_service.db_ref else '❌ Not connected'}"
    )
    print(
        f"   Firestore: {'✅ Connected' if enhanced_iot_service.firestore_client else '❌ Not connected'}"
    )
    print(
        f"   Sensor Locations: {len(enhanced_iot_service.sensor_locations)} configured"
    )

    # Test 2: Get latest sensor data
    print("\n2. Latest Sensor Data Test")
    sensor_id = "bhairahawa_farm_1"
    try:
        data = enhanced_iot_service.get_latest_sensor_data(sensor_id)
        print(f"   Sensor ID: {sensor_id}")
        print(f"   pH: {data.get('ph')}")
        print(f"   Temperature: {data.get('temperature')}°C")
        print(f"   Humidity: {data.get('humidity')}%")
        print(f"   Status: {data.get('status')}")
        print(f"   ✅ Data retrieved successfully")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Get all sensors data
    print("\n3. All Sensors Data Test")
    try:
        all_data = enhanced_iot_service.get_all_sensors_data()
        print(f"   Total sensors: {len(all_data)}")
        for sensor_id, data in all_data.items():
            print(
                f"   - {sensor_id}: pH={data.get('ph')}, Temp={data.get('temperature')}°C"
            )
        print(f"   ✅ All sensors data retrieved")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: Regional data
    print("\n4. Regional Data Test")
    try:
        regional_data = enhanced_iot_service.get_regional_average_data(
            "Bhairahawa-Butwal"
        )
        print(f"   Region: {regional_data.get('region')}")
        print(f"   Average pH: {regional_data.get('ph')}")
        print(f"   Average Temperature: {regional_data.get('temperature')}°C")
        print(f"   Active Sensors: {regional_data.get('active_sensors')}")
        print(f"   ✅ Regional data calculated")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 5: Sensor health
    print("\n5. Sensor Health Test")
    try:
        health = enhanced_iot_service.get_sensor_health_status(sensor_id)
        print(f"   Sensor: {sensor_id}")
        print(f"   Status: {health.get('status')}")
        print(f"   Health: {health.get('health')}")
        print(f"   Issues: {len(health.get('issues', []))}")
        print(f"   ✅ Health status checked")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 6: Demo data creation
    print("\n6. Demo Data Creation Test")
    try:
        success = enhanced_iot_service.create_demo_data(["demo_sensor_001"])
        if success:
            print(f"   ✅ Demo data created successfully")
            # Verify demo data
            demo_data = enhanced_iot_service.get_latest_sensor_data("demo_sensor_001")
            print(f"   Demo pH: {demo_data.get('ph')}")
            print(f"   Demo Temperature: {demo_data.get('temperature')}°C")
        else:
            print(f"   ❌ Demo data creation failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("🎯 Enhanced IoT Service Test Complete")

    # Summary
    sensor_count = len(enhanced_iot_service.sensor_locations)
    cache_count = len(enhanced_iot_service._readings_cache)

    print(f"\n📊 Summary:")
    print(f"   - Configured sensors: {sensor_count}")
    print(f"   - Cached readings: {cache_count}")
    print(
        f"   - Firebase status: {'Connected' if enhanced_iot_service.db_ref else 'Disconnected'}"
    )
    print(
        f"   - Service status: {'Operational' if sensor_count > 0 else 'Configuration needed'}"
    )


if __name__ == "__main__":
    test_enhanced_iot_service()
