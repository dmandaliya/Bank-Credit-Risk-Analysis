-- ============================================================
-- Bank Credit Risk Analysis — SQL Queries
-- Compatible with: MySQL, PostgreSQL
-- Table: credit_data (loaded from credit_data_clean.csv)
-- ============================================================

-- -------------------------------------------------------
-- SECTION 1: DATA VALIDATION & QUALITY CHECKS
-- -------------------------------------------------------

-- Q1: Check total record count
SELECT COUNT(*) AS total_records
FROM credit_data;

-- Q2: Check for NULL values in critical columns
SELECT
    SUM(CASE WHEN credit_score IS NULL THEN 1 ELSE 0 END)       AS null_credit_score,
    SUM(CASE WHEN income IS NULL THEN 1 ELSE 0 END)              AS null_income,
    SUM(CASE WHEN credit_utilization IS NULL THEN 1 ELSE 0 END)  AS null_utilization,
    SUM(CASE WHEN repayment_history IS NULL THEN 1 ELSE 0 END)   AS null_repayment,
    SUM(CASE WHEN risk_label IS NULL THEN 1 ELSE 0 END)          AS null_risk_label
FROM credit_data;

-- Q3: Validate credit score range (must be 300–850)
SELECT COUNT(*) AS invalid_credit_scores
FROM credit_data
WHERE credit_score < 300 OR credit_score > 850;

-- Q4: Validate credit utilization range (must be 0–1)
SELECT COUNT(*) AS invalid_utilization
FROM credit_data
WHERE credit_utilization < 0 OR credit_utilization > 1;

-- Q5: Check for duplicate customer IDs
SELECT customer_id, COUNT(*) AS occurrences
FROM credit_data
GROUP BY customer_id
HAVING COUNT(*) > 1;


-- -------------------------------------------------------
-- SECTION 2: CUSTOMER SEGMENTATION & RISK REPORTING
-- -------------------------------------------------------

-- Q6: Distribution of risk labels
SELECT
    risk_label,
    COUNT(*)                                  AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM credit_data
GROUP BY risk_label
ORDER BY customer_count DESC;

-- Q7: Average credit score by risk tier
SELECT
    risk_label,
    ROUND(AVG(credit_score), 2)   AS avg_credit_score,
    ROUND(MIN(credit_score), 2)   AS min_credit_score,
    ROUND(MAX(credit_score), 2)   AS max_credit_score
FROM credit_data
GROUP BY risk_label
ORDER BY avg_credit_score DESC;

-- Q8: Average income and loan amount by risk tier
SELECT
    risk_label,
    ROUND(AVG(income), 2)        AS avg_income,
    ROUND(AVG(loan_amount), 2)   AS avg_loan_amount,
    ROUND(AVG(debt_to_income_ratio), 4) AS avg_dti_ratio
FROM credit_data
GROUP BY risk_label
ORDER BY avg_income DESC;

-- Q9: Credit utilization buckets by risk label
SELECT
    risk_label,
    CASE
        WHEN credit_utilization < 0.30 THEN 'Low (<30%)'
        WHEN credit_utilization < 0.60 THEN 'Medium (30-60%)'
        ELSE 'High (>60%)'
    END AS utilization_bucket,
    COUNT(*) AS count
FROM credit_data
GROUP BY risk_label, utilization_bucket
ORDER BY risk_label, count DESC;

-- Q10: Default rate by employment status
SELECT
    employment_status,
    COUNT(*)                                            AS total_customers,
    SUM(CASE WHEN risk_label = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
    ROUND(SUM(CASE WHEN risk_label = 'High' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS high_risk_pct
FROM credit_data
GROUP BY employment_status
ORDER BY high_risk_pct DESC;


-- -------------------------------------------------------
-- SECTION 3: REPAYMENT & CREDIT BEHAVIOR ANALYSIS
-- -------------------------------------------------------

-- Q11: Repayment trend — avg on-time payments by risk label
SELECT
    risk_label,
    ROUND(AVG(repayment_history), 2)  AS avg_ontime_payments,
    ROUND(AVG(num_defaults), 2)       AS avg_defaults
FROM credit_data
GROUP BY risk_label
ORDER BY avg_ontime_payments DESC;

-- Q12: Customers with 0 defaults but still high risk (edge cases)
SELECT COUNT(*) AS zero_default_high_risk
FROM credit_data
WHERE num_defaults = 0 AND risk_label = 'High';

-- Q13: Top 10 highest risk customers by debt-to-income ratio
SELECT
    customer_id,
    income,
    loan_amount,
    credit_score,
    debt_to_income_ratio,
    risk_label
FROM credit_data
WHERE risk_label = 'High'
ORDER BY debt_to_income_ratio DESC
LIMIT 10;


-- -------------------------------------------------------
-- SECTION 4: LOAN PORTFOLIO ANALYTICS
-- -------------------------------------------------------

-- Q14: Total loan exposure by risk tier
SELECT
    risk_label,
    COUNT(*)                          AS num_loans,
    ROUND(SUM(loan_amount), 2)        AS total_exposure,
    ROUND(AVG(loan_amount), 2)        AS avg_loan_amount,
    ROUND(AVG(loan_tenure), 1)        AS avg_tenure_months
FROM credit_data
GROUP BY risk_label
ORDER BY total_exposure DESC;

-- Q15: Monthly EMI affordability check (EMI > 40% of monthly income = stress)
SELECT
    risk_label,
    COUNT(*) AS stressed_customers
FROM credit_data
WHERE emi_to_income_ratio > 0.40
GROUP BY risk_label
ORDER BY stressed_customers DESC;

-- Q16: Age group segmentation and risk distribution
SELECT
    CASE
        WHEN age BETWEEN 21 AND 30 THEN '21-30'
        WHEN age BETWEEN 31 AND 40 THEN '31-40'
        WHEN age BETWEEN 41 AND 50 THEN '41-50'
        ELSE '51+'
    END AS age_group,
    risk_label,
    COUNT(*) AS count
FROM credit_data
GROUP BY age_group, risk_label
ORDER BY age_group, count DESC;

-- Q17: Credit score bands and default frequency
SELECT
    CASE
        WHEN credit_score < 500 THEN 'Very Poor (<500)'
        WHEN credit_score < 600 THEN 'Poor (500-599)'
        WHEN credit_score < 670 THEN 'Fair (600-669)'
        WHEN credit_score < 740 THEN 'Good (670-739)'
        WHEN credit_score < 800 THEN 'Very Good (740-799)'
        ELSE 'Exceptional (800+)'
    END AS credit_band,
    COUNT(*)                                                       AS customers,
    ROUND(AVG(num_defaults), 2)                                    AS avg_defaults,
    ROUND(SUM(CASE WHEN risk_label = 'High' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS high_risk_pct
FROM credit_data
GROUP BY credit_band
ORDER BY avg_defaults DESC;

-- Q18: Summary dashboard KPIs
SELECT
    COUNT(*)                                                          AS total_customers,
    ROUND(AVG(credit_score), 1)                                       AS avg_credit_score,
    ROUND(AVG(income), 2)                                             AS avg_income,
    ROUND(AVG(credit_utilization) * 100, 2)                          AS avg_utilization_pct,
    ROUND(AVG(num_defaults), 2)                                       AS avg_defaults,
    SUM(CASE WHEN risk_label = 'High' THEN 1 ELSE 0 END)              AS total_high_risk,
    ROUND(SUM(loan_amount), 2)                                        AS total_loan_portfolio
FROM credit_data;
