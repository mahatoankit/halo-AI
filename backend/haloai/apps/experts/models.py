from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()


class ExpertSpecialization(models.Model):
    """Categories of agricultural expertise"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ExpertProfile(models.Model):
    """Extended profile for agricultural experts"""

    VERIFICATION_STATUS = [
        ("pending", "Pending Verification"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    CONSULTATION_MODES = [
        ("online", "Online (Video/Phone)"),
        ("in_person", "In-Person Visit"),
        ("both", "Both Online & In-Person"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="expert_profile"
    )

    # Professional Information
    professional_title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200, blank=True)
    years_of_experience = models.PositiveIntegerField()
    education_background = models.TextField()
    professional_license = models.CharField(max_length=100, blank=True)

    # Specializations
    specializations = models.ManyToManyField(
        ExpertSpecialization, related_name="experts"
    )

    # Contact & Availability
    phone_number = models.CharField(max_length=15)
    consultation_modes = models.CharField(
        max_length=20, choices=CONSULTATION_MODES, default="both"
    )
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=10, default="NPR")

    # Location for in-person consultations
    service_areas = models.TextField(
        help_text="Areas where expert provides in-person services"
    )
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    # Verification & Status
    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUS, default="pending"
    )
    verification_documents = models.FileField(upload_to="expert_docs/", blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_experts",
    )

    # Profile Enhancement
    profile_image = models.ImageField(upload_to="expert_photos/", blank=True)
    bio = models.TextField()
    languages_spoken = models.CharField(
        max_length=200, help_text="Comma-separated languages"
    )

    # Availability
    is_available = models.BooleanField(default=True)
    available_days = models.CharField(
        max_length=100, default="Monday,Tuesday,Wednesday,Thursday,Friday"
    )
    available_hours = models.CharField(max_length=100, default="09:00-17:00")

    # Statistics (updated by signals)
    total_consultations = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-average_rating", "-total_consultations"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.professional_title}"

    @property
    def is_verified(self):
        return self.verification_status == "verified"

    @property
    def specialization_names(self):
        return ", ".join([spec.name for spec in self.specializations.all()])


class ConsultationRequest(models.Model):
    """Consultation booking requests from farmers"""

    STATUS_CHOICES = [
        ("pending", "Pending Expert Response"),
        ("accepted", "Accepted by Expert"),
        ("rejected", "Rejected by Expert"),
        ("completed", "Consultation Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    ]

    CONSULTATION_TYPES = [
        ("general", "General Agricultural Advice"),
        ("crop_disease", "Crop Disease Diagnosis"),
        ("soil_analysis", "Soil Analysis & Recommendations"),
        ("pest_management", "Pest Management"),
        ("fertilizer", "Fertilizer Recommendations"),
        ("irrigation", "Irrigation Planning"),
        ("crop_planning", "Crop Planning & Selection"),
        ("marketing", "Agricultural Marketing"),
        ("technology", "Agricultural Technology"),
        ("organic_farming", "Organic Farming"),
        ("other", "Other (Specify in description)"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Participants
    farmer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="consultation_requests"
    )
    expert = models.ForeignKey(
        ExpertProfile, on_delete=models.CASCADE, related_name="consultation_requests"
    )

    # Consultation Details
    consultation_type = models.CharField(max_length=30, choices=CONSULTATION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    preferred_mode = models.CharField(
        max_length=20, choices=ExpertProfile.CONSULTATION_MODES
    )

    # Scheduling
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)

    # Location (for in-person consultations)
    consultation_address = models.TextField(blank=True)
    consultation_latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    consultation_longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    # Status & Response
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    expert_response = models.TextField(blank=True)
    expert_responded_at = models.DateTimeField(null=True, blank=True)

    # Meeting Details (filled after acceptance)
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    meeting_link = models.URLField(blank=True, help_text="For online consultations")
    actual_duration = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )

    # Payment
    total_cost = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    payment_status = models.CharField(max_length=20, default="pending")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.farmer.username} -> {self.expert.user.username}"

    @property
    def is_upcoming(self):
        if self.scheduled_datetime:
            return (
                self.scheduled_datetime > timezone.now() and self.status == "accepted"
            )
        return False

    def calculate_cost(self):
        """Calculate total consultation cost"""
        if self.expert.hourly_rate and self.duration_hours:
            return float(self.expert.hourly_rate) * float(self.duration_hours)
        return 0


class ConsultationReview(models.Model):
    """Reviews and ratings for completed consultations"""

    consultation = models.OneToOneField(
        ConsultationRequest, on_delete=models.CASCADE, related_name="review"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_reviews"
    )
    expert = models.ForeignKey(
        ExpertProfile, on_delete=models.CASCADE, related_name="received_reviews"
    )

    # Rating (1-5 stars)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Review Details
    title = models.CharField(max_length=200)
    review_text = models.TextField()

    # Rating Categories
    expertise_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    communication_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    punctuality_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    value_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Recommendations
    would_recommend = models.BooleanField(default=True)
    improvement_suggestions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review for {self.expert.user.username} by {self.reviewer.username} - {self.rating}★"


class ExpertAvailability(models.Model):
    """Expert availability calendar"""

    expert = models.ForeignKey(
        ExpertProfile, on_delete=models.CASCADE, related_name="availability_slots"
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    # Optional details
    notes = models.CharField(max_length=200, blank=True)
    max_consultations = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["expert", "date", "start_time"]
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.expert.user.username} - {self.date} {self.start_time}-{self.end_time}"


class ExpertBlog(models.Model):
    """Expert knowledge sharing through blog posts"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    expert = models.ForeignKey(
        ExpertProfile, on_delete=models.CASCADE, related_name="blog_posts"
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300)

    # Categorization
    specializations = models.ManyToManyField(
        ExpertSpecialization, related_name="blog_posts"
    )
    tags = models.CharField(
        max_length=200, blank=True, help_text="Comma-separated tags"
    )

    # Media
    featured_image = models.ImageField(upload_to="expert_blogs/", blank=True)

    # Status & SEO
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    meta_description = models.CharField(max_length=160, blank=True)

    # Engagement
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title
