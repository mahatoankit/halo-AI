#!/usr/bin/env python
"""
Script to create a test farmer user for dashboard testing
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from apps.users.models import CustomUser, FarmerProfile


def create_test_farmer():
    """Create a test farmer user"""
    # Check if test user already exists
    username = "testfarmer"
    if CustomUser.objects.filter(username=username).exists():
        print(f"✅ Test farmer user '{username}' already exists")
        user = CustomUser.objects.get(username=username)
    else:
        # Create test farmer user
        user = CustomUser.objects.create_user(
            username=username,
            email="testfarmer@example.com",
            password="testpass123",
            first_name="John",
            last_name="Farmer",
            role="farmer",
            phone="+1234567890",
            is_approved=True,
            is_active=True,
        )
        print(f"✅ Created test farmer user: {username}")

    # Create farmer profile if it doesn't exist
    farmer_profile, created = FarmerProfile.objects.get_or_create(
        user=user,
        defaults={
            "farm_size": 25.5,
            "crop_types": "Rice, Wheat, Corn",
            "farming_experience_years": 10,
            "primary_market": "Local Market",
            "annual_income_range": "50000-100000",
            "education_level": "high_school",
            "technology_adoption_level": "medium",
            "primary_challenges": "Weather prediction, Pest control, Market access",
        },
    )

    if created:
        print(f"✅ Created farmer profile for {username}")
    else:
        print(f"✅ Farmer profile for {username} already exists")

    print(f"\n🚀 You can now login with:")
    print(f"   Username: {username}")
    print(f"   Password: testpass123")
    print(f"   Dashboard: http://127.0.0.1:8000/dashboard/farmer/")


if __name__ == "__main__":
    create_test_farmer()
