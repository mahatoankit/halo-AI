#!/usr/bin/env python3
"""
Test script to verify real-time data changes in the frontend
"""

import time
import requests
import json
from datetime import datetime


def test_api_endpoint():
    """Test the Django API endpoint"""
    url = "http://localhost:8000/crop-prediction/api/real-time-data/?region=Bhairahawa-Butwal"

    print("🔄 Testing API endpoint...")
    print(f"URL: {url}")

    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2))

            if data.get("status") == "success":
                sensor_data = data.get("data", {})
                print(f"\n📊 Sensor Data Summary:")
                print(f"  pH: {sensor_data.get('ph')}")
                print(f"  Temperature: {sensor_data.get('temperature')}°C")
                print(f"  Humidity: {sensor_data.get('humidity')}%")
                print(f"  Rainfall: {sensor_data.get('rainfall')}mm")
                print(f"  Sensor ID: {sensor_data.get('sensor_id')}")
                print(f"  Timestamp: {sensor_data.get('timestamp')}")

                return sensor_data
            else:
                print(f"❌ API Error: {data.get('message')}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None


def monitor_changes(duration=60, interval=5):
    """Monitor API for changes over time"""
    print(f"\n🔍 Monitoring API for {duration} seconds (checking every {interval}s)...")

    start_time = time.time()
    previous_data = None

    while time.time() - start_time < duration:
        current_data = test_api_endpoint()

        if current_data and previous_data:
            # Check for changes
            changes = []
            for key in ["ph", "temperature", "humidity", "rainfall"]:
                if current_data.get(key) != previous_data.get(key):
                    changes.append(
                        f"{key}: {previous_data.get(key)} → {current_data.get(key)}"
                    )

            if changes:
                print(
                    f"\n🔄 Changes detected at {datetime.now().strftime('%H:%M:%S')}:"
                )
                for change in changes:
                    print(f"  • {change}")
            else:
                print(f"📊 No changes at {datetime.now().strftime('%H:%M:%S')}")

        previous_data = current_data
        time.sleep(interval)


if __name__ == "__main__":
    print("🧪 Real-Time Data Test Script")
    print("=" * 40)

    # Test once
    test_api_endpoint()

    # Ask user if they want to monitor
    try:
        choice = input("\n🔍 Monitor for changes? (y/N): ").lower().strip()
        if choice in ["y", "yes"]:
            monitor_changes()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")

    print("\n✅ Test completed")
