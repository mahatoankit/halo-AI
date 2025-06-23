from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd
from typing import List, Optional
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HALO-AI Crop Recommendation API",
    description="Intelligent crop recommendation system using machine learning",
    version="1.0.0",
    contact={
        "name": "HALO-AI Team",
        "email": "support@halo-ai.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class CropFeatures(BaseModel):
    """Input features for crop prediction"""
    nitrogen: float = Field(..., ge=0, le=200, description="Nitrogen content in soil (ppm)")
    phosphorous: float = Field(..., ge=0, le=150, description="Phosphorous content in soil (ppm)")
    potassium: float = Field(..., ge=0, le=250, description="Potassium content in soil (ppm)")
    temperature: float = Field(..., ge=-10, le=50, description="Average temperature (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    ph: float = Field(..., ge=0, le=14, description="Soil pH level")
    rainfall: float = Field(..., ge=0, le=3000, description="Annual rainfall (mm)")

    class Config:
        schema_extra = {
            "example": {
                "nitrogen": 90,
                "phosphorous": 42,
                "potassium": 43,
                "temperature": 20.87,
                "humidity": 82.0,
                "ph": 6.5,
                "rainfall": 202.9
            }
        }

class BatchCropFeatures(BaseModel):
    """Batch input for multiple predictions"""
    features: List[CropFeatures] = Field(..., min_items=1, max_items=100)

class CropPrediction(BaseModel):
    """Single crop prediction response"""
    recommended_crop: str
    model_used: str
    confidence: Optional[float] = None
    input_features: CropFeatures

class BatchCropPrediction(BaseModel):
    """Batch prediction response"""
    predictions: List[CropPrediction]
    total_predictions: int

class ModelInfo(BaseModel):
    """Model information response"""
    model_name: str
    accuracy: float
    features: List[str]
    supported_crops: List[str]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    models_loaded: bool

# Global variables for models
rf_model = None
xgb_model = None
label_encoder = None
feature_names = ['nitrogen', 'phosphorous', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']

def load_models():
    """Load trained models and label encoder"""
    global rf_model, xgb_model, label_encoder
    
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        
        # Load models
        rf_model_path = project_root / "random_forest_model.pkl"
        xgb_model_path = project_root / "xgboost_model.pkl"
        
        if rf_model_path.exists():
            rf_model = joblib.load(rf_model_path)
            logger.info("Random Forest model loaded successfully")
        else:
            logger.warning(f"Random Forest model not found at {rf_model_path}")
            
        if xgb_model_path.exists():
            xgb_model = joblib.load(xgb_model_path)
            logger.info("XGBoost model loaded successfully")
        else:
            logger.warning(f"XGBoost model not found at {xgb_model_path}")
        
        # Create a dummy label encoder with known crop types
        # In production, you should save and load the actual label encoder
        from sklearn.preprocessing import LabelEncoder
        label_encoder = LabelEncoder()
        crops = ['apple', 'banana', 'blackgram', 'chickpea', 'coconut', 'coffee', 
                'cotton', 'grapes', 'jute', 'kidneybeans', 'lentil', 'maize', 
                'mango', 'mothbeans', 'mungbean', 'muskmelon', 'orange', 'papaya', 
                'pigeonpeas', 'pomegranate', 'rice', 'watermelon']
        label_encoder.fit(crops)
        
        return True
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return False

def get_model_dependency():
    """Dependency to ensure models are loaded"""
    if rf_model is None and xgb_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Please check server configuration.")
    return True

# Load models on startup
@app.on_event("startup")
async def startup_event():
    """Load models when the application starts"""
    success = load_models()
    if not success:
        logger.error("Failed to load models during startup")

# API Endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to HALO-AI Crop Recommendation API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    models_loaded = rf_model is not None or xgb_model is not None
    
    if models_loaded:
        return HealthResponse(
            status="healthy",
            message="API is running and models are loaded",
            models_loaded=True
        )
    else:
        return HealthResponse(
            status="unhealthy",
            message="Models are not loaded",
            models_loaded=False
        )

@app.post("/predict/random-forest", response_model=CropPrediction)
async def predict_random_forest(
    features: CropFeatures,
    _: bool = Depends(get_model_dependency)
):
    """Make crop prediction using Random Forest model"""
    if rf_model is None:
        raise HTTPException(status_code=503, detail="Random Forest model not available")
    
    try:
        # Convert features to numpy array
        input_array = np.array([[
            features.nitrogen, features.phosphorous, features.potassium,
            features.temperature, features.humidity, features.ph, features.rainfall
        ]])
        
        # Make prediction
        prediction = rf_model.predict(input_array)[0]
        
        # Get crop name
        crop_name = label_encoder.inverse_transform([prediction])[0]
        
        # Get prediction probabilities for confidence
        probabilities = rf_model.predict_proba(input_array)[0]
        confidence = float(np.max(probabilities))
        
        return CropPrediction(
            recommended_crop=crop_name,
            model_used="Random Forest",
            confidence=confidence,
            input_features=features
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/xgboost", response_model=CropPrediction)
async def predict_xgboost(
    features: CropFeatures,
    _: bool = Depends(get_model_dependency)
):
    """Make crop prediction using XGBoost model"""
    if xgb_model is None:
        raise HTTPException(status_code=503, detail="XGBoost model not available")
    
    try:
        # Convert features to numpy array
        input_array = np.array([[
            features.nitrogen, features.phosphorous, features.potassium,
            features.temperature, features.humidity, features.ph, features.rainfall
        ]])
        
        # Make prediction
        prediction = xgb_model.predict(input_array)[0]
        
        # Get crop name
        crop_name = label_encoder.inverse_transform([prediction])[0]
        
        # Get prediction probabilities for confidence
        probabilities = xgb_model.predict_proba(input_array)[0]
        confidence = float(np.max(probabilities))
        
        return CropPrediction(
            recommended_crop=crop_name,
            model_used="XGBoost",
            confidence=confidence,
            input_features=features
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/ensemble", response_model=CropPrediction)
async def predict_ensemble(
    features: CropFeatures,
    _: bool = Depends(get_model_dependency)
):
    """Make crop prediction using ensemble of both models"""
    if rf_model is None or xgb_model is None:
        raise HTTPException(status_code=503, detail="Both models required for ensemble prediction")
    
    try:
        # Convert features to numpy array
        input_array = np.array([[
            features.nitrogen, features.phosphorous, features.potassium,
            features.temperature, features.humidity, features.ph, features.rainfall
        ]])
        
        # Get predictions from both models
        rf_pred = rf_model.predict(input_array)[0]
        xgb_pred = xgb_model.predict(input_array)[0]
        
        # Get probabilities
        rf_proba = rf_model.predict_proba(input_array)[0]
        xgb_proba = xgb_model.predict_proba(input_array)[0]
        
        # Ensemble prediction (average probabilities)
        avg_proba = (rf_proba + xgb_proba) / 2
        ensemble_pred = np.argmax(avg_proba)
        
        # Get crop name
        crop_name = label_encoder.inverse_transform([ensemble_pred])[0]
        confidence = float(np.max(avg_proba))
        
        return CropPrediction(
            recommended_crop=crop_name,
            model_used="Ensemble (RF + XGBoost)",
            confidence=confidence,
            input_features=features
        )
        
    except Exception as e:
        logger.error(f"Ensemble prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ensemble prediction failed: {str(e)}")

@app.post("/predict/batch", response_model=BatchCropPrediction)
async def predict_batch(
    batch_features: BatchCropFeatures,
    model: str = "xgboost",
    _: bool = Depends(get_model_dependency)
):
    """Make batch predictions for multiple inputs"""
    if model == "random-forest" and rf_model is None:
        raise HTTPException(status_code=503, detail="Random Forest model not available")
    elif model == "xgboost" and xgb_model is None:
        raise HTTPException(status_code=503, detail="XGBoost model not available")
    
    try:
        predictions = []
        selected_model = rf_model if model == "random-forest" else xgb_model
        model_name = "Random Forest" if model == "random-forest" else "XGBoost"
        
        for features in batch_features.features:
            # Convert features to numpy array
            input_array = np.array([[
                features.nitrogen, features.phosphorous, features.potassium,
                features.temperature, features.humidity, features.ph, features.rainfall
            ]])
            
            # Make prediction
            prediction = selected_model.predict(input_array)[0]
            crop_name = label_encoder.inverse_transform([prediction])[0]
            
            # Get confidence
            probabilities = selected_model.predict_proba(input_array)[0]
            confidence = float(np.max(probabilities))
            
            predictions.append(CropPrediction(
                recommended_crop=crop_name,
                model_used=model_name,
                confidence=confidence,
                input_features=features
            ))
        return BatchCropPrediction(
            predictions=predictions,
            total_predictions=len(predictions)
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@app.get("/models/info", response_model=List[ModelInfo])
async def get_model_info():
    """Get information about loaded models"""
    models_info = []
    
    if rf_model is not None:
        models_info.append(ModelInfo(
            model_name="Random Forest",
            accuracy=0.988,  # You can store this value when training
            features=feature_names,
            supported_crops=list(label_encoder.classes_)
        ))
    
    if xgb_model is not None:
        models_info.append(ModelInfo(
            model_name="XGBoost",
            accuracy=0.991,  # You can store this value when training
            features=feature_names,
            supported_crops=list(label_encoder.classes_)
        ))
    
    if not models_info:
        raise HTTPException(status_code=503, detail="No models are currently loaded")
    
    return models_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
