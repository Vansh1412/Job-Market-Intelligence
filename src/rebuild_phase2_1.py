"""
INT234 Job Market Intelligence: Phase 2.1 Pipeline Rebuild
Defensible Methodology, Seniority Disambiguation, Role Precedence Hierarchy,
Skill Taxonomy Partitioning, and Zero-Leakage Dataset Construction.

Outputs:
  - data/processed/cleaned_jobs.parquet (335,995 rows)
  - data/processed/skill_matrix_technical.parquet (335,995 rows x 82 skills)
  - data/processed/skill_matrix_professional.parquet (335,995 rows x 2 skills)
  - data/processed/skill_matrix_business.parquet (335,995 rows x 7 skills)
  - data/processed/skill_matrix.parquet (335,995 rows x 91 skills)
  - data/processed/modeling_dataset.parquet (34,036 rows x 102 columns)
"""

import os
import sys
import json
import re
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("INT234 JOB MARKET INTELLIGENCE — PHASE 2.1 REPRODUCIBLE PIPELINE")
print("=" * 70)

# Paths
base_dir = r"e:\Job Market"
raw_path = os.path.join(base_dir, "data", "raw", "dataset_A", "data", "jobs.parquet")
processed_dir = os.path.join(base_dir, "data", "processed")
os.makedirs(processed_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# STEP 1: LOAD RAW DATASET
# -----------------------------------------------------------------------------
print("\n[Step 1] Loading Raw Dataset A...")
df_raw = pd.read_parquet(raw_path)
raw_rows, raw_cols = len(df_raw), len(df_raw.columns)
print(f"  Raw records loaded: {raw_rows:,} rows, {raw_cols} columns")

# -----------------------------------------------------------------------------
# STEP 2: DEDUPLICATION (SmartRecruiters Crawler Token Casing Artifact)
# -----------------------------------------------------------------------------
print("\n[Step 2] Executing Non-Destructive Deduplication...")
df_raw['ats_token_norm'] = df_raw['ats_token'].astype(str).str.lower()
dedup_keys = ['ats', 'ats_token_norm', 'job_id']

df_dedup = df_raw.drop_duplicates(subset=dedup_keys, keep='first').copy()
dedup_rows = len(df_dedup)
removed_casing_dupes = raw_rows - dedup_rows
print(f"  Crawler token-casing duplicates removed: {removed_casing_dupes:,}")
print(f"  Deduplicated corpus: {dedup_rows:,} rows")

# -----------------------------------------------------------------------------
# STEP 3: SALARY VALIDATION & MIDPOINT CALCULATION
# -----------------------------------------------------------------------------
print("\n[Step 3] Parsing and Validating Salaries...")
valid_sal_bounds = (
    df_dedup['salary_min'].notnull() &
    df_dedup['salary_max'].notnull() &
    (df_dedup['salary_min'] > 0) &
    (df_dedup['salary_max'] > 0) &
    (df_dedup['salary_min'] <= df_dedup['salary_max'])
)

df_dedup['salary_is_valid'] = valid_sal_bounds
df_dedup['salary_midpoint'] = np.where(
    valid_sal_bounds,
    (df_dedup['salary_min'] + df_dedup['salary_max']) / 2.0,
    np.nan
)
valid_sal_count = int(valid_sal_bounds.sum())
print(f"  Postings with valid dual salary bounds: {valid_sal_count:,} ({valid_sal_count/dedup_rows:.2%})")

# -----------------------------------------------------------------------------
# STEP 4: SENIORITY PARSER (v3 with Strict Conflict Resolution)
# -----------------------------------------------------------------------------
print("\n[Step 4] Classifying Seniority using v3 Conflict-Resolution Parser...")

def parse_seniority_v3(title):
    t = str(title).lower()
    
    # Tier 1: Internships & Apprenticeships (Highest Specificity)
    if re.search(r'\b(intern|internship|co-op|coop|trainee|apprentice)\b', t):
        return 'Intern'
    
    # Tier 2: Leadership, Staff, Principal & True People Management
    if re.search(r'\b(principal|staff|distinguished|fellow|architect|director|vp\b|vice president|head of|head,|chief|cto|engineering manager|manager, engineering|software manager|it manager|qa manager|lead\b)\b', t):
        return 'Lead / Principal / Executive'
    
    # Tier 3: Junior & Entry-Level Designations
    if re.search(r'\b(junior|jr|jr\.|entry level|entry-level|entry|associate|graduate|level 1|level i\b|tier 1|tier i\b)\b', t):
        return 'Junior / Entry'
    
    # Tier 4: Senior-level Individual Contributors
    if re.search(r'\b(senior|sr|sr\.|software engineer iii|swe iii|level 3|level iii|tier 3|tier iii)\b', t):
        return 'Senior'
    
    # Tier 5: Mid-level / Unspecified (Default IC baseline)
    return 'Mid / Unspecified'

df_dedup['seniority'] = df_dedup['title'].apply(parse_seniority_v3)
print("  Seniority distribution across corpus:")
for sen, cnt in df_dedup['seniority'].value_counts().items():
    print(f"    - {sen:28s}: {cnt:7,} ({cnt/dedup_rows:5.2%})")

# -----------------------------------------------------------------------------
# STEP 5: SKILL TAXONOMY & VOCABULARY CURATION
# -----------------------------------------------------------------------------
print("\n[Step 5] Establishing 4-Tier Skill Taxonomy...")

# 10 Non-technical / corporate noise skills removed from raw 101 skills
noise_skills = {
    'accounting', 'customer-success', 'financial-analysis', 'hubspot',
    'legal', 'marketing', 'recruiting', 'sales', 'sem', 'seo'
}

# The 91 curated skills partitioned into 3 functional domains:
soft_skills = {'communication', 'project-management'}
business_skills = {'crm', 'salesforce', 'sap', 'excel', 'product-management', 'figma', 'ui-ux'}

all_raw_skills = set([s for sublist in df_dedup['skills'].dropna() if len(sublist) > 0 for s in sublist])
curated_91_skills = sorted(list(all_raw_skills - noise_skills))

technical_skills = sorted([s for s in curated_91_skills if s not in soft_skills and s not in business_skills])
professional_skills = sorted([s for s in curated_91_skills if s in soft_skills])
business_functional_skills = sorted([s for s in curated_91_skills if s in business_skills])

print(f"  Raw skill vocabulary:            {len(all_raw_skills)} skills")
print(f"  Excluded noise skills:           {len(noise_skills)} skills ({sorted(list(noise_skills))})")
print(f"  Total curated skills:            {len(curated_91_skills)} skills")
print(f"    1. Technical Skills:           {len(technical_skills)} skills")
print(f"    2. Professional / Soft Skills: {len(professional_skills)} skills ({professional_skills})")
print(f"    3. Business / Functional:      {len(business_functional_skills)} skills ({business_functional_skills})")

# Filter raw skills to clean sets
curated_set = set(curated_91_skills)
tech_set = set(technical_skills)

# Qualifying technical skills for cohort entry (all non-soft non-crm/salesforce/sap/excel skills)
qualifying_tech_set = set(curated_91_skills) - soft_skills - {'crm', 'salesforce', 'sap', 'excel'}

def filter_curated_skills(skills):
    if not isinstance(skills, (list, np.ndarray)):
        return []
    return [s for s in skills if s in curated_set]

def filter_tech_skills(skills):
    if not isinstance(skills, (list, np.ndarray)):
        return []
    return [s for s in skills if s in tech_set]

df_dedup['clean_skills'] = df_dedup['skills'].apply(filter_curated_skills)
df_dedup['clean_tech_skills'] = df_dedup['skills'].apply(filter_tech_skills)
df_dedup['num_skills'] = df_dedup['clean_tech_skills'].apply(len)
df_dedup['num_all_skills'] = df_dedup['clean_skills'].apply(len)

# -----------------------------------------------------------------------------
# STEP 6: ROLE FAMILY CLASSIFICATION (18-Tier Precedence Hierarchy with Fallback)
# -----------------------------------------------------------------------------
print("\n[Step 6] Classifying Role Families using 18-Tier Precedence Hierarchy...")

def classify_role_family(title, skills):
    t = str(title).lower()
    s = set(skills) if isinstance(skills, (list, np.ndarray, set)) else set()
    
    # Tier 1: Engineering Management (Highest Precedence)
    if re.search(r'\b(engineering manager|manager, engineering|director of engineering|director, engineering|vp of engineering|vp, engineering|vp engineering|head of engineering|head, engineering|chief technology officer|cto)\b', t):
        return 'Engineering Management'
    
    # Tier 2: ML / AI Engineer
    elif re.search(r'\b(machine learning|ml engineer|ai engineer|artificial intelligence|deep learning|nlp|computer vision|llm|mlops)\b', t):
        return 'ML / AI Engineer'
    
    # Tier 3: Data Scientist
    elif re.search(r'\b(data scientist|applied scientist|research scientist|data science|statistician)\b', t):
        return 'Data Scientist'
    
    # Tier 4: Data Engineer
    elif re.search(r'\b(data engineer|database engineer|big data engineer|data warehouse|etl engineer|analytics engineer)\b', t):
        return 'Data Engineer'
    
    # Tier 5: Data / BI Analyst
    elif re.search(r'\b(data analyst|bi analyst|business intelligence analyst|reporting analyst|product analyst|insights analyst)\b', t):
        return 'Data / BI Analyst'
    
    # Tier 6: Security Engineer
    elif re.search(r'\b(security engineer|cybersecurity|infosec|application security|appsec|cloud security|information security|penetration tester|soc analyst)\b', t):
        return 'Security Engineer'
    
    # Tier 7: DevOps / Cloud / Platform
    elif re.search(r'\b(devops|sre|site reliability|cloud engineer|cloud architect|platform engineer|infrastructure engineer|release engineer)\b', t):
        return 'DevOps / Cloud / Platform'
    
    # Tier 8: QA / SDET
    elif re.search(r'\b(qa engineer|quality assurance|test engineer|sdet|automation engineer|software test|test automation)\b', t):
        return 'QA / SDET'
    
    # Tier 9: Solutions & Architecture
    elif re.search(r'\b(solutions architect|enterprise architect|technical architect|solutions engineer|forward deployed engineer|pre-sales engineer|customer engineer)\b', t):
        return 'Solutions & Architecture'
    
    # Tier 10: Technical Product & PM
    elif re.search(r'\b(technical product manager|product manager|product owner|technical program manager|tpm|product designer)\b', t):
        return 'Technical Product & PM'
    
    # Tier 11: Mobile Engineer
    elif re.search(r'\b(mobile engineer|mobile developer|ios developer|ios engineer|android developer|android engineer|react native|flutter)\b', t) or \
         (('ios' in s or 'android' in s or 'swift' in s or 'kotlin' in s or 'flutter' in s) and re.search(r'\b(mobile|ios|android|swift|kotlin|flutter)\b', t)):
        return 'Mobile Engineer'
    
    # Tier 12: Embedded & Hardware
    elif re.search(r'\b(embedded engineer|embedded software|firmware engineer|hardware engineer|robotics engineer|fpga|asic|electrical engineer|mechanical engineer|mechatronics)\b', t):
        return 'Embedded & Hardware'
    
    # Tier 13: Systems & Network Engineer
    elif re.search(r'\b(systems engineer|systems administrator|sysadmin|network engineer|network administrator|systems architect|it engineer)\b', t):
        return 'Systems & Network Engineer'
    
    # Tier 14: Frontend Developer
    elif re.search(r'\b(frontend|front-end|ui developer|web developer|react developer|angular developer|javascript developer)\b', t):
        return 'Frontend Developer'
    
    # Tier 15: Backend Developer
    elif re.search(r'\b(backend|back-end|api engineer|server engineer|java developer|python developer|golang developer|ruby developer)\b', t):
        return 'Backend Developer'
    
    # Tier 16: Full-Stack Developer
    elif re.search(r'\b(fullstack|full-stack|full stack)\b', t):
        return 'Full-Stack Developer'
    
    # Tier 17: Core Software Engineer
    elif re.search(r'\b(software engineer|software developer|swe\b|programmer|applications developer|software development)\b', t):
        return 'Software Engineer'
    
    # Tier 18: Skill-Based Disambiguation Fallback
    elif 'machine-learning' in s or 'deep-learning' in s or 'llm' in s or 'computer-vision' in s:
        return 'ML / AI Engineer'
    elif 'data-science' in s or 'statistics' in s:
        return 'Data Scientist'
    elif 'data-engineering' in s or 'spark' in s or 'kafka' in s or 'snowflake' in s or 'dbt' in s:
        return 'Data Engineer'
    elif 'devops' in s or 'kubernetes' in s or 'terraform' in s or 'docker' in s:
        return 'DevOps / Cloud / Platform'
    elif 'react' in s or 'vue' in s or 'angular' in s:
        return 'Frontend Developer'
    elif 'python' in s or 'java' in s or 'c++' in s or 'typescript' in s or 'go' in s or 'rust' in s:
        return 'Software Engineer'
    else:
        return 'Other Tech'

df_dedup['role_family'] = [classify_role_family(t, s) for t, s in zip(df_dedup['title'], df_dedup['clean_skills'])]

# Corporate non-tech exclusion regex (Domain-grounded)
exclude_patterns = [
    r'\b(care assistant|nurse|nursing|physician|therapist|bcba|behavior analyst|dental|pharmacy|pharmacist|clinical)\b',
    r'\b(chef|cook|restaurant|bar & waiting|cashier|store associate|barista|deli|kitchen|housekeeper|janitor|janitorial)\b',
    r'\b(automotive technician|service advisor|mechanic|hvac|plumber|electrician|carpenter|driver|courier|construction)\b',
    r'\b(customer success|account manager|client executive|account executive|sales representative|sales development|business development|seller|sales executive|closer|territory partner|realtor|smb sales)\b',
    r'\b(counsel|attorney|paralegal|legal specialist|legal counsel|settlement)\b',
    r'\b(accountant|accounting|auditor|payroll|tax|bookkeeper|financial analyst|finance manager|strategic finance|fp&a|controller)\b',
    r'\b(product marketing|marketing manager|marketing coordinator|marketing assistant|communications coordinator|copywriter|brand designer|creative director|growth marketer|founding marketer)\b',
    r'\b(recruiter|talent acquisition|human resources|people partner|executive assistant|office manager|receptionist|district manager|chief of staff|supply chain)\b'
]
exclude_regex = '|'.join(exclude_patterns)
df_dedup['is_non_tech_title'] = df_dedup['title'].str.contains(exclude_regex, case=False, na=False)

# Identify tech roles in deduplicated corpus
has_qualifying_skill = df_dedup['clean_skills'].apply(lambda x: any(s in qualifying_tech_set for s in x))
df_dedup['has_technical_skill'] = has_qualifying_skill
df_dedup['is_tech_role'] = has_qualifying_skill & (~df_dedup['is_non_tech_title'])

tech_corpus_count = int(df_dedup['is_tech_role'].sum())
print(f"  Verified technology postings in corpus: {tech_corpus_count:,} ({tech_corpus_count/dedup_rows:5.2%})")

# -----------------------------------------------------------------------------
# STEP 7: EXPORT CLEANED_JOBS.PARQUET
# -----------------------------------------------------------------------------
print("\n[Step 7] Exporting cleaned_jobs.parquet...")
cleaned_jobs_path = os.path.join(processed_dir, "cleaned_jobs.parquet")
export_cols = [
    'job_id', 'title', 'company_name', 'department', 'ats', 'location_raw',
    'country', 'city', 'is_remote', 'employment_type', 'posted_at', 'url',
    'salary_min', 'salary_max', 'salary_currency', 'salary_period', 'salary_is_valid',
    'salary_midpoint', 'seniority', 'role_family', 'is_tech_role', 'num_skills',
    'clean_skills', 'clean_tech_skills'
]
df_dedup[export_cols].to_parquet(cleaned_jobs_path, index=False)
print(f"  Exported: {cleaned_jobs_path} ({len(df_dedup):,} rows)")

# -----------------------------------------------------------------------------
# STEP 8: BUILD DEDICATED MULTI-HOT SKILL MATRICES
# -----------------------------------------------------------------------------
print("\n[Step 8] Building Dedicated Multi-Hot Skill Matrices...")

def build_sparse_skill_df(skill_list, vocab, prefix="skill_"):
    skill_to_idx = {s: i for i, s in enumerate(vocab)}
    n_r, n_s = len(skill_list), len(vocab)
    mat = np.zeros((n_r, n_s), dtype=np.int8)
    for r_idx, sl in enumerate(skill_list):
        for s in sl:
            if s in skill_to_idx:
                mat[r_idx, skill_to_idx[s]] = 1
    cols = [f"{prefix}{s.replace('-', '_').replace('.', '_')}" for s in vocab]
    return pd.DataFrame(mat, columns=cols, index=df_dedup['job_id'])

# A. Technical Skill Matrix (82 skills) - REQUIRED FOR CLUSTERING (PCA + K-Means)
tech_matrix_path = os.path.join(processed_dir, "skill_matrix_technical.parquet")
df_tech_skills = build_sparse_skill_df(df_dedup['clean_tech_skills'], technical_skills, prefix="skill_")
df_tech_skills.to_parquet(tech_matrix_path)
print(f"  Exported: {tech_matrix_path} ({df_tech_skills.shape[0]:,} rows x {df_tech_skills.shape[1]} skills)")

# B. Professional / Soft Skill Matrix (2 skills)
prof_matrix_path = os.path.join(processed_dir, "skill_matrix_professional.parquet")
df_prof_skills = build_sparse_skill_df(df_dedup['clean_skills'], professional_skills, prefix="skill_")
df_prof_skills.to_parquet(prof_matrix_path)
print(f"  Exported: {prof_matrix_path} ({df_prof_skills.shape[0]:,} rows x {df_prof_skills.shape[1]} skills)")

# C. Business / Functional Skill Matrix (7 skills)
biz_matrix_path = os.path.join(processed_dir, "skill_matrix_business.parquet")
df_biz_skills = build_sparse_skill_df(df_dedup['clean_skills'], business_functional_skills, prefix="skill_")
df_biz_skills.to_parquet(biz_matrix_path)
print(f"  Exported: {biz_matrix_path} ({df_biz_skills.shape[0]:,} rows x {df_biz_skills.shape[1]} skills)")

# D. Unified Curated Skill Matrix (91 skills)
unified_matrix_path = os.path.join(processed_dir, "skill_matrix.parquet")
df_all_skills = build_sparse_skill_df(df_dedup['clean_skills'], curated_91_skills, prefix="skill_")
df_all_skills.to_parquet(unified_matrix_path)
print(f"  Exported: {unified_matrix_path} ({df_all_skills.shape[0]:,} rows x {df_all_skills.shape[1]} skills)")

# -----------------------------------------------------------------------------
# STEP 9: ASSEMBLE MODELING DATASET (Clean Tech Cohort with USD Annual Salary)
# -----------------------------------------------------------------------------
print("\n[Step 9] Constructing Supervised Modeling Dataset...")

# Rigorous cohort qualification:
# 1. is_tech_role == True (has >= 1 qualifying tech skill, non-tech corporate title excluded)
# 2. salary_currency == 'USD'
# 3. salary_period == 'year'
# 4. salary_is_valid == True
# 5. salary_midpoint in [$30,000, $600,000] (Domain-grounded boundary trimming 0.25% extremes)

modeling_mask = (
    df_dedup['is_tech_role'] &
    (df_dedup['salary_currency'] == 'USD') &
    (df_dedup['salary_period'].astype(str).str.lower() == 'year') &
    df_dedup['salary_is_valid'] &
    (df_dedup['salary_midpoint'] >= 30000) &
    (df_dedup['salary_midpoint'] <= 600000)
)

modeling_base = df_dedup[modeling_mask].copy().reset_index(drop=True)
n_model = len(modeling_base)
print(f"  Modeling cohort observations: {n_model:,} rows")

# Targets (strictly isolated from predictors)
modeling_base['log_salary'] = np.log(modeling_base['salary_midpoint'])
modeling_base['salary_band'] = pd.qcut(modeling_base['salary_midpoint'], q=3, labels=['Low', 'Medium', 'High'])

# Geographical standardization: Top 15 Tech Hubs + Other
top_cities = modeling_base['city'].value_counts().head(15).index.tolist()
modeling_base['city_clean'] = modeling_base['city'].apply(lambda x: x if x in top_cities else 'Other')

# Predictor metadata (ZERO SALARY LEAKAGE)
predictor_cols = [
    'job_id', 'title', 'company_name', 'seniority', 'role_family',
    'is_remote', 'city_clean', 'num_skills'
]
modeling_features = modeling_base[predictor_cols].reset_index(drop=True)
modeling_targets = modeling_base[['salary_midpoint', 'log_salary', 'salary_band']].reset_index(drop=True)

# Align skill indicators for the modeling cohort
model_skill_df = df_all_skills.loc[modeling_base['job_id']].reset_index(drop=True)

# Combine: 8 predictors + 91 skills + 3 targets = 102 columns
modeling_dataset = pd.concat([modeling_features, model_skill_df, modeling_targets], axis=1)

modeling_path = os.path.join(processed_dir, "modeling_dataset.parquet")
modeling_dataset.to_parquet(modeling_path, index=False)
print(f"  Exported: {modeling_path} ({modeling_dataset.shape[0]:,} rows x {modeling_dataset.shape[1]} columns)")

# -----------------------------------------------------------------------------
# STEP 10: QUALITY AUDIT METRICS REPORTING
# -----------------------------------------------------------------------------
print("\n[Step 10] Validating Quality Metrics...")

rf_dist = modeling_dataset['role_family'].value_counts()
print("\nRole Family Distribution in Final Modeling Dataset:")
for rf, cnt in rf_dist.items():
    print(f"  - {rf:30s}: {cnt:6,} ({cnt/n_model:6.2%})")

sen_dist = modeling_dataset['seniority'].value_counts()
print("\nSeniority Distribution in Final Modeling Dataset:")
for sen, cnt in sen_dist.items():
    print(f"  - {sen:30s}: {cnt:6,} ({cnt/n_model:6.2%})")

sal = modeling_dataset['salary_midpoint']
print("\nSalary Target Metrics (Modeling Dataset):")
print(f"  Mean:   ${sal.mean():,.2f}")
print(f"  Median: ${sal.median():,.2f}")
print(f"  Std:    ${sal.std():,.2f}")
print(f"  Min:    ${sal.min():,.2f}")
print(f"  Max:    ${sal.max():,.2f}")
print(f"  Raw Skewness:   {sal.skew():.3f}")
print(f"  Log Skewness:   {np.log(sal).skew():.3f}")

# Save JSON metrics for report generation
metrics = {
    "raw_rows": int(raw_rows),
    "dedup_rows": int(dedup_rows),
    "removed_casing_duplicates": int(removed_casing_dupes),
    "verified_tech_roles_corpus": int(tech_corpus_count),
    "final_modeling_rows": int(n_model),
    "final_modeling_columns": int(modeling_dataset.shape[1]),
    "curated_skills_count": int(len(curated_91_skills)),
    "technical_skills_count": int(len(technical_skills)),
    "professional_skills_count": int(len(professional_skills)),
    "business_skills_count": int(len(business_functional_skills)),
    "salary_mean": float(sal.mean()),
    "salary_median": float(sal.median()),
    "salary_std": float(sal.std()),
    "salary_min": float(sal.min()),
    "salary_max": float(sal.max()),
    "salary_skew_raw": float(sal.skew()),
    "salary_skew_log": float(np.log(sal).skew()),
    "role_family_distribution": {k: int(v) for k, v in rf_dist.items()},
    "seniority_distribution": {k: int(v) for k, v in sen_dist.items()}
}

metrics_json_path = os.path.join(processed_dir, "phase2_1_metrics.json")
with open(metrics_json_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)
print(f"\nSaved metrics: {metrics_json_path}")

print("\n" + "=" * 70)
print("PHASE 2.1 PIPELINE REBUILD COMPLETE — DATASETS READY & DEFENDED")
print("=" * 70)
