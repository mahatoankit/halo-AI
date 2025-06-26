from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

User = get_user_model()


class IoTDevice(models.Model):
    """
    IoT Device Model - Individual sensor devices assigned to users
    Supports role-based access and location-aware data management
    """

    DEVICE_STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("maintenance", "Under Maintenance"),
        ("error", "Error/Malfunction"),
        ("offline", "Offline"),
    ]

    DEVICE_TYPE_CHOICES = [
        ("soil_sensor", "Soil NPK Sensor"),
        ("weather_station", "Weather Station"),
        ("ph_meter", "pH Meter"),
        ("moisture_sensor", "Soil Moisture Sensor"),
        ("temperature_sensor", "Temperature Sensor"),
        ("humidity_sensor", "Humidity Sensor"),
        ("light_sensor", "Light Intensity Sensor"),
        ("multi_sensor", "Multi-parameter Sensor"),
    ]

    # Primary identifiers
    device_id = models.CharField(
        max_length=100, unique=True, help_text="Unique device identifier"
    )
    name = models.CharField(max_length=200, help_text="Human-readable device name")

    # User assignment - the core of role-based access
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_devices",
        help_text="User responsible for this device",
    )

    # Device specifications
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    firmware_version = models.CharField(max_length=50, blank=True, null=True)

    # Location information - hierarchical and precise
    location_name = models.CharField(
        max_length=200, help_text="Human-readable location"
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    elevation = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Elevation in meters above sea level",
    )

    # Administrative location hierarchy
    region = models.CharField(max_length=100, help_text="Administrative region")
    district = models.CharField(max_length=100, blank=True, null=True)
    municipality = models.CharField(max_length=100, blank=True, null=True)
    ward_number = models.PositiveIntegerField(null=True, blank=True)

    # Status and configuration
    status = models.CharField(
        max_length=20, choices=DEVICE_STATUS_CHOICES, default="active"
    )
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(
        default=False, help_text="Whether data is publicly accessible"
    )

    # Technical specifications (stored as JSON for flexibility)
    technical_specs = models.JSONField(
        default=dict, blank=True, help_text="Technical specifications and configuration"
    )

    # Installation and maintenance
    installation_date = models.DateTimeField(null=True, blank=True)
    last_maintenance = models.DateTimeField(null=True, blank=True)
    next_maintenance = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "IoT Device"
        verbose_name_plural = "IoT Devices"
        indexes = [
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["region", "status"]),
            models.Index(fields=["device_type", "status"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.device_id}) - {self.assigned_to.username}"

    @property
    def location_coordinates(self):
        """Get coordinates as tuple"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None

    @property
    def full_location(self):
        """Get full hierarchical location string"""
        parts = [self.location_name]
        if self.municipality:
            parts.append(self.municipality)
        if self.district:
            parts.append(self.district)
        parts.append(self.region)
        return ", ".join(parts)

    def can_be_accessed_by(self, user):
        """Check if a user can access this device's data"""
        # Global admin can access all devices
        if user.is_admin:
            return True

        # Device owner can access their own devices
        if self.assigned_to == user:
            return True

        # Community admin can access devices in their region
        if user.is_community_admin and user.assigned_region == self.region:
            return True

        # Public devices can be accessed by anyone
        if self.is_public:
            return True

        return False


