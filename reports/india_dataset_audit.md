# JOBINTEL — PHASE INDIA-1: DATASET AUDIT & REPOSITORY INTEGRATION REPORT
## Comprehensive Pre-Modeling Audit: Indian Job Market Dataset (2025) & SQL Reference Analysis

---

## EXECUTIVE SUMMARY

| Audit Attribute | Empirical Finding / Specification | Status |
| :--- | :--- | :--- |
| **Existing USA System** | Phases 1–6 Analytical Engine + Phase 7.2 Full-Stack Product (React + FastAPI) | **STRICTLY FROZEN** |
| **Primary India Dataset** | `data/raw/india/indian-job-market-dataset-2025.xlsx` (`31,709,363 bytes`, 1 sheet: `Sheet1`) | **VERIFIED ON DISK** |
| **Total Raw Records** | **97,929 rows** × **17 columns** | **AUDITED** |
| **Primary Currency** | `INR`: **97,800** (99.87%), `USD`: **129** (0.13%) | **CURRENCY SEGREGATED** |
| **Salary Disclosure Rate** | **33.93%** disclosed positive salary ranges (**33,229 rows**), 65.43% "Not disclosed" | **CONFIRMED** |
| **INR Usable Salary Cohort** | **33,116 rows** with positive INR min/max salary ranges and valid experience | **ISOLATED** |
| **Reference SQL Logic** | 7 SQL scripts in `data/raw/india_reference/` (Naukri-analytical queries) | **ANALYZED & MAPPED** |
| **Model Training Status** | **ZERO TRAINING EXECUTED** (Complies with Phase India-1 audit-only mandate) | **APPROVED** |

---

## A. EXISTING USA ARCHITECTURE

The current JobIntel application operates as a full-stack, decoupled architecture constructed across Phases 1 through 7.2:

```
                          JOBINTEL ARCHITECTURE
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          │                                                   │
    PRESENTATION LAYER                                ANALYTICAL BACKEND
  React 19 + Vite (TypeScript)                      FastAPI (Python Service)
  Port: 5173 · 312 kB Bundle                        Port: 8000 · LRU Cached
  Dark Graphite (`#08090D`)                         Pydantic V2 Schemas
  Atmospheric Multi-Color Drift                     18 REST Endpoints
          │                                                   │
          └─────────────────────────┬─────────────────────────┘
                                    │
                        FROZEN USA ML ENGINE (USD)
                     XGBRegressor (Optuna-Tuned)
                   Cohort: 34,036 Rows · Holdout: 6,808
                    MAE: $36,380.64 · R²: 0.4233
                     PCA (15 dims) + KMeans (k=7)
                      7 Discovered Job Archetypes
