"""
Management command to create demo IoT devices and sensor data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from apps.users.models import CustomUser
from apps.sensors.models import IoTDevice, SensorData, DeviceGroup


class Command(BaseCommand):
    help = "Create demo IoT devices and sensor data"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating demo IoT devices and data...")

        # Get existing users
        community_admin = CustomUser.objects.filter(role="community_admin").first()
        farmers = list(CustomUser.objects.filter(role="farmer"))

        if not community_admin:
            self.stdout.write(self.style.ERROR("No community admin found!"))
            return

        if not farmers:
            self.stdout.write(self.style.ERROR("No farmers found!"))
            return

        # Demo device locations
        locations = [
            {
                "name": "Bhairahawa North Farm",
                "lat": "27.5094",
                "lng": "83.4555",
                "region": "Bhairahawa-Butwal",
                "district": "Rupandehi",
            },
            {
                "name": "Butwal East Farm",
                "lat": "27.7000",
                "lng": "83.4500",
                "region": "Bhairahawa-Butwal",
                "district": "Rupandehi",
            },
            {
                "name": "Lumbini Research Station",
                "lat": "27.4833",
                "lng": "83.2833",
                "region": "Bhairahawa-Butwal",
                "district": "Rupandehi",
            },
        ]

        device_types = ["soil_sensor", "weather_station", "ph_meter"]
        devices_created = 0

        # Create devices
        for i, location in enumerate(locations):
            for j, device_type in enumerate(device_types):
                assigned_user = farmers[i % len(farmers)]

                device_id = f'IOT-{location["region"][:3].upper()}-{i+1:02d}{j+1:02d}'

                device, created = IoTDevice.objects.get_or_create(
                    device_id=device_id,
                    defaults={
                        "name": f'{location["name"]} - {device_type.replace("_", " ").title()}',
                        "assigned_to": assigned_user,
                        "device_type": device_type,
                        "location_name": location["name"],
                        "latitude": Decimal(location["lat"]),
                        "longitude": Decimal(location["lng"]),
                        "region": location["region"],
                        "district": location["district"],
                        "status": "active",
                        "manufacturer": "SensorTech",
                        "model_number": f"ST-{random.randint(100, 999)}",
                    },
                )

                if created:
                    devices_created += 1
                    self.stdout.write(
                        f"  ✅ Created: {device.device_id} - {device.name}"
                    )

                    # Create sensor data for this device
                    readings_created = 0
                    for day in range(7):  # 7 days of data
                        for hour in range(0, 24, 6):  # 4 readings per day
                            reading_time = timezone.now() - timedelta(
                                days=day, hours=hour
                            )

                            SensorData.objects.create(
                                device=device,
                                timestamp=reading_time,
                                nitrogen=(
                                    random.uniform(20, 100)
                                    if device_type in ["soil_sensor"]
                                    else None
                                ),
                                phosphorus=(
                                    random.uniform(10, 60)
                                    if device_type in ["soil_sensor"]
                                    else None
                                ),
                                potassium=(
                                    random.uniform(15, 80)
                                    if device_type in ["soil_sensor"]
                                    else None
                                ),
                                temperature=random.uniform(15, 35),
                                humidity=random.uniform(40, 90),
                                ph=(
                                    random.uniform(5.5, 8.0)
                                    if device_type in ["ph_meter", "soil_sensor"]
                                    else None
                                ),
                                soil_moisture=random.uniform(20, 80),
                                light_intensity=(
                                    random.uniform(200, 1500)
                                    if device_type == "weather_station"
                                    else None
                                ),
                                battery_level=random.uniform(30, 100),
                                signal_strength=random.uniform(-80, -20),
                                data_quality=random.choice(
                                    ["excellent", "good", "good", "fair"]
                                ),
                                quality_score=random.uniform(0.8, 1.0),
                            )
                            readings_created += 1

                    self.stdout.write(
                        f"    📊 Created {readings_created} sensor readings"
                    )

        # Create device groups
        groups_created = 0
        for location in locations:
            location_devices = IoTDevice.objects.filter(location_name=location["name"])
            if location_devices.exists():
                group, created = DeviceGroup.objects.get_or_create(
                    name=f'{location["name"]} Group',
                    defaults={
                        "description": f'All devices at {location["name"]}',
                        "group_type": "farm",
                        "owner": community_admin,
                        "location_name": location["name"],
                        "latitude": Decimal(location["lat"]),
                        "longitude": Decimal(location["lng"]),
                        "region": location["region"],
                    },
                )

                if created:
                    group.devices.set(location_devices)
                    groups_created += 1
                    self.stdout.write(
                        f"  🏗️ Created group: {group.name} with {location_devices.count()} devices"
                    )

        # Summary
        total_devices = IoTDevice.objects.count()
        total_readings = SensorData.objects.count()
        total_groups = DeviceGroup.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Demo data creation completed!\n"
                f"📱 Total devices: {total_devices}\n"
                f"📊 Total sensor readings: {total_readings}\n"
                f"🏗️ Total device groups: {total_groups}\n"
            )
        )
