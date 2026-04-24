import os
import json
import joblib
import pandas as pd
import numpy as np

# Resolve models directory relative to this file's location:
# - Local: backend/ml/../ml/models  → backend/ml/models ✓
# - Docker (WORKDIR /app): /app/ml/../ml/models → /app/ml/models ✓
_ML_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_MODELS_DIR = os.path.join(_ML_DIR, 'models')

class PredictionService:
    def __init__(self, models_dir=None):
        self.models_dir = models_dir or _DEFAULT_MODELS_DIR
        self.artifacts = {}
        self._load_artifacts()

    def _load_artifacts(self):
        """Lazy load and cache model artifacts."""
        try:
            metrics_path = os.path.join(self.models_dir, 'training_metrics.json')
            if not os.path.exists(metrics_path):
                print("[WARNING] No models found. Please run training first.")
                return

            with open(metrics_path, 'r') as f:
                self.artifacts['metrics'] = json.load(f)

            with open(os.path.join(self.models_dir, 'feature_names.json'), 'r') as f:
                self.artifacts['feature_names'] = json.load(f)

            self.artifacts['preprocessor'] = joblib.load(os.path.join(self.models_dir, 'preprocessor.joblib'))
            
            # Load the selected best model
            best_model_name = self.artifacts['metrics']['best_model']
            model_file = 'xgb_model.joblib' if best_model_name == 'XGBoost' else 'rf_model.joblib'
            explainer_file = 'shap_explainer_xgb.joblib' if best_model_name == 'XGBoost' else 'shap_explainer_rf.joblib'
            
            self.artifacts['model'] = joblib.load(os.path.join(self.models_dir, model_file))
            self.artifacts['explainer'] = joblib.load(os.path.join(self.models_dir, explainer_file))
            self.artifacts['best_model_name'] = best_model_name
            
        except Exception as e:
            print(f"[ERROR] Error loading artifacts: {e}")

    def _prepare_input(self, user_input):
        """Converts raw input dict to processed DataFrame, handling missing values."""
        # Define expected columns and their defaults
        defaults = {
            'age_range': '35-44',
            'income_range': '5-12 LPA',
            'self_reported_tolerance': 'Medium',
            'investment_horizon_years': 10,
            'primary_goal': 'Other',
            'has_dependents': False,
            'savings_level': 'Medium',
            'debt_level': 'Medium'
        }

        # Merge input with defaults
        data = {key: user_input.get(key, defaults[key]) for key in defaults}
        df = pd.DataFrame([data])
        
        # Ensure correct types
        df['investment_horizon_years'] = df['investment_horizon_years'].astype(float)
        df['has_dependents'] = df['has_dependents'].astype(bool)
        
        return df

    def predict(self, user_input):
        if 'model' not in self.artifacts:
            self._load_artifacts()
            if 'model' not in self.artifacts:
                return {"error": "Model not loaded"}

        df = self._prepare_input(user_input)
        X_processed = self.artifacts['preprocessor'].transform(df)
        
        # Prediction
        model = self.artifacts['model']
        probs = model.predict_proba(X_processed)[0]
        prediction_idx = np.argmax(probs)
        confidence = float(probs[prediction_idx])
        
        class_names = self.artifacts['metrics']['class_names']
        predicted_class = class_names[prediction_idx]

        # SHAP Values for this instance
        explainer = self.artifacts['explainer']
        # Note: For multi-class, SHAP returns a list of arrays (one per class)
        # We take the SHAP values for the predicted class
        shap_values_all_classes = explainer.shap_values(X_processed)
        
        # In newer SHAP/XGBoost, it might be a single array for binary or a list for multiclass
        if isinstance(shap_values_all_classes, list):
            shap_instance = shap_values_all_classes[prediction_idx][0]
        else:
            # For XGBoost, it might return a 3D array or similar depending on version
            # If 2D (samples, features), it's binary or consolidated
            if len(shap_values_all_classes.shape) == 3:
                shap_instance = shap_values_all_classes[0, :, prediction_idx]
            else:
                shap_instance = shap_values_all_classes[0]

        feature_names = self.artifacts['feature_names']
        shap_dict = {name: float(val) for name, val in zip(feature_names, shap_instance)}
        
        # Sort top 5 features by absolute importance
        top_5 = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

        return {
            "predicted_class": predicted_class,
            "confidence_score": round(confidence, 4),
            "probabilities": {class_names[i]: round(float(probs[i]), 4) for i in range(len(class_names))},
            "shap_values": shap_dict,
            "top_5_features": top_5,
            "model_used": self.artifacts['best_model_name']
        }

    def get_global_importance(self):
        """Returns mean absolute SHAP values for all features."""
        if 'explainer' not in self.artifacts:
            return {}
            
        # We don't want to recompute for all data, but we can return the feature names 
        # as a placeholder or load from a saved global importance if we added that to train.py
        # For now, let's use the feature importance from the model itself as a proxy 
        # or just return a message.
        
        model = self.artifacts['model']
        feature_names = self.artifacts['feature_names']
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            return {name: float(imp) for name, imp in zip(feature_names, importances)}
        
        return {}

if __name__ == "__main__":
    # Test prediction
    service = PredictionService()
    sample_input = {
        "age_range": "25-34",
        "income_range": "25+ LPA",
        "self_reported_tolerance": "High",
        "investment_horizon_years": 20,
        "primary_goal": "Wealth",
        "has_dependents": False,
        "savings_level": "High",
        "debt_level": "Low"
    }
    result = service.predict(sample_input)
    print(json.dumps(result, indent=4))
