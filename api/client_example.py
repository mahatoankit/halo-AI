import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())
    return response.status_code == 200

def test_single_prediction():
    """Test single crop prediction"""
    # Example soil and environmental data
    test_data = {
        "nitrogen": 90,
        "phosphorous": 42,
        "potassium": 43,
        "temperature": 20.87,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9
    }
    
    # Test XGBoost prediction
    response = requests.post(f"{BASE_URL}/predict/xgboost", json=test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"XGBoost Prediction: {result['recommended_crop']}")
        print(f"Confidence: {result['confidence']:.3f}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_batch_prediction():
    """Test batch predictions"""
    batch_data = {
        "features": [
            {
                "nitrogen": 90, "phosphorous": 42, "potassium": 43,
                "temperature": 20.87, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9
            },
            {
                "nitrogen": 85, "phosphorous": 58, "potassium": 41,
                "temperature": 21.77, "humidity": 80.3, "ph": 7.0, "rainfall": 226.6
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/predict/batch?model=xgboost", json=batch_data)
    if response.status_code == 200:
        result = response.json()
        print(f"Batch Predictions: {result['total_predictions']} crops predicted")
        for i, pred in enumerate(result['predictions']):
            print(f"  {i+1}. {pred['recommended_crop']} (confidence: {pred['confidence']:.3f})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_model_info():
    """Test model information endpoint"""
    response = requests.get(f"{BASE_URL}/models/info")
    if response.status_code == 200:
        models = response.json()
        print("Available Models:")
        for model in models:
            print(f"  - {model['model_name']}: {model['accuracy']:.1%} accuracy")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Testing HALO-AI Crop Recommendation API")
    print("=" * 50)
    
    # Test health check
    if test_health_check():
        print("✅ API is healthy")
        
        # Test single prediction
        print("\n📊 Testing Single Prediction:")
        test_single_prediction()
        
        # Test batch prediction
        print("\n📊 Testing Batch Prediction:")
        test_batch_prediction()
        
        # Test model info
        print("\n📊 Testing Model Info:")
        test_model_info()
        
    else:
        print("❌ API health check failed")
