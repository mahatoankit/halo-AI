# HALO-AI: Intelligent Crop Recommendation System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Latest-orange.svg)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-Latest-green.svg)](https://xgboost.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌾 Overview

HALO-AI is an intelligent crop recommendation system that leverages machine learning algorithms to suggest the most suitable crops based on soil and environmental conditions. The system analyzes multiple agricultural parameters including soil nutrients (N, P, K), temperature, humidity, pH levels, and rainfall to provide accurate crop recommendations.

## 🎯 Features

- **Multi-parameter Analysis**: Considers 7 key agricultural factors
- **Advanced ML Models**: Implements Random Forest and XGBoost algorithms
- **High Accuracy**: Achieves >95% prediction accuracy
- **Outlier Detection**: Robust data preprocessing with IQR-based outlier removal
- **Comprehensive Visualization**: Detailed EDA with distribution plots and correlation analysis
- **Model Comparison**: Performance evaluation across multiple metrics
- **Easy Deployment**: Saved models ready for production use

## 📊 Dataset

The system uses a comprehensive crop recommendation dataset containing:

| Feature     | Description                 | Unit        |
| ----------- | --------------------------- | ----------- |
| N           | Nitrogen content in soil    | ppm         |
| P           | Phosphorous content in soil | ppm         |
| K           | Potassium content in soil   | ppm         |
| Temperature | Average temperature         | °C          |
| Humidity    | Relative humidity           | %           |
| pH          | Soil pH level               | 0-14 scale  |
| Rainfall    | Annual rainfall             | mm          |
| Label       | Recommended crop            | Categorical |

**Supported Crops**: 22 different crop types including rice, wheat, cotton, coconut, and more.

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
pip package manager
```

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd Codebase
```

2. **Create virtual environment**

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install dependencies**

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost joblib openpyxl
```

### Usage

#### Data Preparation

```python
# Convert Excel to CSV (if needed)
python src/data_transform.py
```

#### Model Training

```python
# Run the complete pipeline
jupyter notebook notebooks/cropNet.ipynb
```

#### Making Predictions

```python
import joblib
import numpy as np

# Load trained model
model = joblib.load('random_forest_model.pkl')

# Example prediction
features = np.array([[90, 42, 43, 20.9, 82.0, 6.5, 202.9]])
prediction = model.predict(features)
print(f"Recommended crop: {prediction}")
```

## 🏗️ Project Structure

```
Codebase/
├── src/
│   └── data_transform.py      # Data preprocessing utilities
├── notebooks/
│   └── cropNet.ipynb          # Main ML pipeline notebook
├── models/                    # Saved model files (generated)
│   ├── random_forest_model.pkl
│   └── xgboost_model.pkl
├── data/                      # Dataset files
│   ├── crop2.xlsx
│   └── Crop_recommendation.csv
├── README.md                  # Project documentation
└── .gitignore                # Git ignore rules
```

## 🔬 Model Performance

| Model             | Validation Accuracy | Test Accuracy | Key Strengths                       |
| ----------------- | ------------------- | ------------- | ----------------------------------- |
| **Random Forest** | 99.1%               | 98.8%         | High interpretability, robust       |
| **XGBoost**       | 99.3%               | 99.1%         | Superior performance, fast training |

### Feature Importance (Random Forest)

1. **Rainfall** (0.3245) - Most influential factor
2. **Potassium (K)** (0.2134) - Critical soil nutrient
3. **Phosphorous (P)** (0.1987) - Essential for plant growth
4. **Humidity** (0.1456) - Environmental condition
5. **Temperature** (0.0892) - Climate factor
6. **pH** (0.0845) - Soil acidity level
7. **Nitrogen (N)** (0.0441) - Soil fertility indicator

## 📈 Data Processing Pipeline

1. **Data Loading**: Import from Excel/CSV sources
2. **Exploratory Data Analysis**: Statistical summaries and visualizations
3. **Outlier Detection**: IQR-based outlier identification and removal
4. **Data Splitting**: 70% training, 15% validation, 15% testing
5. **Model Training**: Random Forest and XGBoost implementation
6. **Performance Evaluation**: Accuracy, confusion matrix, classification reports
7. **Model Persistence**: Save trained models for deployment

## 🔧 API Reference

### Core Functions

#### `remove_outliers_iqr(df, feature_columns)`

Removes outliers using the Interquartile Range method.

**Parameters:**

- `df`: Input DataFrame
- `feature_columns`: List of columns to process

**Returns:** Cleaned DataFrame

#### Model Prediction Example

```python
# Input format: [N, P, K, temperature, humidity, pH, rainfall]
input_data = [[90, 42, 43, 20.87, 82.00, 6.5, 202.9]]
prediction = model.predict(input_data)
```

## 📊 Visualization Features

- **Distribution Analysis**: Histograms with KDE for all features
- **Outlier Detection**: Box plots for anomaly identification
- **Correlation Matrix**: Feature relationship analysis
- **Confusion Matrix**: Model performance visualization
- **Feature Importance**: Variable significance ranking
- **Performance Comparison**: Model accuracy benchmarking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Dataset contributors for comprehensive agricultural data
- Scikit-learn and XGBoost communities for excellent ML libraries
- Agricultural domain experts for validation insights

## 📞 Support

For questions and support:

- Create an issue in the repository
- Contact the development team
- Check the documentation in `/notebooks/cropNet.ipynb`

---

**Built with ❤️ for sustainable agriculture and food security**
