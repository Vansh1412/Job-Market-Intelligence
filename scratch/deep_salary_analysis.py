"""
Comprehensive salary distribution and outlier analysis.
"""
import pandas as pd
import numpy as np

df = pd.read_parquet("scratch/raw_india_cache.parquet")

min_s = pd.to_numeric(df["minimumSalary"], errors="coerce")
max_s = pd.to_numeric(df["maximumSalary"], errors="coerce")
is_inr = df["currency"] == "INR"
valid_sal = is_inr & min_s.notnull() & max_s.notnull() & (min_s > 0) & (max_s >= min_s)

sal_df = df[valid_sal].copy()
sal_df["min_inr"] = min_s[valid_sal]
sal_df["max_inr"] = max_s[valid_sal]
sal_df["salary_midpoint_inr"] = (sal_df["min_inr"] + sal_df["max_inr"]) / 2.0
sal_df["salary_lpa"] = sal_df["salary_midpoint_inr"] / 100000.0

print(f"Total valid INR salary records: {len(sal_df):,}")

# 1. Percentiles
percentiles = [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.5, 99.9, 100]
pct_rows = []
for p in percentiles:
    lpa_val = float(np.percentile(sal_df["salary_lpa"], p))
    inr_val = float(np.percentile(sal_df["salary_midpoint_inr"], p))
    pct_rows.append({"percentile": f"P{p}", "salary_inr": round(inr_val, 2), "salary_lpa": round(lpa_val, 2)})

pct_df = pd.DataFrame(pct_rows)
print("\n--- SALARY PERCENTILES ---")
print(pct_df.to_string(index=False))

# 2. Salary Bands
band_defs = [
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
band_rows = []
for b_name, mask in band_defs:
    cnt = int(mask.sum())
    pct = round(cnt / len(sal_df) * 100, 2)
    band_rows.append({"salary_band": b_name, "count": cnt, "percentage": pct})

band_df = pd.DataFrame(band_rows)
print("\n--- SALARY BANDS ---")
print(band_df.to_string(index=False))

# 3. Lower tail analysis (<1 LPA and <1.2 LPA)
print("\n--- LOWER TAIL BREAKDOWN ---")
print(f"Count < 1.0 LPA: {(sal_df['salary_lpa'] < 1.0).sum():,}")
print(f"Count < 1.2 LPA: {(sal_df['salary_lpa'] < 1.2).sum():,}")

# What kinds of roles are under 1.2 LPA?
low_sample = sal_df[sal_df["salary_lpa"] < 1.0][["jobId", "title", "companyName", "experience", "salary", "salary_lpa", "tagsAndSkills"]].head(15)
print("\nSamples with < 1.0 LPA:")
print(low_sample.to_string())

# 4. Upper tail analysis (>50 LPA, >80 LPA, >100 LPA)
print("\n--- UPPER TAIL BREAKDOWN ---")
print(f"Count > 50 LPA: {(sal_df['salary_lpa'] > 50.0).sum():,}")
print(f"Count > 80 LPA: {(sal_df['salary_lpa'] > 80.0).sum():,}")
print(f"Count > 100 LPA: {(sal_df['salary_lpa'] > 100.0).sum():,}")

high_sample = sal_df[sal_df["salary_lpa"] > 80.0][["jobId", "title", "companyName", "experience", "salary", "salary_lpa", "tagsAndSkills"]]
print("\nAll samples with > 80 LPA:")
print(high_sample.to_string())
