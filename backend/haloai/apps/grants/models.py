from django.db import models
from django.utils import timezone


class GrantCategory(models.Model):
    """Categories for grants and offers"""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="📄")
    color_class = models.CharField(
        max_length=50,
        default="green",
        help_text="CSS color class (e.g., green, blue, purple, orange)",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Grant Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Grant(models.Model):
    """Grants and offers for farmers"""

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        GrantCategory, on_delete=models.CASCADE, related_name="grants"
    )

    # Financial details
    amount = models.CharField(
        max_length=100, help_text="e.g., ₹6,000/year, Up to ₹50,000"
    )
    max_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    # Eligibility and requirements
    eligibility = models.TextField(help_text="Who can apply for this grant")
    required_documents = models.TextField(blank=True)

    # Application details
    application_url = models.URLField(blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    is_always_open = models.BooleanField(
        default=False, help_text="No specific deadline"
    )

    # Additional info
    duration = models.CharField(
        max_length=100, blank=True, help_text="e.g., 3 years, One-time"
    )
    interest_rate = models.CharField(max_length=50, blank=True, help_text="For loans")
    coverage = models.CharField(
        max_length=100, blank=True, help_text="Coverage area or beneficiaries"
    )

    # Status and management
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-priority", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_deadline_approaching(self):
        """Check if deadline is within 30 days"""
        if not self.application_deadline:
            return False
        return (self.application_deadline - timezone.now().date()).days <= 30

    @property
    def status_text(self):
        """Get human-readable status"""
        if self.is_always_open:
            return "Apply Anytime"
        elif self.application_deadline:
            if self.is_deadline_approaching:
                return f"Deadline: {self.application_deadline.strftime('%b %d, %Y')} (Soon!)"
            return f"Deadline: {self.application_deadline.strftime('%b %d, %Y')}"
        return "Check Details"


class GrantApplication(models.Model):
    """Track grant applications by users"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("on_hold", "On Hold"),
    ]

    grant = models.ForeignKey(
        Grant, on_delete=models.CASCADE, related_name="applications"
    )
    applicant = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)

    # Application details
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    # Documents (can be extended later)
    documents_submitted = models.BooleanField(default=False)
    verification_complete = models.BooleanField(default=False)

    # Timestamps
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["grant", "applicant"]
        ordering = ["-application_date"]

    def __str__(self):
        return f"{self.applicant.get_full_name()} - {self.grant.title}"
