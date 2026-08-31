const API_BASE_URL = "https://revguard-jaui.onrender.com";


// =====================================================
// GLOBAL STATE
// =====================================================

let failedPayments = [];

let notifications = [];

let unreadNotifications = new Set();

let currentForecast = null;


// =====================================================
// HELPERS
// =====================================================

function formatCurrency(value) {

    const number = Number(value || 0);

    return "₹" + number.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}


function formatPercent(value) {

    let number = Number(value || 0);

    if (Math.abs(number) <= 1) {
        number = number * 100;
    }

    return number.toFixed(2) + "%";
}


function formatAction(action) {

    if (!action) {
        return "—";
    }

    return String(action)
        .replace(/_/g, " ")
        .replace(/\b\w/g, letter => letter.toUpperCase());
}


function getElement(...ids) {

    for (const id of ids) {

        const element =
            document.getElementById(id);

        if (element) {
            return element;
        }
    }

    return null;
}


function getDataValue(data, ...keys) {

    for (const key of keys) {

        if (
            data &&
            data[key] !== undefined &&
            data[key] !== null
        ) {
            return data[key];
        }
    }

    return 0;
}


function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function normalizeStatus(status) {

    if (!status) {
        return "at-risk";
    }

    return String(status)
        .toLowerCase()
        .replace(/_/g, "-")
        .trim();
}


function getPaymentStatus(payment) {

    return normalizeStatus(
        payment.status ||
        payment.recovery_status ||
        payment.recoveryStatus ||
        payment.payment_status ||
        "at-risk"
    );
}


// =====================================================
// LOAD ANALYTICS
// =====================================================

async function loadAnalytics() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/analytics`
            );


        if (!response.ok) {

            throw new Error(
                `Analytics request failed: ${response.status}`
            );
        }


        const data =
            await response.json();


        console.log(
            "RevGuard Analytics:",
            data
        );


        updateDashboard(data);


    } catch (error) {

        console.error(
            "Failed to load analytics:",
            error
        );

        showAnalyticsError();
    }
}


// =====================================================
// UPDATE DASHBOARD
// =====================================================

function updateDashboard(data) {

    console.log(
        "Updating dashboard with:",
        data
    );


    const revenueRisk =
        getElement(
            "revenueAtRisk",
            "revenue-at-risk"
        );


    const revenueRecovered =
        getElement(
            "recoveredRevenue",
            "revenueRecovered",
            "revenue-recovered"
        );


    const recoveryRate =
        getElement(
            "recoveryRate",
            "recovery-rate"
        );


    const incrementalOpportunity =
        getElement(
            "incrementalOpportunity",
            "incremental-opportunity"
        );


    const recoveryCases =
        getElement(
            "totalCases",
            "recoveryCases",
            "recovery-cases"
        );


    const unrecoveredRevenue =
        getElement(
            "unrecoveredRevenue",
            "unrecovered-revenue"
        );


    // =================================================
    // REVENUE AT RISK
    // =================================================

    if (revenueRisk) {

        const value =
            getDataValue(
                data,
                "revenue_at_risk",
                "revenueAtRisk",
                "revenue_risk",
                "total_revenue_at_risk"
            );


        revenueRisk.textContent =
            formatCurrency(value);
    }


    // =================================================
    // REVENUE RECOVERED
    // =================================================

    if (revenueRecovered) {

        const value =
            getDataValue(
                data,
                "recovered_revenue",
                "revenue_recovered",
                "revenueRecovered",
                "total_recovered_revenue"
            );


        revenueRecovered.textContent =
            formatCurrency(value);
    }


    // =================================================
    // RECOVERY RATE
    // =================================================

    if (recoveryRate) {

        const value =
            getDataValue(
                data,
                "recovery_rate",
                "recoveryRate"
            );


        recoveryRate.textContent =
            formatPercent(value);
    }


    // =================================================
    // INCREMENTAL OPPORTUNITY
    // =================================================

    if (incrementalOpportunity) {

        const value =
            getDataValue(
                data,
                "incremental_opportunity",
                "incrementalOpportunity",
                "potential_incremental_recovery",
                "total_incremental_recovery"
            );


        incrementalOpportunity.textContent =
            formatCurrency(value);
    }


    // =================================================
    // RECOVERY CASES
    // =================================================

    if (recoveryCases) {

        const value =
            getDataValue(
                data,
                "total_cases",
                "recovery_cases",
                "recoveryCases",
                "cases",
                "record_count"
            );


        recoveryCases.textContent =
            Number(value || 0)
                .toLocaleString("en-IN");
    }


    // =================================================
    // UNRECOVERED REVENUE
    // =================================================

    if (unrecoveredRevenue) {

        const value =
            getDataValue(
                data,
                "unrecovered_revenue",
                "unrecoveredRevenue",
                "remaining_revenue"
            );


        unrecoveredRevenue.textContent =
            formatCurrency(value);
    }


    // =================================================
    // CHART DATA
    // =================================================

    const actionPerformance =
        data.action_performance ||
        data.actionPerformance ||
        data.recovery_rate_by_action ||
        [];


    const strategyDistribution =
        data.strategy_distribution ||
        data.strategyDistribution ||
        data.best_action_distribution ||
        data.bestActionDistribution ||
        {};


    updateRecoveryChart(
        actionPerformance
    );


    updateStrategyChart(
        strategyDistribution
    );


    // =================================================
    // LOAD NEW FEATURES
    // =================================================

    loadRecoveryForecast();

    loadFailedPayments();
}


// =====================================================
// RECOVERY FORECAST
// =====================================================

async function loadRecoveryForecast() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/recovery-forecast`
            );


        if (!response.ok) {

            throw new Error(
                `Forecast request failed: ${response.status}`
            );
        }


        const data =
            await response.json();


        currentForecast = data;


        updateRecoveryForecast(
            data
        );


    } catch (error) {

        console.error(
            "Recovery forecast failed:",
            error
        );


        /*
         * Fallback:
         * Try calculating a transparent
         * run-rate forecast from analytics.
         */

        try {

            const response =
                await fetch(
                    `${API_BASE_URL}/analytics`
                );


            if (!response.ok) {
                throw new Error("Analytics unavailable");
            }


            const analytics =
                await response.json();


            const recovered =
                Number(
                    analytics.recovered_revenue ||
                    analytics.revenue_recovered ||
                    0
                );


            const atRisk =
                Number(
                    analytics.revenue_at_risk ||
                    0
                );


            let rate =
                Number(
                    analytics.recovery_rate ||
                    0
                );


            if (rate > 1) {
                rate = rate / 100;
            }


            const projected =
                atRisk * rate;


            const fallback = {

                projected_recovery:
                    projected,

                current_recovered:
                    recovered,

                revenue_at_risk:
                    atRisk,

                additional_opportunity:
                    Math.max(
                        projected - recovered,
                        0
                    ),

                recovery_rate:
                    rate,

                forecast_type:
                    "run_rate"

            };


            currentForecast =
                fallback;


            updateRecoveryForecast(
                fallback
            );


        } catch (fallbackError) {

            console.error(
                "Forecast fallback failed:",
                fallbackError
            );


            showForecastUnavailable();
        }
    }
}


