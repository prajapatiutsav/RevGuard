from customer_state import build_customer_state
from revguard_engine import rank_actions, ACTIONS
from policy_engine import check_policy
from action_executor import execute_action
from feedback import save_feedback
from intervention_gate import evaluate_intervention
from explainability import (
    generate_explanation,
    print_explanation
)

# ==========================================
# CONFIGURATION
# ==========================================


transaction_id = 29154

BASELINE_ACTION = "retry"


contacts_this_week = 2

retry_count = 1


print("\n==========================================")
print("        REVGUARD AI DECISION ENGINE")
print("==========================================")


# ==========================================
# 1. BUILD CUSTOMER STATE
# ==========================================

print("\n[1] BUILDING CUSTOMER STATE")


customer = build_customer_state(
    transaction_id
)


print("✅ Customer state loaded")

print(
    f"Customer ID: "
    f"{customer['customer_id']}"
)

print(
    f"Transaction ID: "
    f"{customer['transaction_id']}"
)

print(
    f"Amount: "
    f"₹{customer['amount']:,.2f}"
)

print(
    f"Failure reason: "
    f"{customer['failure_reason']}"
)

print(
    f"LTV: "
    f"₹{customer['ltv']:,.2f}"
)


# ==========================================
# 2. RANK ACTIONS
# ==========================================

print("\n[2] PREDICTING RECOVERY ACTIONS")


ranked_actions = rank_actions(
    customer
)


print("\n========== ACTION RANKING ==========")


print(
    ranked_actions[
        [
            "action",
            "probability",
            "expected_recovery",
            "action_cost",
            "score"
        ]
    ].to_string(
        index=False
    )
)


# ==========================================
# 3. FIND BASELINE PROBABILITY
# ==========================================

baseline_row = ranked_actions[
    ranked_actions["action"]
    == BASELINE_ACTION
]


baseline_probability = float(
    baseline_row.iloc[0]["probability"]
)


baseline_cost = ACTIONS[
    BASELINE_ACTION
]["cost"]


print("\n========== BASELINE ==========")


print(
    f"Baseline action: "
    f"{BASELINE_ACTION}"
)

print(
    f"Baseline probability: "
    f"{baseline_probability:.2%}"
)

print(
    f"Baseline cost: "
    f"₹{baseline_cost:,.2f}"
)


# ==========================================
# 4. FIND BEST ALTERNATIVE
# ==========================================

best_alternative = None


for _, row in ranked_actions.iterrows():

    action = row["action"]


    # Don't compare retry against retry

    if action == BASELINE_ACTION:

        continue


    probability = float(
        row["probability"]
    )


    action_cost = ACTIONS[
        action
    ]["cost"]


    gate = evaluate_intervention(

        amount=customer["amount"],

        baseline_probability=
            baseline_probability,

        best_probability=
            probability,

        baseline_cost=
            baseline_cost,

        best_action_cost=
            action_cost
    )


    print(
        f"\nChecking {action}:"
    )

    print(
        f"  Probability: "
        f"{probability:.2%}"
    )

    print(
        f"  Incremental revenue: "
        f"₹{gate['incremental_revenue']:,.2f}"
    )

    print(
        f"  Additional cost: "
        f"₹{gate['additional_cost']:,.2f}"
    )

    print(
        f"  Net incremental value: "
        f"₹{gate['net_incremental_value']:,.2f}"
    )


    if gate["intervene"]:

        best_alternative = {

            "action": action,

            "probability":
                probability,

            "gate": gate,

            "score":
                row["score"]
        }

        break


# ==========================================
# 5. SELECT ACTION
# ==========================================

print("\n==========================================")
print("          INTERVENTION DECISION")
print("==========================================")


if best_alternative is not None:

    selected_action = (
        best_alternative["action"]
    )

    selected_probability = (
        best_alternative["probability"]
    )

    gate_result = (
        best_alternative["gate"]
    )


    print(
        "\n🟢 SWITCH RECOMMENDED"
    )

    print(
        f"Baseline: "
        f"{BASELINE_ACTION}"
    )

    print(
        f"New action: "
        f"{selected_action}"
    )

    print(
        f"Expected incremental value: "
        f"₹{gate_result['net_incremental_value']:,.2f}"
    )


