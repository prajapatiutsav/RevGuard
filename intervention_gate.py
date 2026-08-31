# ==========================================
# REVGUARD INTERVENTION GATE
# ==========================================

MIN_INCREMENTAL_VALUE = 50


def evaluate_intervention(
    amount,
    baseline_probability,
    best_probability,
    baseline_cost,
    best_action_cost
):

    # --------------------------------------
    # EXPECTED INCREMENTAL REVENUE
    # --------------------------------------

    probability_difference = (
        best_probability
        - baseline_probability
    )

    incremental_revenue = (
        amount
        * max(
            probability_difference,
            0
        )
    )


    # --------------------------------------
    # ADDITIONAL ACTION COST
    # --------------------------------------

    additional_cost = (
        best_action_cost
        - baseline_cost
    )


    # --------------------------------------
    # NET INCREMENTAL VALUE
    # --------------------------------------

    net_incremental_value = (
        incremental_revenue
        - additional_cost
    )


    # --------------------------------------
    # DECISION
    # --------------------------------------

    intervene = (
        net_incremental_value
        >= MIN_INCREMENTAL_VALUE
    )


    # --------------------------------------
    # RETURN
    # --------------------------------------

    return {

        "probability_difference":
            probability_difference,

        "incremental_revenue":
            incremental_revenue,

        "additional_cost":
            additional_cost,

        "net_incremental_value":
            net_incremental_value,

        "intervene":
            intervene
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    result = evaluate_intervention(

        amount=8000,

        baseline_probability=0.50,

        best_probability=0.75,

        baseline_cost=8,

        best_action_cost=12
    )


    print("\n===================================")
    print("      INTERVENTION GATE")
    print("===================================")


    print(
        f"\nProbability improvement: "
        f"{result['probability_difference']:.2%}"
    )

    print(
        f"Incremental revenue: "
        f"₹{result['incremental_revenue']:,.2f}"
    )

    print(
        f"Additional cost: "
        f"₹{result['additional_cost']:,.2f}"
    )

    print(
        f"Net incremental value: "
        f"₹{result['net_incremental_value']:,.2f}"
    )


    if result["intervene"]:

        print(
            "\n🟢 INTERVENTION RECOMMENDED"
        )

    else:

        print(
            "\n🔴 DO NOT INTERVENE"
        )
        