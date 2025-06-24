"""
Configuration settings for the HALO-AI system
"""

import os
from typing import List
from pathlib import Path


class Settings:
    """Application configuration settings"""

    # Project Information
    PROJECT_NAME: str = "HALO-AI Crop Recommendation System"
    PROJECT_DESCRIPTION: str = (
        "Intelligent IoT-enabled crop recommendation system using machine learning"
    )
    VERSION: str = "2.0.0"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True

    # CORS Configuration
    ALLOWED_HOSTS: List[str] = ["*"]

    # Paths Configuration
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    MODEL_PATH: Path = BASE_DIR / "models"
    DATA_PATH: Path = BASE_DIR / "data"
    LOGS_PATH: Path = BASE_DIR / "logs"

    # Model Configuration
    RANDOM_FOREST_MODEL: str = "random_forest_model.pkl"
    XGBOOST_MODEL: str = "xgboost_model.pkl"
    SVM_MODEL: str = "svm_model.pkl"
    LABEL_ENCODER: str = "label_encoder.pkl"

    # ML Configuration
    FEATURE_NAMES: List[str] = [
        "nitrogen",
        "phosphorous",
        "potassium",
        "temperature",
        "humidity",
        "ph",
        "rainfall",
    ]

    # Supported Crops
    SUPPORTED_CROPS: List[str] = [
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

    # IoT Configuration
    IOT_DEVICE_TIMEOUT: int = 30  # seconds
    IOT_DATA_RETENTION_DAYS: int = 30
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_PREFIX: str = "halo-ai"

    # Database Configuration (for future use)
    DATABASE_URL: str = "sqlite:///./halo_ai.db"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Prediction Confidence Threshold
    MIN_CONFIDENCE_THRESHOLD: float = 0.7

    def __init__(self):
        """Initialize configuration from environment variables"""
        # Load from environment or use defaults
        self.PROJECT_NAME = os.getenv(
            "PROJECT_NAME", "HALO-AI Crop Recommendation System"
        )
        self.DEBUG = os.getenv("DEBUG", "True").lower() == "true"
        # Create required directories
        self.MODEL_PATH.mkdir(exist_ok=True)
        self.DATA_PATH.mkdir(exist_ok=True)
        self.LOGS_PATH.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()
