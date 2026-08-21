USE SaaS_Churn_Analytics;
GO


/* ============================================================
   SAAS CHURN ANALYTICS
   SQL CLEANING - STAGE 1
   ============================================================
   
   RAW TABLES ARE NOT MODIFIED.

   Raw tables:
   raventstack_accounts
   raventstack_churn_events
   raventstack_feature_usage
   raventstack_subscriptions
   raventstack_support_tickets

   Clean tables created:
   clean_accounts
   clean_churn_events
   clean_feature_usage
   clean_subscriptions
   clean_support_tickets
   ============================================================ */


/* ============================================================
   1. CLEAN ACCOUNTS
   ============================================================ */

IF OBJECT_ID('dbo.clean_accounts', 'U') IS NOT NULL
    DROP TABLE dbo.clean_accounts;
GO

SELECT
    account_id,
    account_name,
    industry,
    country,

    TRY_CONVERT(date, signup_date) AS signup_date,

    referral_source,
    plan_tier,

    CASE
        WHEN TRY_CONVERT(int, seats) >= 0
        THEN TRY_CONVERT(int, seats)
        ELSE NULL
    END AS seats,

    CASE
        WHEN TRY_CONVERT(int, is_trial) IN (0,1)
        THEN TRY_CONVERT(int, is_trial)
        ELSE NULL
    END AS is_trial,

    CASE
        WHEN TRY_CONVERT(int, churn_flag) IN (0,1)
        THEN TRY_CONVERT(int, churn_flag)
        ELSE NULL
    END AS churn_flag

INTO dbo.clean_accounts

FROM dbo.ravenstack_accounts;
GO


/* ============================================================
   2. CLEAN CHURN EVENTS
   ============================================================ */

IF OBJECT_ID('dbo.clean_churn_events', 'U') IS NOT NULL
    DROP TABLE dbo.clean_churn_events;
GO

SELECT
    churn_event_id,
    account_id,

    TRY_CONVERT(date, churn_date) AS churn_date,

    reason_code,

    CASE
        WHEN TRY_CONVERT(decimal(18,2), refund_amount_usd) >= 0
        THEN TRY_CONVERT(decimal(18,2), refund_amount_usd)
        ELSE NULL
    END AS refund_amount_usd,

    CASE
        WHEN TRY_CONVERT(int, preceding_upgrade_flag) IN (0,1)
        THEN TRY_CONVERT(int, preceding_upgrade_flag)
        ELSE NULL
    END AS preceding_upgrade_flag,

    CASE
        WHEN TRY_CONVERT(int, preceding_downgrade_flag) IN (0,1)
        THEN TRY_CONVERT(int, preceding_downgrade_flag)
        ELSE NULL
    END AS preceding_downgrade_flag,

    CASE
        WHEN TRY_CONVERT(int, is_reactivation) IN (0,1)
        THEN TRY_CONVERT(int, is_reactivation)
        ELSE NULL
    END AS is_reactivation,

    feedback_text

INTO dbo.clean_churn_events

FROM dbo.ravenstack_churn_events;
GO


/* ============================================================
   3. CLEAN FEATURE USAGE
   ============================================================ */

IF OBJECT_ID('dbo.clean_feature_usage', 'U') IS NOT NULL
    DROP TABLE dbo.clean_feature_usage;
GO

SELECT
    usage_id,
    subscription_id,

    TRY_CONVERT(date, usage_date) AS usage_date,

    feature_name,

    CASE
        WHEN TRY_CONVERT(int, usage_count) >= 0
        THEN TRY_CONVERT(int, usage_count)
        ELSE NULL
    END AS usage_count,

    CASE
        WHEN TRY_CONVERT(decimal(18,2), usage_duration_secs) >= 0
        THEN TRY_CONVERT(decimal(18,2), usage_duration_secs)
        ELSE NULL
    END AS usage_duration_secs,

    CASE
        WHEN TRY_CONVERT(int, error_count) >= 0
        THEN TRY_CONVERT(int, error_count)
        ELSE NULL
    END AS error_count,

    CASE
        WHEN TRY_CONVERT(int, is_beta_feature) IN (0,1)
        THEN TRY_CONVERT(int, is_beta_feature)
        ELSE NULL
    END AS is_beta_feature

