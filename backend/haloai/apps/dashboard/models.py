from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()


class SubscriptionPlan(models.Model):
    """Subscription plans for farmers"""

    PLAN_TYPES = [
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("gold", "Gold"),
    ]

    name = models.CharField(max_length=50, choices=PLAN_TYPES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="NPR")

    # Features
    monthly_predictions = models.IntegerField(
        help_text="Number of predictions per month"
    )
    expert_consultation = models.BooleanField(default=False)
    sensor_data_access = models.BooleanField(default=False)
    soil_health_reports = models.BooleanField(default=False)
    weather_alerts = models.BooleanField(default=True)

    # Billing
    billing_cycle_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.display_name} - ₹{self.price}"


class FarmerSubscription(models.Model):
    """Individual farmer subscription records"""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("suspended", "Suspended"),
        ("cancelled", "Cancelled"),
    ]

    farmer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="subscription",
        limit_choices_to={"role": "farmer"},
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    community_admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="managed_subscriptions",
        limit_choices_to={"role": "community_admin"},
    )

    # Subscription details
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    # Usage tracking
    predictions_used = models.IntegerField(default=0)
    last_reset_date = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def predictions_remaining(self):
        return max(0, self.plan.monthly_predictions - self.predictions_used)

    @property
    def is_active(self):
        from django.utils import timezone

        return self.status == "active" and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.farmer.get_full_name()} - {self.plan.display_name}"


class PaymentRecord(models.Model):
    """Payment history for farmer subscriptions"""

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("esewa", "eSewa"),
        ("khalti", "Khalti"),
        ("bank_transfer", "Bank Transfer"),
        ("mobile_banking", "Mobile Banking"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        FarmerSubscription, on_delete=models.CASCADE, related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="NPR")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")

    # External reference
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_gateway_response = models.JSONField(blank=True, null=True)

    # Dates
    payment_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Payment {self.id} - ₹{self.amount} ({self.status})"


class ManualCropInput(models.Model):
    """Manual input by farmers for crop recommendations"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="manual_inputs",
        limit_choices_to={"role": "farmer"},
    )

    # Soil parameters
    nitrogen = models.FloatField(help_text="N value (0-140)")
    phosphorus = models.FloatField(help_text="P value (5-145)")
    potassium = models.FloatField(help_text="K value (5-205)")
    ph = models.FloatField(help_text="Soil pH level (3.5-10)")

    # Environmental parameters
    temperature = models.FloatField(help_text="Temperature in Celsius")
    humidity = models.FloatField(help_text="Humidity percentage")
    rainfall = models.FloatField(help_text="Rainfall in mm")

    # Optional field information
    field_area = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Field area in acres",
    )
    notes = models.TextField(blank=True, help_text="Additional notes about the field")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Manual Input by {self.farmer.get_full_name()} - {self.created_at.date()}"
        )


class FarmerFieldProfile(models.Model):
    """Field profile information for farmers"""

    farmer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="field_profile",
        limit_choices_to={"role": "farmer"},
    )

    # Location details
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    local_unit = models.CharField(max_length=100, blank=True)

    # Farm details
    total_area = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="Total farm area in acres"
    )
    soil_type = models.CharField(max_length=100, blank=True)
    irrigation_type = models.CharField(
        max_length=50,
        choices=[
            ("rain_fed", "Rain Fed"),
            ("canal", "Canal Irrigation"),
            ("tubewell", "Tubewell"),
            ("drip", "Drip Irrigation"),
            ("sprinkler", "Sprinkler"),
            ("mixed", "Mixed"),
        ],
        default="rain_fed",
    )

    # Crop preferences
    primary_crops = models.TextField(help_text="Main crops typically grown")
    secondary_crops = models.TextField(blank=True, help_text="Secondary/rotation crops")

    # Farming practices
    organic_farming = models.BooleanField(default=False)
    experience_years = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.farmer.get_full_name()} - {self.region}, {self.district}"


class SoilHealthReport(models.Model):
    """Soil health reports for farmers"""

    REPORT_TYPES = [
        ("lab_test", "Laboratory Test"),
        ("field_test", "Field Test Kit"),
        ("sensor_data", "IoT Sensor Data"),
        ("manual_upload", "Manual Upload"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="soil_reports",
        limit_choices_to={"role": "farmer"},
    )

    # Report details
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    test_date = models.DateField()
    lab_name = models.CharField(max_length=200, blank=True)

    # Soil parameters
    nitrogen = models.FloatField(null=True, blank=True)
    phosphorus = models.FloatField(null=True, blank=True)
    potassium = models.FloatField(null=True, blank=True)
    ph = models.FloatField(null=True, blank=True)
    organic_matter = models.FloatField(null=True, blank=True, help_text="Percentage")
    electrical_conductivity = models.FloatField(null=True, blank=True)

    # Micronutrients (if available)
    zinc = models.FloatField(null=True, blank=True)
    iron = models.FloatField(null=True, blank=True)
    manganese = models.FloatField(null=True, blank=True)
    copper = models.FloatField(null=True, blank=True)

    # File attachments
    report_file = models.FileField(
        upload_to="soil_reports/",
        blank=True,
        null=True,
        help_text="PDF or image of the soil report",
    )

    # Analysis and recommendations
    health_score = models.FloatField(
        null=True, blank=True, help_text="Overall soil health score (0-100)"
    )
    recommendations = models.TextField(blank=True)
    deficiencies = models.JSONField(
        default=list, help_text="List of nutrient deficiencies"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-test_date"]

    def __str__(self):
        return f"Soil Report - {self.farmer.get_full_name()} ({self.test_date})"


class ExpertConsultation(models.Model):
    """Expert consultation requests from farmers"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    CONSULTATION_TYPES = [
        ("crop_selection", "Crop Selection"),
        ("disease_diagnosis", "Disease Diagnosis"),
        ("soil_health", "Soil Health"),
        ("irrigation", "Irrigation Management"),
        ("pest_control", "Pest Control"),
        ("fertilizer", "Fertilizer Recommendation"),
        ("general", "General Farming"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="consultations",
        limit_choices_to={"role": "farmer"},
    )
    expert = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_consultations",
        limit_choices_to={"role__in": ["community_admin", "technician"]},
    )

    # Consultation details
    consultation_type = models.CharField(max_length=30, choices=CONSULTATION_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Priority and urgency
    is_urgent = models.BooleanField(default=False)
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ("phone", "Phone Call"),
            ("whatsapp", "WhatsApp"),
            ("message", "Text Message"),
            ("in_person", "In Person Visit"),
        ],
        default="phone",
    )

    # Response
    expert_response = models.TextField(blank=True)
    response_date = models.DateTimeField(null=True, blank=True)

    # Attachments
    images = models.JSONField(
        default=list, help_text="List of image URLs for crop/field photos"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Consultation - {self.farmer.get_full_name()} ({self.consultation_type})"
        )
