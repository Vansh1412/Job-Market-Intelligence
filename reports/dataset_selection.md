# Dataset Selection and Provenance Report
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning  
**Course / Task:** INT234 Predictive Analytics — Academic Task 2 (30 Marks)  
**Date:** October 5, 2026  
**Status:** Gate 1 Complete — Dataset Selected & Provenance Documented  

---

## 1. Executive Summary

This report establishes the empirical foundation for **Academic Task 2** of INT234 (Predictive Analytics). The core objective of the project is to investigate three central research questions:
1. **RQ1:** Which skills and skill combinations are most strongly associated with higher salaries in the tech labor market?
2. **RQ2:** Do job postings naturally form coherent, skill-based job archetypes when modeled via unsupervised dimensionality reduction (PCA) and clustering (K-Means)?
3. **RQ3:** Does salary-prediction error systematically differ across distinct job archetypes, and what does this reveal about bias-variance trade-offs in labor economics modeling?

To ensure strict academic rigor, two candidate datasets collected from real-world job posting platforms were audited across 14 quantitative and qualitative dimensions. In accordance with the project blueprint, merging disparate datasets merely to artificially inflate row counts is rejected in favor of identifying **one primary dataset** that offers superior salary quality, domain-relevant skill depth, and verifiable provenance.

Based on comprehensive evaluation, **Dataset A (`Tech Job Postings with Parsed Salaries — ATS Direct`, slice `jobs-tier1-L-2026-08-01`)** is selected as the primary dataset.

---

## 2. Objective Dataset Comparison Table

| Criterion | Dataset A (`jobs-tier1-L-2026-08-01`) | Dataset B (`nextgig_jobs_2026-06.parquet`) | Winner |
|---|---|---|---|
| **Rows** | **394,300** | 112,816 | **Dataset A** (3.5× larger corpus) |
| **Columns** | 22 | **47** | **Dataset B** (wider raw schema) |
| **Salary Coverage (paired min/max)** | **107,151 records (27.2%)**; 100% paired `salary_min` & `salary_max` | 46,885 records (41.6% of B); 52,106 single-bound | **Dataset A** (2.3× total paired salaries; 27,295 annual tech salaries vs 4,107) |
| **Skills Coverage & Quality** | **239,252 records (60.7%)**; 101 standardized tech/business skills (35.4k Python, 26.9k SQL, 22.4k AWS, 17.6k ML, 17.1k LLM) | 80,412 records (71.3%); 53,889 noisy freeform tokens; heavily dominated by retail/service tasks (Python: 2.5k, SQL: 1.9k) | **Dataset A** (high density of tech/data skills essential for RQ1 & RQ2) |
| **Job Title Coverage** | 394,300 (100.0%); 210,905 unique titles; 91,378 tech/data titles | 112,816 (100.0%); 71,808 unique raw titles; 11,831 tech titles | **Dataset A** (7.7× volume of tech/data roles) |
| **Experience Coverage** | 0% explicit column; **100% derivable from title** into 5 distinct seniority tiers (Senior: 36.3k, Lead/Exec: 97.0k, Mid: 239.6k, Entry: 17.3k, Intern: 4.0k) | **65,095 records (57.7%)** explicit `experience_level`; 57,410 `job_level_normalized`; 0.22% numeric years | **Dataset B** (explicit column present) |
| **Location Coverage** | 361,849 country (91.8%); 329,889 city (83.7%); **394,300 `is_remote` flag (100.0%)** | 103,467 country (91.7%); 106,582 city (94.5%); 87,117 `work_model` (77.2%) | **Tie** (A has 100% remote coverage; B has coordinates) |
| **Description Coverage** | 0.0% (excluded by vendor whitelist for licensing reasons) | **112,816 records (100.0%)** full text descriptions | **Dataset B** |
| **Currency Coverage** | 38 currencies; **USD dominates: 92,713 (86.5%)**; GBP: 8,457; EUR: 3,952; CAD: 1,138 | 10 currencies; **USD dominates: 49,116 (94.3%)**; EUR: 1,913; CAD: 1,352; GBP: 1,223 | **Dataset A** (88% more USD records; 92.7k vs 49.1k) |
| **Missingness & Integrity** | High quality on core operational fields (ATS, job_id, title, url: 0% null; remote: 0% null; country: 8.2% null) | Core fields missing: function (93.2%), industry (93.5%), occupational_category (98.1%), pay_frequency (99.3%) | **Dataset A** (more reliable core schema) |
| **Duplicate Rate** | **0 exact row duplicates**; 71,413 duplicate (title, company, location) cross-postings | **0 exact row duplicates**; 0 exact title/company/desc duplicates | **Tie** (both clean of exact row duplicates) |
| **Real-World Provenance** | **Exemplary**: Formal `DATASHEET.md` (Gebru et al. standard), full `DATA-DICTIONARY.md`, `LICENSE.md`, and `checksums.txt` | Bare parquet file; no documentation, no datasheet, no data dictionary, no license | **Dataset A** (publication-ready provenance) |
| **Suitability for Regression (RQ1 & RQ3)** | **Outstanding**: 27,295 annual tech salaries (25,008 USD) provide robust statistical power for 5-fold CV, regularized models, and archetype error breakdown | **Marginal**: Only 4,107 annual tech salaries (3,798 USD), risking severe small-sample instability in multi-cluster error analysis | **Dataset A** |
| **Suitability for Clustering (RQ2)** | **Outstanding**: 101 clean multi-hot skill features across tens of thousands of tech postings yield mathematically distinct, interpretable archetypes | **Poor**: `skills_required` dominated by retail/service tasks (cash handling, stocking, patient care); tech clusters become degenerate or tiny | **Dataset A** |
| **OVERALL WINNER** | **DATASET A** (Selected Primary Dataset) | Dataset B (Eliminated) | **DATASET A** |