INTO dbo.clean_feature_usage

FROM dbo.ravenstack_feature_usage;
GO


/* ============================================================
   4. CLEAN SUBSCRIPTIONS
   ============================================================ */

IF OBJECT_ID('dbo.clean_subscriptions', 'U') IS NOT NULL
    DROP TABLE dbo.clean_subscriptions;
GO

SELECT
    subscription_id,
    account_id,

    TRY_CONVERT(date, start_date) AS start_date,

    TRY_CONVERT(date, end_date) AS end_date,

    plan_tier,

    CASE
        WHEN TRY_CONVERT(int, seats) >= 0
        THEN TRY_CONVERT(int, seats)
        ELSE NULL
    END AS seats,

    CASE
        WHEN TRY_CONVERT(decimal(18,2), CAST(mrr_amount AS varchar(MAX))) >= 0
        THEN TRY_CONVERT(decimal(18,2),CAST( mrr_amount AS  varchar(MAX)))
        ELSE NULL
    END AS mrr_amount,

    CASE
        WHEN TRY_CONVERT(decimal(18,2), CAST(arr_amount AS varchar(MAX))) >= 0
        THEN TRY_CONVERT(decimal(18,2), CAST(arr_amount AS varchar(MAX)))
        ELSE NULL
    END AS arr_amount,

    CASE
        WHEN TRY_CONVERT(int, is_trial) IN (0,1)
        THEN TRY_CONVERT(int, is_trial)
        ELSE NULL
    END AS is_trial,

    CASE
        WHEN TRY_CONVERT(int, upgrade_flag) IN (0,1)
        THEN TRY_CONVERT(int, upgrade_flag)
        ELSE NULL
    END AS upgrade_flag,

    CASE
        WHEN TRY_CONVERT(int, downgrade_flag) IN (0,1)
        THEN TRY_CONVERT(int, downgrade_flag)
        ELSE NULL
    END AS downgrade_flag,

    CASE
        WHEN TRY_CONVERT(int, churn_flag) IN (0,1)
        THEN TRY_CONVERT(int, churn_flag)
        ELSE NULL
    END AS churn_flag,

    billing_frequency,

    CASE
        WHEN TRY_CONVERT(int, auto_renew_flag) IN (0,1)
        THEN TRY_CONVERT(int, auto_renew_flag)
        ELSE NULL
    END AS auto_renew_flag

INTO dbo.clean_subscriptions

FROM dbo.ravenstack_subscriptions;
GO


/* ============================================================
   5. CLEAN SUPPORT TICKETS
   ============================================================ */

IF OBJECT_ID('dbo.clean_support_tickets', 'U') IS NOT NULL
    DROP TABLE dbo.clean_support_tickets;
GO

SELECT
    ticket_id,
    account_id,

    TRY_CONVERT(datetime, submitted_at) AS submitted_at,

    TRY_CONVERT(datetime, closed_at) AS closed_at,

    CASE
        WHEN TRY_CONVERT(decimal(18,2), resolution_time_hours) >= 0
        THEN TRY_CONVERT(decimal(18,2), resolution_time_hours)
        ELSE NULL
    END AS resolution_time_hours,

    priority,

    CASE
        WHEN TRY_CONVERT(decimal(18,2), first_response_time_minutes) >= 0
        THEN TRY_CONVERT(decimal(18,2), first_response_time_minutes)
        ELSE NULL
    END AS first_response_time_minutes,

    CASE
        WHEN TRY_CONVERT(int, satisfaction_score) BETWEEN 0 AND 5
        THEN TRY_CONVERT(int, satisfaction_score)
        ELSE NULL
    END AS satisfaction_score,

    CASE
        WHEN TRY_CONVERT(int, escalation_flag) IN (0,1)
        THEN TRY_CONVERT(int, escalation_flag)
        ELSE NULL
    END AS escalation_flag

INTO dbo.clean_support_tickets

FROM dbo.ravenstack_support_tickets;
GO


/* ============================================================
   FINAL CHECK
   ============================================================ */

SELECT 'clean_accounts' AS table_name,
       COUNT(*) AS row_count
FROM dbo.clean_accounts

UNION ALL

