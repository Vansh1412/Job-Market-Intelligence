"""
Refine role mapping to ensure high precision and capture all tech titles properly.
"""
import pandas as pd
import re
from collections import Counter

DATA_PATH = "data/raw/india/indian-job-market-dataset-2025.xlsx"
df = pd.read_excel(DATA_PATH)

# Let's inspect the top titles in Non-Tech to verify they are truly non-tech
from test_role_mapping import classify_role

roles = []
for t, s in zip(df["title"], df["tagsAndSkills"]):
    r, it = classify_role(t, s)
    roles.append((t, r, it, s))

non_tech_titles = [t for t, r, it, s in roles if r == "Non-Tech"]
print("Top 30 Non-Tech titles:")
for t, c in Counter(non_tech_titles).most_common(30):
    print(f"  {c:4d} : {t}")

# Check if any Non-Tech titles contain words like "tech", "web", "data", "it", "code", "system", "analyst", "consultant"
suspicious_non_tech = []
for t, r, it, s in roles:
    if r == "Non-Tech":
        tl = str(t).lower()
        if any(w in tl for w in ["tech", "developer", "programmer", "engineer", "software", "data", "analyst", "cloud", "security"]):
            suspicious_non_tech.append(t)

print(f"\nSuspicious Non-Tech titles count: {len(suspicious_non_tech)}")
print("Top 20 suspicious Non-Tech titles:")
for t, c in Counter(suspicious_non_tech).most_common(20):
    print(f"  {c:4d} : {t}")
