from django.contrib import admin
from .models import GrantCategory, Grant, GrantApplication


@admin.register(GrantCategory)
class GrantCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "color_class", "is_active", "created_at")
    list_filter = ("is_active", "color_class")
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "amount",
        "priority",
        "is_featured",
        "is_active",
        "application_deadline",
        "views_count",
    )
    list_filter = ("category", "priority", "is_featured", "is_active", "is_always_open")
    search_fields = ("title", "description", "eligibility")
    ordering = ("-is_featured", "-priority", "-created_at")
    readonly_fields = ("views_count", "created_at", "updated_at")

    fieldsets = (
        ("Basic Information", {"fields": ("title", "description", "category")}),
        ("Financial Details", {"fields": ("amount", "max_amount")}),
        ("Eligibility", {"fields": ("eligibility", "required_documents")}),
        (
            "Application Details",
            {"fields": ("application_url", "application_deadline", "is_always_open")},
        ),
        (
            "Additional Information",
            {"fields": ("duration", "interest_rate", "coverage")},
        ),
        (
            "Management",
            {"fields": ("priority", "is_featured", "is_active", "views_count")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(GrantApplication)
class GrantApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "applicant",
        "grant",
        "status",
        "application_date",
        "documents_submitted",
        "verification_complete",
    )
    list_filter = (
        "status",
        "documents_submitted",
        "verification_complete",
        "application_date",
    )
    search_fields = ("applicant__username", "applicant__email", "grant__title")
    ordering = ("-application_date",)
    readonly_fields = ("application_date", "updated_at")

    fieldsets = (
        ("Application Details", {"fields": ("grant", "applicant", "status")}),
        ("Progress", {"fields": ("documents_submitted", "verification_complete")}),
        ("Notes", {"fields": ("notes", "admin_notes")}),
        (
            "Timestamps",
            {
                "fields": (
                    "application_date",
                    "submitted_at",
                    "reviewed_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
