#!/usr/bin/env python3
"""
Test experts app URLs and views
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.experts.models import ExpertProfile, ExpertSpecialization


def test_experts_views():
    """Test experts app views"""
    print("🧪 Testing Experts App Views\n")

    client = Client()

    # Test experts list view
    try:
        print("Testing experts list view...")
        response = client.get("/experts/")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print("   ✅ Experts list loads successfully")
            print(f"   📄 Content length: {len(response.content)} bytes")
        else:
            print(f"   ❌ Experts list failed with status {response.status_code}")
            if hasattr(response, "content"):
                print(f"   Error content: {response.content.decode()[:500]}")

    except Exception as e:
        print(f"   ❌ Error accessing experts list: {e}")

    # Test URL reversal
    try:
        print("\nTesting URL reversal...")
        experts_list_url = reverse("experts:experts_list")
        print(f"   ✅ experts:experts_list URL: {experts_list_url}")

        become_expert_url = reverse("experts:become_expert")
        print(f"   ✅ experts:become_expert URL: {become_expert_url}")

    except Exception as e:
        print(f"   ❌ URL reversal error: {e}")

    # Test model access
    try:
        print("\nTesting model access...")
        experts_count = ExpertProfile.objects.count()
        specs_count = ExpertSpecialization.objects.count()
        print(f"   📊 Expert profiles: {experts_count}")
        print(f"   📊 Specializations: {specs_count}")

        if experts_count > 0:
            first_expert = ExpertProfile.objects.first()
            print(f"   👤 First expert: {first_expert.user.get_full_name()}")

    except Exception as e:
        print(f"   ❌ Model access error: {e}")


if __name__ == "__main__":
    test_experts_views()
