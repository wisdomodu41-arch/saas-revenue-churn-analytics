
import pandas as pd

# Load CSV files
datasets = {
    "accounts": pd.read_csv("ravenstack_accounts.csv"),
    "churn_events": pd.read_csv("ravenstack_churn_events.csv"),
    "feature_usage": pd.read_csv("ravenstack_feature_usage.csv"),
    "subscriptions": pd.read_csv("ravenstack_subscriptions.csv"),
    "support_tickets": pd.read_csv("ravenstack_support_tickets.csv")
}

# DATA CLEANING & PREPARATION

print("\n" + "=" * 60)
print("DATA CLEANING & PREPARATION")
print("=" * 60)

# Convert date columns to datetime
date_columns = {
    "accounts": ["created_at"],
    "churn_events": ["event_date"],
    "feature_usage": ["usage_date"],
    "subscriptions": ["start_date", "end_date"],
    "support_tickets": ["submitted_at", "closed_at"]
}

for name, columns in date_columns.items():
    for column in columns:
        if column in datasets[name].columns:
            datasets[name][column] = pd.to_datetime(
                datasets[name][column],
                errors="coerce"
            )

print("\nDATE CONVERSION COMPLETE")

# HANDLE MISSING VALUES
#subscription: missing end_date means the subscription is active
datasets["subscriptions"] ["is_active"] = (datasets["subscriptions"]
["end_date"].isna())
#churn events: missing feedback means no feedback was provided
datasets["churn_events"] ["feedback_text"] = (datasets["churn_events"]
["feedback_text"].fillna("No feedback provided"))
#Support tickets: keep missing satisfaction scores,
#but create an indicator showing that no rating was provided
datasets["support_tickets"] ["satisfaction_missing"] =(datasets["support_tickets"]
["satisfaction_score"].isna())
print("\nMISSING VALUES HANDLED SUCCESSFULLY")
# ==========================================
# FEATURE ENGINEERING
# ==========================================

print("\n" + "=" * 60)
print("FEATURE ENGINEERING")
print("=" * 60)

# Subscription status
datasets["subscriptions"]["is_active"] = (
    datasets["subscriptions"]["end_date"].isna()
).astype(int)

# Subscription tenure in days
analysis_date = datasets["subscriptions"]["end_date"].max()

datasets["subscriptions"]["tenure_days"] = (
    datasets["subscriptions"]["end_date"]
    .fillna(analysis_date)
    - datasets["subscriptions"]["start_date"]
).dt.days

# Convert tenure from days to months
datasets["subscriptions"]["tenure_months"] = (
    datasets["subscriptions"]["tenure_days"] / 30.44
).round(1)

print("Feature engineering completed successfully.")

print("\nNew subscription features:")
print(
    datasets["subscriptions"][
        [
            "subscription_id",
            "is_active",
            "tenure_days",
            "tenure_months"
        ]
    ].head()
)
# ==========================================
# REVENUE & SUBSCRIPTION FEATURES
# ==========================================

print("\n" + "=" * 60)
print("REVENUE & SUBSCRIPTION FEATURES")
print("=" * 60)

subscriptions = datasets["subscriptions"]

# Revenue per seat
subscriptions["mrr_per_seat"] = (
    subscriptions["mrr_amount"] /
    subscriptions["seats"].replace(0, pd.NA)
)

# Annual recurring revenue per seat
subscriptions["arr_per_seat"] = (
    subscriptions["arr_amount"] /
    subscriptions["seats"].replace(0, pd.NA)
)

# Check whether ARR is approximately 12x MRR
subscriptions["arr_mrr_ratio"] = (
    subscriptions["arr_amount"] /
    subscriptions["mrr_amount"].replace(0, pd.NA)
)

# Convert churn flag into a clearer business label
subscriptions["churn_status"] = subscriptions["churn_flag"].map({
    True: "Churned",
    False: "Retained"
})

print("Revenue features created successfully.")

print("\nNew revenue features:")
print(
    subscriptions[
        [
            "subscription_id",
            "mrr_amount",
            "seats",
            "mrr_per_seat",
            "arr_per_seat",
            "arr_mrr_ratio",
            "churn_status"
        ]
    ].head()
)
print("\nChurn flag values:")
print(subscriptions["churn_flag"].
value_counts(dropna=False))
# ============================================================
# EXPLORATORY DATA ANALYSIS (EDA)
# ============================================================

print("\n" + "=" * 60)
print("EXPLORATORY DATA ANALYSIS")
print("=" * 60)


# ------------------------------------------------------------
# 1. OVERALL CHURN RATE
# ------------------------------------------------------------

total_subscriptions = len(subscriptions)
total_churned = subscriptions["churn_flag"].sum()
total_retained = total_subscriptions - total_churned

churn_rate = (total_churned / total_subscriptions) * 100