// =====================================================
// UPDATE RECOVERY FORECAST
// =====================================================

function updateRecoveryForecast(data) {

    const projectedElement =
        getElement(
            "forecastProjectedRecovery"
        );


    const currentElement =
        getElement(
            "forecastCurrentRecovered"
        );


    const riskElement =
        getElement(
            "forecastRevenueAtRisk"
        );


    const opportunityElement =
        getElement(
            "forecastAdditionalOpportunity"
        );


    const rateElement =
        getElement(
            "forecastRecoveryRate"
        );


    const progressBar =
        getElement(
            "forecastProgressBar"
        );


    const noteElement =
        getElement(
            "forecastNote"
        );


    const projected =
        Number(
            getDataValue(
                data,
                "projected_recovery",
                "projectedRecovery",
                "forecast_recovery",
                "forecastRecovery"
            )
        );


    const currentRecovered =
        Number(
            getDataValue(
                data,
                "current_recovered",
                "currentRecovered",
                "recovered_revenue",
                "recoveredRevenue"
            )
        );


    const revenueAtRisk =
        Number(
            getDataValue(
                data,
                "revenue_at_risk",
                "revenueAtRisk"
            )
        );


    const additional =
        Number(
            getDataValue(
                data,
                "additional_opportunity",
                "additionalOpportunity",
                "incremental_opportunity"
            )
        );


    let rate =
        Number(
            getDataValue(
                data,
                "recovery_rate",
                "recoveryRate"
            )
        );


    if (rate > 1) {
        rate = rate / 100;
    }


    if (projectedElement) {

        projectedElement.textContent =
            formatCurrency(projected);
    }


    if (currentElement) {

        currentElement.textContent =
            formatCurrency(currentRecovered);
    }


    if (riskElement) {

        riskElement.textContent =
            formatCurrency(revenueAtRisk);
    }


    if (opportunityElement) {

        opportunityElement.textContent =
            formatCurrency(additional);
    }


    if (rateElement) {

        rateElement.textContent =
            formatPercent(rate);
    }


    if (progressBar) {

        const progress =
            Math.max(
                0,
                Math.min(
                    rate * 100,
                    100
                )
            );


        progressBar.style.width =
            `${progress}%`;
    }


    if (noteElement) {

        const forecastType =
            data.forecast_type ||
            data.forecastType ||
            "run_rate";


        if (
            forecastType ===
            "run_rate"
        ) {

            noteElement.textContent =
                "Projection uses RevGuard's current recovery rate as a transparent run-rate estimate.";
        } else {

            noteElement.textContent =
                "Forecast generated from the current RevGuard recovery analytics.";
        }
    }
}


