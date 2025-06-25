# 🌾 HALO-AI: Intelligent Crop Recommendation System
# This is Jeevan Branch

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development--Phase-yellow.svg)]()

## 📋 Project Overview

HALO-AI is an intelligent IoT-enabled crop recommendation system that combines machine learning, sensor data simulation, and modern backend architecture to help farmers make data-driven decisions about crop selection. The system leverages trained ML models with 99%+ accuracy to analyze soil conditions, environmental factors, and agricultural parameters, suggesting the most suitable crops for given conditions to promote sustainable agriculture and food security.

### 🎯 Key Features

- **🤖 Advanced ML Models**: XGBoost, Random Forest, and SVM algorithms with 99%+ accuracy
- **📡 IoT Simulation**: Realistic sensor data generation and processing framework
- **�️ Modern Architecture**: Modular FastAPI backend with clean separation of concerns
- **📊 Comprehensive Analysis**: Complete data pipeline with 3 detailed Jupyter notebooks
- **🚀 Production-Ready Models**: Pre-trained models available for immediate deployment
- **⚙️ Automated Setup**: One-command environment setup and API server deployment

## 🏗️ Project Structure

```
Codebase/
├── backend/                       # FastAPI backend service
│   └── app/                       # Application core
│       ├── main.py               # Main FastAPI application entry point
│       ├── __init__.py           # Module initialization
│       └── core/                 # Core configurations
│           └── config.py         # Backend-specific configuration
├── frontend/                      # Web frontend (planned for future development)
├── iot/                          # IoT sensor simulation system
│   ├── __init__.py               # Module initialization
│   ├── sensors/                  # Sensor simulation and hardware interface
│   │   └── soil_sensors.py      # Advanced multi-sensor node simulation
│   └── data_collection/          # Data collection services
│       └── service.py           # Real-time data collection service
├── ml/                           # Machine learning pipeline
│   ├── data/                     # Complete dataset collection
│   │   ├── Crop_recommendation.csv         # Primary training dataset (2,200 samples)
│   │   ├── crop2.csv                      # Secondary crop dataset
│   │   ├── Fertilizer Prediction.xls     # Fertilizer recommendation data
│   │   ├── Crop Recommendation using...   # Extended dataset with weather
│   │   └── excel_format/                 # Formatted Excel versions
│   ├── models/                   # Trained machine learning models
│   │   ├── random_forest_model.pkl       # Random Forest (99.0% accuracy)
│   │   ├── xgboost_model.pkl             # XGBoost (99.2% accuracy) - Best
│   │   └── svm_model.pkl                 # SVM (98.5% accuracy)
│   └── notebooks/                # Complete analysis and training pipeline
│       ├── cropNet.ipynb                 # ML model training & evaluation
│       ├── dataAnalysis.ipynb            # Comprehensive EDA
│       └── CropRecommendationNotebook.ipynb  # Additional analysis
├── shared/                       # Shared components and utilities
│   ├── __init__.py               # Module initialization
│   ├── config.py                # Global configuration and settings
│   └── schemas.py               # Pydantic data models and validation schemas
├── scripts/                      # Automation and utility scripts
│   ├── setup.sh                 # Complete environment setup automation
│   └── start_api.sh             # FastAPI server startup script
├── .env.example                  # Environment configuration template
├── .gitignore                   # Git ignore rules
├── requirements.txt              # Python dependencies and versions
└── README.md                    # Project documentation
```

## 📊 Dataset Features

The system analyzes **7 key agricultural parameters**:

| Feature         | Description                 | Unit       |
| --------------- | --------------------------- | ---------- |
| **N**           | Nitrogen content in soil    | ppm        |
| **P**           | Phosphorous content in soil | ppm        |
| **K**           | Potassium content in soil   | ppm        |
| **Temperature** | Average temperature         | °C         |
| **Humidity**    | Relative humidity           | %          |
| **pH**          | Soil pH level               | 0-14 scale |
| **Rainfall**    | Annual rainfall             | mm         |

## 🌱 Supported Crops

The system can recommend **22 different crops**:

- **Cereals**: Rice, Maize
- **Pulses**: Chickpea, Kidney Beans, Pigeon Peas, Moth Beans, Mung Bean, Black Gram, Lentil
- **Fruits**: Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya
- **Commercial Crops**: Cotton, Jute, Coffee
- **Others**: Coconut

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (Tested with Python 3.11)
- **Git** for version control
- **Virtual environment** (recommended - `venv` or `conda`)
- **Jupyter** for notebook analysis (optional)

### ⚡ Quick Setup (Recommended)