print("\n--- OVERALL CUSTOMER METRICS ---")
print(f"Total subscriptions: {total_subscriptions:,}")
print(f"Churned subscriptions: {total_churned:,}")
print(f"Retained subscriptions: {total_retained:,}")
print(f"Overall churn rate: {churn_rate:.2f}%")

print("\nChurn status:")
print(subscriptions["churn_status"].value_counts())


# ------------------------------------------------------------
# 2. CHURN BY PLAN TIER
# ------------------------------------------------------------

print("\n--- CHURN BY PLAN TIER ---")

plan_churn = (
    subscriptions
    .groupby("plan_tier")
    .agg(
        customers=("subscription_id", "count"),
        churned=("churn_flag", "sum")
    )
)

plan_churn["churn_rate"] = (
    plan_churn["churned"] /
    plan_churn["customers"] * 100
)

print(plan_churn.sort_values("churn_rate", ascending=False))


# ------------------------------------------------------------
# 3. CHURN BY TENURE
# ------------------------------------------------------------

print("\n--- CHURN BY TENURE ---")

subscriptions["tenure_group"] = pd.cut(
    subscriptions["tenure_months"],
    bins=[0, 3, 6, 12, 24, float("inf")],
    labels=[
        "0-3 months",
        "3-6 months",
        "6-12 months",
        "12-24 months",
        "24+ months"
    ],
    include_lowest=True
)

tenure_churn = (
    subscriptions
    .groupby("tenure_group", observed=True)
    .agg(
        customers=("subscription_id", "count"),
        churned=("churn_flag", "sum")
    )
)

tenure_churn["churn_rate"] = (
    tenure_churn["churned"] /
    tenure_churn["customers"] * 100
)

print(tenure_churn)


# ------------------------------------------------------------
# 4. CHURN BY TRIAL STATUS
# ------------------------------------------------------------

print("\n--- CHURN BY TRIAL STATUS ---")

trial_churn = (
    subscriptions
    .groupby("is_trial")
    .agg(
        customers=("subscription_id", "count"),
        churned=("churn_flag", "sum")
    )
)

trial_churn["churn_rate"] = (
    trial_churn["churned"] /
    trial_churn["customers"] * 100
)

print(trial_churn)


# ------------------------------------------------------------
# 5. CHURN BY UPGRADE / DOWNGRADE BEHAVIOUR
# ------------------------------------------------------------

print("\n--- CHURN BY UPGRADE STATUS ---")

upgrade_churn = (
    subscriptions
    .groupby("upgrade_flag")
    .agg(
        customers=("subscription_id", "count"),
        churned=("churn_flag", "sum")
    )
)

upgrade_churn["churn_rate"] = (
    upgrade_churn["churned"] /
    upgrade_churn["customers"] * 100
)

print(upgrade_churn)


print("\n--- CHURN BY DOWNGRADE STATUS ---")

downgrade_churn = (
    subscriptions
    .groupby("downgrade_flag")
    .agg(
        customers=("subscription_id", "count"),
        churned=("churn_flag", "sum")
    )
)

downgrade_churn["churn_rate"] = (
    downgrade_churn["churned"] /
    downgrade_churn["customers"] * 100
)

print(downgrade_churn)


# ------------------------------------------------------------
# 6. REVENUE ANALYSIS
# ------------------------------------------------------------

print("\n--- REVENUE ANALYSIS ---")

revenue_summary = subscriptions.groupby("churn_status").agg(
    customers=("subscription_id", "count"),
    total_mrr=("mrr_amount", "sum"),
    average_mrr=("mrr_amount", "mean"),
    median_mrr=("mrr_amount", "median"),
    total_arr=("arr_amount", "sum"),
    average_arr=("arr_amount", "mean")
)

print(revenue_summary)


# ------------------------------------------------------------
# 7. MRR BY PLAN TIER
# ------------------------------------------------------------

print("\n--- REVENUE BY PLAN TIER ---")

plan_revenue = (
    subscriptions
    .groupby("plan_tier")
    .agg(
        customers=("subscription_id", "count"),
        total_mrr=("mrr_amount", "sum"),
        average_mrr=("mrr_amount", "mean"),
        total_arr=("arr_amount", "sum")
    )
)

print(plan_revenue.sort_values("total_mrr", ascending=False))


# ------------------------------------------------------------
# 8. SUPPORT TICKET ANALYSIS
# ------------------------------------------------------------

print("\n--- SUPPORT TICKET ANALYSIS ---")

support = datasets["support_tickets"].copy()

support_summary = (
    support
    .groupby("account_id")
    .agg(
        ticket_count=("ticket_id", "count"),
        avg_resolution_hours=("resolution_time_hours", "mean"),
        avg_first_response_minutes=("first_response_time_minutes", "mean"),
        avg_satisfaction=("satisfaction_score", "mean"),
        escalations=("escalation_flag", "sum")
    )
    .reset_index()
)

# Connect support behaviour to subscriptions
subscriptions = subscriptions.merge(
    support_summary,
    on="account_id",
    how="left"
)

