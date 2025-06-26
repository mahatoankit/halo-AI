"""
Demo script to demonstrate the Firestore IoT relational database setup
This script shows how to map IoT components to community admins
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from django.contrib.auth import get_user_model
from services.firestore_iot_service import firestore_iot_service
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def create_demo_iot_mapping():
    """Create demo IoT sensor sets mapped to community admins"""

    print("🚀 Starting Firestore IoT Mapping Demo")
    print("=" * 50)

    # Check if Firestore is available
    if not firestore_iot_service.is_available():
        print(
            "❌ Firestore is not available. Please check your Firebase configuration."
        )
        return

    # Get community admins from Django
    community_admins = User.objects.filter(role="community_admin")

    if not community_admins.exists():
        print("⚠️ No community admins found. Creating sample admin...")
        admin = User.objects.create_user(
            username="demo_admin",
            email="demo@haloai.com",
            password="demo123",
            first_name="Demo",
            last_name="Admin",
            role="community_admin",
            assigned_region="Bhairahawa-Butwal",
            is_approved=True,
        )
        community_admins = [admin]
    else:
        community_admins = list(community_admins)

    print(f"📊 Found {len(community_admins)} community admin(s)")

    # Create IoT sensor sets for each admin
    for i, admin in enumerate(community_admins):
        print(f"\n👤 Creating IoT sensor set for {admin.username} (ID: {admin.id})")

        # Sample sensor set data
        sensor_set_data = {
            "community_admin_id": admin.id,
            "name": f"SensorSet_{admin.username}_{i+1}",
            "location_name": f"{admin.assigned_region} Farm Site {i+1}",
            "latitude": 27.5167 + (i * 0.01),  # Sample coordinates around Nepal
            "longitude": 83.4667 + (i * 0.01),
            "region": admin.assigned_region or "Bhairahawa-Butwal",
            "status": "active",
            "default_nitrogen": 85.0,
            "default_phosphorus": 50.0,
            "default_potassium": 40.0,
        }

        # Create sensor set in Firestore
        sensor_set_id = firestore_iot_service.create_iot_sensor_set(sensor_set_data)

        if sensor_set_id:
            print(f"✅ Created sensor set: {sensor_set_id}")

            # Add sample IoT components to the sensor set
            component_types = [
                {
                    "component_type": "soil_sensor",
                    "model": "NPK-100",
                    "manufacturer": "AgriTech",
                },
                {
                    "component_type": "temperature_sensor",
                    "model": "TMP-36",
                    "manufacturer": "Sensirion",
                },
                {
                    "component_type": "humidity_sensor",
                    "model": "DHT-22",
                    "manufacturer": "Aosong",
                },
                {
                    "component_type": "ph_sensor",
                    "model": "PH-4502C",
                    "manufacturer": "Generic",
                },
            ]

            for component_data in component_types:
                component_data["status"] = "active"
                component_data["specifications"] = {
                    "accuracy": "±2%",
                    "range": "0-100",
                    "power": "3.3V",
                }

                component_id = firestore_iot_service.add_iot_component(
                    sensor_set_id, component_data
                )
                if component_id:
                    print(
                        f"  🔧 Added {component_data['component_type']}: {component_id}"
                    )

                    # Add sample sensor reading
                    reading_data = {
                        "sensor_type": component_data["component_type"],
                        "value": 75.5 + (i * 5),  # Sample values
                        "unit": get_unit_for_sensor(component_data["component_type"]),
                        "quality_score": 0.95,
                        "metadata": {"location": sensor_set_data["location_name"]},
                    }

                    success = firestore_iot_service.store_sensor_reading(
                        component_id, reading_data
                    )
                    if success:
                        print(
                            f"    📊 Added sample reading: {reading_data['value']} {reading_data['unit']}"
                        )
        else:
            print(f"❌ Failed to create sensor set for {admin.username}")

    print("\n" + "=" * 50)
    print("📈 Demo Summary")
    print("=" * 50)

    # Display summary for each admin
    for admin in community_admins:
        dashboard_data = firestore_iot_service.get_admin_dashboard_data(admin.id)
        print(f"\n👤 {admin.username} ({admin.assigned_region}):")
        print(f"   📡 Sensor Sets: {dashboard_data.get('total_sensor_sets', 0)}")
        print(f"   🔧 Components: {dashboard_data.get('total_components', 0)}")
        print(f"   ✅ Active Sets: {dashboard_data.get('active_sensor_sets', 0)}")

        # Show sensor sets
        sensor_sets = dashboard_data.get("sensor_sets", [])
        for sensor_set in sensor_sets:
            print(
                f"      📍 {sensor_set.get('name')} at {sensor_set.get('location_name')}"
            )

    # Regional overview
    regions = list(
        set(
            [
                admin.assigned_region
                for admin in community_admins
                if admin.assigned_region
            ]
        )
    )
    for region in regions:
        regional_data = firestore_iot_service.get_regional_sensor_overview(region)
        print(f"\n🌍 Regional Overview - {region}:")
        print(f"   📡 Total Sensor Sets: {regional_data.get('total_sensor_sets', 0)}")
        print(f"   ✅ Active Sensor Sets: {regional_data.get('active_sensor_sets', 0)}")
        print(
            f"   👥 Community Admins: {len(regional_data.get('community_admins', []))}"
        )


def get_unit_for_sensor(sensor_type):
    """Get appropriate unit for sensor type"""
    units = {
        "soil_sensor": "ppm",
        "temperature_sensor": "°C",
        "humidity_sensor": "%",
        "ph_sensor": "pH",
    }
    return units.get(sensor_type, "")


def demonstrate_queries():
    """Demonstrate various query capabilities"""
    print("\n🔍 Demonstrating Query Capabilities")
    print("=" * 50)

    # Get all community admins
    community_admins = User.objects.filter(role="community_admin")

    for admin in community_admins:
        print(f"\n👤 Querying data for {admin.username}:")

        # Get sensor sets for this admin
        sensor_sets = firestore_iot_service.get_sensor_sets_by_admin(admin.id)
        print(f"   📡 Found {len(sensor_sets)} sensor sets")

        for sensor_set in sensor_sets:
            sensor_set_id = sensor_set.get("sensor_set_id")
            print(f"   📍 Sensor Set: {sensor_set.get('name')}")

            # Get components for this sensor set
            components = firestore_iot_service.get_components_by_sensor_set(
                sensor_set_id
            )
            print(f"      🔧 Components: {len(components)}")

            for component in components:
                component_id = component.get("component_id")
                component_type = component.get("component_type")

                # Get recent readings for this component
                readings = firestore_iot_service.get_recent_readings(
                    component_id, limit=5
                )
                print(f"         📊 {component_type}: {len(readings)} recent readings")

                if readings:
                    latest = readings[0]
                    print(
                        f"            Latest: {latest.get('value')} {latest.get('unit')}"
                    )


if __name__ == "__main__":
    try:
        # Create demo data
        create_demo_iot_mapping()

        # Demonstrate queries
        demonstrate_queries()

        print("\n✅ Demo completed successfully!")
        print("\n📚 Firestore Collections Created:")
        print("   • iot_sensor_sets - Main sensor set documents")
        print("   • iot_components - Individual IoT components")
        print("   • sensor_readings - Time-series sensor data")
        print("   • admin_sensor_mappings - Relational mappings")
        print("\n🔗 Relationships:")
        print("   • Community Admin -> IoT Sensor Sets (1:N)")
        print("   • IoT Sensor Set -> IoT Components (1:N)")
        print("   • IoT Component -> Sensor Readings (1:N)")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo script error: {e}", exc_info=True)
