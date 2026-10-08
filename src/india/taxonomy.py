"""
Skill Taxonomy and Extraction Module for JobIntel India.
Parses comma-delimited skills from 'tagsAndSkills', applies casing/punctuation cleaning,
normalizes technology aliases, and generates the relational job_skills table and taxonomy metadata.
"""

import re
import json
import pandas as pd
from collections import Counter
from typing import Dict, List, Tuple, Any

# Standardized technology aliases
SKILL_ALIASES: Dict[str, str] = {
    # Cloud & DevOps
    "amazon web services": "aws",
    "microsoft azure": "azure",
    "ms azure": "azure",
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    "k8s": "kubernetes",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "cicd": "ci/cd",
    
    # Web & Frameworks
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "nodejs": "node.js",
    "node js": "node.js",
    "vuejs": "vue.js",
    "vue": "vue.js",
    "angularjs": "angular",
    "angular.js": "angular",
    "dotnet": ".net",
    ".net core": ".net",
    "asp.net": ".net",
    "js": "javascript",
    "ts": "typescript",
    
    # Data & AI
    "powerbi": "power bi",
    "ms power bi": "power bi",
    "power-bi": "power bi",
    "ml": "machine learning",
    "natural language processing": "nlp",
    "artificial intelligence": "ai",
    "deep learning": "deep learning",
    "mssql": "sql server",
    "ms sql": "sql server",
    "ms sql server": "sql server",
    "microsoft sql server": "sql server",
    "plsql": "pl/sql",
    "pl-sql": "pl/sql",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "big query": "bigquery",
    "pyspark": "spark",
    
    # API & Architecture
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest apis": "rest api",
    "rest": "rest api",
    "micro services": "microservices",
    "microservice": "microservices",
}

def clean_skill_token(token: str) -> str:
    """Basic lowercasing and punctuation stripping."""
    t = str(token).strip().lower()
    t = re.sub(r'^[\s\-_/\.]+|[\s\-_/\.]+$', '', t)
    return t

def normalize_skill(token: str) -> str:
    """Normalizes raw skill token by cleaning and applying alias dictionary."""
    cleaned = clean_skill_token(token)
    if not cleaned:
        return ""
    return SKILL_ALIASES.get(cleaned, cleaned)

def build_job_skills_table(df: pd.DataFrame, job_id_col: str = "jobId", tags_col: str = "tagsAndSkills") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Extracts distinct (job_id, skill) pairs per job.
    Returns:
        job_skills_df: DataFrame with ['job_id', 'skill']
        taxonomy_meta: Dict with taxonomy summary metrics
    """
    records = []
    job_counts = []
    unique_jobs = set()
    raw_token_counter = Counter()
    norm_token_counter = Counter()
    
    for _, row in df.iterrows():
        jid = row[job_id_col]
        tags = row[tags_col]
        if pd.isnull(tags):
            job_counts.append(0)
            continue
            
        skills_set = set()
        for tok in str(tags).split(","):
            raw_t = tok.strip()
            if raw_t:
                raw_token_counter[raw_t] += 1
                norm_t = normalize_skill(raw_t)
                if norm_t:
                    skills_set.add(norm_t)
                    
        if skills_set:
            unique_jobs.add(jid)
            job_counts.append(len(skills_set))
            for sk in skills_set:
                records.append((jid, sk))
                norm_token_counter[sk] += 1
        else:
            job_counts.append(0)
            
    job_skills_df = pd.DataFrame(records, columns=["job_id", "skill"])
    
    # Compute summary metrics
    taxonomy_meta = {
        "total_jobs_evaluated": len(df),
        "unique_jobs_with_skills": len(unique_jobs),
        "total_job_skill_pairs": len(job_skills_df),
        "unique_raw_skills": len(raw_token_counter),
        "unique_normalized_skills": len(norm_token_counter),
        "avg_skills_per_job": round(float(pd.Series(job_counts).mean()), 2) if job_counts else 0.0,
        "median_skills_per_job": float(pd.Series(job_counts).median()) if job_counts else 0.0,
        "max_skills_per_job": int(pd.Series(job_counts).max()) if job_counts else 0,
        "missing_skills_jobs": int(len(df) - len(unique_jobs)),
        "alias_mapping_count": len(SKILL_ALIASES),
        "top_50_skills": {k: int(v) for k, v in norm_token_counter.most_common(50)},
        "top_50_raw_tokens": {k: int(v) for k, v in raw_token_counter.most_common(50)}
    }
    
    return job_skills_df, taxonomy_meta
