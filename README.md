# HALO-AI: Intelligent Crop Recommendation System 

**Winner - Idea For Impact 2025 Hackathon | Kings College**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://www.djangoproject.com/)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange.svg)](https://firebase.google.com/docs/firestore)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Problem Statement

Farmers worldwide face critical challenges in crop selection due to:
- **Information Asymmetry**: Limited access to scientific data on optimal crop choices based on soil and environmental conditions
- **Resource Inefficiency**: Suboptimal crop selection leading to poor yields, wasted resources, and economic losses
- **Knowledge Gap**: Lack of real-time expert guidance and community support for agricultural decisions
- **Market Fragmentation**: Difficulty accessing fair markets, quality inputs, and funding opportunities
- **Technology Barrier**: Complex agricultural data remains inaccessible to farmers without technical expertise

These challenges result in reduced agricultural productivity, increased crop failures, and economic hardship for farming communities globally.

## Solution Overview

HALO-AI is a production-ready intelligent agricultural management platform that addresses these challenges through:

- **AI-Driven Crop Recommendations**: Machine learning models (XGBoost, Random Forest, SVM) analyze 7 key parameters (NPK, temperature, humidity, pH, rainfall) to predict optimal crops from 22+ varieties
- **Multi-Role Platform**: Tailored interfaces for farmers, community administrators, technicians, and global administrators
- **Knowledge Exchange**: Community forums, expert consultations, and peer-to-peer knowledge sharing
- **Integrated Marketplace**: Direct access to agricultural products, services, and fair pricing
- **Financial Support**: Centralized information on government grants and funding opportunities
- **IoT Integration**: Real-time sensor data collection and monitoring for precision agriculture
- **Real-Time Data Synchronization**: Firebase-powered backend ensuring instant updates and scalability

## Technical Architecture

HALO-AI employs a modular Django architecture with production-grade components:

```
Application Stack
├── Frontend: Django Templates + Bootstrap CSS + JavaScript
├── Backend: Django 5.2+ with modular app architecture
├── ML Services: XGBoost, Random Forest, SVM models
├── Databases: PostgreSQL (primary) + Firebase Firestore (real-time)
├── IoT Layer: Sensor simulation and data collection framework
└── Deployment: WSGI/ASGI configuration for production readiness
```

### Core Capabilities

**Machine Learning Integration**
- Real-time crop prediction using ensemble ML models
- Support for 22 crop types across cereals, pulses, fruits, and commercial crops
- Prediction accuracy tracking and historical analysis
- Regional optimization based on geographical data

**User Management System**
- Role-based access control (Farmers, Community Admins, Technicians, Global Admins)
- Location-based user profiling with latitude/longitude support
- Account approval workflow and profile management
- Authentication and authorization security

**Community Platform**
- Discussion forums for knowledge sharing
- Expert consultation booking system
- Q&A platform with regional farmer groups
- Success story documentation and best practices

**Agricultural Marketplace**
- Product listings with categorization and filtering
- Service provider directory
- Price comparison and review system
- Location-based supplier discovery

**Analytics & Insights**
- Prediction accuracy metrics and model performance tracking
- Regional crop success rate analysis
- User engagement statistics
- ROI and economic impact assessment

## Project Structure

```
Codebase/
├── backend/                      # Django Application
│   └── haloai/                   # Project Root
│       ├── manage.py             # Django management utility
│       ├── haloai/               # Configuration
│       │   ├── settings.py       # Django settings
│       │   ├── urls.py           # URL routing
│       │   ├── wsgi.py           # WSGI deployment
│       │   └── asgi.py           # ASGI configuration
│       ├── apps/                 # Modular Applications
│       │   ├── analytics/        # Analytics & Reporting
│       │   ├── community/        # Community Forums
│       │   ├── crops/            # Crop Predictions
│       │   ├── dashboard/        # Role-based Dashboards
│       │   ├── experts/          # Expert Consultation
│       │   ├── grants/           # Government Grants
│       │   ├── home/             # Landing Pages
│       │   ├── marketplace/      # Agricultural Marketplace
│       │   ├── sensors/          # IoT Data Management
│       │   └── users/            # User Management
│       ├── services/             # Business Logic
│       │   ├── crop_prediction_service.py
│       │   ├── firebase_service_refactored.py
│       │   ├── real_ml_prediction_service.py
│       │   ├── enhanced_iot_service.py
│       │   └── firestore_user_service.py
│       ├── templates/            # HTML Templates
│       └── static/               # CSS, JavaScript, Images
├── iot/                          # IoT Sensor Framework
│   ├── sensors/                  # Sensor Simulation
│   └── data_collection/          # Data Collection Services
├── ml/                           # Machine Learning
│   ├── data/                     # Training Datasets
│   ├── models/                   # Trained Models
│   └── notebooks/                # Jupyter Notebooks
├── env/                          # Virtual Environment
├── requirements.txt              # Dependencies
└── firebase-service-account.json # Firebase Configuration
```