# Customers with no tickets receive zero ticket count
subscriptions["ticket_count"] = (
    subscriptions["ticket_count"].fillna(0)
)

subscriptions["escalations"] = (
    subscriptions["escalations"].fillna(0)
)

print(
    subscriptions
    .groupby("churn_status")
    .agg(
        customers=("subscription_id", "count"),
        avg_tickets=("ticket_count", "mean"),
        avg_escalations=("escalations", "mean"),
        avg_resolution_hours=("avg_resolution_hours", "mean"),
        avg_satisfaction=("avg_satisfaction", "mean")
    )
)


# ------------------------------------------------------------
# 9. USAGE ANALYSIS
# ------------------------------------------------------------

print("\n--- USAGE ANALYSIS ---")

usage = datasets["feature_usage"].copy()

print("\nAvailable usage columns:")
print(usage.columns.tolist())

usage_summary = (
    usage
    .groupby("subscription_id")
    .agg(
        total_usage=("usage_count", "sum"),
        average_usage=("usage_count", "mean"),
        active_usage_days=("usage_date", "nunique")
    )
    .reset_index()
)

subscriptions = subscriptions.merge(
    usage_summary,
    on="subscription_id",
    how="left"
)

subscriptions["total_usage"] = (
    subscriptions["total_usage"].fillna(0)
)

subscriptions["average_usage"] = (
    subscriptions["average_usage"].fillna(0)
)

subscriptions["active_usage_days"] = (
    subscriptions["active_usage_days"].fillna(0)
)

print("\n--- USAGE BY CHURN STATUS ---")

usage_churn = (
    subscriptions
    .groupby("churn_status")
    .agg(
        customers=("subscription_id", "count"),
        avg_total_usage=("total_usage", "mean"),
        avg_usage=("average_usage", "mean"),
        avg_active_usage_days=("active_usage_days", "mean")
    )
)

print(usage_churn.round(2))



# ------------------------------------------------------------
# 9. USAGE ANALYSIS
# ------------------------------------------------------------

print("\n--- USAGE ANALYSIS ---")

usage = datasets["feature_usage"].copy()

print("\nAvailable usage columns:")
print(usage.columns.tolist())

usage_summary = (
    usage
    .groupby("subscription_id")
    .agg(
        total_usage=("usage_count", "sum"),
        average_usage=("usage_count", "mean"),
        active_usage_days=("usage_date", "nunique")
    )
    .reset_index()
)
print("\n---USAGE SUMMARY CHECK---")
print(usage_summary.head())
print("Rows:", len(usage_summary))
subscriptions = subscriptions.drop(columns=["total_usage","average_usage","active_usage_days"],
    errors="ignore")
subscriptions = subscriptions.merge(
    usage_summary,
    on="subscription_id",
    how="left"
)
print("\n---MERGE CHECK ---")
print(subscriptions[["subscription_id", "total_usage", "average_usage","active_usage_days"]].head())

# Replaces lines 520-530 
cols = ["total_usage", "average_usage", "active_usage_days"]
for col in cols:
    if col in subscriptions.columns:
        subscriptions[col] = subscriptions[col].fillna(0)
    else:
        subscriptions[col] = 0

print("\n--- USAGE BY CHURN STATUS ---")

usage_churn = (
    subscriptions
    .groupby("churn_status")
    .agg(
        customers=("subscription_id", "count"),
        avg_total_usage=("total_usage", "mean"),
        avg_usage=("average_usage", "mean"),
        avg_active_usage_days=("active_usage_days", "mean")
    )
)

print(usage_churn.round(2))


# ============================================================
# 10. STATISTICAL & BUSINESS ANALYSIS
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

print("\n" + "=" * 60)
print("STATISTICAL & BUSINESS ANALYSIS")
print("=" * 60)


# ------------------------------------------------------------
# 10.1 CORRELATION ANALYSIS
# ------------------------------------------------------------

print("\n--- CORRELATION WITH CHURN ---")

numeric_columns = [
    "churn_flag",
    "tenure_days",
    "tenure_months",
    "mrr_amount",
    "arr_amount",
    "seats",
    "mrr_per_seat",
    "arr_per_seat",
    "arr_mrr_ratio",
    "ticket_count",
    "escalations",
    "total_usage",
    "average_usage",
    "active_usage_days"
]

available_numeric_columns = [
    col for col in numeric_columns
    if col in subscriptions.columns
]

correlation_data = subscriptions[
    available_numeric_columns
].copy()

for column in correlation_data.columns:
    correlation_data[column] = pd.to_numeric(
        correlation_data[column],
        errors="coerce"
    )

correlation_matrix = correlation_data.corr()

churn_correlations = (
    correlation_matrix["churn_flag"]
    .sort_values(ascending=False)
    .round(3)
)

print(churn_correlations)


# ------------------------------------------------------------
# 10.2 DESCRIPTIVE STATISTICS
# ------------------------------------------------------------

