"""
JobIntel India — Phase India-2: Schema Normalization & Cleaning Pipeline.
Deterministic, reproducible ETL pipeline that reads the raw Indian job market dataset
and creates the clean analytical parquet layer:
    - data/processed/india/cleaned_india_jobs.parquet (all 97,929 rows with flags)
    - data/processed/india/india_job_postings.parquet (analytical job postings)
    - data/processed/india/india_job_skills.parquet (normalized bridge table)
    - data/processed/india/india_taxonomy.json (taxonomy metadata)
"""

import os
import sys
import json
import re
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

from src.india.role_mapping import classify_role
from src.india.taxonomy import build_job_skills_table

# City to State mapping dictionary
CITY_STATE_MAP = {
    "bengaluru": ("Bengaluru", "Karnataka"),
    "bangalore": ("Bengaluru", "Karnataka"),
    "hyderabad": ("Hyderabad", "Telangana"),
    "secunderabad": ("Hyderabad", "Telangana"),
    "pune": ("Pune", "Maharashtra"),
    "mumbai": ("Mumbai", "Maharashtra"),
    "navi mumbai": ("Mumbai", "Maharashtra"),
    "thane": ("Mumbai", "Maharashtra"),
    "mumbai suburban": ("Mumbai", "Maharashtra"),
    "chennai": ("Chennai", "Tamil Nadu"),
    "madras": ("Chennai", "Tamil Nadu"),
    "gurugram": ("Gurugram", "Haryana"),
    "gurgaon": ("Gurugram", "Haryana"),
    "noida": ("Noida", "Uttar Pradesh"),
    "greater noida": ("Noida", "Uttar Pradesh"),
    "delhi": ("Delhi NCR", "Delhi"),
    "new delhi": ("Delhi NCR", "Delhi"),
    "delhi / ncr": ("Delhi NCR", "Delhi"),
    "delhi ncr": ("Delhi NCR", "Delhi"),
    "kolkata": ("Kolkata", "West Bengal"),
    "ahmedabad": ("Ahmedabad", "Gujarat"),
    "jaipur": ("Jaipur", "Rajasthan"),
    "coimbatore": ("Coimbatore", "Tamil Nadu"),
    "vadodara": ("Vadodara", "Gujarat"),
    "baroda": ("Vadodara", "Gujarat"),
    "kochi": ("Kochi", "Kerala"),
    "cochin": ("Kochi", "Kerala"),
    "surat": ("Surat", "Gujarat"),
    "nagpur": ("Nagpur", "Maharashtra"),
    "lucknow": ("Lucknow", "Uttar Pradesh"),
    "chandigarh": ("Chandigarh", "Chandigarh"),
    "mohali": ("Mohali", "Punjab"),
    "indore": ("Indore", "Madhya Pradesh"),
    "bhopal": ("Bhopal", "Madhya Pradesh"),
    "faridabad": ("Faridabad", "Haryana"),
    "ghaziabad": ("Ghaziabad", "Uttar Pradesh"),
    "nashik": ("Nashik", "Maharashtra"),
    "aurangabad": ("Aurangabad", "Maharashtra"),
    "bhubaneswar": ("Bhubaneswar", "Odisha"),
    "trivandrum": ("Thiruvananthapuram", "Kerala"),
    "thiruvananthapuram": ("Thiruvananthapuram", "Kerala"),
    "visakhapatnam": ("Visakhapatnam", "Andhra Pradesh"),
    "vizag": ("Visakhapatnam", "Andhra Pradesh"),
    "vijayawada": ("Vijayawada", "Andhra Pradesh"),
    "patna": ("Patna", "Bihar"),
    "mysuru": ("Mysuru", "Karnataka"),
    "mysore": ("Mysuru", "Karnataka"),
    "remote": ("Remote", "Remote"),
}

RECOGNIZED_KEYS = sorted(CITY_STATE_MAP.keys(), key=lambda x: -len(x))