SELECT 'clean_churn_events',
       COUNT(*)
FROM dbo.clean_churn_events

UNION ALL

SELECT 'clean_feature_usage',
       COUNT(*)
FROM dbo.clean_feature_usage

UNION ALL

SELECT 'clean_subscriptions',
       COUNT(*)
FROM dbo.clean_subscriptions

UNION ALL

SELECT 'clean_support_tickets',
       COUNT(*)
FROM dbo.clean_support_tickets;
GO


PRINT '=============================================';
PRINT 'STAGE 1 CLEANING COMPLETE';
PRINT '=============================================';
GO
USE SaaS_Churn_Analytics;
GO

/* ============================================================
   STAGE 2 — CLEAN DATA VALIDATION
   ============================================================ */


/* 1. ROW COUNTS */

SELECT 'clean_accounts' AS table_name, COUNT(*) AS row_count
FROM dbo.clean_accounts

UNION ALL

SELECT 'clean_churn_events', COUNT(*)
FROM dbo.clean_churn_events

UNION ALL

SELECT 'clean_feature_usage', COUNT(*)
FROM dbo.clean_feature_usage

UNION ALL

SELECT 'clean_subscriptions', COUNT(*)
FROM dbo.clean_subscriptions

UNION ALL

SELECT 'clean_support_tickets', COUNT(*)
FROM dbo.clean_support_tickets;


/* ============================================================
   2. DUPLICATE ID CHECKS
   ============================================================ */

SELECT account_id, COUNT(*) AS duplicate_count
FROM dbo.clean_accounts
GROUP BY account_id
HAVING COUNT(*) > 1;


SELECT subscription_id, COUNT(*) AS duplicate_count
FROM dbo.clean_subscriptions
GROUP BY subscription_id
HAVING COUNT(*) > 1;


SELECT churn_event_id, COUNT(*) AS duplicate_count
FROM dbo.clean_churn_events
GROUP BY churn_event_id
HAVING COUNT(*) > 1;


SELECT usage_id, COUNT(*) AS duplicate_count
FROM dbo.clean_feature_usage
GROUP BY usage_id
HAVING COUNT(*) > 1;


SELECT ticket_id, COUNT(*) AS duplicate_count
FROM dbo.clean_support_tickets
GROUP BY ticket_id
HAVING COUNT(*) > 1;


/* ============================================================
   3. ORPHAN RECORD CHECKS
   ============================================================ */

/* Subscriptions without an account */
SELECT COUNT(*) AS orphan_subscriptions
FROM dbo.clean_subscriptions s
LEFT JOIN dbo.clean_accounts a
    ON s.account_id = a.account_id
WHERE a.account_id IS NULL;


/* Churn events without an account */
SELECT COUNT(*) AS orphan_churn_events
FROM dbo.clean_churn_events c
LEFT JOIN dbo.clean_accounts a
    ON c.account_id = a.account_id
WHERE a.account_id IS NULL;


/* Feature usage without a subscription */
SELECT COUNT(*) AS orphan_usage
FROM dbo.clean_feature_usage f
LEFT JOIN dbo.clean_subscriptions s
    ON f.subscription_id = s.subscription_id
WHERE s.subscription_id IS NULL;


/* Support tickets without an account */
SELECT COUNT(*) AS orphan_tickets
FROM dbo.clean_support_tickets t
LEFT JOIN dbo.clean_accounts a
    ON t.account_id = a.account_id
WHERE a.account_id IS NULL;


/* ============================================================
   4. INVALID VALUE CHECK
   ============================================================ */

SELECT COUNT(*) AS invalid_account_seats
FROM dbo.clean_accounts
WHERE seats < 0;


SELECT COUNT(*) AS invalid_subscription_seats
FROM dbo.clean_subscriptions
WHERE seats < 0;


SELECT COUNT(*) AS invalid_mrr
FROM dbo.clean_subscriptions
WHERE mrr_amount < 0;


SELECT COUNT(*) AS invalid_arr
FROM dbo.clean_subscriptions
WHERE arr_amount < 0;


SELECT COUNT(*) AS invalid_usage
FROM dbo.clean_feature_usage
WHERE usage_count < 0
   OR usage_duration_secs < 0
   OR error_count < 0;


