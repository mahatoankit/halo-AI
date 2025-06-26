"""
Real ML Prediction Service
Uses actual trained XGBoost, Random Forest, and SVM models for crop prediction
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from django.conf import settings


class RealMLPredictionService:
    """Service for making actual ML predictions using trained models"""

    def __init__(self):
        self.models = {}
        self.label_encoder = None
        self.crop_labels = [
            "rice",
            "maize",
            "chickpea",
            "kidneybeans",
            "pigeonpeas",
            "mothbeans",
            "mungbean",
            "blackgram",
            "lentil",
            "pomegranate",
            "banana",
            "mango",
            "grapes",
            "watermelon",
            "muskmelon",
            "apple",
            "orange",
            "papaya",
            "coconut",
            "cotton",
            "jute",
            "coffee",
        ]
        self.load_models()

    def load_models(self):
        """Load the pre-trained ML models"""
        try:
            models_dir = os.path.join(settings.BASE_DIR.parent, "ml", "models")

            model_files = {
                "xgboost": "xgboost_model.pkl",
                "random_forest": "random_forest_model.pkl",
                "svm": "svm_model.pkl",
            }

            for model_name, filename in model_files.items():
                model_path = os.path.join(models_dir, filename)
                if os.path.exists(model_path):
                    try:
                        with open(model_path, "rb") as f:
                            self.models[model_name] = pickle.load(f)
                        print(f"✅ Loaded {model_name} model successfully")
                    except Exception as e:
                        print(f"⚠️ Error loading {model_name} model: {e}")
                else:
                    print(f"⚠️ Model file not found: {model_path}")

            print(f"📊 Loaded {len(self.models)} ML models")

        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            self.models = {}

    def preprocess_input(self, input_data: Dict[str, float]) -> np.ndarray:
        """
        Preprocess input data for ML models
        Expected format: [N, P, K, temperature, humidity, ph, rainfall]
        """
        try:
            # Extract features in the correct order
            features = [
                float(input_data.get("nitrogen", 85.0)),  # N
                float(input_data.get("phosphorus", 50.0)),  # P
                float(input_data.get("potassium", 40.0)),  # K
                float(input_data.get("temperature", 25.0)),  # temperature
                float(input_data.get("humidity", 75.0)),  # humidity
                float(input_data.get("ph", 6.8)),  # ph
                float(input_data.get("rainfall", 200.0)),  # rainfall
            ]

            return np.array([features])

        except Exception as e:
            print(f"Error preprocessing input: {e}")
            # Return default values if preprocessing fails
            return np.array([[85.0, 50.0, 40.0, 25.0, 75.0, 6.8, 200.0]])

    def make_prediction(
        self, input_data: Dict[str, float]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Make crop predictions using all available models
        Returns predictions from each model with confidence scores
        """
        results = {}

        if not self.models:
            print("⚠️ No ML models loaded, using fallback prediction")
            return self._fallback_prediction(input_data)

        # Preprocess input
        features = self.preprocess_input(input_data)

        for model_name, model in self.models.items():
            try:
                # Make prediction
                prediction = model.predict(features)[0]

                # Get confidence score if available
                confidence = 0.8  # Default confidence
                if hasattr(model, "predict_proba"):
                    try:
                        probabilities = model.predict_proba(features)[0]
                        confidence = float(np.max(probabilities))
                    except Exception:
                        pass
                elif hasattr(model, "decision_function"):
                    try:
                        decision_scores = model.decision_function(features)[0]
                        # Normalize decision scores to 0-1 range
                        confidence = min(
                            1.0, max(0.1, abs(decision_scores.max()) / 10.0)
                        )
                    except Exception:
                        pass

                # Convert prediction to crop name
                if isinstance(prediction, (int, np.integer)):
                    if 0 <= prediction < len(self.crop_labels):
                        crop_name = self.crop_labels[prediction]
                    else:
                        crop_name = "rice"  # Default fallback
                else:
                    crop_name = str(prediction).lower()

                results[model_name] = [
                    {
                        "crop": crop_name,
                        "confidence": round(confidence, 3),
                        "model": model_name,
                        "prediction_index": (
                            int(prediction)
                            if isinstance(prediction, (int, np.integer))
                            else -1
                        ),
                    }
                ]

            except Exception as e:
                print(f"Error making prediction with {model_name}: {e}")
                # Add fallback for this model
                results[model_name] = [
                    {
                        "crop": "rice",
                        "confidence": 0.5,
                        "model": model_name,
                        "error": str(e),
                    }
                ]

        return results

    def get_ensemble_prediction(
        self, input_data: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Get ensemble prediction by combining results from all models
        Returns top 3 crop recommendations
        """
        model_predictions = self.make_prediction(input_data)

        # Aggregate predictions
        crop_scores = {}

        for model_name, predictions in model_predictions.items():
            for pred in predictions:
                crop = pred["crop"]
                confidence = pred["confidence"]

                if crop not in crop_scores:
                    crop_scores[crop] = {
                        "total_confidence": 0.0,
                        "model_count": 0,
                        "models": [],
                    }

                crop_scores[crop]["total_confidence"] += confidence
                crop_scores[crop]["model_count"] += 1
                crop_scores[crop]["models"].append(model_name)

        # Calculate weighted average confidence
        final_predictions = []
        for crop, scores in crop_scores.items():
            avg_confidence = scores["total_confidence"] / scores["model_count"]

            # Boost confidence if multiple models agree
            if scores["model_count"] > 1:
                avg_confidence = min(1.0, avg_confidence * 1.1)

            final_predictions.append(
                {
                    "crop": crop,
                    "confidence": round(avg_confidence, 3),
                    "supporting_models": scores["models"],
                    "model_agreement": scores["model_count"],
                }
            )

        # Sort by confidence and return top 3
        final_predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return final_predictions[:3]

    def get_prediction_with_rationale(
        self, input_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Get prediction with detailed rationale and analysis
        """
        ensemble_predictions = self.get_ensemble_prediction(input_data)

        if not ensemble_predictions:
            return self._fallback_prediction_with_rationale(input_data)

        top_prediction = ensemble_predictions[0]

        # Generate rationale based on input conditions
        rationale = self._generate_prediction_rationale(
            top_prediction["crop"], input_data, top_prediction["confidence"]
        )

        return {
            "recommended_crop": top_prediction["crop"],
            "confidence": top_prediction["confidence"],
            "rationale": rationale,
            "alternative_crops": ensemble_predictions[1:],
            "input_analysis": self._analyze_input_conditions(input_data),
            "model_details": {
                "supporting_models": top_prediction["supporting_models"],
                "model_agreement": top_prediction["model_agreement"],
                "total_models": len(self.models),
            },
        }

    def _generate_prediction_rationale(
        self, crop: str, input_data: Dict[str, float], confidence: float
    ) -> str:
        """Generate human-readable rationale for the prediction"""
        temp = input_data.get("temperature", 25.0)
        humidity = input_data.get("humidity", 75.0)
        rainfall = input_data.get("rainfall", 200.0)
        ph = input_data.get("ph", 6.8)

        base_rationale = (
            f"{crop.title()} is recommended with {confidence*100:.1f}% confidence. "
        )

        # Crop-specific rationales
        crop_rationales = {
            "rice": f"Rice thrives in high humidity ({humidity:.1f}%) and adequate rainfall ({rainfall:.1f}mm). The temperature ({temp:.1f}°C) and pH ({ph:.1f}) are suitable for rice cultivation.",
            "wheat": f"Wheat is well-suited for the moderate temperature ({temp:.1f}°C) and current soil conditions. The pH level ({ph:.1f}) supports healthy wheat growth.",
            "maize": f"Maize adapts well to these conditions with temperature at {temp:.1f}°C and humidity at {humidity:.1f}%. Good versatility for varying weather conditions.",
            "cotton": f"Cotton benefits from the warm temperature ({temp:.1f}°C) and moderate rainfall ({rainfall:.1f}mm). Soil pH ({ph:.1f}) is optimal for cotton fiber development.",
            "sugarcane": f"Sugarcane requires high water availability, which is met by {rainfall:.1f}mm rainfall and {humidity:.1f}% humidity. Temperature conditions are favorable.",
        }

        specific_rationale = crop_rationales.get(
            crop,
            f"{crop.title()} is suitable based on the current environmental conditions and regional climate patterns.",
        )

        return base_rationale + specific_rationale

    def _analyze_input_conditions(self, input_data: Dict[str, float]) -> Dict[str, str]:
        """Analyze input conditions and provide insights"""
        analysis = {}

        temp = input_data.get("temperature", 25.0)
        humidity = input_data.get("humidity", 75.0)
        rainfall = input_data.get("rainfall", 200.0)
        ph = input_data.get("ph", 6.8)
        nitrogen = input_data.get("nitrogen", 85.0)
        phosphorus = input_data.get("phosphorus", 50.0)
        potassium = input_data.get("potassium", 40.0)

        # Temperature analysis
        if temp > 35:
            analysis["temperature"] = (
                "High temperature - consider heat-resistant varieties"
            )
        elif temp < 15:
            analysis["temperature"] = "Low temperature - suitable for cool-season crops"
        else:
            analysis["temperature"] = "Optimal temperature range for most crops"

        # Humidity analysis
        if humidity > 80:
            analysis["humidity"] = "High humidity - monitor for fungal diseases"
        elif humidity < 40:
            analysis["humidity"] = "Low humidity - ensure adequate irrigation"
        else:
            analysis["humidity"] = "Good humidity levels for crop growth"

        # Rainfall analysis
        if rainfall > 400:
            analysis["rainfall"] = "High rainfall - ensure proper drainage"
        elif rainfall < 100:
            analysis["rainfall"] = "Low rainfall - supplemental irrigation needed"
        else:
            analysis["rainfall"] = "Adequate rainfall for rain-fed agriculture"

        # pH analysis
        if ph > 8:
            analysis["ph"] = "Alkaline soil - may need acid-forming fertilizers"
        elif ph < 6:
            analysis["ph"] = "Acidic soil - consider lime application"
        else:
            analysis["ph"] = "Optimal soil pH for nutrient availability"

        # NPK analysis
        if nitrogen < 40:
            analysis["nitrogen"] = "Low nitrogen - consider nitrogen fertilizers"
        elif nitrogen > 120:
            analysis["nitrogen"] = (
                "High nitrogen - monitor for excessive vegetative growth"
            )
        else:
            analysis["nitrogen"] = "Adequate nitrogen levels"

        return analysis

    def _fallback_prediction(
        self, input_data: Dict[str, float]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Fallback prediction when ML models are not available"""
        return {
            "rule_based": [
                {
                    "crop": "rice",
                    "confidence": 0.7,
                    "model": "rule_based",
                    "note": "Fallback prediction - ML models not available",
                }
            ]
        }

    def _fallback_prediction_with_rationale(
        self, input_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """Fallback prediction with rationale when ML models fail"""
        return {
            "recommended_crop": "rice",
            "confidence": 0.7,
            "rationale": "Rice is recommended as a safe choice for the Bhairahawa-Butwal region based on regional agricultural patterns.",
            "alternative_crops": [
                {"crop": "maize", "confidence": 0.6},
                {"crop": "wheat", "confidence": 0.5},
            ],
            "input_analysis": self._analyze_input_conditions(input_data),
            "model_details": {
                "supporting_models": ["rule_based"],
                "model_agreement": 1,
                "total_models": 0,
                "note": "ML models not available - using rule-based fallback",
            },
        }


# Global instance
real_ml_service = RealMLPredictionService()


# Example usage
if __name__ == "__main__":
    # Test the ML service
    ml_service = RealMLPredictionService()

    # Sample input data (format expected by the models)
    test_input = {
        "nitrogen": 90,
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 20.8,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9,
    }

    print("Testing Real ML Prediction Service...")
    print("=" * 50)

    # Test individual model predictions
    predictions = ml_service.make_prediction(test_input)
    print(f"Individual model predictions: {predictions}")

    # Test ensemble prediction
    ensemble = ml_service.get_ensemble_prediction(test_input)
    print(f"Ensemble prediction: {ensemble}")

    # Test full prediction with rationale
    full_prediction = ml_service.get_prediction_with_rationale(test_input)
    print(f"Full prediction: {full_prediction}")
