"""
Analyze titles and design the deterministic role normalization rules.
"""
import pandas as pd
import re
from collections import Counter

DATA_PATH = "data/raw/india/indian-job-market-dataset-2025.xlsx"
df = pd.read_excel(DATA_PATH)

titles = df["title"].dropna().astype(str).tolist()

# Let's inspect frequency of role-relevant keywords
print(f"Total titles: {len(titles):,}, unique: {len(set(titles)):,}")

# Top 50 raw titles
print("\nTop 50 raw titles:")
for t, c in Counter(titles).most_common(50):
    print(f"  {c:5d} : {t}")
