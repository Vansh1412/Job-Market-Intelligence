"""
Inspect experience bands distribution.
"""
import pandas as pd
import numpy as np

df = pd.read_parquet("scratch/raw_india_cache.parquet")
min_e = pd.to_numeric(df["minimumExperience"], errors="coerce")
max_e = pd.to_numeric(df["maximumExperience"], errors="coerce")
valid_exp = min_e.notnull() & max_e.notnull() & (min_e >= 0) & (max_e >= min_e)
df_exp = df[valid_exp].copy()
df_exp["exp_midpoint"] = (min_e[valid_exp] + max_e[valid_exp]) / 2.0

def get_band(m):
    if m <= 2:
        return "0-2 Yrs (Entry)"
    elif m <= 5:
        return "3-5 Yrs (Mid)"
    elif m <= 10:
        return "6-10 Yrs (Senior)"
    else:
        return "11+ Yrs (Lead / Principal)"

df_exp["experience_band"] = df_exp["exp_midpoint"].apply(get_band)
print("Experience bands across all valid postings:")
print(df_exp["experience_band"].value_counts())

# Now within valid INR salary
min_s = pd.to_numeric(df_exp["minimumSalary"], errors="coerce")
max_s = pd.to_numeric(df_exp["maximumSalary"], errors="coerce")
sal_mask = (df_exp["currency"] == "INR") & (min_s > 0) & (max_s >= min_s)
sal_df = df_exp[sal_mask].copy()
sal_df["salary_lpa"] = (min_s[sal_mask] + max_s[sal_mask]) / 200000.0

print("\nExperience bands within valid INR salary cohort:")
gb = sal_df.groupby("experience_band")["salary_lpa"].agg(["count", "mean", "median", "min", "max"])
gb["mean"] = gb["mean"].round(2)
gb["median"] = gb["median"].round(2)
print(gb)
