import pandas as pd

# ==========================================
# 1. LOAD DATA
# ==========================================

customers = pd.read_csv("data/customers.csv")
transactions = pd.read_csv("data/transactions.csv")
interactions = pd.read_csv("data/customer_interactions.csv")
outcomes = pd.read_csv("data/recovery_outcomes.csv")

print("\n========== DATASET SHAPES ==========")

print("Customers:", customers.shape)
print("Transactions:", transactions.shape)
print("Interactions:", interactions.shape)
print("Recovery Outcomes:", outcomes.shape)


# ==========================================
# 2. BASIC INFORMATION
# ==========================================

print("\n========== DATA TYPES ==========")

print("\nCUSTOMERS")
print(customers.dtypes)

print("\nTRANSACTIONS")
print(transactions.dtypes)

print("\nINTERACTIONS")
print(interactions.dtypes)

print("\nOUTCOMES")
print(outcomes.dtypes)


# ==========================================
# 3. MISSING VALUES
# ==========================================

print("\n========== MISSING VALUES ==========")

print("\nCUSTOMERS")
print(customers.isnull().sum())

print("\nTRANSACTIONS")
print(transactions.isnull().sum())

print("\nINTERACTIONS")
print(interactions.isnull().sum())

print("\nOUTCOMES")
print(outcomes.isnull().sum())


# ==========================================
# 4. DUPLICATES
# ==========================================

print("\n========== DUPLICATES ==========")

print(
    "Duplicate Customer IDs:",
    customers["customer_id"].duplicated().sum()
)

print(
    "Duplicate Transaction IDs:",
    transactions["transaction_id"].duplicated().sum()
)

print(
    "Duplicate Interaction IDs:",
    interactions["interaction_id"].duplicated().sum()
)


# ==========================================
# 5. BASIC STATISTICS
# ==========================================

print("\n========== CUSTOMER STATISTICS ==========")

print(customers.describe())


print("\n========== TRANSACTION STATISTICS ==========")

print(transactions.describe())


print("\n========== RECOVERY STATISTICS ==========")

print(outcomes.describe())


# ==========================================
# 6. CATEGORICAL VALUES
# ==========================================

print("\n========== CATEGORICAL VALUES ==========")

print("\nPayment Methods:")
print(transactions["payment_method"].value_counts())

print("\nFailure Reasons:")
print(transactions["failure_reason"].value_counts())

print("\nTransaction Status:")
print(transactions["status"].value_counts())

print("\nSubscription Status:")
print(customers["subscription_status"].value_counts())

print("\nRecovery Actions:")
print(outcomes["action"].value_counts())


# ==========================================
# 7. INVALID VALUES
# ==========================================

print("\n========== INVALID VALUES ==========")

print(
    "Invalid ages:",
    len(customers[
        (customers["customer_age"] < 18) |
        (customers["customer_age"] > 100)
    ])
)

print(
    "Invalid transaction amounts:",
    len(transactions[
        transactions["amount"] <= 0
    ])
)

print(
    "Invalid customer spending:",
    len(customers[
        customers["total_spend"] < 0
    ])
)

print(
    "Invalid LTV:",
    len(customers[
        customers["ltv"] < 0
    ])
)


# ==========================================
# 8. LOGICAL CONSISTENCY
# ==========================================

print("\n========== LOGICAL CONSISTENCY ==========")

# Successful transaction shouldn't have failure reason
invalid_success = transactions[
    (transactions["status"] == "success") &
    (transactions["failure_reason"] != "none")
]

print(
    "Successful transactions with failure reason:",
    len(invalid_success)
)


# Recovered = 0 should have recovered amount = 0
invalid_recovery = outcomes[
    (outcomes["recovered"] == 0) &
    (outcomes["recovered_amount"] != 0)
]

print(
    "Non-recovered transactions with recovered amount:",
    len(invalid_recovery)
)


# Recovered amount should not exceed transaction amount
check_amount = outcomes.merge(
    transactions[["transaction_id", "amount"]],
    on="transaction_id",
    how="left"
)

invalid_amount = check_amount[
    check_amount["recovered_amount"] > check_amount["amount"]
]

print(
    "Recovered amount greater than transaction amount:",
    len(invalid_amount)
)


# ==========================================
# 9. FOREIGN KEY CHECKS
# ==========================================

print("\n========== RELATIONSHIP CHECKS ==========")

invalid_transaction_customers = transactions[
    ~transactions["customer_id"].isin(
        customers["customer_id"]
    )
]

print(
    "Transactions with unknown customers:",
    len(invalid_transaction_customers)
)


invalid_interaction_customers = interactions[
    ~interactions["customer_id"].isin(
        customers["customer_id"]
    )
]

print(
    "Interactions with unknown customers:",
    len(invalid_interaction_customers)
)


invalid_outcome_transactions = outcomes[
    ~outcomes["transaction_id"].isin(
        transactions["transaction_id"]
    )
]

print(
    "Outcomes with unknown transactions:",
    len(invalid_outcome_transactions)
)


# ==========================================
# 10. RECOVERY ANALYSIS
# ==========================================

print("\n========== RECOVERY ANALYSIS ==========")

recovery_by_action = (
    outcomes
    .groupby("action")["recovered"]
    .mean()
    .sort_values(ascending=False)
)

print("\nRecovery rate by action:")
print(recovery_by_action)


analysis = outcomes.merge(
    transactions[
        [
            "transaction_id",
            "failure_reason",
            "amount",
            "payment_method"
        ]
    ],
    on="transaction_id",
    how="left"
)

recovery_by_failure = (
    analysis
    .groupby("failure_reason")["recovered"]
    .mean()
    .sort_values(ascending=False)
)

print("\nRecovery rate by failure reason:")
print(recovery_by_failure)


recovery_by_payment = (
    analysis
    .groupby("payment_method")["recovered"]
    .mean()
    .sort_values(ascending=False)
)

print("\nRecovery rate by payment method:")
print(recovery_by_payment)


# ==========================================
# DONE
# ==========================================

print("\n==========================================")
print("DATA QUALITY CHECK COMPLETED")
print("==========================================")