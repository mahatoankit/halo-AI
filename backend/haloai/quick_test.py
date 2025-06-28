#!/usr/bin/env python3
"""
Quick test of expert detail page
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


def test_expert_detail():
    """Quick test of expert detail page"""
    print("🧪 Testing Expert Detail Page")

    client = Client()

    try:
        response = client.get("/experts/expert/2/")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print("   ✅ Expert detail page loads successfully")
        else:
            print(f"   ❌ Expert detail failed with status {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    test_expert_detail()
