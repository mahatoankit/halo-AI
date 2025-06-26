#!/usr/bin/env python
"""
Test script to verify login redirect functionality for farmers
"""
import os
import sys
import django
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

# Add the Django project to path
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

User = get_user_model()


def test_farmer_login_redirect():
    """Test that farmer login redirects to farmer dashboard"""
    print("🧪 Testing farmer login redirect...")

    # Create test client
    client = Client()

    # Create a test farmer user
    try:
        # Clean up any existing test user
        if User.objects.filter(username="test_farmer").exists():
            User.objects.filter(username="test_farmer").delete()

        farmer = User.objects.create_user(
            username="test_farmer",
            password="testpass123",
            email="test@farmer.com",
            role="farmer",
        )
        print(
            f"✅ Created test farmer: {farmer.username} with role: {getattr(farmer, 'role', 'farmer')}"
        )

        # Test login redirect
        response = client.post(
            "/auth/login/", {"username": "test_farmer", "password": "testpass123"}
        )

        print(f"📡 Login response status: {response.status_code}")
        print(f"📍 Redirect location: {response.get('Location', 'No redirect')}")

        # Check if redirected to farmer dashboard
        if response.status_code == 302:
            location = response.get("Location", "")
            if "/dashboard/farmer/" in location:
                print("✅ SUCCESS: Farmer redirected to farmer dashboard!")
                return True
            else:
                print(
                    f"❌ FAILED: Farmer redirected to {location} instead of farmer dashboard"
                )
                return False
        else:
            print(f"❌ FAILED: Expected redirect (302), got {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        # Clean up
        try:
            User.objects.filter(username="test_farmer").delete()
            print("🧹 Cleaned up test user")
        except:
            pass


def test_community_admin_login_redirect():
    """Test that community admin login redirects correctly"""
    print("\n🧪 Testing community admin login redirect...")

    # Create test client
    client = Client()

    try:
        # Clean up any existing test user
        if User.objects.filter(username="test_admin").exists():
            User.objects.filter(username="test_admin").delete()

        admin = User.objects.create_user(
            username="test_admin",
            password="testpass123",
            email="test@admin.com",
            role="community_admin",
            is_approved=True,
        )
        print(
            f"✅ Created test admin: {admin.username} with role: {getattr(admin, 'role', 'community_admin')}"
        )

        # Test login redirect
        response = client.post(
            "/auth/login/", {"username": "test_admin", "password": "testpass123"}
        )

        print(f"📡 Login response status: {response.status_code}")
        print(f"📍 Redirect location: {response.get('Location', 'No redirect')}")

        # Check if redirected to community dashboard
        if response.status_code == 302:
            location = response.get("Location", "")
            if "/auth/community/dashboard/" in location:
                print("✅ SUCCESS: Community admin redirected to community dashboard!")
                return True
            else:
                print(f"❌ FAILED: Community admin redirected to {location}")
                return False
        else:
            print(f"❌ FAILED: Expected redirect (302), got {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        # Clean up
        try:
            User.objects.filter(username="test_admin").delete()
            print("🧹 Cleaned up test user")
        except:
            pass


if __name__ == "__main__":
    print("🚀 Starting login redirect tests...\n")

    farmer_success = test_farmer_login_redirect()
    admin_success = test_community_admin_login_redirect()

    print(f"\n📊 Test Results:")
    print(f"Farmer redirect: {'✅ PASS' if farmer_success else '❌ FAIL'}")
    print(f"Admin redirect: {'✅ PASS' if admin_success else '❌ FAIL'}")

    if farmer_success and admin_success:
        print("\n🎉 All tests passed! Login redirects are working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        sys.exit(1)