function showForecastUnavailable() {

    const ids = [

        "forecastProjectedRecovery",
        "forecastCurrentRecovered",
        "forecastRevenueAtRisk",
        "forecastAdditionalOpportunity",
        "forecastRecoveryRate"

    ];


    ids.forEach(id => {

        const element =
            document.getElementById(id);


        if (element) {
            element.textContent =
                "Unavailable";
        }
    });


    const note =
        document.getElementById(
            "forecastNote"
        );


    if (note) {

        note.textContent =
            "Recovery forecast is currently unavailable.";
    }
}


// =====================================================
// FAILED PAYMENT ALERTS
// =====================================================

async function loadFailedPayments() {

    const table =
        getElement(
            "failedPaymentsTable"
        );


    if (table) {

        table.innerHTML = `
            <tr>
                <td
                    colspan="6"
                    class="table-loading"
                >
                    Loading failed payments...
                </td>
            </tr>
        `;
    }


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/failed-payments`
            );


        if (!response.ok) {

            throw new Error(
                `Failed payments request failed: ${response.status}`
            );
        }


        const data =
            await response.json();


        failedPayments =
            Array.isArray(data)
                ? data
                : (
                    data.payments ||
                    data.failed_payments ||
                    data.transactions ||
                    []
                );


        console.log(
            "Failed payments:",
            failedPayments
        );


        populateReasonFilter();

        renderFailedPayments();

        buildNotifications();


    } catch (error) {

        console.error(
            "Failed to load failed payments:",
            error
        );


        if (table) {

            table.innerHTML = `
                <tr>
                    <td
                        colspan="6"
                        class="table-loading"
                    >
                        Failed payment alerts unavailable.
                    </td>
                </tr>
            `;
        }


        updateAlertCount(0);

        updateNotificationCenter();
    }
}


// =====================================================
// POPULATE FAILURE REASON FILTER
// =====================================================

function populateReasonFilter() {

    const select =
        getElement(
            "paymentReasonFilter"
        );


    if (!select) {
        return;
    }


    const currentValue =
        select.value;


    const reasons =
        [
            ...new Set(
                failedPayments
                    .map(payment =>
                        payment.failure_reason ||
                        payment.failureReason ||
                        payment.reason
                    )
                    .filter(Boolean)
            )
        ]
        .sort();


    select.innerHTML = `
        <option value="all">
            All Failure Reasons
        </option>
    `;


    reasons.forEach(reason => {

        const option =
            document.createElement(
                "option"
            );


        option.value =
            String(reason);


        option.textContent =
            formatAction(reason);


        select.appendChild(
            option
        );
    });


    if (
        reasons.includes(
            currentValue
        )
    ) {

        select.value =
            currentValue;
    }
}


// =====================================================
// FILTER FAILED PAYMENTS
// =====================================================

function getFilteredPayments() {

    const searchInput =
        getElement(
            "paymentSearch"
        );


    const statusFilter =
        getElement(
            "paymentStatusFilter"
        );


    const reasonFilter =
        getElement(
            "paymentReasonFilter"
        );


    const minimumAmountInput =
        getElement(
            "minimumAmount"
        );


    const search =
        (
            searchInput?.value ||
            ""
        )
        .trim()
        .toLowerCase();


    const selectedStatus =
        statusFilter?.value ||
        "all";


    const selectedReason =
        reasonFilter?.value ||
        "all";


    const minimumAmount =
        Number(
            minimumAmountInput?.value ||
            0
        );


    return failedPayments.filter(
        payment => {

            const transactionId =
                String(
                    payment.transaction_id ||
                    payment.transactionId ||
                    payment.id ||
                    ""
                )
                .toLowerCase();


            const customer =
                String(
                    payment.customer_id ||
                    payment.customerId ||
                    payment.customer ||
                    ""
                )
                .toLowerCase();


            const failureReason =
                String(
                    payment.failure_reason ||
                    payment.failureReason ||
                    payment.reason ||
                    ""
                )
                .toLowerCase();


            const amount =
                Number(
                    payment.amount ||
                    0
                );


            const status =
                getPaymentStatus(
                    payment
                );


            // SEARCH

            const matchesSearch =
                !search ||
                transactionId.includes(search) ||
                customer.includes(search) ||
                failureReason.includes(search);


            // STATUS

            const matchesStatus =
                selectedStatus === "all" ||
                status === selectedStatus;


            // FAILURE REASON

            const matchesReason =
                selectedReason === "all" ||
                (
                    payment.failure_reason ||
                    payment.failureReason ||
                    payment.reason ||
                    ""
                ) === selectedReason;


            // MINIMUM AMOUNT

            const matchesAmount =
                amount >= minimumAmount;


            return (
                matchesSearch &&
                matchesStatus &&
                matchesReason &&
                matchesAmount
            );
        }
    );
}


// =====================================================
// RENDER FAILED PAYMENT TABLE
// =====================================================

function renderFailedPayments() {

    const table =
        getElement(
            "failedPaymentsTable"
        );


    const emptyState =
        getElement(
            "alertsEmpty"
        );


    if (!table) {
        return;
    }


    const filteredPayments =
        getFilteredPayments();


    updateAlertCount(
        failedPayments.filter(
            payment => {

                const status =
                    getPaymentStatus(
                        payment
                    );

                return (
                    status !==
                    "recovered"
                );
            }
        ).length
    );


    table.innerHTML =
        "";


    if (
        filteredPayments.length === 0
    ) {

        if (emptyState) {

            emptyState.classList.remove(
                "hidden"
            );
        }


        return;
    }


    if (emptyState) {

        emptyState.classList.add(
            "hidden"
        );
    }


    filteredPayments.forEach(
        payment => {

            const row =
                document.createElement(
                    "tr"
                );


            const transactionId =
                payment.transaction_id ||
                payment.transactionId ||
                payment.id ||
                "—";


            const customer =
                payment.customer_id ||
                payment.customerId ||
                payment.customer ||
                "—";


            const amount =
                Number(
                    payment.amount ||
                    0
                );


            const reason =
                payment.failure_reason ||
                payment.failureReason ||
                payment.reason ||
                "Unknown";


            const action =
                payment.recommended_action ||
                payment.recommendedAction ||
                payment.action ||
                "—";


            const status =
                getPaymentStatus(
                    payment
                );


            row.innerHTML = `

                <td>

                    <strong>
                        #${escapeHTML(transactionId)}
                    </strong>

                </td>


                <td>
                    ${escapeHTML(customer)}
                </td>


                <td>

                    <strong>
                        ${formatCurrency(amount)}
                    </strong>

                </td>


                <td>

                    <span class="failure-reason-cell">
                        ${escapeHTML(
                            formatAction(reason)
                        )}
                    </span>

                </td>


                <td>

                    <span class="action-cell">
                        ${escapeHTML(
                            formatAction(action)
                        )}
                    </span>

                </td>


                <td>

                    <span
                        class="payment-status status-${escapeHTML(status)}"
                    >
                        ${escapeHTML(
                            formatAction(status)
                        )}
                    </span>

                </td>

            `;


            row.addEventListener(
                "click",
                () => {

                    const input =
                        getElement(
                            "transactionId"
                        );


                    if (input) {

                        input.value =
                            transactionId;
                    }


                    const analyzer =
                        getElement(
                            "analyzeButton"
                        );


                    if (analyzer) {

                        analyzer.scrollIntoView({
                            behavior: "smooth",
                            block: "center"
                        });
                    }

                }
            );


            table.appendChild(
                row
            );
        }
    );
}


// =====================================================
// ALERT COUNT
// =====================================================

function updateAlertCount(count) {

    const element =
        getElement(
            "openAlertCount"
        );


    if (element) {

        element.textContent =
            Number(count || 0)
                .toLocaleString("en-IN");
    }
}


// =====================================================
// NOTIFICATION CENTER
// =====================================================

function buildNotifications() {

    const candidates =
        failedPayments
            .filter(
                payment =>
                    getPaymentStatus(
                        payment
                    ) !== "recovered"
            )
            .sort(
                (a, b) =>
                    Number(
                        b.amount || 0
                    ) -
                    Number(
                        a.amount || 0
                    )
            );


    notifications =
        candidates
            .slice(0, 8)
            .map(
                payment => {

                    const transactionId =
                        payment.transaction_id ||
                        payment.transactionId ||
                        payment.id ||
                        "—";


                    const amount =
                        Number(
                            payment.amount ||
                            0
                        );


                    const reason =
                        payment.failure_reason ||
                        payment.failureReason ||
                        payment.reason ||
                        "Payment failure";


                    return {

                        id:
                            `payment-${transactionId}`,

                        title:
                            "Failed payment requires attention",

                        message:
                            `Transaction #${transactionId} · ${formatCurrency(amount)} · ${formatAction(reason)}`,

                        transactionId:
                            transactionId,

                        amount:
                            amount,

                        type:
                            "payment-alert"

                    };
                }
            );


    const storedRead =
        JSON.parse(
            localStorage.getItem(
                "revguardReadNotifications"
            ) ||
            "[]"
        );


    unreadNotifications =
        new Set(
            notifications
                .map(
                    notification =>
                        notification.id
                )
                .filter(
                    id =>
                        !storedRead.includes(id)
                )
        );


    updateNotificationCenter();
}


