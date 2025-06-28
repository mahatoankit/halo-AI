from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    ExpertSpecialization,
    ExpertProfile,
    ConsultationRequest,
    ConsultationReview,
    ExpertAvailability,
    ExpertBlog,
)


@admin.register(ExpertSpecialization)
class ExpertSpecializationAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "expert_count", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    ordering = ["name"]

    def expert_count(self, obj):
        return obj.experts.count()

    expert_count.short_description = "Number of Experts"


class ConsultationRequestInline(admin.TabularInline):
    model = ConsultationRequest
    extra = 0
    readonly_fields = ["created_at", "total_cost"]
    fields = [
        "farmer",
        "consultation_type",
        "status",
        "preferred_date",
        "total_cost",
        "created_at",
    ]


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user_full_name",
        "professional_title",
        "verification_status",
        "is_available",
        "total_consultations",
        "average_rating",
        "hourly_rate",
        "created_at",
    ]
    list_filter = [
        "verification_status",
        "is_available",
        "consultation_modes",
        "specializations",
        "created_at",
    ]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "professional_title",
        "organization",
    ]
    readonly_fields = [
        "total_consultations",
        "average_rating",
        "response_rate",
        "created_at",
        "updated_at",
    ]
    filter_horizontal = ["specializations"]
    inlines = [ConsultationRequestInline]

    fieldsets = (
        (
            "User Information",
            {"fields": ("user", "verification_status", "verified_at", "verified_by")},
        ),
        (
            "Professional Details",
            {
                "fields": (
                    "professional_title",
                    "organization",
                    "years_of_experience",
                    "education_background",
                    "professional_license",
                    "specializations",
                )
            },
        ),
        (
            "Contact & Availability",
            {
                "fields": (
                    "phone_number",
                    "consultation_modes",
                    "hourly_rate",
                    "currency",
                    "is_available",
                    "available_days",
                    "available_hours",
                )
            },
        ),
        (
            "Location & Service Areas",
            {"fields": ("service_areas", "latitude", "longitude")},
        ),
        (
            "Profile Information",
            {"fields": ("profile_image", "bio", "languages_spoken")},
        ),
        (
            "Statistics",
            {
                "fields": ("total_consultations", "average_rating", "response_rate"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_full_name.short_description = "Expert Name"
    user_full_name.admin_order_field = "user__first_name"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("specializations")
        )

    actions = ["verify_experts", "unverify_experts"]

    def verify_experts(self, request, queryset):
        updated = queryset.update(
            verification_status="verified",
            verified_at=timezone.now(),
            verified_by=request.user,
        )
        self.message_user(request, f"{updated} experts verified successfully.")

    verify_experts.short_description = "Verify selected experts"

    def unverify_experts(self, request, queryset):
        updated = queryset.update(verification_status="pending")
        self.message_user(request, f"{updated} experts unverified.")

    unverify_experts.short_description = "Unverify selected experts"


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "farmer_name",
        "expert_name",
        "consultation_type",
        "status",
        "preferred_date",
        "total_cost",
        "created_at",
    ]
    list_filter = [
        "status",
        "consultation_type",
        "preferred_mode",
        "created_at",
        "expert__specializations",
    ]
    search_fields = [
        "title",
        "farmer__first_name",
        "farmer__last_name",
        "expert__user__first_name",
        "expert__user__last_name",
    ]
    readonly_fields = ["id", "total_cost", "created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Consultation Details",
            {
                "fields": (
                    "id",
                    "farmer",
                    "expert",
                    "title",
                    "description",
                    "consultation_type",
                )
            },
        ),
        (
            "Scheduling",
            {
                "fields": (
                    "preferred_mode",
                    "preferred_date",
                    "preferred_time",
                    "duration_hours",
                    "scheduled_datetime",
                )
            },
        ),
        (
            "Location (for in-person)",
            {
                "fields": (
                    "consultation_address",
                    "consultation_latitude",
                    "consultation_longitude",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Status & Response",
            {"fields": ("status", "expert_response", "expert_responded_at")},
        ),
        (
            "Meeting Details",
            {"fields": ("meeting_link", "actual_duration"), "classes": ("collapse",)},
        ),
        ("Payment", {"fields": ("total_cost", "payment_status")}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "completed_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def farmer_name(self, obj):
        return obj.farmer.get_full_name() or obj.farmer.username

    farmer_name.short_description = "Farmer"
    farmer_name.admin_order_field = "farmer__first_name"

    def expert_name(self, obj):
        return obj.expert.user.get_full_name() or obj.expert.user.username

    expert_name.short_description = "Expert"
    expert_name.admin_order_field = "expert__user__first_name"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("farmer", "expert__user")

    actions = ["mark_completed", "mark_cancelled"]

    def mark_completed(self, request, queryset):
        updated = queryset.update(status="completed", completed_at=timezone.now())
        self.message_user(request, f"{updated} consultations marked as completed.")

    mark_completed.short_description = "Mark selected consultations as completed"

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} consultations cancelled.")

    mark_cancelled.short_description = "Cancel selected consultations"


@admin.register(ConsultationReview)
class ConsultationReviewAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "reviewer_name",
        "expert_name",
        "rating",
        "would_recommend",
        "created_at",
    ]
    list_filter = ["rating", "would_recommend", "created_at", "expert__specializations"]
    search_fields = [
        "title",
        "review_text",
        "reviewer__first_name",
        "reviewer__last_name",
        "expert__user__first_name",
        "expert__user__last_name",
    ]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Review Information",
            {"fields": ("consultation", "reviewer", "expert", "title", "review_text")},
        ),
        (
            "Ratings",
            {
                "fields": (
                    "rating",
                    "expertise_rating",
                    "communication_rating",
                    "punctuality_rating",
                    "value_rating",
                )
            },
        ),
        ("Recommendations", {"fields": ("would_recommend", "improvement_suggestions")}),
        ("Timestamp", {"fields": ("created_at",)}),
    )

    def reviewer_name(self, obj):
        return obj.reviewer.get_full_name() or obj.reviewer.username

    reviewer_name.short_description = "Reviewer"

    def expert_name(self, obj):
        return obj.expert.user.get_full_name() or obj.expert.user.username

    expert_name.short_description = "Expert"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("reviewer", "expert__user", "consultation")
        )


