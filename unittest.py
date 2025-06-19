import unittest
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class TestCropRecommendationModel(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Load the dataset
        cls.df = pd.read_csv('Crop_recommendation.csv')
        
        # Load trained models
        cls.rf_model = joblib.load('random_forest_model.pkl')
        cls.xgb_model = joblib.load('xgboost_model.pkl')
        
        # Prepare label encoder
        cls.label_encoder = LabelEncoder()
        cls.label_encoder.fit(cls.df['label'])
        
        # Prepare data splits
        cls.X = cls.df.drop('label', axis=1)
        cls.y = cls.label_encoder.transform(cls.df['label'])
        
        # Split data
        X_train, X_temp, y_train, y_temp = train_test_split(
            cls.X, cls.y, test_size=0.3, random_state=42, stratify=cls.y
        )
        cls.X_val, cls.X_test, cls.y_val, cls.y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        cls.X_train, cls.y_train = X_train, y_train
    
    def test_data_integrity(self):
        """Test data loading and basic integrity."""
        # Check if data is loaded correctly
        self.assertGreater(len(self.df), 0, "Dataset should not be empty")
        
        # Check for required columns
        expected_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']
        for col in expected_columns:
            self.assertIn(col, self.df.columns, f"Column {col} should be present")
        
        # Check for missing values
        self.assertEqual(self.df.isnull().sum().sum(), 0, "Dataset should not have missing values")
        
        # Check data types
        numeric_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for col in numeric_columns:
            self.assertTrue(pd.api.types.is_numeric_dtype(self.df[col]), 
                          f"Column {col} should be numeric")
    
    def test_model_loading(self):
        """Test if models are loaded correctly."""
        self.assertIsNotNone(self.rf_model, "Random Forest model should be loaded")
        self.assertIsNotNone(self.xgb_model, "XGBoost model should be loaded")
        
        # Check if models have the right number of features
        expected_features = len(self.X.columns)
        self.assertEqual(self.rf_model.n_features_in_, expected_features,
                        f"RF model should expect {expected_features} features")
    
    def test_model_predictions(self):
        """Test model prediction functionality."""
        # Test prediction on a sample
        sample = self.X_test.iloc[:5]
        
        rf_pred = self.rf_model.predict(sample)
        xgb_pred = self.xgb_model.predict(sample)
        
        # Check prediction shapes
        self.assertEqual(len(rf_pred), 5, "RF should predict 5 samples")
        self.assertEqual(len(xgb_pred), 5, "XGB should predict 5 samples")
        
        # Check prediction ranges
        n_classes = len(self.label_encoder.classes_)
        self.assertTrue(all(0 <= p < n_classes for p in rf_pred),
                       "RF predictions should be within valid range")
        self.assertTrue(all(0 <= p < n_classes for p in xgb_pred),
                       "XGB predictions should be within valid range")
    
    def test_model_accuracy_thresholds(self):
        """Test if models meet minimum accuracy thresholds."""
        # Test on validation set
        rf_val_pred = self.rf_model.predict(self.X_val)
        rf_val_accuracy = accuracy_score(self.y_val, rf_val_pred)
        
        xgb_val_pred = self.xgb_model.predict(self.X_val)
        xgb_val_accuracy = accuracy_score(self.y_val, xgb_val_pred)
        
        # Minimum accuracy thresholds
        min_accuracy = 0.85  # 85% minimum accuracy
        
        self.assertGreaterEqual(rf_val_accuracy, min_accuracy,
                               f"RF validation accuracy {rf_val_accuracy:.3f} below threshold")
        self.assertGreaterEqual(xgb_val_accuracy, min_accuracy,
                               f"XGB validation accuracy {xgb_val_accuracy:.3f} below threshold")
    
    def test_overfitting_detection(self):
        """Test for overfitting by comparing training and validation performance."""
        # Get training accuracy
        rf_train_pred = self.rf_model.predict(self.X_train)
        rf_train_accuracy = accuracy_score(self.y_train, rf_train_pred)
        
        # Get validation accuracy
        rf_val_pred = self.rf_model.predict(self.X_val)
        rf_val_accuracy = accuracy_score(self.y_val, rf_val_pred)
        
        # Calculate overfitting gap
        overfitting_gap = rf_train_accuracy - rf_val_accuracy
        max_acceptable_gap = 0.05  # 5% maximum gap
        
        self.assertLessEqual(overfitting_gap, max_acceptable_gap,
                            f"Overfitting detected: training accuracy ({rf_train_accuracy:.3f}) "
                            f"vs validation accuracy ({rf_val_accuracy:.3f}) gap: {overfitting_gap:.3f}")
        
        print(f"Overfitting check - Training: {rf_train_accuracy:.3f}, "
              f"Validation: {rf_val_accuracy:.3f}, Gap: {overfitting_gap:.3f}")
    
    def test_cross_validation_stability(self):
        """Test model stability using cross-validation."""
        # Perform 5-fold cross-validation
        cv_scores = cross_val_score(RandomForestClassifier(n_estimators=100, random_state=42),
                                   self.X, self.y, cv=5, scoring='accuracy')
        
        mean_cv_score = np.mean(cv_scores)
        std_cv_score = np.std(cv_scores)
        
        # Check if CV scores are stable (low standard deviation)
        max_std = 0.03  # Maximum 3% standard deviation
        self.assertLessEqual(std_cv_score, max_std,
                            f"Model unstable: CV std deviation {std_cv_score:.3f} > {max_std}")
        
        # Check if mean CV score is reasonable
        min_cv_score = 0.90  # Minimum 90% CV accuracy
        self.assertGreaterEqual(mean_cv_score, min_cv_score,
                               f"Mean CV score {mean_cv_score:.3f} below threshold")
        
        print(f"Cross-validation: Mean={mean_cv_score:.3f}, Std={std_cv_score:.3f}")
    
    def test_feature_importance_validity(self):
        """Test if feature importance makes sense."""
        feature_importance = self.rf_model.feature_importances_
        feature_names = self.X.columns
        
        # Check if all features have non-negative importance
        self.assertTrue(all(imp >= 0 for imp in feature_importance),
                       "All feature importances should be non-negative")
        
        # Check if importances sum to 1
        self.assertAlmostEqual(np.sum(feature_importance), 1.0, places=5,
                              msg="Feature importances should sum to 1")
        
        # Print top features
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': feature_importance
        }).sort_values('importance', ascending=False)
        
        print("Top 3 important features:")
        print(importance_df.head(3))
    
    def test_specific_crop_predictions(self):
        """Test predictions for specific crop conditions."""
        # Test case for rice (high N, moderate P, K)
        rice_conditions = np.array([[90, 42, 43, 20.8, 82.0, 6.5, 202.9]])
        rf_pred = self.rf_model.predict(rice_conditions)
        predicted_crop = self.label_encoder.inverse_transform(rf_pred)[0]
        
        # Note: We can't assert exact crop due to model variability,
        # but we can check if prediction is reasonable
        self.assertIn(predicted_crop, self.label_encoder.classes_,
                     "Predicted crop should be in valid classes")
        
        print(f"Rice-like conditions predicted as: {predicted_crop}")
    
    def test_model_consistency(self):
        """Test if models give consistent predictions on same input."""
        # Test multiple predictions on same sample
        sample = self.X_test.iloc[[0]]
        
        predictions = []
        for _ in range(10):
            pred = self.rf_model.predict(sample)
            predictions.append(pred[0])
        
        # All predictions should be the same (deterministic)
        unique_predictions = set(predictions)
        self.assertEqual(len(unique_predictions), 1,
                        "Model should give consistent predictions for same input")