// =====================================================
// UPDATE NOTIFICATION CENTER
// =====================================================

function updateNotificationCenter() {

    const list =
        getElement(
            "notificationList"
        );


    const countElement =
        getElement(
            "notificationCount"
        );


    const summary =
        getElement(
            "notificationSummary"
        );


    if (
        countElement
    ) {

        const count =
            unreadNotifications.size;


        countElement.textContent =
            count > 99
                ? "99+"
                : count;


        countElement.classList.toggle(
            "hidden",
            count === 0
        );
    }


    if (summary) {

        const count =
            unreadNotifications.size;


        summary.textContent =
            count === 0
                ? "No new alerts"
                : `${count} unread alert${count === 1 ? "" : "s"}`;
    }


    if (!list) {
        return;
    }


    if (
        notifications.length === 0
    ) {

        list.innerHTML = `

            <div class="notification-empty">

                <span>
                    ✓
                </span>

                <p>
                    You're all caught up.
                </p>

            </div>

        `;

        return;
    }


    list.innerHTML =
        "";


    notifications.forEach(
        notification => {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "notification-item";


            if (
                unreadNotifications.has(
                    notification.id
                )
            ) {

                item.classList.add(
                    "unread"
                );
            }


            item.innerHTML = `

                <div class="notification-item-icon">
                    🚨
                </div>


                <div class="notification-item-content">

                    <strong>
                        ${escapeHTML(
                            notification.title
                        )}
                    </strong>

                    <p>
                        ${escapeHTML(
                            notification.message
                        )}
                    </p>

                </div>

            `;


            item.addEventListener(
                "click",
                () => {

                    markNotificationRead(
                        notification.id
                    );


                    const input =
                        getElement(
                            "transactionId"
                        );


                    if (input) {

                        input.value =
                            notification.transactionId;
                    }


                    const searchSection =
                        getElement(
                            "search-section"
                        );


                    if (searchSection) {

                        searchSection.scrollIntoView({
                            behavior: "smooth"
                        });
                    }

                }
            );


            list.appendChild(
                item
            );
        }
    );
}