---

## 3. In-Depth Multi-Criteria Evaluation

### 3.1 Salary Quality and Usability (The Primary Regression Target)
The primary predictive analytics task is to predict normalized annual salary.
- **Dataset A** contains **107,151 postings with parsed salary data**. Crucially, every single one of these 107,151 records has **both** `salary_min` and `salary_max` populated, allowing precise calculation of `salary_midpoint = (salary_min + salary_max) / 2`. Furthermore, 71,822 postings are explicitly denominated per year (`salary_period == 'year'`), and 28,726 per hour (`hour`). In USD alone, Dataset A provides **92,713 valid salaries**, of which **25,008 belong directly to technical and analytical roles** (e.g., Software Engineers, Data Scientists, ML Engineers, Data Analysts, DevOps).
- **Dataset B** contains 52,106 records with at least one salary bound, but only 46,885 have both minimum and maximum values. More critically, only 19,039 records in Dataset B are annual salaries, and when subsetting to technical/data roles, only **4,107 postings** have annual salary (and only **3,798 in USD**).
- **Verdict:** Dataset A provides **over 6.5 times more technical annual salary observations** than Dataset B. This difference is decisive: training complex non-linear regressors (Random Forest, Gradient Boosting, MLP) on 4,000 noisy samples across multiple feature sets leads to severe variance and overfitting, whereas ~25,000 records provides sufficient power for cross-validation and hyperparameter tuning.

### 3.2 Skill Extraction and Archetype Discovery (RQ1 & RQ2)
- **Dataset A** includes a pre-extracted, controlled vocabulary of **101 standardized technology and business competencies** serialized across 239,252 postings (60.7% coverage). The skill frequencies mirror the modern tech industry stack:
  - Languages: Python (35,417), SQL (26,875), TypeScript (13,451), Java (11,426), Ruby (4,210), C++ (3,980)
  - Cloud & Infra: AWS (22,361), Azure (14,454), GCP (12,454), Kubernetes (13,193), Docker (9,561), CI/CD (18,063), DevOps (13,123)
  - AI / ML / Data: Machine Learning (17,598), LLM (17,130), Data Science (10,648), Data Engineering (10,576)
  - Business / Analytics: Project Management (48,625), Excel (42,353), Product Management (27,855), Salesforce (13,698), UI/UX (8,881)
- **Dataset B** provides an unstandardized list of 53,889 distinct tokens in `skills_required`. An empirical frequency scan shows that Dataset B is predominantly a general job board feed: its top skills are *customer service* (20,422), *inventory management* (7,395), *safety compliance* (7,252), *patient care* (3,802), and *cash handling* (3,555). Technical skills are severely underrepresented (Python: 2,577; SQL: 1,909; AWS: 1,215). Performing PCA and K-Means on Dataset B would produce non-technical clusters (e.g., Retail Cashiers vs Nurses vs Warehouse Stockers) rather than the specialized software and data archetypes required by the research brief.
- While Dataset B contains full `job_description` text (enabling TF-IDF), extracting skills from noisy retail descriptions yields extreme sparsity and does not compensate for the lack of actual tech job volume.

### 3.3 Experience Level Representation
- **Dataset B** contains an explicit `experience_level` column populated in 57.7% of rows (Mid: 38k, Entry: 17k, Senior: 8k).
- **Dataset A** does not feature a dedicated experience column. However, job title string parsing enables high-precision recovery of seniority tiers. In Dataset A:
  - `Senior / Sr / Principal / Staff` -> 36,336 postings (plus 7,221 in the tech USD salary subset)
  - `Lead / Manager / Director / VP / Head` -> 97,045 postings (plus 6,445 in tech USD)
  - `Junior / Entry / Associate / Trainee` -> 17,314 postings (plus 285 in tech USD)
  - `Intern / Internship / Co-op` -> 4,013 postings (plus 39 in tech USD)
  - `Mid / Standard Role` -> 239,592 postings (plus 11,018 in tech USD)
- Because seniority tiers in tech are heavily codified in the job title itself, engineering an explicit 5-tier seniority feature from `title` resolves the lack of a standalone experience column in Dataset A without loss of predictive signal.