```

The presentation layer abstracts the analytical pipeline via REST endpoints, allowing seamless dual-engine expansion (USA USD Engine vs. India INR Engine) without breaking any existing interfaces.

---

## B. EXISTING USA ASSETS THAT MUST REMAIN FROZEN

The following assets are **100% frozen** and must never be altered, overwritten, or retrained during India expansion:

1. **Raw Datasets (`data/raw/`):**
   - `data/raw/dataset_A/`
   - `data/raw/dataset_B/`
2. **Processed Datasets (`data/processed/`):**
   - `cleaned_jobs.parquet` (`335,995 rows`)
   - `modeling_dataset.parquet` (`34,036 rows`, 123 explicit features)
   - `skill_matrix.parquet` & `skill_matrix_*.parquet` (`116,830 rows`, Taxonomy D)
   - `job_archetype_assignments.parquet` (7 latent archetypes)
   - `phase2_1_metrics.json`
3. **Model & Pipeline Artifacts (`models/`):**
   - `models/phase5/best_model.pkl` (XGBoost Regressor)
   - `models/phase5/best_pipeline.pkl` (`MetadataTransformer`)
   - `models/phase5/feature_metadata.json`
   - `models/scaler_phase4_1.pkl`
   - `models/pca_phase4_1.pkl`
   - `models/kmeans_phase4_1_k7.pkl`
4. **USA Source Pipeline Modules (`src/`):**
   - `src/phase5/` (`train.py`, `eval.py`, `interpretability.py`, `preprocessing.py`)
   - `src/rebuild_phase2_1.py`, `src/run_phase3_eda.py`, `src/run_phase4_1_archetype_correction.py`, `src/run_phase5_experiments.py`
5. **Research Tables & Reports (`reports/`):**
   - `reports/tables/phase1/` through `phase6/` (All 22 validated CSV tables)
   - `reports/phase5_executive_summary.md`, `reports/phase5_model_card.md`, `reports/phase6_final_research_synthesis.md`, `reports/phase7_2_frontend_reconstruction_audit.md`

---

## C. INDIA DATASET LOCATION & PROVENANCE

- **Physical File Path:** `data/raw/india/indian-job-market-dataset-2025.xlsx`
- **File Size:** `31,709,363 bytes` (~31.7 MB)
- **Format:** Microsoft Excel OpenXML Spreadsheet (`.xlsx`), Single Sheet: `Sheet1`
- **Integrity Check:** Read successfully with `openpyxl` engine; zero truncated blocks.
- **Reference SQL Location:** `data/raw/india_reference/` (7 reference queries).

---

## D. INDIA DATASET SCHEMA

The raw Excel file contains **17 columns** with zero structural schema defects:

| Column Name | Inferred Dtype | Null Count | Null % | Unique Count | Semantic Description |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `title` | `object` | 0 | 0.00% | 55,104 | Raw job advertisement title |
| `jobId` | `int64` | 0 | 0.00% | 97,679 | Unique job posting identifier |
| `currency` | `object` | 0 | 0.00% | 2 | Currency code (`INR` or `USD`) |
| `jobUploaded` | `object` | 0 | 0.00% | 30 | Posting freshness (e.g. "6 Days Ago", "30+ Days Ago") |
| `companyName` | `object` | 4 | 0.00% | 18,668 | Hiring organization name |
| `tagsAndSkills` | `object` | 571 | 0.58% | 84,307 | Comma-delimited skill list |
| `experience` | `object` | 2,105 | 2.15% | 287 | Textual experience range (e.g. "2-4 Yrs") |
| `salary` | `object` | 0 | 0.00% | 1,339 | Textual salary string (e.g. "3-5 Lacs PA", "Not disclosed") |
| `location` | `object` | 0 | 0.00% | 10,066 | Freeform location string (e.g. "Bengaluru", "Hybrid - Pune") |
| `companyId` | `int64` | 0 | 0.00% | 18,328 | Numeric company identifier |
| `ReviewsCount` | `float64` | 35,252 | 36.00% | 1,375 | Glassdoor/portal review count |
| `AggregateRating` | `float64` | 35,252 | 36.00% | 41 | Employer star rating (1.0 to 5.0) |
| `jobDescription` | `object` | 0 | 0.00% | 80,679 | Detailed textual job description |
| `minimumSalary` | `float64` | 571 | 0.58% | 164 | Lower bound annual compensation (INR) |
| `maximumSalary` | `float64` | 571 | 0.58% | 204 | Upper bound annual compensation (INR) |
| `minimumExperience`| `float64` | 571 | 0.58% | 31 | Minimum required years of experience |
| `maximumExperience`| `float64` | 571 | 0.58% | 33 | Maximum required years of experience |

---

## E. INDIA DATA QUALITY SUMMARY & EMPIRICAL FINDINGS

### 1. Duplication & Identifier Integrity
- **Exact Duplicate Rows:** 247 rows (0.25% of corpus).
- **Duplicate `jobId`s:** 250 duplicate IDs across 97,929 rows (97,679 unique IDs).
- **Content Duplicates (`title`, `companyName`, `location`, `salary`, `experience`):** 9,758 rows (9.96%). Represents recurring recruitment openings for high-volume roles (e.g. Accenture Application Developers).

### 2. Currency Breakdown
- **INR:** **97,800** (99.87%)
- **USD:** **129** (0.13%)
- *Decision:* All 129 USD postings must be excluded from the domestic India INR modeling dataset to prevent severe currency mixing.

### 3. Salary Disclosure & Range Semantics
- **Text `salary` Column:**
  - `"Not disclosed"`: **64,076 rows** (65.43% of total corpus).
  - `"Unpaid"`: **333 rows**.
  - Disclosed Text Ranges: **33,520 rows** (e.g. "3-5 Lacs PA", "10-20 Lacs PA", "50,000-3 Lacs PA").
- **Numeric Fields (`minimumSalary`, `maximumSalary`):**
  - Stored in **Annual INR** (e.g. "3-5 Lacs PA" maps to `min=300,000`, `max=500,000`).
  - Rows where min/max are `0.0`: **64,129 rows** (65.49%). This confirms that non-disclosed salaries are encoded as `0`.
  - Rows with strictly positive, valid ranges (`minimumSalary > 0` and `maximumSalary >= minimumSalary`): **33,229 rows** (33.93%).
  - Negative values or `min > max` anomalies: **0 rows** (0.0%).
- **Empirical Salary Distribution (Disclosed Positive Cohort, N = 33,229):**
  - Minimum Midpoint: ₹786 (anomalous entry/stipend)
  - 25th Percentile (Q1): **₹287,500** (₹2.88 LPA)
  - **Median Midpoint:** **₹425,000** (**₹4.25 LPA**)
  - 75th Percentile (Q3): **₹825,000** (**₹8.25 LPA**)
  - Interquartile Range (IQR): **₹537,500** (₹5.38 LPA)
  - Mean Midpoint: **₹757,087** (~₹7.57 LPA) — Heavily right-skewed
  - Maximum Midpoint: ₹82,500,000 (₹825 LPA — executive outlier)
  - Postings under 1 LPA (₹100,000): **456 rows** (clerical/internship stipends)
  - Postings over 50 LPA: **218 rows** (executive/niche tech)
  - Postings over 100 LPA: **18 rows**

### 4. Experience Distribution
- `minimumExperience` Range: 0 to 30 years (Median = 3.0, Mean = 3.51).
- `maximumExperience` Range: 0 to 35 years (Median = 7.0, Mean = 7.37).
- Both numeric bounds valid: **97,358 rows** (99.42%).
- Anomalies where `min_exp > max_exp`: **0 rows**.
- Postings with >30 years experience: **23 rows**.

### 5. Geographic Coverage
- Top Metros in Raw Corpus (10,066 distinct strings):
  - **Bengaluru:** 16,823 (17.2%) + Hybrid: 946
  - **Hyderabad:** 7,669 (7.8%) + Hybrid: 576
  - **Pune:** 6,112 (6.2%) + Hybrid: 480
  - **Chennai:** 4,431 (4.5%)
  - **Gurugram:** 4,233 (4.3%)
  - **Mumbai & MMR (Mumbai, Navi Mumbai, Thane):** 6,020 (6.1%)
  - **Noida:** 2,695 (2.8%)
  - **Remote:** 1,961 (2.0%)

### 6. Domain Composition: Tech vs. Non-Tech
- The raw dataset is a **multi-industry Indian job corpus**:
  - Tech Titles: **39,450 rows** (40.28% of corpus).
  - Non-Tech Titles: Sales, Customer Service, HR, Accounting, Nursing, Civil/Site Engineering.
- In the disclosed INR salary cohort (N = 33,116):
  - Software/Data/AI/Cloud tech roles account for **9,146 rows** (27.5%).
  - Median tech salary: **₹6.50 LPA** (vs. Non-tech median: **₹3.88 LPA**).
  - Clear tech wage premium observed (**+67.5% premium**).

---

## F. SQL REFERENCE ANALYSIS

The 7 SQL files located in `data/raw/india_reference/` provide verified analytical specifications:

| SQL File | Analytical Intent | Input Columns Expected | Aggregations / Filters Applied |
| :--- | :--- | :--- | :--- |
| `postings_by_city.sql` | Geographic demand concentration across top 15 metros | `city` | `COUNT(*)`, percentage share, `WHERE city IS NOT NULL` |
| `postings_by_role.sql` | Macro demand volume across functional role categories | `role_category` | `COUNT(*)` grouped by role category |
| `salary_by_experience.sql` | Experience wage curve across seniority bands | `experience_band`, `salary_lpa` | `AVG(salary_lpa)` grouped by `experience_band` |
| `salary_by_role.sql` | Disclosed compensation variance by role category | `role_category`, `salary_lpa` | `AVG`, `MIN`, `MAX(salary_lpa)`, `HAVING COUNT(*) >= 5` |
| `salary_by_city_analyst.sql` | Geographic compensation benchmarking for Analyst cohort | `city`, `role_category`, `salary_lpa` | `AVG(salary_lpa)` filtered to Data/Business Analysts |
| `top_skills_by_role.sql` | Relational skill demand matrix per role category | `role_category`, `skill` | `COUNT(*)` from `job_skills` joined to `job_postings` |
| `job_market_analysis.sql` | Master script consolidating all 5 analytical views | All of the above | Comprehensive macro analysis |

---

## G. SCHEMA MAPPING: SQL CONCEPTS → ACTUAL INDIA EXCEL SCHEMA

The supplied SQL assumes a clean, normalized relational schema (`job_postings`, `job_skills`, `salary_lpa`, `experience_band`, `role_category`, `city`). The actual Excel dataset has a flatter, unnormalized structure:

```
    SQL SCHEMA ASSUMPTION                        EXCEL RAW DATASET (ACTUAL)
    ─────────────────────                        ──────────────────────────
    job_postings.job_id         ───────►         jobId (int64)
    job_postings.city           ───────►         location (string) ──► normalized_city
    job_postings.salary_lpa     ───────►         minimumSalary, maximumSalary ──► (min+max)/200,000
    job_postings.experience_band ──────►         minimumExperience, maximumExperience ──► binned bands
    job_postings.role_category  ───────►         title (string) ──► normalized_role_family
    job_skills.skill            ───────►         tagsAndSkills (comma-separated string) ──► unnested
