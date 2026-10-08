"""
Fast exploration of roles, tech vs non-tech, locations, and skills from cached parquet.
"""
import pandas as pd
import numpy as np
import re
from collections import Counter

df = pd.read_parquet("scratch/raw_india_cache.parquet")
print(f"Loaded {len(df):,} rows.")

# 1. Inspect titles with "analyst"
analyst_titles = df[df["title"].str.lower().str.contains("analyst", na=False)]["title"].value_counts()
print("\n--- TOP ANALYST TITLES ---")
print(analyst_titles.head(25))

# 2. Inspect locations
print("\n--- TOP 40 LOCATIONS ---")
print(df["location"].value_counts().head(40))

# 3. Check compound locations and prefixes
print("\n--- PREFIX LOCATIONS ---")
hybrid_locs = df[df["location"].str.startswith("Hybrid", na=False)]["location"].value_counts()
print(hybrid_locs.head(10))

# 4. Check skills
skills_series = df["tagsAndSkills"].dropna().astype(str)
all_tokens = [t.strip() for line in skills_series for t in line.split(",") if t.strip()]
token_counter = Counter(all_tokens)
print("\n--- TOP 50 RAW SKILL TOKENS ---")
for k, v in token_counter.most_common(50):
    print(f"  {k:30s}: {v:,}")

# Let's inspect aliases like Power BI vs PowerBI, ML vs Machine Learning, etc.
def check_variants(variants):
    print(f"\nChecking variants: {variants}")
    for v in variants:
        matches = [k for k in token_counter if k.lower() == v.lower()]
        total = sum(token_counter[m] for m in matches)
        print(f"  {v}: {total} mentions (keys: {matches})")

check_variants(["power bi", "powerbi", "power-bi", "ms power bi"])
check_variants(["machine learning", "ml", "machinelearning"])
check_variants(["nlp", "natural language processing"])
check_variants(["sql server", "mssql", "ms sql", "microsoft sql server"])
check_variants(["react", "react.js", "reactjs", "react js"])
check_variants(["node.js", "nodejs", "node", "node js"])
check_variants(["vue", "vue.js", "vuejs"])
check_variants(["angular", "angular.js", "angularjs"])
check_variants(["aws", "amazon web services"])
check_variants(["azure", "microsoft azure"])
check_variants(["gcp", "google cloud platform", "google cloud"])
check_variants(["docker", "kubernetes", "k8s"])
