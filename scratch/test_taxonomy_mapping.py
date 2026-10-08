"""
Test taxonomy alias mappings on the actual India dataset.
"""
import pandas as pd
from collections import Counter
import re
import json

df = pd.read_parquet("scratch/raw_india_cache.parquet")
dedup = df.drop_duplicates(subset=["jobId"])

SKILL_ALIASES = {
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

def normalize_skill(token):
    t = token.strip().lower()
    t = re.sub(r'^[\s\-_/\.]+|[\s\-_/\.]+$', '', t)
    if not t:
        return None
    return SKILL_ALIASES.get(t, t)

# Build job_skills table
job_skills_records = []
job_skill_counts = []
unique_jobs_with_skills = set()

for job_id, tags in zip(dedup["jobId"], dedup["tagsAndSkills"]):
    if pd.isnull(tags):
        job_skill_counts.append(0)
        continue
    skills_in_job = set()
    for token in str(tags).split(","):
        norm = normalize_skill(token)
        if norm:
            skills_in_job.add(norm)
    if skills_in_job:
        unique_jobs_with_skills.add(job_id)
        job_skill_counts.append(len(skills_in_job))
        for sk in skills_in_job:
            job_skills_records.append((job_id, sk))
    else:
        job_skill_counts.append(0)

skills_df = pd.DataFrame(job_skills_records, columns=["job_id", "skill"])
print(f"Total jobs evaluated: {len(dedup):,}")
print(f"Unique jobs with skills: {len(unique_jobs_with_skills):,}")
print(f"Total job_skills rows (no duplicates per job): {len(skills_df):,}")
print(f"Unique normalized skills: {skills_df['skill'].nunique():,}")
print(f"Average skills per job: {pd.Series(job_skill_counts).mean():.2f}")
print(f"Median skills per job: {pd.Series(job_skill_counts).median():.1f}")
print(f"Max skills per job: {pd.Series(job_skill_counts).max()}")

print("\n--- TOP 30 NORMALIZED SKILLS ---")
print(skills_df["skill"].value_counts().head(30))
