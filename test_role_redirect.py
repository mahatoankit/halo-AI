#!/usr/bin/env python3
"""
Test the role-based dashboard redirect functionality
"""

import os
import sys
import django

# Add the Django project to the path
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


def test_role_based_dashboard_redirect():
    """Test that users are redirected to the correct dashboard based on their role"""
    client = Client()

    # Create test users with different roles
    test_users = [
        {"username": "farmer_test", "role": "farmer", "email": "farmer@test.com"},
        {"username": "admin_test", "role": "admin", "email": "admin@test.com"},
        {
            "username": "community_test",
            "role": "community_admin",
            "email": "community@test.com",
        },
        {"username": "tech_test", "role": "technician", "email": "tech@test.com"},
    ]

    expected_redirects = {
        "farmer": "/dashboard/farmer/",
        "admin": "/dashboard/",
        "community_admin": "/dashboard/",
        "technician": "/dashboard/",
    }

    for user_data in test_users:
        print(f"\nTesting user role: {user_data['role']}")

        # Create or get user
        try:
            user = User.objects.get(username=user_data["username"])
            # Update role for existing user
            User.objects.filter(username=user_data["username"]).update(
                role=user_data["role"]
            )
            user.refresh_from_db()
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=user_data["username"],
                email=user_data["email"],
                password="testpass123",
                role=user_data["role"],
            )

        # Login the user
        client.force_login(user)

        # Test the redirect URL
        response = client.get(reverse("dashboard:redirect"))

        expected_url = expected_redirects[user_data["role"]]

        print(f"Response status: {response.status_code}")
        print(f"Expected redirect to: {expected_url}")

        if response.status_code == 302:
            redirect_url = response.get("Location", "")
            print(f"Actually redirected to: {redirect_url}")
            if redirect_url == expected_url:
                print("✅ Redirect test PASSED")
            else:
                print("❌ Redirect test FAILED")
        else:
            print("❌ Expected a redirect (302), but got a different response")

        # Logout
        client.logout()


if __name__ == "__main__":
    print("Starting role-based dashboard redirect tests...")
    test_role_based_dashboard_redirect()
    print("\nAll tests completed!")