print("\n--- DESCRIPTIVE STATISTICS ---")

descriptive_statistics = (
    subscriptions[available_numeric_columns]
    .describe()
    .T
    .round(2)
)

print(descriptive_statistics)


# ------------------------------------------------------------
# 10.3 CHURNED VS RETAINED COMPARISON
# ------------------------------------------------------------

print("\n--- CHURNED VS RETAINED ---")

comparison = (
    subscriptions
    .groupby("churn_status")
    .agg(
        customers=("subscription_id", "count"),
        avg_tenure_months=("tenure_months", "mean"),
        avg_mrr=("mrr_amount", "mean"),
        avg_arr=("arr_amount", "mean"),
        avg_seats=("seats", "mean"),
        avg_total_usage=("total_usage", "mean"),
        avg_usage=("average_usage", "mean"),
        avg_active_usage_days=("active_usage_days", "mean"),
        avg_tickets=("ticket_count", "mean"),
        avg_escalations=("escalations", "mean")
    )
    .round(2)
)

print(comparison)


# ------------------------------------------------------------
# 10.4 CHURN BY BILLING FREQUENCY
# ------------------------------------------------------------

print("\n--- CHURN BY BILLING FREQUENCY ---")

billing_churn = (
    subscriptions
    .groupby("billing_frequency")
    .agg(
        customers=("subscription_id", "count"),
        churned=("churn_flag", "sum")
    )
)

billing_churn["churn_rate"] = (
    billing_churn["churned"] /
    billing_churn["customers"] * 100
)

print(billing_churn.round(2))


# ------------------------------------------------------------
# 10.5 CHURN BY AUTO-RENEWAL
# ------------------------------------------------------------

print("\n--- CHURN BY AUTO-RENEWAL ---")

renewal_churn = (
    subscriptions
    .groupby("auto_renew_flag")
    .agg(
        customers=("subscription_id", "count"),
        churned=("churn_flag", "sum")
    )
)

renewal_churn["churn_rate"] = (
    renewal_churn["churned"] /
    renewal_churn["customers"] * 100
)

print(renewal_churn.round(2))


# ------------------------------------------------------------
# 10.6 CHURN BY UPGRADE / DOWNGRADE
# ------------------------------------------------------------

print("\n--- UPGRADE VS CHURN ---")

upgrade_churn = (
    subscriptions
    .groupby("upgrade_flag")
    .agg(
        customers=("subscription_id", "count"),
        churned=("churn_flag", "sum")
    )
)

upgrade_churn["churn_rate"] = (
    upgrade_churn["churned"] /
    upgrade_churn["customers"] * 100
)

print(upgrade_churn.round(2))


print("\n--- DOWNGRADE VS CHURN ---")

downgrade_churn = (
    subscriptions
    .groupby("downgrade_flag")
    .agg(
        customers=("subscription_id", "count"),
        churned=("churn_flag", "sum")
    )
)

downgrade_churn["churn_rate"] = (
    downgrade_churn["churned"] /
    downgrade_churn["customers"] * 100
)

print(downgrade_churn.round(2))


# ------------------------------------------------------------
# 10.7 STATISTICAL TEST: TENURE
# ------------------------------------------------------------

print("\n--- HYPOTHESIS TEST: TENURE ---")

churned_tenure = subscriptions.loc[
    subscriptions["churn_flag"] == True,
    "tenure_months"
].dropna()

retained_tenure = subscriptions.loc[
    subscriptions["churn_flag"] == False,
    "tenure_months"
].dropna()

tenure_test = stats.ttest_ind(
    churned_tenure,
    retained_tenure,
    equal_var=False
)

print(f"T-statistic: {tenure_test.statistic:.4f}")
print(f"P-value: {tenure_test.pvalue:.6f}")

if tenure_test.pvalue < 0.05:
    print("Result: statistically significant difference in tenure.")
else:
    print("Result: no statistically significant difference in tenure.")


# ------------------------------------------------------------
# 10.8 STATISTICAL TEST: MRR
# ------------------------------------------------------------

print("\n--- HYPOTHESIS TEST: MRR ---")

churned_mrr = subscriptions.loc[
    subscriptions["churn_flag"] == True,
    "mrr_amount"
].dropna()

retained_mrr = subscriptions.loc[
    subscriptions["churn_flag"] == False,
    "mrr_amount"
].dropna()

mrr_test = stats.ttest_ind(
    churned_mrr,
    retained_mrr,
    equal_var=False
)

print(f"T-statistic: {mrr_test.statistic:.4f}")
print(f"P-value: {mrr_test.pvalue:.6f}")

if mrr_test.pvalue < 0.05:
    print("Result: statistically significant difference in MRR.")
else:
    print("Result: no statistically significant difference in MRR.")


# ------------------------------------------------------------
# 10.9 STATISTICAL TEST: USAGE
# ------------------------------------------------------------

print("\n--- HYPOTHESIS TEST: TOTAL USAGE ---")