// =====================================================
// MARK ONE NOTIFICATION READ
// =====================================================

function markNotificationRead(id) {

    unreadNotifications.delete(
        id
    );


    saveReadNotifications();

    updateNotificationCenter();
}


// =====================================================
// MARK ALL NOTIFICATIONS READ
// =====================================================

function markAllNotificationsRead() {

    notifications.forEach(
        notification => {

            unreadNotifications.delete(
                notification.id
            );
        }
    );


    saveReadNotifications();

    updateNotificationCenter();
}


// =====================================================
// SAVE READ NOTIFICATIONS
// =====================================================

function saveReadNotifications() {

    const existing =
        JSON.parse(
            localStorage.getItem(
                "revguardReadNotifications"
            ) ||
            "[]"
        );


    const currentIds =
        notifications.map(
            notification =>
                notification.id
        );


    const merged =
        [
            ...new Set(
                [
                    ...existing,
                    ...currentIds.filter(
                        id =>
                            !unreadNotifications.has(id)
                    )
                ]
            )
        ];


    localStorage.setItem(
        "revguardReadNotifications",
        JSON.stringify(merged)
    );
}


// =====================================================
// NOTIFICATION PANEL
// =====================================================

function toggleNotificationPanel() {

    const panel =
        getElement(
            "notificationPanel"
        );


    if (!panel) {
        return;
    }


    panel.classList.toggle(
        "hidden"
    );
}


function closeNotificationPanel() {

    const panel =
        getElement(
            "notificationPanel"
        );


    if (panel) {

        panel.classList.add(
            "hidden"
        );
    }
}


// =====================================================
// ANALYZE PAYMENT
// =====================================================

async function analyzePayment() {

    const transactionInput =
        getElement(
            "transactionId",
            "transaction-id",
            "transaction_id"
        );


    if (!transactionInput) {

        console.error(
            "Transaction ID input not found."
        );

        return;
    }


    const transactionId =
        transactionInput.value.trim();


    if (!transactionId) {

        alert(
            "Please enter a transaction ID."
        );

        return;
    }


    const button =
        getElement(
            "analyzeButton",
            "analyzePayment",
            "analyze-payment"
        );


    if (button) {

        button.disabled =
            true;

        button.textContent =
            "Analyzing...";
    }


    try {

        const errorElement =
            getElement(
                "error"
            );


        if (errorElement) {

            errorElement.textContent =
                "";

            errorElement.classList.add(
                "hidden"
            );
        }


        const response =
            await fetch(
                `${API_BASE_URL}/analyze-payment`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            transaction_id:
                                Number(
                                    transactionId
                                )
                        })
                }
            );


        if (!response.ok) {

            let errorMessage =
                "Unable to analyze payment.";


            try {

                const errorData =
                    await response.json();


                if (
                    errorData.detail
                ) {

                    errorMessage =
                        errorData.detail;
                }

            } catch (_) {

                // Ignore parsing error
            }


            throw new Error(
                errorMessage
            );
        }


        const result =
            await response.json();


        console.log(
            "RevGuard decision:",
            result
        );


        displayPaymentResult(
            result
        );


    } catch (error) {

        console.error(
            "Payment analysis failed:",
            error
        );


        const errorElement =
            getElement(
                "error"
            );


        if (errorElement) {

            errorElement.textContent =
                error.message ||
                "Something went wrong while analyzing the payment.";

            errorElement.classList.remove(
                "hidden"
            );

        } else {

            alert(
                error.message ||
                "Something went wrong while analyzing the payment."
            );
        }


    } finally {

        if (button) {

            button.disabled =
                false;

            button.textContent =
                "Analyze Payment";
        }
    }
}


// =====================================================
// DISPLAY PAYMENT RESULT
// =====================================================

