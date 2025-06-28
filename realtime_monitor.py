#!/usr/bin/env python3
"""
Real-time IoT Data Monitoring Script
Demonstrates continuous sensor data fetching from the enhanced backend
"""

import requests
import time
import json
from datetime import datetime
import sys


class RealtimeIoTMonitor:
    def __init__(self, base_url="http://localhost:8000/sensors/api/enhanced"):
        self.base_url = base_url
        self.running = False

    def fetch_live_data(self, sensor_id="SENSOR_001"):
        """Fetch live sensor data (bypasses cache)"""
        try:
            response = requests.get(f"{self.base_url}/live/?sensor_id={sensor_id}")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fetch_cached_data(self, sensor_id="SENSOR_001"):
        """Fetch cached sensor data for comparison"""
        try:
            response = requests.get(f"{self.base_url}/sensor/?sensor_id={sensor_id}")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def start_monitoring(self, sensor_id="SENSOR_001", interval=3):
        """Start continuous monitoring"""
        print(f"🔴 Starting real-time monitoring for sensor: {sensor_id}")
        print(f"📡 Update interval: {interval} seconds")
        print("=" * 80)

        self.running = True
        count = 0

        try:
            while self.running:
                count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")

                # Fetch live data
                live_data = self.fetch_live_data(sensor_id)

                if live_data.get("status") == "success":
                    reading = live_data["data"]["reading"]

                    print(f"[{timestamp}] Update #{count:03d}")
                    print(f"  🌡️  Temperature: {reading['temperature']}°C")
                    print(f"  🌱  Soil Temp:   {reading['soil_temperature']}°C")
                    print(f"  💧  pH Level:    {reading['ph']}")
                    print(f"  💨  Humidity:    {reading['humidity']}%")
                    print(f"  📊  Status:      {reading['status']}")
                    print(f"  🕐  Data Time:   {reading['timestamp'][:19]}")

                    # Check if data is being updated
                    if count > 1:
                        print(
                            f"  🔄  Cache Used:   {live_data['data']['metadata']['cache_used']}"
                        )

                    print("-" * 60)

                else:
                    print(
                        f"[{timestamp}] ❌ Error: {live_data.get('message', 'Unknown error')}"
                    )

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        finally:
            self.running = False

    def compare_live_vs_cached(self, sensor_id="SENSOR_001"):
        """Compare live data vs cached data"""
        print(f"🔍 Comparing LIVE vs CACHED data for sensor: {sensor_id}")
        print("=" * 80)

        # Fetch both
        live_data = self.fetch_live_data(sensor_id)
        cached_data = self.fetch_cached_data(sensor_id)

        if (
            live_data.get("status") == "success"
            and cached_data.get("status") == "success"
        ):
            live_reading = live_data["data"]["reading"]
            cached_reading = cached_data["data"]["reading"]

            print("LIVE DATA (bypasses cache):")
            print(f"  Temperature: {live_reading['temperature']}°C")
            print(f"  pH:          {live_reading['ph']}")
            print(f"  Timestamp:   {live_reading['timestamp']}")
            print(f"  Cache Used:  {live_data['data']['metadata']['cache_used']}")

            print("\nCACHED DATA (may use cache):")
            print(f"  Temperature: {cached_reading['temperature']}°C")
            print(f"  pH:          {cached_reading['ph']}")
            print(f"  Timestamp:   {cached_reading['timestamp']}")
            print(f"  Cache Used:  {cached_data['data']['metadata']['cache_used']}")

            # Check if timestamps differ
            if live_reading["timestamp"] != cached_reading["timestamp"]:
                print("\n✅ Data timestamps differ - live data is fresher!")
            else:
                print("\n⚡ Data timestamps match - cached data is recent")
        else:
            print("❌ Error fetching data for comparison")


def main():
    monitor = RealtimeIoTMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        sensor_id = sys.argv[2] if len(sys.argv) > 2 else "SENSOR_001"

        if command == "monitor":
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 3
            monitor.start_monitoring(sensor_id, interval)
        elif command == "compare":
            monitor.compare_live_vs_cached(sensor_id)
        else:
            print(
                "Usage: python realtime_monitor.py [monitor|compare] [sensor_id] [interval]"
            )
    else:
        print("🚀 Real-time IoT Data Monitor")
        print("\nUsage:")
        print("  python realtime_monitor.py monitor [sensor_id] [interval]")
        print("  python realtime_monitor.py compare [sensor_id]")
        print("\nExamples:")
        print("  python realtime_monitor.py monitor SENSOR_001 2")
        print("  python realtime_monitor.py compare bhairahawa_farm_1")
        print("\nDefault sensor: SENSOR_001, Default interval: 3 seconds")


if __name__ == "__main__":
    main()
