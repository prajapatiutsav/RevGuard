import pandas as pd
import joblib

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
    roc_auc_score
)

from xgboost import XGBClassifier


# ==========================================
# 1. LOAD DATA
# ==========================================

data = pd.read_csv(
    "data/cleaned/recovery_cases_ml.csv"
)

print("Dataset loaded.")
print("Shape:", data.shape)


# ==========================================
# 2. FEATURES
# ==========================================

features = [
    "amount",
    "payment_method",
    "failure_reason",

    "customer_age",
    "total_purchases",
    "total_spend",
    "avg_order_value",
    "purchase_frequency",
    "subscription_status",
    "ltv",

    "total_interactions",
    "open_rate",
    "click_rate",
    "response_rate",
    "fatigue_score",
    "customer_tenure_days",

    "action"
]


X = data[features].copy()

y = data["recovered"].copy()


# ==========================================
# 3. CATEGORICAL FEATURES
# ==========================================

categorical_features = [
    "payment_method",
    "failure_reason",
    "subscription_status",
    "action"
]


# ==========================================
# 4. NUMERICAL FEATURES
# ==========================================

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
# 5. PREPROCESSING
# ==========================================

numerical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)


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
# 6. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ==========================================
# 7. MODEL
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
# 8. PIPELINE
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
# 9. TRAIN
# ==========================================

print("\nTraining action-aware model...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed!")


# ==========================================
# 10. EVALUATE
# ==========================================

y_pred = pipeline.predict(X_test)

y_probability = pipeline.predict_proba(
    X_test
)[:, 1]


print("\n===================================")
print("ACTION MODEL PERFORMANCE")
print("===================================")

print(
    f"Accuracy  : {accuracy_score(y_test, y_pred):.4f}"
)

print(
    f"Precision : {precision_score(y_test, y_pred):.4f}"
)

print(
    f"Recall    : {recall_score(y_test, y_pred):.4f}"
)

print(
    f"F1 Score  : {f1_score(y_test, y_pred):.4f}"
)

print(
    f"ROC-AUC   : {roc_auc_score(y_test, y_probability):.4f}"
)


# ==========================================
# 11. SAVE MODEL
# ==========================================

joblib.dump(
    pipeline,
    "action_model.pkl"
)

print("\nSaved:")
print("action_model.pkl")