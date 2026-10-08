# Phase 2 Summary: Data Cleaning, Normalization & Skill Matrix Construction
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction  
**Dataset:** Tech Job Postings with Parsed Salaries (ATS Direct), Package `jobs-tier1-L-2026-08-01`  
**Date:** October 5, 2026  
**Status:** Gate 2 & Gate 3 Successfully Passed  

---

## 1. Pipeline Execution Flow

```text
RAW CORPUS: 394,300 rows x 22 columns
               ↓  [Deduplication: drop crawler token-casing duplicates (58,305 rows)]
DEDUPLICATED CORPUS: 335,995 rows
               ↓  [Salary Normalization: validate dual bounds, calculate midpoint]
VALID SALARY POPULATION: 99,208 rows (29.53%)
               ↓  [Seniority & Role Engineering: regex parsing into 5 seniority tiers & 14 role families]
               ↓  [Skill Curation: 101 raw skills -> remove 10 non-tech noise skills -> 91 technical vocabulary]
CLEANED JOBS PARQUET: 335,995 rows x 23 columns (Exported: data/processed/cleaned_jobs.parquet)
SKILL MATRIX PARQUET: 335,995 rows x 91 binary columns (Exported: data/processed/skill_matrix.parquet)
               ↓  [Modeling Cohort Filter: is_tech_role == True, USD Annual, $30k-$600k midpoint, num_skills >= 1]
SUPERVISED MODELING DATASET: 46,608 rows x 102 columns (Exported: data/processed/modeling_dataset.parquet)
```

---

## 2. Quantitative Transformations Summary

| Metric | Raw Dataset | Cleaned Corpus (`cleaned_jobs.parquet`) | Modeling Cohort (`modeling_dataset.parquet`) |
|---|---:|---:|---:|
| **Total Rows** | 394,300 | 335,995 | **46,608** |
| **Total Columns** | 22 | 23 | **102** (8 metadata + 91 skills + 3 targets) |
| **Valid Dual Salary Bounds** | 107,151 (27.17%) | 99,208 (29.53%) | **46,608 (100.0%)** |
| **USD Annual Salaries** | 71,822 | 62,138 | **46,608 (100.0%)** |
| **Technology Roles** | — | 174,135 (51.83%) | **46,608 (100.0%)** |
| **Skill Vocabulary Size** | 101 | 91 | **91** |
| **Average Skills / Posting** | 2.13 | 2.13 | **4.07** |
| **Exact Crawler Duplicates** | 58,305 | 0 | **0** |

---

## 3. Detailed Component Breakdown

### 3.1 Duplicate Handling
- **Total Rows Filtered:** 58,305
- **Mechanism:** Identified systematic crawler token-casing duplicates on SmartRecruiters (e.g. `ALTEN` vs `alten` in `ats_token`). Deduplication on `(ats, ats_token_norm, job_id)` purged all 58,305 redundant records.
- **Protected Variations:** Genuine multiple job requisitions at the same company and location (26,387 rows), geographic hiring variations across cities (21,480 groups), and temporal reposts (26,267 rows) were 100% retained.

### 3.2 Salary Normalization
- **Harmonized Target:** Annual USD salary midpoint ($\text{salary\_midpoint} = (\text{salary\_min} + \text{salary\_max}) / 2$).
- **Filtering Thresholds:** 
  - Bounds must be strictly positive ($\text{salary\_min} > 0$ and $\text{salary\_max} > 0$).
  - Logical order enforced ($\text{salary\_min} \le \text{salary\_max}$).
  - Realistic annual compensation bounds applied: $\$30,000 \le \text{salary\_midpoint} \le \$600,000$.
- **Modeling Cohort Salary Distribution ($N = 46,608$):**
  - **Minimum:** \$30,000.00
  - **25th Percentile (Q1):** \$140,000.00
  - **50th Percentile (Median):** \$170,000.00
  - **Mean:** \$176,560.87
  - **75th Percentile (Q3):** \$210,000.00
  - **Maximum:** \$600,000.00
  - **Standard Deviation:** \$58,746.12