The fastest way to get HALO-AI running:

1. **Clone and setup in one command**

   ```bash
   git clone <repository-url>
   cd Codebase
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

2. **Start the API server**

   ```bash
   ./scripts/start_api.sh
   ```

3. **Access the system**
   - **API Documentation**: `http://localhost:8000/docs` (Interactive Swagger UI)
   - **Health Check**: `http://localhost:8000/health`
   - **API Base**: `http://localhost:8000/`

### 🔧 Manual Setup (Alternative)

If you prefer manual control over the setup process:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env with your preferred settings

# Start the FastAPI server
cd backend/app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 📓 Working with Jupyter Notebooks

To explore the data analysis and model training:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install Jupyter (if not already installed)
pip install jupyter

# Start Jupyter server
jupyter notebook

# Navigate to ml/notebooks/ and explore:
# 1. dataAnalysis.ipynb     - Complete exploratory data analysis
# 2. cropNet.ipynb          - ML model training and evaluation
# 3. CropRecommendationNotebook.ipynb - Additional insights
```

## 📈 Model Performance

| Model             | Validation Accuracy | Test Accuracy | Status              |
| ----------------- | ------------------- | ------------- | ------------------- |
| **Random Forest** | 99.1%               | 99.0%         | ✅ Production Ready |
| **XGBoost**       | 99.3%               | 99.2%         | ✅ Production Ready |
| **SVM**           | 98.8%               | 98.5%         | ✅ Available        |

### 🏆 Best Model: XGBoost

- **Test Accuracy**: 99.2%
- **Low Overfitting**: Excellent generalization
- **Feature Importance**: Rainfall and NPK nutrients most critical

## 📓 System Components

### 🤖 Machine Learning Pipeline (`ml/`)

**Production-Ready Trained Models:**

- ✅ **XGBoost** (99.2% accuracy) - **Primary recommendation model**
- ✅ **Random Forest** (99.0% accuracy) - Robust ensemble method
- ✅ **SVM** (98.5% accuracy) - Support vector classification

**Complete Dataset Collection:**

- **Primary Dataset**: 2,200 samples with 7 environmental features
- **Extended Data**: Weather prediction integration
- **Fertilizer Data**: Additional nutrient recommendation capabilities
- **Multiple Formats**: CSV and Excel formats for different use cases

**Comprehensive Jupyter Analysis:**

- `dataAnalysis.ipynb` - Complete EDA with statistical insights
- `cropNet.ipynb` - ML pipeline development and model comparison
- `CropRecommendationNotebook.ipynb` - Extended analysis and validation

### 🌐 Backend System (`backend/`)

**FastAPI Application Architecture:**

- Modern async Python web framework
- Modular application structure with clean separation
- Environment-based configuration management
- Built-in API documentation (Swagger/OpenAPI)
- Health monitoring and status endpoints

**Current Implementation Status:**

- ✅ Basic FastAPI application structure
- ✅ Configuration management system
- 🚧 API endpoints for model predictions (planned)
- 🚧 Model loading and serving (planned)

### 📡 IoT Integration (`iot/`)

**Advanced Sensor Simulation:**

- Multi-sensor node architecture with location tracking
- Realistic environmental data generation (NPK, pH, temperature, humidity)
- Configurable sensor accuracy and noise simulation
- Batch and real-time data collection capabilities

**Data Collection Service:**

- Async data processing pipeline
- Schema validation with Pydantic models
- Error handling and logging
- Buffer management for efficient processing

### 🔧 Shared Components (`shared/`)

**Configuration Management:**

- Environment-based settings (development/production)
- Path management and directory creation
- API server configuration
- IoT and ML model settings

**Data Models & Validation:**

- Pydantic schemas for type safety
- IoT sensor data structures
- Crop feature models
- API request/response schemas

## 🔮 Making Predictions

### 🚧 Using the API (In Development)

The FastAPI endpoints are currently being implemented. Once complete, you'll be able to make predictions like this:

```bash
# Health check (currently available)
curl http://localhost:8000/health

# Prediction endpoint (planned implementation)
curl -X POST "http://localhost:8000/predict/xgboost" \
     -H "Content-Type: application/json" \
     -d '{
       "nitrogen": 90,
       "phosphorous": 42,
       "potassium": 43,
       "temperature": 20.8,
       "humidity": 82.0,
       "ph": 6.5,
       "rainfall": 202.9
     }'
```

### ✅ Direct Model Usage (Currently Available)

You can immediately use the trained models for predictions:

```python
import joblib
import numpy as np
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Load the best performing model
model_path = "ml/models/xgboost_model.pkl"
model = joblib.load(model_path)

