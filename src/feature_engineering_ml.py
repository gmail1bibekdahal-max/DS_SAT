"""
Feature Engineering and Machine Learning Pipeline
Challenge ID: CH24 - MANUFACTURING QUALITY INSIGHT
PrimeForge Manufacturing Ltd.

Performs:
1. Feature Engineering (process deviations, stress indicators, operational intensity)
2. Categorical Encoding
3. Feature Selection & Importance Ranking
4. Predictive Modeling using Random Forest (Classification & Regression)
5. Comprehensive Model Evaluation (Accuracy, F1-Score, ROC-AUC, RMSE)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, mean_squared_error, r2_score
)
from sklearn.preprocessing import LabelEncoder

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def run_ml_pipeline():
    df = pd.read_csv("data/cleaned/cleaned_manufacturing_quality.csv")
    print(f"Loaded {len(df)} records for Feature Engineering & ML.")

    # 1. Feature Engineering
    # Thermal stability deviation
    df["temp_deviation"] = (df["temperature"] - 205.0).abs()
    # Pressure stability deviation
    df["pressure_deviation"] = (df["pressure"] - 5.8).abs()
    # Speed deviation
    df["speed_deviation"] = (df["speed"] - 1500.0).abs()
    # Thermal-Pressure Stress index
    df["stress_index"] = (df["temperature"] * df["pressure"]) / 1000.0
    # Machine wear intensity
    df["machine_wear_index"] = df["operating_hours"] / 1000.0
    # Impurity impact index
    df["impurity_risk_factor"] = df["impurity_pct"] / (df["tensile_strength_mpa"] / 100.0)

    # 2. Categorical Encoding
    cat_cols = ["line", "shift", "machine_type", "age_band", "supplier", "material_grade"]
    df_encoded = df.copy()
    label_encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df_encoded[col + "_enc"] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le

    # Feature List
    features = [
        "quantity", "operating_hours", "temperature", "pressure", "speed",
        "tensile_strength_mpa", "impurity_pct",
        "temp_deviation", "pressure_deviation", "speed_deviation",
        "stress_index", "machine_wear_index", "impurity_risk_factor",
        "line_enc", "shift_enc", "machine_type_enc", "age_band_enc",
        "supplier_enc", "material_grade_enc"
    ]

    # Target definition: High Defect Risk batch (defect rate >= 7.0%)
    # Approximately top 35-40% defect batches
    median_defect_rate = df["defect_rate_pct"].median()
    df_encoded["target_high_defect"] = (df_encoded["defect_rate_pct"] >= median_defect_rate).astype(int)
    
    X = df_encoded[features]
    y = df_encoded["target_high_defect"]
    y_reg = df_encoded["defect_rate_pct"]

    print(f"\nFeature matrix shape: {X.shape}, Target distribution:")
    print(y.value_counts(normalize=True))

    # Split dataset: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    _, _, y_reg_train, y_reg_test = train_test_split(X, y_reg, test_size=0.20, random_state=42)

    # 3. Model Training: Random Forest Classifier
    rf_clf = RandomForestClassifier(n_estimators=150, max_depth=8, min_samples_split=4, random_state=42)
    rf_clf.fit(X_train, y_train)

    # Predictions
    y_pred = rf_clf.predict(X_test)
    y_proba = rf_clf.predict_proba(X_test)[:, 1]

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)

    print("\n=== Random Forest Classifier Performance ===")
    print(f"Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=["Normal/Low Risk", "High Defect Risk"]))

    # Regression model to predict continuous defect rate
    rf_reg = RandomForestRegressor(n_estimators=150, max_depth=8, random_state=42)
    rf_reg.fit(X_train, y_reg_train)
    y_reg_pred = rf_reg.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_reg_test, y_reg_pred))
    r2 = r2_score(y_reg_test, y_reg_pred)
    print(f"=== Defect Rate Regressor Performance ===")
    print(f"RMSE: {rmse:.4f}% defect rate")
    print(f"R²:   {r2:.4f}")

    # 4. Feature Importance Analysis
    importances = pd.Series(rf_clf.feature_importances_, index=features).sort_values(ascending=False)
    print("\n=== Top 10 Most Important Features ===")
    print(importances.head(10))

    # Plot Feature Importance
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=importances.values[:12], y=importances.index[:12], palette="viridis", ax=ax)
    ax.set_title("Random Forest - Top 12 Feature Importances for Defect Prediction", pad=15)
    ax.set_xlabel("Relative Importance Score", fontweight="bold")
    ax.set_ylabel("Engineered & Selected Features", fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "08_feature_importance.png", dpi=300)
    plt.close()

    # Save metrics to summary text
    results = {
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1_Score": f1,
        "ROC_AUC": roc_auc,
        "RMSE": rmse,
        "R2": r2,
        "Top_Features": importances.head(5).to_dict()
    }
    return results

if __name__ == "__main__":
    run_ml_pipeline()
