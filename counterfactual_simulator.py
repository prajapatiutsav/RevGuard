import pandas as pd
import numpy as np
import joblib

from revguard_engine import ACTIONS


# ==========================================
# CONFIGURATION
# ==========================================

DATA_FILE = "data/cleaned/recovery_cases_ml.csv"

N_CUSTOMERS = 5000

RANDOM_STATE = 42

ACTIONS_LIST = [
    "retry",
    "payment_link",
    "whatsapp",
    "email",
    "voice_call",
    "human_escalation"
]

ACTION_COSTS = {
    "retry": 8,
    "payment_link": 12,
    "whatsapp": 18,
    "email": 5,
    "voice_call": 90,
    "human_escalation": 250
}


FEATURES = [
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
# LOAD DATA
# ==========================================

data = pd.read_csv(DATA_FILE)

print("\n==========================================")
print("     FAST COUNTERFACTUAL SIMULATION")
print("==========================================")

print(
    f"\nOriginal records: {len(data):,}"
)


sample = data.sample(
    n=min(N_CUSTOMERS, len(data)),
    random_state=RANDOM_STATE
).copy()


print(
    f"Simulation population: {len(sample):,}"
)


# ==========================================
# LOAD MODEL
# ==========================================

action_model = joblib.load(
    "action_model.pkl"
)


# ==========================================
# FUNCTION: BATCH PREDICTION
# ==========================================

def predict_action_probability(
    population,
    action
):

    model_input = population[
        FEATURES
    ].copy()

    model_input["action"] = action

    probabilities = (
        action_model
        .predict_proba(model_input)[:, 1]
    )

    return probabilities


# ==========================================
# FIXED STRATEGIES
# ==========================================

results = []


for action in ACTIONS_LIST:

    print(
        f"\nSimulating: {action}"
    )

    probabilities = (
        predict_action_probability(
            sample,
            action
        )
    )

    expected_revenue = (
        sample["amount"].values
        * probabilities
    )

    total_revenue = (
        expected_revenue.sum()
    )

    total_cost = (
        ACTION_COSTS[action]
        * len(sample)
    )

    net_recovery = (
        total_revenue
        - total_cost
    )

    results.append({

        "strategy": action,

        "expected_recovery":
            total_revenue,

        "action_cost":
            total_cost,

        "net_recovery":
            net_recovery,

        "average_probability":
            probabilities.mean()
    })


# ==========================================
# REVGUARD
# ==========================================

print(
    "\nSimulating: REVGUARD"
)


# Store scores for every action

action_scores = []

action_probabilities = []


for action in ACTIONS_LIST:

    probabilities = (
        predict_action_probability(
            sample,
            action
        )
    )

    action_probabilities.append(
        probabilities
    )

    # Expected money recovered

    expected_recovery = (
        sample["amount"].values
        * probabilities
    )

    # Cost

    cost = ACTION_COSTS[action]

    # Fatigue penalty

    fatigue_penalty = (
        sample["fatigue_score"].values
        / 100
    ) * ACTIONS[action]["fatigue_penalty"]

    # RevGuard economic score

    score = (
        expected_recovery
        - cost
        - fatigue_penalty
    )

    action_scores.append(score)


# ==========================================
# FIND BEST ACTION PER CUSTOMER
# ==========================================

scores_matrix = np.column_stack(
    action_scores
)


best_indices = (
    np.argmax(
        scores_matrix,
        axis=1
    )
)


best_actions = [
    ACTIONS_LIST[i]
    for i in best_indices
]


best_probabilities = np.array([
    action_probabilities[i][row]
    for row, i
    in enumerate(best_indices)
])


# ==========================================
# CALCULATE REVGUARD RESULTS
# ==========================================

amounts = sample[
    "amount"
].values


expected_recovery = (
    amounts
    * best_probabilities
)


selected_costs = np.array([
    ACTION_COSTS[action]
    for action in best_actions
])


total_expected_recovery = (
    expected_recovery.sum()
)


total_action_cost = (
    selected_costs.sum()
)


total_net_recovery = (
    total_expected_recovery
    - total_action_cost
)


results.append({

    "strategy": "REVGUARD",

    "expected_recovery":
        total_expected_recovery,

    "action_cost":
        total_action_cost,

    "net_recovery":
        total_net_recovery,

    "average_probability":
        best_probabilities.mean()
})


# ==========================================
# RESULTS
# ==========================================

results_df = pd.DataFrame(
    results
)


print("\n==========================================")
print("          SIMULATION RESULTS")
print("==========================================")


display_df = results_df.copy()


display_df[
    "expected_recovery"
] = display_df[
    "expected_recovery"
].map(
    lambda x: f"₹{x:,.2f}"
)


display_df[
    "action_cost"
] = display_df[
    "action_cost"
].map(
    lambda x: f"₹{x:,.2f}"
)


display_df[
    "net_recovery"
] = display_df[
    "net_recovery"
].map(
    lambda x: f"₹{x:,.2f}"
)


display_df[
    "average_probability"
] = display_df[
    "average_probability"
].map(
    lambda x: f"{x:.2%}"
)


print(
    display_df.to_string(
        index=False
    )
)


# ==========================================
# BEST STRATEGY
# ==========================================

best_row = (
    results_df
    .loc[
        results_df[
            "net_recovery"
        ].idxmax()
    ]
)


print("\n==========================================")
print("          BEST STRATEGY")
print("==========================================")


print(
    f"Strategy: "
    f"{best_row['strategy']}"
)


print(
    f"Expected recovery: "
    f"₹{best_row['expected_recovery']:,.2f}"
)


print(
    f"Action cost: "
    f"₹{best_row['action_cost']:,.2f}"
)


print(
    f"Net recovery: "
    f"₹{best_row['net_recovery']:,.2f}"
)


# ==========================================
# REVGUARD ACTION DISTRIBUTION
# ==========================================

print("\n==========================================")
print("      REVGUARD ACTION DISTRIBUTION")
print("==========================================")


distribution = (
    pd.Series(best_actions)
    .value_counts()
)


print(
    distribution
)


print("\nSimulation completed successfully! 🚀")