### 3.3 Skill Vocabulary & Multi-Hot Matrix
- **Raw Skills:** 101 controlled vocabulary tags from DataForge.
- **Removed Non-Tech Noise (10 skills):** `accounting`, `customer-success`, `financial-analysis`, `hubspot`, `legal`, `marketing`, `recruiting`, `sales`, `sem`, `seo`.
- **Final Technical Vocabulary (91 skills):**
  - *Languages:* Python, SQL, TypeScript, JavaScript, Java, C++, C#, Ruby, Go, Rust, Swift, Kotlin, Scala, PHP
  - *Cloud & Infrastructure:* AWS, Azure, GCP, Kubernetes, Docker, Terraform, Ansible, Linux, CI/CD, DevOps, Serverless, Microservices
  - *AI / ML / Data Science:* Machine Learning, LLM, Deep Learning, PyTorch, TensorFlow, NLP, Computer Vision, Scikit-learn, Pandas, NumPy, Spark, Databricks, Snowflake, BigQuery, Redshift, Kafka, Airflow, dbt, ETL, Hadoop, Statistics
  - *Databases:* PostgreSQL, MongoDB, Redis, Elasticsearch, NoSQL
  - *Web & Frameworks:* React, Angular, Vue, Next.js, Node.js, Django, FastAPI, Flask, Spring, HTML/CSS, Android, iOS, Flutter, REST API, GraphQL, gRPC
  - *Analytics & BI:* Tableau, Power BI, Looker, Excel
  - *Architecture & Specializations:* Robotics, Embedded, Unity, Blockchain, Hardware, GIS, RabbitMQ, Security, QA/Testing, Git, UI/UX, Figma
- **Skill Density:** In the modeling cohort, postings contain an average of **4.07 skills** (up from 2.13 across the raw corpus), providing rich co-occurrence patterns for PCA and K-Means.

### 3.4 Seniority Distribution (Modeling Cohort)
| Seniority Tier | Count | Percentage |
|---|---:|---:|
| **Lead / Principal / Executive** | 17,857 | 38.31% |
| **Mid / Unspecified** | 14,781 | 31.71% |
| **Senior** | 12,412 | 26.63% |
| **Junior / Entry** | 1,463 | 3.14% |
| **Intern** | 95 | 0.20% |
| **Total** | **46,608** | **100.00%** |

### 3.5 Role Family Distribution (Modeling Cohort)
| Role Family | Count | Percentage |
|---|---:|---:|
| **Software Engineer** | 6,583 | 14.12% |
| **ML / AI Engineer** | 5,631 | 12.08% |
| **DevOps / Cloud** | 3,009 | 6.46% |
| **Product & Solutions** | 2,746 | 5.89% |
| **Data Scientist** | 2,268 | 4.87% |
| **Data Engineer** | 1,882 | 4.04% |
| **Security Engineer** | 1,221 | 2.62% |
| **Tech Leadership / Architecture** | 1,118 | 2.40% |
| **Full-Stack Developer** | 820 | 1.76% |
| **Backend Developer** | 692 | 1.48% |
| **Frontend Developer** | 664 | 1.42% |
| **QA / SDET** | 557 | 1.19% |
| **Data / BI Analyst** | 311 | 0.67% |
| **Other Tech** | 19,106 | 40.99% |
| **Total** | **46,608** | **100.00%** |

---

## 4. Phase 2 Deliverables Manifest

```text
e:/Job Market/
├── data/
│   ├── raw/
│   │   ├── dataset_A/              # Untouched original DataForge package
│   │   └── dataset_B/              # Preserved secondary dataset
│   └── processed/
│       ├── cleaned_jobs.parquet     # 335,995 rows x 23 columns
│       ├── skill_matrix.parquet    # 335,995 rows x 91 binary columns
│       └── modeling_dataset.parquet # 46,608 rows x 102 columns
│
├── reports/
│   ├── license_compliance.md       # Legal audit & gitignore enforcement
│   ├── duplicate_analysis.md       # 58,305 crawler duplicates diagnosed
│   ├── salary_normalization.md     # Midpoint & USD annual methodology
│   ├── leakage_audit.md            # Zero-leakage protocol verification
│   └── phase2_summary.md           # This comprehensive synthesis
```

---

## 5. Phase 2 Quality Gate Checklist

- [x] **Gate 1 Passed:** Primary dataset selected and provenance documented.
- [x] **Gate 2 Passed:** Salary target verified, normalized to annual USD midpoint, dual bounds enforced, non-positive placeholders purged, and outlier boundaries documented.
- [x] **Gate 3 Passed:** Skill vocabulary curated (91 technical skills), noise removed, multi-hot matrix built, and average skill density validated.
- [x] **Gate 4 Passed:** Zero-leakage audit completed; target variables strictly isolated from predictor matrices; train-only pipeline design confirmed.
