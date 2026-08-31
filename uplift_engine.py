import pandas as pd
import numpy as np
import joblib


# ==========================================
# CONFIGURATION
# ==========================================

DATA_FILE = (
    "data/cleaned/recovery_cases_ml.csv"
)

MODEL_FILE = "action_model.pkl"


ACTIONS = [
    "retry",
    "payment_link",
    "whatsapp",
    "email",
    "voice_call",
    "human_escalation"
]


# Cost of performing each recovery action
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

data = pd.read_csv(
    DATA_FILE
)


print("\n==========================================")
print("       INCREMENTAL RECOVERY ENGINE")
print("==========================================")


print(
    f"\nRecords available: "
    f"{len(data):,}"
)


# ==========================================
# LOAD MODEL
# ==========================================

action_model = joblib.load(
    MODEL_FILE
)


# ==========================================
# PREDICT PROBABILITY FOR ACTION
# ==========================================

def predict_probability(
    population,
    action
):

    model_input = population[
        FEATURES
    ].copy()

    model_input["action"] = action

    probability = (
        action_model
        .predict_proba(model_input)[:, 1]
    )

    return probability


# ==========================================
# CALCULATE ACTION OPPORTUNITY
# ==========================================

def calculate_opportunity(
    population
):

    population = population.copy()


    # --------------------------------------
    # OBSERVED ACTION
    # --------------------------------------

    observed_actions = (
        population["action"]
        .values
    )


    # --------------------------------------
    # TRANSACTION AMOUNTS
    # --------------------------------------

    amounts = (
        population["amount"]
        .values
        .astype(float)
    )


    # --------------------------------------
    # PREDICTIONS FOR ALL ACTIONS
    # --------------------------------------

    probabilities = {}


    for action in ACTIONS:

        probabilities[action] = (
            predict_probability(
                population,
                action
            )
        )


    # --------------------------------------
    # PROBABILITY MATRIX
    # --------------------------------------

    probability_matrix = np.column_stack(
        [
            probabilities[action]
            for action in ACTIONS
        ]
    )


    # Matrix shape:

    # rows    = transactions
    # columns = recovery actions


    # ======================================
    # ACTION COST MATRIX
    # ======================================

    cost_matrix = np.array([
        ACTION_COSTS[action]
        for action in ACTIONS
    ])


    # ======================================
    # TRANSACTION AMOUNT MATRIX
    # ======================================

    amount_matrix = (
        amounts[:, np.newaxis]
    )


    # ======================================
    # EXPECTED RECOVERED REVENUE
    # ======================================

    expected_revenue_matrix = (
        probability_matrix
        *
        amount_matrix
    )


    # ======================================
    # NET ECONOMIC VALUE
    # ======================================

    # Expected recovered revenue
    # minus cost of performing action

    net_value_matrix = (
        expected_revenue_matrix
        -
        cost_matrix
    )


    # ======================================
    # BEST ECONOMIC ACTION
    # ======================================

    # IMPORTANT:
    #
    # We are NO LONGER using:
    #
    # np.argmax(probability_matrix)
    #
    # because that would only maximize
    # recovery probability.
    #
    # RevGuard should maximize:
    #
    # expected recovery - action cost

    best_indices = np.argmax(
        net_value_matrix,
        axis=1
    )


    best_actions = np.array([
        ACTIONS[index]
        for index in best_indices
    ])


    # ======================================
    # BEST ACTION PROBABILITY
    # ======================================

    best_probabilities = (
        probability_matrix[
            np.arange(len(population)),
            best_indices
        ]
    )


    # ======================================
    # BEST EXPECTED REVENUE
    # ======================================

    best_expected_revenue = (
        expected_revenue_matrix[
            np.arange(len(population)),
            best_indices
        ]
    )


    # ======================================
    # BEST ACTION COST
    # ======================================

    best_cost = (
        cost_matrix[
            best_indices
        ]
    )


    # ======================================
    # BEST NET ECONOMIC VALUE
    # ======================================

    best_net_value = (
        net_value_matrix[
            np.arange(len(population)),
            best_indices
        ]
    )


    # ======================================
    # OBSERVED ACTION PROBABILITY
    # ======================================

    observed_probabilities = np.array([

        probabilities[action][i]

        for i, action
        in enumerate(observed_actions)

    ])


    # ======================================
    # OBSERVED EXPECTED REVENUE
    # ======================================

    observed_expected_revenue = (
        amounts
        *
        observed_probabilities
    )


    # ======================================
    # OBSERVED ACTION COST
    # ======================================

    observed_cost = np.array([

        ACTION_COSTS.get(
            action,
            0
        )

        for action in observed_actions

    ])


    # ======================================
    # OBSERVED NET ECONOMIC VALUE
    # ======================================

    observed_net_value = (
        observed_expected_revenue
        -
        observed_cost
    )


    # ======================================
    # PROBABILITY UPLIFT
    # ======================================

    probability_uplift = (
        best_probabilities
        -
        observed_probabilities
    )


    # ======================================
    # REVENUE UPLIFT
    # ======================================

    # Difference in expected recovered
    # revenue between best action and
    # observed action.

    incremental_revenue = (
        best_expected_revenue
        -
        observed_expected_revenue
    )


    # ======================================
    # COST DIFFERENCE
    # ======================================

    incremental_cost = (
        best_cost
        -
        observed_cost
    )


    # ======================================
    # NET INCREMENTAL VALUE
    # ======================================

    # This is the most important metric.
    #
    # Best economic value
    # minus
    # current economic value

    net_incremental_value = (
        best_net_value
        -
        observed_net_value
    )


    # ======================================
    # CREATE RESULT
    # ======================================

    result = population[
        [
            "transaction_id",
            "customer_id",
            "amount",
            "action"
        ]
    ].copy()


    # ======================================
    # CURRENT / OBSERVED METRICS
    # ======================================

    result[
        "observed_probability"
    ] = (
        observed_probabilities
    )


    result[
        "observed_expected_revenue"
    ] = (
        observed_expected_revenue
    )


    result[
        "observed_cost"
    ] = (
        observed_cost
    )


    result[
        "observed_net_value"
    ] = (
        observed_net_value
    )


    # ======================================
    # BEST ACTION METRICS
    # ======================================

    result[
        "best_action"
    ] = (
        best_actions
    )


    result[
        "best_probability"
    ] = (
        best_probabilities
    )


    result[
        "best_expected_revenue"
    ] = (
        best_expected_revenue
    )


    result[
        "best_action_cost"
    ] = (
        best_cost
    )


    result[
        "best_net_value"
    ] = (
        best_net_value
    )


    # ======================================
    # UPLIFT METRICS
    # ======================================

    result[
        "probability_uplift"
    ] = (
        probability_uplift
    )


    result[
        "incremental_revenue"
    ] = (
        incremental_revenue
    )


    result[
        "incremental_cost"
    ] = (
        incremental_cost
    )


    result[
        "net_incremental_value"
    ] = (
        net_incremental_value
    )


    # ======================================
    # OPPORTUNITY FLAG
    # ======================================

    # Switch only when:
    #
    # 1. Best action is different from
    #    current action
    #
    # 2. Switching produces positive
    #    incremental economic value

    result[
        "action_switch_recommended"
    ] = (

        (
            result["best_action"]
            !=
            result["action"]
        )

        &

        (
            result[
                "net_incremental_value"
            ]
            > 0
        )

    )


    return result


