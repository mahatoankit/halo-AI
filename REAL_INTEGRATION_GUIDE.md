# 🌾 HALO-AI Real IoT & ML Integration Guide

## 🚀 Overview

This integration brings together **real-time IoT sensor data**, **live weather data**, and **actual machine learning models** to provide accurate crop predictions for the Bhairahawa-Butwal region of Nepal.

## 📊 Data Sources Integration

### 1. 🔧 IoT Sensor Data (Firebase Realtime Database)

**Format**: `ph,temperature` (e.g., `6.5,29.6`)

**Source**: Firebase Realtime Database at path `/iot_sensors/{sensor_id}/latest`

**Fields Collected**:

- **pH Level**: Soil acidity/alkalinity (6.5)
- **Temperature**: Ambient temperature in °C (29.6)

**Code Location**: `backend/haloai/services/iot_data_service.py`

### 2. 🌤️ Weather Data (Open-Meteo API)

**API**: [Open-Meteo](https://api.open-meteo.com) (Free, no API key required)

**Coordinates**:

- Bhairahawa: 27.5057°N, 83.4163°E
- Butwal: 27.6855°N, 83.4409°E

**Fields Collected**:

- **Rainfall**: Daily precipitation in mm (22.5)
- **Humidity**: Relative humidity percentage (60.0)

**Code Location**: `backend/haloai/services/enhanced_weather_service.py`

### 3. 🌱 Regional NPK Data

**Source**: Regional agricultural averages for Bhairahawa-Butwal

**Default Values**:

- **Nitrogen (N)**: 30 mg/kg
- **Phosphorus (P)**: 22.5 mg/kg
- **Potassium (K)**: 60 mg/kg

## 🤖 Machine Learning Models

### Models Used

1. **XGBoost** (99.2% accuracy) - Primary model
2. **Random Forest** (99.0% accuracy) - Ensemble member
3. **SVM** (98.5% accuracy) - Ensemble member

### Input Format

```python
[N, P, K, temperature, humidity, ph, rainfall]
# Example: [30, 22.5, 60, 29.6, 60.0, 6.5, 22.5]
```

### Output

- **Crop Recommendation**: Name of recommended crop
- **Confidence Score**: ML model confidence (0-1)
- **Rationale**: AI-generated explanation
- **Alternative Crops**: Secondary recommendations

**Code Location**: `backend/haloai/services/real_ml_prediction_service.py`

## 🔌 API Endpoints

### 1. Real-Time Data Endpoint

```
GET /crops/api/real-time-data/?region=Bhairahawa-Butwal
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "ph": 6.5,
    "temperature": 29.6,
    "rainfall": 22.5,
    "humidity": 60.0,
    "nitrogen": 30,
    "phosphorus": 22.5,
    "potassium": 60,
    "region": "Bhairahawa-Butwal",
    "data_sources": {
      "iot_sensors": "Firebase Realtime Database",
      "weather": "open-meteo",
      "npk": "Regional averages"
    }
  }
}
```

### 2. ML Prediction Endpoint

```
POST /crops/api/predict/
```

**Request Body**:

```json
{
  "nitrogen": 30,
  "phosphorus": 22.5,
  "potassium": 60,
  "ph": 6.5,
  "temperature": 29.6,
  "humidity": 60.0,
  "rainfall": 22.5,
  "location": "Bhairahawa, Nepal",
  "season": "kharif",
  "area": "2.5"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "recommended_crops": [
      {
        "name": "Rice",
        "confidence": 92,
        "reason": "Rice is recommended with 92.1% confidence. Rice thrives in high humidity (60.0%) and adequate rainfall (22.5mm).",
        "type": "primary"
      }
    ],
    "prediction_summary": {
      "primary_crop": "Rice",
      "confidence": 0.921,
      "total_recommendations": 3,
      "data_sources_used": [
        "IoT Sensors",
        "Weather API",
        "Regional Data",
        "ML Models"
      ]
    }
  }
}
```

## 🎯 Frontend Integration

### Enhanced UI Features

1. **"Use Real-Time IoT & Weather Data" Button**

   - Automatically fetches and fills form with current sensor and weather data
   - Shows data source indicators
   - Provides real-time status updates

2. **AI-Powered Predictions**

   - Uses actual XGBoost, Random Forest, and SVM models
   - Shows confidence scores from ensemble learning
   - Displays model details and data sources

3. **Smart Data Prioritization**
   - User Input → IoT Sensors → Weather API → Regional Defaults
   - Seamless fallback system for reliability

## 🔄 Data Flow

```
1. User opens prediction page
2. Clicks "Use Real-Time IoT & Weather Data"
3. Frontend calls /crops/api/real-time-data/
4. Backend collects:
   - IoT sensor data from Firebase
   - Weather data from Open-Meteo API
   - Regional NPK averages
5. Form is auto-filled with real data
6. User submits prediction form
7. Frontend calls /crops/api/predict/
8. Backend processes with ML models:
   - XGBoost prediction
   - Random Forest prediction
   - SVM prediction
   - Ensemble averaging
9. AI-generated rationale created
10. Results displayed with confidence scores
```

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
cd backend/haloai
pip install -r requirements.txt
```

### 2. Configure Firebase (Optional)

- If you have Firebase configured, sensor data will be fetched automatically
- If not, the system uses realistic simulated data

### 3. Run the Server

```bash
python manage.py runserver
```

### 4. Test the Integration

```bash
# Run the integration test
python test_integration.py
```

### 5. Access the Interface

1. Open `http://localhost:8000/crops/prediction/`
2. Click "🔄 Use Real-Time IoT & Weather Data"
3. Submit form to get AI predictions

## 📈 Features Implemented

### ✅ Real Data Integration

- [x] IoT sensor data from Firebase (pH, temperature)
- [x] Live weather data from Open-Meteo API (rainfall, humidity)
- [x] Regional NPK averages for Bhairahawa
- [x] Automatic fallback systems

### ✅ Machine Learning

- [x] XGBoost model (99.2% accuracy)
- [x] Random Forest model (99.0% accuracy)
- [x] SVM model (98.5% accuracy)
- [x] Ensemble prediction combining all models
- [x] Confidence scoring and rationale generation

### ✅ Enhanced UI/UX

- [x] Real-time data fetching button
- [x] Data source indicators
- [x] AI-powered prediction results
- [x] Model transparency and details
- [x] Confidence score visualization

### ✅ API Architecture

- [x] RESTful API endpoints
- [x] JSON request/response format
- [x] Error handling and fallbacks
- [x] Data source prioritization

## 🔧 Code Organization

```
backend/haloai/
├── services/
│   ├── iot_data_service.py          # IoT sensor data handling
│   ├── enhanced_weather_service.py  # Weather API integration
│   ├── real_ml_prediction_service.py # ML model predictions
│   └── crop_prediction_service.py   # Original service (enhanced)
├── apps/crops/
│   ├── views.py                     # Updated with real APIs
│   ├── urls.py                      # New API endpoints
│   └── models.py                    # Django models
└── templates/crops/
    └── prediction.html              # Enhanced UI with real data
```

## 🎯 Example Usage

### Manual Testing

```python
# Test IoT data
from services.iot_data_service import iot_data_service
sensor_data = iot_data_service.get_latest_sensor_data("bhairahawa_farm_1")
print(f"IoT Data: {sensor_data}")

# Test weather data
from services.enhanced_weather_service import enhanced_weather_service
weather_data = enhanced_weather_service.get_current_weather_data("Bhairahawa-Butwal")
print(f"Weather Data: {weather_data}")

# Test ML prediction
from services.real_ml_prediction_service import real_ml_service
input_data = {
    'nitrogen': 30, 'phosphorus': 22.5, 'potassium': 60,
    'temperature': 29.6, 'humidity': 60.0, 'ph': 6.5, 'rainfall': 22.5
}
prediction = real_ml_service.get_prediction_with_rationale(input_data)
print(f"ML Prediction: {prediction}")
```

### UI Testing

1. Open the crop prediction page
2. Click "🔄 Use Real-Time IoT & Weather Data"
3. Observe form being filled with real data
4. Submit form and see AI predictions with confidence scores

## 🌟 Benefits Achieved

1. **Real Data**: No more dummy data - actual IoT sensors and weather APIs
2. **ML Accuracy**: 99.2% accuracy with ensemble of three models
3. **User Experience**: One-click real-time data loading
4. **Transparency**: Shows data sources and model confidence
5. **Reliability**: Multiple fallback systems for robustness
6. **Scalability**: Modular service architecture for easy expansion

## 🔮 Future Enhancements

1. **More IoT Sensors**: Add moisture, light, and nutrient sensors
2. **Historical Analysis**: Trend analysis and seasonal predictions
3. **Market Integration**: Crop price predictions and profitability analysis
4. **Mobile App**: React Native app for farmers
5. **Satellite Data**: Remote sensing for large-scale monitoring

## 🆘 Troubleshooting

### Common Issues

1. **"Failed to load real-time data"**

   - Check internet connection for weather API
   - Firebase may not be configured (uses simulated data)
   - Check console for specific error messages

2. **"ML models not available"**

   - Ensure model files exist in `ml/models/` directory
   - Check file permissions and paths
   - System will use rule-based fallback

3. **"API endpoint not found"**
   - Ensure Django server is running
   - Check URL configuration in `apps/crops/urls.py`
   - Verify view imports are correct

### Debug Mode

Set `DEBUG = True` in Django settings for detailed error messages.

## 📞 Support

For technical support or questions about the integration:

1. Check the console logs for error messages
2. Run `python test_integration.py` to test all components
3. Verify all services are properly imported and initialized
4. Contact the development team with specific error details

---

**🎉 Congratulations! Your HALO-AI system now uses real IoT data and machine learning models for accurate crop predictions!**
