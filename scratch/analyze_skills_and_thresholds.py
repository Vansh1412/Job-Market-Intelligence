"""
Comprehensive Skill Frequency Analysis and Threshold Comparison.
Generates:
- reports/tables/india/skill_frequency_analysis.csv
- reports/tables/india/skill_threshold_comparison.csv
"""
import pandas as pd
import numpy as np

postings_path = "data/processed/india/india_job_postings.parquet"
skills_path = "data/processed/india/india_job_skills.parquet"

postings_df = pd.read_parquet(postings_path)
skills_df = pd.read_parquet(skills_path)

# Merge skills with postings metadata
merged_skills = pd.merge(
    skills_df,
    postings_df[["job_id", "is_salary_valid", "salary_lpa", "is_tech_role", "role_category"]],
    on="job_id",
    how="inner"
)

# 1. Skill frequency analysis on the entire analytical corpus (N = 97,679)
# and on the salary-bearing tech cohort (N = 5,859)
print("Computing skill frequencies...")
total_jobs = postings_df["job_id"].nunique()

skill_counts = merged_skills["skill"].value_counts()
skill_sal_counts = merged_skills[merged_skills["is_salary_valid"]]["skill"].value_counts()

# Groupby skill to get statistics
gb_sal = merged_skills[merged_skills["is_salary_valid"]].groupby("skill")["salary_lpa"].agg(
    salary_obs="count",
    median_salary_lpa="median",
    mean_salary_lpa="mean"
)

# Role distribution per skill: find top associated role
role_mode = merged_skills.groupby(["skill", "role_category"]).size().reset_index(name="count")
top_roles = role_mode.sort_values(["skill", "count"], ascending=[True, False]).drop_duplicates(subset=["skill"])
top_role_dict = dict(zip(top_roles["skill"], top_roles["role_category"]))

skill_analysis_records = []
for skill, doc_freq in skill_counts.head(500).items():
    pct_jobs = round(doc_freq / total_jobs * 100, 2)
    sal_n = int(gb_sal.loc[skill, "salary_obs"]) if skill in gb_sal.index else 0
    med_sal = round(float(gb_sal.loc[skill, "median_salary_lpa"]), 2) if skill in gb_sal.index else np.nan
    mean_sal = round(float(gb_sal.loc[skill, "mean_salary_lpa"]), 2) if skill in gb_sal.index else np.nan
    top_r = top_role_dict.get(skill, "Unknown")
    
    skill_analysis_records.append({
        "skill": skill,
        "document_frequency": int(doc_freq),
        "pct_of_all_jobs": pct_jobs,
        "salary_sample_size": sal_n,
        "median_salary_lpa": med_sal,
        "mean_salary_lpa": mean_sal,
        "primary_associated_role": top_r
    })

skill_analysis_df = pd.DataFrame(skill_analysis_records)
skill_analysis_df.to_csv("reports/tables/india/skill_frequency_analysis.csv", index=False)
print(f"Saved reports/tables/india/skill_frequency_analysis.csv ({len(skill_analysis_df)} skills).")

# 2. Skill Threshold Comparison
# Evaluate thresholds on Tech Bounded Cohort (N = 5,859) and All Bounded Cohort (N = 32,490)
bounded_sal = postings_df[(postings_df["is_salary_valid"]) & (postings_df["salary_lpa"] >= 1.20) & (postings_df["salary_lpa"] <= 80.00)]
tech_sal = bounded_sal[bounded_sal["is_tech_role"]]

tech_job_ids = set(tech_sal["job_id"])
tech_skills = skills_df[skills_df["job_id"].isin(tech_job_ids)]
tech_skill_counts = tech_skills["skill"].value_counts()
N_tech_jobs = len(tech_job_ids)

all_job_ids = set(bounded_sal["job_id"])
all_skills = skills_df[skills_df["job_id"].isin(all_job_ids)]
all_skill_counts = all_skills["skill"].value_counts()
N_all_jobs = len(all_job_ids)

thresholds = [10, 25, 50, 100, 250]
threshold_rows = []

for th in thresholds:
    # Tech cohort evaluation
    qual_tech_skills = set(tech_skill_counts[tech_skill_counts >= th].index)
    k_tech = len(qual_tech_skills)
    sub_tech_skills = tech_skills[tech_skills["skill"].isin(qual_tech_skills)]
    covered_tech_jobs = sub_tech_skills["job_id"].nunique()
    pct_cov_tech = round(covered_tech_jobs / N_tech_jobs * 100, 2)
    skills_per_tech_job = sub_tech_skills.groupby("job_id").size()
    med_skills_tech = float(skills_per_tech_job.median()) if len(skills_per_tech_job) > 0 else 0.0
    mean_skills_tech = round(float(skills_per_tech_job.mean()), 2) if len(skills_per_tech_job) > 0 else 0.0
    sparsity_tech = round((1.0 - (len(sub_tech_skills) / (N_tech_jobs * k_tech if k_tech else 1))) * 100, 2)
    
    # All bounded cohort evaluation
    qual_all_skills = set(all_skill_counts[all_skill_counts >= th].index)
    k_all = len(qual_all_skills)
    sub_all_skills = all_skills[all_skills["skill"].isin(qual_all_skills)]
    covered_all_jobs = sub_all_skills["job_id"].nunique()
    pct_cov_all = round(covered_all_jobs / N_all_jobs * 100, 2)
    sparsity_all = round((1.0 - (len(sub_all_skills) / (N_all_jobs * k_all if k_all else 1))) * 100, 2)

    threshold_rows.append({
        "threshold_min_jobs": th,
        "tech_retained_skills_count": k_tech,
        "tech_jobs_covered": covered_tech_jobs,
        "tech_job_coverage_pct": pct_cov_tech,
        "tech_median_skills_per_job": med_skills_tech,
        "tech_mean_skills_per_job": mean_skills_tech,
        "tech_feature_sparsity_pct": sparsity_tech,
        "all_retained_skills_count": k_all,
        "all_job_coverage_pct": pct_cov_all,
        "all_feature_sparsity_pct": sparsity_all
    })

threshold_df = pd.DataFrame(threshold_rows)
print("\n--- SKILL THRESHOLD COMPARISON ---")
print(threshold_df)
threshold_df.to_csv("reports/tables/india/skill_threshold_comparison.csv", index=False)
print("Saved reports/tables/india/skill_threshold_comparison.csv.")
