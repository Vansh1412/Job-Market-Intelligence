"""
Comprehensive Audit Script for Indian Job Market Dataset (2025)
Author: JobIntel / Antigravity
"""

import sys
import os
import json
import numpy as np
import pandas as pd

DATA_PATH = "data/raw/india/indian-job-market-dataset-2025.xlsx"

def run_audit():
    print(f"Loading {DATA_PATH}...")
    df = pd.read_excel(DATA_PATH)
    n_rows, n_cols = df.shape
    print(f"Loaded {n_rows:,} rows and {n_cols} columns.")

    results = {}
    results["dimensions"] = {"rows": n_rows, "cols": n_cols}
    results["columns"] = df.columns.tolist()

    # 1. Column Info & Missingness
    col_info = {}
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_pct = round(null_count / n_rows * 100, 2)
        dtype = str(df[col].dtype)
        col_info[col] = {
            "dtype": dtype,
            "null_count": null_count,
            "null_pct": null_pct,
            "non_null_count": n_rows - null_count,
            "non_null_pct": round(100 - null_pct, 2),
            "unique_count": int(df[col].nunique(dropna=True))
        }
    results["column_info"] = col_info

    # 2. Duplication Audit
    exact_dups = int(df.duplicated().sum())
    jobid_dups = int(df.duplicated(subset=["jobId"]).sum()) if "jobId" in df.columns else 0
    content_dups = int(df.duplicated(subset=["title", "companyName", "location", "salary", "experience"]).sum())
    results["duplicates"] = {
        "exact_duplicates": exact_dups,
        "jobId_duplicates": jobid_dups,
        "content_duplicates": content_dups
    }

    # 3. Currency
    curr_dist = df["currency"].value_counts(dropna=False).to_dict()
    # convert keys to str
    results["currency_distribution"] = {str(k): int(v) for k, v in curr_dist.items()}

    # 4. Salary Audit
    # Analyze text 'salary' column
    salary_text_nonnull = int(df["salary"].notnull().sum())
    top_salary_strings = df["salary"].value_counts().head(20).to_dict()

    # Analyze numeric minimumSalary and maximumSalary
    min_sal = pd.to_numeric(df["minimumSalary"], errors="coerce")
    max_sal = pd.to_numeric(df["maximumSalary"], errors="coerce")

    both_sal_present = int((min_sal.notnull() & max_sal.notnull()).sum())
    only_min_present = int((min_sal.notnull() & max_sal.isnull()).sum())
    only_max_present = int((min_sal.isnull() & max_sal.notnull()).sum())
    neither_sal_present = int((min_sal.isnull() & max_sal.isnull()).sum())

    # Salary anomalies
    zero_min = int((min_sal == 0).sum())
    zero_max = int((max_sal == 0).sum())
    neg_min = int((min_sal < 0).sum())
    neg_max = int((max_sal < 0).sum())
    min_gt_max = int((min_sal > max_sal).sum())

    # Range stats for non-null salaries
    valid_sal_mask = min_sal.notnull() & max_sal.notnull() & (min_sal > 0) & (max_sal >= min_sal)
    valid_sal_df = df[valid_sal_mask].copy()
    valid_sal_df["min_sal_num"] = min_sal[valid_sal_mask]
    valid_sal_df["max_sal_num"] = max_sal[valid_sal_mask]
    valid_sal_df["midpoint_inr"] = (valid_sal_df["min_sal_num"] + valid_sal_df["max_sal_num"]) / 2
    valid_sal_df["midpoint_lpa"] = valid_sal_df["midpoint_inr"] / 100000

    sal_stats = {
        "salary_text_nonnull": salary_text_nonnull,
        "salary_text_nonnull_pct": round(salary_text_nonnull / n_rows * 100, 2),
        "both_numeric_present": both_sal_present,
        "both_numeric_present_pct": round(both_sal_present / n_rows * 100, 2),
        "only_min_present": only_min_present,
        "only_max_present": only_max_present,
        "neither_present": neither_sal_present,
        "zero_min": zero_min,
        "zero_max": zero_max,
        "negative_min": neg_min,
        "negative_max": neg_max,
        "min_greater_than_max": min_gt_max,
        "valid_positive_ranges": int(valid_sal_mask.sum()),
        "valid_positive_ranges_pct": round(int(valid_sal_mask.sum()) / n_rows * 100, 2),
    }

    if len(valid_sal_df) > 0:
        sal_stats["min_salary_quantiles"] = {
            "min": float(valid_sal_df["min_sal_num"].min()),
            "p1": float(valid_sal_df["min_sal_num"].quantile(0.01)),
            "p5": float(valid_sal_df["min_sal_num"].quantile(0.05)),
            "p25": float(valid_sal_df["min_sal_num"].quantile(0.25)),
            "median": float(valid_sal_df["min_sal_num"].median()),
            "p75": float(valid_sal_df["min_sal_num"].quantile(0.75)),
            "p95": float(valid_sal_df["min_sal_num"].quantile(0.95)),
            "p99": float(valid_sal_df["min_sal_num"].quantile(0.99)),
            "max": float(valid_sal_df["min_sal_num"].max()),
            "mean": float(valid_sal_df["min_sal_num"].mean()),
            "std": float(valid_sal_df["min_sal_num"].std())
        }
        sal_stats["max_salary_quantiles"] = {
            "min": float(valid_sal_df["max_sal_num"].min()),
            "p25": float(valid_sal_df["max_sal_num"].quantile(0.25)),
            "median": float(valid_sal_df["max_sal_num"].median()),
            "p75": float(valid_sal_df["max_sal_num"].quantile(0.75)),
            "max": float(valid_sal_df["max_sal_num"].max()),
        }
        sal_stats["midpoint_inr_quantiles"] = {
            "min": float(valid_sal_df["midpoint_inr"].min()),
            "p25": float(valid_sal_df["midpoint_inr"].quantile(0.25)),
            "median": float(valid_sal_df["midpoint_inr"].median()),
            "p75": float(valid_sal_df["midpoint_inr"].quantile(0.75)),
            "max": float(valid_sal_df["midpoint_inr"].max()),
            "mean": float(valid_sal_df["midpoint_inr"].mean()),
        }
        sal_stats["midpoint_lpa_quantiles"] = {
            "min": float(valid_sal_df["midpoint_lpa"].min()),
            "p25": float(valid_sal_df["midpoint_lpa"].quantile(0.25)),
            "median": float(valid_sal_df["midpoint_lpa"].median()),
            "p75": float(valid_sal_df["midpoint_lpa"].quantile(0.75)),
            "max": float(valid_sal_df["midpoint_lpa"].max()),
            "mean": float(valid_sal_df["midpoint_lpa"].mean()),
        }
        # Outlier counts
        sal_stats["under_50k_inr"] = int((valid_sal_df["midpoint_inr"] < 50000).sum())
        sal_stats["under_1_lpa"] = int((valid_sal_df["midpoint_lpa"] < 1.0).sum())
        sal_stats["over_50_lpa"] = int((valid_sal_df["midpoint_lpa"] > 50.0).sum())
        sal_stats["over_100_lpa"] = int((valid_sal_df["midpoint_lpa"] > 100.0).sum())

    results["salary_analysis"] = sal_stats
    results["top_salary_strings"] = {str(k): int(v) for k, v in top_salary_strings.items()}

    # 5. Experience Audit
    min_exp = pd.to_numeric(df["minimumExperience"], errors="coerce")
    max_exp = pd.to_numeric(df["maximumExperience"], errors="coerce")

    exp_both = int((min_exp.notnull() & max_exp.notnull()).sum())
    exp_min_gt_max = int((min_exp > max_exp).sum())
    valid_exp_mask = min_exp.notnull() & max_exp.notnull() & (min_exp >= 0) & (max_exp >= min_exp)

    results["experience_analysis"] = {
        "text_nonnull": int(df["experience"].notnull().sum()),
        "text_nonnull_pct": round(int(df["experience"].notnull().sum()) / n_rows * 100, 2),
        "both_numeric_present": exp_both,
        "both_numeric_present_pct": round(exp_both / n_rows * 100, 2),
        "min_gt_max": exp_min_gt_max,
        "valid_exp_count": int(valid_exp_mask.sum()),
        "valid_exp_pct": round(int(valid_exp_mask.sum()) / n_rows * 100, 2),
        "min_exp_distribution": {
            "min": float(min_exp.min()) if min_exp.notnull().any() else 0,
            "p25": float(min_exp.quantile(0.25)) if min_exp.notnull().any() else 0,
            "median": float(min_exp.median()) if min_exp.notnull().any() else 0,
            "p75": float(min_exp.quantile(0.75)) if min_exp.notnull().any() else 0,
            "max": float(min_exp.max()) if min_exp.notnull().any() else 0,
        },
        "max_exp_distribution": {
            "min": float(max_exp.min()) if max_exp.notnull().any() else 0,
            "median": float(max_exp.median()) if max_exp.notnull().any() else 0,
            "max": float(max_exp.max()) if max_exp.notnull().any() else 0,
        },
        "exp_over_30_yrs": int((max_exp > 30).sum())
    }

    # 6. Location Audit
    loc_nonnull = int(df["location"].notnull().sum())
    top_locations = df["location"].value_counts().head(25).to_dict()
    results["location_analysis"] = {
        "nonnull_count": loc_nonnull,
        "nonnull_pct": round(loc_nonnull / n_rows * 100, 2),
        "unique_locations": int(df["location"].nunique()),
        "top_locations": {str(k): int(v) for k, v in top_locations.items()}
    }

    # 7. Skills Audit
    skills_nonnull = int(df["tagsAndSkills"].notnull().sum())
    skill_series = df["tagsAndSkills"].dropna().astype(str)
    
    # Parse comma separated skills
    all_skills = []
    skill_counts_per_job = []
    for s in skill_series:
        tokens = [t.strip().lower() for t in s.split(",") if t.strip()]
        skill_counts_per_job.append(len(tokens))
        all_skills.extend(tokens)
    
    skill_freq = pd.Series(all_skills).value_counts()
    
    results["skills_analysis"] = {
        "nonnull_count": skills_nonnull,
        "nonnull_pct": round(skills_nonnull / n_rows * 100, 2),
        "total_skill_instances": len(all_skills),
        "unique_skill_tokens": len(skill_freq),
        "avg_skills_per_job": round(float(np.mean(skill_counts_per_job)), 2) if skill_counts_per_job else 0,
        "median_skills_per_job": float(np.median(skill_counts_per_job)) if skill_counts_per_job else 0,
        "top_30_skills": {str(k): int(v) for k, v in skill_freq.head(30).items()}
    }

    # 8. Title / Role Domain Audit
    title_nonnull = int(df["title"].notnull().sum())
    top_titles = df["title"].value_counts().head(30).to_dict()

    # Identify tech keywords in titles
    tech_keywords = [
        "developer", "engineer", "software", "data", "analyst", "analytics",
        "python", "java", "frontend", "backend", "full stack", "cloud", "devops",
        "machine learning", "ai", "scientist", "architect", "database", "sql",
        "react", "node", "angular", "qa", "tester", "test", "security", "network",
        "sysadmin", "infrastructure", "programmer", "web", "bi", "tableau", "power bi"
    ]
    title_lower = df["title"].dropna().astype(str).str.lower()
    tech_title_mask = title_lower.apply(lambda t: any(k in t for k in tech_keywords))
    tech_title_count = int(tech_title_mask.sum())

    results["title_analysis"] = {
        "nonnull_count": title_nonnull,
        "nonnull_pct": round(title_nonnull / n_rows * 100, 2),
        "unique_titles": int(df["title"].nunique()),
        "top_30_titles": {str(k): int(v) for k, v in top_titles.items()},
        "tech_keyword_title_count": tech_title_count,
        "tech_keyword_title_pct": round(tech_title_count / title_nonnull * 100, 2) if title_nonnull else 0
    }

    # 9. Company Audit
    comp_nonnull = int(df["companyName"].notnull().sum())
    top_comps = df["companyName"].value_counts().head(20).to_dict()
    results["company_analysis"] = {
        "nonnull_count": comp_nonnull,
        "nonnull_pct": round(comp_nonnull / n_rows * 100, 2),
        "unique_companies": int(df["companyName"].nunique()),
        "top_20_companies": {str(k): int(v) for k, v in top_comps.items()}
    }

    # 10. Funnel Breakdown
    # Let's see how many rows pass each filter:
    # F0: Raw
    f0 = n_rows
    # F1: De-duplicated by jobId
    f1 = int(df.drop_duplicates(subset=["jobId"]).shape[0])
    # F2: Has positive salary range
    f2_df = df.drop_duplicates(subset=["jobId"])
    f2_mask = (pd.to_numeric(f2_df["minimumSalary"], errors="coerce") > 0) & \
              (pd.to_numeric(f2_df["maximumSalary"], errors="coerce") >= pd.to_numeric(f2_df["minimumSalary"], errors="coerce"))
    f2 = int(f2_mask.sum())
    # F3: Currency is INR
    f3_mask = f2_mask & (f2_df["currency"].astype(str).str.upper() == "INR")
    f3 = int(f3_mask.sum())
    # F4: Has valid experience
    min_e = pd.to_numeric(f2_df["minimumExperience"], errors="coerce")
    max_e = pd.to_numeric(f2_df["maximumExperience"], errors="coerce")
    f4_mask = f3_mask & min_e.notnull() & max_e.notnull() & (min_e >= 0) & (max_e >= min_e) & (max_e <= 35)
    f4 = int(f4_mask.sum())
    # F5: Has skills
    f5_mask = f4_mask & f2_df["tagsAndSkills"].notnull()
    f5 = int(f5_mask.sum())
    # F6: Tech-domain title or tech skills
    # Let's see how many of F5 have tech titles or tech skills
    f5_df = f2_df[f5_mask]
    t_lower = f5_df["title"].astype(str).str.lower()
    is_tech_title = t_lower.apply(lambda t: any(k in t for k in tech_keywords))
    f6_tech_title = int(is_tech_title.sum())

    results["funnel"] = {
        "raw_rows": f0,
        "unique_jobid_rows": f1,
        "valid_positive_salary": f2,
        "inr_currency": f3,
        "valid_experience": f4,
        "has_skills": f5,
        "tech_title_subset": f6_tech_title
    }

    # Save results to json
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/india_audit_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("Audit finished successfully. Saved scratch/india_audit_summary.json.")
    return results

if __name__ == "__main__":
    run_audit()
