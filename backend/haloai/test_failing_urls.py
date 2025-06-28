#!/usr/bin/env python3
"""
Test specific failing URLs
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
from apps.experts.models import ExpertProfile


def test_failing_urls():
    """Test the URLs that were failing"""
    print("🧪 Testing Previously Failing URLs\n")

    client = Client()

    # Test book consultation URL
    try:
        print("Testing book consultation URL...")
        expert = ExpertProfile.objects.first()
        if expert:
            url = f"/experts/book/{expert.id}/"
            response = client.get(url)
            print(f"   URL: {url}")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print("   ✅ Book consultation loads successfully")
            else:
                print(
                    f"   ❌ Book consultation failed with status {response.status_code}"
                )

        else:
            print("   ⚠️ No experts found to test")

    except Exception as e:
        print(f"   ❌ Error accessing book consultation: {e}")

    # Test expert detail URL
    try:
        print("\nTesting expert detail URL...")
        expert = ExpertProfile.objects.first()
        if expert:
            url = f"/experts/expert/{expert.id}/"
            response = client.get(url)
            print(f"   URL: {url}")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print("   ✅ Expert detail loads successfully")
            else:
                print(f"   ❌ Expert detail failed with status {response.status_code}")

        else:
            print("   ⚠️ No experts found to test")

    except Exception as e:
        print(f"   ❌ Error accessing expert detail: {e}")


if __name__ == "__main__":
    test_failing_urls()
