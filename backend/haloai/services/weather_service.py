"""
Weather API Service
Fetches weather data for crop prediction, particularly rainfall information
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from django.conf import settings
from apps.crops.models import WeatherData


class WeatherAPIService:
    """Service to fetch weather data from external APIs"""

    def __init__(self):
        self.api_key = getattr(settings, "OPENWEATHER_API_KEY", None)
        self.base_url = "http://api.openweathermap.org/data/2.5"

        # Coordinates for Bhairahawa-Butwal region
        self.region_coords = {
            "Bhairahawa-Butwal": {"lat": 27.5, "lon": 83.45},
            "default": {"lat": 27.5, "lon": 83.45},
        }

    def get_current_weather(
        self, region: str = "Bhairahawa-Butwal"
    ) -> Dict[str, float]:
        """Get current weather data for the region"""
        try:
            coords = self.region_coords.get(region, self.region_coords["default"])

            if self.api_key:
                # Make API call to OpenWeatherMap
                url = f"{self.base_url}/weather"
                params = {
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "appid": self.api_key,
                    "units": "metric",
                }

                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    weather_data = {
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "rainfall": data.get("rain", {}).get("1h", 0.0)
                        * 24,  # Convert to daily estimate
                        "pressure": data["main"]["pressure"],
                        "wind_speed": data["wind"]["speed"],
                    }

                    # Store in database
                    self.store_weather_data(region, weather_data, response.json())

                    return weather_data

            # Fallback to regional defaults if API fails
            return self.get_regional_defaults(region)

        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self.get_regional_defaults(region)

    def get_regional_defaults(self, region: str) -> Dict[str, float]:
        """Get default weather values for the region"""
        # Based on historical data for Bhairahawa-Butwal region
        defaults = {
            "Bhairahawa-Butwal": {
                "temperature": 25.0,
                "humidity": 75.0,
                "rainfall": 180.0,  # Annual average distributed
                "pressure": 1013.25,
                "wind_speed": 5.0,
            }
        }

        return defaults.get(region, defaults["Bhairahawa-Butwal"])

    def store_weather_data(self, region: str, weather_data: Dict, raw_response: Dict):
        """Store weather data in database"""
        try:
            today = datetime.now().date()

            WeatherData.objects.update_or_create(
                region=region,
                date=today,
                source_api="OpenWeatherMap",
                defaults={
                    "temperature_max": weather_data["temperature"] + 3,  # Estimate max
                    "temperature_min": weather_data["temperature"] - 3,  # Estimate min
                    "humidity": weather_data["humidity"],
                    "rainfall": weather_data["rainfall"],
                    "wind_speed": weather_data.get("wind_speed", 0),
                    "api_response": raw_response,
                },
            )
        except Exception as e:
            print(f"Error storing weather data: {e}")

    def get_historical_weather(self, region: str, days: int = 7):
        """Get historical weather data from database"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        return WeatherData.objects.filter(
            region=region, date__range=[start_date, end_date]
        ).order_by("-date")

    def get_forecast(self, region: str = "Bhairahawa-Butwal") -> Dict:
        """Get weather forecast (5-day forecast)"""
        try:
            coords = self.region_coords.get(region, self.region_coords["default"])

            if self.api_key:
                url = f"{self.base_url}/forecast"
                params = {
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "appid": self.api_key,
                    "units": "metric",
                }

                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    # Process forecast data
                    forecast = []
                    for item in data["list"][:5]:  # Next 5 periods
                        forecast.append(
                            {
                                "datetime": item["dt_txt"],
                                "temperature": item["main"]["temp"],
                                "humidity": item["main"]["humidity"],
                                "rainfall": item.get("rain", {}).get("3h", 0.0),
                                "description": item["weather"][0]["description"],
                            }
                        )

                    return {
                        "region": region,
                        "forecast": forecast,
                        "updated_at": datetime.now().isoformat(),
                    }

            # Fallback forecast
            return self.get_default_forecast(region)

        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return self.get_default_forecast(region)

    def get_default_forecast(self, region: str) -> Dict:
        """Generate default forecast based on regional patterns"""
        base_weather = self.get_regional_defaults(region)

        forecast = []
        for i in range(5):
            # Add some variation to base values
            temp_variation = (-2 + i * 1) if i < 3 else (1 - (i - 3))
            forecast.append(
                {
                    "datetime": (datetime.now() + timedelta(days=i)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "temperature": base_weather["temperature"] + temp_variation,
                    "humidity": base_weather["humidity"] + (-5 + i * 2),
                    "rainfall": base_weather["rainfall"] * (0.8 + i * 0.1),
                    "description": "Partly cloudy",
                }
            )

        return {
            "region": region,
            "forecast": forecast,
            "updated_at": datetime.now().isoformat(),
            "source": "default_regional_pattern",
        }
