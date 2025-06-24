"""
Shared schemas and data models for the HALO-AI system
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ModelType(str, Enum):
    """Supported ML model types"""

    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost"
    SVM = "svm"
    ENSEMBLE = "ensemble"


class CropFeatures(BaseModel):
    """Input features for crop prediction"""

    nitrogen: float = Field(
        ..., ge=0, le=200, description="Nitrogen content in soil (ppm)"
    )
    phosphorous: float = Field(
        ..., ge=0, le=150, description="Phosphorous content in soil (ppm)"
    )
    potassium: float = Field(
        ..., ge=0, le=250, description="Potassium content in soil (ppm)"
    )
    temperature: float = Field(
        ..., ge=-10, le=50, description="Average temperature (°C)"
    )
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
                "rainfall": 202.9,
            }
        }


class IoTSensorData(BaseModel):
    """IoT sensor data structure"""

    device_id: str = Field(..., description="Unique device identifier")
    timestamp: str = Field(..., description="ISO timestamp of measurement")
    soil_nitrogen: float = Field(..., description="Soil nitrogen level (ppm)")
    soil_phosphorous: float = Field(..., description="Soil phosphorous level (ppm)")
    soil_potassium: float = Field(..., description="Soil potassium level (ppm)")
    soil_ph: float = Field(..., description="Soil pH level")
    ambient_temperature: float = Field(..., description="Ambient temperature (°C)")
    humidity: float = Field(..., description="Relative humidity (%)")
    rainfall: Optional[float] = Field(None, description="Rainfall in mm (if available)")
    location: Optional[dict] = Field(None, description="GPS coordinates")


class BatchCropFeatures(BaseModel):
    """Batch input for multiple predictions"""

    features: List[CropFeatures] = Field(..., min_items=1, max_items=100)


class CropPrediction(BaseModel):
    """Single crop prediction response"""

    recommended_crop: str
    model_used: str
    confidence: Optional[float] = None
    input_features: CropFeatures
    timestamp: Optional[str] = None


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
    model_type: ModelType


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    message: str
    models_loaded: bool
    timestamp: str


class ApiResponse(BaseModel):
    """Generic API response wrapper"""

    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


# Constants
SUPPORTED_CROPS = [
    "apple",
    "banana",
    "blackgram",
    "chickpea",
    "coconut",
    "coffee",
    "cotton",
    "grapes",
    "jute",
    "kidneybeans",
    "lentil",
    "maize",
    "mango",
    "mothbeans",
    "mungbean",
    "muskmelon",
    "orange",
    "papaya",
    "pigeonpeas",
    "pomegranate",
    "rice",
    "watermelon",
]

FEATURE_NAMES = [
    "nitrogen",
    "phosphorous",
    "potassium",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
]