function displayPaymentResult(result) {

    console.log(
        "Displaying payment result:",
        result
    );


    // =================================================
    // TRANSACTION DETAILS
    // =================================================

    const transactionElement =
        getElement(
            "transaction",
            "resultTransaction",
            "transactionValue"
        );


    const customerElement =
        getElement(
            "customer",
            "resultCustomer",
            "customerValue"
        );


    const amountElement =
        getElement(
            "amount",
            "resultAmount",
            "amountValue"
        );


    const failureElement =
        getElement(
            "failure",
            "failureReason",
            "resultFailure",
            "failureValue"
        );


    if (transactionElement) {

        transactionElement.textContent =
            result.transaction_id ??
            "—";
    }


    if (customerElement) {

        customerElement.textContent =
            result.customer_id ??
            "—";
    }


    if (amountElement) {

        amountElement.textContent =
            formatCurrency(
                result.amount
            );
    }


    if (failureElement) {

        failureElement.textContent =
            formatAction(
                result.failure_reason
            );
    }


    // =================================================
    // AI COMMAND CENTER
    // =================================================

    const aiAction =
        getElement(
            "aiRecommendedAction"
        );


    const aiProbability =
        getElement(
            "aiRecoveryProbability"
        );


    const aiIncremental =
        getElement(
            "aiIncrementalValue"
        );


    const aiExpected =
        getElement(
            "aiExpectedRecovery"
        );


    const aiNetValue =
        getElement(
            "aiNetEconomicValue"
        );


    const aiDescription =
        getElement(
            "aiDecisionDescription"
        );


    if (aiAction) {

        aiAction.textContent =
            formatAction(
                result.recommended_action
            );
    }


    if (aiProbability) {

        aiProbability.textContent =
            formatPercent(
                result.recovery_probability
            );
    }


    if (aiIncremental) {

        aiIncremental.textContent =
            formatCurrency(
                result.incremental_value
            );
    }


    if (aiExpected) {

        aiExpected.textContent =
            formatCurrency(
                result.expected_recovery
            );
    }


    if (aiNetValue) {

        aiNetValue.textContent =
            formatCurrency(
                result.net_economic_value
            );
    }


    if (aiDescription) {

        const intervention =
            Boolean(
                result.intervention
            );


        aiDescription.textContent =
            intervention
                ? "RevGuard recommends an intervention because this payment presents a meaningful recovery opportunity."
                : "RevGuard does not recommend an additional intervention for this payment.";
    }


    displayAIReasons(
        result
    );


    // =================================================
    // EXISTING AI RECOMMENDATION
    // =================================================

    const actionElement =
        getElement(
            "recommendedAction",
            "aiRecommendation",
            "recommendation"
        );


    const probabilityElement =
        getElement(
            "probability",
            "recoveryProbability"
        );


    const incrementalElement =
        getElement(
            "incrementalValue",
            "incremental-value"
        );


    const baselineElement =
        getElement(
            "baseline",
            "baselineAction",
            "baseline-action"
        );


    if (actionElement) {

        actionElement.textContent =
            formatAction(
                result.recommended_action
            );
    }


    if (probabilityElement) {

        probabilityElement.textContent =
            formatPercent(
                result.recovery_probability
            );
    }


    if (incrementalElement) {

        incrementalElement.textContent =
            formatCurrency(
                result.incremental_value
            );
    }


    if (baselineElement) {

        baselineElement.textContent =
            formatAction(
                result.baseline_action
            );
    }


    // =================================================
    // INTERVENTION BADGE
    // =================================================

    const interventionBadge =
        getElement(
            "interventionBadge"
        );


    if (interventionBadge) {

        const intervention =
            Boolean(
                result.intervention
            );


        interventionBadge.textContent =
            intervention
                ? "Intervention Required"
                : "No Intervention";


        interventionBadge.classList.remove(
            "yes",
            "no"
        );


        interventionBadge.classList.add(
            intervention
                ? "yes"
                : "no"
        );
    }


    // =================================================
    // POLICY
    // =================================================

    const policyElement =
        getElement(
            "policy",
            "policyStatus"
        );


    if (policyElement) {

        policyElement.textContent =
            result.policy_allowed
                ? "Allowed"
                : "Blocked";
    }


    // =================================================
    // EXISTING EXPLANATION
    // =================================================

    displayExplanation(
        result
    );


    // =================================================
    // SHOW RESULT
    // =================================================

    const resultSection =
        getElement(
            "result",
            "paymentResult",
            "analysisResult",
            "resultSection"
        );


    if (resultSection) {

        resultSection.classList.remove(
            "hidden"
        );


        resultSection.style.display =
            "grid";


        setTimeout(
            () => {

                resultSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            },
            100
        );
    }
}


// =====================================================
// AI COMMAND CENTER REASONS
// =====================================================

function displayAIReasons(result) {

    const container =
        getElement(
            "aiReasons"
        );


    if (!container) {
        return;
    }


    container.innerHTML =
        "";


    const reasons =
        Array.isArray(
            result.reasons
        )
            ? result.reasons
            : [];


    if (
        reasons.length === 0
    ) {

        const li =
            document.createElement(
                "li"
            );


        li.textContent =
            "No additional explanation available.";


        container.appendChild(
            li
        );


        return;
    }


    reasons
        .slice(0, 6)
        .forEach(
            reason => {

                const li =
                    document.createElement(
                        "li"
                    );


                li.textContent =
                    reason;


                container.appendChild(
                    li
                );
            }
        );
}


