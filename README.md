# Bank Credit Risk Analysis

End-to-end credit risk pipeline covering data engineering, statistical analysis, machine learning, and a live Streamlit dashboard simulating a bank's internal loan review system.

**Stack:** Python · Pandas · NumPy · XGBoost · Scikit-learn · SMOTE · SciPy · Statsmodels · SQL · Matplotlib · Seaborn · openpyxl · Streamlit · Docker

---

## Model Performance

| Metric | Score |
|---|---|
| ROC-AUC (One-vs-Rest) | 99.3% |
| 5-Fold CV ROC-AUC | 99.32% ± 0.19% |
| Accuracy | 93.6% |
| Weighted F1-Score | 0.94 |

---

## What's Inside

| Component | Details |
|---|---|
| Dataset | 5,000 records × 12 features → 4,850 after cleaning |
| Data Cleaning | Median imputation, IQR outlier removal, 8 validation checks |
| SQL | 18 queries — validation, segmentation, KPI reporting (MySQL/PostgreSQL) |
| EDA | 10+ Matplotlib charts — distributions, heatmaps, scatter plots |
| Statistical Tests | 17 tests — t-test, ANOVA, Chi-Square, Mann-Whitney, OLS, VIF, and more |
| ML Model | XGBoost (3-class) + SMOTE oversampling for class imbalance |
| Streamlit App | FICO gauge, radar chart, loan approval engine, risk flags |
| Excel Dashboard | 3-sheet openpyxl workbook with bar charts |

---

## How to Run

```bash
pip install -r requirements.txt

python src/generate_data.py
python src/cleaning.py

streamlit run app.py
```

**Docker:**
```bash
docker build -t credit-risk-app .
docker run -p 8501:8501 credit-risk-app
```

---

## License

MIT License — free to use and modify.
