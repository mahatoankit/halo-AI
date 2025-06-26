"""
IoT Data Service
Handles real-time sensor data collection from Firebase Realtime Database
Format: ph, temperature from IoT sensors
Example: 6.5,29.6
"""

import json
from datetime import datetime
from typing import Dict, Optional, Tuple, Union, Any
from firebase_admin import db
from .firebase_service_refactored import firebase_service


class IoTDataService:
    """Service to fetch real-time IoT sensor data from Firebase"""

    def __init__(self):
        self.firebase_service = firebase_service
        # Default IoT sensor locations in Bhairahawa region
        self.sensor_locations = {
            "bhairahawa_farm_1": {
                "lat": 27.5057,
                "lon": 83.4163,
                "region": "Bhairahawa-Butwal",
            },
            "butwal_farm_1": {
                "lat": 27.6855,
                "lon": 83.4409,
                "region": "Bhairahawa-Butwal",
            },
        }

    def get_latest_sensor_data(
        self, sensor_id: str = "bhairahawa_farm_1"
    ) -> Dict[str, Union[float, int, None]]:
        """
        Get latest IoT sensor data from Firebase Realtime Database
        Expected format in Firebase: ph, temperature
        Example: 6.5,29.6
        """
        try:
            # Reference to the sensor data in Firebase Realtime Database
            ref = db.reference(f"iot_sensors/{sensor_id}/latest")
            sensor_data = ref.get()

            if sensor_data:
                # Parse the comma-separated format: ph,temperature
                if isinstance(sensor_data, str) and "," in sensor_data:
                    values = sensor_data.split(",")
                    if len(values) >= 2:
                        return {
                            "ph": float(values[0].strip()),
                            "temperature": float(values[1].strip()),
                            "timestamp": None,
                        }
                elif isinstance(sensor_data, dict):
                    # Handle structured data format
                    return {
                        "ph": float(sensor_data.get("ph", 6.5)),
                        "temperature": float(sensor_data.get("temperature", 25.0)),
                        "timestamp": sensor_data.get("timestamp", None),
                    }

            # Return default values if no data available
            return self._get_default_sensor_data()

        except Exception as e:
            print(f"Error fetching IoT sensor data: {e}")
            return self._get_default_sensor_data()

    def get_all_sensors_data(
        self,
    ) -> Dict[str, Dict[str, Union[float, int, None, str]]]:
        """Get data from all available IoT sensors"""
        all_data = {}

        for sensor_id in self.sensor_locations.keys():
            sensor_data = self.get_latest_sensor_data(sensor_id)
            if sensor_data:
                all_data[sensor_id] = {
                    **sensor_data,
                    **self.sensor_locations[sensor_id],
                }

        return all_data

    def get_regional_average_data(
        self, region: str = "Bhairahawa-Butwal"
    ) -> Dict[str, Union[float, int]]:
        """
        Get regional average of all sensors in the specified region
        """
        all_data = self.get_all_sensors_data()
        region_sensors = [
            data for data in all_data.values() if data.get("region") == region
        ]

        if not region_sensors:
            return {"ph": 6.5, "temperature": 29.6, "sensor_count": 0}

        # Calculate averages
        ph_values = []
        temp_values = []

        for sensor in region_sensors:
            ph_val = sensor.get("ph")
            temp_val = sensor.get("temperature")

            if ph_val is not None:
                try:
                    ph_values.append(float(ph_val))
                except (ValueError, TypeError):
                    pass

            if temp_val is not None:
                try:
                    temp_values.append(float(temp_val))
                except (ValueError, TypeError):
                    pass

        avg_ph = sum(ph_values) / len(ph_values) if ph_values else 6.5
        avg_temp = sum(temp_values) / len(temp_values) if temp_values else 29.6

        return {
            "ph": round(avg_ph, 2),
            "temperature": round(avg_temp, 1),
            "sensor_count": len(region_sensors),
        }

    def store_sensor_reading(
        self, sensor_id: str, ph: float, temperature: float
    ) -> bool:
        """
        Store new sensor reading to Firebase
        Format: ph,temperature
        """
        try:
            ref = db.reference(f"iot_sensors/{sensor_id}")
            timestamp = int(datetime.now().timestamp())

            # Store in comma-separated format as specified
            data_string = f"{ph},{temperature}"

            ref.update(
                {
                    "latest": data_string,
                    "timestamp": timestamp,
                    "history": {timestamp: data_string},
                }
            )

            return True

        except Exception as e:
            print(f"Error storing sensor data: {e}")
            return False

    def _get_default_sensor_data(self) -> Dict[str, Union[float, int, None]]:
        """Return default sensor values when real data is unavailable"""
        return {"ph": 6.5, "temperature": 29.6, "timestamp": None}

    def simulate_sensor_data(
        self, sensor_id: str = "bhairahawa_farm_1"
    ) -> Dict[str, float]:
        """
        Simulate realistic sensor data for testing
        Based on typical Bhairahawa region conditions
        """
        import random

        # Realistic ranges for Bhairahawa region
        ph_range = (6.0, 7.5)
        temp_range = (20.0, 35.0)

        simulated_data = {
            "ph": round(random.uniform(*ph_range), 1),
            "temperature": round(random.uniform(*temp_range), 1),
            "timestamp": int(datetime.now().timestamp()),
            "simulated": True,
        }

        # Store simulated data
        self.store_sensor_reading(
            sensor_id, simulated_data["ph"], simulated_data["temperature"]
        )

        return simulated_data


# Global instance
iot_data_service = IoTDataService()
