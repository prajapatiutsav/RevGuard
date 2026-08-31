import random
from datetime import datetime


# ==========================================
# ACTION COSTS
# ==========================================

ACTION_COSTS = {
    "retry": 8,
    "payment_link": 12,
    "whatsapp": 18,
    "email": 5,
    "voice_call": 90,
    "human_escalation": 250
}


# ==========================================
# ACTION EXECUTOR
# ==========================================

def execute_action(
    action,
    amount,
    recovery_probability
):

    print("\n===================================")
    print("ACTION EXECUTION")
    print("===================================")

    print(f"Action: {action}")
    print(f"Amount at risk: ₹{amount:,.2f}")
    print(
        f"Predicted recovery probability: "
        f"{recovery_probability:.2%}"
    )


    # --------------------------------------
    # SIMULATE CUSTOMER RESPONSE
    # --------------------------------------

    random_value = random.random()

    recovered = (
        random_value < recovery_probability
    )


    # --------------------------------------
    # CALCULATE RESULT
    # --------------------------------------

    if recovered:

        recovered_amount = amount

    else:

        recovered_amount = 0


    action_cost = ACTION_COSTS[action]

    net_recovery = (
        recovered_amount
        - action_cost
    )


    # --------------------------------------
    # RESULT
    # --------------------------------------

    print("\n---------- RESULT ----------")

    if recovered:

        print("✅ PAYMENT RECOVERED")

    else:

        print("❌ PAYMENT NOT RECOVERED")


    print(
        f"Recovered amount: "
        f"₹{recovered_amount:,.2f}"
    )

    print(
        f"Action cost: "
        f"₹{action_cost:,.2f}"
    )

    print(
        f"Net recovery: "
        f"₹{net_recovery:,.2f}"
    )


    # --------------------------------------
    # RETURN RESULT
    # --------------------------------------

    return {

        "timestamp": datetime.now(),

        "action": action,

        "amount": amount,

        "recovery_probability":
            recovery_probability,

        "recovered":
            recovered,

        "recovered_amount":
            recovered_amount,

        "action_cost":
            action_cost,

        "net_recovery":
            net_recovery
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    result = execute_action(

        action="payment_link",

        amount=8000,

        recovery_probability=0.76
    )

    print("\nReturned result:")

    print(result)
    