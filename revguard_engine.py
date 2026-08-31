import pandas as pd
import joblib


# ==========================================
# LOAD MODEL
# ==========================================

action_model = joblib.load("action_model.pkl")


# ==========================================
# ACTION CONFIGURATION
# ==========================================

ACTIONS = {
    "retry": {
        "cost": 8,
        "fatigue_penalty": 2
    },

    "payment_link": {
        "cost": 12,
        "fatigue_penalty": 3
    },

    "whatsapp": {
        "cost": 18,
        "fatigue_penalty": 6
    },

    "email": {
        "cost": 5,
        "fatigue_penalty": 4
    },

    "voice_call": {
        "cost": 90,
        "fatigue_penalty": 15
    },

    "human_escalation": {
        "cost": 250,
        "fatigue_penalty": 5
    }
}


# ==========================================
# RANK ACTIONS
# ==========================================

def rank_actions(customer):

    results = []

    for action in ACTIONS:

        input_data = customer.copy()

        input_data["action"] = action

        input_df = pd.DataFrame([input_data])

        probability = action_model.predict_proba(
            input_df
        )[0][1]

        amount = customer["amount"]

        expected_recovery = (
            amount * probability
        )

        cost = ACTIONS[action]["cost"]

        fatigue = customer["fatigue_score"]

        fatigue_penalty = (
            fatigue / 100
        ) * ACTIONS[action]["fatigue_penalty"]

        score = (
            expected_recovery
            - cost
            - fatigue_penalty
        )

        results.append({
            "action": action,
            "probability": probability,
            "expected_recovery": expected_recovery,
            "action_cost": cost,
            "fatigue_penalty": fatigue_penalty,
            "score": score
        })

    results_df = pd.DataFrame(results)

    return results_df.sort_values(
        "score",
        ascending=False
    ).reset_index(drop=True)