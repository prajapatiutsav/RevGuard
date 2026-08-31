import pandas as pd
from pathlib import Path


# ==========================================
# 1. LOAD RAW DATA
# ==========================================

customers = pd.read_csv("data/customers.csv")
transactions = pd.read_csv("data/transactions.csv")
interactions = pd.read_csv("data/customer_interactions.csv")
outcomes = pd.read_csv("data/recovery_outcomes.csv")

print("Raw data loaded successfully.")


# ==========================================
# 2. REMOVE DUPLICATES
# ==========================================

customers = customers.drop_duplicates(
    subset=["customer_id"]
)

transactions = transactions.drop_duplicates(
    subset=["transaction_id"]
)

interactions = interactions.drop_duplicates(
    subset=["interaction_id"]
)


# ==========================================
# 3. CONVERT DATE COLUMNS
# ==========================================

customers["customer_since"] = pd.to_datetime(
    customers["customer_since"],
    errors="coerce"
)

transactions["timestamp"] = pd.to_datetime(
    transactions["timestamp"],
    errors="coerce"
)

interactions["timestamp"] = pd.to_datetime(
    interactions["timestamp"],
    errors="coerce"
)


# ==========================================
# 4. STANDARDIZE TEXT
# ==========================================

transactions["payment_method"] = (
    transactions["payment_method"]
    .str.lower()
    .str.strip()
)

transactions["failure_reason"] = (
    transactions["failure_reason"]
    .str.lower()
    .str.strip()
)

transactions["status"] = (
    transactions["status"]
    .str.lower()
    .str.strip()
)

customers["subscription_status"] = (
    customers["subscription_status"]
    .str.lower()
    .str.strip()
)

interactions["channel"] = (
    interactions["channel"]
    .str.lower()
    .str.strip()
)

interactions["action"] = (
    interactions["action"]
    .str.lower()
    .str.strip()
)

outcomes["action"] = (
    outcomes["action"]
    .str.lower()
    .str.strip()
)


# ==========================================
# 5. HANDLE INVALID CUSTOMER VALUES
# ==========================================

customers.loc[
    (customers["customer_age"] < 18) |
    (customers["customer_age"] > 100),
    "customer_age"
] = pd.NA


customers.loc[
    customers["total_spend"] < 0,
    "total_spend"
] = pd.NA


customers.loc[
    customers["avg_order_value"] <= 0,
    "avg_order_value"
] = pd.NA


customers.loc[
    customers["purchase_frequency"] < 0,
    "purchase_frequency"
] = pd.NA


customers.loc[
    customers["ltv"] < 0,
    "ltv"
] = pd.NA


# ==========================================
# 6. HANDLE INVALID TRANSACTIONS
# ==========================================

transactions.loc[
    transactions["amount"] <= 0,
    "amount"
] = pd.NA


# Successful transactions should have no failure reason
transactions.loc[
    transactions["status"] == "success",
    "failure_reason"
] = "none"


# ==========================================
# 7. HANDLE RECOVERY OUTCOMES
# ==========================================

# If recovery didn't happen,
# recovered amount must be zero.

outcomes.loc[
    outcomes["recovered"] == 0,
    "recovered_amount"
] = 0


# Recovery amount cannot be negative
outcomes.loc[
    outcomes["recovered_amount"] < 0,
    "recovered_amount"
] = 0


# ==========================================
# 8. KEEP ONLY FAILED TRANSACTIONS
# ==========================================

# For our revenue-recovery model,
# successful transactions are not recovery opportunities.

failed_transactions = transactions[
    transactions["status"] == "failed"
].copy()


# ==========================================
# 9. CONNECT RECOVERY OUTCOMES
# ==========================================

recovery_cases = outcomes.merge(
    failed_transactions[
        [
            "transaction_id",
            "customer_id",
            "amount",
            "payment_method",
            "failure_reason",
            "timestamp"
        ]
    ],
    on="transaction_id",
    how="inner"
)


# ==========================================
# 10. CONNECT CUSTOMER INFORMATION
# ==========================================

