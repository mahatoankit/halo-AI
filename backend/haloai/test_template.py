#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from django.test import Client
from django.contrib.auth import authenticate
from apps.users.models import CustomUser


def test_manage_farmers_template():
    """Test the manage farmers template and functionality."""

    # Test authentication
    user = authenticate(username="community_admin_bhairahawa", password="demo123")
    if not user:
        print("❌ Authentication failed")
        return False

    print("✅ Authentication successful")

    # Test client login
    client = Client()
    login_success = client.login(
        username="community_admin_bhairahawa", password="demo123"
    )

    if not login_success:
        print("❌ Django test client login failed")
        return False

    print("✅ Django test client login successful")

    # Test manage farmers view
    try:
        response = client.get("/auth/community/manage-farmers/")
        if response.status_code == 200:
            print("✅ Manage farmers page loads successfully")
            print(f"   Response size: {len(response.content)} bytes")
            if b"Manage Registered Farmers" in response.content:
                print("✅ Template content looks correct")
            else:
                print("⚠️  Template content may be incomplete")
            return True
        else:
            print(f"❌ Manage farmers page returned status {response.status_code}")
            if hasattr(response, "content"):
                error_content = response.content.decode("utf-8")[:500]
                print(f"   Error content: {error_content}")
            return False
    except Exception as e:
        print(f"❌ Error accessing manage farmers: {e}")
        return False


if __name__ == "__main__":
    success = test_manage_farmers_template()
    sys.exit(0 if success else 1)