# Example prediction
# Format: [N, P, K, temperature, humidity, ph, rainfall]
input_features = np.array([[90, 42, 43, 20.8, 82.0, 6.5, 202.9]])
prediction = model.predict(input_features)

print(f"Predicted crop index: {prediction[0]}")

# For crop name, you'll need the label encoder from training
# (Available in the notebooks)
```

### 🔬 IoT Data Simulation

Test the IoT sensor simulation:

```python
from iot.sensors.soil_sensors import MultiSensorNode
from iot.data_collection.service import DataCollectionService

# Create sensor node
sensor_node = MultiSensorNode(
    node_id="farm_01",
    latitude=40.7128,
    longitude=-74.0060
)

# Collect data
sensor_data = sensor_node.collect_all_data()
print(f"Collected data: {sensor_data}")

# Use with data collection service
import asyncio

async def test_collection():
    service = DataCollectionService()
    reading = await service.collect_single_reading("farm_01")
    if reading:
        print(f"IoT Reading: {reading}")

# Run the test
asyncio.run(test_collection())
```

## 📊 Data Insights

### Top Feature Importance (Random Forest)

1. **Rainfall** (0.234) - Most critical factor
2. **Potassium** (0.156) - Essential nutrient
3. **Phosphorous** (0.154) - Soil fertility
4. **Nitrogen** (0.142) - Growth factor
5. **Humidity** (0.128) - Environmental condition

### Crop Characteristics

- **High NPK Requirements**: Apple, Grapes, Banana
- **Low NPK Requirements**: Lentil, Orange, Coffee
- **Heat-loving Crops**: Mango, Papaya, Coconut
- **Cool-weather Crops**: Apple, Pomegranate, Lentil

## 🛠️ Development Status

### 📊 Project Status Overview

**✅ Completed Components:**

- **ML Pipeline**: 3 trained models with 99%+ accuracy rates
- **Data Analysis**: Complete EDA with 2,200+ samples across 22 crops
- **IoT Simulation**: Advanced multi-sensor node simulation framework
- **Backend Structure**: FastAPI application architecture setup
- **Configuration**: Environment-based config management system
- **Data Models**: Pydantic schemas for type-safe data validation
- **Automation**: Setup and deployment scripts
- **Documentation**: Comprehensive project documentation

**🚧 In Development:**

- **API Endpoints**: FastAPI routes for model predictions
- **Model Integration**: Loading and serving trained models via API
- **Error Handling**: Robust error handling and logging
- **Testing**: Unit and integration test suite

**📋 Planned for Next Phase:**

- **Frontend Interface**: Web dashboard for predictions and monitoring
- **Database Integration**: Data persistence layer
- **Authentication**: User management and API security
- **Real-time Processing**: Live IoT data streaming
- **Model Management**: A/B testing and model versioning

### 🎯 Current Development Focus

**Priority 1: Complete API Implementation**

- Model loading and prediction endpoints
- Request validation and error handling
- Performance optimization for inference

**Priority 2: Frontend Development**

- Interactive web dashboard
- Real-time prediction interface
- Data visualization components

**Priority 3: Production Features**

- Database integration for data persistence
- User authentication and authorization
- Monitoring and alerting systems

### 🔧 Development Guidelines

**Adding New ML Models:**

```python
# Add to ml/notebooks/cropNet.ipynb
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier

# Gradient Boosting
gb_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3
)
gb_model.fit(X_train, y_train)

# Neural Network
nn_model = MLPClassifier(
    hidden_layer_sizes=(100, 50),
    max_iter=1000,
    alpha=0.01
)
nn_model.fit(X_train, y_train)

# Follow existing evaluation and saving pattern
```

**Extending IoT Sensors:**

```python
# Add to iot/sensors/soil_sensors.py
class WeatherStation:
    """Advanced weather monitoring station"""

    def __init__(self, station_id: str, elevation: float):
        self.station_id = station_id
        self.elevation = elevation

    def get_weather_forecast(self) -> Dict:
        """Get 7-day weather forecast simulation"""
        return {
            "forecast": [...],
            "confidence": 0.85,
            "last_updated": datetime.now()
        }
```

**Project Structure Guidelines:**

- **Backend**: Follow FastAPI best practices with dependency injection
- **Shared**: Keep common utilities and schemas in shared module
- **IoT**: Maintain sensor abstraction for easy hardware integration
- **ML**: Preserve notebook-driven development for reproducibility
- **Scripts**: Add automation for common development tasks

### 🧪 Testing (Planned)

```bash
# Install development dependencies
pip install pytest pytest-asyncio pytest-cov