```

### Deterministic Transformation Rules for India Schema:
1. **Target Construction (`salary_lpa` & `salary_midpoint_inr`):**
   $$\text{salary\_midpoint\_inr} = \frac{\text{minimumSalary} + \text{maximumSalary}}{2}$$
   $$\text{salary\_lpa} = \frac{\text{salary\_midpoint\_inr}}{100,000}$$
   *Constraint:* Fit only where `currency == 'INR'`, `minimumSalary > 0`, and `maximumSalary >= minimumSalary`.
2. **Experience Banding (`experience_band`):**
   $$\text{exp\_midpoint} = \frac{\text{minimumExperience} + \text{maximumExperience}}{2}$$
   - `0 - 2 Yrs (Entry)`: `exp_midpoint < 3`
   - `3 - 5 Yrs (Mid)`: `3 <= exp_midpoint < 6`
   - `6 - 10 Yrs (Senior)`: `6 <= exp_midpoint < 11`
   - `11+ Yrs (Lead / Principal)`: `exp_midpoint >= 11`
3. **Location Normalization (`normalized_city`):**
   - Extract primary metro from compound strings (e.g., `"Bengaluru"`, `"Hybrid - Bengaluru"`, `"Bangalore/Bengaluru"` → `Bengaluru`).
   - Group Delhi NCR (`Noida`, `Gurugram`, `Delhi` → `Delhi NCR`).
   - Standardize Mumbai MMR (`Navi Mumbai`, `Thane`, `Mumbai` → `Mumbai MMR`).
4. **Role Normalization (`normalized_role`):**
   - Deterministic regex matcher classifying raw `title` into standardized families:
     - `AI / ML Engineer`
     - `Data Engineer`
     - `Data / Business Analyst`
     - `Software Development Engineer (Backend / Core)`
     - `Frontend / Web Developer`
     - `Full Stack Developer`
     - `Cloud / DevOps Engineer`
     - `QA / Automation Engineer`
     - `Product / Technical Program Manager`
5. **Skill Bridge Table (`job_skills`):**
   - Explode `tagsAndSkills` on comma delimiters, apply casing normalization, strip whitespace, and deduplicate to form a clean `(jobId, skill)` relational mapping for SQL compliance.

---

## H. PROPOSED INDIA DIRECTORY STRUCTURE

All India code, data, models, and reports must be completely partitioned into their own dedicated namespaces:

```text
Job Market/
├── data/
│   ├── raw/
│   │   ├── dataset_A/              <-- FROZEN USA
│   │   ├── dataset_B/              <-- FROZEN USA
│   │   ├── india/
│   │   │   └── indian-job-market-dataset-2025.xlsx  <-- PRIMARY SOURCE
│   │   └── india_reference/
│   │       └── *.sql               <-- REFERENCE SQL
│   └── processed/
│       ├── ... (USA parquets) ...  <-- FROZEN USA
│       └── india/
│           ├── cleaned_india_jobs.parquet
│           ├── india_modeling_cohort.parquet
│           ├── india_skill_matrix.parquet
│           └── india_taxonomy.json
├── src/
│   ├── phase5/                     <-- FROZEN USA
│   ├── backend/                    <-- UNIFIED BACKEND
│   │   ├── routers/
│   │   │   ├── ... (USA routers) ...
│   │   │   └── india_predict.py    <-- NEW DEDICATED ROUTER
│   │   └── services/
│   └── india/                      <-- DEDICATED INDIA MODULES
│       ├── __init__.py
│       ├── audit.py
│       ├── cleaning.py
│       ├── taxonomy.py
│       ├── role_mapping.py
│       ├── cohort.py
│       ├── eda.py
│       └── modeling.py
├── models/
│   ├── phase5/                     <-- FROZEN USA
│   └── india/
│       ├── best_india_model.pkl
│       ├── india_feature_pipeline.pkl
│       └── india_metadata.json
├── reports/
│   ├── tables/
│   │   ├── phase1/ - phase6/       <-- FROZEN USA
│   │   └── india/
│   ├── figures/
│   │   └── india/
│   ├── india_dataset_audit.md      <-- THIS REPORT
│   ├── india_preprocessing.md
│   └── india_model_card.md
└── sql/
    └── india/
        └── executed_queries/       <-- ADAPTED, WORKING SQL QUERIES
