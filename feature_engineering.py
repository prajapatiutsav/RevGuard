import pandas as pd

# ==========================================
# LOAD CLEANED DATA
# ==========================================

data = pd.read_csv(
    "data/cleaned/recovery_cases_ml.csv"
)

print("Original dataset:")
print(data.shape)


# ==========================================
# SELECT MODEL FEATURES
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
    "customer_tenure_days"
]


# ==========================================
# CREATE X AND y
# ==========================================

X = data[features].copy()

y = data["recovered"].copy()


# ==========================================
# DISPLAY
# ==========================================

print("\n========== FEATURES ==========")

print(X.columns.tolist())

print("\nNumber of features:", len(X.columns))

print("\n========== TARGET ==========")

print(y.value_counts())

print("\nRecovery rate:")

print(y.mean())


# ==========================================
# SAVE MODEL DATA
# ==========================================

model_data = X.copy()

model_data["recovered"] = y

model_data.to_csv(
    "data/cleaned/recovery_model_data.csv",
    index=False
)


print("\n===================================")
print("FEATURE DATASET CREATED")
print("===================================")

print(
    "Saved to: data/cleaned/recovery_model_data.csv"
)

print(
    "Shape:",
    model_data.shape
)