# Run test suite (when implemented)
pytest tests/ -v

# Run with coverage report
pytest --cov=backend --cov=shared --cov=iot tests/

# Run specific test modules
pytest tests/test_models.py -v
pytest tests/test_api.py -v
```

## 🎯 Use Cases

### 🌾 Precision Agriculture

- **Optimize crop selection** for maximum yield
- **Reduce farming risks** through data-driven decisions
- **Efficient resource utilization** (fertilizers, water)

### 📱 Applications

- **Mobile farming apps** for real-time recommendations
- **Agricultural advisory systems** for extension services
- **Smart farming platforms** for precision agriculture
- **Research tools** for agricultural studies

### 🌍 Impact Areas

- **Food Security**: Improved crop yields
- **Sustainability**: Optimized resource usage
- **Economic**: Reduced crop failure risks
- **Environmental**: Data-driven farming practices

## 🔬 Technical Features

### Data Processing

- **Outlier Handling**: IQR-based robust detection
- **Feature Engineering**: NPK ratios, interaction terms
- **Categorical Encoding**: pH and rainfall classifications
- **Statistical Analysis**: Skewness, kurtosis, variance analysis

### Model Features

- **Cross-validation**: Stratified train/validation/test splits
- **Performance Metrics**: Accuracy, precision, recall, F1-score
- **Visualization**: Confusion matrices, feature importance plots
- **Model Persistence**: Trained models saved for deployment

## 📈 Architecture & Future Roadmap

### �️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   ML Pipeline   │
│   (Planned)     │◄──►│   FastAPI       │◄──►│   Models        │
│                 │    │   (Active)      │    │   (Ready)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   API Layer     │    │   Data Science  │
│   Interface     │    │   & Services    │    │   Notebooks     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                                ▼
                       ┌─────────────────┐
                       │   IoT Sensors   │
                       │   (Simulation)  │
                       └─────────────────┘
```

### 🚀 Development Roadmap

**Phase 1: Core API Development (Current)**

- [ ] Complete FastAPI prediction endpoints
- [ ] Model loading and inference optimization
- [ ] API testing and validation
- [ ] Performance benchmarking

**Phase 2: Frontend & User Experience**

- [ ] React/Vue.js dashboard development
- [ ] Interactive prediction interface
- [ ] Real-time data visualization
- [ ] Mobile-responsive design

**Phase 3: Production & Deployment**

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP/Azure)

**Phase 4: Advanced Features**

- [ ] Real-time IoT hardware integration
- [ ] Weather API integration
- [ ] Geospatial crop mapping
- [ ] Economic optimization models
- [ ] Multi-language support

**Phase 5: Scale & Intelligence**

- [ ] Microservices architecture
- [ ] ML model versioning and A/B testing
- [ ] Automated model retraining
- [ ] Advanced analytics and insights
- [ ] Mobile application (React Native/Flutter)

### 🌐 Deployment Strategy

**Development Environment:**

- Local development with FastAPI dev server
- Jupyter notebooks for ML experimentation
- SQLite for rapid prototyping

**Staging Environment:**

- Docker containers for consistency
- PostgreSQL database
- Redis for caching
- API load testing

**Production Environment:**

- Kubernetes orchestration
- Cloud-managed databases
- CDN for static assets
- Monitoring with Prometheus/Grafana
- Auto-scaling based on demand

## 🤝 Contributing

We welcome contributions to HALO-AI! Here's how you can help improve this agricultural intelligence system:

### 🚀 Getting Started with Contributions

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-improvement`)
3. **Set up development environment** (`./scripts/setup.sh`)
4. **Make your changes** with proper testing
5. **Commit with descriptive messages** (`git commit -m 'Add crop yield prediction feature'`)
6. **Push to your branch** (`git push origin feature/amazing-improvement`)
7. **Open a Pull Request** with detailed description

### 🎯 Priority Contribution Areas

**🔥 High Priority:**

- � **FastAPI Endpoints**: Complete the prediction API implementation
- 🌐 **Frontend Dashboard**: Build the web interface for farmers
- 🧪 **Testing Suite**: Add comprehensive test coverage
- 📊 **Data Visualization**: Create interactive charts and dashboards

**🌟 Medium Priority:**

- 🤖 **New ML Models**: Add ensemble methods or deep learning
- 📡 **IoT Hardware**: Real sensor integration and drivers
- 🌍 **Internationalization**: Multi-language support
- � **Mobile App**: React Native or Flutter application

**💡 Enhancement Ideas:**

- 🛰️ **Satellite Data**: Remote sensing integration
- 🌦️ **Weather APIs**: Real-time weather integration
- 💰 **Economic Models**: Cost-benefit analysis features
- 🔄 **Crop Rotation**: Multi-season planning algorithms

### 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/halo-ai.git
cd halo-ai/Codebase

# Set up development environment
./scripts/setup.sh

# Create feature branch
git checkout -b feature/your-feature-name

# Start development server
./scripts/start_api.sh
```

