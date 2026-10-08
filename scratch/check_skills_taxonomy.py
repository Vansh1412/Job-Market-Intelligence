"""
Inspect top raw skill tokens, design taxonomy alias mappings, and verify frequencies.
"""
import pandas as pd
from collections import Counter
import re

df = pd.read_parquet("scratch/raw_india_cache.parquet")
dedup = df.drop_duplicates(subset=["jobId"])

skills_series = dedup["tagsAndSkills"].dropna().astype(str)

raw_tokens = []
cleaned_tokens = []

# Basic clean: lowercase, strip, remove leading/trailing punctuation except dots/plus/#
def clean_token(token):
    t = token.strip().lower()
    # strip quotes and extra symbols
    t = re.sub(r'^[\s\-_/\.]+|[\s\-_/\.]+$', '', t)
    return t

for s in skills_series:
    parts = s.split(",")
    for p in parts:
        raw_t = p.strip()
        if raw_t:
            raw_tokens.append(raw_t)
            c_t = clean_token(raw_t)
            if c_t:
                cleaned_tokens.append(c_t)

print(f"Total raw skill tokens: {len(raw_tokens):,}")
print(f"Unique raw tokens: {len(set(raw_tokens)):,}")
print(f"Unique basic-cleaned tokens: {len(set(cleaned_tokens)):,}")

raw_top100 = Counter(raw_tokens).most_common(100)
clean_top100 = Counter(cleaned_tokens).most_common(100)

print("\n--- TOP 30 BASIC CLEANED SKILLS ---")
for k, v in clean_top100[:30]:
    print(f"  {k:30s}: {v:,}")
