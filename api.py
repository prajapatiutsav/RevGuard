import pandas as pd

from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from customer_state import build_customer_state

from revguard_engine import rank_actions, ACTIONS

from policy_engine import check_policy

from intervention_gate import evaluate_intervention

from explainability import generate_explanation


# ==========================================
# CREATE FASTAPI APP
# ==========================================

app = FastAPI(

    title="RevGuard AI",

    description=(
        "AI-powered revenue recovery "
        "decision engine"
    ),

    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ==========================================
# REQUEST MODEL
# ==========================================

class PaymentRequest(BaseModel):

    transaction_id: int


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def home():

    return {

        "system":
            "RevGuard AI",

        "status":
            "online",

        "message":
            "Revenue recovery engine is running"
    }


# ==========================================
# HEALTH ENDPOINT
# ==========================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "service":
            "RevGuard Revenue Recovery Engine"
    }


# ==========================================
# ANALYTICS
# ==========================================

@app.get("/analytics")
def analytics():

    try:

        data = pd.read_csv(
            "data/cleaned/recovery_cases_ml.csv"
        )


        # ------------------------------
        # OVERALL METRICS
        # ------------------------------

        revenue_at_risk = float(
            data["amount"].sum()
        )


        recovered_revenue = float(
            data["recovered_amount"].sum()
        )


        recovery_rate = float(
            data["recovered"].mean()
        )


        unrecovered_revenue = (
            revenue_at_risk
            -
            recovered_revenue
        )


        # ------------------------------
        # ACTION PERFORMANCE
        # ------------------------------

        action_stats = (

            data

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

            .reset_index()
        )


        action_stats[
            "net_recovery"
        ] = (

            action_stats[
                "recovered_revenue"
            ]

            -

            action_stats[
                "action_cost"
            ]
        )


        # ------------------------------
        # REVGUARD DISTRIBUTION
        # ------------------------------

        try:

            opportunities = pd.read_csv(

                "data/cleaned/"
                "incremental_recovery_opportunities.csv"
            )


            strategy_distribution = (

                opportunities[
                    "best_action"
                ]

                .value_counts()

                .to_dict()
            )


            incremental_opportunity = float(

                opportunities[
                    "net_incremental_value"
                ]

                .clip(lower=0)

                .sum()
            )


        except Exception:

            strategy_distribution = {}

            incremental_opportunity = 0


        return {

            "total_cases":
                len(data),

            "revenue_at_risk":
                revenue_at_risk,

            "recovered_revenue":
                recovered_revenue,

            "unrecovered_revenue":
                unrecovered_revenue,

            "recovery_rate":
                recovery_rate,

            "incremental_opportunity":
                incremental_opportunity,

            "action_performance":
                action_stats.to_dict(
                    orient="records"
                ),

            "strategy_distribution":
                strategy_distribution
        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ==========================================
# 🚨 FAILED PAYMENT ALERTS
# ==========================================

@app.get("/failed-payments")
def failed_payments():

    try:

        data = pd.read_csv(
            "data/cleaned/recovery_cases_ml.csv"
        )


        # ----------------------------------
        # Make sure missing values do not
        # break JSON serialization.
        # ----------------------------------

        data = data.where(
            pd.notnull(data),
            None
        )


        payments = []


        for _, row in data.iterrows():

            transaction_id = row.get(
                "transaction_id"
            )


            customer_id = row.get(
                "customer_id"
            )


            amount = row.get(
                "amount",
                0
            )


            failure_reason = row.get(
                "failure_reason",
                "Unknown"
            )


            action = row.get(
                "action",
                "retry"
            )


            recovered = row.get(
                "recovered",
                0
            )


            recovered_amount = row.get(
                "recovered_amount",
                0
            )


            # ----------------------------------
            # STATUS
            # ----------------------------------

            try:

                recovered_bool = (
                    float(recovered) == 1
                )

            except Exception:

                recovered_bool = (
                    str(recovered)
                    .lower()
                    in [
                        "true",
                        "yes",
                        "recovered",
                        "1"
                    ]
                )


            if recovered_bool:

                status = "recovered"

            else:

                status = "at-risk"


            # ----------------------------------
            # SAFE NUMERIC VALUES
            # ----------------------------------

            try:

                amount = float(
                    amount or 0
                )

            except Exception:

                amount = 0.0


            try:

                recovered_amount = float(
                    recovered_amount or 0
                )

            except Exception:

                recovered_amount = 0.0


            # ----------------------------------
            # BUILD RESPONSE
            # ----------------------------------

            payments.append({

                "transaction_id":
                    int(transaction_id)
                    if transaction_id is not None
                    else None,

                "customer_id":
                    int(customer_id)
                    if customer_id is not None
                    else None,

                "amount":
                    amount,

                "failure_reason":
                    str(
                        failure_reason
                        or "Unknown"
                    ),

                "recommended_action":
                    str(
                        action
                        or "retry"
                    ),

                "status":
                    status,

                "recovered":
                    recovered_bool,

                "recovered_amount":
                    recovered_amount

            })


        # ----------------------------------
        # Sort by amount so the dashboard
        # highlights the highest-value
        # failed payments first.
        # ----------------------------------

        payments.sort(

            key=lambda payment:
                payment["amount"],

            reverse=True
        )


        return {

            "total":
                len(payments),

            "payments":
                payments
        }


    except FileNotFoundError:

        raise HTTPException(

            status_code=404,

            detail=(
                "Recovery dataset not found."
            )
        )


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ==========================================
# 📈 RECOVERY FORECAST
# ==========================================

@app.get("/recovery-forecast")
def recovery_forecast():

    try:

        data = pd.read_csv(
            "data/cleaned/recovery_cases_ml.csv"
        )


        # ----------------------------------
        # CURRENT METRICS
        # ----------------------------------

        revenue_at_risk = float(
            data["amount"].sum()
        )


        current_recovered = float(
            data["recovered_amount"].sum()
        )


        recovery_rate = float(
            data["recovered"].mean()
        )


        # ----------------------------------
        # Normalize recovery rate
        # ----------------------------------

        if recovery_rate > 1:

            recovery_rate = (
                recovery_rate / 100
            )


        # ----------------------------------
        # Transparent run-rate forecast
        #
        # This is NOT pretending to be
        # a machine-learning forecast.
        #
        # It projects the current recovery
        # rate across the revenue currently
        # at risk.
        # ----------------------------------

        projected_recovery = (

            revenue_at_risk

            *

            recovery_rate
        )


        additional_opportunity = max(

            projected_recovery
            -
            current_recovered,

            0
        )


        # ----------------------------------
        # Remaining revenue
        # ----------------------------------

        remaining_at_risk = max(

            revenue_at_risk
            -
            current_recovered,

            0
        )


        return {

            "projected_recovery":
                round(
                    projected_recovery,
                    2
                ),

            "current_recovered":
                round(
                    current_recovered,
                    2
                ),

            "revenue_at_risk":
                round(
                    revenue_at_risk,
                    2
                ),

            "additional_opportunity":
                round(
                    additional_opportunity,
                    2
                ),

            "remaining_at_risk":
                round(
                    remaining_at_risk,
                    2
                ),

            "recovery_rate":
                round(
                    recovery_rate,
                    4
                ),

            "forecast_type":
                "run_rate",

            "forecast_period":
                "30_days",

            "description":
                (
                    "Projected recovery based on "
                    "the current RevGuard recovery "
                    "rate applied to revenue at risk."
                )
        }


    except FileNotFoundError:

        raise HTTPException(

            status_code=404,

            detail=(
                "Recovery dataset not found."
            )
        )


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ==========================================
# ANALYZE PAYMENT
# ==========================================

@app.post("/analyze-payment")
def analyze_payment(
    request: PaymentRequest
):


    transaction_id = (
        request.transaction_id
    )


    # ======================================
    # 1. BUILD CUSTOMER STATE
    # ======================================

    try:

        customer = (
            build_customer_state(
                transaction_id
            )
        )


    except Exception:

        raise HTTPException(

            status_code=404,

            detail=(

                f"Transaction "
                f"{transaction_id} "
                f"not found."
            )
        )


    # ======================================
    # 2. RANK ACTIONS
    # ======================================

    ranked_actions = rank_actions(
        customer
    )


    # ======================================
    # 3. BASELINE
    # ======================================

    baseline_action = "retry"


    baseline_row = (

        ranked_actions[
            ranked_actions["action"]
            ==
            baseline_action
        ]
    )


    if baseline_row.empty:

        raise HTTPException(

            status_code=500,

            detail=
                "Baseline action unavailable."
        )


    baseline_probability = float(

        baseline_row.iloc[0][
            "probability"
        ]
    )


    baseline_cost = float(

        ACTIONS[
            baseline_action
        ]["cost"]
    )


    # ======================================
    # 4. TRANSACTION AMOUNT
    # ======================================

    amount = float(
        customer["amount"]
    )


    # ======================================
    # 5. BASELINE ECONOMIC VALUE
    # ======================================

    baseline_expected_revenue = (

        amount

        *

        baseline_probability
    )


    baseline_net_value = (

        baseline_expected_revenue

        -

        baseline_cost
    )


    # ======================================
    # 6. CALCULATE ECONOMIC VALUE
    #    FOR EVERY ACTION
    # ======================================

    economic_actions = []


    for _, row in ranked_actions.iterrows():

        action = row["action"]


        if action not in ACTIONS:

            continue


        probability = float(
            row["probability"]
        )


        action_cost = float(

            ACTIONS[
                action
            ]["cost"]
        )


        expected_revenue = (

            amount

            *

            probability
        )


        net_value = (

            expected_revenue

            -

            action_cost
        )


        incremental_value = (

            net_value

            -

            baseline_net_value
        )


        economic_actions.append({

            "action":
                action,

            "probability":
                probability,

            "cost":
                action_cost,

            "expected_revenue":
                expected_revenue,

            "net_value":
                net_value,

            "incremental_value":
                incremental_value
        })


    # ======================================
    # 7. SORT BY ECONOMIC VALUE
    # ======================================

    economic_actions = sorted(

        economic_actions,

        key=lambda x:
            x["net_value"],

        reverse=True
    )


    # ======================================
    # 8. SELECT BEST ECONOMIC ACTION
    # ======================================

    selected_action = (
        baseline_action
    )


    selected_probability = (
        baseline_probability
    )


    selected_expected_revenue = (
        baseline_expected_revenue
    )


    selected_cost = (
        baseline_cost
    )


    selected_net_value = (
        baseline_net_value
    )


    selected_incremental_value = 0


    selected_gate = {

        "probability_difference":
            0,

        "incremental_revenue":
            0,

        "additional_cost":
            0,

        "net_incremental_value":
            0,

        "intervene":
            False
    }


    # ======================================
    # 9. CHECK ECONOMIC ALTERNATIVES
    # ======================================

    for candidate in economic_actions:

        action = candidate["action"]


        if action == baseline_action:

            continue


        # ----------------------------------
        # Only consider actions that
        # create additional value.
        # ----------------------------------

        if candidate[
            "incremental_value"
        ] <= 0:

            continue


        probability = (
            candidate[
                "probability"
            ]
        )


        action_cost = (
            candidate[
                "cost"
            ]
        )


        # ----------------------------------
        # INTERVENTION GATE
        # ----------------------------------

        gate = evaluate_intervention(

            amount=amount,

            baseline_probability=
                baseline_probability,

            best_probability=
                probability,

            baseline_cost=
                baseline_cost,

            best_action_cost=
                action_cost
        )


        # ----------------------------------
        # ACCEPT ONLY IF GATE ALLOWS IT
        # ----------------------------------

        if gate["intervene"]:

            selected_action = action


            selected_probability = (
                probability
            )


            selected_expected_revenue = (

                candidate[
                    "expected_revenue"
                ]
            )


            selected_cost = (
                action_cost
            )


            selected_net_value = (

                candidate[
                    "net_value"
                ]
            )


            selected_incremental_value = (

                candidate[
                    "incremental_value"
                ]
            )


            selected_gate = gate


            break


    # ======================================
    # 10. POLICY CHECK
    # ======================================

    policy_result = check_policy(

        action=selected_action,

        amount=amount,

        fatigue_score=
            customer[
                "fatigue_score"
            ],

        contacts_this_week=2,

        retry_count=1
    )


    # ======================================
    # 11. POLICY FALLBACK
    # ======================================

    if not policy_result["allowed"]:

        selected_action = (
            baseline_action
        )


        selected_probability = (
            baseline_probability
        )


        selected_expected_revenue = (
            baseline_expected_revenue
        )


        selected_cost = (
            baseline_cost
        )


        selected_net_value = (
            baseline_net_value
        )


        selected_incremental_value = 0


        selected_gate = {

            "probability_difference":
                0,

            "incremental_revenue":
                0,

            "additional_cost":
                0,

            "net_incremental_value":
                0,

            "intervene":
                False
        }


    # ======================================
    # 12. EXPLANATION
    # ======================================

    explanation = (

        generate_explanation(

            customer=customer,

            baseline_action=
                baseline_action,

            baseline_probability=
                baseline_probability,

            selected_action=
                selected_action,

            selected_probability=
                selected_probability,

            incremental_value=
                selected_incremental_value,

            ranked_actions=
                ranked_actions
        )
    )


    # ======================================
    # 13. RETURN API RESPONSE
    # ======================================

    return {

        # ------------------------------
        # TRANSACTION
        # ------------------------------

        "transaction_id":
            transaction_id,


        "customer_id":
            int(
                customer[
                    "customer_id"
                ]
            ),


        "amount":
            amount,


        "failure_reason":
            customer[
                "failure_reason"
            ],


        # ------------------------------
        # DECISION
        # ------------------------------

        "baseline_action":
            baseline_action,


        "recommended_action":
            selected_action,


        # ------------------------------
        # PROBABILITY
        # ------------------------------

        "recovery_probability":
            round(
                selected_probability,
                4
            ),


        # ------------------------------
        # ECONOMIC METRICS
        # ------------------------------

        "expected_recovery":
            round(
                selected_expected_revenue,
                2
            ),


        "action_cost":
            round(
                selected_cost,
                2
            ),


        "net_economic_value":
            round(
                selected_net_value,
                2
            ),


        "incremental_value":
            round(
                selected_incremental_value,
                2
            ),


        # ------------------------------
        # BASELINE ECONOMICS
        # ------------------------------

        "baseline_expected_recovery":
            round(
                baseline_expected_revenue,
                2
            ),


        "baseline_net_value":
            round(
                baseline_net_value,
                2
            ),


        # ------------------------------
        # DECISION STATUS
        # ------------------------------

        "intervention":
            selected_gate[
                "intervene"
            ],


        "policy_allowed":
            policy_result[
                "allowed"
            ],


        # ------------------------------
        # EXPLANATION
        # ------------------------------

        "reasons":
            explanation[
                "reasons"
            ],


        "warnings":
            explanation[
                "warnings"
            ]
    }