### � Contribution Guidelines

**Code Standards:**

- Follow PEP 8 for Python code style
- Add type hints for all functions
- Include docstrings for classes and methods
- Use meaningful variable and function names

**Testing Requirements:**

- Add tests for new features
- Ensure existing tests pass
- Aim for >80% code coverage
- Include integration tests for API endpoints

**Documentation:**

- Update README for new features
- Add docstrings and comments
- Include usage examples
- Update API documentation

### 🐛 Bug Reports

Found a bug? Help us fix it:

1. **Check existing issues** to avoid duplicates
2. **Create detailed bug report** with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)
   - Error messages and logs
3. **Add relevant labels** (bug, critical, etc.)

### 💡 Feature Requests

Have an idea for improvement?

1. **Open an issue** with the `enhancement` label
2. **Describe the feature** and its benefits
3. **Provide use cases** and examples
4. **Discuss implementation** approaches

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team & Project Info

**🏆 Idea for Impact Hackathon 2025**

HALO-AI represents our commitment to leveraging cutting-edge technology for sustainable agriculture and food security. This project combines:

- **� Mission**: Empowering farmers with AI-driven crop recommendations
- **🌱 Vision**: Contributing to global food security through intelligent agriculture
- **🚀 Innovation**: Modern ML/IoT architecture for agricultural applications
- **📊 Impact**: 99%+ accurate models trained on comprehensive agricultural datasets

### 🏗️ Technical Excellence

- **Advanced ML Pipeline**: XGBoost, Random Forest, and SVM with 99%+ accuracy
- **Modern Architecture**: FastAPI backend with modular, scalable design
- **IoT Integration**: Comprehensive sensor simulation and data collection framework
- **Data Science**: 3 complete Jupyter notebooks with thorough analysis
- **Production Ready**: Automated setup, deployment scripts, and configuration management

### 🌍 Real-World Impact

- **Precision Agriculture**: Data-driven crop selection for optimal yields
- **Resource Optimization**: Efficient use of fertilizers, water, and land
- **Risk Reduction**: Evidence-based farming decisions to minimize crop failure
- **Sustainability**: Promoting environmentally conscious agricultural practices
- **Food Security**: Contributing to global agricultural productivity and food availability

### 📈 Project Metrics

- **Dataset Size**: 2,200+ agricultural samples
- **Crop Coverage**: 22 different crop types supported
- **Model Accuracy**: 99.2% (XGBoost), 99.0% (Random Forest), 98.5% (SVM)
- **Features Analyzed**: 7 key environmental and soil parameters
- **Code Quality**: Modular architecture with type safety and error handling

## 🙏 Acknowledgments

- **📊 Dataset Source**: [Kaggle Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) - High-quality agricultural data for model training
- **🛠️ Core Technologies**:
  - **Machine Learning**: Scikit-learn, XGBoost, Pandas, NumPy for robust ML pipeline
  - **Web Framework**: FastAPI, Uvicorn for modern async API development
  - **Data Analysis**: Jupyter, Matplotlib, Seaborn for comprehensive data exploration
  - **Validation**: Pydantic for type-safe data models and validation
- **🎓 Inspiration**: UN Sustainable Development Goals, particularly Goal 2 (Zero Hunger) and Goal 15 (Life on Land)
- **🌍 Community**:
  - Open-source machine learning and agricultural technology communities
  - Sustainable agriculture research and precision farming initiatives
  - IoT and sensor technology development communities

### 🔗 Related Resources

- **Agricultural Data**: FAO (Food and Agriculture Organization) datasets
- **ML Frameworks**: Scikit-learn, XGBoost documentation and communities
- **Modern Web APIs**: FastAPI and Pydantic communities
- **Sustainable Agriculture**: Precision agriculture research papers and initiatives

---

**🌱 "Empowering farmers with intelligent, IoT-enabled crop recommendations for a sustainable future"**

---

<div align="center">
  <b>Made with ❤️ for Idea for Impact Hackathon 2025</b>
  <br>
  <em>Building tomorrow's agricultural intelligence today</em>
</div>