```

---

## I. POTENTIAL RISKS & METHODOLOGICAL SAFEGUARDS

1. **Salary Disclosure Selection Bias:**
   - 65.43% of Indian postings do not disclose salary.
   - *Safeguard:* Transparently document in the Model Card that the India model predicts compensation within the *disclosed salary market*. Compare disclosed vs. non-disclosed distributions across company size, role, and city.
2. **Currency Mixing (USD vs. INR):**
   - 129 postings are denominated in USD (e.g. US remote contracts).
   - *Safeguard:* Strictly filter `currency == 'INR'`. Zero USD records will enter the training cohort.
3. **Clerical / Extreme Salary Outliers:**
   - Salaries under ₹1 LPA (₹10,000 - ₹50,000) represent internships or data-entry stipends.
   - *Safeguard:* Establish a verified domain boundary (e.g. ₹1.2 LPA to ₹80 LPA) backed by distributional quantiles.
4. **Target Leakage:**
   - Neither `minimumSalary`, `maximumSalary`, nor any binned salary derivative may ever be exposed as input features.
5. **Multi-Industry Dilution:**
   - Over 55% of the raw corpus represents non-tech roles (e.g., retail sales, nursing, civil site engineering).
   - *Safeguard:* Isolate a dedicated Technology Cohort for technical salary intelligence, ensuring high predictive fidelity for technology careers.

---

## J. RECOMMENDED NEXT STEPS: INDIA PHASE 1 ROADMAP

```
                    INDIA WORKFLOW PROGRESSION
                                │
    [✓] PHASE INDIA-1: DATASET AUDIT & REPOSITORY INTEGRATION
        • Raw Excel audited (97,929 rows, 17 cols)
        • Schema verified, duplicates and missingness cataloged
        • Reference SQL analyzed and mapped
                                │
                                ▼
    [ ] PHASE INDIA-2: SCHEMA NORMALIZATION & SQL LOGIC EXECUTION
        • Build src/india/cleaning.py
        • Generate normalized fields (normalized_city, role_family, experience_band, salary_lpa)
        • Execute and validate the 7 SQL reference analyses against India data
        • Export SQL benchmark tables to reports/tables/india/
                                │
                                ▼
    [ ] PHASE INDIA-3: SKILL & ROLE TAXONOMY ENGINEERING
        • Build deterministic India tech taxonomy (Top 100+ validated skills)
        • Construct role-family classifier for software, data, AI, cloud, and engineering
                                │
                                ▼
    [ ] PHASE INDIA-4: MODELING COHORT CONSTRUCTION & EDA
        • Apply defensive cohort filters (INR only, tech/relevant, verified bounds)
        • Save data/processed/india/india_modeling_cohort.parquet
        • Perform bivariate EDA (Salary vs Role, Experience, City, Skills)
                                │
                                ▼
    [ ] PHASE INDIA-5: SUPERVISED MODELING & CROSS-VALIDATION
        • Evaluate candidate regressors (Ridge, Random Forest, XGBoost)
        • 5-Fold Cross Validation with zero leakage
        • Evaluate MAE (in INR / LPA) and R²
                                │
                                ▼
    [ ] PHASE INDIA-6: PRODUCT & API INTEGRATION
        • Expose /api/india/predict on FastAPI
        • Update React frontend with [ USA ] [ INDIA ] country selector
```

---

## CONCLUSION

The India dataset has been thoroughly inspected and audited. The existing USA research assets remain untouched and completely frozen. We are now ready to proceed to **Phase India-2 (Schema Normalization & SQL Execution)** upon your command.
