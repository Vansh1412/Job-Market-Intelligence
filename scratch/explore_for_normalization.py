"""
Exploratory script to examine titles, locations, skills, and salaries for normalization.
"""
import pandas as pd
import numpy as np
import re
from collections import Counter

DATA_PATH = "data/raw/india/indian-job-market-dataset-2025.xlsx"

print("Reading Excel...")
df = pd.read_excel(DATA_PATH)
print(f"Loaded {len(df):,} rows.")

# 1. Salary investigation
print("\n--- SALARY DISTRIBUTION ---")
min_sal = pd.to_numeric(df["minimumSalary"], errors="coerce")
max_sal = pd.to_numeric(df["maximumSalary"], errors="coerce")
is_inr = df["currency"] == "INR"
valid_sal_mask = is_inr & min_sal.notnull() & max_sal.notnull() & (min_sal > 0) & (max_sal >= min_sal)

sal_df = df[valid_sal_mask].copy()
sal_df["midpoint_inr"] = (min_sal[valid_sal_mask] + max_sal[valid_sal_mask]) / 2.0
sal_df["salary_lpa"] = sal_df["midpoint_inr"] / 100000.0

print(f"Valid INR salary rows: {len(sal_df):,}")
percentiles = [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.5, 99.9, 100]
pct_vals = np.percentile(sal_df["salary_lpa"], percentiles)
for p, v in zip(percentiles, pct_vals):
    inr_v = v * 100000
    print(f"P{p:5.1f} | INR {inr_v:12,.0f} | LPA {v:8.2f}")

# Salary bands
bands = [
    ("<1 LPA", sal_df["salary_lpa"] < 1.0),
    ("1-2 LPA", (sal_df["salary_lpa"] >= 1.0) & (sal_df["salary_lpa"] < 2.0)),
    ("2-3 LPA", (sal_df["salary_lpa"] >= 2.0) & (sal_df["salary_lpa"] < 3.0)),
    ("3-5 LPA", (sal_df["salary_lpa"] >= 3.0) & (sal_df["salary_lpa"] < 5.0)),
    ("5-10 LPA", (sal_df["salary_lpa"] >= 5.0) & (sal_df["salary_lpa"] < 10.0)),
    ("10-20 LPA", (sal_df["salary_lpa"] >= 10.0) & (sal_df["salary_lpa"] < 20.0)),
    ("20-30 LPA", (sal_df["salary_lpa"] >= 20.0) & (sal_df["salary_lpa"] < 30.0)),
    ("30-50 LPA", (sal_df["salary_lpa"] >= 30.0) & (sal_df["salary_lpa"] < 50.0)),
    ("50-80 LPA", (sal_df["salary_lpa"] >= 50.0) & (sal_df["salary_lpa"] < 80.0)),
    ("80-100 LPA", (sal_df["salary_lpa"] >= 80.0) & (sal_df["salary_lpa"] < 100.0)),
    (">100 LPA", sal_df["salary_lpa"] >= 100.0),
]
print("\n--- SALARY BANDS ---")
for b_name, mask in bands:
    cnt = mask.sum()
    pct = cnt / len(sal_df) * 100
    print(f"{b_name:12s}: {cnt:6,d} ({pct:5.2f}%)")

# Inspect extreme lower tail (<1 LPA)
print("\n--- LOWER TAIL SAMPLES (< 1 LPA) ---")
low_tail = sal_df[sal_df["salary_lpa"] < 1.0][["jobId", "title", "companyName", "experience", "salary", "salary_lpa", "tagsAndSkills"]].head(10)
print(low_tail.to_string())

# Inspect extreme upper tail (> 50 LPA)
print("\n--- UPPER TAIL SAMPLES (> 50 LPA) ---")
high_tail = sal_df[sal_df["salary_lpa"] > 50.0][["jobId", "title", "companyName", "experience", "salary", "salary_lpa", "tagsAndSkills"]].head(10)
print(high_tail.to_string())

# 2. Location inspection
print("\n--- TOP RAW LOCATIONS ---")
top_locs = df["location"].value_counts().head(30)
print(top_locs)

# 3. Titles inspection
print("\n--- TOP RAW TITLES ---")
top_titles = df["title"].value_counts().head(30)
print(top_titles)

# 4. Experience inspection
print("\n--- EXPERIENCE DISTRIBUTION ---")
min_exp = pd.to_numeric(df["minimumExperience"], errors="coerce")
max_exp = pd.to_numeric(df["maximumExperience"], errors="coerce")
valid_exp = min_exp.notnull() & max_exp.notnull()
exp_df = df[valid_exp].copy()
exp_df["exp_midpoint"] = (min_exp[valid_exp] + max_exp[valid_exp]) / 2.0
print(exp_df["exp_midpoint"].describe())
