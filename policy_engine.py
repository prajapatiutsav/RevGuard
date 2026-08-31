# ==========================================
# REVGUARD POLICY & GUARDRAIL ENGINE
# ==========================================


# ==========================================
# 1. MERCHANT POLICIES
# ==========================================

POLICIES = {

    # Maximum transaction amount that
    # can be handled automatically
    "max_auto_amount": 10000,

    # Maximum number of customer contacts
    # allowed within the configured period
    "max_contacts_per_week": 3,

    # Maximum payment retries
    "max_retries": 2,

    # Maximum fatigue allowed for channels
    "max_fatigue": {

        "retry": 80,

        "payment_link": 75,

        "whatsapp": 70,

        "email": 75,

        "voice_call": 50,

        "human_escalation": 100
    },

    # Above this amount,
    # human approval is required
    "human_approval_amount": 50000,

    # Maximum discount allowed
    "max_discount_percent": 10
}


# ==========================================
# 2. POLICY CHECK FUNCTION
# ==========================================

def check_policy(
    action,
    amount,
    fatigue_score,
    contacts_this_week,
    retry_count
):

    reasons = []


    # --------------------------------------
    # CHECK 1: AUTOMATIC AMOUNT LIMIT
    # --------------------------------------

    if (
        amount > POLICIES["max_auto_amount"]
        and action != "human_escalation"
    ):

        reasons.append(
            "Transaction exceeds automatic action limit."
        )


    # --------------------------------------
    # CHECK 2: CUSTOMER CONTACT LIMIT
    # --------------------------------------

    communication_actions = [
        "whatsapp",
        "email",
        "voice_call"
    ]

    if action in communication_actions:

        if (
            contacts_this_week
            >= POLICIES["max_contacts_per_week"]
        ):

            reasons.append(
                "Customer contact limit exceeded."
            )


    # --------------------------------------
    # CHECK 3: RETRY LIMIT
    # --------------------------------------

    if action == "retry":

        if retry_count >= POLICIES["max_retries"]:

            reasons.append(
                "Maximum retry attempts reached."
            )


    # --------------------------------------
    # CHECK 4: FATIGUE LIMIT
    # --------------------------------------

    max_fatigue = POLICIES[
        "max_fatigue"
    ][action]

    if fatigue_score > max_fatigue:

        reasons.append(
            f"Customer fatigue score "
            f"{fatigue_score} exceeds "
            f"allowed limit {max_fatigue}."
        )


    # --------------------------------------
    # FINAL DECISION
    # --------------------------------------

    allowed = len(reasons) == 0


    return {
        "allowed": allowed,
        "action": action,
        "reasons": reasons
    }


# ==========================================
# 3. TEST THE POLICY ENGINE
# ==========================================

if __name__ == "__main__":

    print("\n===================================")
    print("REVGUARD POLICY ENGINE")
    print("===================================\n")


    # Example customer

    amount = 8000

    fatigue_score = 85

    contacts_this_week = 3

    retry_count = 2


    actions = [
        "retry",
        "payment_link",
        "whatsapp",
        "email",
        "voice_call",
        "human_escalation"
    ]


    for action in actions:

        result = check_policy(
            action=action,
            amount=amount,
            fatigue_score=fatigue_score,
            contacts_this_week=contacts_this_week,
            retry_count=retry_count
        )


        if result["allowed"]:

            print(
                f"✅ {action}: ALLOWED"
            )

        else:

            print(
                f"❌ {action}: BLOCKED"
            )

            for reason in result["reasons"]:

                print(
                    f"   → {reason}"
                )