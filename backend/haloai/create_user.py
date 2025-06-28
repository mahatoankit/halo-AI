from apps.users.models import CustomUser, FarmerProfile

# Create test farmer user
username = "testfarmer"
if not CustomUser.objects.filter(username=username).exists():
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
else:
    user = CustomUser.objects.get(username=username)
    print(f"✅ Test farmer user {username} already exists")

# Create farmer profile
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

print("\n🚀 Login credentials:")
print("Username: testfarmer")
print("Password: testpass123")
