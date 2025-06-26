from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, FarmerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "username",
        "email",
        "role",
        "assigned_region",
        "is_approved",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "is_approved", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name", "assigned_region")
    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        ("Role & Location", {"fields": ("role", "assigned_region", "is_approved")}),
        ("Profile Information", {"fields": ("phone", "profile_image", "bio")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role & Location", {"fields": ("role", "assigned_region", "is_approved")}),
        (
            "Profile Information",
            {"fields": ("phone", "first_name", "last_name", "email")},
        ),
    )

    actions = ["approve_community_admins", "reject_community_admins"]

    @admin.action(description="Approve selected Community Admins")
    def approve_community_admins(self, request, queryset):
        updated = queryset.filter(role="community_admin").update(is_approved=True)
        self.message_user(request, f"{updated} Community Admins approved.")

    @admin.action(description="Reject selected Community Admin applications")
    def reject_community_admins(self, request, queryset):
        deleted = queryset.filter(role="community_admin", is_approved=False).delete()
        self.message_user(
            request, f"{deleted[0]} Community Admin applications rejected."
        )


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "community_admin",
        "farm_location",
        "farm_size_acres",
        "has_smartphone",
        "digital_literacy_level",
    )
    list_filter = ("has_smartphone", "digital_literacy_level", "community_admin")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "farm_location",
        "primary_crops",
    )
    raw_id_fields = ("user", "community_admin")

    fieldsets = (
        ("Farmer Information", {"fields": ("user", "community_admin")}),
        (
            "Farm Details",
            {"fields": ("farm_location", "farm_size_acres", "primary_crops")},
        ),
        (
            "Digital Information",
            {"fields": ("has_smartphone", "digital_literacy_level")},
        ),
    )
