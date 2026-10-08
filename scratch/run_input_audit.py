"""
Phase India-3 Input Audit Script
Audits data/processed/india/ inputs and raw inputs to create reports/india_phase3_input_audit.md.
"""
import os
import json
import pandas as pd
import numpy as np

# Load tables
postings_path = "data/processed/india/india_job_postings.parquet"
cleaned_path = "data/processed/india/cleaned_india_jobs.parquet"
skills_path = "data/processed/india/india_job_skills.parquet"
taxonomy_path = "data/processed/india/india_taxonomy.json"
raw_excel_path = "data/raw/india/indian-job-market-dataset-2025.xlsx"

print("Auditing inputs...")
df_postings = pd.read_parquet(postings_path)
df_cleaned = pd.read_parquet(cleaned_path)
df_skills = pd.read_parquet(skills_path)
with open(taxonomy_path, "r", encoding="utf-8") as f:
    tax_meta = json.load(f)

audit_data = {}

# 1. Dimensions
audit_data["files"] = {
    "raw_excel": {"path": raw_excel_path, "size_bytes": os.path.getsize(raw_excel_path)},
    "cleaned_master": {"path": cleaned_path, "size_bytes": os.path.getsize(cleaned_path), "rows": len(df_cleaned), "cols": len(df_cleaned.columns)},
    "job_postings": {"path": postings_path, "size_bytes": os.path.getsize(postings_path), "rows": len(df_postings), "cols": len(df_postings.columns)},
    "job_skills": {"path": skills_path, "size_bytes": os.path.getsize(skills_path), "rows": len(df_skills), "cols": len(df_skills.columns)},
    "taxonomy_json": {"path": taxonomy_path, "size_bytes": os.path.getsize(taxonomy_path)}
}

# 2. Columns & dtypes for job_postings
col_audit = []
for c in df_postings.columns:
    nulls = int(df_postings[c].isnull().sum())
    null_pct = round(nulls / len(df_postings) * 100, 2)
    dtype_str = str(df_postings[c].dtype)
    n_unique = int(df_postings[c].nunique(dropna=True))
    sample_val = str(df_postings[c].dropna().iloc[0]) if df_postings[c].notnull().any() else "ALL_NULL"
    col_audit.append({
        "column": c,
        "dtype": dtype_str,
        "null_count": nulls,
        "null_pct": null_pct,
        "unique_count": n_unique,
        "sample_val": sample_val[:40]
    })
audit_data["columns_audit"] = col_audit

# 3. Key domain subsets
audit_data["subsets"] = {
    "raw_total": len(df_cleaned),
    "postings_total": len(df_postings),
    "unique_job_ids": int(df_postings["job_id"].nunique()),
    "inr_count": int((df_postings["currency"] == "INR").sum()),
    "usd_count": int((df_postings["currency"] == "USD").sum()),
    "valid_inr_salaries": int(df_postings["is_salary_valid"].sum()),
    "valid_inr_nonnull_lpa": int(df_postings["salary_lpa"].notnull().sum()),
    "tech_postings": int(df_postings["is_tech_role"].sum()),
    "tech_with_valid_salary": int((df_postings["is_tech_role"] & df_postings["is_salary_valid"]).sum()),
    "nontech_with_valid_salary": int((~df_postings["is_tech_role"] & df_postings["is_salary_valid"]).sum()),
    "unique_roles": int(df_postings["role_category"].nunique()),
    "unique_cities": int(df_postings["city"].nunique()),
    "known_city_count": int(df_postings["city"].notnull().sum()),
    "valid_exp_count": int(df_postings["experience_midpoint"].notnull().sum()),
    "valid_exp_pct": round(int(df_postings["experience_midpoint"].notnull().sum()) / len(df_postings) * 100, 2)
}

# 4. Salary sanity
sal_s = df_postings[df_postings["is_salary_valid"]]
audit_data["salary_stats"] = {
    "count": len(sal_s),
    "min_lpa": float(sal_s["salary_lpa"].min()),
    "q25_lpa": float(sal_s["salary_lpa"].quantile(0.25)),
    "median_lpa": float(sal_s["salary_lpa"].median()),
    "mean_lpa": float(sal_s["salary_lpa"].mean()),
    "q75_lpa": float(sal_s["salary_lpa"].quantile(0.75)),
    "p90_lpa": float(sal_s["salary_lpa"].quantile(0.90)),
    "p99_lpa": float(sal_s["salary_lpa"].quantile(0.99)),
    "p99_9_lpa": float(sal_s["salary_lpa"].quantile(0.999)),
    "max_lpa": float(sal_s["salary_lpa"].max()),
    "negative_count": int((sal_s["salary_lpa"] < 0).sum()),
    "zero_count": int((sal_s["salary_lpa"] == 0).sum()),
    "min_gt_max_count": int((sal_s["minimum_salary_inr"] > sal_s["maximum_salary_inr"]).sum())
}

# 5. Skills sanity
audit_data["skills_stats"] = {
    "total_pairs": len(df_skills),
    "unique_jobs_in_skills": int(df_skills["job_id"].nunique()),
    "unique_skills": int(df_skills["skill"].nunique()),
    "duplicate_pairs": int(df_skills.duplicated(subset=["job_id", "skill"]).sum()),
    "orphan_jobs": int((~df_skills["job_id"].isin(set(df_postings["job_id"]))).sum())
}

with open("scratch/input_audit_data.json", "w", encoding="utf-8") as f:
    json.dump(audit_data, f, indent=2)

print("Input audit completed successfully. Saved scratch/input_audit_data.json.")
