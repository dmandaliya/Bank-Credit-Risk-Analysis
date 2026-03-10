"""
generate_data.py
Generates a synthetic bank credit risk dataset with 5000+ records and 12 features.
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
N = 5000

# --- Feature Generation ---
customer_id = [f"CUST{str(i).zfill(5)}" for i in range(1, N + 1)]

age = np.random.randint(21, 65, N)

employment_status = np.random.choice(
    ["Employed", "Self-Employed", "Unemployed", "Retired"],
    N,
    p=[0.60, 0.20, 0.12, 0.08],
)

# Income depends on employment
income = np.where(
    employment_status == "Employed",
    np.random.normal(65000, 20000, N),
    np.where(
        employment_status == "Self-Employed",
        np.random.normal(75000, 30000, N),
        np.where(
            employment_status == "Retired",
            np.random.normal(40000, 10000, N),
            np.random.normal(20000, 8000, N),  # Unemployed
        ),
    ),
)
income = np.clip(income, 10000, 300000).round(2)

loan_amount = np.random.uniform(5000, 150000, N).round(2)

loan_tenure = np.random.choice([12, 24, 36, 48, 60, 84, 120], N)

credit_score = np.random.normal(650, 80, N)
credit_score = np.clip(credit_score, 300, 850).astype(int)

credit_utilization = np.random.beta(2, 5, N)  # Skewed right (most people use <50%)
credit_utilization = np.clip(credit_utilization, 0.01, 1.0).round(4)

# Repayment history: number of on-time payments (out of last 24)
repayment_history = np.random.binomial(24, 0.80, N)

num_defaults = np.random.choice(
    [0, 1, 2, 3, 4, 5],
    N,
    p=[0.60, 0.20, 0.10, 0.05, 0.03, 0.02],
)

debt_to_income_ratio = (loan_amount / income).round(4)
debt_to_income_ratio = np.clip(debt_to_income_ratio, 0.01, 5.0)

# --- Risk Label Logic (realistic bank scoring) ---
# Normalize credit score: 0 = worst (300), 1 = best (850)
cs_norm = (credit_score - 300) / 550.0

# Employment multiplier: unemployed = higher risk
emp_mult = np.where(employment_status == "Unemployed", 1.4,
           np.where(employment_status == "Retired",    1.1,
           np.where(employment_status == "Self-Employed", 1.0, 0.85)))

risk_score = (
    + 5.0 * (1 - cs_norm)            # credit score is dominant: 398→high, 750→low
    + 3.0 * credit_utilization        # high utilization = high risk
    + 1.8 * num_defaults              # each default raises risk significantly
    - 0.10 * repayment_history        # more on-time payments = lower risk
    + 2.5 * debt_to_income_ratio      # high DTI = high risk
    + emp_mult                        # employment penalty
    + np.random.normal(0, 0.25, N)    # small noise
)

# Percentile-based thresholds for realistic class split (~55% Low, 30% Medium, 15% High)
p55 = np.percentile(risk_score, 55)
p85 = np.percentile(risk_score, 85)
risk_label = np.where(risk_score < p55, "Low",
             np.where(risk_score < p85, "Medium", "High"))

# --- Introduce realistic missing values (~2-3%) ---
df = pd.DataFrame({
    "customer_id": customer_id,
    "age": age,
    "employment_status": employment_status,
    "income": income,
    "loan_amount": loan_amount,
    "loan_tenure": loan_tenure,
    "credit_score": credit_score,
    "credit_utilization": credit_utilization,
    "repayment_history": repayment_history,
    "num_defaults": num_defaults,
    "debt_to_income_ratio": debt_to_income_ratio,
    "risk_label": risk_label,
})

for col in ["income", "credit_score", "credit_utilization", "repayment_history"]:
    mask = np.random.rand(N) < 0.025
    df.loc[mask, col] = np.nan

# --- Save ---
os.makedirs("data", exist_ok=True)
output_path = os.path.join(os.path.dirname(__file__), "..", "data", "credit_data.csv")
df.to_csv(output_path, index=False)

print(f"Dataset generated: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Risk label distribution:\n{df['risk_label'].value_counts()}")
print(f"Missing values:\n{df.isnull().sum()}")
print(f"Saved to: {os.path.abspath(output_path)}")
