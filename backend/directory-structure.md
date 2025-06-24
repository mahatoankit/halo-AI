# Halo-AI Backend Directory Structure

This document outlines the recommended directory structure for the Halo-AI Django backend project.

## Project Structure

```
halo_ai/
├── manage.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
├── halo_ai/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   └── tests.py
│   ├── crops/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   └── tests.py
│   ├── community/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   └── tests.py
│   ├── sensors/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   └── tests.py
│   └── dashboard/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       ├── forms.py
│       ├── migrations/
│       └── tests.py
├── templates/
│   ├── base.html
│   ├── dashboard/
│   │   ├── farmer_dashboard.html
│   │   ├── technician_dashboard.html
│   │   └── admin_dashboard.html
│   ├── community/
│   │   ├── forum.html
│   │   ├── post_detail.html
│   │   └── create_post.html
│   ├── crops/
│   │   ├── recommendations.html
│   │   └── crop_detail.html
│   └── users/
│       ├── login.html
│       ├── register.html
│       └── profile.html
├── static/
│   ├── css/
│   │   ├── base.css
│   │   ├── dashboard.css
│   │   └── community.css
│   ├── js/
│   │   ├── main.js
│   │   ├── dashboard.js
│   │   └── charts.js
│   └── images/
│       └── logo.png
├── ml_models/
│   ├── __init__.py
│   ├── crop_predictor.py
│   ├── model_trainer.py
│   ├── data_preprocessor.py
│   └── trained_models/
│       └── crop_recommendation_model.pkl
├── firebase_config/
│   ├── __init__.py
│   ├── firebase_client.py
│   ├── firestore_operations.py
│   └── service_account_key.json
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   ├── validators.py
│   └── decorators.py
└── tests/
    ├── __init__.py
    ├── test_users.py
    ├── test_crops.py
    ├── test_community.py
    └── test_sensors.py
```

## Directory Descriptions

### Core Django Files
- **manage.py**: Django's command-line utility
- **requirements.txt**: Python dependencies
- **halo_ai/**: Main project configuration directory

### Apps Directory
- **users/**: User management (farmers, technicians, admins)
- **crops/**: Crop recommendations and related functionality
- **community/**: Social platform features (forums, posts, discussions)
- **sensors/**: IoT sensor data management
- **dashboard/**: Dashboard views for different user types

### Templates & Static Files
- **templates/**: HTML templates organized by app
- **static/**: CSS, JavaScript, and image files

### Machine Learning
- **ml_models/**: ML model implementations and trained models
- **trained_models/**: Serialized ML models for inference

### Firebase Integration
- **firebase_config/**: Firebase configuration and client setup
- **service_account_key.json**: Firebase service account credentials

### Utilities & Tests
- **utils/**: Helper functions and utilities
- **tests/**: Unit tests for the application

## Setup Commands

```bash
# Create virtual environment
python3 -m venv halo_ai_env
source halo_ai_env/bin/activate

# Install dependencies
pip install django firebase-admin scikit-learn pandas numpy

# Create project structure
django-admin startproject halo_ai
cd halo_ai
mkdir apps templates static ml_models firebase_config utils tests

# Create apps
python manage.py startapp users apps/users
python manage.py startapp crops apps/crops
python manage.py startapp community apps/community
python manage.py startapp sensors apps/sensors
python manage.py startapp dashboard apps/dashboard

# Initial setup
python manage.py migrate
python manage.py runserver
```

This structure supports the Halo-AI project's requirements for user management, crop recommendations, community features, IoT sensor integration, and Firebase connectivity.