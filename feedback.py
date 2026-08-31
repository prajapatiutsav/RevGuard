import pandas as pd
from pathlib import Path


# ==========================================
# FILE LOCATION
# ==========================================

HISTORY_FILE = Path(
    "data/action_history.csv"
)


# ==========================================
# SAVE FEEDBACK
# ==========================================

def save_feedback(result):

    new_record = pd.DataFrame([result])


    # --------------------------------------
    # EXISTING HISTORY
    # --------------------------------------

    if HISTORY_FILE.exists():

        history = pd.read_csv(
            HISTORY_FILE
        )

        history = pd.concat(
            [
                history,
                new_record
            ],
            ignore_index=True
        )

    else:

        history = new_record


    # --------------------------------------
    # SAVE
    # --------------------------------------

    history.to_csv(
        HISTORY_FILE,
        index=False
    )


    print("\n===================================")
    print("FEEDBACK SAVED")
    print("===================================")

    print(
        f"Total action records: "
        f"{len(history)}"
    )

    print(
        f"Saved to: {HISTORY_FILE}"
    )


# ==========================================
# LOAD HISTORY
# ==========================================

def load_history():

    if not HISTORY_FILE.exists():

        return pd.DataFrame()

    return pd.read_csv(
        HISTORY_FILE
    )


# ==========================================
# ANALYZE FEEDBACK
# ==========================================

def analyze_feedback():

    history = load_history()


    if history.empty:

        print(
            "\nNo feedback data available."
        )

        return


    print("\n===================================")
    print("       REVGUARD ANALYTICS")
    print("===================================")


    # --------------------------------------
    # TOTAL CASES
    # --------------------------------------

    total_cases = len(history)

    print(
        f"\nTotal recovery attempts: "
        f"{total_cases}"
    )


    # --------------------------------------
    # RECOVERY RATE
    # --------------------------------------

    recovery_rate = (
        history["recovered"]
        .mean()
    )


    print(
        f"Recovery rate: "
        f"{recovery_rate:.2%}"
    )


    # --------------------------------------
    # TOTAL AMOUNT ATTEMPTED
    # --------------------------------------

    total_attempted = (
        history["amount"]
        .sum()
    )


    print(
        f"Revenue at risk: "
        f"₹{total_attempted:,.2f}"
    )


    # --------------------------------------
    # TOTAL RECOVERED
    # --------------------------------------

    total_recovered = (
        history["recovered_amount"]
        .sum()
    )


    print(
        f"Revenue recovered: "
        f"₹{total_recovered:,.2f}"
    )


    # --------------------------------------
    # TOTAL ACTION COST
    # --------------------------------------

    total_cost = (
        history["action_cost"]
        .sum()
    )


    print(
        f"Recovery cost: "
        f"₹{total_cost:,.2f}"
    )


    # --------------------------------------
    # NET RECOVERY
    # --------------------------------------

    net_recovery = (
        total_recovered
        - total_cost
    )


    print(
        f"Net recovered revenue: "
        f"₹{net_recovery:,.2f}"
    )


    # --------------------------------------
    # ROI
    # --------------------------------------

    if total_cost > 0:

        roi = (
            net_recovery
            / total_cost
        )

        print(
            f"Recovery ROI: "
            f"{roi:.2f}x"
        )


    # --------------------------------------
    # ACTION PERFORMANCE
    # --------------------------------------

    print(
        "\n========== ACTION PERFORMANCE =========="
    )


    action_stats = (
        history
        .groupby("action")
        .agg(
            attempts=(
                "action",
                "count"
            ),

            recovery_rate=(
                "recovered",
                "mean"
            ),

            recovered_revenue=(
                "recovered_amount",
                "sum"
            ),

            total_cost=(
                "action_cost",
                "sum"
            )
        )
    )


    action_stats["net_recovery"] = (
        action_stats["recovered_revenue"]
        -
        action_stats["total_cost"]
    )


    print(
        action_stats
    )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    analyze_feedback()