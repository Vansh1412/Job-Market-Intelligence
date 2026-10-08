"""
Detailed inspection of skills, titles, locations, and audit alignment.
"""
import pandas as pd
import numpy as np

DATA_PATH = "data/raw/india/indian-job-market-dataset-2025.xlsx"
df = pd.read_excel(DATA_PATH)

min_sal = pd.to_numeric(df["minimumSalary"], errors="coerce")
max_sal = pd.to_numeric(df["maximumSalary"], errors="coerce")
min_exp = pd.to_numeric(df["minimumExperience"], errors="coerce")
max_exp = pd.to_numeric(df["maximumExperience"], errors="coerce")

print("Total raw:", len(df))
print("INR count:", (df["currency"] == "INR").sum())
print("USD count:", (df["currency"] == "USD").sum())

pos_sal = min_sal.notnull() & max_sal.notnull() & (min_sal > 0) & (max_sal >= min_sal)
print("Positive salary all currencies:", pos_sal.sum())
print("Positive salary INR:", (pos_sal & (df["currency"] == "INR")).sum())
print("Positive salary USD:", (pos_sal & (df["currency"] == "USD")).sum())

valid_exp = min_exp.notnull() & max_exp.notnull() & (min_exp >= 0) & (max_exp >= min_exp)
print("Valid exp all currencies:", valid_exp.sum())
print("Positive salary INR AND valid exp:", (pos_sal & (df["currency"] == "INR") & valid_exp).sum())

# Undisclosed salary count
undisclosed = (min_sal == 0) & (max_sal == 0)
print("min=0 & max=0 (undisclosed numeric):", undisclosed.sum())
print("text salary == 'Not disclosed':", (df["salary"] == "Not disclosed").sum())

# Examine skills
skills_series = df["tagsAndSkills"].dropna().astype(str)
all_skills_raw = [s.strip() for line in skills_series for s in line.split(",") if s.strip()]
from collections import Counter
raw_counter = Counter(all_skills_raw)
print("\nTop 30 raw skill tokens:")
for k, v in raw_counter.most_common(30):
    print(f"  {k:30s}: {v:,}")

print(f"\nTotal raw skill tokens extracted: {len(all_skills_raw):,}")
print(f"Unique raw skill tokens: {len(raw_counter):,}")

clean_skills = [s.strip().lower() for line in skills_series for s in line.split(",") if s.strip()]
clean_counter = Counter(clean_skills)
print(f"Unique lowercased skill tokens: {len(clean_counter):,}")
