#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)
django.setup()

from apps.users.models import CustomUser

# Create superuser
try:
    if not CustomUser.objects.filter(username="admin").exists():
        CustomUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
        )
        print("✅ Superuser 'admin' created successfully")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("✅ Superuser 'admin' already exists")

    # Also create a test farmer
    if not CustomUser.objects.filter(username="testfarmer").exists():
        user = CustomUser.objects.create_user(
            username="testfarmer",
            email="testfarmer@example.com",
            password="testpass123",
            first_name="John",
            last_name="Farmer",
            role="farmer",
            is_approved=True,
            is_active=True,
        )
        print("✅ Test farmer 'testfarmer' created successfully")
        print("Username: testfarmer")
        print("Password: testpass123")
    else:
        print("✅ Test farmer 'testfarmer' already exists")

except Exception as e:
    print(f"❌ Error: {e}")