SELECT COUNT(*) AS invalid_support_metrics
FROM dbo.clean_support_tickets
WHERE resolution_time_hours < 0
   OR first_response_time_minutes < 0;


/* ============================================================
   5. DATE LOGIC CHECK
   ============================================================ */

SELECT COUNT(*) AS invalid_subscription_dates
FROM dbo.clean_subscriptions
WHERE end_date IS NOT NULL
  AND end_date < start_date;


SELECT COUNT(*) AS invalid_ticket_dates
FROM dbo.clean_support_tickets
WHERE closed_at IS NOT NULL
  AND closed_at < submitted_at;


/* ============================================================
   VALIDATION COMPLETE
   ============================================================ */

PRINT '=============================================';
PRINT 'STAGE 2 VALIDATION COMPLETE';
PRINT '=============================================';
GO;

SELECT *
FROM dbo.ravenstack_feature_usage
WHERE usage_id IN 
    (SELECT usage_id
     FROM dbo.clean_feature_usage
     GROUP BY usage_id
     HAVING COUNT(*) > 1)
     ORDER BY usage_id;

     /* ============================================================
   FIX DUPLICATE USAGE IDs
   Keeps all 2,500 legitimate usage records
   ============================================================ */

-- Make sure the ID column has enough room for the new IDs
ALTER TABLE dbo.clean_feature_usage
ALTER COLUMN usage_id VARCHAR(30);

GO

-- Give repeated usage IDs a unique suffix
;WITH DuplicateIDs AS
(
    SELECT
        usage_id,
        subscription_id,
        usage_date,
        feature_name,
        ROW_NUMBER() OVER
        (
            PARTITION BY usage_id
            ORDER BY usage_date, subscription_id, feature_name
        ) AS rn
    FROM dbo.clean_feature_usage
)
UPDATE c
SET c.usage_id =
    c.usage_id + '_D' + CAST(d.rn AS VARCHAR(10))
FROM dbo.clean_feature_usage c
INNER JOIN DuplicateIDs d
    ON c.usage_id = d.usage_id
    AND c.subscription_id = d.subscription_id
    AND c.usage_date = d.usage_date
    AND c.feature_name = d.feature_name
WHERE d.rn > 1;

GO

/* ============================================================
   VERIFY THE FIX
   ============================================================ */

SELECT
    usage_id,
    COUNT(*) AS duplicate_count
FROM dbo.clean_feature_usage
GROUP BY usage_id
HAVING COUNT(*) > 1;

GO

/* Confirm row count */
SELECT COUNT(*) AS total_rows
FROM dbo.clean_feature_usage;

GO;
/* ============================================================
   STAGE 3 — SAAS BUSINESS ANALYSIS
   Database: SaaS_Churn_Analytics

   SQL = business metrics, segmentation and relationships
   Python later = ROI, statistics, forecasting, what-if analysis
   Power BI later = dashboard / visualization
   ============================================================ */


USE SaaS_Churn_Analytics;
GO


/* ============================================================
   1. OVERALL SAAS HEALTH
   ============================================================ */

SELECT
    COUNT(DISTINCT account_id) AS total_accounts,
    COUNT(*) AS total_subscriptions,

    SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        AS churned_subscriptions,

    CAST(
        100.0 * SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
        AS DECIMAL(10,2)
    ) AS churn_rate_pct,

    SUM(mrr_amount) AS total_mrr,
    SUM(arr_amount) AS total_arr

FROM dbo.clean_subscriptions;
GO


/* ============================================================
   2. CHURN BY PLAN TIER
   ============================================================ */

SELECT
    plan_tier,
    COUNT(*) AS subscriptions,

    SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        AS churned,

    CAST(
        100.0 * SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
        AS DECIMAL(10,2)
    ) AS churn_rate_pct,

    SUM(mrr_amount) AS total_mrr,

    SUM(
        CASE WHEN churn_flag = 1
        THEN mrr_amount ELSE 0 END
    ) AS churned_mrr

FROM dbo.clean_subscriptions
GROUP BY plan_tier
ORDER BY churn_rate_pct DESC;
GO


/* ============================================================
   3. REVENUE AT RISK FROM CHURN
   ============================================================ */

