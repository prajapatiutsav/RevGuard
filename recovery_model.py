import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

from xgboost import XGBClassifier

import joblib


# ==========================================
# 1. LOAD DATA
# ==========================================

data = pd.read_csv(
    "data/cleaned/recovery_model_data.csv"
)

print("Dataset loaded.")
print("Shape:", data.shape)


# ==========================================
# 2. SEPARATE FEATURES AND TARGET
# ==========================================

X = data.drop(
    columns=["recovered"]
)

y = data["recovered"]


print("\nFeatures:")
print(X.columns.tolist())

print("\nTarget distribution:")
print(y.value_counts())

print("\nRecovery rate:")
print(round(y.mean() * 100, 2), "%")


# ==========================================
# 3. IDENTIFY COLUMN TYPES
# ==========================================

categorical_features = [
    "payment_method",
    "failure_reason",
    "subscription_status"
]

numerical_features = [
    "amount",
    "customer_age",
    "total_purchases",
    "total_spend",
    "avg_order_value",
    "purchase_frequency",
    "ltv",
    "total_interactions",
    "open_rate",
    "click_rate",
    "response_rate",
    "fatigue_score",
    "customer_tenure_days"
]


# ==========================================
# 4. NUMERICAL PIPELINE
# ==========================================

numerical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)


# ==========================================
# 5. CATEGORICAL PIPELINE
# ==========================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


# ==========================================
# 6. PREPROCESSOR
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numerical",
            numerical_pipeline,
            numerical_features
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# ==========================================
# 7. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# 8. XGBOOST MODEL
# ==========================================

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42
)


# ==========================================
# 9. COMPLETE PIPELINE
# ==========================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            model
        )
    ]
)


# ==========================================
# 10. TRAIN
# ==========================================

print("\nTraining XGBoost model...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed!")


# ==========================================
# 11. PREDICTIONS
# ==========================================

y_pred = pipeline.predict(X_test)

y_probability = pipeline.predict_proba(
    X_test
)[:, 1]


# ==========================================
# 12. EVALUATION
# ==========================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred
)

recall = recall_score(
    y_test,
    y_pred
)

f1 = f1_score(
    y_test,
    y_pred
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)


print("\n===================================")
print("MODEL PERFORMANCE")
print("===================================")

print(
    f"Accuracy  : {accuracy:.4f}"
)

print(
    f"Precision : {precision:.4f}"
)

print(
    f"Recall    : {recall:.4f}"
)

print(
    f"F1 Score  : {f1:.4f}"
)

print(
    f"ROC-AUC   : {roc_auc:.4f}"
)


# ==========================================
# 13. CLASSIFICATION REPORT
# ==========================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# ==========================================
# 14. CONFUSION MATRIX
# ==========================================

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ==========================================
# 15. SAVE MODEL
# ==========================================

joblib.dump(
    pipeline,
    "recovery_model.pkl"
)

print(
    "\nModel saved as: recovery_model.pkl"
)


# ==========================================
# 16. TEST WITH ONE EXAMPLE
# ==========================================

example = pd.DataFrame([
    {
        "amount": 8000,
        "payment_method": "upi",
        "failure_reason": "temporary_bank_issue",

        "customer_age": 28,
        "total_purchases": 18,
        "total_spend": 65000,
        "avg_order_value": 3600,
        "purchase_frequency": 8.5,

        "subscription_status": "active",

        "ltv": 70000,

        "total_interactions": 2,
        "open_rate": 0.8,
        "click_rate": 0.4,
        "response_rate": 0.5,

        "fatigue_score": 25,

        "customer_tenure_days": 900
    }
])


probability = pipeline.predict_proba(
    example
)[0][1]


print("\n===================================")
print("EXAMPLE PREDICTION")
print("===================================")

print(
    f"Recovery Probability: {probability * 100:.2f}%"
)
