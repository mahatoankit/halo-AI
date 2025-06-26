"""
Enhanced Crop Prediction Service
ML-based crop recommendations with community admin role-based access control
"""

import os
import pickle
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from apps.crops.models import CropPredictionRequest, CropRecommendation, CropType
from apps.sensors.models import IoTSensorSet, SensorReading
from .firebase_service_refactored import firebase_service
from .enhanced_weather_service import enhanced_weather_service


class EnhancedCropPredictionService:
    """Enhanced service for crop prediction with community admin support"""

    def __init__(self):
        self.firebase_service = firebase_service
        self.weather_service = enhanced_weather_service
        self.models = {}
        self.load_ml_models()

        # Regional defaults for Bhairahawa-Butwal (MVP)
        self.regional_defaults = {
            "Bhairahawa-Butwal": {
                "nitrogen": 85.0,
                "phosphorus": 50.0,
                "potassium": 40.0,
                "temperature": 25.0,
                "humidity": 75.0,
                "ph": 6.8,
                "rainfall": 200.0,
            }
        }

    def load_ml_models(self):
        """Load pre-trained ML models"""
        try:
            models_dir = os.path.join(settings.BASE_DIR.parent, "ml", "models")

            model_files = [
                ("random_forest", "random_forest_model.pkl"),
                ("svm", "svm_model.pkl"),
                ("xgboost", "xgboost_model.pkl"),
            ]

            for model_name, filename in model_files:
                model_path = os.path.join(models_dir, filename)
                if os.path.exists(model_path):
                    with open(model_path, "rb") as f:
                        self.models[model_name] = pickle.load(f)
                    print(f"✅ Loaded {model_name} model")
                else:
                    print(f"⚠️ Model file not found: {model_path}")

        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            # Use mock predictions if models fail to load
            self.models = {}

    def collect_prediction_data(
        self, community_admin_id: str, sensor_set: IoTSensorSet
    ) -> Dict[str, float]:
        """Collect sensor data and regional defaults for crop prediction"""
        try:
            region_defaults = self.regional_defaults.get(
                sensor_set.region, self.regional_defaults["Bhairahawa-Butwal"]
            )

            # Start with regional defaults
            prediction_data = region_defaults.copy()

            # Try to get real sensor data from Firebase
            sensor_readings = self.firebase_service.get_latest_sensor_readings(
                community_admin_id, str(sensor_set.id)
            )

            # Override defaults with actual sensor readings if available
            if sensor_readings:
                for sensor_type, reading_data in sensor_readings.items():
                    if (
                        sensor_type in ["temperature", "humidity", "ph"]
                        and "value" in reading_data
                    ):
                        prediction_data[sensor_type] = reading_data["value"]

            # For MVP: Always use default NPK values from sensor set
            prediction_data["nitrogen"] = sensor_set.default_nitrogen
            prediction_data["phosphorus"] = sensor_set.default_phosphorus
            prediction_data["potassium"] = sensor_set.default_potassium

            # Get weather data for rainfall
            try:
                weather_data = self.weather_service.get_current_weather_data(
                    sensor_set.region
                )
                if weather_data and "rainfall" in weather_data:
                    prediction_data["rainfall"] = float(weather_data["rainfall"])
            except Exception as weather_error:
                print(f"Weather API error: {weather_error}")
                # Keep default rainfall value

            return prediction_data

        except Exception as e:
            print(f"Error collecting prediction data: {e}")
            # Return defaults if anything fails
            return self.regional_defaults["Bhairahawa-Butwal"].copy()

    def create_prediction_request(
        self, community_admin_id: str, sensor_set_id: str
    ) -> Optional[CropPredictionRequest]:
        """Create a new crop prediction request"""
        try:
            # Get sensor set
            sensor_set = IoTSensorSet.objects.get(
                id=sensor_set_id, community_admin_id=community_admin_id
            )

            # Collect prediction data
            prediction_data = self.collect_prediction_data(
                community_admin_id, sensor_set
            )

            # Create prediction request
            prediction_request = CropPredictionRequest.objects.create(
                community_admin_id=community_admin_id,
                sensor_set=sensor_set,
                nitrogen=prediction_data["nitrogen"],
                phosphorus=prediction_data["phosphorus"],
                potassium=prediction_data["potassium"],
                temperature=prediction_data["temperature"],
                humidity=prediction_data["humidity"],
                ph=prediction_data["ph"],
                rainfall=prediction_data["rainfall"],
                status="processing",
            )

            # Store in Firebase for real-time tracking
            self.firebase_service.store_prediction_request(
                str(prediction_request.id),
                community_admin_id,
                sensor_set_id,
                prediction_data,
            )

            return prediction_request

        except Exception as e:
            print(f"Error creating prediction request: {e}")
            return None
            print(f"Error getting sensor data: {e}")
            # Return all defaults
            return {
                "nitrogen": sensor_set.default_nitrogen,
                "phosphorus": sensor_set.default_phosphorus,
                "potassium": sensor_set.default_potassium,
                "temperature": 25.0,
                "humidity": 80.0,
                "ph": 6.5,
                "rainfall": 200.0,
            }

    def create_prediction_request(
        self, community_admin, sensor_set: IoTSensorSet
    ) -> CropPredictionRequest:
        """Create a new crop prediction request"""
        # Get current sensor data
        sensor_data = self.get_sensor_data(sensor_set)

        # Create prediction request
        prediction_request = CropPredictionRequest.objects.create(
            community_admin=community_admin,
            sensor_set=sensor_set,
            nitrogen=sensor_data["nitrogen"],
            phosphorus=sensor_data["phosphorus"],
            potassium=sensor_data["potassium"],
            temperature=sensor_data["temperature"],
            humidity=sensor_data["humidity"],
            ph=sensor_data["ph"],
            rainfall=sensor_data["rainfall"],
            status="processing",
        )

        # Process prediction asynchronously
        self.process_prediction(prediction_request)

        return prediction_request

    def process_prediction(self, prediction_request: CropPredictionRequest):
        """Process crop prediction using ML models"""
        try:
            # Prepare input data
            input_data = pd.DataFrame([prediction_request.input_parameters])

            # Get predictions from available models
            predictions = {}

            if self.models:
                for model_name, model in self.models.items():
                    try:
                        pred = model.predict(input_data)[0]
                        prob = getattr(model, "predict_proba", lambda x: [[0.5, 0.5]])(
                            input_data
                        )[0]
                        confidence = max(prob) if hasattr(prob, "__iter__") else 0.8

                        predictions[model_name] = {
                            "crop": pred,
                            "confidence": confidence,
                        }
                    except Exception as e:
                        print(f"Error with {model_name}: {e}")

            # If no models available, use rule-based prediction
            if not predictions:
                predictions = self.rule_based_prediction(
                    prediction_request.input_parameters
                )

            # Generate ensemble prediction
            final_predictions = self.ensemble_prediction(predictions)

            # Update prediction request
            prediction_request.predicted_crops = final_predictions
            prediction_request.confidence_score = (
                final_predictions[0]["confidence"] if final_predictions else 0.5
            )
            prediction_request.status = "completed"
            prediction_request.processed_at = datetime.now(timezone.utc)
            prediction_request.save()

            # Create recommendations
            self.create_recommendations(prediction_request, final_predictions)

        except Exception as e:
            print(f"Error processing prediction: {e}")
            prediction_request.status = "failed"
            prediction_request.notes = f"Processing error: {str(e)}"
            prediction_request.save()

    def rule_based_prediction(self, input_params: Dict[str, float]) -> Dict[str, Dict]:
        """Rule-based prediction for Bhairahawa-Butwal region"""
        temp = input_params["temperature"]
        humidity = input_params["humidity"]
        rainfall = input_params["rainfall"]
        ph = input_params["ph"]

        predictions = {}

        # Rice - suitable for high humidity and rainfall
        if humidity > 80 and rainfall > 200 and 20 <= temp <= 30:
            predictions["rice"] = {"crop": "rice", "confidence": 0.85}

        # Wheat - suitable for moderate conditions
        if 15 <= temp <= 25 and rainfall < 300 and ph > 6:
            predictions["wheat"] = {"crop": "wheat", "confidence": 0.75}

        # Maize - versatile crop
        if 18 <= temp <= 28 and rainfall > 100:
            predictions["maize"] = {"crop": "maize", "confidence": 0.70}

        # Lentil - good for dry conditions
        if temp < 25 and rainfall < 200:
            predictions["lentil"] = {"crop": "lentil", "confidence": 0.65}

        # Default to rice if no specific conditions met
        if not predictions:
            predictions["default"] = {"crop": "rice", "confidence": 0.60}

        return predictions

    def ensemble_prediction(self, predictions: Dict[str, Dict]) -> List[Dict]:
        """Combine predictions from multiple models/rules"""
        crop_scores = {}

        for model_name, pred_data in predictions.items():
            crop = pred_data["crop"]
            confidence = pred_data["confidence"]

            if crop not in crop_scores:
                crop_scores[crop] = []
            crop_scores[crop].append(confidence)

        # Average confidence scores for each crop
        final_predictions = []
        for crop, scores in crop_scores.items():
            avg_confidence = sum(scores) / len(scores)
            final_predictions.append({"crop": crop, "confidence": avg_confidence})

        # Sort by confidence
        final_predictions.sort(key=lambda x: x["confidence"], reverse=True)

        return final_predictions[:3]  # Top 3 predictions

    def create_recommendations(
        self, prediction_request: CropPredictionRequest, predictions: List[Dict]
    ):
        """Create crop recommendations based on predictions"""
        recommendation_types = ["primary", "secondary", "alternative"]

        for i, pred in enumerate(predictions):
            if i >= len(recommendation_types):
                break

            crop_name = pred["crop"]
            confidence = pred["confidence"]

            # Get or create crop type
            crop_type, created = CropType.objects.get_or_create(
                name=crop_name,
                defaults={
                    "regional_success_rate": 0.7,
                    "growing_season": "Multiple seasons",
                },
            )

            # Generate rationale
            rationale = self.generate_rationale(
                crop_name, prediction_request.input_parameters
            )

            # Create recommendation
            CropRecommendation.objects.create(
                prediction_request=prediction_request,
                crop_type=crop_type,
                recommendation_type=recommendation_types[i],
                confidence_score=confidence,
                rationale=rationale,
                expected_yield=f"Regional average for {crop_name}",
                risk_factors=self.get_risk_factors(
                    crop_name, prediction_request.input_parameters
                ),
                local_market_demand=(
                    "high" if crop_name in ["rice", "wheat", "maize"] else "medium"
                ),
            )

    def generate_rationale(self, crop_name: str, input_params: Dict[str, float]) -> str:
        """Generate explanation for crop recommendation"""
        temp = input_params["temperature"]
        humidity = input_params["humidity"]
        rainfall = input_params["rainfall"]

        rationales = {
            "rice": f"Rice is recommended due to high humidity ({humidity:.1f}%) and adequate rainfall ({rainfall:.1f}mm). Temperature ({temp:.1f}°C) is optimal for rice cultivation.",
            "wheat": f"Wheat suits the moderate temperature ({temp:.1f}°C) and controlled moisture conditions. Regional climate is favorable for wheat production.",
            "maize": f"Maize is versatile and adapts well to current conditions (T:{temp:.1f}°C, H:{humidity:.1f}%). Good market demand in the region.",
            "lentil": f"Lentil is suitable for the current soil and climate conditions. Requires minimal water and suits the temperature range.",
        }

        return rationales.get(
            crop_name,
            f"{crop_name} is recommended based on current environmental conditions and regional suitability.",
        )

    def get_risk_factors(
        self, crop_name: str, input_params: Dict[str, float]
    ) -> List[str]:
        """Identify potential risk factors for crop"""
        risks = []

        temp = input_params["temperature"]
        humidity = input_params["humidity"]
        rainfall = input_params["rainfall"]
        ph = input_params["ph"]

        # Temperature risks
        if temp > 35:
            risks.append("High temperature stress")
        elif temp < 10:
            risks.append("Low temperature may affect growth")

        # Humidity risks
        if humidity > 90:
            risks.append("High humidity may cause fungal diseases")
        elif humidity < 40:
            risks.append("Low humidity may cause water stress")

        # Rainfall risks
        if rainfall > 500:
            risks.append("Excessive rainfall may cause waterlogging")
        elif rainfall < 50:
            risks.append("Insufficient rainfall may require irrigation")

        # pH risks
        if ph > 8:
            risks.append("Alkaline soil may affect nutrient uptake")
        elif ph < 5:
            risks.append("Acidic soil may limit crop growth")

        # Crop-specific risks
        crop_risks = {
            "rice": [
                "Blast disease in high humidity",
                "Brown planthopper in warm conditions",
            ],
            "wheat": [
                "Rust diseases in humid conditions",
                "Heat stress during grain filling",
            ],
            "maize": ["Corn borer in warm weather", "Stalk rot in wet conditions"],
        }

        if crop_name in crop_risks:
            risks.extend(crop_risks[crop_name])

        return risks[:3]  # Limit to top 3 risks

    def get_prediction_history(self, community_admin) -> List[CropPredictionRequest]:
        """Get prediction history for community admin"""
        return CropPredictionRequest.objects.filter(
            community_admin=community_admin
        ).order_by("-requested_at")[:20]


# Compatibility alias for backward compatibility
CropPredictionService = EnhancedCropPredictionService
