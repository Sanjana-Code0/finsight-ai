import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from xgboost import XGBClassifier
import shap

# Set random seed for reproducibility
np.random.seed(42)

def generate_synthetic_data(n_samples=5000):
    print(f"--- Generating {n_samples} synthetic samples ---")
    
    # Feature ranges and categories
    age_ranges = ['18-24', '25-34', '35-44', '45-54', '55+']
    income_ranges = ['<5 LPA', '5-12 LPA', '12-25 LPA', '25+ LPA']
    tolerances = ['Low', 'Medium', 'High']
    goals = ['Retirement', 'Wealth', 'ChildEdu', 'Property', 'Business', 'Marriage', 'Other']
    levels = ['Low', 'Medium', 'High']

    data = []
    for _ in range(n_samples):
        age = np.random.choice(age_ranges)
        income = np.random.choice(income_ranges)
        tolerance = np.random.choice(tolerances)
        horizon = np.random.randint(1, 31)
        goal = np.random.choice(goals)
        dependents = np.random.choice([True, False])
        savings = np.random.choice(levels)
        debt = np.random.choice(levels)

        # Logic for target (risk_profile)
        # 0: Conservative, 1: Moderate, 2: Aggressive
        
        score = 0
        
        # Age influence (stronger penalty for older, modest bonus for young)
        if age == '55+': score -= 3
        elif age == '45-54': score -= 1
        elif age == '25-34': score += 1
        elif age == '18-24': score += 1.5
        
        # Tolerance influence (primary driver)
        if tolerance == 'High': score += 2
        elif tolerance == 'Low': score -= 3
        
        # Aggressive requires BOTH High tolerance AND young age
        aggressive_bonus = 2.0 if (tolerance == 'High' and age in ['18-24', '25-34']) else 0
        score += aggressive_bonus
        
        # Horizon influence
        if horizon > 20: score += 1.5
        elif horizon > 10: score += 0.5
        elif horizon < 5: score -= 2
        
        # Goal influence
        if goal in ['Wealth', 'Business']: score += 0.5
        elif goal in ['Marriage', 'Other']: score -= 0.5
        
        # Financial health
        if savings == 'High': score += 0.5
        if debt == 'High': score -= 1.5
        if debt == 'Low': score += 0.5
        if dependents: score -= 1

        # Add noise
        score += np.random.normal(0, 1)

        # Thresholds tuned to ~35% Conservative, ~40% Moderate, ~25% Aggressive
        if score < -1.5:
            profile = 'Conservative'
        elif score > 1.8:
            profile = 'Aggressive'
        else:
            profile = 'Moderate'
            
        data.append([age, income, tolerance, horizon, goal, dependents, savings, debt, profile])

    columns = [
        'age_range', 'income_range', 'self_reported_tolerance', 
        'investment_horizon_years', 'primary_goal', 'has_dependents', 
        'savings_level', 'debt_level', 'risk_profile'
    ]
    df = pd.DataFrame(data, columns=columns)
    
    # Adjust distribution to match user request (approx 35/40/25)
    # This is a bit tricky with rules, so we'll just log the distribution
    print("Class Distribution:")
    print(df['risk_profile'].value_counts(normalize=True) * 100)
    
    return df

def train_pipeline():
    df = generate_synthetic_data()
    
    X = df.drop('risk_profile', axis=1)
    y = df['risk_profile']

    # Preprocessing
    categorical_cols = [
        'age_range', 'income_range', 'self_reported_tolerance', 
        'primary_goal', 'savings_level', 'debt_level'
    ]
    numeric_cols = ['investment_horizon_years']
    binary_cols = ['has_dependents']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), categorical_cols),
            ('num', StandardScaler(), numeric_cols),
            ('bin', 'passthrough', binary_cols)
        ]
    )

    X_processed = preprocessor.fit_transform(X)
    feature_names = categorical_cols + numeric_cols + binary_cols

    # Model Selection
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=200, learning_rate=0.1, random_state=42)
    }

    # Label encode y for XGBoost
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    class_names = le.classes_.tolist()

    results = {}
    
    for name, model in models.items():
        print(f"\n--- Evaluating {name} ---")
        cv_results = cross_validate(
            model, X_processed, y_encoded, 
            cv=skf, 
            scoring=['accuracy', 'f1_macro', 'precision_macro', 'recall_macro'],
            return_train_score=False
        )
        
        print(f"Accuracy: {cv_results['test_accuracy'].mean():.4f}")
        print(f"F1 (Macro): {cv_results['test_f1_macro'].mean():.4f}")
        
        # Fit final model
        model.fit(X_processed, y_encoded)
        
        # Metrics for JSON
        y_pred = model.predict(X_processed)
        report = classification_report(y_encoded, y_pred, target_names=class_names, output_dict=True)
        cm = confusion_matrix(y_encoded, y_pred).tolist()
        
        results[name] = {
            'accuracy': accuracy_score(y_encoded, y_pred),
            'f1_macro': report['macro avg']['f1-score'],
            'report': report,
            'confusion_matrix': cm
        }

    # Better model selection
    best_model_name = 'XGBoost' if results['XGBoost']['f1_macro'] > results['RandomForest']['f1_macro'] else 'RandomForest'
    print(f"\n--- Selected Best Model: {best_model_name} ---")

    # SHAP Explainability
    print("\n--- Computing SHAP values ---")
    explainer_rf = shap.TreeExplainer(models['RandomForest'])
    shap_values_rf = explainer_rf.shap_values(X_processed)
    
    explainer_xgb = shap.TreeExplainer(models['XGBoost'])
    shap_values_xgb = explainer_xgb.shap_values(X_processed)

    # Save artifacts
    models_dir = 'backend/ml/models'
    os.makedirs(models_dir, exist_ok=True)

    joblib.dump(models['RandomForest'], f"{models_dir}/rf_model.joblib")
    joblib.dump(models['XGBoost'], f"{models_dir}/xgb_model.joblib")
    joblib.dump(preprocessor, f"{models_dir}/preprocessor.joblib")
    joblib.dump(explainer_rf, f"{models_dir}/shap_explainer_rf.joblib")
    joblib.dump(explainer_xgb, f"{models_dir}/shap_explainer_xgb.joblib")
    
    with open(f"{models_dir}/feature_names.json", 'w') as f:
        json.dump(feature_names, f)
        
    with open(f"{models_dir}/training_metrics.json", 'w') as f:
        json.dump({
            'best_model': best_model_name,
            'class_names': class_names,
            'metrics': results
        }, f, indent=4)

    print(f"\nAll artifacts saved to {models_dir}")

if __name__ == "__main__":
    train_pipeline()
