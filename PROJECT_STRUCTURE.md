# 🌾 HALO-AI Agricultural Management System

## 📁 Project Structure

```
Codebase/
├── .env                    # Environment variables (not in version control)
├── .git/                   # Git repository
├── .gitignore             # Git ignore rules
├── .vscode/               # VS Code settings
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── firebase-service-account.json  # Firebase credentials (not in version control)
├── PROJECT_STRUCTURE.md   # This file
│
├── backend/               # Django Backend Application
│   └── haloai/
│       ├── manage.py      # Django management script
│       ├── apps/          # Django applications
│       │   ├── analytics/ # Analytics and reporting
│       │   ├── community/ # Community features
│       │   ├── crops/     # Crop management
│       │   ├── dashboard/ # Dashboard views
│       │   ├── experts/   # Expert consultation
│       │   ├── grants/    # Government grants
│       │   ├── home/      # Home page
│       │   ├── marketplace/ # Product marketplace
│       │   ├── sensors/   # IoT sensor management
│       │   └── users/     # User management
│       ├── haloai/        # Django project settings
│       │   ├── __init__.py
│       │   ├── asgi.py
│       │   ├── settings.py
│       │   ├── urls.py
│       │   └── wsgi.py
│       ├── services/      # Business logic services
│       │   ├── crop_prediction_service.py
│       │   ├── enhanced_iot_service.py
│       │   ├── enhanced_weather_service.py
│       │   ├── firebase_service_refactored.py
│       │   ├── firestore_user_service.py
│       │   ├── iot_data_service.py
│       │   └── real_ml_prediction_service.py
│       ├── static/        # Static files (CSS, JS, images)
│       └── templates/     # HTML templates
│
├── env/                   # Python virtual environment (not in version control)
└── iot/                   # IoT data collection modules
    ├── __init__.py
    ├── data_collection/
    │   └── service.py
    └── sensors/
        └── soil_sensors.py
```

## 🚀 Quick Start

1. **Activate virtual environment:**

   ```bash
   source env/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**

   - Copy `.env.example` to `.env`
   - Add your database and Firebase credentials

4. **Run migrations:**

   ```bash
   cd backend/haloai
   python manage.py migrate
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```

## 🧩 Core Features

- **🌱 Crop Management**: ML-powered crop recommendations
- **🌡️ IoT Integration**: Real-time sensor data monitoring
- **📊 Dashboard**: Comprehensive farm analytics
- **🛒 Marketplace**: Agricultural product trading
- **👥 Community**: Farmer networking and support
- **💰 Grants**: Government scheme integration
- **🎯 Predictions**: Weather and yield forecasting

## 🛠️ Technology Stack

- **Backend**: Django 5.2+
- **Database**: PostgreSQL
- **ML/AI**: scikit-learn, XGBoost, pandas
- **IoT**: Firebase Firestore
- **Frontend**: Django Templates + Modern CSS/JS
- **Weather**: OpenMeteo API
- **Authentication**: Django Auth + Custom profiles

## 📈 Development

The codebase is now clean and production-ready:

- ✅ No cache files or temporary artifacts
- ✅ Organized dependencies
- ✅ Proper Git configuration
- ✅ Modular architecture
- ✅ Comprehensive documentation

## 🔧 Maintenance

Regular cleanup commands:

```bash
# Remove Python cache files
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -type f -delete

# Update dependencies
pip list --outdated
pip install --upgrade package_name
```
