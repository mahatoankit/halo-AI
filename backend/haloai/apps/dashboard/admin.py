from django.contrib import admin
from .models import (
    SubscriptionPlan,
    FarmerSubscription,
    PaymentRecord,
    ManualCropInput,
    FarmerFieldProfile,
    SoilHealthReport,
    ExpertConsultation,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["display_name", "name", "price", "monthly_predictions", "is_active"]
    list_filter = ["name", "is_active", "expert_consultation", "sensor_data_access"]
    search_fields = ["display_name", "description"]
    ordering = ["price"]


@admin.register(FarmerSubscription)
class FarmerSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "farmer",
        "plan",
        "status",
        "start_date",
        "end_date",
        "predictions_used",
    ]
    list_filter = ["status", "plan", "start_date"]
    search_fields = ["farmer__username", "farmer__first_name", "farmer__last_name"]
    date_hierarchy = "start_date"
    raw_id_fields = ["farmer", "community_admin"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("farmer", "plan", "community_admin")
        )


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "subscription",
        "amount",
        "payment_method",
        "status",
        "payment_date",
    ]
    list_filter = ["status", "payment_method", "payment_date"]
    search_fields = ["subscription__farmer__username", "transaction_id"]
    date_hierarchy = "payment_date"
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ManualCropInput)
class ManualCropInputAdmin(admin.ModelAdmin):
    list_display = ["farmer", "nitrogen", "phosphorus", "potassium", "ph", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["farmer__username", "farmer__first_name", "farmer__last_name"]
    date_hierarchy = "created_at"
    readonly_fields = ["id", "created_at"]

    fieldsets = (
        ("Farmer Information", {"fields": ("farmer",)}),
        ("Soil Parameters", {"fields": ("nitrogen", "phosphorus", "potassium", "ph")}),
        (
            "Environmental Parameters",
            {"fields": ("temperature", "humidity", "rainfall")},
        ),
        (
            "Additional Information",
            {"fields": ("field_area", "notes", "created_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(FarmerFieldProfile)
class FarmerFieldProfileAdmin(admin.ModelAdmin):
    list_display = ["farmer", "region", "district", "total_area", "irrigation_type"]
    list_filter = ["region", "district", "irrigation_type", "organic_farming"]
    search_fields = [
        "farmer__username",
        "farmer__first_name",
        "farmer__last_name",
        "region",
    ]

    fieldsets = (
        ("Farmer", {"fields": ("farmer",)}),
        ("Location Details", {"fields": ("region", "district", "local_unit")}),
        ("Farm Details", {"fields": ("total_area", "soil_type", "irrigation_type")}),
        ("Crop Information", {"fields": ("primary_crops", "secondary_crops")}),
        (
            "Farming Practices",
            {
                "fields": ("organic_farming", "experience_years"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(SoilHealthReport)
class SoilHealthReportAdmin(admin.ModelAdmin):
    list_display = ["farmer", "report_type", "test_date", "health_score", "ph"]
    list_filter = ["report_type", "test_date", "health_score"]
    search_fields = [
        "farmer__username",
        "farmer__first_name",
        "farmer__last_name",
        "lab_name",
    ]
    date_hierarchy = "test_date"
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        (
            "Report Information",
            {"fields": ("farmer", "report_type", "test_date", "lab_name")},
        ),
        (
            "Primary Nutrients",
            {"fields": ("nitrogen", "phosphorus", "potassium", "ph")},
        ),
        (
            "Additional Parameters",
            {
                "fields": ("organic_matter", "electrical_conductivity"),
                "classes": ("collapse",),
            },
        ),
        (
            "Micronutrients",
            {
                "fields": ("zinc", "iron", "manganese", "copper"),
                "classes": ("collapse",),
            },
        ),
        (
            "Analysis",
            {
                "fields": (
                    "health_score",
                    "recommendations",
                    "deficiencies",
                    "report_file",
                )
            },
        ),
    )


@admin.register(ExpertConsultation)
class ExpertConsultationAdmin(admin.ModelAdmin):
    list_display = [
        "farmer",
        "consultation_type",
        "subject",
        "status",
        "is_urgent",
        "created_at",
    ]
    list_filter = [
        "consultation_type",
        "status",
        "is_urgent",
        "preferred_contact_method",
        "created_at",
    ]
    search_fields = [
        "farmer__username",
        "farmer__first_name",
        "farmer__last_name",
        "subject",
    ]
    date_hierarchy = "created_at"
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["expert"]

    fieldsets = (
        (
            "Consultation Request",
            {"fields": ("farmer", "consultation_type", "subject", "description")},
        ),
        ("Contact Preferences", {"fields": ("is_urgent", "preferred_contact_method")}),
        (
            "Assignment & Response",
            {"fields": ("expert", "status", "expert_response", "response_date")},
        ),
        ("Attachments", {"fields": ("images",), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("farmer", "expert")
