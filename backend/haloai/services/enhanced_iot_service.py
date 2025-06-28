"""
Enhanced IoT Data Service with Robust Firebase Integration
Provides improved error handling, data validation, and real-time sensor monitoring
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List, Union, Any, Tuple
from dataclasses import dataclass, asdict
from firebase_admin import db, firestore
from .firebase_service_refactored import firebase_service

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class SensorReading:
    """Data class for sensor readings with validation"""

    sensor_id: str
    ph: float
    temperature: float
    humidity: float = 60.0
    soil_temperature: float = 25.0
    timestamp: Optional[str] = None
    location: Optional[str] = None
    region: str = "Bhairahawa-Butwal"
    status: str = "active"

    def __post_init__(self):
        """Validate sensor data after initialization"""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

        # Validate ranges for sensor values
        self.ph = max(0.0, min(14.0, self.ph))  # pH range 0-14
        self.temperature = max(
            -50.0, min(100.0, self.temperature)
        )  # Temperature range -50 to 100°C
        self.humidity = max(0.0, min(100.0, self.humidity))  # Humidity 0-100%
        self.soil_temperature = max(
            -50.0, min(100.0, self.soil_temperature)
        )  # Soil temp range

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    def is_valid(self) -> bool:
        """Check if sensor reading is within valid ranges"""
        return (
            0.0 <= self.ph <= 14.0
            and -50.0 <= self.temperature <= 100.0
            and 0.0 <= self.humidity <= 100.0
            and -50.0 <= self.soil_temperature <= 100.0
        )


class EnhancedIoTService:
    """Enhanced IoT service with robust Firebase integration and error handling"""

    def __init__(self):
        self.firebase_service = firebase_service
        self.db_ref = None
        self.firestore_client = None
        self._initialize_connections()

        # Default sensor locations with enhanced metadata
        self.sensor_locations = {
            "bhairahawa_farm_1": {
                "lat": 27.5057,
                "lon": 83.4163,
                "region": "Bhairahawa-Butwal",
                "farm_name": "Farm A - Wheat Field",
                "crops": ["wheat", "rice", "maize"],
                "installation_date": "2024-01-15",
                "sensor_types": ["ph", "temperature", "humidity", "soil_temperature"],
            },
            "butwal_farm_1": {
                "lat": 27.6855,
                "lon": 83.4409,
                "region": "Bhairahawa-Butwal",
                "farm_name": "Farm B - Rice Field",
                "crops": ["rice", "vegetables"],
                "installation_date": "2024-01-20",
                "sensor_types": ["ph", "temperature", "humidity", "soil_temperature"],
            },
            "demo_sensor_001": {
                "lat": 27.5500,
                "lon": 83.4300,
                "region": "Bhairahawa-Butwal",
                "farm_name": "Demo Farm - Mixed Crops",
                "crops": ["demo"],
                "installation_date": "2024-01-01",
                "sensor_types": ["ph", "temperature", "humidity", "soil_temperature"],
            },
        }

        # Cache for recent readings to reduce Firebase calls
        self._readings_cache = {}
        self._cache_ttl = 30  # 30 seconds cache TTL for more frequent updates

    def _initialize_connections(self):
        """Initialize Firebase connections with error handling"""
        try:
            if self.firebase_service.db_ref:
                self.db_ref = self.firebase_service.db_ref
                logger.info("✅ Firebase Realtime Database connection established")
            else:
                logger.warning("⚠️ Firebase Realtime Database not available")

            if self.firebase_service.firestore_client:
                self.firestore_client = self.firebase_service.firestore_client
                logger.info("✅ Firestore connection established")
            else:
                logger.warning("⚠️ Firestore not available")

        except Exception as e:
            logger.error(f"❌ Firebase connection failed: {e}")

    def get_latest_sensor_data(
        self, sensor_id: str = "bhairahawa_farm_1", use_cache: bool = True
    ) -> Dict[str, Union[float, int, str, None]]:
        """
        Get latest IoT sensor data with enhanced error handling and validation
        """
        logger.info(f"🔍 Fetching data for sensor: {sensor_id}")

        # Check cache first
        if use_cache and self._is_cache_valid(sensor_id):
            logger.info(f"📋 Using cached data for sensor: {sensor_id}")
            return self._readings_cache[sensor_id]["data"]

        try:
            # Try Firebase Realtime Database first
            sensor_data = self._fetch_from_realtime_db(sensor_id)

            if sensor_data:
                reading = self._parse_sensor_data(sensor_id, sensor_data)
                if reading and reading.is_valid():
                    result = reading.to_dict()
                    self._update_cache(sensor_id, result)
                    logger.info(f"✅ Successfully fetched valid data for {sensor_id}")
                    return result

            # Fallback to Firestore if available
            if self.firestore_client:
                sensor_data = self._fetch_from_firestore(sensor_id)
                if sensor_data:
                    reading = self._parse_sensor_data(sensor_id, sensor_data)
                    if reading and reading.is_valid():
                        result = reading.to_dict()
                        self._update_cache(sensor_id, result)
                        logger.info(
                            f"✅ Successfully fetched data from Firestore for {sensor_id}"
                        )
                        return result

            # If no valid data found, generate intelligent defaults
            logger.warning(
                f"⚠️ No valid sensor data found for {sensor_id}, using intelligent defaults"
            )
            return self._get_intelligent_default_data(sensor_id)

        except Exception as e:
            logger.error(f"❌ Error fetching sensor data for {sensor_id}: {e}")
            return self._get_intelligent_default_data(sensor_id)

    def _fetch_from_realtime_db(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Firebase Realtime Database"""
        if not self.db_ref:
            return None

        try:
            # Try multiple path patterns based on actual Firebase structure
            paths_to_try = [
                f"sensorData",  # Root level sensor data
                f"sensorData/{sensor_id}",  # Sensor-specific data
                f"iot_sensors/{sensor_id}/latest",  # Our structured format
                f"sensors/{sensor_id}/latest",  # Alternative structured format
                f"sensor_data/{sensor_id}/current",  # Current reading format
                f"iot_data/{sensor_id}",  # Simple IoT data format
                f"{sensor_id}",  # Direct sensor ID path
                f"data/{sensor_id}",  # Data subfolder
                f"realtime/{sensor_id}",  # Realtime subfolder
            ]

            for path in paths_to_try:
                logger.debug(f"🔍 Trying Firebase path: {path}")
                ref = self.db_ref.child(path)
                data = ref.get()

                if data:
                    logger.info(f"📊 Found data at Firebase path: {path}")
                    logger.debug(f"Raw data: {data}")

                    # If we got the root sensorData, return it directly
                    if path == "sensorData" and isinstance(data, dict):
                        # Check if it has the expected format (prioritize soilTemperature)
                        if any(
                            key in data
                            for key in [
                                "soilTemperature",
                                "phValue",
                                "humidity",
                                "airTemperature",
                            ]
                        ):
                            return data
                        # If it's a nested structure, try to find sensor data
                        for key, value in data.items():
                            if isinstance(value, dict) and any(
                                subkey in value
                                for subkey in [
                                    "soilTemperature",
                                    "phValue",
                                    "airTemperature",
                                ]
                            ):
                                logger.info(
                                    f"📊 Found nested sensor data under key: {key}"
                                )
                                return value

                    # For other paths, validate the data structure
                    if isinstance(data, dict):
                        return data
                    elif isinstance(data, str):
                        # Handle string data format
                        return {"raw_data": data}

            logger.warning(
                f"⚠️ No data found for sensor {sensor_id} in any Firebase path"
            )
            return None

        except Exception as e:
            logger.error(f"❌ Firebase Realtime DB fetch error for {sensor_id}: {e}")
            return None

    def _fetch_from_firestore(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Firestore as fallback"""
        if not self.firestore_client:
            return None

        try:
            doc_ref = self.firestore_client.collection("sensor_readings").document(
                sensor_id
            )
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()

            return None

        except Exception as e:
            logger.error(f"❌ Firestore fetch error: {e}")
            return None

    def _parse_sensor_data(
        self, sensor_id: str, raw_data: Any
    ) -> Optional[SensorReading]:
        """Parse raw sensor data into SensorReading object"""
        try:
            location_info = self.sensor_locations.get(sensor_id, {})

            # Handle different data formats
            if isinstance(raw_data, dict):
                # Check for the actual Firebase format first (prioritize soilTemperature)
                if (
                    "soilTemperature" in raw_data
                    or "phValue" in raw_data
                    or "airTemperature" in raw_data
                ):
                    # Firebase format: airTemperature, humidity, phValue, soilTemperature
                    # Use soilTemperature as primary temperature value
                    logger.info(f"📊 Parsing Firebase format data for {sensor_id}")
                    return SensorReading(
                        sensor_id=sensor_id,
                        ph=float(raw_data.get("phValue", 6.5)),
                        temperature=float(raw_data.get("soilTemperature", 25.0)),
                        humidity=float(raw_data.get("humidity", 60.0)),
                        soil_temperature=float(raw_data.get("soilTemperature", 25.0)),
                        timestamp=raw_data.get("timestamp"),
                        location=location_info.get("farm_name"),
                        region=location_info.get("region", "Bhairahawa-Butwal"),
                        status="active",  # Mark as active since we have real data
                    )

                # Fallback to generic structured format
                else:
                    logger.info(f"📊 Parsing generic format data for {sensor_id}")
                    return SensorReading(
                        sensor_id=sensor_id,
                        ph=float(raw_data.get("ph", raw_data.get("phValue", 6.5))),
                        temperature=float(
                            raw_data.get(
                                "temperature",
                                raw_data.get(
                                    "soilTemperature",
                                    raw_data.get("airTemperature", 25.0),
                                ),
                            )
                        ),
                        humidity=float(raw_data.get("humidity", 60.0)),
                        soil_temperature=float(
                            raw_data.get(
                                "soil_temperature",
                                raw_data.get("soilTemperature", 25.0),
                            )
                        ),
                        timestamp=raw_data.get("timestamp"),
                        location=location_info.get("farm_name"),
                        region=location_info.get("region", "Bhairahawa-Butwal"),
                        status="active",
                    )

            elif isinstance(raw_data, str):
                # Handle string data format
                if "," in raw_data:
                    # Legacy comma-separated format: "ph,temperature"
                    values = raw_data.split(",")
                    if len(values) >= 2:
                        logger.info(f"📊 Parsing CSV format data for {sensor_id}")
                        return SensorReading(
                            sensor_id=sensor_id,
                            ph=float(values[0].strip()),
                            temperature=float(values[1].strip()),
                            location=location_info.get("farm_name"),
                            region=location_info.get("region", "Bhairahawa-Butwal"),
                            status="active",
                        )
                elif raw_data:
                    # Single value string - treat as raw data
                    logger.info(
                        f"📊 Parsing raw string data for {sensor_id}: {raw_data}"
                    )
                    return None  # Cannot parse single string value

            logger.warning(
                f"⚠️ Unrecognized data format for {sensor_id}: {type(raw_data)}"
            )
            return None

        except (ValueError, TypeError) as e:
            logger.error(f"❌ Error parsing sensor data for {sensor_id}: {e}")
            logger.error(f"Raw data: {raw_data}")
            return None

    def _is_cache_valid(self, sensor_id: str) -> bool:
        """Check if cached data is still valid"""
        if sensor_id not in self._readings_cache:
            return False

        cache_time = self._readings_cache[sensor_id]["timestamp"]
        return (
            datetime.now(timezone.utc) - cache_time
        ).total_seconds() < self._cache_ttl

    def _update_cache(self, sensor_id: str, data: Dict[str, Any]):
        """Update cache with new sensor data"""
        self._readings_cache[sensor_id] = {
            "data": data,
            "timestamp": datetime.now(timezone.utc),
        }

    def _get_intelligent_default_data(
        self, sensor_id: str
    ) -> Dict[str, Union[float, int, str, None]]:
        """Generate intelligent default data based on sensor location and time"""
        location_info = self.sensor_locations.get(sensor_id, {})

        # Time-based variations for more realistic defaults
        current_hour = datetime.now().hour

        # Temperature varies by time of day
        base_temp = 25.0
        if 6 <= current_hour < 12:  # Morning
            temp_adjustment = 0.0
        elif 12 <= current_hour < 18:  # Afternoon
            temp_adjustment = 5.0
        elif 18 <= current_hour < 22:  # Evening
            temp_adjustment = 2.0
        else:  # Night
            temp_adjustment = -3.0

        # Regional pH variations
        region_ph_defaults = {
            "Bhairahawa-Butwal": 6.8,
            "Kathmandu": 6.5,
            "Pokhara": 7.0,
        }

        default_reading = SensorReading(
            sensor_id=sensor_id,
            ph=region_ph_defaults.get(
                location_info.get("region", "Bhairahawa-Butwal"), 6.5
            ),
            temperature=base_temp + temp_adjustment,
            humidity=65.0 if current_hour < 12 else 55.0,  # Higher humidity in morning
            soil_temperature=base_temp
            + temp_adjustment
            - 2.0,  # Soil temp slightly lower
            location=location_info.get("farm_name", "Unknown Farm"),
            region=location_info.get("region", "Bhairahawa-Butwal"),
            status="default",
        )

        result = default_reading.to_dict()
        self._update_cache(sensor_id, result)
        return result

    def get_all_sensors_data(
        self,
    ) -> Dict[str, Dict[str, Union[float, int, str, None]]]:
        """Get data from all available IoT sensors with location info"""
        all_data = {}

        for sensor_id, location_info in self.sensor_locations.items():
            try:
                sensor_data = self.get_latest_sensor_data(sensor_id)
                if sensor_data:
                    # Merge sensor data with location info
                    combined_data = {**sensor_data, **location_info}
                    all_data[sensor_id] = combined_data

            except Exception as e:
                logger.error(f"❌ Error fetching data for {sensor_id}: {e}")
                # Still include the sensor with default data
                default_data = self._get_intelligent_default_data(sensor_id)
                all_data[sensor_id] = {**default_data, **location_info}

        return all_data

    def get_regional_average_data(
        self, region: str = "Bhairahawa-Butwal"
    ) -> Dict[str, Union[float, int, str]]:
        """Get regional average of all sensors with enhanced statistics"""
        all_data = self.get_all_sensors_data()
        region_sensors = [
            data for data in all_data.values() if data.get("region") == region
        ]

        if not region_sensors:
            logger.warning(f"⚠️ No sensors found for region: {region}")
            return self._get_regional_defaults(region)

        # Calculate comprehensive statistics
        ph_values = []
        temp_values = []
        soil_temp_values = []
        humidity_values = []
        active_sensors = 0

        for sensor in region_sensors:
            if sensor.get("status") in ["active", "default"]:
                active_sensors += 1

            # Safely extract and validate values
            for value_list, key in [
                (ph_values, "ph"),
                (temp_values, "temperature"),
                (soil_temp_values, "soil_temperature"),
                (humidity_values, "humidity"),
            ]:
                val = sensor.get(key)
                if val is not None:
                    try:
                        value_list.append(float(val))
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Invalid {key} value: {val}")

        # Calculate averages with fallbacks
        result = {
            "ph": round(sum(ph_values) / len(ph_values) if ph_values else 6.5, 2),
            "temperature": round(
                sum(temp_values) / len(temp_values) if temp_values else 29.6, 1
            ),
            "soil_temperature": round(
                (
                    sum(soil_temp_values) / len(soil_temp_values)
                    if soil_temp_values
                    else 25.0
                ),
                1,
            ),
            "humidity": round(
                (
                    sum(humidity_values) / len(humidity_values)
                    if humidity_values
                    else 60.0
                ),
                1,
            ),
            "sensor_count": len(region_sensors),
            "active_sensors": active_sensors,
            "region": region,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"📊 Regional averages for {region}: {result}")
        return result

    def _get_regional_defaults(self, region: str) -> Dict[str, Union[float, int, str]]:
        """Get default values for a region when no sensors are available"""
        regional_defaults = {
            "Bhairahawa-Butwal": {
                "ph": 6.8,
                "temperature": 29.5,
                "soil_temperature": 26.0,
                "humidity": 65.0,
            },
            "Kathmandu": {
                "ph": 6.5,
                "temperature": 22.0,
                "soil_temperature": 20.0,
                "humidity": 70.0,
            },
            "Pokhara": {
                "ph": 7.0,
                "temperature": 25.0,
                "soil_temperature": 23.0,
                "humidity": 75.0,
            },
        }

        defaults = regional_defaults.get(region, regional_defaults["Bhairahawa-Butwal"])
        return {
            **defaults,
            "sensor_count": 0,
            "active_sensors": 0,
            "region": region,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "status": "no_sensors",
        }

    def store_sensor_reading(
        self, sensor_id: str, reading: Union[SensorReading, Dict[str, Any]]
    ) -> bool:
        """Store sensor reading to Firebase with validation"""
        try:
            if isinstance(reading, dict):
                reading = SensorReading(**reading)

            if not reading.is_valid():
                logger.error(f"❌ Invalid sensor reading for {sensor_id}: {reading}")
                return False

            timestamp = datetime.now(timezone.utc).isoformat()
            data = reading.to_dict()

            # Store in Realtime Database
            if self.db_ref:
                ref = self.db_ref.child(f"iot_sensors/{sensor_id}")
                ref.update(
                    {
                        "latest": data,
                        "timestamp": timestamp,
                        "history": {int(datetime.now().timestamp()): data},
                    }
                )
                logger.info(
                    f"✅ Stored reading in Firebase Realtime DB for {sensor_id}"
                )

            # Store in Firestore if available
            if self.firestore_client:
                doc_ref = self.firestore_client.collection("sensor_readings").document(
                    sensor_id
                )
                doc_ref.set(
                    {**data, "updated_at": datetime.now(timezone.utc)}, merge=True
                )
                logger.info(f"✅ Stored reading in Firestore for {sensor_id}")

            # Update cache
            self._update_cache(sensor_id, data)

            return True

        except Exception as e:
            logger.error(f"❌ Error storing sensor reading for {sensor_id}: {e}")
            return False

    def get_sensor_history(
        self, sensor_id: str, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get historical sensor data for the specified time period"""
        try:
            if not self.db_ref:
                return []

            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            start_timestamp = int(start_time.timestamp())

            history_ref = self.db_ref.child(f"iot_sensors/{sensor_id}/history")
            history_data = (
                history_ref.order_by_key().start_at(str(start_timestamp)).get()
            )

            if not history_data:
                return []

            # Convert to list of readings
            readings = []
            if isinstance(history_data, dict):
                for timestamp, data in history_data.items():
                    if isinstance(data, dict):
                        data["timestamp"] = timestamp
                        readings.append(data)
            elif isinstance(history_data, list):
                # Handle list format
                for i, data in enumerate(history_data):
                    if isinstance(data, dict):
                        data["timestamp"] = str(int(start_time.timestamp()) + i)
                        readings.append(data)

            # Sort by timestamp (most recent first)
            readings.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return readings[:100]  # Limit to 100 most recent readings

        except Exception as e:
            logger.error(f"❌ Error fetching history for {sensor_id}: {e}")
            return []

    def get_sensor_health_status(self, sensor_id: str) -> Dict[str, Any]:
        """Get health status and diagnostics for a sensor"""
        try:
            latest_data = self.get_latest_sensor_data(sensor_id, use_cache=False)

            # Check if sensor is responding
            if latest_data.get("status") == "default":
                return {
                    "sensor_id": sensor_id,
                    "status": "offline",
                    "health": "poor",
                    "last_seen": "unknown",
                    "issues": ["No data received", "Using default values"],
                }

            # Check data freshness
            timestamp = latest_data.get("timestamp")
            issues = []

            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        last_reading = datetime.fromisoformat(
                            timestamp.replace("Z", "+00:00")
                        )
                        time_diff = (
                            datetime.now(timezone.utc) - last_reading
                        ).total_seconds()

                        if time_diff > 3600:  # More than 1 hour old
                            issues.append(f"Data is {int(time_diff/3600)} hours old")
                        elif time_diff > 1800:  # More than 30 minutes old
                            issues.append(f"Data is {int(time_diff/60)} minutes old")
                    else:
                        issues.append("Timestamp format is not a string")

                except Exception:
                    issues.append("Invalid timestamp format")
            else:
                issues.append("No timestamp available")

            # Check sensor value ranges
            ph = latest_data.get("ph", 0)
            temp = latest_data.get("temperature", 0)

            try:
                ph_val = float(ph) if ph is not None else 0.0
                if ph_val < 4.0 or ph_val > 9.0:
                    issues.append(f"pH value unusual: {ph_val}")
            except (ValueError, TypeError):
                issues.append(f"Invalid pH value: {ph}")

            try:
                temp_val = float(temp) if temp is not None else 0.0
                if temp_val < 10.0 or temp_val > 50.0:
                    issues.append(f"Temperature unusual: {temp_val}°C")
            except (ValueError, TypeError):
                issues.append(f"Invalid temperature value: {temp}")

            # Determine overall health
            if not issues:
                health = "excellent"
                status = "online"
            elif len(issues) == 1:
                health = "good"
                status = "online"
            elif len(issues) <= 2:
                health = "fair"
                status = "warning"
            else:
                health = "poor"
                status = "error"

            return {
                "sensor_id": sensor_id,
                "status": status,
                "health": health,
                "last_seen": timestamp or "unknown",
                "issues": issues,
                "data_quality": "valid" if not issues else "questionable",
            }

        except Exception as e:
            logger.error(f"❌ Error checking sensor health for {sensor_id}: {e}")
            return {
                "sensor_id": sensor_id,
                "status": "error",
                "health": "unknown",
                "last_seen": "unknown",
                "issues": [f"Health check failed: {str(e)}"],
            }

    def create_demo_data(self, sensors: Optional[List[str]] = None) -> bool:
        """Create realistic demo data for testing and demonstrations"""
        if sensors is None:
            sensors = list(self.sensor_locations.keys())

        try:
            import random

            for sensor_id in sensors:
                # Generate realistic demo data based on region and time
                location_info = self.sensor_locations.get(sensor_id, {})
                region = location_info.get("region", "Bhairahawa-Butwal")

                # Base values for different regions
                if region == "Bhairahawa-Butwal":
                    ph_range = (6.2, 7.2)
                    temp_range = (20.0, 35.0)
                    humidity_range = (55.0, 80.0)
                else:
                    ph_range = (6.0, 7.5)
                    temp_range = (15.0, 30.0)
                    humidity_range = (60.0, 85.0)

                demo_reading = SensorReading(
                    sensor_id=sensor_id,
                    ph=round(random.uniform(*ph_range), 1),
                    temperature=round(random.uniform(*temp_range), 1),
                    humidity=round(random.uniform(*humidity_range), 1),
                    soil_temperature=round(
                        random.uniform(temp_range[0] - 2, temp_range[1] - 2), 1
                    ),
                    location=location_info.get("farm_name", f"Farm {sensor_id}"),
                    region=region,
                )

                if self.store_sensor_reading(sensor_id, demo_reading):
                    logger.info(f"✅ Created demo data for {sensor_id}")
                else:
                    logger.error(f"❌ Failed to create demo data for {sensor_id}")

            return True

        except Exception as e:
            logger.error(f"❌ Error creating demo data: {e}")
            return False

    def get_realtime_sensor_data(
        self, sensor_id: str = "bhairahawa_farm_1"
    ) -> Dict[str, Union[float, int, str, None]]:
        """
        Get real-time IoT sensor data WITHOUT caching - always fetches fresh data
        This method bypasses the cache and directly queries Firebase for live updates
        """
        logger.info(f"🔴 REAL-TIME: Fetching live data for sensor: {sensor_id}")

        try:
            # Always fetch fresh data from Firebase - no cache
            sensor_data = self._fetch_from_realtime_db(sensor_id)

            if sensor_data:
                reading = self._parse_sensor_data(sensor_id, sensor_data)
                if reading and reading.is_valid():
                    result = reading.to_dict()
                    # Update cache but don't use it for this request
                    self._update_cache(sensor_id, result)
                    logger.info(f"✅ REAL-TIME: Fresh data retrieved for {sensor_id}")
                    return result

            # Fallback to Firestore if available
            if self.firestore_client:
                sensor_data = self._fetch_from_firestore(sensor_id)
                if sensor_data:
                    reading = self._parse_sensor_data(sensor_id, sensor_data)
                    if reading and reading.is_valid():
                        result = reading.to_dict()
                        self._update_cache(sensor_id, result)
                        logger.info(
                            f"✅ REAL-TIME: Fresh data from Firestore for {sensor_id}"
                        )
                        return result

            # If no valid data found, generate intelligent defaults
            logger.warning(
                f"⚠️ REAL-TIME: No live data found for {sensor_id}, using intelligent defaults"
            )
            return self._get_intelligent_default_data(sensor_id)

        except Exception as e:
            logger.error(f"❌ REAL-TIME: Error fetching live data for {sensor_id}: {e}")
            return self._get_intelligent_default_data(sensor_id)


# Global instance
enhanced_iot_service = EnhancedIoTService()
