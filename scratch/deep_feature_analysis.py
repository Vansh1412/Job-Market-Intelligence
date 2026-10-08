"""
Deep analysis of City, Work Mode, Content Duplicates, Skills, and Target Transformation.
"""
import pandas as pd
import numpy as np
import json
import re
from scipy import stats

postings_path = "data/processed/india/india_job_postings.parquet"
skills_path = "data/processed/india/india_job_skills.parquet"

df = pd.read_parquet(postings_path)
skills_df = pd.read_parquet(skills_path)

sal_df = df[df["is_salary_valid"] & (df["currency"] == "INR")].copy()
bounded_sal = sal_df[(sal_df["salary_lpa"] >= 1.20) & (sal_df["salary_lpa"] <= 80.00)].copy()
tech_sal = bounded_sal[bounded_sal["is_tech_role"]].copy()

print(f"Bounded All Sal: {len(bounded_sal):,}, Bounded Tech Sal: {len(tech_sal):,}")

# ==============================================================================
# 1. CITY FEATURE COVERAGE
# ==============================================================================
print("\n--- CITY COVERAGE ANALYSIS ---")
city_counts_all = bounded_sal["city"].value_counts()
city_counts_tech = tech_sal["city"].value_counts()

print(f"Total unique cities in Bounded All: {len(city_counts_all)}")
print(f"Total unique cities in Tech: {len(city_counts_tech)}")

# Test thresholds for grouping rare cities into "Other"
thresholds = [10, 20, 30, 50, 100]
city_cov_rows = []
for th in thresholds:
    # For tech cohort
    retained_tech_cities = city_counts_tech[city_counts_tech >= th].index
    cov_tech = tech_sal["city"].isin(retained_tech_cities).mean() * 100
    
    # For all bounded
    retained_all_cities = city_counts_all[city_counts_all >= th].index
    cov_all = bounded_sal["city"].isin(retained_all_cities).mean() * 100
    
    city_cov_rows.append({
        "threshold_min_jobs": th,
        "tech_retained_cities": len(retained_tech_cities),
        "tech_coverage_pct": round(cov_tech, 2),
        "tech_other_count": int((~tech_sal["city"].isin(retained_tech_cities)).sum()),
        "all_retained_cities": len(retained_all_cities),
        "all_coverage_pct": round(cov_all, 2),
        "all_other_count": int((~bounded_sal["city"].isin(retained_all_cities)).sum())
    })

city_cov_df = pd.DataFrame(city_cov_rows)
print(city_cov_df)
city_cov_df.to_csv("reports/tables/india/city_feature_coverage.csv", index=False)
print("Saved reports/tables/india/city_feature_coverage.csv")

# ==============================================================================
# 2. WORK MODE / REMOTE ANALYSIS
# ==============================================================================
print("\n--- WORK MODE ANALYSIS ---")
def extract_work_mode(loc_str):
    s = str(loc_str).lower().strip()
    if "remote" in s or "work from home" in s or "wfh" in s:
        return "Remote"
    elif "hybrid" in s:
        return "Hybrid"
    else:
        return "Onsite"

bounded_sal["work_mode"] = bounded_sal["original_location"].apply(extract_work_mode)
tech_sal["work_mode"] = tech_sal["original_location"].apply(extract_work_mode)

print("Tech cohort work mode breakdown:")
wm_gb = tech_sal.groupby("work_mode")["salary_lpa"].agg(["count", "mean", "median", "std"])
wm_gb["pct"] = (wm_gb["count"] / len(tech_sal) * 100).round(2)
print(wm_gb)

# ==============================================================================
# 3. CONTENT DUPLICATE / LEAKAGE ANALYSIS
# ==============================================================================
print("\n--- CONTENT DUPLICATE ANALYSIS ---")
# Content fingerprint: (title, company_name, location, experience)
# Let's inspect content duplicates in bounded salary cohort
bounded_sal["content_fp"] = (
    bounded_sal["original_title"].astype(str) + "||" +
    bounded_sal["company_name"].astype(str) + "||" +
    bounded_sal["original_location"].astype(str) + "||" +
    bounded_sal["original_experience"].astype(str)
)

fp_counts = bounded_sal["content_fp"].value_counts()
dup_groups = fp_counts[fp_counts > 1]
print(f"Total content groups: {len(fp_counts):,}")
print(f"Duplicate content groups (size > 1): {len(dup_groups):,}")
print(f"Rows in duplicate groups: {dup_groups.sum():,} ({dup_groups.sum()/len(bounded_sal)*100:.2f}%)")
print(f"Max group size: {dup_groups.max()}")

# Inspect salary variation within duplicate groups
std_within_groups = bounded_sal.groupby("content_fp")["salary_lpa"].std().dropna()
zero_var_groups = (std_within_groups == 0.0).sum()
print(f"Groups with 0 salary variance: {zero_var_groups:,} / {len(std_within_groups):,} ({zero_var_groups/len(std_within_groups)*100:.1f}%)")

# Content duplicate metrics table
dup_analysis_rows = [
    {"metric": "Total Postings Evaluated", "value": len(bounded_sal)},
    {"metric": "Unique Content Fingerprints", "value": len(fp_counts)},
    {"metric": "Unique Fingerprints with Size = 1 (Singletons)", "value": int((fp_counts == 1).sum())},
    {"metric": "Duplicate Fingerprint Groups (Size >= 2)", "value": len(dup_groups)},
    {"metric": "Total Records in Duplicate Groups", "value": int(dup_groups.sum())},
    {"metric": "Percentage of Records in Duplicate Groups", "value": round(dup_groups.sum()/len(bounded_sal)*100, 2)},
    {"metric": "Average Group Size (for Duplicates)", "value": round(float(dup_groups.mean()), 2)},
    {"metric": "Median Group Size (for Duplicates)", "value": float(dup_groups.median())},
    {"metric": "Maximum Group Size", "value": int(dup_groups.max())},
    {"metric": "Groups with Identical Salaries (Zero Variance)", "value": int(zero_var_groups)},
    {"metric": "Pct Groups with Identical Salaries", "value": round(zero_var_groups/len(std_within_groups)*100, 2) if len(std_within_groups)>0 else 0.0},
    {"metric": "Recommended Splitting Policy", "value": "GroupKFold / GroupShuffleSplit on content_fp"}
]
pd.DataFrame(dup_analysis_rows).to_csv("reports/tables/india/content_duplicate_analysis.csv", index=False)
print("Saved reports/tables/india/content_duplicate_analysis.csv")

# ==============================================================================
# 4. TARGET SKEWNESS & LOG TRANSFORMATION
# ==============================================================================
print("\n--- TARGET SKEWNESS ANALYSIS ---")
for c_name, c_data in [("Bounded All Sal", bounded_sal), ("Bounded Tech Sal", tech_sal)]:
    raw_s = c_data["salary_midpoint_inr"]
    raw_skew = stats.skew(raw_s)
    log_s = np.log1p(raw_s)
    log_skew = stats.skew(log_s)
    print(f"{c_name}:")
    print(f"  Raw Target Skewness: {raw_skew:.3f}")
    print(f"  Log1p Target Skewness: {log_skew:.3f}")