recovery_cases = recovery_cases.merge(
    customers[
        [
            "customer_id",
            "customer_age",
            "customer_since",
            "total_purchases",
            "total_spend",
            "avg_order_value",
            "purchase_frequency",
            "subscription_status",
            "ltv"
        ]
    ],
    on="customer_id",
    how="left"
)


# ==========================================
# 11. CUSTOMER INTERACTION FEATURES
# ==========================================

interaction_summary = (
    interactions
    .groupby("customer_id")
    .agg(
        total_interactions=("interaction_id", "count"),
        total_opened=("opened", "sum"),
        total_clicked=("clicked", "sum"),
        total_responded=("responded", "sum")
    )
    .reset_index()
)


# Calculate interaction rates

interaction_summary["open_rate"] = (
    interaction_summary["total_opened"]
    / interaction_summary["total_interactions"]
)

interaction_summary["click_rate"] = (
    interaction_summary["total_clicked"]
    / interaction_summary["total_interactions"]
)

interaction_summary["response_rate"] = (
    interaction_summary["total_responded"]
    / interaction_summary["total_interactions"]
)


# ==========================================
# 12. ADD INTERACTION FEATURES
# ==========================================

recovery_cases = recovery_cases.merge(
    interaction_summary,
    on="customer_id",
    how="left"
)


# Customers with no interaction history
# get zero values.

interaction_columns = [
    "total_interactions",
    "total_opened",
    "total_clicked",
    "total_responded",
    "open_rate",
    "click_rate",
    "response_rate"
]

recovery_cases[interaction_columns] = (
    recovery_cases[interaction_columns]
    .fillna(0)
)


# ==========================================
# 13. CREATE CUSTOMER FATIGUE SCORE
# ==========================================

# Simple transparent score for MVP.
# We will improve this later.

recovery_cases["fatigue_score"] = (
    recovery_cases["total_interactions"] * 5
    + (1 - recovery_cases["response_rate"]) * 30
)

recovery_cases["fatigue_score"] = (
    recovery_cases["fatigue_score"]
    .clip(0, 100)
    .round(2)
)


# ==========================================
# 14. CREATE CUSTOMER TENURE
# ==========================================

today = pd.Timestamp("2026-08-23")

recovery_cases["customer_tenure_days"] = (
    today - recovery_cases["customer_since"]
).dt.days


# ==========================================
# 15. CREATE BASIC RECOVERY FEATURES
# ==========================================

recovery_cases["recovery_value_ratio"] = (
    recovery_cases["recovered_amount"]
    / recovery_cases["amount"]
)

recovery_cases["net_recovered_value"] = (
    recovery_cases["recovered_amount"]
    - recovery_cases["action_cost"]
)


# ==========================================
# 16. HANDLE REMAINING MISSING VALUES
# ==========================================

numeric_columns = recovery_cases.select_dtypes(
    include=["number"]
).columns

recovery_cases[numeric_columns] = (
    recovery_cases[numeric_columns]
    .fillna(0)
)


# ==========================================
# 17. SAVE CLEANED DATA
# ==========================================

output_folder = Path("data/cleaned")

output_folder.mkdir(
    parents=True,
    exist_ok=True
)


customers.to_csv(
    output_folder / "customers_clean.csv",
    index=False
)

transactions.to_csv(
    output_folder / "transactions_clean.csv",
    index=False
)

interactions.to_csv(
    output_folder / "customer_interactions_clean.csv",
    index=False
)

outcomes.to_csv(
    output_folder / "recovery_outcomes_clean.csv",
    index=False
)

recovery_cases.to_csv(
    output_folder / "recovery_cases_ml.csv",
    index=False
)


# ==========================================
# 18. FINAL INFORMATION
# ==========================================

print("\n===================================")
print("CLEANING COMPLETED")
print("===================================")

print("\nCustomers:", customers.shape)
print("Transactions:", transactions.shape)
print("Interactions:", interactions.shape)
print("Outcomes:", outcomes.shape)

print(
    "\nFailed transaction recovery cases:",
    recovery_cases.shape
)

print("\nML dataset columns:")
print(recovery_cases.columns.tolist())

print("\nSaved to:")
print("data/cleaned/")