def normalize_location(loc_raw: Any) -> Tuple[str, str]:
    """
    Normalizes a freeform Indian location string into (normalized_city, normalized_state).
    Applies deterministic primary-city rule for compound strings.
    """
    if pd.isnull(loc_raw):
        return None, None
    s = str(loc_raw).strip()
    if not s:
        return None, None
        
    s_lower = s.lower()
    
    # Remote handling
    if s_lower == "remote" or s_lower.startswith("remote -"):
        for k in RECOGNIZED_KEYS:
            if k != "remote" and re.search(r'\b' + re.escape(k) + r'\b', s_lower):
                c, st = CITY_STATE_MAP[k]
                return c, st
        return "Remote", "Remote"
        
    # Strip Hybrid prefix
    clean_s = re.sub(r'^(hybrid\s*-\s*|work\s*from\s*home\s*-\s*)', '', s_lower).strip()
    
    # Deterministic primary-city rule: check first token of compound string
    parts = re.split(r'[,/]', clean_s)
    first_part = parts[0].strip()
    for k in RECOGNIZED_KEYS:
        if k != "remote" and re.search(r'\b' + re.escape(k) + r'\b', first_part):
            c, st = CITY_STATE_MAP[k]
            return c, st
            
    # Check entire string for first recognized metro
    for k in RECOGNIZED_KEYS:
        if k != "remote" and re.search(r'\b' + re.escape(k) + r'\b', clean_s):
            c, st = CITY_STATE_MAP[k]
            return c, st
            
    if "remote" in clean_s or "work from home" in clean_s:
        return "Remote", "Remote"
        
    # Fallback to Title Cased first token
    raw_first = re.split(r'[,/]', s)[0].strip()
    raw_clean = re.sub(r'^(Hybrid\s*-\s*|Remote\s*-\s*)', '', raw_first).strip()
    return (raw_clean.title() if raw_clean else None), None

def compute_experience_band(exp_midpoint: float) -> str:
    """
    Maps experience midpoint to a standardized experience band:
        - 0-2 Yrs (Entry)
        - 3-5 Yrs (Mid)
        - 6-10 Yrs (Senior)
        - 11+ Yrs (Lead / Principal)
    """
    if pd.isnull(exp_midpoint) or exp_midpoint < 0:
        return None
    if exp_midpoint <= 2.0:
        return "0-2 Yrs (Entry)"
    elif exp_midpoint <= 5.0:
        return "3-5 Yrs (Mid)"
    elif exp_midpoint <= 10.0:
        return "6-10 Yrs (Senior)"
    else:
        return "11+ Yrs (Lead / Principal)"

