"""
Firestore IoT Service for managing IoT sensor components and their mapping to community admins
Provides relational database functionality using Firestore collections
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from firebase_admin import firestore
import firebase_admin
from django.contrib.auth import get_user_model
import logging
import uuid

logger = logging.getLogger(__name__)

User = get_user_model()


class FirestoreIoTService:
    """Service for managing IoT sensor data and relationships in Firestore"""

    def __init__(self):
        self.db = None
        self.initialize_firestore()

    def initialize_firestore(self):
        """Initialize Firestore client"""
        try:
            if firebase_admin._apps:
                self.db = firestore.client()
                logger.info("✅ Firestore IoT Service initialized")
            else:
                logger.error("❌ Firebase not initialized")
                self.db = None
        except Exception as e:
            logger.error(f"❌ Firestore IoT initialization failed: {e}")
            self.db = None

    def is_available(self) -> bool:
        """Check if Firestore is available"""
        return self.db is not None

    # =========================================================================
    # IoT Sensor Set Management
    # =========================================================================

    def create_iot_sensor_set(self, sensor_set_data: Dict[str, Any]) -> Optional[str]:
        """
        Create IoT sensor set in Firestore with relational mapping to community admin

        Args:
            sensor_set_data: Dictionary containing sensor set information
                Required fields:
                - community_admin_id: Django user ID of community admin
                - name: Sensor set name
                - location_name: Human readable location
                - region: Assigned region

        Returns:
            str: Document ID of created sensor set or None
        """
        if not self.is_available():
            logger.warning("Firestore not available, skipping sensor set creation")
            return None

        try:
            # Generate unique ID for sensor set
            sensor_set_id = str(uuid.uuid4())

            # Prepare sensor set data
            firestore_data = {
                "sensor_set_id": sensor_set_id,
                "community_admin_id": sensor_set_data["community_admin_id"],
                "name": sensor_set_data["name"],
                "location_name": sensor_set_data["location_name"],
                "latitude": sensor_set_data.get("latitude"),
                "longitude": sensor_set_data.get("longitude"),
                "region": sensor_set_data["region"],
                "status": sensor_set_data.get("status", "active"),
                "firebase_path": f"sensors/{sensor_set_data['region']}/{sensor_set_id}",
                # Default NPK values
                "default_nitrogen": sensor_set_data.get("default_nitrogen", 85.0),
                "default_phosphorus": sensor_set_data.get("default_phosphorus", 50.0),
                "default_potassium": sensor_set_data.get("default_potassium", 40.0),
                # Timestamps
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

            # Create sensor set document
            self.db.collection("iot_sensor_sets").document(sensor_set_id).set(
                firestore_data
            )

            # Create relational mapping
            self._create_admin_sensor_mapping(
                sensor_set_data["community_admin_id"], sensor_set_id
            )

            logger.info(
                f"✅ Created IoT sensor set {sensor_set_id} for admin {sensor_set_data['community_admin_id']}"
            )
            return sensor_set_id

        except Exception as e:
            logger.error(f"❌ Failed to create IoT sensor set: {e}")
            return None

    def get_sensor_sets_by_admin(self, community_admin_id: int) -> List[Dict[str, Any]]:
        """
        Get all sensor sets managed by a specific community admin

        Args:
            community_admin_id: Django user ID of community admin

        Returns:
            List of sensor set documents
        """
        if not self.is_available():
            return []

        try:
            # Query sensor sets by community admin
            query = (
                self.db.collection("iot_sensor_sets")
                .where("community_admin_id", "==", community_admin_id)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
            )

            docs = query.stream()
            sensor_sets = [doc.to_dict() for doc in docs]

            logger.info(
                f"📡 Retrieved {len(sensor_sets)} sensor sets for admin {community_admin_id}"
            )
            return sensor_sets

        except Exception as e:
            logger.error(
                f"❌ Failed to get sensor sets for admin {community_admin_id}: {e}"
            )
            return []

    def get_sensor_set_details(self, sensor_set_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific sensor set

        Args:
            sensor_set_id: Unique sensor set identifier

        Returns:
            Dict containing sensor set details or None
        """
        if not self.is_available():
            return None

        try:
            doc = self.db.collection("iot_sensor_sets").document(sensor_set_id).get()

            if doc.exists:
                return doc.to_dict()
            else:
                logger.info(f"Sensor set {sensor_set_id} not found")
                return None

        except Exception as e:
            logger.error(f"❌ Failed to get sensor set {sensor_set_id}: {e}")
            return None

    # =========================================================================
    # IoT Component Management
    # =========================================================================

    def add_iot_component(
        self, sensor_set_id: str, component_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Add individual IoT component to a sensor set

        Args:
            sensor_set_id: Parent sensor set ID
            component_data: Component information (type, model, specs, etc.)

        Returns:
            str: Component ID or None
        """
        if not self.is_available():
            return None

        try:
            component_id = str(uuid.uuid4())

            component_doc = {
                "component_id": component_id,
                "sensor_set_id": sensor_set_id,
                "component_type": component_data[
                    "component_type"
                ],  # e.g., "soil_sensor", "temperature_sensor"
                "model": component_data.get("model", ""),
                "manufacturer": component_data.get("manufacturer", ""),
                "specifications": component_data.get("specifications", {}),
                "status": component_data.get("status", "active"),
                "last_reading": None,
                "last_reading_timestamp": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

            # Store component
            self.db.collection("iot_components").document(component_id).set(
                component_doc
            )

            # Update parent sensor set with component reference
            self.db.collection("iot_sensor_sets").document(sensor_set_id).update(
                {
                    "components": firestore.ArrayUnion([component_id]),
                    "updated_at": datetime.now(timezone.utc),
                }
            )

            logger.info(
                f"✅ Added IoT component {component_id} to sensor set {sensor_set_id}"
            )
            return component_id

        except Exception as e:
            logger.error(f"❌ Failed to add IoT component: {e}")
            return None

    def get_components_by_sensor_set(self, sensor_set_id: str) -> List[Dict[str, Any]]:
        """
        Get all IoT components for a specific sensor set

        Args:
            sensor_set_id: Sensor set identifier

        Returns:
            List of component documents
        """
        if not self.is_available():
            return []

        try:
            query = (
                self.db.collection("iot_components")
                .where("sensor_set_id", "==", sensor_set_id)
                .order_by("created_at")
            )

            docs = query.stream()
            components = [doc.to_dict() for doc in docs]

            logger.info(
                f"🔧 Retrieved {len(components)} components for sensor set {sensor_set_id}"
            )
            return components

        except Exception as e:
            logger.error(
                f"❌ Failed to get components for sensor set {sensor_set_id}: {e}"
            )
            return []

    # =========================================================================
    # Sensor Readings Management
    # =========================================================================

    def store_sensor_reading(
        self, component_id: str, reading_data: Dict[str, Any]
    ) -> bool:
        """
        Store sensor reading data

        Args:
            component_id: IoT component identifier
            reading_data: Sensor reading information

        Returns:
            bool: Success status
        """
        if not self.is_available():
            return False

        try:
            reading_id = str(uuid.uuid4())

            reading_doc = {
                "reading_id": reading_id,
                "component_id": component_id,
                "sensor_type": reading_data["sensor_type"],
                "value": reading_data["value"],
                "unit": reading_data.get("unit", ""),
                "quality_score": reading_data.get("quality_score", 1.0),
                "timestamp": datetime.now(timezone.utc),
                "firebase_timestamp": reading_data.get("firebase_timestamp"),
                "metadata": reading_data.get("metadata", {}),
            }

            # Store reading
            self.db.collection("sensor_readings").document(reading_id).set(reading_doc)

            # Update component with latest reading
            self.db.collection("iot_components").document(component_id).update(
                {
                    "last_reading": reading_data["value"],
                    "last_reading_timestamp": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to store sensor reading: {e}")
            return False

    def get_recent_readings(
        self, component_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent sensor readings for a component

        Args:
            component_id: IoT component identifier
            limit: Maximum number of readings to return

        Returns:
            List of reading documents
        """
        if not self.is_available():
            return []

        try:
            query = (
                self.db.collection("sensor_readings")
                .where("component_id", "==", component_id)
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
            )

            docs = query.stream()
            readings = [doc.to_dict() for doc in docs]

            return readings

        except Exception as e:
            logger.error(f"❌ Failed to get readings for component {component_id}: {e}")
            return []

    # =========================================================================
    # Relational Mapping Management
    # =========================================================================

    def _create_admin_sensor_mapping(self, community_admin_id: int, sensor_set_id: str):
        """Create bidirectional mapping between admin and sensor set"""
        try:
            mapping_doc = {
                "community_admin_id": community_admin_id,
                "sensor_set_id": sensor_set_id,
                "relationship_type": "manages",
                "created_at": datetime.now(timezone.utc),
            }

            # Create mapping document
            mapping_id = f"{community_admin_id}_{sensor_set_id}"
            self.db.collection("admin_sensor_mappings").document(mapping_id).set(
                mapping_doc
            )

        except Exception as e:
            logger.error(f"❌ Failed to create admin-sensor mapping: {e}")

    def get_admin_dashboard_data(self, community_admin_id: int) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a community admin

        Args:
            community_admin_id: Django user ID of community admin

        Returns:
            Dict containing dashboard statistics and data
        """
        if not self.is_available():
            return {}

        try:
            # Get sensor sets
            sensor_sets = self.get_sensor_sets_by_admin(community_admin_id)

            # Calculate statistics
            total_sensor_sets = len(sensor_sets)
            active_sensor_sets = len(
                [s for s in sensor_sets if s.get("status") == "active"]
            )

            # Get total components
            total_components = 0
            for sensor_set in sensor_sets:
                components = self.get_components_by_sensor_set(
                    sensor_set["sensor_set_id"]
                )
                total_components += len(components)

            dashboard_data = {
                "total_sensor_sets": total_sensor_sets,
                "active_sensor_sets": active_sensor_sets,
                "total_components": total_components,
                "sensor_sets": sensor_sets,
                "regions_covered": list(
                    set([s.get("region") for s in sensor_sets if s.get("region")])
                ),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"❌ Failed to get admin dashboard data: {e}")
            return {}

    # =========================================================================
    # Regional Analytics
    # =========================================================================

    def get_regional_sensor_overview(self, region: str) -> Dict[str, Any]:
        """
        Get overview of all sensor sets in a specific region

        Args:
            region: Region name

        Returns:
            Dict containing regional sensor statistics
        """
        if not self.is_available():
            return {}

        try:
            query = self.db.collection("iot_sensor_sets").where("region", "==", region)

            docs = query.stream()
            sensor_sets = [doc.to_dict() for doc in docs]

            regional_data = {
                "region": region,
                "total_sensor_sets": len(sensor_sets),
                "active_sensor_sets": len(
                    [s for s in sensor_sets if s.get("status") == "active"]
                ),
                "community_admins": list(
                    set([s.get("community_admin_id") for s in sensor_sets])
                ),
                "sensor_sets": sensor_sets,
            }

            return regional_data

        except Exception as e:
            logger.error(f"❌ Failed to get regional overview for {region}: {e}")
            return {}


# Global instance
firestore_iot_service = FirestoreIoTService()
