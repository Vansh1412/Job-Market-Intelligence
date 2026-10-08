"""
JobIntel India — Phase India-3: Modeling Cohort Isolation.
Defines, evaluates, and isolates the primary modeling population from the analytical postings layer.
Generates:
- reports/tables/india/salary_bound_analysis.csv
- reports/tables/india/cohort_comparison.csv
- reports/tables/india/content_duplicate_analysis.csv
"""

import os
import json
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, Tuple

POSTINGS_PARQUET = "data/processed/india/india_job_postings.parquet"
OUTPUT_TABLES_DIR = "reports/tables/india"

def load_and_filter_salary_cohort(postings_path: str = POSTINGS_PARQUET) -> pd.DataFrame:
    """Loads postings and filters strictly to domestic INR postings with valid salary ranges."""
    df = pd.read_parquet(postings_path)
    sal_df = df[df["is_salary_valid"] & (df["currency"] == "INR")].copy()
    return sal_df

def evaluate_salary_bounds(sal_df: pd.DataFrame, lower_lpa: float = 1.20, upper_lpa: float = 80.00) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Evaluates proposed salary bounds (₹1.20 LPA to ₹80.00 LPA) against empirical data.
    Returns:
        bounded_df: DataFrame with records within bounds
        analysis_df: DataFrame summarizing bound metrics
    """
    below_mask = sal_df["salary_lpa"] < lower_lpa
    above_mask = sal_df["salary_lpa"] > upper_lpa
    bounded_mask = (~below_mask) & (~above_mask)
    
    n_total = len(sal_df)
    n_below = int(below_mask.sum())
    n_above = int(above_mask.sum())
    n_retained = int(bounded_mask.sum())
    
    bound_records = [
        {
            "segment": f"Lower Tail (< {lower_lpa:.2f} LPA)",
            "count": n_below,
            "percentage": round(n_below / n_total * 100, 2),
            "min_lpa": round(float(sal_df[below_mask]["salary_lpa"].min()), 2),
            "median_lpa": round(float(sal_df[below_mask]["salary_lpa"].median()), 2),
            "mean_lpa": round(float(sal_df[below_mask]["salary_lpa"].mean()), 2),
            "max_lpa": round(float(sal_df[below_mask]["salary_lpa"].max()), 2),
            "tech_count": int(sal_df[below_mask]["is_tech_role"].sum()),
            "nontech_count": int((~sal_df[below_mask]["is_tech_role"]).sum()),
            "top_roles": "; ".join([f"{k} ({v})" for k, v in sal_df[below_mask]["role_category"].value_counts().head(3).items()]),
            "action": "Exclude from ML (Stipends / sub-minimum-wage trainees)"
        },
        {
            "segment": f"Retained Core ({lower_lpa:.2f} - {upper_lpa:.2f} LPA)",
            "count": n_retained,
            "percentage": round(n_retained / n_total * 100, 2),
            "min_lpa": round(float(sal_df[bounded_mask]["salary_lpa"].min()), 2),
            "median_lpa": round(float(sal_df[bounded_mask]["salary_lpa"].median()), 2),
            "mean_lpa": round(float(sal_df[bounded_mask]["salary_lpa"].mean()), 2),
            "max_lpa": round(float(sal_df[bounded_mask]["salary_lpa"].max()), 2),
            "tech_count": int(sal_df[bounded_mask]["is_tech_role"].sum()),
            "nontech_count": int((~sal_df[bounded_mask]["is_tech_role"]).sum()),
            "top_roles": "; ".join([f"{k} ({v})" for k, v in sal_df[bounded_mask]["role_category"].value_counts().head(3).items()]),
            "action": "Retain for ML modeling"
        },
        {
            "segment": f"Upper Tail (> {upper_lpa:.2f} LPA)",
            "count": n_above,
            "percentage": round(n_above / n_total * 100, 2),
            "min_lpa": round(float(sal_df[above_mask]["salary_lpa"].min()), 2),
            "median_lpa": round(float(sal_df[above_mask]["salary_lpa"].median()), 2),
            "mean_lpa": round(float(sal_df[above_mask]["salary_lpa"].mean()), 2),
            "max_lpa": round(float(sal_df[above_mask]["salary_lpa"].max()), 2),
            "tech_count": int(sal_df[above_mask]["is_tech_role"].sum()),
            "nontech_count": int((~sal_df[above_mask]["is_tech_role"]).sum()),
            "top_roles": "; ".join([f"{k} ({v})" for k, v in sal_df[above_mask]["role_category"].value_counts().head(3).items()]),
            "action": "Exclude from ML (Recruiter Cr errors / non-tech C-suite)"
        }
    ]
    
    analysis_df = pd.DataFrame(bound_records)
    bounded_df = sal_df[bounded_mask].copy()
    return bounded_df, analysis_df

def compare_candidate_cohorts(sal_df: pd.DataFrame, bounded_df: pd.DataFrame) -> pd.DataFrame:
    """Evaluates Cohorts A, B, C, D across sample size, distributions, and coverage."""
    N_sal = len(sal_df)
    
    cA = sal_df.copy()
    cB = bounded_df.copy()
    cC = bounded_df[bounded_df["is_tech_role"]].copy()
    cD = cC[cC["experience_midpoint"].notnull() & cC["city"].notnull() & cC["tags_and_skills"].notnull()].copy()
    
    cohorts = [
        ("Cohort A: All Disclosed INR Salaries", cA),
        ("Cohort B: Bounded Disclosed INR (1.2-80 LPA)", cB),
        ("Cohort C: Bounded Tech Roles (1.2-80 LPA)", cC),
        ("Cohort D: Bounded Tech Roles with Complete Features", cD),
    ]
    
    rows = []
    for name, c_df in cohorts:
        n = len(c_df)
        pct = round(n / N_sal * 100, 2)
        med_sal = round(float(c_df["salary_lpa"].median()), 2)
        mean_sal = round(float(c_df["salary_lpa"].mean()), 2)
        q25 = float(c_df["salary_lpa"].quantile(0.25))
        q75 = float(c_df["salary_lpa"].quantile(0.75))
        iqr = round(q75 - q25, 2)
        n_roles = int(c_df["role_category"].nunique())
        n_cities = int(c_df["city"].nunique())
        exp_cov = round(float(c_df["experience_midpoint"].notnull().mean() * 100), 2)
        skill_cov = round(float(c_df["tags_and_skills"].notnull().mean() * 100), 2)
        overall_missing = round(float(c_df[["experience_midpoint", "city", "tags_and_skills"]].isnull().any(axis=1).mean() * 100), 2)
        n_companies = int(c_df["company_name"].nunique())
        
        skill_lens = c_df["tags_and_skills"].dropna().apply(lambda s: len([x for x in s.split(",") if x.strip()]))
        avg_skill_density = round(float(skill_lens.mean()), 2) if len(skill_lens) > 0 else 0.0
        skewness = round(float(stats.skew(c_df["salary_lpa"].dropna())), 2)
        
        top_role_pct = round(float(c_df["role_category"].value_counts(normalize=True).iloc[0] * 100), 2)
        top_role_name = c_df["role_category"].value_counts().index[0]
        
        rows.append({
            "cohort_name": name,
            "sample_size_N": n,
            "pct_of_valid_salaries": pct,
            "median_salary_lpa": med_sal,
            "mean_salary_lpa": mean_sal,
            "salary_iqr_lpa": iqr,
            "salary_skewness": skewness,
            "unique_roles": n_roles,
            "unique_cities": n_cities,
            "experience_coverage_pct": exp_cov,
            "skill_coverage_pct": skill_cov,
            "records_with_missing_features_pct": overall_missing,
            "unique_companies": n_companies,
            "avg_skills_per_job": avg_skill_density,
            "top_role_name": top_role_name,
            "top_role_share_pct": top_role_pct
        })
        
    return pd.DataFrame(rows)

def analyze_content_duplicates(df_cohort: pd.DataFrame) -> pd.DataFrame:
    """Analyzes duplicate content fingerprints to evaluate train/test leakage risk."""
    df_cohort = df_cohort.copy()
    df_cohort["content_fp"] = (
        df_cohort["original_title"].astype(str) + "||" +
        df_cohort["company_name"].astype(str) + "||" +
        df_cohort["original_location"].astype(str) + "||" +
        df_cohort["original_experience"].astype(str)
    )
    
    fp_counts = df_cohort["content_fp"].value_counts()
    dup_groups = fp_counts[fp_counts > 1]
    
    std_within = df_cohort.groupby("content_fp")["salary_lpa"].std().dropna()
    zero_var = (std_within == 0.0).sum()
    
    records = [
        {"metric": "Total Postings Evaluated", "value": len(df_cohort)},
        {"metric": "Unique Content Fingerprints", "value": len(fp_counts)},
        {"metric": "Unique Fingerprints with Size = 1 (Singletons)", "value": int((fp_counts == 1).sum())},
        {"metric": "Duplicate Fingerprint Groups (Size >= 2)", "value": len(dup_groups)},
        {"metric": "Total Records in Duplicate Groups", "value": int(dup_groups.sum())},
        {"metric": "Percentage of Records in Duplicate Groups", "value": round(dup_groups.sum() / len(df_cohort) * 100, 2)},
        {"metric": "Average Group Size (for Duplicates)", "value": round(float(dup_groups.mean()), 2) if len(dup_groups) > 0 else 0.0},
        {"metric": "Median Group Size (for Duplicates)", "value": float(dup_groups.median()) if len(dup_groups) > 0 else 0.0},
        {"metric": "Maximum Group Size", "value": int(dup_groups.max()) if len(dup_groups) > 0 else 0},
        {"metric": "Groups with Identical Salaries (Zero Variance)", "value": int(zero_var)},
        {"metric": "Pct Groups with Identical Salaries", "value": round(zero_var / len(std_within) * 100, 2) if len(std_within) > 0 else 0.0},
        {"metric": "Recommended Splitting Policy", "value": "GroupShuffleSplit on content_fp (80/20 train/test)"}
    ]
    return pd.DataFrame(records)

def run_cohort_isolation():
    """Runs full cohort isolation and generates tabular reports."""
    os.makedirs(OUTPUT_TABLES_DIR, exist_ok=True)
    print("Loading valid INR salary cohort...")
    sal_df = load_and_filter_salary_cohort()
    
    print("Evaluating salary bounds (₹1.20 - ₹80.00 LPA)...")
    bounded_df, bounds_analysis = evaluate_salary_bounds(sal_df)
    bounds_analysis.to_csv(os.path.join(OUTPUT_TABLES_DIR, "salary_bound_analysis.csv"), index=False)
    
    print("Comparing candidate cohorts...")
    cohort_comparison = compare_candidate_cohorts(sal_df, bounded_df)
    cohort_comparison.to_csv(os.path.join(OUTPUT_TABLES_DIR, "cohort_comparison.csv"), index=False)
    
    print("Analyzing content duplicate leakage on Tech Cohort (N = 5,859)...")
    tech_bounded = bounded_df[bounded_df["is_tech_role"]].copy()
    content_dup_analysis = analyze_content_duplicates(tech_bounded)
    content_dup_analysis.to_csv(os.path.join(OUTPUT_TABLES_DIR, "content_duplicate_analysis.csv"), index=False)
    
    print("Cohort isolation analysis complete. Tables exported to reports/tables/india/.")

if __name__ == "__main__":
    run_cohort_isolation()