churned_usage = subscriptions.loc[
    subscriptions["churn_flag"] == True,
    "total_usage"
].dropna()

retained_usage = subscriptions.loc[
    subscriptions["churn_flag"] == False,
    "total_usage"
].dropna()

usage_test = stats.ttest_ind(
    churned_usage,
    retained_usage,
    equal_var=False
)

print(f"T-statistic: {usage_test.statistic:.4f}")
print(f"P-value: {usage_test.pvalue:.6f}")

if usage_test.pvalue < 0.05:
    print("Result: statistically significant difference in usage.")
else:
    print("Result: no statistically significant difference in usage.")


# ------------------------------------------------------------
# 10.10 CONFIDENCE INTERVAL FOR CHURN RATE
# ------------------------------------------------------------

print("\n--- 95% CONFIDENCE INTERVAL FOR CHURN RATE ---")

n = len(subscriptions)
churned = subscriptions["churn_flag"].sum()
p = churned / n

standard_error = np.sqrt(
    (p * (1 - p)) / n
)

margin_of_error = (
    stats.norm.ppf(0.975) * standard_error
)

lower_ci = p - margin_of_error
upper_ci = p + margin_of_error

print(f"Churn rate: {p * 100:.2f}%")
print(
    f"95% confidence interval: "
    f"{lower_ci * 100:.2f}% - {upper_ci * 100:.2f}%"
)


# ------------------------------------------------------------
# 10.11 PEARSON CORRELATION
# ------------------------------------------------------------

print("\n--- PEARSON CORRELATIONS ---")

pearson_variables = [
    "tenure_months",
    "mrr_amount",
    "total_usage",
    "ticket_count",
    "active_usage_days"
]

for variable in pearson_variables:

    if variable in subscriptions.columns:

        clean_data = subscriptions[
            ["churn_flag", variable]
        ].dropna()

        correlation, p_value = stats.pearsonr(
            clean_data["churn_flag"],
            clean_data[variable]
        )

        print(
            f"{variable}: "
            f"r={correlation:.3f}, "
            f"p={p_value:.6f}"
        )


# ------------------------------------------------------------
# 10.12 SPEARMAN CORRELATION
# ------------------------------------------------------------

print("\n--- SPEARMAN CORRELATIONS ---")

for variable in pearson_variables:

    if variable in subscriptions.columns:

        clean_data = subscriptions[
            ["churn_flag", variable]
        ].dropna()

        correlation, p_value = stats.spearmanr(
            clean_data["churn_flag"],
            clean_data[variable]
        )

        print(
            f"{variable}: "
            f"rho={correlation:.3f}, "
            f"p={p_value:.6f}"
        )


# ------------------------------------------------------------
# 10.13 SIMPLE REGRESSION
# ------------------------------------------------------------

print("\n--- REGRESSION ANALYSIS ---")

regression_variables = [
    "tenure_months",
    "mrr_amount",
    "total_usage",
    "ticket_count",
    "active_usage_days"
]

for variable in regression_variables:

    if variable in subscriptions.columns:

        regression_data = subscriptions[
            ["churn_flag", variable]
        ].dropna()

        if len(regression_data) > 2:

            x = regression_data[variable].values
            y = regression_data["churn_flag"].astype(float).values

            slope, intercept = np.polyfit(x, y, 1)

            predictions = (
                slope * x + intercept
            )

            ss_res = np.sum(
                (y - predictions) ** 2
            )

            ss_tot = np.sum(
                (y - np.mean(y)) ** 2
            )

            r_squared = (
                1 - (ss_res / ss_tot)
                if ss_tot != 0
                else np.nan
            )

            print(
                f"{variable}: "
                f"slope={slope:.6f}, "
                f"R²={r_squared:.4f}"
            )


# ------------------------------------------------------------
# 10.14 BUSINESS KPI SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("KEY BUSINESS KPIs")
print("=" * 60)

total_mrr = subscriptions["mrr_amount"].sum()
total_arr = subscriptions["arr_amount"].sum()

avg_mrr = subscriptions["mrr_amount"].mean()
avg_tenure = subscriptions["tenure_months"].mean()

print(f"Total customers/subscriptions: {len(subscriptions):,}")
print(f"Churned customers: {churned:,}")
print(f"Retained customers: {n - churned:,}")
print(f"Churn rate: {p * 100:.2f}%")
print(f"Total MRR: {total_mrr:,.2f}")
print(f"Total ARR: {total_arr:,.2f}")
print(f"Average MRR: {avg_mrr:,.2f}")
print(f"Average tenure: {avg_tenure:.2f} months")


# ============================================================
# 11. VISUAL ANALYSIS
# ============================================================


# ------------------------------------------------------------
# 11.1 CHURN RATE BY PLAN
# ------------------------------------------------------------

plan_churn["churn_rate"].sort_values().plot(
    kind="barh",
    figsize=(8, 5)
)