## Django Applications

### Core Applications

| Application | Purpose | Key Features |
|------------|---------|--------------|
| **users** | User management and authentication | Multi-role system, location-based profiles, approval workflow |
| **crops** | Crop prediction and recommendations | ML-powered predictions, history tracking, regional analysis |
| **community** | Social platform for farmers | Forums, discussions, Q&A, knowledge sharing |
| **marketplace** | Agricultural products and services | Product listings, price comparison, reviews |
| **experts** | Expert consultation platform | Booking system, expert profiles, consultation history |
| **grants** | Government grants and funding | Eligibility checker, application tracking, documentation support |
| **analytics** | Data insights and reporting | Prediction accuracy, usage statistics, regional trends |
| **sensors** | IoT sensor data management | Sensor registration, data visualization, health monitoring |
| **dashboard** | Role-specific interfaces | Customized dashboards for each user role |
| **home** | Public landing pages | Homepage, about, contact information |

## Machine Learning Pipeline

### Model Architecture

The system employs an ensemble approach with three ML models:

1. **XGBoost** (Primary Model)
   - Gradient boosting for high accuracy
   - Handles non-linear relationships effectively
   - Production-optimized for real-time predictions

2. **Random Forest**
   - Ensemble method for robust predictions
   - Reduces overfitting through bagging
   - Provides feature importance insights

3. **Support Vector Machine (SVM)**
   - Classification for discrete crop categories
   - Effective in high-dimensional spaces
   - Complementary predictions to ensemble models

### Input Parameters

The models analyze seven critical agricultural parameters:

| Parameter | Description | Unit |
|-----------|-------------|------|
| **N** | Nitrogen content in soil | kg/ha |
| **P** | Phosphorus content in soil | kg/ha |
| **K** | Potassium content in soil | kg/ha |
| **Temperature** | Average temperature | °C |
| **Humidity** | Relative humidity | % |
| **pH** | Soil pH level | 0-14 scale |
| **Rainfall** | Annual rainfall | mm |

### Supported Crops

The system provides recommendations for 22 crop types:

**Cereals**: Rice, Maize  
**Pulses**: Chickpea, Kidney Beans, Pigeon Peas, Moth Beans, Mung Bean, Black Gram, Lentil  
**Fruits**: Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya  
**Commercial**: Cotton, Jute, Coffee, Coconut

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Firebase account with Firestore enabled
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Codebase
   ```

2. **Set up Python environment**
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/Mac
   # env\Scripts\activate   # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

   Required environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/haloai_db
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   FIREBASE_CREDENTIALS_PATH=firebase-service-account.json
   FIREBASE_PROJECT_ID=your-project-id
   ```

5. **Set up database**
   ```bash
   cd backend/haloai
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main Application: `http://localhost:8000/`
   - Admin Panel: `http://localhost:8000/admin/`
   - Crop Predictions: `http://localhost:8000/crop-prediction/`

### Firebase Setup

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Enable Firestore Database
3. Generate service account key (Settings → Service accounts → Generate new private key)
4. Save as `firebase-service-account.json` in project root
5. Update `.env` with Firebase project details

## Application Features

### User Workflows

**Farmer Workflow**
1. Register with location details
2. Input soil and environmental parameters (manual or IoT)
3. Receive AI-powered crop recommendations
4. Access community forums and expert consultations
5. Browse marketplace for agricultural products
6. Track prediction history and outcomes

**Community Admin Workflow**
1. Manage regional farmers and data
2. Input environmental data for region
3. Moderate community discussions
4. Review regional analytics and trends
5. Coordinate grant opportunities

**Technician Workflow**
1. Collect field data and sensor readings
2. Monitor IoT equipment status
3. Provide technical support to farmers
4. Validate data quality
5. Generate technical reports

**Global Admin Workflow**
1. Oversee platform operations
2. Manage user approvals and roles
3. Monitor system analytics
4. Verify expert credentials
5. Administer grants and funding programs

### Key URLs

| Feature | URL Path | Description |
|---------|----------|-------------|
| Home | `/` | Landing page |
| Authentication | `/auth/` | Login, register, profile |
| Crop Predictions | `/crop-prediction/` | AI recommendations |
| Community | `/community/` | Forums and discussions |
| Marketplace | `/marketplace/` | Products and services |
| Experts | `/experts/` | Consultation platform |
| Grants | `/grants-and-offers/` | Funding opportunities |
| Analytics | `/analytics/` | Insights and reporting |
| Sensors | `/sensors/` | IoT monitoring |
| Dashboard | `/dashboard/` | Role-based dashboards |
| Admin | `/admin/` | Django admin interface |

## Technology Stack

### Backend
- **Django 5.2+**: Web framework
- **PostgreSQL 15+**: Primary database
- **Firebase Firestore**: Real-time NoSQL database
- **Python 3.12**: Core language