// =====================================================
// EXPLANATION
// =====================================================

function displayExplanation(result) {

    const reasonsContainer =
        getElement(
            "reasons",
            "decisionReasons"
        );


    if (reasonsContainer) {

        reasonsContainer.innerHTML =
            "";


        if (
            Array.isArray(
                result.reasons
            ) &&
            result.reasons.length > 0
        ) {

            result.reasons.forEach(
                reason => {

                    const li =
                        document.createElement(
                            "li"
                        );


                    li.textContent =
                        reason;


                    reasonsContainer.appendChild(
                        li
                    );
                }
            );


        } else {

            const li =
                document.createElement(
                    "li"
                );


            li.textContent =
                "No additional explanation available.";


            reasonsContainer.appendChild(
                li
            );
        }
    }


    // =================================================
    // WARNINGS
    // =================================================

    const warningsContainer =
        getElement(
            "warningsContainer"
        );


    const warningsList =
        getElement(
            "warnings",
            "decisionWarnings"
        );


    if (
        warningsContainer &&
        warningsList
    ) {

        warningsList.innerHTML =
            "";


        if (
            Array.isArray(
                result.warnings
            ) &&
            result.warnings.length > 0
        ) {

            result.warnings.forEach(
                warning => {

                    const li =
                        document.createElement(
                            "li"
                        );


                    li.textContent =
                        warning;


                    warningsList.appendChild(
                        li
                    );
                }
            );


            warningsContainer.classList.remove(
                "hidden"
            );


        } else {

            warningsContainer.classList.add(
                "hidden"
            );
        }
    }
}


// =====================================================
// RECOVERY RATE CHART
// =====================================================

function updateRecoveryChart(
    actionPerformance
) {

    const container =
        getElement(
            "recoveryRateChart",
            "recoveryChart"
        );


    if (!container) {
        return;
    }


    container.innerHTML =
        "";


    if (
        !Array.isArray(
            actionPerformance
        )
    ) {

        if (
            actionPerformance &&
            typeof actionPerformance === "object"
        ) {

            actionPerformance =
                Object.entries(
                    actionPerformance
                ).map(
                    ([action, value]) => {

                        return {

                            action,

                            recovery_rate:
                                typeof value === "object"
                                    ? (
                                        value.recovery_rate ??
                                        value.rate ??
                                        value.value ??
                                        0
                                    )
                                    : value
                        };
                    }
                );

        } else {

            actionPerformance =
                [];
        }
    }


    if (
        actionPerformance.length === 0
    ) {

        container.innerHTML =
            `
            <div class="chart-loading">
                No recovery data available.
            </div>
            `;

        return;
    }


    actionPerformance.forEach(
        item => {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "bar-row";


            const label =
                document.createElement(
                    "div"
                );


            label.className =
                "bar-label";


            label.textContent =
                formatAction(
                    item.action
                );


            const track =
                document.createElement(
                    "div"
                );


            track.className =
                "bar-track";


            const fill =
                document.createElement(
                    "div"
                );


            fill.className =
                "bar-fill";


            let rate =
                Number(
                    item.recovery_rate ??
                    item.recoveryRate ??
                    item.rate ??
                    0
                );


            if (rate > 1) {
                rate =
                    rate / 100;
            }


            rate =
                Math.max(
                    0,
                    Math.min(
                        rate,
                        1
                    )
                );


            fill.style.width =
                `${rate * 100}%`;


            const value =
                document.createElement(
                    "div"
                );


            value.className =
                "bar-value";


            value.textContent =
                `${(
                    rate * 100
                ).toFixed(2)}%`;


            track.appendChild(
                fill
            );


            row.appendChild(
                label
            );


            row.appendChild(
                track
            );


            row.appendChild(
                value
            );


            container.appendChild(
                row
            );
        }
    );
}


// =====================================================
// STRATEGY DISTRIBUTION CHART
// =====================================================

