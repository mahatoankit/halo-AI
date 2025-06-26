"""
IoT Sensor Data Simulator
Simulates real sensor data for testing Firebase integration
"""

import time
import random
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List
from services.firebase_service import firebase_iot_service


class SensorSimulator:
    """Simulates various agricultural sensors"""

    def __init__(self):
        self.running = False
        self.farms = [
            {"id": "farm_001", "location": "Bhaktapur", "crops": ["rice", "wheat"]},
            {
                "id": "farm_002",
                "location": "Lalitpur",
                "crops": ["maize", "vegetables"],
            },
            {"id": "farm_003", "location": "Kathmandu", "crops": ["tomato", "potato"]},
        ]

    def generate_soil_sensor_data(self) -> Dict[str, Any]:
        """Generate realistic soil sensor data"""
        return {
            "moisture": round(random.uniform(20, 80), 2),  # Percentage
            "ph": round(random.uniform(6.0, 8.0), 2),
            "nitrogen": round(random.uniform(10, 50), 2),  # mg/kg
            "phosphorus": round(random.uniform(5, 30), 2),  # mg/kg
            "potassium": round(random.uniform(50, 200), 2),  # mg/kg
            "temperature": round(random.uniform(15, 35), 2),  # Celsius
            "conductivity": round(random.uniform(100, 1000), 2),  # μS/cm
        }

    def generate_weather_sensor_data(self) -> Dict[str, Any]:
        """Generate weather sensor data"""
        return {
            "temperature": round(random.uniform(10, 35), 2),  # Celsius
            "humidity": round(random.uniform(30, 90), 2),  # Percentage
            "pressure": round(random.uniform(950, 1050), 2),  # hPa
            "rainfall": round(random.uniform(0, 10), 2),  # mm
            "wind_speed": round(random.uniform(0, 15), 2),  # km/h
            "wind_direction": random.choice(
                ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            ),
            "solar_radiation": round(random.uniform(0, 1000), 2),  # W/m²
            "uv_index": round(random.uniform(0, 11), 1),
        }

    def generate_crop_sensor_data(self) -> Dict[str, Any]:
        """Generate crop monitoring sensor data"""
        return {
            "leaf_wetness": round(random.uniform(0, 100), 2),  # Percentage
            "stem_diameter": round(random.uniform(0.5, 3.0), 2),  # cm
            "plant_height": round(random.uniform(10, 150), 2),  # cm
            "chlorophyll_content": round(random.uniform(20, 60), 2),  # SPAD units
            "growth_stage": random.choice(
                ["seedling", "vegetative", "flowering", "fruiting", "mature"]
            ),
        }

    def generate_irrigation_sensor_data(self) -> Dict[str, Any]:
        """Generate irrigation system sensor data"""
        return {
            "water_level": round(random.uniform(0, 100), 2),  # Percentage
            "water_flow": round(random.uniform(0, 50), 2),  # L/min
            "pump_status": random.choice(["on", "off"]),
            "valve_position": round(random.uniform(0, 100), 2),  # Percentage open
            "water_quality_ec": round(random.uniform(0.1, 2.0), 3),  # dS/m
            "water_ph": round(random.uniform(6.5, 8.5), 2),
        }

    def simulate_sensor_reading(self, farm_id: str, sensor_type: str):
        """Simulate a single sensor reading"""
        try:
            if sensor_type == "soil":
                data = self.generate_soil_sensor_data()
            elif sensor_type == "weather":
                data = self.generate_weather_sensor_data()
            elif sensor_type == "crop":
                data = self.generate_crop_sensor_data()
            elif sensor_type == "irrigation":
                data = self.generate_irrigation_sensor_data()
            else:
                return False

            # Store in Firebase
            success = firebase_iot_service.store_sensor_data(farm_id, sensor_type, data)

            if success:
                print(f"✅ {sensor_type.title()} data stored for {farm_id}: {data}")
            else:
                print(f"❌ Failed to store {sensor_type} data for {farm_id}")

            return success

        except Exception as e:
            print(f"Error simulating {sensor_type} sensor for {farm_id}: {e}")
            return False

    def simulate_weather_for_location(self, location: str):
        """Simulate weather data for a location"""
        try:
            weather_data = self.generate_weather_sensor_data()
            success = firebase_iot_service.store_weather_data(location, weather_data)

            if success:
                print(f"🌤️ Weather data stored for {location}: {weather_data}")
            else:
                print(f"❌ Failed to store weather data for {location}")

            return success

        except Exception as e:
            print(f"Error simulating weather for {location}: {e}")
            return False

    def run_simulation_cycle(self):
        """Run one complete simulation cycle for all farms"""
        sensor_types = ["soil", "weather", "crop", "irrigation"]

        for farm in self.farms:
            farm_id = farm["id"]
            location = farm["location"]

            # Generate sensor data for each type
            for sensor_type in sensor_types:
                self.simulate_sensor_reading(farm_id, sensor_type)
                time.sleep(0.5)  # Small delay between sensors

            # Generate weather data for the location
            self.simulate_weather_for_location(location)

            print(f"📊 Completed simulation cycle for {farm_id}")
            print("-" * 50)

    def start_continuous_simulation(self, interval_seconds: int = 30):
        """Start continuous sensor simulation"""
        self.running = True
        print(f"🚀 Starting IoT sensor simulation (every {interval_seconds}s)")
        print("=" * 60)

        try:
            while self.running:
                self.run_simulation_cycle()
                print(f"💤 Waiting {interval_seconds} seconds for next cycle...")
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\n🛑 Simulation stopped by user")
        except Exception as e:
            print(f"❌ Simulation error: {e}")
        finally:
            self.running = False

    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        print("🛑 Simulation stopped")

    def run_single_test(self):
        """Run a single test simulation"""
        print("🧪 Running single test simulation...")
        print("=" * 40)

        # Test each farm with one sensor reading
        for farm in self.farms:
            farm_id = farm["id"]

            # Test soil sensor
            self.simulate_sensor_reading(farm_id, "soil")

            # Test weather for location
            self.simulate_weather_for_location(farm["location"])

            print(f"✅ Test completed for {farm_id}")
            print("-" * 30)


# Create global simulator instance
sensor_simulator = SensorSimulator()


def start_sensor_simulation(interval: int = 60):
    """Start sensor simulation in background thread"""

    def run():
        sensor_simulator.start_continuous_simulation(interval)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread


def run_sensor_test():
    """Run a quick sensor test"""
    sensor_simulator.run_single_test()


# Example usage functions for management commands
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_sensor_test()
        elif sys.argv[1] == "continuous":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            sensor_simulator.start_continuous_simulation(interval)
    else:
        print("Usage: python iot_simulator.py [test|continuous] [interval_seconds]")
