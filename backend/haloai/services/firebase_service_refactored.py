"""
Refactored Firebase Service for IoT Sensor Data Management
Enhanced with Firestore support for community admin role-based access control
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from firebase_admin import db, firestore
import firebase_admin


class RefactoredFirebaseService:
    """Enhanced Firebase service with Firestore support for community admin management"""

    def __init__(self):
        self.db_ref = None
        self.firestore_client = None
        self.initialize_firebase()

    def initialize_firebase(self):
        """Initialize Firebase with both Realtime Database and Firestore"""
        try:
            if firebase_admin._apps:
                # Initialize Realtime Database
                self.db_ref = db.reference()

                # Initialize Firestore with error handling
                try:
                    self.firestore_client = firestore.client()
                    print("✅ Firebase and Firestore initialized successfully")
                except Exception as fs_error:
                    print(f"⚠️  Firestore initialization failed: {fs_error}")
                    print("🔄 Continuing with Realtime Database only")
                    self.firestore_client = None

                self._test_connection()
            else:
                raise Exception("Firebase not initialized in Django settings")
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            print("📖 Please check your Firebase configuration in .env file")
            # Don't raise - allow graceful degradation
            self.db_ref = None
            self.firestore_client = None

    def _test_connection(self):
        """Test Firebase connection"""
        try:
            if self.db_ref:
                test_ref = self.db_ref.child("_connection_test")
                test_ref.set({"timestamp": datetime.now(timezone.utc).isoformat()})
                print("✅ Firebase Realtime Database connection test passed")
        except Exception as e:
            print(f"⚠️ Firebase connection test failed: {e}")

    # ==== REGION-BASED SENSOR DATA MANAGEMENT ====

    def store_sensor_reading(
        self,
        community_admin_id: str,
        sensor_set_id: str,
        sensor_type: str,
        value: float,
        unit: str = "",
    ) -> bool:
        """Store sensor reading with community admin association"""
        try:
            if not self.db_ref:
                return False

            timestamp = datetime.now(timezone.utc).isoformat()

            # Store in Realtime Database for real-time access
            sensor_data = {
                "community_admin_id": community_admin_id,
                "sensor_set_id": sensor_set_id,
                "sensor_type": sensor_type,
                "value": value,
                "unit": unit,
                "timestamp": timestamp,
            }

            # Path structure: sensors/{community_admin_id}/{sensor_set_id}/{sensor_type}
            latest_ref = self.db_ref.child(
                f"sensors/{community_admin_id}/{sensor_set_id}/{sensor_type}/latest"
            )
            latest_ref.set(sensor_data)

            # Store historical data
            history_ref = self.db_ref.child(
                f"sensors/{community_admin_id}/{sensor_set_id}/{sensor_type}/history/{timestamp}"
            )
            history_ref.set(sensor_data)

            # Store metadata in Firestore if available
            if self.firestore_client:
                self._store_sensor_metadata(
                    community_admin_id, sensor_set_id, sensor_type, sensor_data
                )

            return True

        except Exception as e:
            print(f"Error storing sensor reading: {e}")
            return False

    def get_admin_sensor_data(
        self, community_admin_id: str, sensor_set_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get sensor data for a specific community admin"""
        try:
            if not self.db_ref:
                return {}

            if sensor_set_id:
                # Get specific sensor set data
                sensor_ref = self.db_ref.child(
                    f"sensors/{community_admin_id}/{sensor_set_id}"
                )
                return sensor_ref.get() or {}
            else:
                # Get all sensor data for the admin
                admin_ref = self.db_ref.child(f"sensors/{community_admin_id}")
                return admin_ref.get() or {}

        except Exception as e:
            print(f"Error getting admin sensor data: {e}")
            return {}

    def get_latest_sensor_readings(
        self, community_admin_id: str, sensor_set_id: str
    ) -> Dict[str, Any]:
        """Get latest readings for all sensor types in a sensor set"""
        try:
            if not self.db_ref:
                return {}

            readings = {}
            sensor_set_ref = self.db_ref.child(
                f"sensors/{community_admin_id}/{sensor_set_id}"
            )
            sensor_data = sensor_set_ref.get()

            if sensor_data:
                for sensor_type, data in sensor_data.items():
                    if "latest" in data:
                        readings[sensor_type] = data["latest"]

            return readings

        except Exception as e:
            print(f"Error getting latest sensor readings: {e}")
            return {}

    # ==== CROP PREDICTION DATA MANAGEMENT ====

    def store_prediction_request(
        self,
        prediction_id: str,
        community_admin_id: str,
        sensor_set_id: str,
        input_params: Dict[str, Any],
    ) -> bool:
        """Store crop prediction request"""
        try:
            if not self.db_ref:
                return False

            timestamp = datetime.now(timezone.utc).isoformat()

            prediction_data = {
                "prediction_id": prediction_id,
                "community_admin_id": community_admin_id,
                "sensor_set_id": sensor_set_id,
                "input_parameters": input_params,
                "status": "processing",
                "requested_at": timestamp,
            }

            # Store in Realtime Database
            pred_ref = self.db_ref.child(
                f"predictions/{community_admin_id}/{prediction_id}"
            )
            pred_ref.set(prediction_data)

            # Store in Firestore if available
            if self.firestore_client:
                self._store_prediction_firestore(prediction_data)

            return True

        except Exception as e:
            print(f"Error storing prediction request: {e}")
            return False

    def update_prediction_result(
        self, prediction_id: str, community_admin_id: str, results: Dict[str, Any]
    ) -> bool:
        """Update prediction with results"""
        try:
            if not self.db_ref:
                return False

            timestamp = datetime.now(timezone.utc).isoformat()

            update_data = {
                "status": "completed",
                "processed_at": timestamp,
                "predicted_crops": results.get("predicted_crops", []),
                "confidence_score": results.get("confidence_score", 0.0),
                "model_version": results.get("model_version", "v1.0"),
            }

            # Update in Realtime Database
            pred_ref = self.db_ref.child(
                f"predictions/{community_admin_id}/{prediction_id}"
            )
            pred_ref.update(update_data)

            # Update in Firestore if available
            if self.firestore_client:
                self._update_prediction_firestore(prediction_id, update_data)

            return True

        except Exception as e:
            print(f"Error updating prediction result: {e}")
            return False

    def get_admin_predictions(
        self, community_admin_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent predictions for a community admin"""
        try:
            if not self.db_ref:
                return []

            predictions_ref = self.db_ref.child(f"predictions/{community_admin_id}")
            predictions_data = predictions_ref.get()

            if not predictions_data:
                return []

            # Convert to list and sort by timestamp
            predictions = []
            for pred_id, pred_data in predictions_data.items():
                pred_data["prediction_id"] = pred_id
                predictions.append(pred_data)

            # Sort by requested_at timestamp (most recent first)
            predictions.sort(key=lambda x: x.get("requested_at", ""), reverse=True)

            return predictions[:limit]

        except Exception as e:
            print(f"Error getting admin predictions: {e}")
            return []

    # ==== REGIONAL ANALYTICS ====

    def get_regional_summary(self, region: str) -> Dict[str, Any]:
        """Get aggregated data for a region"""
        try:
            summary = {
                "region": region,
                "total_sensors": 0,
                "active_sensors": 0,
                "total_predictions": 0,
                "recent_activity": [],
            }

            if self.firestore_client:
                # Use Firestore for efficient querying
                try:
                    # Count sensors by region
                    sensor_docs = list(
                        self.firestore_client.collection("sensor_metadata")
                        .where("region", "==", region)
                        .stream()
                    )
                    summary["total_sensors"] = len(sensor_docs)

                    # Count active sensors
                    active_sensors = [
                        doc
                        for doc in sensor_docs
                        if doc.to_dict().get("status") == "active"
                    ]
                    summary["active_sensors"] = len(active_sensors)

                    # Count predictions
                    prediction_docs = list(
                        self.firestore_client.collection("crop_predictions")
                        .where("region", "==", region)
                        .stream()
                    )
                    summary["total_predictions"] = len(prediction_docs)

                except Exception as fs_error:
                    print(
                        f"Firestore query failed, falling back to Realtime DB: {fs_error}"
                    )

            return summary

        except Exception as e:
            print(f"Error getting regional summary: {e}")
            return {
                "region": region,
                "total_sensors": 0,
                "active_sensors": 0,
                "total_predictions": 0,
            }

    # ==== PRIVATE FIRESTORE HELPER METHODS ====

    def _store_sensor_metadata(
        self,
        community_admin_id: str,
        sensor_set_id: str,
        sensor_type: str,
        sensor_data: Dict[str, Any],
    ):
        """Store sensor metadata in Firestore"""
        try:
            if not self.firestore_client:
                return

            doc_id = f"{sensor_set_id}_{sensor_type}"
            doc_ref = self.firestore_client.collection("sensor_metadata").document(
                doc_id
            )

            doc_ref.set(
                {
                    "community_admin_id": community_admin_id,
                    "sensor_set_id": sensor_set_id,
                    "sensor_type": sensor_type,
                    "last_reading": sensor_data.get("value"),
                    "last_updated": datetime.now(timezone.utc),
                    "status": "active",
                },
                merge=True,
            )

        except Exception as e:
            print(f"Error storing sensor metadata: {e}")

    def _store_prediction_firestore(self, prediction_data: Dict[str, Any]):
        """Store prediction in Firestore"""
        try:
            if not self.firestore_client:
                return

            doc_ref = self.firestore_client.collection("crop_predictions").document(
                prediction_data["prediction_id"]
            )
            doc_ref.set({**prediction_data, "created_at": datetime.now(timezone.utc)})

        except Exception as e:
            print(f"Error storing prediction in Firestore: {e}")

    def _update_prediction_firestore(
        self, prediction_id: str, update_data: Dict[str, Any]
    ):
        """Update prediction in Firestore"""
        try:
            if not self.firestore_client:
                return

            doc_ref = self.firestore_client.collection("crop_predictions").document(
                prediction_id
            )
            doc_ref.update({**update_data, "updated_at": datetime.now(timezone.utc)})

        except Exception as e:
            print(f"Error updating prediction in Firestore: {e}")

    # ==== DEMO DATA HELPERS FOR PITCH ====

    def create_demo_data(
        self, community_admin_id: str, region: str = "Bhairahawa-Butwal"
    ) -> bool:
        """Create demo sensor data for pitch presentations"""
        try:
            demo_sensors = [
                {
                    "id": "sensor_001",
                    "location": "Farm A - Wheat Field",
                    "type": "temperature",
                    "value": 25.5,
                    "unit": "°C",
                },
                {
                    "id": "sensor_001",
                    "location": "Farm A - Wheat Field",
                    "type": "humidity",
                    "value": 65.0,
                    "unit": "%",
                },
                {
                    "id": "sensor_001",
                    "location": "Farm A - Wheat Field",
                    "type": "ph",
                    "value": 6.8,
                    "unit": "pH",
                },
                {
                    "id": "sensor_002",
                    "location": "Farm B - Rice Field",
                    "type": "temperature",
                    "value": 28.2,
                    "unit": "°C",
                },
                {
                    "id": "sensor_002",
                    "location": "Farm B - Rice Field",
                    "type": "humidity",
                    "value": 78.0,
                    "unit": "%",
                },
                {
                    "id": "sensor_002",
                    "location": "Farm B - Rice Field",
                    "type": "ph",
                    "value": 7.2,
                    "unit": "pH",
                },
            ]

            for sensor in demo_sensors:
                self.store_sensor_reading(
                    community_admin_id,
                    sensor["id"],
                    sensor["type"],
                    sensor["value"],
                    sensor["unit"],
                )

            print(f"✅ Demo data created for community admin: {community_admin_id}")
            return True

        except Exception as e:
            print(f"Error creating demo data: {e}")
            return False


# Global instance
firebase_service = RefactoredFirebaseService()
