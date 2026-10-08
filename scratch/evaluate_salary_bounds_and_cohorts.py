"""
Evaluate salary bounds and compare candidate cohorts.
Generates data for:
- reports/tables/india/salary_bound_analysis.csv
- reports/tables/india/cohort_comparison.csv
"""
import pandas as pd
import numpy as np
from scipy import stats

postings_path = "data/processed/india/india_job_postings.parquet"
df = pd.read_parquet(postings_path)

# Restrict to valid INR salary records
sal_df = df[df["is_salary_valid"] & (df["currency"] == "INR")].copy()
N_sal = len(sal_df)
print(f"Valid INR salary cohort N = {N_sal:,}")

# 1. Salary Bounds Analysis: ₹1.20 LPA to ₹80.00 LPA
below_mask = sal_df["salary_lpa"] < 1.20
above_mask = sal_df["salary_lpa"] > 80.00
bounded_mask = (~below_mask) & (~above_mask)

n_below = int(below_mask.sum())
pct_below = round(n_below / N_sal * 100, 2)
n_above = int(above_mask.sum())
pct_above = round(n_above / N_sal * 100, 2)
n_retained = int(bounded_mask.sum())
pct_retained = round(n_retained / N_sal * 100, 2)

print(f"Below INR 1.20 LPA: {n_below:,} ({pct_below}%)")
print(f"Above INR 80.00 LPA: {n_above:,} ({pct_above}%)")
print(f"Retained (INR 1.20 - 80.00 LPA): {n_retained:,} ({pct_retained}%)")

# Detailed metrics for bounds table
bound_analysis = [
    {
        "segment": "Lower Tail (< 1.20 LPA)",
        "count": n_below,
        "percentage": pct_below,
        "min_lpa": round(sal_df[below_mask]["salary_lpa"].min(), 2),
        "median_lpa": round(sal_df[below_mask]["salary_lpa"].median(), 2),
        "mean_lpa": round(sal_df[below_mask]["salary_lpa"].mean(), 2),
        "max_lpa": round(sal_df[below_mask]["salary_lpa"].max(), 2),
        "tech_count": int(sal_df[below_mask]["is_tech_role"].sum()),
        "nontech_count": int((~sal_df[below_mask]["is_tech_role"]).sum()),
        "top_roles": "; ".join([f"{k} ({v})" for k, v in sal_df[below_mask]["role_category"].value_counts().head(3).items()]),
        "action": "Exclude from ML (Stipends/non-target employment)"
    },
    {
        "segment": "Retained Core (1.20 - 80.00 LPA)",
        "count": n_retained,
        "percentage": pct_retained,
        "min_lpa": round(sal_df[bounded_mask]["salary_lpa"].min(), 2),
        "median_lpa": round(sal_df[bounded_mask]["salary_lpa"].median(), 2),
        "mean_lpa": round(sal_df[bounded_mask]["salary_lpa"].mean(), 2),
        "max_lpa": round(sal_df[bounded_mask]["salary_lpa"].max(), 2),
        "tech_count": int(sal_df[bounded_mask]["is_tech_role"].sum()),
        "nontech_count": int((~sal_df[bounded_mask]["is_tech_role"]).sum()),
        "top_roles": "; ".join([f"{k} ({v})" for k, v in sal_df[bounded_mask]["role_category"].value_counts().head(3).items()]),
        "action": "Retain for ML modeling"
    },
    {
        "segment": "Upper Tail (> 80.00 LPA)",
        "count": n_above,
        "percentage": pct_above,
        "min_lpa": round(sal_df[above_mask]["salary_lpa"].min(), 2),
        "median_lpa": round(sal_df[above_mask]["salary_lpa"].median(), 2),
        "mean_lpa": round(sal_df[above_mask]["salary_lpa"].mean(), 2),
        "max_lpa": round(sal_df[above_mask]["salary_lpa"].max(), 2),
        "tech_count": int(sal_df[above_mask]["is_tech_role"].sum()),
        "nontech_count": int((~sal_df[above_mask]["is_tech_role"]).sum()),
        "top_roles": "; ".join([f"{k} ({v})" for k, v in sal_df[above_mask]["role_category"].value_counts().head(3).items()]),
        "action": "Exclude from ML (Recruiter errors / C-suite non-tech)"
    }
]
pd.DataFrame(bound_analysis).to_csv("reports/tables/india/salary_bound_analysis.csv", index=False)
print("Saved reports/tables/india/salary_bound_analysis.csv.")

# 2. Candidate Cohorts Comparison
# Cohort A: All valid INR salary records
cA = sal_df.copy()

# Cohort B: Valid INR salary + ₹1.20 - ₹80.00 LPA
cB = sal_df[bounded_mask].copy()

# Cohort C: Tech-role + valid INR salary + ₹1.20 - ₹80.00 LPA
cC = sal_df[bounded_mask & sal_df["is_tech_role"]].copy()

# Cohort D: Tech-role + valid INR salary + ₹1.20 - ₹80.00 LPA + sufficient feature coverage (has exp, has city, has skills)
cD = cC[cC["experience_midpoint"].notnull() & cC["city"].notnull() & cC["tags_and_skills"].notnull()].copy()

cohorts = [
    ("Cohort A: All Disclosed INR Salaries", cA),
    ("Cohort B: Bounded Disclosed INR (1.2-80 LPA)", cB),
    ("Cohort C: Bounded Tech Roles (1.2-80 LPA)", cC),
    ("Cohort D: Bounded Tech Roles with Complete Features", cD),
]

cohort_rows = []
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
    
    # Skill density (average tokens in tags_and_skills)
    skill_lens = c_df["tags_and_skills"].dropna().apply(lambda s: len([x for x in s.split(",") if x.strip()]))
    avg_skill_density = round(float(skill_lens.mean()), 2) if len(skill_lens) > 0 else 0.0
    
    skewness = round(float(stats.skew(c_df["salary_lpa"].dropna())), 2)
    
    # Role imbalance: Herfindahl-Hirschman Index (HHI) or top role %
    top_role_pct = round(float(c_df["role_category"].value_counts(normalize=True).iloc[0] * 100), 2)
    top_role_name = c_df["role_category"].value_counts().index[0]
    
    cohort_rows.append({
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

pd.DataFrame(cohort_rows).to_csv("reports/tables/india/cohort_comparison.csv", index=False)
print("Saved reports/tables/india/cohort_comparison.csv.")
