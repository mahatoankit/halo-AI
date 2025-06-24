"""
IoT data collection and processing service for HALO-AI
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional
import logging
from pathlib import Path

from ..sensors.soil_sensors import MultiSensorNode, SENSOR_CONFIGURATIONS
from ...shared.schemas import IoTSensorData, CropFeatures
from ...shared.config import settings

logger = logging.getLogger(__name__)


class DataCollectionService:
    """Service for collecting and processing IoT sensor data"""

    def __init__(self):
        self.sensor_nodes: Dict[str, MultiSensorNode] = {}
        self.data_buffer: List[Dict] = []
        self.max_buffer_size = 1000
        self.is_collecting = False

    def initialize_sensors(self):
        """Initialize sensor nodes based on configuration"""
        for farm_section, config in SENSOR_CONFIGURATIONS.items():
            for node_id in config["sensors"]:
                location = config["location"].copy()
                # Add some variation to sensor locations
                location["lat"] += (hash(node_id) % 100) * 0.0001
                location["lon"] += (hash(node_id) % 100) * 0.0001

                self.sensor_nodes[node_id] = MultiSensorNode(node_id, location)
                logger.info(f"Initialized sensor node {node_id} at {location}")

    async def collect_single_reading(self, node_id: str) -> Optional[IoTSensorData]:
        """Collect a single reading from a specific sensor node"""
        if node_id not in self.sensor_nodes:
            logger.error(f"Sensor node {node_id} not found")
            return None

        try:
            sensor_node = self.sensor_nodes[node_id]
            raw_data = sensor_node.collect_all_data()

            # Convert to IoTSensorData schema
            sensor_data = IoTSensorData(
                device_id=node_id,
                timestamp=str(raw_data["timestamp"]),
                soil_nitrogen=raw_data["nitrogen"],
                soil_phosphorous=raw_data["phosphorous"],
                soil_potassium=raw_data["potassium"],
                soil_ph=raw_data["ph"],
                ambient_temperature=raw_data["temperature"],
                humidity=raw_data["humidity"],
                rainfall=raw_data.get("rainfall", 0.0),
                location=sensor_node.location,
            )

            return sensor_data

        except Exception as e:
            logger.error(f"Error collecting data from {node_id}: {str(e)}")
            return None

    async def collect_all_readings(self) -> List[IoTSensorData]:
        """Collect readings from all active sensor nodes"""
        readings = []

        for node_id in self.sensor_nodes.keys():
            reading = await self.collect_single_reading(node_id)
            if reading:
                readings.append(reading)

        logger.info(f"Collected {len(readings)} sensor readings")
        return readings

    def convert_to_ml_features(self, sensor_data: IoTSensorData) -> CropFeatures:
        """Convert IoT sensor data to ML model features"""
        return CropFeatures(
            nitrogen=sensor_data.soil_nitrogen,
            phosphorous=sensor_data.soil_phosphorous,
            potassium=sensor_data.soil_potassium,
            temperature=sensor_data.ambient_temperature,
            humidity=sensor_data.humidity,
            ph=sensor_data.soil_ph,
            rainfall=sensor_data.rainfall or 0.0,
        )

    async def save_data_to_file(
        self, data: List[IoTSensorData], filename: Optional[str] = None
    ):
        """Save collected data to a JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"iot_data_{timestamp}.json"

        file_path = settings.DATA_PATH / filename

        try:
            # Convert to serializable format
            data_dict = [
                {
                    "device_id": d.device_id,
                    "timestamp": d.timestamp,
                    "soil_nitrogen": d.soil_nitrogen,
                    "soil_phosphorous": d.soil_phosphorous,
                    "soil_potassium": d.soil_potassium,
                    "soil_ph": d.soil_ph,
                    "ambient_temperature": d.ambient_temperature,
                    "humidity": d.humidity,
                    "rainfall": d.rainfall,
                    "location": d.location,
                }
                for d in data
            ]

            with open(file_path, "w") as f:
                json.dump(data_dict, f, indent=2)

            logger.info(f"Saved {len(data)} readings to {file_path}")

        except Exception as e:
            logger.error(f"Error saving data to file: {str(e)}")

    async def start_continuous_collection(self, interval_seconds: int = 300):
        """Start continuous data collection at specified intervals"""
        if self.is_collecting:
            logger.warning("Data collection is already running")
            return

        self.is_collecting = True
        logger.info(
            f"Starting continuous data collection every {interval_seconds} seconds"
        )

        try:
            while self.is_collecting:
                readings = await self.collect_all_readings()

                # Add to buffer
                for reading in readings:
                    if len(self.data_buffer) >= self.max_buffer_size:
                        # Remove oldest entries
                        self.data_buffer = self.data_buffer[len(readings) :]

                    self.data_buffer.append(reading.dict())

                # Save to file periodically (every hour)
                if len(self.data_buffer) % 12 == 0:  # Assuming 5-minute intervals
                    await self.save_data_to_file(readings)

                await asyncio.sleep(interval_seconds)

        except Exception as e:
            logger.error(f"Error in continuous collection: {str(e)}")
        finally:
            self.is_collecting = False

    def stop_continuous_collection(self):
        """Stop continuous data collection"""
        self.is_collecting = False
        logger.info("Stopped continuous data collection")

    def get_sensor_status(self) -> Dict:
        """Get status of all sensor nodes"""
        status = {
            "total_nodes": len(self.sensor_nodes),
            "active_nodes": 0,
            "data_buffer_size": len(self.data_buffer),
            "is_collecting": self.is_collecting,
            "nodes": {},
        }

        for node_id, node in self.sensor_nodes.items():
            node_status = node.get_node_status()
            status["nodes"][node_id] = node_status
            if node_status["node_status"] == "operational":
                status["active_nodes"] += 1

        return status


# Global data collection service instance
data_collection_service = DataCollectionService()
