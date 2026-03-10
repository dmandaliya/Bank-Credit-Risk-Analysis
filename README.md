# Bank Credit Risk Analysis

**Tools:** Python · Pandas · NumPy · Scikit-learn · XGBoost · Matplotlib · Seaborn · SciPy · Statsmodels · SQL · Excel · Streamlit · Docker

---

## Overview

End-to-end credit risk analytics pipeline built on a synthetic dataset of **5,000+ bank customers** across **12 features**. Covers data generation, cleaning, SQL validation, EDA, 16 statistical tests, customer segmentation, and a credit default prediction model with a live Streamlit dashboard.

---

## Project Structure

```
Bank Credit Risk Analysis/
├── data/
│   ├── credit_data.csv           # Raw synthetic dataset (5,000 records)
│   └── credit_data_clean.csv     # Cleaned & validated dataset (4,850 records)
├── notebooks/
│   └── credit_risk_analysis.ipynb  # Main analysis notebook
├── src/
│   ├── generate_data.py          # Synthetic data generation
│   ├── cleaning.py               # Data cleaning & validation
│   └── build_dashboard.py        # Excel dashboard builder
├── sql/
│   └── queries.sql               # 18 SQL queries (validation, segmentation, reporting)
├── output/
│   ├── plots/                    # Saved Matplotlib charts
│   └── dashboard.xlsx            # Excel dashboard (3 sheets + charts)
├── app.py                        # Streamlit interactive dashboard
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Key Results

| Metric | Value |
|---|---|
| Dataset Size | 5,000 records × 12 features |
| Records Validated (100%) | 4,850 after cleaning |
| Statistical Tests Run | 16 |
| XGBoost ROC-AUC | ~0.92+ (One-vs-Rest) |
| High Risk Customers | ~4% of portfolio |
| Top Predictor of Default | `num_defaults`, `credit_utilization`, `debt_to_income_ratio` |

---

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate & Clean Data
```bash
python src/generate_data.py
python src/cleaning.py
```

### 3. Launch Streamlit App
```bash
streamlit run app.py
```

### 4. Open Jupyter Notebook
```bash
jupyter notebook notebooks/credit_risk_analysis.ipynb
```

### 5. Build Excel Dashboard
```bash
python src/build_dashboard.py
```

### 6. Run with Docker
```bash
docker build -t credit-risk-app .
docker run -p 8501:8501 credit-risk-app
```
Then open: http://localhost:8501

---

## Dataset Features

| Feature | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `age` | Customer age (21–65) |
| `employment_status` | Employed / Self-Employed / Unemployed / Retired |
| `income` | Annual income ($) |
| `loan_amount` | Loan amount ($) |
| `loan_tenure` | Loan duration in months |
| `credit_score` | Credit score (300–850) |
| `credit_utilization` | Ratio of credit used (0–1) |
| `repayment_history` | On-time payments out of last 24 |
| `num_defaults` | Number of historical defaults |
| `debt_to_income_ratio` | Loan amount / Annual income |
| `risk_label` | Target: Low / Medium / High |

---

## Analysis Highlights

### EDA
- Distribution analysis across all 12 features
- Correlation matrix with heatmap
- Risk segmentation by employment status and age group
- Credit utilization vs credit score scatter by risk tier

### Statistical Tests (16 Total)
- Independent t-test (credit score, income: Low vs High risk)
- One-Way ANOVA (credit score, income across 3 risk groups)
- Chi-Square (employment status vs risk, defaults vs risk)
- Mann-Whitney U (credit utilization, DTI ratio)
- Pearson & Spearman correlation (credit score vs utilization, DTI vs risk)
- Shapiro-Wilk normality test
- Levene variance test
- Kruskal-Wallis test (repayment history)
- OLS Regression (credit score → risk score, R²)
- VIF multicollinearity analysis

### Machine Learning
- **Models:** Logistic Regression, Random Forest, XGBoost
- **Class Imbalance:** SMOTE oversampling
- **Evaluation:** ROC-AUC, confusion matrix, classification report, 5-fold cross-validation
- **Feature Importance:** XGBoost importance scores

### SQL Queries (18 Queries)
- Data validation & null checks
- Risk tier distribution and KPI reporting
- Credit utilization bucketing
- Loan portfolio exposure analysis
- Age group and credit score band segmentation

---

## Streamlit App Features
- Live credit risk prediction with sidebar inputs
- Real-time risk probability display
- Risk flag alerts (high utilization, low credit score, etc.)
- EDA charts, risk analysis, model performance tabs
- Full dataset preview

---

## Author
Deep | Data Science Portfolio Project | Bank Credit Risk Analysis