### Machine Learning
- **XGBoost**: Primary ML model
- **Scikit-learn**: ML framework
- **Pandas & NumPy**: Data processing
- **Random Forest & SVM**: Ensemble methods

### Frontend
- **Django Templates**: Server-side rendering
- **Bootstrap CSS**: Responsive design
- **JavaScript**: Interactive features

### Cloud Services
- **Firebase**: Real-time sync and authentication
- **Google Cloud**: Infrastructure support

### Development Tools
- **Git**: Version control
- **Virtual Environment**: Dependency isolation
- **WSGI/ASGI**: Production deployment

## Testing

```bash
# Run full test suite
python manage.py test

# Test specific application
python manage.py test apps.crops

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

### Production Configuration

1. **Set production environment variables**
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com
   ```

2. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

3. **Use production database**
   - Configure PostgreSQL with connection pooling
   - Set up database backups

4. **Deploy with WSGI server**
   ```bash
   gunicorn haloai.wsgi:application
   ```

5. **Configure web server**
   - Nginx reverse proxy
   - SSL/TLS certificates
   - Static file serving

### Production Checklist

- [ ] Environment variables configured
- [ ] Debug mode disabled
- [ ] Allowed hosts set
- [ ] Static files collected
- [ ] Database migrations applied
- [ ] Superuser created
- [ ] Firebase credentials configured
- [ ] HTTPS enabled
- [ ] Monitoring and logging configured
- [ ] Backup system implemented

## Impact & Use Cases

### Target Users

- **Small and Medium Farmers**: Primary beneficiaries seeking data-driven crop guidance
- **Agricultural Departments**: Government agencies supporting farmers
- **Agricultural Cooperatives**: Organizations managing farmer groups
- **Research Institutions**: Universities studying agricultural practices
- **Agricultural Businesses**: Companies serving the farming community
- **NGOs**: Organizations working in agricultural development
- **Policy Makers**: Government officials creating agricultural policies

### Real-World Impact

- **Food Security**: Improved crop yields and production efficiency
- **Sustainability**: Optimized resource usage and environmental protection
- **Economic Growth**: Increased farmer income through better crop selection
- **Education**: Knowledge transfer and capacity building
- **Digital Inclusion**: Technology accessibility for rural communities
- **Community Development**: Strengthening agricultural networks

## Contributing

We welcome contributions to HALO-AI. This project represents a production-ready platform that can make meaningful impact in agricultural communities.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Set up development environment
4. Make changes with proper testing
5. Follow code standards (PEP 8, type hints, docstrings)
6. Commit with descriptive messages (`git commit -m 'Add feature'`)
7. Push to branch (`git push origin feature/improvement`)
8. Open a Pull Request with detailed description

### Priority Areas

**High Priority**
- Comprehensive test coverage
- Mobile responsiveness improvements
- Multi-language support (i18n)
- Performance optimization and caching
- Security enhancements and audit trails

**Medium Priority**
- Advanced analytics and visualization
- ML model improvements and deep learning
- Satellite imagery integration
- Real-time chat and messaging
- Email/SMS notification system

**Enhancement Ideas**
- Mobile application (React Native/Flutter)
- Weather API integration
- Economic analysis and ROI calculations
- Crop rotation planning algorithms
- GPS-based field mapping

### Code Standards

- Follow PEP 8 guidelines
- Add type annotations for functions
- Include comprehensive docstrings
- Write tests for new features
- Use clear commit messages
- All changes require code review

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

**MIT License Summary**
- Commercial use allowed
- Modification allowed
- Distribution allowed
- Private use allowed
- License and copyright notice required
- No warranty provided

## Acknowledgments

### Idea for Impact Hackathon 2025

HALO-AI was developed for the Idea for Impact Hackathon 2025 at Kings College, representing our commitment to using technology for sustainable agriculture and global food security.

**Project Mission**: Empowering farmers worldwide with AI-driven agricultural intelligence to promote sustainable farming practices, increase crop yields, and ensure food security for future generations.

### Data & Research
- Open-source agricultural and crop recommendation datasets
- Scientific research on precision agriculture
- Government agricultural statistics and regional data

### Technology
- Django Foundation and open-source community
- Firebase for real-time infrastructure
- Scikit-learn ML community
- PostgreSQL development team

### Inspiration
- UN Sustainable Development Goals (Goal 2: Zero Hunger, Goal 15: Life on Land)
- Precision agriculture movement
- Global food security initiatives
- Agricultural innovation communities

---

**Bridging technology and agriculture to cultivate a sustainable future**

Made for Idea for Impact Hackathon 2025 | Kings College

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black.svg)](#)
[![Django](https://img.shields.io/badge/Built%20with-Django-green.svg)](https://www.djangoproject.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-blue.svg)](#)