# ==========================================
# RUN ANALYSIS
# ==========================================

sample = data.sample(
    n=min(5000, len(data)),
    random_state=42
).copy()


print(
    f"\nAnalyzing "
    f"{len(sample):,} cases..."
)


opportunity = calculate_opportunity(
    sample
)


# ==========================================
# SUMMARY
# ==========================================

print("\n==========================================")
print("         OPPORTUNITY SUMMARY")
print("==========================================")


# ------------------------------------------
# ACTION SWITCHES
# ------------------------------------------

switches = (
    opportunity[
        "action_switch_recommended"
    ].sum()
)


print(
    f"\nPotential action switches: "
    f"{switches:,}"
)


percentage = (
    switches
    /
    len(opportunity)
)


print(
    f"Percentage benefiting from "
    f"switching: "
    f"{percentage:.2%}"
)


# ------------------------------------------
# INCREMENTAL RECOVERED REVENUE
# ------------------------------------------

total_incremental = (
    opportunity[
        "incremental_revenue"
    ].sum()
)


print(
    f"\nPotential incremental recovered "
    f"revenue: "
    f"₹{total_incremental:,.2f}"
)


# ------------------------------------------
# NET INCREMENTAL VALUE
# ------------------------------------------

total_net = (
    opportunity[
        "net_incremental_value"
    ].sum()
)


print(
    f"Potential net incremental value: "
    f"₹{total_net:,.2f}"
)


# ==========================================
# ACTION DISTRIBUTION
# ==========================================

print("\n==========================================")
print("         BEST ACTION DISTRIBUTION")
print("==========================================")


action_distribution = (
    opportunity[
        "best_action"
    ]
    .value_counts()
)


print(
    action_distribution
    .to_string()
)


# ==========================================
# TOP RECOVERY OPPORTUNITIES
# ==========================================

print("\n==========================================")
print("        TOP RECOVERY OPPORTUNITIES")
print("==========================================")


top = (
    opportunity[
        opportunity[
            "action_switch_recommended"
        ]
    ]

    .sort_values(
        "net_incremental_value",
        ascending=False
    )

    .head(20)
)


if len(top) == 0:

    print(
        "\nNo positive action-switch "
        "opportunities found."
    )

else:

    print(
        top[
            [
                "transaction_id",
                "customer_id",
                "amount",
                "action",
                "best_action",
                "observed_probability",
                "best_probability",
                "observed_expected_revenue",
                "best_expected_revenue",
                "observed_cost",
                "best_action_cost",
                "incremental_revenue",
                "incremental_cost",
                "net_incremental_value"
            ]
        ]
        .to_string(
            index=False
        )
    )


# ==========================================
# SAVE RESULTS
# ==========================================

output_file = (
    "data/cleaned/"
    "incremental_recovery_opportunities.csv"
)


opportunity.to_csv(
    output_file,
    index=False
)


print("\n==========================================")


print(
    f"Saved results to:\n"
    f"{output_file}"
)


print("==========================================")