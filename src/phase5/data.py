"""
Phase 5: Data Loading, Audit, and Partitioning
==============================================
INT234 Predictive Analytics — Job Market Intelligence
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

DATA_DIR = "data/processed"
TABLES_DIR = "reports/tables/phase5"
RANDOM_STATE = 42
TEST_SIZE = 0.20


def load_raw_modeling_data():
    """Load the verified Phase 2.1 modeling dataset and 82 technical skills taxonomy."""
    model_path = os.path.join(DATA_DIR, "modeling_dataset.parquet")
    tech_path = os.path.join(DATA_DIR, "skill_matrix_technical.parquet")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modeling dataset not found at {model_path}")
    if not os.path.exists(tech_path):
        raise FileNotFoundError(f"Technical skills matrix not found at {tech_path}")

    df = pd.read_parquet(model_path)
    df_tech = pd.read_parquet(tech_path)
    tech_skills = df_tech.columns.tolist()

    return df, tech_skills


def audit_dataset(df, tech_skills):
    """
    Perform rigorous data audit:
    - Row count & column count
    - Target completeness, statistics, and skewness
    - Missing values and duplicate IDs
    - Feature distributions
    """
    os.makedirs(TABLES_DIR, exist_ok=True)

    n_rows, n_cols = df.shape
    target = df["salary_midpoint"]
    log_target = np.log1p(target)

    # Integrity checks
    null_count = int(df.isnull().sum().sum())
    dup_ids = int(df["job_id"].duplicated().sum()) if "job_id" in df.columns else 0

    # Skill validation
    present_tech_skills = [c for c in tech_skills if c in df.columns]
    missing_tech_skills = [c for c in tech_skills if c not in df.columns]
    assert len(missing_tech_skills) == 0, f"Missing technical skills in modeling dataset: {missing_tech_skills}"

    audit_records = [
        {"Metric": "Total Observations (N)", "Value": str(n_rows), "Description": "Verified technology postings with valid USD salary"},
        {"Metric": "Total Features in Parquet", "Value": str(n_cols), "Description": "All metadata and skill indicator columns"},
        {"Metric": "Technical Skills (Taxonomy D)", "Value": str(len(present_tech_skills)), "Description": "Standardized 82 technical skill features"},
        {"Metric": "Duplicate job_id Count", "Value": str(dup_ids), "Description": "Should be strictly 0"},
        {"Metric": "Total Missing / Null Values", "Value": str(null_count), "Description": "Should be strictly 0"},
        {"Metric": "Target Min Salary ($)", "Value": f"${target.min():,.2f}", "Description": "Lower salary boundary ($30,000)"},
        {"Metric": "Target Q1 Salary ($)", "Value": f"${target.quantile(0.25):,.2f}", "Description": "25th percentile"},
        {"Metric": "Target Median Salary ($)", "Value": f"${target.median():,.2f}", "Description": "Median salary midpoint"},
        {"Metric": "Target Mean Salary ($)", "Value": f"${target.mean():,.2f}", "Description": "Arithmetic mean"},
        {"Metric": "Target Q3 Salary ($)", "Value": f"${target.quantile(0.75):,.2f}", "Description": "75th percentile"},
        {"Metric": "Target Max Salary ($)", "Value": f"${target.max():,.2f}", "Description": "Upper salary boundary ($600,000)"},
        {"Metric": "Target Std Dev ($)", "Value": f"${target.std():,.2f}", "Description": "Standard deviation"},
        {"Metric": "Target IQR ($)", "Value": f"${target.quantile(0.75) - target.quantile(0.25):,.2f}", "Description": "Interquartile range"},
        {"Metric": "Raw Target Skewness", "Value": f"{target.skew():.4f}", "Description": "Positive right-tail skewness"},
        {"Metric": "Raw Target Kurtosis", "Value": f"{target.kurtosis():.4f}", "Description": "Kurtosis of raw salary"},
        {"Metric": "Log Target Skewness", "Value": f"{log_target.skew():.4f}", "Description": "Skewness of log1p(salary)"},
        {"Metric": "Log Target Kurtosis", "Value": f"{log_target.kurtosis():.4f}", "Description": "Kurtosis of log1p(salary)"},
        {"Metric": "Seniority Classes", "Value": str(df['seniority'].nunique()), "Description": "Tiers: Intern, Junior, Mid, Senior, Lead"},
        {"Metric": "Role Family Classes", "Value": str(df['role_family'].nunique()), "Description": "18 standardized role families"},
        {"Metric": "Remote Flag Classes", "Value": str(df['is_remote'].nunique()), "Description": "Boolean True/False"},
        {"Metric": "Cleaned Cities Classes", "Value": str(df['city_clean'].nunique()), "Description": "Top metropolitan locations + Other"},
    ]

    audit_df = pd.DataFrame(audit_records)
    audit_csv_path = os.path.join(TABLES_DIR, "phase5_data_audit.csv")
    audit_df.to_csv(audit_csv_path, index=False)
    print(f"[DATA AUDIT] Successfully exported audit table: {audit_csv_path}")

    return audit_df


def get_train_test_split(df, tech_skills):
    """
    Perform strict 80/20 train/test split.
    The test set must remain isolated until final model evaluation.
    """
    # Columns to strictly exclude from feature sets
    leakage_cols = [
        "job_id",
        "title",
        "company_name",
        "salary_midpoint",
        "log_salary",
        "salary_band",
    ]

    # Non-skill metadata predictors
    metadata_cols = ["seniority", "role_family", "is_remote", "city_clean", "num_skills"]

    # Verify all predictors exist
    for col in metadata_cols:
        assert col in df.columns, f"Metadata column '{col}' missing from modeling dataset!"
    for col in tech_skills:
        assert col in df.columns, f"Technical skill column '{col}' missing from modeling dataset!"

    feature_cols = metadata_cols + tech_skills

    X = df[feature_cols].copy()
    y = df["salary_midpoint"].values.astype(np.float64)
    y_log = np.log1p(y)

    # 80/20 Split with fixed random seed
    train_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        shuffle=True
    )

    X_train = X.iloc[train_idx].reset_index(drop=True)
    X_test = X.iloc[test_idx].reset_index(drop=True)
    y_train = y[train_idx]
    y_test = y[test_idx]
    y_train_log = y_log[train_idx]
    y_test_log = y_log[test_idx]

    print(f"[TRAIN/TEST SPLIT] Total N = {len(df):,}")
    print(f"  - Training Set (80%): N = {len(X_train):,} rows, {X_train.shape[1]} features")
    print(f"  - Test Set (20%):     N = {len(X_test):,} rows (ISOLATED for final evaluation)")

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "y_train_log": y_train_log,
        "y_test_log": y_test_log,
        "metadata_cols": metadata_cols,
        "tech_skills": tech_skills,
        "train_idx": train_idx,
        "test_idx": test_idx,
    }


if __name__ == "__main__":
    df, tech_skills = load_raw_modeling_data()
    audit_dataset(df, tech_skills)
    split_data = get_train_test_split(df, tech_skills)
    print("Stage 1-3 Data loading & partitioning passed.")
