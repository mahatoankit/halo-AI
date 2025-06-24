"""
Soil sensor simulation and data collection for HALO-AI
"""

import random
import time
from datetime import datetime, timezone
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SoilSensor:
    """Simulated soil sensor for NPK, pH monitoring"""

    def __init__(self, device_id: str, location: Optional[Dict] = None):
        self.device_id = device_id
        self.location = location or {"lat": 0.0, "lon": 0.0}
        self.is_active = True

    def read_soil_nutrients(self) -> Dict[str, float]:
        """Read soil nutrient levels (NPK)"""
        if not self.is_active:
            raise RuntimeError(f"Sensor {self.device_id} is not active")

        # Simulate realistic soil nutrient readings with some variation
        base_values = {
            "nitrogen": 90 + random.uniform(-20, 20),
            "phosphorous": 42 + random.uniform(-15, 15),
            "potassium": 43 + random.uniform(-10, 10),
            "ph": 6.5 + random.uniform(-1.0, 1.0),
        }

        # Ensure values are within realistic ranges
        base_values["nitrogen"] = max(0, min(200, base_values["nitrogen"]))
        base_values["phosphorous"] = max(0, min(150, base_values["phosphorous"]))
        base_values["potassium"] = max(0, min(250, base_values["potassium"]))
        base_values["ph"] = max(0, min(14, base_values["ph"]))

        logger.info(
            f"Soil sensor {self.device_id} read: N={base_values['nitrogen']:.1f}, P={base_values['phosphorous']:.1f}, K={base_values['potassium']:.1f}, pH={base_values['ph']:.1f}"
        )

        return base_values

    def get_device_status(self) -> Dict:
        """Get device status information"""
        return {
            "device_id": self.device_id,
            "status": "active" if self.is_active else "inactive",
            "location": self.location,
            "last_reading": datetime.now(timezone.utc).isoformat(),
            "battery_level": random.uniform(60, 100),  # Simulated battery level
        }


class EnvironmentalSensor:
    """Simulated environmental sensor for temperature, humidity, rainfall"""

    def __init__(self, device_id: str, location: Optional[Dict] = None):
        self.device_id = device_id
        self.location = location or {"lat": 0.0, "lon": 0.0}
        self.is_active = True

    def read_environmental_data(self) -> Dict[str, float]:
        """Read environmental conditions"""
        if not self.is_active:
            raise RuntimeError(f"Environmental sensor {self.device_id} is not active")

        # Simulate realistic environmental readings
        base_values = {
            "temperature": 25.0 + random.uniform(-5, 15),  # 20-40°C range
            "humidity": 70.0 + random.uniform(-20, 20),  # 50-90% range
            "rainfall": (
                random.uniform(0, 10) if random.random() > 0.7 else 0
            ),  # Occasional rainfall
        }

        # Ensure values are within realistic ranges
        base_values["temperature"] = max(-10, min(50, base_values["temperature"]))
        base_values["humidity"] = max(0, min(100, base_values["humidity"]))
        base_values["rainfall"] = max(0, base_values["rainfall"])

        logger.info(
            f"Environmental sensor {self.device_id} read: T={base_values['temperature']:.1f}°C, H={base_values['humidity']:.1f}%, R={base_values['rainfall']:.1f}mm"
        )

        return base_values

    def get_device_status(self) -> Dict:
        """Get device status information"""
        return {
            "device_id": self.device_id,
            "status": "active" if self.is_active else "inactive",
            "location": self.location,
            "last_reading": datetime.now(timezone.utc).isoformat(),
            "battery_level": random.uniform(60, 100),  # Simulated battery level
        }


class MultiSensorNode:
    """Combined sensor node with soil and environmental sensors"""

    def __init__(self, node_id: str, location: Optional[Dict] = None):
        self.node_id = node_id
        self.location = location or {"lat": 0.0, "lon": 0.0}
        self.soil_sensor = SoilSensor(f"{node_id}_soil", location)
        self.env_sensor = EnvironmentalSensor(f"{node_id}_env", location)

    def collect_all_data(self) -> Dict[str, float]:
        """Collect data from all sensors in the node"""
        try:
            soil_data = self.soil_sensor.read_soil_nutrients()
            env_data = self.env_sensor.read_environmental_data()

            # Combine all sensor data
            combined_data = {
                **soil_data,
                **env_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "node_id": self.node_id,
            }

            return combined_data

        except Exception as e:
            logger.error(f"Error collecting data from node {self.node_id}: {str(e)}")
            raise

    def get_node_status(self) -> Dict:
        """Get status of the entire sensor node"""
        return {
            "node_id": self.node_id,
            "location": self.location,
            "soil_sensor": self.soil_sensor.get_device_status(),
            "environmental_sensor": self.env_sensor.get_device_status(),
            "node_status": (
                "operational"
                if (self.soil_sensor.is_active and self.env_sensor.is_active)
                else "partial"
            ),
        }


# Predefined sensor configurations for different regions
SENSOR_CONFIGURATIONS = {
    "farm_north": {
        "location": {"lat": 40.7128, "lon": -74.0060, "region": "North Field"},
        "sensors": ["node_001", "node_002", "node_003"],
    },
    "farm_south": {
        "location": {"lat": 40.7000, "lon": -74.0100, "region": "South Field"},
        "sensors": ["node_004", "node_005", "node_006"],
    },
    "greenhouse": {
        "location": {"lat": 40.7150, "lon": -74.0080, "region": "Greenhouse"},
        "sensors": ["node_007", "node_008"],
    },
}
