# 🌾 HALO-AI: Intelligent Crop Recommendation System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 📋 Project Overview

HALO-AI is an intelligent crop recommendation system that leverages machine learning to help farmers make data-driven decisions about crop selection. The system analyzes soil conditions, environmental factors, and agricultural parameters to suggest the most suitable crops for given conditions, promoting sustainable agriculture and food security.

### 🎯 Key Features

- **Smart Crop Prediction**: ML-powered recommendations based on soil and environmental data
- **Multiple ML Models**: Comparison between Random Forest, XGBoost, and SVM algorithms
- **Comprehensive Analysis**: In-depth data exploration and feature engineering
- **Production Ready**: Trained models saved for deployment
- **Visual Analytics**: Rich visualizations for data insights and model performance

## 🏗️ Project Structure

```
Codebase/
├── data/
│   └── Crop_recommendation.csv     # Dataset with soil & environmental parameters
├── notebooks/
│   ├── dataAnalysis.ipynb          # Comprehensive data exploration & EDA
│   └── cropNet.ipynb              # ML model training & evaluation
├── models/                        # Saved trained models (generated)
│   ├── random_forest_model.pkl
│   ├── xgboost_model.pkl
│   └── svm_model.pkl
└── README.md                      # Project documentation
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

```bash
# Required Python packages
pip install pandas numpy matplotlib seaborn scikit-learn xgboost jupyter scipy
```

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Codebase
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt  # If available
   # Or install packages individually as listed above
   ```

3. **Launch Jupyter Notebook**
   ```bash
   jupyter notebook
   ```

### Quick Start

1. **Data Analysis**: Open `notebooks/dataAnalysis.ipynb` for comprehensive EDA
2. **Model Training**: Open `notebooks/cropNet.ipynb` for ML model development
3. **Make Predictions**: Use trained models for crop recommendations

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

## 📓 Notebook Descriptions

### 1. Data Analysis (`dataAnalysis.ipynb`)

**Comprehensive exploratory data analysis and insights**

- ✅ Dataset overview and quality assessment
- ✅ Statistical analysis and distribution visualization
- ✅ Outlier detection and handling (IQR method)
- ✅ Correlation analysis and feature relationships
- ✅ Crop-wise feature analysis
- ✅ Advanced feature engineering
- ✅ Climate and soil condition categorization

**Key Insights:**

- 2,200 samples across 22 crop types
- No missing values, high data quality
- Rainfall most influential feature
- Clear crop clusters based on environmental needs

### 2. Model Training (`cropNet.ipynb`)

**Machine learning pipeline for crop recommendation**

- ✅ Data preprocessing and cleaning
- ✅ Train/Validation/Test split (70/15/15)
- ✅ Multiple ML algorithm comparison
- ✅ Hyperparameter optimization
- ✅ Comprehensive model evaluation
- ✅ Production-ready model artifacts

**Features:**

- Modular training cells for easy model addition
- Detailed performance visualization
- Model comparison dashboard
- Feature importance analysis

## 🔮 Making Predictions

### Using Trained Models

```python
import joblib
import numpy as np

# Load the best model
model = joblib.load('models/xgboost_model.pkl')

# Example prediction
# Format: [N, P, K, temperature, humidity, ph, rainfall]
input_features = np.array([[90, 42, 43, 20.8, 82.0, 6.5, 202.9]])
prediction = model.predict(input_features)

# Convert to crop name
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
# ... load fitted label encoder
crop_name = le.inverse_transform(prediction)[0]
print(f"Recommended crop: {crop_name}")
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

## 🛠️ Development

### Adding New Models

The notebook structure supports easy addition of new ML models:

1. Copy an existing model training cell
2. Modify the algorithm and hyperparameters
3. Add to the `models_performance` dictionary
4. Automatic inclusion in comparison analysis

### Example: Adding Naive Bayes

```python
from sklearn.naive_bayes import GaussianNB

nb_model = GaussianNB()
nb_model.fit(X_train, y_train)
# ... follow the template pattern
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

## 📈 Future Enhancements

### 🚀 Planned Features

- [ ] **Ensemble Methods**: Voting and stacking classifiers
- [ ] **Deep Learning**: Neural network implementations
- [ ] **Real-time API**: REST API for production deployment
- [ ] **Geographic Integration**: Location-based recommendations
- [ ] **Economic Analysis**: Profit optimization models
- [ ] **Crop Rotation**: Multi-season planning
- [ ] **Weather Integration**: Real-time weather data

### 🌐 Deployment Options

- [ ] **Web Application**: Flask/Django interface
- [ ] **Mobile App**: React Native/Flutter
- [ ] **Cloud Deployment**: AWS/Azure/GCP
- [ ] **Edge Computing**: IoT device integration

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Contribution Areas

- 🐛 Bug fixes and improvements
- 📊 New model implementations
- 📈 Performance optimizations
- 📚 Documentation enhancements
- 🧪 Test coverage improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**Idea for Impact Hackathon 2025**

- Project developed for sustainable agriculture solutions
- Focus on data-driven farming recommendations
- Contributing to food security and agricultural innovation


## 🙏 Acknowledgments

- **Dataset**: kaggle
- **Libraries**: Scikit-learn, XGBoost, Pandas, NumPy
- **Inspiration**: Sustainable agriculture and food security goals
- **Community**: Open-source ML and agricultural technology communities

---

**🌱 "Empowering farmers with intelligent crop recommendations for a sustainable future"**

---

<div align="center">
  <b>Made with ❤️ for Idea for Impact Hackathon 2025</b>
</div>
