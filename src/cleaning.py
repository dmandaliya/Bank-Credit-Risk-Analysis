"""
cleaning.py
Cleans, standardizes, and validates the credit risk dataset.
Produces a cleaned CSV used by the notebook and Streamlit app.
"""

import pandas as pd
import numpy as np
import os

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "credit_data.csv")
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "credit_data_clean.csv")


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"[LOAD] Shape: {df.shape}")
    return df


def report_missing(df: pd.DataFrame) -> None:
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    print("\n[MISSING VALUES BEFORE CLEANING]")
    for col, count in missing.items():
        print(f"  {col}: {count} ({count/len(df)*100:.2f}%)")


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    # Numeric: fill with median (robust to outliers)
    numeric_cols = ["income", "credit_score", "credit_utilization", "repayment_history"]
    for col in numeric_cols:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"  [IMPUTE] {col} → median = {median_val:.2f}")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset="customer_id")
    removed = before - len(df)
    print(f"\n[DUPLICATES] Removed: {removed}")
    return df


def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df["credit_score"] = df["credit_score"].astype(int)
    df["repayment_history"] = df["repayment_history"].astype(int)
    df["age"] = df["age"].astype(int)
    df["loan_tenure"] = df["loan_tenure"].astype(int)
    df["num_defaults"] = df["num_defaults"].astype(int)
    print("\n[DTYPES] Fixed: credit_score, repayment_history, age, loan_tenure, num_defaults → int")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    # IQR method for income and loan_amount
    for col in ["income", "loan_amount"]:
        Q1 = df[col].quantile(0.01)
        Q3 = df[col].quantile(0.99)
        df = df[(df[col] >= Q1) & (df[col] <= Q3)]
    removed = before - len(df)
    print(f"\n[OUTLIERS] Removed: {removed} rows via IQR on income & loan_amount")
    return df


def standardize_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    df["employment_status"] = df["employment_status"].str.strip().str.title()
    df["risk_label"] = df["risk_label"].str.strip().str.title()
    print("\n[STANDARDIZE] employment_status, risk_label → Title Case")
    return df


def validate(df: pd.DataFrame) -> None:
    print("\n[VALIDATION CHECKS]")
    assert df["credit_score"].between(300, 850).all(), "Credit score out of range!"
    assert df["credit_utilization"].between(0, 1).all(), "Credit utilization out of range!"
    assert df["age"].between(18, 100).all(), "Age out of range!"
    assert df["income"].gt(0).all(), "Negative income found!"
    assert df["loan_amount"].gt(0).all(), "Negative loan amount found!"
    assert df["repayment_history"].between(0, 24).all(), "Repayment history out of range!"
    assert df["num_defaults"].ge(0).all(), "Negative defaults found!"
    assert df["risk_label"].isin(["Low", "Medium", "High"]).all(), "Unknown risk label!"
    assert df.isnull().sum().sum() == 0, "Missing values remain!"
    print("  All checks passed. 100% records validated.")


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    df["monthly_emi"] = (df["loan_amount"] / df["loan_tenure"]).round(2)
    df["emi_to_income_ratio"] = (df["monthly_emi"] / (df["income"] / 12)).round(4)
    df["risk_score_numeric"] = df["risk_label"].map({"Low": 0, "Medium": 1, "High": 2})
    print("\n[FEATURE ENGINEERING] Added: monthly_emi, emi_to_income_ratio, risk_score_numeric")
    return df


def save(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
    print(f"\n[SAVE] Cleaned data saved → {os.path.abspath(path)}")
    print(f"[FINAL SHAPE] {df.shape[0]} rows x {df.shape[1]} columns")


def run():
    df = load_data(RAW_PATH)
    report_missing(df)
    df = remove_duplicates(df)
    df = handle_missing(df)
    df = fix_dtypes(df)
    df = remove_outliers(df)
    df = standardize_categoricals(df)
    validate(df)
    df = add_engineered_features(df)
    save(df, CLEAN_PATH)
    return df


if __name__ == "__main__":
    run()