@admin.register(ExpertAvailability)
class ExpertAvailabilityAdmin(admin.ModelAdmin):
    list_display = [
        "expert_name",
        "date",
        "start_time",
        "end_time",
        "is_available",
        "max_consultations",
    ]
    list_filter = ["is_available", "date", "expert"]
    search_fields = ["expert__user__first_name", "expert__user__last_name"]
    date_hierarchy = "date"

    def expert_name(self, obj):
        return obj.expert.user.get_full_name() or obj.expert.user.username

    expert_name.short_description = "Expert"


@admin.register(ExpertBlog)
class ExpertBlogAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "expert_name",
        "status",
        "views_count",
        "likes_count",
        "published_at",
        "created_at",
    ]
    list_filter = ["status", "specializations", "published_at", "created_at"]
    search_fields = [
        "title",
        "content",
        "tags",
        "expert__user__first_name",
        "expert__user__last_name",
    ]
    readonly_fields = ["slug", "views_count", "likes_count", "created_at", "updated_at"]
    filter_horizontal = ["specializations"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"

    fieldsets = (
        (
            "Post Information",
            {"fields": ("expert", "title", "slug", "excerpt", "content")},
        ),
        ("Categorization", {"fields": ("specializations", "tags")}),
        ("Media", {"fields": ("featured_image",)}),
        ("SEO & Status", {"fields": ("status", "meta_description")}),
        (
            "Statistics",
            {"fields": ("views_count", "likes_count"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "published_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def expert_name(self, obj):
        return obj.expert.user.get_full_name() or obj.expert.user.username

    expert_name.short_description = "Expert"
    expert_name.admin_order_field = "expert__user__first_name"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("expert__user")

    actions = ["publish_posts", "unpublish_posts"]

    def publish_posts(self, request, queryset):
        updated = queryset.update(status="published", published_at=timezone.now())
        self.message_user(request, f"{updated} posts published successfully.")

    publish_posts.short_description = "Publish selected posts"

    def unpublish_posts(self, request, queryset):
        updated = queryset.update(status="draft")
        self.message_user(request, f"{updated} posts unpublished.")

    unpublish_posts.short_description = "Unpublish selected posts"


# Customize admin site header
admin.site.site_header = "HALO-AI Expert System Administration"
admin.site.site_title = "HALO-AI Expert Admin"
admin.site.index_title = "Expert System Management"