plt.title("Churn Rate by Plan Tier")
plt.xlabel("Churn Rate (%)")
plt.ylabel("Plan Tier")
plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 11.2 CHURN RATE BY TENURE
# ------------------------------------------------------------

tenure_churn["churn_rate"].plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Churn Rate by Customer Tenure")
plt.xlabel("Tenure Group")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 11.3 CHURNED VS RETAINED
# ------------------------------------------------------------

subscriptions["churn_status"].value_counts().plot(
    kind="bar",
    figsize=(7, 5)
)

plt.title("Churned vs Retained Customers")
plt.xlabel("Customer Status")
plt.ylabel("Number of Customers")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("chart.png")
plt.close()


# ------------------------------------------------------------
# 11.4 MRR BY CHURN STATUS
# ------------------------------------------------------------

subscriptions.boxplot(
    column="mrr_amount",
    by="churn_status",
    figsize=(8, 5)
)

plt.title("MRR Distribution: Churned vs Retained")
plt.suptitle("")
plt.xlabel("Customer Status")
plt.ylabel("MRR")
plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 11.5 TENURE BY CHURN STATUS
# ------------------------------------------------------------

subscriptions.boxplot(
    column="tenure_months",
    by="churn_status",
    figsize=(8, 5)
)

plt.title("Tenure Distribution: Churned vs Retained")
plt.suptitle("")
plt.xlabel("Customer Status")
plt.ylabel("Tenure (Months)")
plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 11.6 USAGE BY CHURN STATUS
# ------------------------------------------------------------

subscriptions.boxplot(
    column="total_usage",
    by="churn_status",
    figsize=(8, 5)
)

plt.title("Usage Distribution: Churned vs Retained")
plt.suptitle("")
plt.xlabel("Customer Status")
plt.ylabel("Total Usage")
plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 11.7 SUPPORT TICKETS BY CHURN STATUS
# ------------------------------------------------------------

subscriptions.boxplot(
    column="ticket_count",
    by="churn_status",
    figsize=(8, 5)
)

plt.title("Support Tickets: Churned vs Retained")
plt.suptitle("")
plt.xlabel("Customer Status")
plt.ylabel("Number of Tickets")
plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 11.8 CHURN BY BILLING FREQUENCY
# ------------------------------------------------------------

billing_churn["churn_rate"].plot(
    kind="bar",
    figsize=(8, 5)
)

plt.title("Churn Rate by Billing Frequency")
plt.xlabel("Billing Frequency")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 11.9 CHURN BY AUTO-RENEWAL
# ------------------------------------------------------------

renewal_churn["churn_rate"].plot(
    kind="bar",
    figsize=(8, 5)
)

plt.title("Churn Rate by Auto-Renewal")
plt.xlabel("Auto-Renewal")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


# ============================================================
# 12. EXPORT ANALYTICAL DATASET
# ============================================================

print("\n--- EXPORTING ANALYTICAL DATASET ---")

subscriptions.to_csv(
    "saas_churn_analytical_dataset.csv",
    index=False
)

print(
    "Analytical dataset exported successfully:"
    " saas_churn_analytical_dataset.csv"
)


# ============================================================
# 13. FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("PYTHON ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 60)

print("\nThe analytical dataset is ready for:")
print("1. SQL analysis")
print("2. Power BI dashboard")
print("3. Final business recommendations")
print("4. GitHub documentation")

# ============================================================
# SAAS CHURN ANALYTICS — ROI / FINANCIAL IMPACT ANALYSIS
# ============================================================

import pandas as pd
import numpy as np

# ------------------------------------------------------------
# 1. BASIC VALIDATION
# ------------------------------------------------------------

required_columns = [
    "account_id",
    "subscription_id",
    "mrr_amount",
    "arr_amount",
    "churn_flag",
    "plan_tier",
    "seats",
    "is_active",
    "tenure_months"
]

