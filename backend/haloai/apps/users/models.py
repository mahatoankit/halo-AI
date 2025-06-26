from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER_ROLES = [
        ("admin", "Global Administrator"),
        ("community_admin", "Community Administrator"),
        ("technician", "Field Technician"),
        ("farmer", "Farmer"),
    ]

    role = models.CharField(max_length=20, choices=USER_ROLES, default="farmer")
    phone = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)

    # Enhanced location information for hierarchical structure
    assigned_region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Sub-metropolitan area for Community Admins",
    )
    location_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Latitude coordinate for precise location",
    )
    location_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Longitude coordinate for precise location",
    )
    location_address = models.TextField(
        blank=True, null=True, help_text="Full address for location reference"
    )

    # Profile information
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    bio = models.TextField(blank=True, null=True)

    # Status fields
    is_approved = models.BooleanField(
        default=False, help_text="Approval status for Community Admins"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({dict(self.USER_ROLES).get(self.role, self.role)})"

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_community_admin(self):
        return self.role == "community_admin"

    @property
    def is_technician(self):
        return self.role == "technician"

    @property
    def is_farmer(self):
        return self.role == "farmer"


class FarmerProfile(models.Model):
    """Extended profile for farmers managed by Community Admins"""

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="farmer_profile"
    )
    community_admin = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="managed_farmers",
        limit_choices_to={"role": "community_admin"},
    )

    # Farm information
    farm_location = models.CharField(max_length=200)
    farm_size_acres = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    primary_crops = models.TextField(help_text="Main crops grown by the farmer")

    # Digital literacy status
    has_smartphone = models.BooleanField(default=False)
    digital_literacy_level = models.CharField(
        max_length=20,
        choices=[
            ("none", "No Digital Skills"),
            ("basic", "Basic"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        default="none",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.farm_location}"