SELECT
    SUM(
        CASE WHEN churn_flag = 1
        THEN mrr_amount ELSE 0 END
    ) AS monthly_revenue_at_risk,

    SUM(
        CASE WHEN churn_flag = 1
        THEN arr_amount ELSE 0 END
    ) AS annual_revenue_at_risk,

    CAST(
        100.0 *
        SUM(
            CASE WHEN churn_flag = 1
            THEN arr_amount ELSE 0 END
        )
        / NULLIF(SUM(arr_amount), 0)
        AS DECIMAL(10,2)
    ) AS pct_arr_at_risk

FROM dbo.clean_subscriptions;
GO


/* ============================================================
   4. CHURN BY BILLING FREQUENCY
   ============================================================ */

SELECT
    billing_frequency,
    COUNT(*) AS subscriptions,

    SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        AS churned,

    CAST(
        100.0 * SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
        AS DECIMAL(10,2)
    ) AS churn_rate_pct,

    SUM(mrr_amount) AS total_mrr

FROM dbo.clean_subscriptions
GROUP BY billing_frequency
ORDER BY churn_rate_pct DESC;
GO


/* ============================================================
   5. TRIAL VS NON-TRIAL CHURN
   ============================================================ */

SELECT
    is_trial,

    COUNT(*) AS subscriptions,

    SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        AS churned,

    CAST(
        100.0 * SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
        AS DECIMAL(10,2)
    ) AS churn_rate_pct

FROM dbo.clean_subscriptions
GROUP BY is_trial
ORDER BY is_trial;
GO


/* ============================================================
   6. UPGRADE / DOWNGRADE BEHAVIOR
   ============================================================ */

SELECT
    SUM(CASE WHEN upgrade_flag = 1 THEN 1 ELSE 0 END)
        AS upgrades,

    SUM(CASE WHEN downgrade_flag = 1 THEN 1 ELSE 0 END)
        AS downgrades,

    SUM(
        CASE
            WHEN upgrade_flag = 1
             AND churn_flag = 1
            THEN 1 ELSE 0
        END
    ) AS upgrades_then_churned,

    SUM(
        CASE
            WHEN downgrade_flag = 1
             AND churn_flag = 1
            THEN 1 ELSE 0
        END
    ) AS downgrades_then_churned

FROM dbo.clean_subscriptions;
GO


/* ============================================================
   7. CHURN BY CUSTOMER SIZE
   ============================================================ */

