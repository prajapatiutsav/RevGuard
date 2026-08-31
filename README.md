# RevGuard AI

## AI-Powered Revenue Recovery Decision Engine

RevGuard AI is an intelligent payment recovery system that analyzes failed payments and determines the economically optimal recovery action for each customer.

Instead of applying the same recovery strategy to every failed payment, RevGuard evaluates customer behavior, payment characteristics, recovery probability, action cost, and incremental economic value before recommending an action.

---

## Key Capabilities

- Failed payment analysis
- Customer state evaluation
- ML-based recovery prediction
- Action recommendation
- Counterfactual action simulation
- Uplift analysis
- Incremental recovery estimation
- Economic action optimization
- Policy validation
- Intervention gating
- Explainable AI recommendations
- FastAPI backend
- Interactive web dashboard

---

## Recovery Actions

RevGuard evaluates the following recovery strategies:

- Retry
- Payment Link
- WhatsApp
- Email
- Voice Call
- Human Escalation

---

## Decision Pipeline

Failed Payment
        ↓
Customer State
        ↓
ML Prediction
        ↓
Action Evaluation
        ↓
Counterfactual Simulation
        ↓
Incremental Value Calculation
        ↓
Policy Check
        ↓
Intervention Gate
        ↓
Explainable Recommendation
        ↓
Dashboard

---

## Machine Learning

RevGuard uses machine-learning models to estimate recovery outcomes and evaluate possible recovery actions.

The trained models are stored as:

- `recovery_model.pkl`
- `action_model.pkl`

The corresponding training pipelines are:

- `recovery_model.py`
- `action_model.py`

---

## Counterfactual & Uplift Engine

The system evaluates multiple possible recovery actions for the same failed payment.

For each action, RevGuard estimates:

- Recovery probability
- Probability uplift
- Incremental revenue
- Action cost
- Net incremental value

This allows the system to determine whether changing the recovery strategy is economically beneficial.

---

## Backend

The backend is implemented using FastAPI.

Main API:

`api.py`

Example endpoint:

`POST /analyze-payment`

The endpoint accepts a transaction ID and returns the RevGuard recommendation, economic metrics, policy status, intervention decision, explanations, and warnings.

---

## Frontend

The dashboard is located in:

`frontend/`

It contains:

- `index.html`
- `style.css`
- `app.js`

The dashboard displays:

- Revenue at risk
- Revenue recovered
- Recovery rate
- Incremental opportunity
- Recovery cases
- Unrecovered revenue
- Historical action performance
- AI strategy distribution
- Transaction-level recommendations
- Explainability and warnings

---

## Project Structure

```text
REVGUARD/
│
├── api.py
├── revguard_engine.py
├── customer_state.py
├── policy_engine.py
├── intervention_gate.py
├── explainability.py
├── action_executor.py
├── feedback.py
│
├── recovery_model.py
├── recovery_model.pkl
├── action_model.py
├── action_model.pkl
│
├── counterfactual_simulator.py
├── uplift_engine.py
│
├── main.py
│
├── data/
│   ├── cleaned/
│   ├── customers.csv
│   ├── customer_interactions.csv
│   ├── transactions.csv
│   ├── recovery_outcomes.csv
│   └── action_history.csv
│
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js