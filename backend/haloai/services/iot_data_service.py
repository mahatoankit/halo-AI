import json
from datetime import datetime
from typing import Dict, Optional, Tuple, Union, Any
from firebase_admin import db
from .firebase_service_refactored import firebase_service


class IoTDataService:
    """Service to fetch real-time IoT sensor data from Firebase"""

    # Default constants for fallback values
    DEFAULT_PH = 6.5
    DEFAULT_TEMP = 29.6
    DEFAULT_SOIL_TEMP = 25.0
    DEFAULT_HUMIDITY = 60.0

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
        Get latest IoT sensor data from Firebase Realtime Database.
        Maps Firebase variable names to internal schema.
        """
        try:
            ref = db.reference(f"iot_sensors/{sensor_id}/latest")
            sensor_data = ref.get()

            if sensor_data:
                # Handle structured dictionary format
                if isinstance(sensor_data, dict):
                    return {
                        "ph": float(sensor_data.get("phValue", self.DEFAULT_PH)),
                        "temperature": float(sensor_data.get("airTemperature", self.DEFAULT_TEMP)),
                        "soil_temperature": float(
                            sensor_data.get("soilTemperature", self.DEFAULT_SOIL_TEMP)
                        ),
                        "humidity": float(sensor_data.get("humidity", self.DEFAULT_HUMIDITY)),
                        "timestamp": sensor_data.get("timestamp", None),
                    }

                # Legacy support for comma-separated string format
                elif isinstance(sensor_data, str) and "," in sensor_data:
                    values = sensor_data.split(",")
                    if len(values) >= 2:
                        return {
                            "ph": float(values[0].strip()),
                            "temperature": float(values[1].strip()),
                            "soil_temperature": self.DEFAULT_SOIL_TEMP,
                            "humidity": self.DEFAULT_HUMIDITY,
                            "timestamp": None,
                        }

            return self._get_default_sensor_data()

        except Exception as e:
            print(f"Error fetching IoT sensor data for {sensor_id}: {e}")
            return self._get_default_sensor_data()

    def get_all_sensors_data(
        self,
    ) -> Dict[str, Dict[str, Union[float, int, None, str]]]:
        """
        Get data from all available IoT sensors.
        Optimized to perform a single Firebase request for the entire node.
        """
        all_results = {}
        try:
            # Fetch the entire sensors node in one call for efficiency
            root_ref = db.reference("iot_sensors")
            all_sensors_raw = root_ref.get() or {}

            for sensor_id, location_info in self.sensor_locations.items():
                sensor_entry = all_sensors_raw.get(sensor_id, {})
                latest_raw = sensor_entry.get("latest")

                # Parse data similar to get_latest_sensor_data but from local dict
                if isinstance(latest_raw, dict):
                    parsed_data = {
                        "ph": float(latest_raw.get("phValue", self.DEFAULT_PH)),
                        "temperature": float(latest_raw.get("airTemperature", self.DEFAULT_TEMP)),
                        "soil_temperature": float(latest_raw.get("soilTemperature", self.DEFAULT_SOIL_TEMP)),
                        "humidity": float(latest_raw.get("humidity", self.DEFAULT_HUMIDITY)),
                        "timestamp": latest_raw.get("timestamp"),
                    }
                else:
                    parsed_data = self._get_default_sensor_data()

                all_results[sensor_id] = {**parsed_data, **location_info}

        except Exception as e:
            print(f"Error fetching all sensor data: {e}")
            # Fallback to defaults for known locations
            for sensor_id, location_info in self.sensor_locations.items():
                all_results[sensor_id] = {**self._get_default_sensor_data(), **location_info}

        return all_results

    def get_regional_average_data(
        self, region: str = "Bhairahawa-Butwal"
    ) -> Dict[str, Union[float, int]]:
        """
        Get regional average of all sensors in the specified region.
        """
        all_data = self.get_all_sensors_data()
        region_sensors = [
            data for data in all_data.values() if data.get("region") == region
        ]

        if not region_sensors:
            return {
                "ph": self.DEFAULT_PH,
                "temperature": self.DEFAULT_TEMP,
                "soil_temperature": self.DEFAULT_SOIL_TEMP,
                "humidity": self.DEFAULT_HUMIDITY,
                "sensor_count": 0,
            }

        metrics = {"ph": [], "temperature": [], "soil_temperature": [], "humidity": []}

        for sensor in region_sensors:
            for key in metrics.keys():
                val = sensor.get(key)
                if val is not None:
                    try:
                        metrics[key].append(float(val))
                    except (ValueError, TypeError):
                        pass

        return {
            "ph": round(sum(metrics["ph"]) / len(metrics["ph"]), 2) if metrics["ph"] else self.DEFAULT_PH,
            "temperature": round(sum(metrics["temperature"]) / len(metrics["temperature"]), 1) if metrics["temperature"] else self.DEFAULT_TEMP,
            "soil_temperature": round(sum(metrics["soil_temperature"]) / len(metrics["soil_temperature"]), 1) if metrics["soil_temperature"] else self.DEFAULT_SOIL_TEMP,
            "humidity": round(sum(metrics["humidity"]) / len(metrics["humidity"]), 1) if metrics["humidity"] else self.DEFAULT_HUMIDITY,
            "sensor_count": len(region_sensors),
        }

    def store_sensor_reading(
        self, 
        sensor_id: str, 
        ph: float, 
        temperature: float, 
        soil_temp: float = 25.0, 
        humidity: float = 60.0
    ) -> bool:
        """
        Store new sensor reading to Firebase in structured format.
        """
        try:
            ref = db.reference(f"iot_sensors/{sensor_id}")
            timestamp = int(datetime.now().timestamp())

            data_payload = {
                "phValue": ph,
                "airTemperature": temperature,
                "soilTemperature": soil_temp,
                "humidity": humidity,
                "timestamp": timestamp
            }

            ref.update({
                "latest": data_payload,
                "timestamp": timestamp,
                "history": {str(timestamp): data_payload}
            })

            return True

        except Exception as e:
            print(f"Error storing sensor data: {e}")
            return False

    def _get_default_sensor_data(self) -> Dict[str, Union[float, int, None]]:
        """Return default sensor values when real data is unavailable"""
        return {
            "ph": self.DEFAULT_PH,
            "temperature": self.DEFAULT_TEMP,
            "soil_temperature": self.DEFAULT_SOIL_TEMP,
            "humidity": self.DEFAULT_HUMIDITY,
            "timestamp": None,
        }

    def simulate_sensor_data(
        self, sensor_id: str = "bhairahawa_farm_1"
    ) -> Dict[str, Any]:
        """
        Simulate realistic sensor data for testing based on Bhairahawa conditions.
        """
        import random

        simulated_data = {
            "ph": round(random.uniform(6.0, 7.5), 1),
            "temperature": round(random.uniform(20.0, 35.0), 1),
            "soil_temperature": round(random.uniform(18.0, 28.0), 1),
            "humidity": round(random.uniform(50.0, 85.0), 1),
            "timestamp": int(datetime.now().timestamp()),
            "simulated": True,
        }

        self.store_sensor_reading(
            sensor_id, 
            simulated_data["ph"], 
            simulated_data["temperature"],
            simulated_data["soil_temperature"],
            simulated_data["humidity"]
        )

        return simulated_data


# Global instance
iot_data_service = IoTDataService()