### 3.4 Data Completeness, Quality, and Provenance
- **Dataset A** is an industry-grade package curated by DataForge. It includes:
  1. `DATA-DICTIONARY.md`: Exact data types, unique counts, and non-null percentages calculated at build time.
  2. `DATASHEET.md`: Standardized documentation covering motivation, collection mechanics (login-free ATS JSON endpoints across Greenhouse, Lever, Ashby, Workable, SmartRecruiters), rate limiting, PII sanitization, GDPR Art. 6(1)(f) compliance, and known platform biases.
  3. `checksums.txt`: SHA-256 hashes verifying data integrity.
  4. `LICENSE.md`: Formal Tier 1 Internal Analytics license.
- **Dataset B** is an unverified parquet dump with no documentation, no license, missing 93%+ of its industry and functional metadata, and lacking verifiable collection dates or sampling methodology.
- In an academic research submission, reproducibility and provenance are paramount. Dataset A provides unimpeachable documentation that can be directly cited.

---

## 4. Final Dataset Selection & Justification

### Selected Primary Dataset
> **Dataset A: Tech Job Postings with Parsed Salaries (ATS Direct)**  
> **Package Identifier:** `jobs-tier1-L-2026-08-01`  
> **Primary Storage Path:** `data/raw/dataset_A/data/jobs.parquet` (and `jobs.csv`)

### Alignment with the 10 Priority Criteria

1. **Salary Quality:** 107,151 records with dual min/max bounds; 27,295 annual tech salaries (25,008 USD) provide clean continuous target values without reliance on synthetic imputations.
2. **Skill Information:** 101 high-signal, controlled-vocabulary technology competencies directly aligned with modern predictive analytics, AI/ML, cloud, and software engineering.
3. **Job Title Coverage:** 394,300 standardized job titles with rich semantic variance, covering 91,378 tech titles that map cleanly into 8–12 standard role families.
4. **Experience Coverage:** Recoverable via robust regex parsing of job titles into 5 standard seniority tiers (Intern, Junior/Entry, Mid, Senior, Lead/Executive).
5. **Location Coverage:** 91.8% country resolution, 83.7% city resolution, and 100% binary remote-work indicator (`is_remote`).
6. **Data Completeness:** Zero nulls in core identifiers (`company_name`, `ats`, `job_id`, `title`, `url`, `is_remote`, `posted_at`).
7. **Provenance:** Peer-reviewed documentation standard (Datasheet for Datasets) with documented collection from 5 major enterprise ATS APIs.
8. **Suitability for PCA/K-Means (RQ2):** Clean binary/multi-hot skill representations ensure orthogonal component decomposition in PCA and well-separated, interpretable cluster centroids in K-Means.
9. **Suitability for Salary Regression (RQ1 & RQ3):** Sufficiently large sample size (N ≈ 25,000) prevents high-variance failure modes across complex models (Random Forest, Gradient Boosting, MLP) and provides adequate sub-sample sizes for per-archetype residual analysis (RQ3).
10. **Reproducibility:** SHA-256 checksums, fixed seeds, and transparent data dictionary allow examiners to verify every step end-to-end.

---

## 5. Formal Data Provenance

```text
Dataset Name:               Tech Job Postings with Parsed Salaries (ATS Direct)
Package / Version:          jobs-tier1-L-2026-08-01 (Version 1.0)
Release Date:               2026-08-01
Original Source:            Public ATS JSON endpoints (Greenhouse, Lever, Ashby, Workable, SmartRecruiters)
Creator / Vendor:           DataForge (pipelines/jobs v1.0)
Contact / Support:          data@dataforge.example
Source URL:                 Direct ATS endpoints: boards-api.greenhouse.io, api.lever.co, 
                            api.ashbyhq.com, apply.workable.com, api.smartrecruiters.com
License:                    DataForge Dataset License, Tier 1 (Internal Analytics)
Time Window Covered:        2020-01-01 to 2026-08-01
Geographic Scope:           65 countries (US: 39%, France: 9%, UK: 9%, etc.)
Original Rows:              394,300
Original Columns:           22
Collection Methodology:     Automated HTTP GET requests to public, login-free ATS JSON endpoints.
                            Adaptive per-domain rate limiting, User-Agent rotation, 
                            exponential backoff with Retry-After headers, and checkpointed collection.
Preprocessing by Source:    HTML stripped to plain text; locations parsed to ISO country + city;
                            employment types normalized; salaries parsed from structured ATS fields
                            supplemented by regularized text extraction; duplicate job_ids collapsed.
Attribution Requirements:   Cite DataForge and refer to LICENSE.md (Schedule B). 
                            No PII present; compliance with GDPR Art. 6(1)(f) legitimate interests.
```

---

## 6. Phase 1 Gate Sign-Off & Next Steps

- [x] **Gate 1 Verified:** Candidate datasets audited objectively; comparison metrics compiled from raw files; primary dataset selected and justified against all project requirements; formal provenance documented.
- **Next Phase (Phase 2):** Implement data cleaning, role family mapping (~8–12 categories), seniority extraction, salary normalization (USD annual midpoint), multi-hot skill matrix generation, and export `cleaned_jobs.parquet` and `modeling_dataset.parquet`.
