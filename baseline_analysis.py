import pandas as pd


# ==========================================
# LOAD HISTORICAL DATA
# ==========================================

data = pd.read_csv(
    "data/cleaned/recovery_cases_ml.csv"
)


print("\n==========================================")
print("      HISTORICAL RECOVERY ANALYSIS")
print("==========================================")


# ==========================================
# OVERALL STATISTICS
# ==========================================

print("\nTotal recovery cases:")

print(len(data))


print("\nOverall recovery rate:")

print(
    f"{data['recovered'].mean():.2%}"
)


print("\nTotal revenue at risk:")

print(
    f"₹{data['amount'].sum():,.2f}"
)


print("\nTotal revenue recovered:")

print(
    f"₹{data['recovered_amount'].sum():,.2f}"
)


# ==========================================
# ACTION PERFORMANCE
# ==========================================

action_stats = (
    data
    .groupby("action")
    .agg(
        attempts=("action", "count"),

        recovery_rate=(
            "recovered",
            "mean"
        ),

        revenue_at_risk=(
            "amount",
            "sum"
        ),

        recovered_revenue=(
            "recovered_amount",
            "sum"
        ),

        action_cost=(
            "action_cost",
            "sum"
        )
    )
)


# ==========================================
# NET RECOVERY
# ==========================================

action_stats["net_recovery"] = (
    action_stats["recovered_revenue"]
    -
    action_stats["action_cost"]
)


# ==========================================
# ROI
# ==========================================

action_stats["roi"] = (
    action_stats["net_recovery"]
    /
    action_stats["action_cost"]
)


# ==========================================
# DISPLAY
# ==========================================

print("\n==========================================")
print("          ACTION PERFORMANCE")
print("==========================================")


print(
    action_stats.sort_values(
        "net_recovery",
        ascending=False
    )
)


# ==========================================
# BEST HISTORICAL ACTION
# ==========================================

best_action = (
    action_stats["net_recovery"]
    .idxmax()
)


print("\n==========================================")

print(
    f"Best historical action: {best_action}"
)

print("==========================================")