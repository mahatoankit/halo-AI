#!/usr/bin/env python
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.dashboard.models import (
    SubscriptionPlan,
    FarmerSubscription,
    FarmerFieldProfile,
)

User = get_user_model()


def test_dashboard_setup():
    print("🧪 Testing Farmer Dashboard Setup...")

    # Check subscription plans
    plans = SubscriptionPlan.objects.all()
    print(f"📋 Subscription Plans: {plans.count()}")
    for plan in plans:
        print(
            f"   - {plan.display_name}: ₹{plan.price} ({plan.monthly_predictions} predictions)"
        )

    # Check farmers
    farmers = User.objects.filter(role="farmer")
    print(f"👨‍🌾 Farmers: {farmers.count()}")
    for farmer in farmers:
        print(f"   - {farmer.get_full_name()} ({farmer.username})")

        # Check subscription
        try:
            sub = FarmerSubscription.objects.get(farmer=farmer)
            print(f"     Subscription: {sub.plan.display_name} - {sub.status}")
            print(
                f"     Predictions: {sub.predictions_used}/{sub.plan.monthly_predictions}"
            )
        except FarmerSubscription.DoesNotExist:
            print("     No subscription found")

        # Check field profile
        try:
            profile = FarmerFieldProfile.objects.get(farmer=farmer)
            print(f"     Farm: {profile.total_area} acres in {profile.region}")
        except FarmerFieldProfile.DoesNotExist:
            print("     No field profile found")

    print("\n✅ Dashboard setup test completed!")

    # Test URL patterns
    print("\n🔗 Available URLs:")
    print("   - /dashboard/farmer/ - Main farmer dashboard")
    print("   - /dashboard/farmer/predictions/ - Prediction history")
    print("   - /dashboard/farmer/manual-input/ - New prediction form")
    print("   - /dashboard/farmer/subscription/ - Subscription details")

    # Login instructions
    print("\n🔐 Test Login Credentials:")
    print("   - farmer_krishna / demo123")
    print("   - farmer_sita / demo123")
    print("   - farmer_ram / demo123")


if __name__ == "__main__":
    test_dashboard_setup()
