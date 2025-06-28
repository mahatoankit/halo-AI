from django.db import models
from django.contrib.auth import get_user_model
from apps.sensors.models import IoTSensorSet
import uuid
import json

User = get_user_model()


class CropType(models.Model):
    """Supported crop types for prediction"""

    name = models.CharField(max_length=50, unique=True)
    scientific_name = models.CharField(max_length=100, blank=True)
    optimal_conditions = models.JSONField(
        default=dict, help_text="Optimal growing conditions as JSON"
    )

    # Regional data for Bhairahawa-Butwal
    regional_success_rate = models.FloatField(
        default=0.0, help_text="Historical success rate in region"
    )
    growing_season = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CropPredictionRequest(models.Model):
    """Crop prediction request with input parameters"""

    PREDICTION_STATUS = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Support both IoT sensor-based and manual input predictions
    community_admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="crop_predictions",
        limit_choices_to={"role": "community_admin"},
        null=True,
        blank=True,
    )
    sensor_set = models.ForeignKey(
        IoTSensorSet,
        on_delete=models.CASCADE,
        related_name="crop_predictions",
        null=True,
        blank=True,
    )
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="farmer_predictions",
        limit_choices_to={"role": "farmer"},
        null=True,
        blank=True,
        help_text="Farmer who requested the prediction (for manual inputs)",
    )
    manual_input = models.ForeignKey(
        "dashboard.ManualCropInput",
        on_delete=models.CASCADE,
        related_name="prediction_requests",
        null=True,
        blank=True,
        help_text="Link to manual crop input if this prediction is from manual data",
    )

    # Input parameters for prediction
    nitrogen = models.FloatField(help_text="N value")
    phosphorus = models.FloatField(help_text="P value")
    potassium = models.FloatField(help_text="K value")
    temperature = models.FloatField(help_text="Temperature in Celsius")
    humidity = models.FloatField(help_text="Humidity percentage")
    ph = models.FloatField(help_text="Soil pH level")
    rainfall = models.FloatField(help_text="Rainfall in mm")

    # Prediction results
    status = models.CharField(
        max_length=20, choices=PREDICTION_STATUS, default="pending"
    )
    predicted_crops = models.JSONField(
        default=list, help_text="List of predicted crops with confidence scores"
    )
    confidence_score = models.FloatField(null=True, blank=True)
    model_version = models.CharField(max_length=50, default="v1.0")

    # Metadata
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["community_admin", "-requested_at"]),
            models.Index(fields=["sensor_set", "-requested_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        if self.sensor_set:
            source = self.sensor_set.name
        elif self.farmer:
            source = f"Manual by {self.farmer.get_full_name()}"
        else:
            source = "Unknown source"
        return f"Prediction {self.id} - {source} ({self.status})"

    @property
    def input_parameters(self):
        """Return input parameters as dictionary"""
        return {
            "N": self.nitrogen,
            "P": self.phosphorus,
            "K": self.potassium,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "ph": self.ph,
            "rainfall": self.rainfall,
        }

    @property
    def parsed_predicted_crops(self):
        """Return predicted_crops as a list of dictionaries with proper structure"""
        if not self.predicted_crops:
            return []

        # If it's already a list of dictionaries, return as is
        if isinstance(self.predicted_crops, list):
            return self.predicted_crops

        # If it's a string, try to parse it as JSON
        if isinstance(self.predicted_crops, str):
            try:
                return json.loads(self.predicted_crops)
            except (json.JSONDecodeError, ValueError):
                return []

        return []

    def get_top_predicted_crops(self, limit=3):
        """Get top predicted crops with confidence scores"""
        crops = self.parsed_predicted_crops
        if not crops:
            return []

        # Sort by confidence score if available
        sorted_crops = sorted(crops, key=lambda x: x.get("confidence", 0), reverse=True)
        return sorted_crops[:limit]


class CropRecommendation(models.Model):
    """Final crop recommendations based on predictions"""

    RECOMMENDATION_TYPE = [
        ("primary", "Primary Recommendation"),
        ("secondary", "Secondary Option"),
        ("alternative", "Alternative Choice"),
    ]

    prediction_request = models.ForeignKey(
        CropPredictionRequest, on_delete=models.CASCADE, related_name="recommendations"
    )
    crop_type = models.ForeignKey(CropType, on_delete=models.CASCADE)

    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE)
    confidence_score = models.FloatField(help_text="Confidence score 0-1")

    # Contextual information
    rationale = models.TextField(help_text="Why this crop is recommended")
    expected_yield = models.CharField(max_length=100, blank=True)
    risk_factors = models.JSONField(
        default=list, help_text="Potential risks for this crop"
    )

    # Regional context
    local_market_demand = models.CharField(
        max_length=20,
        choices=[
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        ],
        default="medium",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-confidence_score"]
        unique_together = ["prediction_request", "crop_type"]

    def __str__(self):
        return f"{self.crop_type.name} - {self.recommendation_type} ({self.confidence_score:.2f})"


class WeatherData(models.Model):
    """Weather data from external APIs for rainfall information"""

    region = models.CharField(max_length=100, default="Bhairahawa-Butwal")
    date = models.DateField()

    # Weather parameters
    temperature_max = models.FloatField()
    temperature_min = models.FloatField()
    humidity = models.FloatField()
    rainfall = models.FloatField(default=0.0)
    wind_speed = models.FloatField(null=True, blank=True)

    # Data source
    source_api = models.CharField(max_length=50, default="OpenWeatherMap")
    api_response = models.JSONField(null=True, blank=True, help_text="Raw API response")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["region", "date", "source_api"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.region} - {self.date} (Rainfall: {self.rainfall}mm)"
