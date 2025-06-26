"""
Regional configuration settings for Halo AI
"""

import os
from django.conf import settings


class RegionalConfig:
    """Configuration for regional soil and climate defaults"""

    @staticmethod
    def get_soil_defaults(region="bhairahawa"):
        """Get soil parameter defaults for a region"""
        if region.lower() == "bhairahawa":
            defaults_str = os.getenv(
                "REGION_SOIL_DEFAULTS_BHAIRAHAWA", "30,22.5,60,6.0"
            )
            climate_str = os.getenv("REGION_CLIMATE_DEFAULTS_BHAIRAHAWA", "25,70,150")

            try:
                n, p, k, ph = map(float, defaults_str.split(","))
                temp, humidity, rainfall = map(float, climate_str.split(","))

                return {
                    "nitrogen": n,
                    "phosphorus": p,
                    "potassium": k,
                    "ph": ph,
                    "temperature": temp,
                    "humidity": humidity,
                    "rainfall": rainfall,
                }
            except (ValueError, IndexError):
                # Fallback to hardcoded defaults
                return {
                    "nitrogen": 30.0,
                    "phosphorus": 22.5,
                    "potassium": 60.0,
                    "ph": 6.0,
                    "temperature": 25.0,
                    "humidity": 70.0,
                    "rainfall": 150.0,
                }

        # Default values for other regions
        return {
            "nitrogen": 25.0,
            "phosphorus": 20.0,
            "potassium": 50.0,
            "ph": 6.5,
            "temperature": 22.0,
            "humidity": 65.0,
            "rainfall": 120.0,
        }

    @staticmethod
    def get_parameter_ranges():
        """Get validation ranges for soil parameters"""

        def parse_range(env_var, default_range):
            try:
                min_val, max_val = map(
                    float, os.getenv(env_var, default_range).split(",")
                )
                return min_val, max_val
            except (ValueError, IndexError):
                return map(float, default_range.split(","))

        return {
            "nitrogen": parse_range("NITROGEN_RANGE", "0,140"),
            "phosphorus": parse_range("PHOSPHORUS_RANGE", "5,145"),
            "potassium": parse_range("POTASSIUM_RANGE", "5,205"),
            "ph": parse_range("PH_RANGE", "3.5,10.0"),
            "temperature": parse_range("TEMPERATURE_RANGE", "0,50"),
            "humidity": parse_range("HUMIDITY_RANGE", "14,100"),
            "rainfall": parse_range("RAINFALL_RANGE", "20,300"),
        }

    @staticmethod
    def get_iot_sensor_format():
        """Get IoT sensor data format"""
        format_str = os.getenv("IOT_SENSOR_FORMAT", "ph,temperature")
        example_str = os.getenv("IOT_SENSOR_EXAMPLE", "6.5,25.0")

        return {
            "format": format_str.split(","),
            "example": example_str,
        }

    @staticmethod
    def get_weather_data_format():
        """Get weather data format"""
        format_str = os.getenv("WEATHER_DATA_FORMAT", "rainfall,humidity")
        example_str = os.getenv("WEATHER_DATA_EXAMPLE", "150,70")

        return {
            "format": format_str.split(","),
            "example": example_str,
        }


# Helper functions for templates and views
def get_regional_defaults(region="bhairahawa"):
    """Template helper to get regional defaults"""
    return RegionalConfig.get_soil_defaults(region)


def validate_soil_parameters(params):
    """Validate soil parameters against regional ranges"""
    ranges = RegionalConfig.get_parameter_ranges()
    errors = []

    for param, value in params.items():
        if param in ranges:
            min_val, max_val = ranges[param]
            if not min_val <= float(value) <= max_val:
                errors.append(
                    f"{param.title()} must be between {min_val} and {max_val}"
                )

    return errors