missing_columns = [
    col for col in required_columns
    if col not in subscriptions.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("ROI analysis dataset validated successfully.")
print(f"Rows available: {len(subscriptions):,}")


# ------------------------------------------------------------
# 2. OVERALL REVENUE AND CHURN POSITION
# ------------------------------------------------------------

total_arr = subscriptions["arr_amount"].sum()

churned = subscriptions[
    subscriptions["churn_flag"] == 1
].copy()

churned_arr = churned["arr_amount"].sum()
churned_mrr = churned["mrr_amount"].sum()

total_customers = subscriptions["account_id"].nunique()
churned_customers = churned["account_id"].nunique()

churn_rate = (
    churned_customers / total_customers
    if total_customers > 0 else 0
)

arr_at_risk_pct = (
    churned_arr / total_arr
    if total_arr > 0 else 0
)

print("\n========== CURRENT FINANCIAL POSITION ==========")

print(f"Total customers: {total_customers:,}")
print(f"Churned customers: {churned_customers:,}")
print(f"Customer churn rate: {churn_rate:.2%}")

print(f"Total ARR: ${total_arr:,.2f}")
print(f"Churned ARR: ${churned_arr:,.2f}")
print(f"Churned MRR: ${churned_mrr:,.2f}")
print(f"ARR at risk: {arr_at_risk_pct:.2%}")


# ------------------------------------------------------------
# 3. POTENTIAL REVENUE RECOVERY SCENARIOS
# ------------------------------------------------------------

reduction_scenarios = [0.10, 0.20, 0.30, 0.40, 0.50]

scenario_results = []

for reduction in reduction_scenarios:

    recovered_arr = churned_arr * reduction

    scenario_results.append({
        "churn_reduction": reduction,
        "recovered_arr": recovered_arr,
        "recovered_mrr": recovered_arr / 12
    })

roi_scenarios = pd.DataFrame(scenario_results)

print("\n========== REVENUE RECOVERY SCENARIOS ==========")

print(
    roi_scenarios.to_string(
        index=False,
        formatters={
            "churn_reduction": "{:.0%}".format,
            "recovered_arr": "${:,.2f}".format,
            "recovered_mrr": "${:,.2f}".format
        }
    )
)


# ------------------------------------------------------------
# 4. RETENTION PROGRAM COST ASSUMPTION
# ------------------------------------------------------------
#
# IMPORTANT:
# The dataset does not contain the actual cost of a retention
# program. Therefore, we explicitly define an assumption.
#
# You can change this number later.
#
# Example:
# $50 per customer successfully retained.
#

retention_cost_per_customer = 50


# ------------------------------------------------------------
# 5. ROI CALCULATION
# ------------------------------------------------------------

roi_results = []

for reduction in reduction_scenarios:

    customers_saved = round(
        churned_customers * reduction
    )

    recovered_arr = churned_arr * reduction

    retention_cost = (
        customers_saved *
        retention_cost_per_customer
    )

    net_benefit = (
        recovered_arr -
        retention_cost
    )

    roi = (
        net_benefit / retention_cost
        if retention_cost > 0
        else np.nan
    )

    roi_results.append({
        "churn_reduction": reduction,
        "customers_saved": customers_saved,
        "recovered_arr": recovered_arr,
        "retention_cost": retention_cost,
        "net_benefit": net_benefit,
        "roi": roi
    })

roi_analysis = pd.DataFrame(roi_results)

print("\n========== ROI SCENARIOS ==========")

print(
    roi_analysis.to_string(
        index=False,
        formatters={
            "churn_reduction": "{:.0%}".format,
            "recovered_arr": "${:,.2f}".format,
            "retention_cost": "${:,.2f}".format,
            "net_benefit": "${:,.2f}".format,
            "roi": "{:.2f}x".format
        }
    )
)


# ------------------------------------------------------------
# 6. BREAK-EVEN RETENTION RATE
# ------------------------------------------------------------

# Number of churned customers required to recover enough ARR
# to cover the retention cost.

average_churned_arr_per_customer = (
    churned_arr / churned_customers
    if churned_customers > 0 else 0
)

break_even_customers = (
    retention_cost_per_customer /
    average_churned_arr_per_customer
    if average_churned_arr_per_customer > 0
    else np.nan
)

break_even_rate = (
    break_even_customers / churned_customers
    if churned_customers > 0 else np.nan
)

print("\n========== BREAK-EVEN ANALYSIS ==========")

print(
    f"Average ARR per churned customer: "
    f"${average_churned_arr_per_customer:,.2f}"
)

print(
    f"Customers that must be retained to break even: "
    f"{break_even_customers:.2f}"
)

print(
    f"Approximate break-even retention rate: "
    f"{break_even_rate:.2%}"
)


# ------------------------------------------------------------
# 7. ROI BY PLAN TIER
# ------------------------------------------------------------

plan_roi = (
    churned
    .groupby("plan_tier")
    .agg(
        churned_customers=("account_id", "nunique"),
        churned_arr=("arr_amount", "sum"),
        churned_mrr=("mrr_amount", "sum")
    )
    .reset_index()
)

plan_roi["arr_per_churned_customer"] = (
    plan_roi["churned_arr"] /
    plan_roi["churned_customers"]
)

# Assume a 20% reduction in churn for this scenario
plan_roi["potential_recovered_arr_20pct"] = (
    plan_roi["churned_arr"] * 0.20
)

plan_roi["retention_cost_20pct"] = (
    np.round(
        plan_roi["churned_customers"] * 0.20
    )
    * retention_cost_per_customer
)

plan_roi["net_benefit_20pct"] = (
    plan_roi["potential_recovered_arr_20pct"]
    - plan_roi["retention_cost_20pct"]
)

plan_roi["roi_20pct"] = (
    plan_roi["net_benefit_20pct"] /
    plan_roi["retention_cost_20pct"]
)

print("\n========== ROI BY PLAN TIER ==========")

print(
    plan_roi.to_string(
        index=False,
        formatters={
            "churned_arr": "${:,.2f}".format,
            "churned_mrr": "${:,.2f}".format,
            "arr_per_churned_customer": "${:,.2f}".format,
            "potential_recovered_arr_20pct": "${:,.2f}".format,
            "retention_cost_20pct": "${:,.2f}".format,
            "net_benefit_20pct": "${:,.2f}".format,
            "roi_20pct": "{:.2f}x".format
        }
    )
)


# ------------------------------------------------------------
# 8. HIGH-VALUE CHURNED CUSTOMERS
# ------------------------------------------------------------

high_value_churn = (
    churned[
        [
            "account_id",
            "subscription_id",
            "plan_tier",
            "seats",
            "mrr_amount",
            "arr_amount",
            "tenure_months"
        ]
    ]
    .sort_values(
        "arr_amount",
        ascending=False
    )
    .head(20)
)

print("\n========== TOP 20 CHURNED CUSTOMERS BY ARR ==========")

print(
    high_value_churn.to_string(
        index=False,
        formatters={
            "mrr_amount": "${:,.2f}".format,
            "arr_amount": "${:,.2f}".format
        }
    )
)


# ------------------------------------------------------------
# 9. FINANCIAL IMPACT SUMMARY
# ------------------------------------------------------------

financial_summary = pd.DataFrame({
    "metric": [
        "Total ARR",
        "Churned ARR",
        "Churned MRR",
        "ARR at Risk",
        "Customer Churn Rate",
        "Average ARR per Churned Customer",
        "Retention Cost per Customer",
        "Break-Even Retention Rate"
    ],

    "value": [
        total_arr,
        churned_arr,
        churned_mrr,
        churned_arr,
        churn_rate,
        average_churned_arr_per_customer,
        retention_cost_per_customer,
        break_even_rate
    ]
})

print("\n========== FINANCIAL IMPACT SUMMARY ==========")

print(financial_summary.to_string(index=False))


# ------------------------------------------------------------
# 10. EXPORT ROI RESULTS
# ------------------------------------------------------------

roi_analysis.to_csv(
    "saas_roi_scenarios.csv",
    index=False
)

plan_roi.to_csv(
    "saas_plan_roi_analysis.csv",
    index=False
)

high_value_churn.to_csv(
    "saas_high_value_churn.csv",
    index=False
)

financial_summary.to_csv(
    "saas_financial_impact_summary.csv",
    index=False
)

print("\nROI analysis completed successfully.")
print("ROI result files exported successfully.")

# ============================================================
# EXPORT PYTHON ANALYSIS RESULTS FOR POWER BI
# ============================================================

print("\n" + "=" * 60)
print("EXPORTING PYTHON ANALYSIS RESULTS")
print("=" * 60)

# 1. Overall churn and revenue analysis
revenue_summary.to_csv(
    "python_revenue_summary.csv",
    index=True
)

# 2. Churn by plan
plan_churn.to_csv(
    "python_churn_by_plan.csv",
    index=True
)

# 3. Churn by tenure
tenure_churn.to_csv(
    "python_churn_by_tenure.csv",
    index=True
)

# 4. Churn by trial status
trial_churn.to_csv(
    "python_churn_by_trial.csv",
    index=True
)

# 5. Upgrade vs churn
upgrade_churn.to_csv(
    "python_upgrade_vs_churn.csv",
    index=True
)

# 6. Downgrade vs churn
downgrade_churn.to_csv(
    "python_downgrade_vs_churn.csv",
    index=True
)

# 7. Billing frequency vs churn
billing_churn.to_csv(
    "python_billing_vs_churn.csv",
    index=True
)

# 8. Auto-renewal vs churn
renewal_churn.to_csv(
    "python_autorenewal_vs_churn.csv",
    index=True
)

# 9. Usage vs churn
usage_churn.to_csv(
    "python_usage_vs_churn.csv",
    index=True
)

# 10. Churned vs retained comparison
comparison.to_csv(
    "python_churned_vs_retained.csv",
    index=True
)

# 11. Correlation with churn
churn_correlations.to_frame(
    name="correlation"
).to_csv(
    "python_churn_correlations.csv"
)

# 12. Descriptive statistics
descriptive_statistics.to_csv(
    "python_descriptive_statistics.csv"
)

# 13. ROI scenarios
roi_analysis.to_csv(
    "saas_roi_scenarios.csv",
    index=False
)

# 14. ROI by plan tier
plan_roi.to_csv(
    "saas_plan_roi_analysis.csv",
    index=False
)

# 15. High-value churned customers
high_value_churn.to_csv(
    "saas_high_value_churn.csv",
    index=False
)

# 16. Financial impact summary
financial_summary.to_csv(
    "saas_financial_impact_summary.csv",
    index=False
)

print("\nALL PYTHON RESULTS EXPORTED SUCCESSFULLY.")
print("The CSV files are ready for Power BI.")