SELECT
    CASE
        WHEN seats <= 5 THEN '1-5'
        WHEN seats <= 20 THEN '6-20'
        WHEN seats <= 50 THEN '21-50'
        ELSE '51+'
    END AS customer_size,

    COUNT(*) AS subscriptions,

    SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        AS churned,

    CAST(
        100.0 * SUM(CASE WHEN churn_flag = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
        AS DECIMAL(10,2)
    ) AS churn_rate_pct,

    SUM(arr_amount) AS total_arr,

    SUM(
        CASE WHEN churn_flag = 1
        THEN arr_amount ELSE 0 END
    ) AS arr_at_risk

FROM dbo.clean_subscriptions

GROUP BY
    CASE
        WHEN seats <= 5 THEN '1-5'
        WHEN seats <= 20 THEN '6-20'
        WHEN seats <= 50 THEN '21-50'
        ELSE '51+'
    END

ORDER BY churn_rate_pct DESC;
GO


/* ============================================================
   8. FEATURE USAGE VS CHURN
   ============================================================ */

SELECT
    s.churn_flag,

    COUNT(DISTINCT s.account_id) AS customers,

    COUNT(f.usage_id) AS usage_events,

    AVG(
        CAST(f.usage_count AS DECIMAL(18,2))
    ) AS avg_usage_count,

    AVG(
        CAST(f.usage_duration_secs AS DECIMAL(18,2))
    ) AS avg_usage_duration_seconds

FROM dbo.clean_subscriptions s

LEFT JOIN dbo.clean_feature_usage f
    ON s.subscription_id = f.subscription_id

GROUP BY s.churn_flag
ORDER BY s.churn_flag;
GO


/* ============================================================
   9. FEATURE POPULARITY
   ============================================================ */

SELECT
    feature_name,

    COUNT(*) AS usage_events,

    COUNT(DISTINCT subscription_id)
        AS subscriptions_using_feature,

    AVG(
        CAST(usage_count AS DECIMAL(18,2))
    ) AS avg_usage_count,

    AVG(
        CAST(usage_duration_secs AS DECIMAL(18,2))
    ) AS avg_usage_duration_seconds

FROM dbo.clean_feature_usage

GROUP BY feature_name

ORDER BY usage_events DESC;
GO


/* ============================================================
   10. FEATURE USAGE BY CHURN STATUS
   ============================================================ */

SELECT
    f.feature_name,
    s.churn_flag,

    COUNT(DISTINCT s.subscription_id)
        AS subscriptions,

    COUNT(*) AS usage_events,

    AVG(
        CAST(f.usage_count AS DECIMAL(18,2))
    ) AS avg_usage_count,

    AVG(
        CAST(f.usage_duration_secs AS DECIMAL(18,2))
    ) AS avg_usage_duration_seconds

FROM dbo.clean_feature_usage f

INNER JOIN dbo.clean_subscriptions s
    ON f.subscription_id = s.subscription_id

GROUP BY
    f.feature_name,
    s.churn_flag

ORDER BY
    f.feature_name,
    s.churn_flag;
GO


/* ============================================================
   11. SUPPORT EXPERIENCE VS CHURN
   ============================================================ */

SELECT
    s.churn_flag,

    COUNT(DISTINCT s.account_id)
        AS customers,

    COUNT(t.ticket_id)
        AS support_tickets,

    AVG(
        CAST(t.resolution_time_hours AS DECIMAL(18,2))
    ) AS avg_resolution_hours,

    AVG(
        CAST(t.first_response_time_minutes AS DECIMAL(18,2))
    ) AS avg_first_response_minutes,

    AVG(
        CAST(t.satisfaction_score AS DECIMAL(18,2))
    ) AS avg_satisfaction_score,

    SUM(t.escalation_flag)
        AS escalations

FROM dbo.clean_subscriptions s

LEFT JOIN dbo.clean_support_tickets t
    ON s.account_id = t.account_id

GROUP BY s.churn_flag
ORDER BY s.churn_flag;
GO


/* ============================================================
   12. SUPPORT PRIORITY VS CHURN
   ============================================================ */

SELECT
    t.priority,
    s.churn_flag,

    COUNT(*) AS ticket_count,

    AVG(
        CAST(t.resolution_time_hours AS DECIMAL(18,2))
    ) AS avg_resolution_hours,

    AVG(
        CAST(t.satisfaction_score AS DECIMAL(18,2))
    ) AS avg_satisfaction_score

FROM dbo.clean_support_tickets t

INNER JOIN dbo.clean_subscriptions s
    ON t.account_id = s.account_id

GROUP BY
    t.priority,
    s.churn_flag

ORDER BY
    t.priority,
    s.churn_flag;
GO


/* ============================================================
   13. ESCALATION VS CHURN
   ============================================================ */

SELECT
    t.escalation_flag,

    COUNT(DISTINCT s.account_id)
        AS customers,

    SUM(
        CASE WHEN s.churn_flag = 1
        THEN 1 ELSE 0 END
    ) AS churned,

    CAST(
        100.0 *
        SUM(
            CASE WHEN s.churn_flag = 1
            THEN 1 ELSE 0 END
        )
        / NULLIF(COUNT(DISTINCT s.account_id), 0)
        AS DECIMAL(10,2)
    ) AS churn_rate_pct

FROM dbo.clean_support_tickets t

INNER JOIN dbo.clean_subscriptions s
    ON t.account_id = s.account_id

GROUP BY t.escalation_flag

ORDER BY churn_rate_pct DESC;
GO


/* ============================================================
   14. HIGHEST-VALUE CHURNED CUSTOMERS
   ============================================================ */

SELECT TOP 20
    account_id,
    subscription_id,
    plan_tier,
    seats,
    mrr_amount,
    arr_amount,
    billing_frequency,
    churn_flag

FROM dbo.clean_subscriptions

WHERE churn_flag = 1

ORDER BY arr_amount DESC;
GO


/* ============================================================
   15. TOP REVENUE ACCOUNTS
   ============================================================ */

SELECT TOP 20
    account_id,
    subscription_id,
    plan_tier,
    seats,
    mrr_amount,
    arr_amount,
    churn_flag

FROM dbo.clean_subscriptions

ORDER BY arr_amount DESC;
GO


/* ============================================================
   16. REVENUE CONCENTRATION BY PLAN
   ============================================================ */

SELECT
    plan_tier,

    COUNT(DISTINCT account_id) AS customers,

    SUM(mrr_amount) AS total_mrr,

    SUM(arr_amount) AS total_arr,

    CAST(
        100.0 * SUM(arr_amount)
        / NULLIF(
            (
                SELECT SUM(arr_amount)
                FROM dbo.clean_subscriptions
            ),
            0
        )
        AS DECIMAL(10,2)
    ) AS pct_total_arr

FROM dbo.clean_subscriptions

GROUP BY plan_tier

ORDER BY total_arr DESC;
GO


/* ============================================================
   17. AUTO-RENEWAL VS CHURN
   ============================================================ */

SELECT
    auto_renew_flag,

    COUNT(*) AS subscriptions,

    SUM(
        CASE WHEN churn_flag = 1
        THEN 1 ELSE 0 END
    ) AS churned,

    CAST(
        100.0 *
        SUM(
            CASE WHEN churn_flag = 1
            THEN 1 ELSE 0 END
        )
        / NULLIF(COUNT(*), 0)
        AS DECIMAL(10,2)
    ) AS churn_rate_pct,

    SUM(arr_amount) AS total_arr

FROM dbo.clean_subscriptions

GROUP BY auto_renew_flag

ORDER BY churn_rate_pct DESC;
GO


/* ============================================================
   18. MONTHLY SUBSCRIPTION / CHURN TREND
   ============================================================ */

SELECT
    YEAR(start_date) AS analysis_year,

    MONTH(start_date) AS analysis_month,

    COUNT(*) AS subscriptions_started,

    SUM(
        CASE WHEN churn_flag = 1
        THEN 1 ELSE 0 END
    ) AS churned,

    CAST(
        100.0 *
        SUM(
            CASE WHEN churn_flag = 1
            THEN 1 ELSE 0 END
        )
        / NULLIF(COUNT(*), 0)
        AS DECIMAL(10,2)
    ) AS churn_rate_pct

FROM dbo.clean_subscriptions

GROUP BY
    YEAR(start_date),
    MONTH(start_date)

ORDER BY
    analysis_year,
    analysis_month;
GO


/* ============================================================
   19. EXECUTIVE KPI SUMMARY
   ============================================================ */

SELECT

    COUNT(DISTINCT account_id)
        AS total_customers,

    COUNT(*)
        AS total_subscriptions,

    SUM(
        CASE WHEN churn_flag = 1
        THEN 1 ELSE 0 END
    ) AS churned_customers,

    CAST(
        100.0 *
        SUM(
            CASE WHEN churn_flag = 1
            THEN 1 ELSE 0 END
        )
        / NULLIF(COUNT(*), 0)
        AS DECIMAL(10,2)
    ) AS churn_rate_pct,

    SUM(mrr_amount)
        AS total_mrr,

    SUM(arr_amount)
        AS total_arr,

    SUM(
        CASE WHEN churn_flag = 1
        THEN arr_amount ELSE 0 END
    ) AS arr_at_risk,

    CAST(
        100.0 *
        SUM(
            CASE WHEN churn_flag = 1
            THEN arr_amount ELSE 0 END
        )
        / NULLIF(SUM(arr_amount), 0)
        AS DECIMAL(10,2)
    ) AS arr_at_risk_pct,

    SUM(
        CASE WHEN upgrade_flag = 1
        THEN 1 ELSE 0 END
    ) AS upgrades,

    SUM(
        CASE WHEN downgrade_flag = 1
        THEN 1 ELSE 0 END
    ) AS downgrades

FROM dbo.clean_subscriptions;
GO


/* ============================================================
   END OF STAGE 3
   ============================================================ */

PRINT '==============================================';
PRINT 'STAGE 3 BUSINESS ANALYSIS COMPLETE';
PRINT '==============================================';
GO