function updateStrategyChart(
    distribution
) {

    const container =
        getElement(
            "strategyChart",
            "strategyDistributionChart"
        );


    if (!container) {
        return;
    }


    container.innerHTML =
        "";


    if (
        !distribution ||
        typeof distribution !== "object"
    ) {

        container.innerHTML =
            `
            <div class="chart-loading">
                No strategy data available.
            </div>
            `;

        return;
    }


    const entries =
        Object.entries(
            distribution
        )
        .map(
            ([action, value]) => {

                let count =
                    value;


                if (
                    value &&
                    typeof value === "object"
                ) {

                    count =
                        value.count ??
                        value.total ??
                        value.value ??
                        value.cases ??
                        0;
                }


                return [
                    action,
                    Number(count) || 0
                ];
            }
        )
        .sort(
            (a, b) =>
                b[1] - a[1]
        );


    if (
        entries.length === 0
    ) {

        container.innerHTML =
            `
            <div class="chart-loading">
                No strategy data available.
            </div>
            `;

        return;
    }


    const maxValue =
        Math.max(
            ...entries.map(
                item =>
                    item[1]
            ),
            1
        );


    entries.forEach(
        ([action, count]) => {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "strategy-row";


            const label =
                document.createElement(
                    "div"
                );


            label.className =
                "strategy-label";


            label.textContent =
                formatAction(
                    action
                );


            const track =
                document.createElement(
                    "div"
                );


            track.className =
                "strategy-track";


            const fill =
                document.createElement(
                    "div"
                );


            fill.className =
                "strategy-fill";


            const percentage =
                (
                    count /
                    maxValue
                ) * 100;


            fill.style.width =
                `${count > 0
                    ? Math.max(
                        percentage,
                        1
                    )
                    : 0}%`;


            const value =
                document.createElement(
                    "div"
                );


            value.className =
                "strategy-value";


            value.textContent =
                count.toLocaleString(
                    "en-IN"
                );


            track.appendChild(
                fill
            );


            row.appendChild(
                label
            );


            row.appendChild(
                track
            );


            row.appendChild(
                value
            );


            container.appendChild(
                row
            );
        }
    );
}


// =====================================================
// ANALYTICS ERROR
// =====================================================

function showAnalyticsError() {

    const metricIds = [

        "revenueAtRisk",

        "recoveredRevenue",

        "recoveryRate",

        "incrementalOpportunity",

        "totalCases",

        "unrecoveredRevenue"

    ];


    metricIds.forEach(
        id => {

            const element =
                document.getElementById(
                    id
                );


            if (
                element &&
                element.textContent
                    .trim() ===
                    "Loading..."
            ) {

                element.textContent =
                    "Unavailable";
            }
        }
    );


    const chartContainers = [

        "recoveryRateChart",

        "strategyChart"

    ];


    chartContainers.forEach(
        id => {

            const element =
                document.getElementById(
                    id
                );


            if (element) {

                element.innerHTML =
                    `
                    <div class="chart-loading">
                        Analytics unavailable.
                    </div>
                    `;
            }
        }
    );
}


// =====================================================
// PAYMENT FILTER EVENTS
// =====================================================

function setupPaymentFilters() {

    const search =
        getElement(
            "paymentSearch"
        );


    const status =
        getElement(
            "paymentStatusFilter"
        );


    const reason =
        getElement(
            "paymentReasonFilter"
        );


    const minimumAmount =
        getElement(
            "minimumAmount"
        );


    const clearButton =
        getElement(
            "clearPaymentFilters"
        );


    if (search) {

        search.addEventListener(
            "input",
            renderFailedPayments
        );
    }


    if (status) {

        status.addEventListener(
            "change",
            renderFailedPayments
        );
    }


    if (reason) {

        reason.addEventListener(
            "change",
            renderFailedPayments
        );
    }


    if (minimumAmount) {

        minimumAmount.addEventListener(
            "input",
            renderFailedPayments
        );
    }


    if (clearButton) {

        clearButton.addEventListener(
            "click",
            () => {

                if (search) {
                    search.value = "";
                }


                if (status) {
                    status.value =
                        "all";
                }


                if (reason) {
                    reason.value =
                        "all";
                }


                if (minimumAmount) {
                    minimumAmount.value =
                        "";
                }


                renderFailedPayments();
            }
        );
    }
}


// =====================================================
// NOTIFICATION EVENTS
// =====================================================

function setupNotifications() {

    const notificationButton =
        getElement(
            "notificationButton"
        );


    const markReadButton =
        getElement(
            "markNotificationsRead"
        );


    if (notificationButton) {

        notificationButton.addEventListener(
            "click",
            event => {

                event.stopPropagation();

                toggleNotificationPanel();
            }
        );
    }


    if (markReadButton) {

        markReadButton.addEventListener(
            "click",
            event => {

                event.stopPropagation();

                markAllNotificationsRead();
            }
        );
    }


    document.addEventListener(
        "click",
        event => {

            const panel =
                getElement(
                    "notificationPanel"
                );


            const button =
                getElement(
                    "notificationButton"
                );


            if (
                panel &&
                button &&
                !panel.contains(
                    event.target
                ) &&
                !button.contains(
                    event.target
                )
            ) {

                closeNotificationPanel();
            }
        }
    );
}


// =====================================================
// PAGE INITIALIZATION
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "RevGuard AI frontend initialized."
        );


        // =================================================
        // ENTER KEY SUPPORT
        // =================================================

        const input =
            getElement(
                "transactionId",
                "transaction-id",
                "transaction_id"
            );


        if (input) {

            input.addEventListener(
                "keydown",
                event => {

                    if (
                        event.key ===
                        "Enter"
                    ) {

                        analyzePayment();
                    }
                }
            );
        }


        // =================================================
        // NEW FEATURE EVENTS
        // =================================================

        setupPaymentFilters();

        setupNotifications();


        // =================================================
        // LOAD DASHBOARD
        // =================================================

        loadAnalytics();

    }
);