class SensorData(models.Model):
    """
    Sensor Data Model - Time-series data from IoT devices
    Optimized for high-frequency data collection and querying
    """

    DATA_QUALITY_CHOICES = [
        ("excellent", "Excellent (>95%)"),
        ("good", "Good (85-95%)"),
        ("fair", "Fair (70-85%)"),
        ("poor", "Poor (<70%)"),
    ]

    # Device relationship
    device = models.ForeignKey(
        IoTDevice, on_delete=models.CASCADE, related_name="sensor_readings"
    )

    # Timestamp with timezone support
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    reading_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual time when reading was taken (if different from upload time)",
    )

    # Core agricultural parameters
    nitrogen = models.FloatField(
        null=True, blank=True, help_text="Nitrogen content (ppm)"
    )
    phosphorus = models.FloatField(
        null=True, blank=True, help_text="Phosphorus content (ppm)"
    )
    potassium = models.FloatField(
        null=True, blank=True, help_text="Potassium content (ppm)"
    )

    # Environmental parameters
    temperature = models.FloatField(null=True, blank=True, help_text="Temperature (°C)")
    humidity = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Relative humidity (%)",
    )
    ph = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(14)],
        help_text="pH level",
    )

    # Additional environmental data
    soil_moisture = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Soil moisture content (%)",
    )
    light_intensity = models.FloatField(
        null=True, blank=True, help_text="Light intensity (lux)"
    )
    rainfall = models.FloatField(null=True, blank=True, help_text="Rainfall (mm)")
    wind_speed = models.FloatField(null=True, blank=True, help_text="Wind speed (km/h)")
    barometric_pressure = models.FloatField(
        null=True, blank=True, help_text="Atmospheric pressure (hPa)"
    )

    # Data quality and validation
    data_quality = models.CharField(
        max_length=20, choices=DATA_QUALITY_CHOICES, default="good"
    )
    quality_score = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Data quality score (0-1)",
    )
    is_validated = models.BooleanField(default=False)
    validation_notes = models.TextField(blank=True, null=True)

    # Raw data storage for debugging
    raw_data = models.JSONField(
        default=dict, blank=True, help_text="Raw sensor data for debugging purposes"
    )

    # Battery and device health
    battery_level = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Device battery level (%)",
    )
    signal_strength = models.FloatField(
        null=True, blank=True, help_text="Signal strength (dBm)"
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Sensor Reading"
        verbose_name_plural = "Sensor Readings"
        indexes = [
            models.Index(fields=["device", "-timestamp"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["device", "data_quality"]),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @property
    def npk_values(self):
        """Get NPK values as dictionary"""
        return {
            "nitrogen": self.nitrogen,
            "phosphorus": self.phosphorus,
            "potassium": self.potassium,
        }

    @property
    def environmental_data(self):
        """Get environmental parameters as dictionary"""
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "ph": self.ph,
            "soil_moisture": self.soil_moisture,
            "light_intensity": self.light_intensity,
            "rainfall": self.rainfall,
        }


class DeviceGroup(models.Model):
    """
    Device Group Model - For organizing devices into logical groups
    Enables bulk management and hierarchical organization
    """

    GROUP_TYPE_CHOICES = [
        ("farm", "Farm"),
        ("field", "Field"),
        ("greenhouse", "Greenhouse"),
        ("research", "Research Site"),
        ("demo", "Demo Site"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    group_type = models.CharField(max_length=50, choices=GROUP_TYPE_CHOICES)

    # Group ownership and permissions
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_device_groups"
    )
    members = models.ManyToManyField(User, related_name="device_groups", blank=True)

    # Devices in this group
    devices = models.ManyToManyField(
        IoTDevice, related_name="device_groups", blank=True
    )

    # Location (can be inherited by devices)
    location_name = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=7, null=True, blank=True
    )
    region = models.CharField(max_length=100, blank=True, null=True)

    # Settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Device Group"
        verbose_name_plural = "Device Groups"

    def __str__(self):
        return f"{self.name} ({self.group_type}) - {self.owner.username}"

    def get_device_count(self):
        """Get number of devices in this group"""
        return self.devices.count()

    def get_active_device_count(self):
        """Get number of active devices in this group"""
        return self.devices.filter(status="active").count()


class DataAlert(models.Model):
    """
    Data Alert Model - For monitoring and alerting on sensor data
    Supports threshold-based alerts and anomaly detection
    """

    ALERT_TYPE_CHOICES = [
        ("threshold", "Threshold Alert"),
        ("anomaly", "Anomaly Detection"),
        ("device_offline", "Device Offline"),
        ("low_battery", "Low Battery"),
        ("data_quality", "Data Quality Issue"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("acknowledged", "Acknowledged"),
        ("resolved", "Resolved"),
        ("false_positive", "False Positive"),
    ]

    # Alert identification
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(
        max_length=20, choices=SEVERITY_CHOICES, default="medium"
    )

    # Related objects
    device = models.ForeignKey(
        IoTDevice, on_delete=models.CASCADE, related_name="alerts"
    )
    sensor_data = models.ForeignKey(
        SensorData,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Related sensor reading that triggered the alert",
    )

    # Alert details
    threshold_value = models.FloatField(null=True, blank=True)
    actual_value = models.FloatField(null=True, blank=True)
    parameter = models.CharField(max_length=50, blank=True, null=True)

    # Status and handling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_alerts",
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Notification settings
    recipients = models.ManyToManyField(
        User, related_name="received_alerts", blank=True
    )
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Data Alert"
        verbose_name_plural = "Data Alerts"
        indexes = [
            models.Index(fields=["device", "status"]),
            models.Index(fields=["severity", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.device.name} ({self.severity})"


# Legacy model for backward compatibility - will be deprecated
class IoTSensorSet(models.Model):
    """
    DEPRECATED: Legacy IoT Sensor Set model
    Use IoTDevice and DeviceGroup models instead
    """

    SENSOR_STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("maintenance", "Under Maintenance"),
        ("error", "Error/Malfunction"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Sensor set identifier")
    community_admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="managed_sensors",
        limit_choices_to={"role": "community_admin"},
    )

    # Location details
    location_name = models.CharField(
        max_length=200, help_text="Human-readable location"
    )
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    region = models.CharField(max_length=100, default="Bhairahawa-Butwal")

    # Status and configuration
    status = models.CharField(
        max_length=20, choices=SENSOR_STATUS_CHOICES, default="active"
    )
    firebase_path = models.CharField(
        max_length=200, unique=True, help_text="Firebase database path"
    )

    # Default NPK values for MVP (can be overridden by actual sensors later)
    default_nitrogen = models.FloatField(
        default=85.0, help_text="Default N value for region"
    )
    default_phosphorus = models.FloatField(
        default=50.0, help_text="Default P value for region"
    )
    default_potassium = models.FloatField(
        default=40.0, help_text="Default K value for region"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "IoT Sensor Set (Legacy)"
        verbose_name_plural = "IoT Sensor Sets (Legacy)"

    def __str__(self):
        return f"{self.name} - {self.location_name} ({self.community_admin.username})"

    def save(self, *args, **kwargs):
        if not self.firebase_path:
            region = (
                getattr(self.community_admin, "assigned_region", "default") or "default"
            )
            self.firebase_path = f"sensors/{region}/{self.id}"
        super().save(*args, **kwargs)


# Legacy model for backward compatibility - will be deprecated
class SensorReading(models.Model):
    """
    DEPRECATED: Legacy sensor readings model
    Use SensorData model instead
    """

    SENSOR_TYPES = [
        ("temperature", "Temperature"),
        ("humidity", "Humidity"),
        ("ph", "pH Level"),
        ("soil_moisture", "Soil Moisture"),
        ("light", "Light Intensity"),
    ]

    sensor_set = models.ForeignKey(
        IoTSensorSet, on_delete=models.CASCADE, related_name="readings"
    )
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=20, default="")

    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    firebase_timestamp = models.CharField(max_length=50, null=True, blank=True)
    quality_score = models.FloatField(
        default=1.0, help_text="Data quality indicator (0-1)"
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Sensor Reading (Legacy)"
        verbose_name_plural = "Sensor Readings (Legacy)"

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["sensor_set", "sensor_type", "-timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.sensor_set.name} - {self.sensor_type}: {self.value} {self.unit}"
