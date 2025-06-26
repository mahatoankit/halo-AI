"""
Django management command to setup IoT sensor mappings with community admins
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from services.firestore_iot_service import firestore_iot_service
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Setup IoT sensor mappings with community admins in Firestore"

    def add_arguments(self, parser):
        parser.add_argument(
            "--create-demo",
            action="store_true",
            help="Create demo IoT sensor sets and components",
        )
        parser.add_argument(
            "--admin-id",
            type=int,
            help="Specific community admin ID to create sensors for",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Starting IoT Sensor Setup"))

        # Check Firestore availability
        if not firestore_iot_service.is_available():
            self.stdout.write(
                self.style.ERROR(
                    "❌ Firestore is not available. Check Firebase configuration."
                )
            )
            return

        self.stdout.write(self.style.SUCCESS("✅ Firestore connection verified"))

        if options["create_demo"]:
            self.create_demo_data(options.get("admin_id"))
        else:
            self.show_existing_data()

    def create_demo_data(self, specific_admin_id=None):
        """Create demo IoT sensor data"""
        self.stdout.write("📊 Creating demo IoT sensor data...")

        # Get community admins
        if specific_admin_id:
            admins = User.objects.filter(id=specific_admin_id, role="community_admin")
        else:
            admins = User.objects.filter(role="community_admin", is_approved=True)

        if not admins.exists():
            self.stdout.write(self.style.WARNING("⚠️ No community admins found."))
            return

        for admin in admins:
            self.stdout.write(f"👤 Creating sensors for {admin.username}...")

            # Create sensor set
            sensor_set_data = {
                "community_admin_id": admin.id,
                "name": f"IoT_Farm_{admin.username}",
                "location_name": f"{admin.assigned_region or 'Default'} Farm Site",
                "latitude": 27.5167,
                "longitude": 83.4667,
                "region": admin.assigned_region or "Bhairahawa-Butwal",
                "status": "active",
            }

            sensor_set_id = firestore_iot_service.create_iot_sensor_set(sensor_set_data)

            if sensor_set_id:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Created sensor set: {sensor_set_id}")
                )

                # Add components
                components = [
                    {
                        "component_type": "soil_sensor",
                        "model": "NPK-Analyzer-Pro",
                        "manufacturer": "AgriTech Solutions",
                    },
                    {
                        "component_type": "temperature_sensor",
                        "model": "TempMaster-5000",
                        "manufacturer": "WeatherTech",
                    },
                    {
                        "component_type": "humidity_sensor",
                        "model": "HumidityPro-300",
                        "manufacturer": "ClimateControl Inc",
                    },
                ]

                for component_data in components:
                    component_id = firestore_iot_service.add_iot_component(
                        sensor_set_id, component_data
                    )
                    if component_id:
                        self.stdout.write(
                            f'    🔧 Added {component_data["component_type"]}: {component_id[:8]}...'
                        )

                        # Add sample reading
                        reading_data = {
                            "sensor_type": component_data["component_type"],
                            "value": self.get_sample_value(
                                component_data["component_type"]
                            ),
                            "unit": self.get_unit(component_data["component_type"]),
                            "quality_score": 0.95,
                        }

                        firestore_iot_service.store_sensor_reading(
                            component_id, reading_data
                        )
                        self.stdout.write(
                            f'      📊 Added sample reading: {reading_data["value"]} {reading_data["unit"]}'
                        )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ❌ Failed to create sensor set for {admin.username}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("✅ Demo data creation completed!"))

    def show_existing_data(self):
        """Show existing IoT sensor data"""
        self.stdout.write("📋 Showing existing IoT sensor data...")

        admins = User.objects.filter(role="community_admin")

        for admin in admins:
            dashboard_data = firestore_iot_service.get_admin_dashboard_data(admin.id)

            self.stdout.write(f"\n👤 {admin.username}:")
            self.stdout.write(
                f'   📡 Sensor Sets: {dashboard_data.get("total_sensor_sets", 0)}'
            )
            self.stdout.write(
                f'   🔧 Components: {dashboard_data.get("total_components", 0)}'
            )
            self.stdout.write(
                f'   ✅ Active Sets: {dashboard_data.get("active_sensor_sets", 0)}'
            )

            sensor_sets = dashboard_data.get("sensor_sets", [])
            for sensor_set in sensor_sets:
                self.stdout.write(
                    f'      📍 {sensor_set.get("name")} at {sensor_set.get("location_name")}'
                )

    def get_sample_value(self, sensor_type):
        """Get sample sensor value"""
        values = {
            "soil_sensor": 85.2,
            "temperature_sensor": 24.5,
            "humidity_sensor": 65.8,
            "ph_sensor": 6.8,
        }
        return values.get(sensor_type, 50.0)

    def get_unit(self, sensor_type):
        """Get sensor unit"""
        units = {
            "soil_sensor": "ppm",
            "temperature_sensor": "°C",
            "humidity_sensor": "%",
            "ph_sensor": "pH",
        }
        return units.get(sensor_type, "")