else:

    # No alternative is economically
    # better than the baseline.

    selected_action = (
        BASELINE_ACTION
    )

    selected_probability = (
        baseline_probability
    )

    gate_result = {

        "probability_difference": 0,

        "incremental_revenue": 0,

        "additional_cost": 0,

        "net_incremental_value": 0,

        "intervene": False
    }


    print(
        "\n🔵 NO SWITCH REQUIRED"
    )

    print(
        f"Using baseline action: "
        f"{BASELINE_ACTION}"
    )


# ==========================================
# 6. POLICY CHECK
# ==========================================

print("\n[3] POLICY CHECK")


policy_result = check_policy(

    action=selected_action,

    amount=customer["amount"],

    fatigue_score=
        customer["fatigue_score"],

    contacts_this_week=
        contacts_this_week,

    retry_count=
        retry_count
)


if not policy_result["allowed"]:

    print(
        f"\n❌ {selected_action} "
        f"blocked by policy."
    )


    for reason in policy_result["reasons"]:

        print(
            f"   → {reason}"
        )


    # --------------------------------------
    # FALLBACK TO BASELINE
    # --------------------------------------

    print(
        f"\nTrying baseline action: "
        f"{BASELINE_ACTION}"
    )


    baseline_policy = check_policy(

        action=BASELINE_ACTION,

        amount=customer["amount"],

        fatigue_score=
            customer["fatigue_score"],

        contacts_this_week=
            contacts_this_week,

        retry_count=
            retry_count
    )


    if baseline_policy["allowed"]:

        selected_action = (
            BASELINE_ACTION
        )

        selected_probability = (
            baseline_probability
        )

        print(
            "✅ Baseline action allowed."
        )


    else:

        print(
            "⚠️ Baseline also blocked."
        )

        selected_action = (
            "human_escalation"
        )

        selected_probability = 0.50


else:

    print(
        f"✅ {selected_action} "
        f"is allowed."
    )


# ==========================================
# 8. EXECUTE
# ==========================================

explanation = generate_explanation(

    customer=customer,

    baseline_action=BASELINE_ACTION,

    baseline_probability=
        baseline_probability,

    selected_action=
        selected_action,

    selected_probability=
        selected_probability,

    incremental_value=
        gate_result[
            "net_incremental_value"
        ],

    ranked_actions=
        ranked_actions
)


print_explanation(
    explanation
)

print("\n[4] EXECUTING ACTION")


result = execute_action(

    action=selected_action,

    amount=customer["amount"],

    recovery_probability=
        selected_probability
)


# ==========================================
# 8. ADD DECISION CONTEXT
# ==========================================

result["transaction_id"] = (
    customer["transaction_id"]
)

result["customer_id"] = (
    customer["customer_id"]
)

result["failure_reason"] = (
    customer["failure_reason"]
)

result["payment_method"] = (
    customer["payment_method"]
)

result["ltv"] = (
    customer["ltv"]
)

result["fatigue_score"] = (
    customer["fatigue_score"]
)

result["predicted_probability"] = (
    selected_probability
)

result["baseline_action"] = (
    BASELINE_ACTION
)

result["baseline_probability"] = (
    baseline_probability
)

result["incremental_revenue"] = (
    gate_result["incremental_revenue"]
)

result["incremental_cost"] = (
    gate_result["additional_cost"]
)

result["net_incremental_value"] = (
    gate_result["net_incremental_value"]
)

result["intervention_recommended"] = (
    gate_result["intervene"]
)


# ==========================================
# 9. SAVE FEEDBACK
# ==========================================

print("\n[5] SAVING FEEDBACK")


save_feedback(
    result
)


# ==========================================
# 10. FINAL DECISION
# ==========================================

print("\n==========================================")
print("          FINAL REVGUARD DECISION")
print("==========================================")


print(
    f"Transaction: "
    f"{transaction_id}"
)

print(
    f"Baseline action: "
    f"{BASELINE_ACTION}"
)

print(
    f"Selected action: "
    f"{selected_action}"
)

print(
    f"Recovery probability: "
    f"{selected_probability:.2%}"
)

print(
    f"Recovered amount: "
    f"₹{result['recovered_amount']:,.2f}"
)

print(
    f"Action cost: "
    f"₹{result['action_cost']:,.2f}"
)

print(
    f"Net recovery: "
    f"₹{result['net_recovery']:,.2f}"
)

print(
    f"Incremental opportunity: "
    f"₹{gate_result['net_incremental_value']:,.2f}"
)

print("\n==========================================")
print("       REVGUARD COMPLETED ✅")
print("==========================================")