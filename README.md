# Bank Credit Risk Analysis

> End-to-end credit risk analytics pipeline — data engineering, statistical testing, machine learning, and real-time Streamlit dashboard built to simulate a bank's internal credit decisioning workflow.

**Stack:** Python · Pandas · NumPy · Scikit-learn · XGBoost · SMOTE · Matplotlib · Seaborn · SciPy · Statsmodels · SQL · openpyxl · Streamlit · Docker

---

## Results at a Glance

| Metric | Value |
|---|---|
| Dataset | 5,000 records × 12 features |
| Records after cleaning | 4,850 (100% validation pass rate) |
| Missing values imputed | 506 (median imputation) |
| SQL queries written | 18 (MySQL / PostgreSQL) |
| Statistical tests run | 17 |
| XGBoost ROC-AUC (OvR) | **99.3%** |
| 5-Fold CV ROC-AUC | **99.32% ± 0.19%** |
| Overall accuracy | **93.6%** |
| Weighted F1-Score | **0.94** |
| Top default predictors | `num_defaults`, `credit_utilization`, `debt_to_income_ratio` |

---

## Project Structure

```
Bank Credit Risk Analysis/
├── data/
│   ├── credit_data.csv             # Raw synthetic dataset (5,000 records)
│   └── credit_data_clean.csv       # Cleaned & feature-engineered dataset (4,850 records)
├── notebooks/
│   └── credit_risk_analysis.ipynb  # Full analysis: EDA → Stats → ML
├── src/
│   ├── generate_data.py            # Synthetic data generation with realistic bank logic
│   ├── cleaning.py                 # Cleaning pipeline: imputation, outliers, validation
│   ├── build_dashboard.py          # Excel dashboard builder (openpyxl)
│   └── get_metrics.py              # Prints all provable model metrics
├── sql/
│   └── queries.sql                 # 18 SQL queries: validation, segmentation, KPI reporting
├── output/
│   ├── plots/                      # Saved Matplotlib charts
│   └── dashboard.xlsx              # 3-sheet Excel dashboard
├── app.py                          # Streamlit credit assessment dashboard
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate and clean data
```bash
python src/generate_data.py
python src/cleaning.py
```

### 3. Launch the Streamlit app
```bash
streamlit run app.py
```

### 4. Run the Jupyter notebook
```bash
jupyter notebook notebooks/credit_risk_analysis.ipynb
```

### 5. Build the Excel dashboard
```bash
python src/build_dashboard.py
```

### 6. Print model metrics
```bash
python src/get_metrics.py
```

### 7. Run with Docker
```bash
docker build -t credit-risk-app .
docker run -p 8501:8501 credit-risk-app
```
Open: http://localhost:8501

---

## Dataset Features

| Feature | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `age` | Customer age (21–65) |
| `employment_status` | Employed / Self-Employed / Unemployed / Retired |
| `income` | Annual income ($) |
| `loan_amount` | Loan amount requested ($) |
| `loan_tenure` | Loan duration in months |
| `credit_score` | FICO-style credit score (300–850) |
| `credit_utilization` | Ratio of credit used (0.0–1.0) |
| `repayment_history` | On-time payments out of last 24 months |
| `num_defaults` | Number of historical loan defaults |
| `debt_to_income_ratio` | Loan amount ÷ annual income |
| `risk_label` | Target variable: Low / Medium / High |

**Engineered features added during cleaning:**

| Feature | Formula |
|---|---|
| `monthly_emi` | `loan_amount / loan_tenure` |
| `emi_to_income_ratio` | `monthly_emi / (income / 12)` |
| `risk_score_numeric` | `Low=0, Medium=1, High=2` |

---

## Analysis Pipeline

### Data Cleaning
- Detected and imputed **506 missing values** using median imputation
- Removed duplicates and standardized categorical labels to Title Case
- Applied IQR-based outlier removal (1st–99th percentile) on income and loan amount
- Ran **8 assertion-based validation checks** (dtype, range, null, label integrity)
- Output: 4,850 clean records with 100% validation pass rate

### SQL Queries (18 Total)
Written in MySQL / PostgreSQL syntax across 4 analytical sections:
- **Data Validation** — null checks, duplicate detection, range assertions
- **Risk Segmentation** — risk tier distribution, employment vs risk, credit score bands
- **Repayment & Credit Behavior** — utilization buckets, repayment quality tiers
- **Loan Portfolio Analytics** — exposure by risk tier, DTI analysis, high-risk flags

### Exploratory Data Analysis
- Feature distributions across all 12 variables
- Correlation heatmap (Pearson)
- Risk segmentation by employment status and age group
- Credit utilization vs credit score scatter by risk tier
- Box plots: income, credit score, DTI ratio by risk label
- 10+ saved Matplotlib charts

### Statistical Testing (17 Tests)

| Test | Purpose |
|---|---|
| Independent t-test × 2 | Credit score & income: Low vs High risk |
| One-Way ANOVA × 2 | Credit score & income across 3 risk groups |
| Chi-Square × 2 | Employment status vs risk; defaults vs risk |
| Mann-Whitney U × 2 | Credit utilization & DTI: Low vs High risk |
| Pearson Correlation × 2 | Credit score vs utilization; income vs loan amount |
| Spearman Correlation × 2 | DTI vs risk score; repayment history vs defaults |
| Shapiro-Wilk | Normality of credit score distribution |
| Levene Test | Variance equality across risk groups |
| Kruskal-Wallis | Repayment history across risk groups |
| OLS Regression | Credit score → risk score (R²) |
| VIF Analysis | Multicollinearity detection across all features |

All key predictors confirmed significant at **p < 0.05**.

### Machine Learning Model

**XGBoost Gradient Boosting Classifier** (3-class: Low / Medium / High risk)

- **Class imbalance handled:** SMOTE oversampling — training set expanded from 3,880 → 6,369 samples
- **Split:** Stratified 80/20 holdout (train/test)
- **Validation:** 5-fold stratified cross-validation
- **Hyperparameters:** `n_estimators=200`, `learning_rate=0.05`, `max_depth=5`

| Metric | Score |
|---|---|
| ROC-AUC (One-vs-Rest) | 99.30% |
| 5-Fold CV ROC-AUC | 99.32% ± 0.19% |
| Overall Accuracy | 93.6% |
| Weighted F1-Score | 0.94 |

**Top 5 features by XGBoost importance:**
1. `num_defaults`
2. `credit_utilization`
3. `debt_to_income_ratio`
4. `credit_score`
5. `repayment_history`

---

## Streamlit Dashboard

A real-time credit assessment app simulating a bank's internal loan review tool.

**Tabs:**
- **Exploratory Analysis** — EDA charts, correlation heatmap, feature distributions
- **Risk Segmentation** — risk tier breakdown, employment risk, age group analysis
- **Model Performance** — confusion matrix, ROC curve, feature importance, CV results
- **Credit Assessment** — live scoring for a new customer profile

**Credit Assessment tab features:**
- FICO score gauge (300–850 semicircle with colored bands)
- Risk classification card with probability breakdown (Low / Medium / High %)
- Loan decision engine: **APPROVED / CONDITIONAL / DECLINED** with rule explanation
- Risk radar chart across 6 financial dimensions
- Portfolio positioning scatter (where customer lands vs full portfolio)
- Risk flag alerts (CRITICAL / WARNING) for high utilization, low score, defaults, etc.

---

## Excel Dashboard (openpyxl)

3-sheet workbook saved to `output/dashboard.xlsx`:

| Sheet | Content |
|---|---|
| Credit Utilization | Utilization by risk tier + bar chart |
| Repayment Trends | Default rates by repayment quality band + bar chart |
| Customer Risk Scores | Loan exposure summary by risk segment + chart |

---

## License

This is a portfolio project built on a fully synthetic dataset. No real customer data was used.
