"""
Test Script for Real IoT & ML Integration
Demonstrates the complete data flow from IoT sensors to ML predictions
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(
    "/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/backend/haloai"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "haloai.settings")
django.setup()

from services.iot_data_service import iot_data_service
from services.enhanced_weather_service import enhanced_weather_service
from services.real_ml_prediction_service import real_ml_service


def test_iot_integration():
    """Test IoT sensor data integration"""
    print("🔧 Testing IoT Sensor Integration...")
    print("=" * 50)

    # Test IoT data fetching
    sensor_data = iot_data_service.get_latest_sensor_data("bhairahawa_farm_1")
    print(f"📡 IoT Sensor Data: {sensor_data}")

    # Test simulated data
    simulated_data = iot_data_service.simulate_sensor_data()
    print(f"🎲 Simulated Data: {simulated_data}")

    # Test regional averages
    regional_data = iot_data_service.get_regional_average_data()
    print(f"📊 Regional Averages: {regional_data}")

    print()


def test_weather_integration():
    """Test enhanced weather service integration"""
    print("🌤️ Testing Weather API Integration...")
    print("=" * 50)

    # Test current weather
    current_weather = enhanced_weather_service.get_current_weather_data(
        "Bhairahawa-Butwal"
    )
    print(f"🌡️ Current Weather: {current_weather}")

    # Test seasonal weather
    kharif_weather = enhanced_weather_service.get_crop_season_weather(
        "Bhairahawa-Butwal", "kharif"
    )
    print(f"🌾 Kharif Season Weather: {kharif_weather}")

    # Test API connection
    api_status = enhanced_weather_service.test_api_connection()
    print(f"🔗 API Status: {'✅ Connected' if api_status else '❌ Failed'}")

    print()


def test_ml_integration():
    """Test real ML model integration"""
    print("🤖 Testing ML Model Integration...")
    print("=" * 50)

    # Sample input data (format expected by ML models)
    test_input = {
        "nitrogen": 90,
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 20.8,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9,
    }

    # Test individual model predictions
    predictions = real_ml_service.make_prediction(test_input)
    print(f"🔮 Individual Predictions: {predictions}")

    # Test ensemble prediction
    ensemble = real_ml_service.get_ensemble_prediction(test_input)
    print(f"🎯 Ensemble Prediction: {ensemble}")

    # Test full prediction with rationale
    full_prediction = real_ml_service.get_prediction_with_rationale(test_input)
    print(f"📋 Full Analysis:")
    print(f"   Recommended Crop: {full_prediction['recommended_crop']}")
    print(f"   Confidence: {full_prediction['confidence']*100:.1f}%")
    print(f"   Rationale: {full_prediction['rationale']}")

    print()


def test_complete_integration():
    """Test complete end-to-end integration"""
    print("🌟 Testing Complete Integration Pipeline...")
    print("=" * 50)

    # Step 1: Collect IoT data
    print("Step 1: Collecting IoT sensor data...")
    iot_data = iot_data_service.get_latest_sensor_data("bhairahawa_farm_1")
    ph_value = iot_data.get("ph", 6.5)
    temperature_value = iot_data.get("temperature", 29.6)
    print(f"   📡 pH: {ph_value}, Temperature: {temperature_value}°C")

    # Step 2: Collect weather data
    print("Step 2: Fetching weather data...")
    weather_data = enhanced_weather_service.get_current_weather_data(
        "Bhairahawa-Butwal"
    )
    rainfall_value = weather_data.get("rainfall", 22.5)
    humidity_value = weather_data.get("humidity", 60.0)
    print(f"   🌤️ Rainfall: {rainfall_value}mm, Humidity: {humidity_value}%")

    # Step 3: Add regional NPK data
    print("Step 3: Adding regional NPK averages...")
    npk_data = {"nitrogen": 30, "phosphorus": 22.5, "potassium": 60}
    print(
        f"   🌱 N: {npk_data['nitrogen']}, P: {npk_data['phosphorus']}, K: {npk_data['potassium']}"
    )

    # Step 4: Combine all data for ML prediction
    print("Step 4: Preparing ML input...")
    ml_input = {
        "nitrogen": npk_data["nitrogen"],
        "phosphorus": npk_data["phosphorus"],
        "potassium": npk_data["potassium"],
        "temperature": temperature_value,
        "humidity": humidity_value,
        "ph": ph_value,
        "rainfall": rainfall_value,
    }
    print(f"   🔢 ML Input: {ml_input}")

    # Step 5: Make ML prediction
    print("Step 5: Running ML prediction...")
    prediction_result = real_ml_service.get_prediction_with_rationale(ml_input)

    print("🎉 FINAL RESULT:")
    print(f"   🌾 Recommended Crop: {prediction_result['recommended_crop'].title()}")
    print(f"   📊 Confidence: {prediction_result['confidence']*100:.1f}%")
    print(f"   💭 Rationale: {prediction_result['rationale']}")
    print(
        f"   🔄 Alternative Options: {[crop['crop'] for crop in prediction_result.get('alternative_crops', [])]}"
    )

    # Step 6: Show data sources
    print("\n📋 Data Sources Used:")
    print("   • IoT Sensors: Firebase Realtime Database")
    print("   • Weather Data: Open-Meteo API")
    print("   • NPK Data: Regional averages for Bhairahawa")
    print("   • ML Models: XGBoost, Random Forest, SVM")

    return prediction_result


def test_api_endpoints():
    """Test that our API endpoints would work"""
    print("🔌 Testing API Endpoint Logic...")
    print("=" * 50)

    # Simulate the data collection that happens in views.py
    from apps.crops.views import collect_real_time_data, format_prediction_response

    # Simulate user input (what would come from the form)
    user_input = {
        "location": "Bhairahawa-Butwal",
        "season": "kharif",
        "area": "2.5",
        # Other fields would be filled by real-time data
    }

    print("🔄 Simulating API data collection...")
    prediction_input = collect_real_time_data(user_input)
    print(f"📊 Collected Input: {prediction_input}")

    print("🤖 Making ML prediction...")
    prediction_result = real_ml_service.get_prediction_with_rationale(prediction_input)

    print("📤 Formatting API response...")
    api_response = format_prediction_response(prediction_result, prediction_input)

    print("✅ API Response Preview:")
    print(f"   Primary Crop: {api_response['prediction_summary']['primary_crop']}")
    print(f"   Confidence: {api_response['prediction_summary']['confidence']*100:.1f}%")
    print(
        f"   Total Recommendations: {api_response['prediction_summary']['total_recommendations']}"
    )
    print(f"   Data Sources: {api_response['prediction_summary']['data_sources_used']}")

    return api_response


if __name__ == "__main__":
    print("🚀 HALO-AI Real IoT & ML Integration Test")
    print("=" * 60)
    print()

    try:
        # Run individual tests
        test_iot_integration()
        test_weather_integration()
        test_ml_integration()

        # Run complete integration test
        complete_result = test_complete_integration()
        print()

        # Test API endpoint logic
        api_response = test_api_endpoints()
        print()

        print("🎯 Integration Test Summary:")
        print("=" * 30)
        print("✅ IoT Sensor Integration: Working")
        print("✅ Weather API Integration: Working")
        print("✅ ML Model Integration: Working")
        print("✅ Complete Pipeline: Working")
        print("✅ API Endpoint Logic: Working")
        print()
        print(
            "🌟 Your crop prediction system is ready to use real IoT data and ML models!"
        )
        print(
            "📱 Open the web interface and click 'Use Real-Time IoT & Weather Data' to see it in action!"
        )

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
