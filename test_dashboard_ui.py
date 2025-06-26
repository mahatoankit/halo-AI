#!/usr/bin/env python3
"""
Test script to verify the farmer dashboard UI loads without template errors.
"""

import os
import sys
import django
import requests
from django.test import Client, TestCase
from django.contrib.auth import get_user_model

# Add the backend/haloai directory to Python path
sys.path.insert(
    0, "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from apps.users.models import CustomUser


def test_dashboard_template():
    """Test if the farmer dashboard template loads without errors."""
    print("Testing farmer dashboard template...")

    # Create a test client
    client = Client()

    # Create or get a test user
    User = CustomUser
    test_user, created = User.objects.get_or_create(
        username="testfarmer",
        defaults={
            "email": "test@farmer.com",
            "first_name": "Test",
            "last_name": "Farmer",
            "role": "farmer",
            "phone": "+1234567890",
        },
    )

    # Log in the test user
    client.force_login(test_user)

    try:
        # Try to access the farmer dashboard
        response = client.get("/dashboard/farmer/")

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Dashboard loaded successfully!")
            print(f"Response content length: {len(response.content)} bytes")

            # Check if there are any template errors in the response
            content = response.content.decode("utf-8")
            if "TemplateSyntaxError" in content:
                print("❌ Template syntax error found in response")
                return False
            elif "Invalid block tag" in content:
                print("❌ Invalid block tag error found in response")
                return False
            else:
                print("✅ No template syntax errors detected")
                return True

        elif response.status_code == 302:
            print(f"🔄 Redirected to: {response.get('Location', 'Unknown')}")
            return True

        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response content: {response.content.decode('utf-8')[:500]}")
            return False

    except Exception as e:
        print(f"❌ Error testing dashboard: {str(e)}")
        return False


def test_dashboard_via_redirect():
    """Test dashboard access via the role-based redirect."""
    print("\nTesting dashboard via role-based redirect...")

    client = Client()

    # Get the test user
    User = CustomUser
    test_user = User.objects.get(username="testfarmer")

    # Log in the test user
    client.force_login(test_user)

    try:
        # Try to access the dashboard redirect URL
        response = client.get("/dashboard/")

        print(f"Response status: {response.status_code}")

        if response.status_code == 302:
            redirect_url = response.get("Location", "")
            print(f"✅ Redirected to: {redirect_url}")

            # Follow the redirect
            if redirect_url.endswith("/dashboard/farmer/"):
                response = client.get(redirect_url)
                print(f"Final response status: {response.status_code}")

                if response.status_code == 200:
                    print("✅ Dashboard loaded successfully after redirect!")
                    return True
                else:
                    print(
                        f"❌ Error loading dashboard after redirect: {response.status_code}"
                    )
                    return False
            else:
                print(f"❌ Unexpected redirect URL: {redirect_url}")
                return False
        else:
            print(f"❌ Expected redirect, got status: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error testing dashboard redirect: {str(e)}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Farmer Dashboard UI...")
    print("=" * 50)

    # Test direct dashboard access
    success1 = test_dashboard_template()

    # Test dashboard via redirect
    success2 = test_dashboard_via_redirect()

    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All dashboard tests passed!")
    else:
        print("❌ Some dashboard tests failed!")

    print("🧪 Testing complete.")
