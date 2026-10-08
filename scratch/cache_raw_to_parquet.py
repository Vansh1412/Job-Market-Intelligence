"""
Cache raw Excel into scratch/raw_india_cache.parquet for instant sub-second access.
"""
import pandas as pd
import time

start = time.time()
print("Reading data/raw/india/indian-job-market-dataset-2025.xlsx...")
df = pd.read_excel("data/raw/india/indian-job-market-dataset-2025.xlsx")
print(f"Loaded {len(df):,} rows in {time.time()-start:.2f}s. Saving to scratch/raw_india_cache.parquet...")
df.to_parquet("scratch/raw_india_cache.parquet", index=False)
print("Done!")
