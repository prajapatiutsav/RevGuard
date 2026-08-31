# ==========================================
# REVGUARD EXPLAINABILITY ENGINE
# ==========================================


def generate_explanation(
    customer,
    baseline_action,
    baseline_probability,
    selected_action,
    selected_probability,
    incremental_value,
    ranked_actions
):

    reasons = []

    warnings = []


    # ======================================
    # BASIC CUSTOMER FACTORS
    # ======================================

    amount = customer["amount"]

    fatigue = customer["fatigue_score"]

    ltv = customer["ltv"]

    failure_reason = customer[
        "failure_reason"
    ]

    response_rate = customer[
        "response_rate"
    ]


    # ======================================
    # SELECTED ACTION
    # ======================================

    if selected_action == baseline_action:

        reasons.append(
            "Baseline action remained "
            "economically optimal."
        )

        reasons.append(
            f"No alternative produced "
            f"sufficient incremental value."
        )

    else:

        improvement = (
            selected_probability
            - baseline_probability
        )

        reasons.append(
            f"{selected_action} improves "
            f"predicted recovery probability "
            f"by {improvement:.2%}."
        )

        reasons.append(
            f"Estimated net incremental value "
            f"is ₹{incremental_value:,.2f}."
        )


    # ======================================
    # CUSTOMER VALUE
    # ======================================

    if ltv >= 100000:

        reasons.append(
            "Customer has high lifetime value."
        )

    elif ltv >= 50000:

        reasons.append(
            "Customer has meaningful lifetime value."
        )


    # ======================================
    # FATIGUE
    # ======================================

    if fatigue >= 70:

        warnings.append(
            "Customer fatigue is high; "
            "aggressive contact should be avoided."
        )

    elif fatigue >= 40:

        warnings.append(
            "Customer has moderate interaction "
            "fatigue."
        )

    else:

        reasons.append(
            "Customer interaction fatigue is low."
        )


    # ======================================
    # RESPONSE BEHAVIOR
    # ======================================

    if response_rate >= 0.70:

        reasons.append(
            "Customer has a strong historical "
            "response rate."
        )

    elif response_rate <= 0.30:

        warnings.append(
            "Customer has historically shown "
            "low response behavior."
        )


    # ======================================
    # FAILURE REASON
    # ======================================

    if failure_reason:

        reasons.append(
            f"Payment failure reason: "
            f"{failure_reason}."
        )


    # ======================================
    # TRANSACTION SIZE
    # ======================================

    if amount >= 50000:

        reasons.append(
            "High-value transaction may justify "
            "more expensive recovery actions."
        )

    elif amount <= 500:

        reasons.append(
            "Low transaction value favors "
            "low-cost recovery actions."
        )


    # ======================================
    # TOP ALTERNATIVES
    # ======================================

    alternatives = []


    for _, row in ranked_actions.iterrows():

        action = row["action"]

        probability = row[
            "probability"
        ]

        score = row["score"]


        if action == selected_action:

            continue


        alternatives.append({

            "action": action,

            "probability":
                probability,

            "score":
                score
        })


    # ======================================
    # RETURN EXPLANATION
    # ======================================

    return {

        "selected_action":
            selected_action,

        "recovery_probability":
            selected_probability,

        "incremental_value":
            incremental_value,

        "reasons":
            reasons,

        "warnings":
            warnings,

        "alternatives":
            alternatives
    }


# ==========================================
# DISPLAY EXPLANATION
# ==========================================

def print_explanation(
    explanation
):

    print("\n")
    print("==========================================")
    print("       WHY REVGUARD CHOSE THIS")
    print("==========================================")


    print(
        f"\n🎯 Recommended action:"
    )

    print(
        f"   {explanation['selected_action']}"
    )


    print(
        f"\n📊 Recovery probability:"
    )

    print(
        f"   "
        f"{explanation['recovery_probability']:.2%}"
    )


    print(
        f"\n💰 Incremental value:"
    )

    print(
        f"   "
        f"₹{explanation['incremental_value']:,.2f}"
    )


    print("\nWHY?")


    for reason in explanation[
        "reasons"
    ]:

        print(
            f"  • {reason}"
        )


    if explanation["warnings"]:

        print("\n⚠️ WARNINGS")

        for warning in explanation[
            "warnings"
        ]:

            print(
                f"  • {warning}"
            )


    print("\nALTERNATIVES")


    for alternative in explanation[
        "alternatives"
    ]:

        print(
            f"  • "
            f"{alternative['action']}: "
            f"{alternative['probability']:.2%}"
        )