def run_india_etl(
    raw_excel_path: str = "data/raw/india/indian-job-market-dataset-2025.xlsx",
    output_dir: str = "data/processed/india",
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Executes the complete Phase India-2 schema normalization and analytical table generation.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load data
    cache_path = "scratch/raw_india_cache.parquet"
    if use_cache and os.path.exists(cache_path):
        print(f"Loading raw data from cache: {cache_path}...")
        df_raw = pd.read_parquet(cache_path)
    else:
        print(f"Loading raw data from Excel: {raw_excel_path}...")
        df_raw = pd.read_excel(raw_excel_path)
        
    n_raw = len(df_raw)
    print(f"Loaded {n_raw:,} records.")
    
    # 2. Duplicate Detection
    exact_dup_mask = df_raw.duplicated()
    jobid_dup_mask = df_raw.duplicated(subset=["jobId"])
    content_dup_mask = df_raw.duplicated(subset=["title", "companyName", "location", "salary", "experience"])
    
    # 3. Currency and Salary Normalization
    is_inr = (df_raw["currency"] == "INR")
    min_sal_num = pd.to_numeric(df_raw["minimumSalary"], errors="coerce")
    max_sal_num = pd.to_numeric(df_raw["maximumSalary"], errors="coerce")
    
    # Valid positive salary range mask
    valid_salary_mask = (
        is_inr &
        min_sal_num.notnull() &
        max_sal_num.notnull() &
        (min_sal_num > 0) &
        (max_sal_num >= min_sal_num)
    )
    
    # Calculate midpoint and LPA
    salary_midpoint_inr = np.where(valid_salary_mask, (min_sal_num + max_sal_num) / 2.0, np.nan)
    salary_lpa = np.where(valid_salary_mask, salary_midpoint_inr / 100000.0, np.nan)
    
    # 4. Experience Normalization
    min_exp_num = pd.to_numeric(df_raw["minimumExperience"], errors="coerce")
    max_exp_num = pd.to_numeric(df_raw["maximumExperience"], errors="coerce")
    
    valid_exp_mask = (
        min_exp_num.notnull() &
        max_exp_num.notnull() &
        (min_exp_num >= 0) &
        (max_exp_num >= min_exp_num)
    )
    
    experience_midpoint = np.where(valid_exp_mask, (min_exp_num + max_exp_num) / 2.0, np.nan)
    experience_bands = [compute_experience_band(m) if pd.notnull(m) else None for m in experience_midpoint]
    
    # 5. Location Normalization
    norm_cities = []
    norm_states = []
    for loc in df_raw["location"]:
        c, s = normalize_location(loc)
        norm_cities.append(c)
        norm_states.append(s)
        
    # 6. Role & Tech Classification
    norm_roles = []
    is_tech_list = []
    for t, s in zip(df_raw["title"], df_raw["tagsAndSkills"]):
        r, it = classify_role(t, s)
        norm_roles.append(r)
        is_tech_list.append(it)
        
    # 7. Construct Full Master Cleaned Dataset (All 97,929 rows)
    cleaned_df = pd.DataFrame({
        "job_id": df_raw["jobId"],
        "original_title": df_raw["title"],
        "company_name": df_raw["companyName"],
        "company_id": df_raw["companyId"],
        "original_location": df_raw["location"],
        "normalized_city": norm_cities,
        "normalized_state": norm_states,
        "currency": df_raw["currency"],
        "original_salary": df_raw["salary"],
        "minimum_salary_inr": np.where(valid_salary_mask, min_sal_num, np.nan),
        "maximum_salary_inr": np.where(valid_salary_mask, max_sal_num, np.nan),
        "salary_midpoint_inr": salary_midpoint_inr,
        "salary_lpa": salary_lpa,
        "original_experience": df_raw["experience"],
        "minimum_experience": np.where(valid_exp_mask, min_exp_num, np.nan),
        "maximum_experience": np.where(valid_exp_mask, max_exp_num, np.nan),
        "experience_midpoint": experience_midpoint,
        "experience_band": experience_bands,
        "normalized_role": norm_roles,
        "is_tech_role": is_tech_list,
        "tags_and_skills": df_raw["tagsAndSkills"],
        "job_description": df_raw["jobDescription"],
        "job_uploaded": df_raw["jobUploaded"],
        "reviews_count": df_raw["ReviewsCount"],
        "aggregate_rating": df_raw["AggregateRating"],
        # Provenance & Audit Flags
        "is_salary_valid": valid_salary_mask,
        "is_inr": is_inr,
        "is_exact_duplicate": exact_dup_mask,
        "is_jobid_duplicate": jobid_dup_mask,
        "is_content_duplicate": content_dup_mask,
        "is_analytical_eligible": (is_inr & ~exact_dup_mask)
    })
    
    cleaned_parquet_path = os.path.join(output_dir, "cleaned_india_jobs.parquet")
    print(f"Saving cleaned master dataset ({len(cleaned_df):,} rows) to {cleaned_parquet_path}...")
    cleaned_df.to_parquet(cleaned_parquet_path, index=False)
    
    # 8. Construct Analytical Job Postings Table (Unique jobId deduplication: N = 97,679)
    # This matches the SQL relational model where job_id is unique primary key
    postings_df = cleaned_df.drop_duplicates(subset=["job_id"]).copy()
    # Add alias columns for SQL schema direct compatibility
    postings_df["city"] = postings_df["normalized_city"]
    postings_df["state"] = postings_df["normalized_state"]
    postings_df["role_category"] = postings_df["normalized_role"]
    
    postings_parquet_path = os.path.join(output_dir, "india_job_postings.parquet")
    print(f"Saving analytical job postings ({len(postings_df):,} rows) to {postings_parquet_path}...")
    postings_df.to_parquet(postings_parquet_path, index=False)
    
    # 9. Construct Relational Job Skills Bridge Table
    skills_df, taxonomy_meta = build_job_skills_table(postings_df, job_id_col="job_id", tags_col="tags_and_skills")
    skills_parquet_path = os.path.join(output_dir, "india_job_skills.parquet")
    print(f"Saving job skills bridge table ({len(skills_df):,} rows) to {skills_parquet_path}...")
    skills_df.to_parquet(skills_parquet_path, index=False)
    
    # 10. Save Taxonomy Metadata JSON
    taxonomy_json_path = os.path.join(output_dir, "india_taxonomy.json")
    print(f"Saving taxonomy metadata to {taxonomy_json_path}...")
    with open(taxonomy_json_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy_meta, f, indent=2)
        
    summary = {
        "raw_rows": n_raw,
        "cleaned_rows": len(cleaned_df),
        "analytical_postings_rows": len(postings_df),
        "valid_inr_salary_postings": int(postings_df["is_salary_valid"].sum()),
        "tech_postings_count": int(postings_df["is_tech_role"].sum()),
        "job_skills_pairs_count": len(skills_df),
        "unique_normalized_skills": int(skills_df["skill"].nunique()),
        "unique_normalized_roles": int(postings_df["normalized_role"].nunique()),
        "cleaned_parquet_path": cleaned_parquet_path,
        "postings_parquet_path": postings_parquet_path,
        "skills_parquet_path": skills_parquet_path,
        "taxonomy_json_path": taxonomy_json_path
    }
    
    print("\nETL Pipeline completed successfully:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
        
    return summary

if __name__ == "__main__":
    run_india_etl()
