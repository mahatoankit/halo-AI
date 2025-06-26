"""
Firestore User Service for storing extended user profile data
Complements Django's built-in authentication system
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from firebase_admin import firestore
import firebase_admin
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class FirestoreUserService:
    """Service for managing user profile data in Firestore"""

    def __init__(self):
        self.db = None
        self.initialize_firestore()

    def initialize_firestore(self):
        """Initialize Firestore client"""
        try:
            if firebase_admin._apps:
                self.db = firestore.client()
                logger.info("✅ Firestore User Service initialized")
            else:
                logger.error("❌ Firebase not initialized")
                self.db = None
        except Exception as e:
            logger.error(f"❌ Firestore initialization failed: {e}")
            self.db = None

    def is_available(self) -> bool:
        """Check if Firestore is available"""
        return self.db is not None

    def create_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """
        Create user profile in Firestore

        Args:
            user_id: Django user ID
            profile_data: Dictionary containing profile information

        Returns:
            bool: Success status
        """
        if not self.is_available():
            logger.warning("Firestore not available, skipping profile creation")
            return False

        try:
            # Prepare profile data
            firestore_data = {
                "django_user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                **profile_data,
            }

            # Store in Firestore with user_id as document ID
            doc_ref = self.db.collection("user_profiles").document(str(user_id))
            doc_ref.set(firestore_data)

            logger.info(f"✅ Created Firestore profile for user {user_id}")
            return True

        except Exception as e:
            logger.error(
                f"❌ Failed to create Firestore profile for user {user_id}: {e}"
            )
            return False

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user profile from Firestore

        Args:
            user_id: Django user ID

        Returns:
            Dict containing profile data or None
        """
        if not self.is_available():
            return None

        try:
            doc_ref = self.db.collection("user_profiles").document(str(user_id))
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()
            else:
                logger.info(f"No Firestore profile found for user {user_id}")
                return None

        except Exception as e:
            logger.error(f"❌ Failed to get Firestore profile for user {user_id}: {e}")
            return None

    def update_user_profile(self, user_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update user profile in Firestore

        Args:
            user_id: Django user ID
            update_data: Dictionary containing fields to update

        Returns:
            bool: Success status
        """
        if not self.is_available():
            return False

        try:
            # Add timestamp
            update_data["updated_at"] = datetime.now(timezone.utc)

            doc_ref = self.db.collection("user_profiles").document(str(user_id))
            doc_ref.update(update_data)

            logger.info(f"✅ Updated Firestore profile for user {user_id}")
            return True

        except Exception as e:
            logger.error(
                f"❌ Failed to update Firestore profile for user {user_id}: {e}"
            )
            return False

    def delete_user_profile(self, user_id: int) -> bool:
        """
        Delete user profile from Firestore

        Args:
            user_id: Django user ID

        Returns:
            bool: Success status
        """
        if not self.is_available():
            return False

        try:
            doc_ref = self.db.collection("user_profiles").document(str(user_id))
            doc_ref.delete()

            logger.info(f"✅ Deleted Firestore profile for user {user_id}")
            return True

        except Exception as e:
            logger.error(
                f"❌ Failed to delete Firestore profile for user {user_id}: {e}"
            )
            return False

    def get_users_by_region(self, region: str) -> List[Dict[str, Any]]:
        """
        Get users by assigned region (for community admins)

        Args:
            region: Region name

        Returns:
            List of user profiles
        """
        if not self.is_available():
            return []

        try:
            docs = (
                self.db.collection("user_profiles")
                .where("assigned_region", "==", region)
                .stream()
            )

            profiles = []
            for doc in docs:
                profile = doc.to_dict()
                profile["firestore_id"] = doc.id
                profiles.append(profile)

            return profiles

        except Exception as e:
            logger.error(f"❌ Failed to get users by region {region}: {e}")
            return []

    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        Get users by role

        Args:
            role: User role (admin, community_admin, farmer)

        Returns:
            List of user profiles
        """
        if not self.is_available():
            return []

        try:
            docs = (
                self.db.collection("user_profiles").where("role", "==", role).stream()
            )

            profiles = []
            for doc in docs:
                profile = doc.to_dict()
                profile["firestore_id"] = doc.id
                profiles.append(profile)

            return profiles

        except Exception as e:
            logger.error(f"❌ Failed to get users by role {role}: {e}")
            return []

    def search_users(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search users with multiple criteria

        Args:
            search_params: Dictionary of search parameters

        Returns:
            List of matching user profiles
        """
        if not self.is_available():
            return []

        try:
            query = self.db.collection("user_profiles")

            # Apply filters
            for field, value in search_params.items():
                if value is not None:
                    query = query.where(field, "==", value)

            docs = query.stream()

            profiles = []
            for doc in docs:
                profile = doc.to_dict()
                profile["firestore_id"] = doc.id
                profiles.append(profile)

            return profiles

        except Exception as e:
            logger.error(f"❌ Failed to search users: {e}")
            return []

    def get_community_stats(self, region: str) -> Dict[str, Any]:
        """
        Get community statistics for a region

        Args:
            region: Region name

        Returns:
            Dictionary with community statistics
        """
        if not self.is_available():
            return {}

        try:
            # Get all users in region
            users = self.get_users_by_region(region)

            # Calculate stats
            stats = {
                "total_users": len(users),
                "farmers": len([u for u in users if u.get("role") == "farmer"]),
                "community_admins": len(
                    [u for u in users if u.get("role") == "community_admin"]
                ),
                "active_users": len([u for u in users if u.get("is_active", True)]),
                "region": region,
                "last_updated": datetime.now(timezone.utc),
            }

            return stats

        except Exception as e:
            logger.error(f"❌ Failed to get community stats for {region}: {e}")
            return {}


# Global instance
firestore_user_service = FirestoreUserService()
