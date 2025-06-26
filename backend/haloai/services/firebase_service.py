"""
Firebase Service for IoT Sensor Data Management
Handles real-time sensor data for agricultural monitoring
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from firebase_admin import db
import firebase_admin


class FirebaseIoTService:
    """Service class to handle IoT sensor data in Firebase Realtime Database"""

    def __init__(self):
        self.db_ref = None
        self.initialize_firebase()

    def initialize_firebase(self):
        """Initialize Firebase database reference"""
        try:
            if firebase_admin._apps:
                self.db_ref = db.reference()
                print("✅ Firebase service initialized successfully")
                self._test_connection()
            else:
                raise Exception("Firebase not initialized in Django settings")
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            print("📖 Please check your Firebase configuration in .env file")
            raise e

    def _test_connection(self):
        """Test Firebase connection"""
        try:
            if self.db_ref:
                test_ref = self.db_ref.child("_connection_test")
                test_ref.set({"timestamp": datetime.now(timezone.utc).isoformat()})
                print("✅ Firebase connection test passed")
        except Exception as e:
            print(f"⚠️ Firebase connection test failed: {e}")
            raise e

    def store_sensor_data(
        self, farm_id: str, sensor_type: str, data: Dict[str, Any]
    ) -> bool:
        """Store sensor data in Firebase"""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            sensor_data = {
                "timestamp": timestamp,
                "farm_id": farm_id,
                "sensor_type": sensor_type,
                "data": data,
                "created_at": timestamp,
            }

            # Store in sensors/{farm_id}/{sensor_type}/latest
            latest_ref = self.db_ref.child(f"sensors/{farm_id}/{sensor_type}/latest")
            latest_ref.set(sensor_data)

            # Store in sensors/{farm_id}/{sensor_type}/history with timestamp key
            history_ref = self.db_ref.child(
                f"sensors/{farm_id}/{sensor_type}/history/{timestamp}"
            )
            history_ref.set(sensor_data)

            return True

        except Exception as e:
            print(f"Error storing sensor data: {e}")
            return False

    def get_latest_sensor_data(
        self, farm_id: str, sensor_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get latest sensor data from Firebase"""
        try:
            if sensor_type:
                latest_ref = self.db_ref.child(
                    f"sensors/{farm_id}/{sensor_type}/latest"
                )
                return latest_ref.get()
            else:
                # Get all latest sensor data for farm
                farm_ref = self.db_ref.child(f"sensors/{farm_id}")
                farm_data = farm_ref.get()
                if farm_data:
                    latest_data = {}
                    for sensor, sensor_data in farm_data.items():
                        if "latest" in sensor_data:
                            latest_data[sensor] = sensor_data["latest"]
                    return latest_data
                return None

        except Exception as e:
            print(f"Error getting latest sensor data: {e}")
            return None

    def get_sensor_history(
        self,
        farm_id: str,
        sensor_type: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get historical sensor data from Firebase"""
        try:
            history_ref = self.db_ref.child(f"sensors/{farm_id}/{sensor_type}/history")

            query = history_ref.order_by_key()
            if start_time:
                query = query.start_at(start_time)
            if end_time:
                query = query.end_at(end_time)

            query = query.limit_to_last(limit)
            history_data = query.get()

            if history_data:
                return list(history_data.values())
            return []

        except Exception as e:
            print(f"Error getting sensor history: {e}")
            return []

    def store_weather_data(self, location: str, data: Dict[str, Any]) -> bool:
        """Store weather data in Firebase"""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            weather_data = {
                "timestamp": timestamp,
                "location": location,
                "data": data,
                "created_at": timestamp,
            }

            # Store latest weather data
            latest_ref = self.db_ref.child(f"weather/{location}/latest")
            latest_ref.set(weather_data)

            # Store historical weather data
            history_ref = self.db_ref.child(f"weather/{location}/history/{timestamp}")
            history_ref.set(weather_data)

            return True

        except Exception as e:
            print(f"Error storing weather data: {e}")
            return False

    def get_latest_weather_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Get latest weather data from Firebase"""
        try:
            latest_ref = self.db_ref.child(f"weather/{location}/latest")
            return latest_ref.get()

        except Exception as e:
            print(f"Error getting weather data: {e}")
            return None

    def store_prediction_data(
        self, farm_id: str, prediction_type: str, data: Dict[str, Any]
    ) -> bool:
        """Store ML prediction data in Firebase"""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            prediction_data = {
                "timestamp": timestamp,
                "farm_id": farm_id,
                "prediction_type": prediction_type,
                "data": data,
                "created_at": timestamp,
            }

            # Store latest prediction
            latest_ref = self.db_ref.child(
                f"predictions/{farm_id}/{prediction_type}/latest"
            )
            latest_ref.set(prediction_data)

            # Store prediction history
            history_ref = self.db_ref.child(
                f"predictions/{farm_id}/{prediction_type}/history/{timestamp}"
            )
            history_ref.set(prediction_data)

            return True

        except Exception as e:
            print(f"Error storing prediction data: {e}")
            return False

    def get_latest_prediction_data(
        self, farm_id: str, prediction_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get latest prediction data from Firebase"""
        try:
            latest_ref = self.db_ref.child(
                f"predictions/{farm_id}/{prediction_type}/latest"
            )
            return latest_ref.get()

        except Exception as e:
            print(f"Error getting prediction data: {e}")
            return None

    def get_farm_summary(self, farm_id: str) -> Dict[str, Any]:
        """Get comprehensive farm data summary from Firebase"""
        try:
            summary = {
                "sensors": {},
                "predictions": {},
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

            # Get all sensor data
            sensors_ref = self.db_ref.child(f"sensors/{farm_id}")
            sensors_data = sensors_ref.get()
            if sensors_data:
                for sensor_type, sensor_info in sensors_data.items():
                    if "latest" in sensor_info:
                        summary["sensors"][sensor_type] = sensor_info["latest"]

            # Get all prediction data
            predictions_ref = self.db_ref.child(f"predictions/{farm_id}")
            predictions_data = predictions_ref.get()
            if predictions_data:
                for pred_type, pred_info in predictions_data.items():
                    if "latest" in pred_info:
                        summary["predictions"][pred_type] = pred_info["latest"]

            return summary

        except Exception as e:
            print(f"Error getting farm summary: {e}")
            return {
                "sensors": {},
                "predictions": {},
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
            }

    def delete_farm_data(self, farm_id: str) -> bool:
        """Delete all data for a specific farm"""
        try:
            # Delete sensor data
            sensors_ref = self.db_ref.child(f"sensors/{farm_id}")
            sensors_ref.delete()

            # Delete prediction data
            predictions_ref = self.db_ref.child(f"predictions/{farm_id}")
            predictions_ref.delete()

            print(f"✅ Deleted all data for farm: {farm_id}")
            return True

        except Exception as e:
            print(f"Error deleting farm data: {e}")
            return False

    def get_all_farms(self) -> List[str]:
        """Get list of all farm IDs with data"""
        try:
            farms = set()

            # Get farms from sensors
            sensors_ref = self.db_ref.child("sensors")
            sensors_data = sensors_ref.get()
            if sensors_data:
                farms.update(sensors_data.keys())

            # Get farms from predictions
            predictions_ref = self.db_ref.child("predictions")
            predictions_data = predictions_ref.get()
            if predictions_data:
                farms.update(predictions_data.keys())

            return list(farms)

        except Exception as e:
            print(f"Error getting farms list: {e}")
            return []

    def get_farm_analytics(self, farm_id: str) -> Dict[str, Any]:
        """Get farm analytics data (alias for get_farm_summary)"""
        return self.get_farm_summary(farm_id)

    def get_weather_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Get weather data (alias for get_latest_weather_data)"""
        return self.get_latest_weather_data(location)


# Global instance for backward compatibility
firebase_iot_service = FirebaseIoTService()


def get_farm_sensor_data(farm_id: str) -> Dict[str, Any]:
    """Helper function to get farm sensor data"""
    return firebase_iot_service.get_farm_summary(farm_id)
