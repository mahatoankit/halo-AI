"""
Enhanced Weather API Service using Open-Meteo
Fetches rainfall and humidity data for crop prediction
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Union, Any
import json


class EnhancedWeatherService:
    """Service to fetch weather data using Open-Meteo API (free, no API key required)"""

    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

        # Coordinates for Bhairahawa-Butwal region
        self.region_coords = {
            "Bhairahawa-Butwal": {"lat": 27.5057, "lon": 83.4163},
            "Bhairahawa": {"lat": 27.5057, "lon": 83.4163},
            "Butwal": {"lat": 27.6855, "lon": 83.4409},
            "default": {"lat": 27.5057, "lon": 83.4163},
        }

    def get_current_weather_data(
        self, region: str = "Bhairahawa-Butwal"
    ) -> Dict[str, Union[float, str]]:
        """
        Get current weather data for rainfall and humidity
        Returns: {"rainfall": mm, "humidity": %}
        """
        try:
            coords = self.region_coords.get(region, self.region_coords["default"])

            # Parameters for Open-Meteo API
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "hourly": ["rain", "relative_humidity_2m"],
                "forecast_days": 1,  # Get current day data
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Process hourly data
                hourly = data.get("hourly", {})
                rain_data = hourly.get("rain", [])
                humidity_data = hourly.get("relative_humidity_2m", [])

                if rain_data and humidity_data:
                    # Get current hour data (most recent)
                    current_rainfall = rain_data[0] if rain_data else 0.0
                    current_humidity = humidity_data[0] if humidity_data else 65.0

                    # Convert to daily values for crop prediction
                    # Rainfall: sum of current day hourly values
                    daily_rainfall = sum(rain_data) if rain_data else 0.0

                    # Humidity: average of current day hourly values
                    avg_humidity = (
                        sum(humidity_data) / len(humidity_data)
                        if humidity_data
                        else 65.0
                    )

                    return {
                        "rainfall": round(daily_rainfall, 1),
                        "humidity": round(avg_humidity, 1),
                        "region": region,
                        "source": "open-meteo",
                    }

            # Return default values if API fails
            return self._get_default_weather_data(region)

        except Exception as e:
            print(f"Error fetching weather data from Open-Meteo: {e}")
            return self._get_default_weather_data(region)

    def get_weekly_forecast(
        self, region: str = "Bhairahawa-Butwal"
    ) -> List[Dict[str, float]]:
        """Get 7-day weather forecast for the region"""
        try:
            coords = self.region_coords.get(region, self.region_coords["default"])

            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "daily": ["rain_sum", "relative_humidity_2m_mean"],
                "forecast_days": 7,
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                daily = data.get("daily", {})

                dates = daily.get("time", [])
                rainfall = daily.get("rain_sum", [])
                humidity = daily.get("relative_humidity_2m_mean", [])

                forecast = []
                for i, date in enumerate(dates):
                    if i < len(rainfall) and i < len(humidity):
                        forecast.append(
                            {
                                "date": date,
                                "rainfall": rainfall[i] or 0.0,
                                "humidity": humidity[i] or 65.0,
                            }
                        )

                return forecast

            return []

        except Exception as e:
            print(f"Error fetching weekly forecast: {e}")
            return []

    def get_historical_data(
        self, region: str = "Bhairahawa-Butwal", days_back: int = 30
    ) -> Dict[str, Union[float, int, str]]:
        """Get historical weather averages for the past N days"""
        try:
            coords = self.region_coords.get(region, self.region_coords["default"])

            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)

            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "daily": ["rain_sum", "relative_humidity_2m_mean"],
            }

            # Use archive API for historical data
            archive_url = "https://archive-api.open-meteo.com/v1/archive"
            response = requests.get(archive_url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                daily = data.get("daily", {})

                rainfall_data = daily.get("rain_sum", [])
                humidity_data = daily.get("relative_humidity_2m_mean", [])

                if rainfall_data and humidity_data:
                    # Calculate averages
                    avg_rainfall = sum(r for r in rainfall_data if r is not None) / len(
                        [r for r in rainfall_data if r is not None]
                    )
                    avg_humidity = sum(h for h in humidity_data if h is not None) / len(
                        [h for h in humidity_data if h is not None]
                    )

                    return {
                        "avg_rainfall": round(avg_rainfall, 1),
                        "avg_humidity": round(avg_humidity, 1),
                        "days_analyzed": days_back,
                        "region": region,
                    }

            return {
                "avg_rainfall": 22.5,
                "avg_humidity": 60.0,
                "days_analyzed": days_back,
                "region": region,
            }

        except Exception as e:
            print(f"Error fetching historical weather data: {e}")
            return {
                "avg_rainfall": 22.5,
                "avg_humidity": 60.0,
                "days_analyzed": days_back,
                "region": region,
            }

    def get_crop_season_weather(
        self, region: str = "Bhairahawa-Butwal", season: str = "kharif"
    ) -> Dict[str, Union[float, str]]:
        """
        Get weather data optimized for specific crop seasons
        Season types: kharif (monsoon), rabi (winter), zaid (summer)
        """
        current_weather = self.get_current_weather_data(region)

        # Season-specific adjustments for Bhairahawa region
        season_adjustments = {
            "kharif": {  # Monsoon season (June-October)
                "rainfall_multiplier": 1.5,
                "humidity_adjustment": 5.0,
            },
            "rabi": {  # Winter season (November-April)
                "rainfall_multiplier": 0.3,
                "humidity_adjustment": -10.0,
            },
            "zaid": {  # Summer season (March-June)
                "rainfall_multiplier": 0.5,
                "humidity_adjustment": -5.0,
            },
        }

        adjustments = season_adjustments.get(season, season_adjustments["kharif"])

        # Apply seasonal adjustments with proper type conversion
        rainfall_val = current_weather.get("rainfall", 22.5)
        humidity_val = current_weather.get("humidity", 60.0)

        # Ensure we have numeric values
        if isinstance(rainfall_val, str):
            try:
                rainfall_val = float(rainfall_val)
            except ValueError:
                rainfall_val = 22.5

        if isinstance(humidity_val, str):
            try:
                humidity_val = float(humidity_val)
            except ValueError:
                humidity_val = 60.0

        adjusted_rainfall = rainfall_val * adjustments["rainfall_multiplier"]
        adjusted_humidity = max(
            20, min(95, humidity_val + adjustments["humidity_adjustment"])
        )

        return {
            "rainfall": round(adjusted_rainfall, 1),
            "humidity": round(adjusted_humidity, 1),
            "season": season,
            "region": region,
            "source": "open-meteo-adjusted",
        }

    def _get_default_weather_data(self, region: str) -> Dict[str, Union[float, str]]:
        """Return default weather values based on region and season"""
        # Default values for Bhairahawa-Butwal region
        defaults = {
            "Bhairahawa-Butwal": {"rainfall": 22.5, "humidity": 60.0},
            "Bhairahawa": {"rainfall": 25.0, "humidity": 65.0},
            "Butwal": {"rainfall": 20.0, "humidity": 55.0},
        }

        region_defaults = defaults.get(region, defaults["Bhairahawa-Butwal"])

        return {
            "rainfall": region_defaults["rainfall"],
            "humidity": region_defaults["humidity"],
            "region": region,
            "source": "default",
        }

    def test_api_connection(self) -> bool:
        """Test if the Open-Meteo API is accessible"""
        try:
            test_params = {
                "latitude": 27.5057,
                "longitude": 83.4163,
                "hourly": ["temperature_2m"],
                "forecast_days": 1,
            }

            response = requests.get(self.base_url, params=test_params, timeout=5)
            return response.status_code == 200

        except Exception:
            return False


# Global instance
enhanced_weather_service = EnhancedWeatherService()


# Example usage and testing
if __name__ == "__main__":
    weather_service = EnhancedWeatherService()

    print("Testing Enhanced Weather Service...")
    print("=" * 50)

    # Test current weather
    current = weather_service.get_current_weather_data("Bhairahawa-Butwal")
    print(f"Current weather: {current}")

    # Test seasonal weather
    kharif_weather = weather_service.get_crop_season_weather(
        "Bhairahawa-Butwal", "kharif"
    )
    print(f"Kharif season weather: {kharif_weather}")

    # Test API connection
    api_status = weather_service.test_api_connection()
    print(f"API connection: {'✅ Connected' if api_status else '❌ Failed'}")
