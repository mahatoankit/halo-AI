#!/usr/bin/env python
"""
Script to create sample expert data for testing the experts app
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from apps.experts.models import ExpertSpecialization, ExpertProfile
from decimal import Decimal

User = get_user_model()


def create_sample_data():
    """Create sample specializations and expert profiles"""

    # Create specializations
    specializations_data = [
        {
            "name": "Crop Disease Management",
            "description": "Diagnosis and treatment of plant diseases",
            "icon": "fas fa-leaf",
        },
        {
            "name": "Soil Science",
            "description": "Soil analysis and fertility management",
            "icon": "fas fa-seedling",
        },
        {
            "name": "Pest Control",
            "description": "Integrated pest management solutions",
            "icon": "fas fa-bug",
        },
        {
            "name": "Irrigation Systems",
            "description": "Water management and irrigation planning",
            "icon": "fas fa-tint",
        },
        {
            "name": "Organic Farming",
            "description": "Sustainable and organic agriculture practices",
            "icon": "fas fa-recycle",
        },
        {
            "name": "Crop Planning",
            "description": "Crop rotation and seasonal planning",
            "icon": "fas fa-calendar-alt",
        },
    ]

    print("Creating specializations...")
    specializations = []
    for spec_data in specializations_data:
        spec, created = ExpertSpecialization.objects.get_or_create(
            name=spec_data["name"],
            defaults={
                "description": spec_data["description"],
                "icon": spec_data["icon"],
            },
        )
        specializations.append(spec)
        if created:
            print(f"  ✓ Created: {spec.name}")
        else:
            print(f"  → Already exists: {spec.name}")

    # Create sample expert users
    experts_data = [
        {
            "username": "dr_smith_agro",
            "email": "dr.smith@example.com",
            "first_name": "John",
            "last_name": "Smith",
            "professional_title": "Senior Agricultural Scientist",
            "organization": "National Agricultural Research Institute",
            "years_of_experience": 15,
            "education_background": "PhD in Plant Pathology from Agricultural University, MSc in Crop Science",
            "bio": "Dr. Smith is a renowned expert in crop disease management with over 15 years of experience. He has published numerous research papers and helped thousands of farmers improve their crop yields.",
            "phone_number": "+977-9841234567",
            "hourly_rate": Decimal("2500.00"),
            "service_areas": "Kathmandu, Bhaktapur, Lalitpur, Central Nepal",
            "consultation_modes": "both",
            "languages_spoken": "English, Nepali, Hindi",
            "specializations": ["Crop Disease Management", "Soil Science"],
        },
        {
            "username": "expert_maria",
            "email": "maria.gonzalez@example.com",
            "first_name": "Maria",
            "last_name": "Gonzalez",
            "professional_title": "Organic Farming Specialist",
            "organization": "Sustainable Agriculture Foundation",
            "years_of_experience": 8,
            "education_background": "MSc in Sustainable Agriculture, BSc in Environmental Science",
            "bio": "Maria specializes in organic farming and sustainable agriculture practices. She helps farmers transition to organic methods and achieve organic certification.",
            "phone_number": "+977-9851234567",
            "hourly_rate": Decimal("1800.00"),
            "service_areas": "Pokhara, Kaski, Gandaki Province",
            "consultation_modes": "online",
            "languages_spoken": "English, Spanish, Nepali",
            "specializations": ["Organic Farming", "Pest Control"],
        },
        {
            "username": "eng_patel",
            "email": "raj.patel@example.com",
            "first_name": "Raj",
            "last_name": "Patel",
            "professional_title": "Irrigation Engineer",
            "organization": "Water Management Solutions Pvt. Ltd.",
            "years_of_experience": 12,
            "education_background": "BTech in Agricultural Engineering, MTech in Water Resources",
            "bio": "Raj is an experienced irrigation engineer specializing in modern irrigation systems and water management. He helps farmers optimize water usage and improve crop productivity.",
            "phone_number": "+977-9861234567",
            "hourly_rate": Decimal("2200.00"),
            "service_areas": "Chitwan, Nawalpur, Bagmati Province",
            "consultation_modes": "in_person",
            "languages_spoken": "English, Nepali, Hindi, Gujarati",
            "specializations": ["Irrigation Systems", "Crop Planning"],
        },
    ]

    print("\nCreating expert users and profiles...")
    for expert_data in experts_data:
        # Create user
        user, user_created = User.objects.get_or_create(
            username=expert_data["username"],
            defaults={
                "email": expert_data["email"],
                "first_name": expert_data["first_name"],
                "last_name": expert_data["last_name"],
                "role": "expert",
            },
        )

        if user_created:
            user.set_password("testpass123")
            user.save()
            print(f"  ✓ Created user: {user.username}")
        else:
            print(f"  → User already exists: {user.username}")

        # Create expert profile
        profile, profile_created = ExpertProfile.objects.get_or_create(
            user=user,
            defaults={
                "professional_title": expert_data["professional_title"],
                "organization": expert_data["organization"],
                "years_of_experience": expert_data["years_of_experience"],
                "education_background": expert_data["education_background"],
                "bio": expert_data["bio"],
                "phone_number": expert_data["phone_number"],
                "hourly_rate": expert_data["hourly_rate"],
                "service_areas": expert_data["service_areas"],
                "consultation_modes": expert_data["consultation_modes"],
                "languages_spoken": expert_data["languages_spoken"],
                "verification_status": "verified",
                "is_available": True,
            },
        )

        if profile_created:
            print(f"  ✓ Created profile: {profile.professional_title}")

            # Add specializations
            for spec_name in expert_data["specializations"]:
                try:
                    spec = ExpertSpecialization.objects.get(name=spec_name)
                    profile.specializations.add(spec)
                except ExpertSpecialization.DoesNotExist:
                    print(f"    ⚠ Specialization not found: {spec_name}")

            profile.save()
        else:
            print(f"  → Profile already exists: {profile.professional_title}")

    print("\n✅ Sample data creation completed!")
    print("\nCreated:")
    print(f"  - {ExpertSpecialization.objects.count()} specializations")
    print(
        f"  - {ExpertProfile.objects.filter(verification_status='verified').count()} verified expert profiles"
    )
    print("\nYou can now test the experts app with sample data!")


if __name__ == "__main__":
    create_sample_data()