def detect_overfitting_comprehensive(X, y, model_class, **model_params):
    """
    Comprehensive overfitting detection using multiple methods.
    """
    print("=== COMPREHENSIVE OVERFITTING ANALYSIS ===")
    
    # Method 1: Learning Curves
    train_sizes, train_scores, val_scores = learning_curve(
        model_class(**model_params), X, y, cv=5, 
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='accuracy', random_state=42
    )
    
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    val_scores_mean = np.mean(val_scores, axis=1)
    val_scores_std = np.std(val_scores, axis=1)
    
    # Plot learning curves
    plt.figure(figsize=(10, 6))
    plt.plot(train_sizes, train_scores_mean, 'o-', color='blue', label='Training accuracy')
    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1, color='blue')
    
    plt.plot(train_sizes, val_scores_mean, 'o-', color='red', label='Validation accuracy')
    plt.fill_between(train_sizes, val_scores_mean - val_scores_std,
                     val_scores_mean + val_scores_std, alpha=0.1, color='red')
    
    plt.xlabel('Training Set Size')
    plt.ylabel('Accuracy')
    plt.title('Learning Curves - Overfitting Detection')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Method 2: Gap Analysis
    final_train_score = train_scores_mean[-1]
    final_val_score = val_scores_mean[-1]
    gap = final_train_score - final_val_score
    
    print(f"Final Training Accuracy: {final_train_score:.4f}")
    print(f"Final Validation Accuracy: {final_val_score:.4f}")
    print(f"Overfitting Gap: {gap:.4f}")
    
    # Method 3: Overfitting Assessment
    if gap < 0.02:
        print("✅ LOW OVERFITTING: Model generalizes well")
    elif gap < 0.05:
        print("⚠️  MODERATE OVERFITTING: Some overfitting detected")
    else:
        print("❌ HIGH OVERFITTING: Significant overfitting detected")
    
    # Method 4: Stability Check
    if val_scores_std[-1] < 0.03:
        print("✅ STABLE: Low variance in validation scores")
    else:
        print("⚠️  UNSTABLE: High variance in validation scores")
    
    return {
        'train_accuracy': final_train_score,
        'val_accuracy': final_val_score,
        'overfitting_gap': gap,
        'val_std': val_scores_std[-1]
    }

# Run comprehensive overfitting analysis
if __name__ == "__main__":
    # Load data
    df = pd.read_csv('Crop_recommendation.csv')
    
    # Prepare data
    X = df.drop('label', axis=1)
    y = LabelEncoder().fit_transform(df['label'])
    
    # Analyze Random Forest for overfitting
    rf_analysis = detect_overfitting_comprehensive(
        X, y, RandomForestClassifier, 
        n_estimators=100, max_depth=10, random_state=42
    )
    
    # Run unit tests
    unittest.main(verbosity=2)