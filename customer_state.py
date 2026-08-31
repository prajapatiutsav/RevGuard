import pandas as pd


# ==========================================
# 1. LOAD DATA
# ==========================================

customers = pd.read_csv(
    "data/customers.csv"
)

transactions = pd.read_csv(
    "data/transactions.csv"
)

interactions = pd.read_csv(
    "data/customer_interactions.csv"
)

outcomes = pd.read_csv(
    "data/recovery_outcomes.csv"
)


# ==========================================
# 2. CONVERT DATES
# ==========================================

customers["customer_since"] = pd.to_datetime(
    customers["customer_since"]
)

transactions["timestamp"] = pd.to_datetime(
    transactions["timestamp"]
)

interactions["timestamp"] = pd.to_datetime(
    interactions["timestamp"]
)


# ==========================================
# 3. BUILD CUSTOMER STATE
# ==========================================

def build_customer_state(transaction_id):

    # --------------------------------------
    # FIND TRANSACTION
    # --------------------------------------

    transaction = transactions[
        transactions["transaction_id"] == transaction_id
    ]

    if transaction.empty:

        raise ValueError(
            f"Transaction {transaction_id} not found."
        )

    transaction = transaction.iloc[0]


    # --------------------------------------
    # MAKE SURE TRANSACTION FAILED
    # --------------------------------------

    if transaction["status"] != "failed":

        raise ValueError(
            f"Transaction {transaction_id} "
            f"is not a failed transaction."
        )


    customer_id = transaction["customer_id"]

    transaction_time = transaction["timestamp"]


    # --------------------------------------
    # CUSTOMER PROFILE
    # --------------------------------------

    customer = customers[
        customers["customer_id"] == customer_id
    ]

    if customer.empty:

        raise ValueError(
            f"Customer {customer_id} not found."
        )

    customer = customer.iloc[0]


    # --------------------------------------
    # PREVIOUS TRANSACTION HISTORY
    # --------------------------------------

    previous_transactions = transactions[
        (transactions["customer_id"] == customer_id)
        &
        (transactions["timestamp"] < transaction_time)
    ]


    previous_failures = (
        previous_transactions["status"]
        .eq("failed")
        .sum()
    )


    previous_successes = (
        previous_transactions["status"]
        .eq("success")
        .sum()
    )


    # --------------------------------------
    # PREVIOUS RECOVERY HISTORY
    # --------------------------------------

    # Connect outcomes to their transactions
    # so we know which customer they belonged to.

    outcome_history = outcomes.merge(
        transactions[
            [
                "transaction_id",
                "customer_id",
                "timestamp"
            ]
        ],
        on="transaction_id",
        how="left",
        suffixes=("_outcome", "_transaction")
    )

    previous_recoveries = outcome_history[
        (outcome_history["customer_id"] == customer_id)
        &
        (
             outcome_history["timestamp"]
             < transaction_time
        )
        &
        (outcome_history["recovered"] == 1)
   ]

    previous_recovery_count = len(
        previous_recoveries
    )


    # --------------------------------------
    # INTERACTION HISTORY
    # --------------------------------------

    previous_interactions = interactions[
        (interactions["customer_id"] == customer_id)
        &
        (interactions["timestamp"] < transaction_time)
    ]


    total_interactions = len(
        previous_interactions
    )


    total_opened = (
        previous_interactions["opened"]
        .sum()
    )


    total_clicked = (
        previous_interactions["clicked"]
        .sum()
    )


    total_responded = (
        previous_interactions["responded"]
        .sum()
    )


    # --------------------------------------
    # INTERACTION RATES
    # --------------------------------------

    if total_interactions > 0:

        open_rate = (
            total_opened / total_interactions
        )

        click_rate = (
            total_clicked / total_interactions
        )

        response_rate = (
            total_responded / total_interactions
        )

    else:

        open_rate = 0

        click_rate = 0

        response_rate = 0


    # --------------------------------------
    # FATIGUE SCORE
    # --------------------------------------

    fatigue_score = (
        total_interactions * 5
        +
        (1 - response_rate) * 30
    )

    fatigue_score = max(
        0,
        min(100, fatigue_score)
    )


    # --------------------------------------
    # CUSTOMER TENURE
    # --------------------------------------

    customer_tenure_days = (
        transaction_time
        - customer["customer_since"]
    ).days


    # --------------------------------------
    # PREVIOUS RECOVERY RATE
    # --------------------------------------

    if previous_failures > 0:

        previous_recovery_rate = (
            previous_recovery_count
            / previous_failures
        )

    else:

        previous_recovery_rate = 0


    # --------------------------------------
    # FINAL CUSTOMER STATE
    # --------------------------------------

    state = {

        "customer_id":
            int(customer_id),

        "transaction_id":
            int(transaction_id),

        "amount":
            float(transaction["amount"]),

        "payment_method":
            transaction["payment_method"],

        "failure_reason":
            transaction["failure_reason"],

        "customer_age":
            int(customer["customer_age"]),

        "total_purchases":
            int(customer["total_purchases"]),

        "total_spend":
            float(customer["total_spend"]),

        "avg_order_value":
            float(customer["avg_order_value"]),

        "purchase_frequency":
            float(customer["purchase_frequency"]),

        "subscription_status":
            customer["subscription_status"],

        "ltv":
            float(customer["ltv"]),

        "total_interactions":
            int(total_interactions),

        "open_rate":
            float(open_rate),

        "click_rate":
            float(click_rate),

        "response_rate":
            float(response_rate),

        "fatigue_score":
            float(round(fatigue_score, 2)),

        "customer_tenure_days":
            int(customer_tenure_days),

        "previous_failures":
            int(previous_failures),

        "previous_successes":
            int(previous_successes),

        "previous_recoveries":
            int(previous_recovery_count),

        "previous_recovery_rate":
            float(
                round(
                    previous_recovery_rate,
                    4
                )
            )
    }


    return state


# ==========================================
# 4. TEST CUSTOMER STATE
# ==========================================

if __name__ == "__main__":

    transaction_id = 29154

    state = build_customer_state(
        transaction_id
    )


    print("\n==========================================")
    print("         CUSTOMER STATE")
    print("==========================================")

    for key, value in state.items():

        print(
            f"{key:25} : {value}"
        )
        