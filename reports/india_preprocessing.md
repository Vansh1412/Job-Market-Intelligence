# JOBINTEL — PHASE INDIA-2: PREPROCESSING & SCHEMA NORMALIZATION REPORT
## Comprehensive Technical Lineage, Transformation Logic, and Analytical Architecture

---

## 1. EXECUTIVE OVERVIEW

This document establishes the official data lineage, schema normalization rules, and architectural definitions for the **JobIntel India Analytical Pipeline** (Phase India-2).

All transformations were developed under strict adherence to the **USA Isolation Directive**:
- Zero USA models, datasets, pipelines, or reports were modified.
- All India analytical logic resides within dedicated namespaces (`src/india/`, `data/processed/india/`, `sql/india/`, `reports/tables/india/`).
- Zero machine learning model training was performed in this phase.
- No arbitrary salary truncation was imposed on the analytical layer.

---

## 2. DATA PROVENANCE & PRIMARY SOURCE

- **Primary Data Source:** `data/raw/india/indian-job-market-dataset-2025.xlsx`
- **File Format:** Single OpenXML Sheet (`Sheet1`), 17 columns
- **Raw Observations ($N$):** **97,929 rows**
- **Raw File Integrity:** Verified on disk (`31,709,363 bytes`), zero corrupted rows.
- **Reference SQL Source:** `data/raw/india_reference/` (7 analytical queries).

---

## 3. MASTER TARGET ANALYTICAL SCHEMA

The pipeline establishes a clean, decoupled analytical data layer in `data/processed/india/`:

```
data/processed/india/
├── cleaned_india_jobs.parquet       (97,929 rows × 31 columns — complete provenance master)
├── india_job_postings.parquet       (97,679 rows × 31 columns — deduplicated analytical entity)
├── india_job_skills.parquet         (751,947 rows × 2 columns — relational bridge table)
└── india_taxonomy.json              (Taxonomy metadata, alias dictionary, frequency mappings)
```

### Schema Field Definitions (`cleaned_india_jobs.parquet` & `india_job_postings.parquet`)

| Target Field | Data Type | Source Field | Transformation & Semantic Meaning |
| :--- | :---: | :--- | :--- |
| `job_id` | `int64` | `jobId` | Primary recruitment identifier |
| `original_title` | `string` | `title` | Preserved raw job title string |
| `company_name` | `string` | `companyName` | Hiring organization name |
| `company_id` | `int64` | `companyId` | Source employer identifier |
| `original_location`| `string` | `location` | Preserved freeform location text |
| `normalized_city` | `string` | `location` | Primary metropolitan hub extracted via deterministic regex rule |
| `normalized_state`| `string` | `location` | Indian state / union territory derived from recognized city |
| `city` | `string` | Derived | Alias to `normalized_city` for exact ANSI SQL compatibility |
| `state` | `string` | Derived | Alias to `normalized_state` for SQL compatibility |
| `currency` | `string` | `currency` | Currency denomination (`INR` or `USD`) |
| `original_salary` | `string` | `salary` | Preserved textual salary description |
| `minimum_salary_inr`| `float64`| `minimumSalary`| Annual lower bound in INR (NULL if undisclosed or non-INR) |
| `maximum_salary_inr`| `float64`| `maximumSalary`| Annual upper bound in INR (NULL if undisclosed or non-INR) |
| `salary_midpoint_inr`| `float64`| Derived | $(\text{min} + \text{max}) / 2.0$ (Annual INR) |
| `salary_lpa` | `float64`| Derived | $\text{salary\_midpoint\_inr} / 100,000.0$ (Lacs Per Annum) |
| `original_experience`| `string` | `experience` | Preserved raw textual experience range |
| `minimum_experience`| `float64`| `minimumExperience`| Lower bound required experience (years) |
| `maximum_experience`| `float64`| `maximumExperience`| Upper bound required experience (years) |
| `experience_midpoint`| `float64`| Derived | $(\text{min} + \text{max}) / 2.0$ (years) |
| `experience_band` | `string` | Derived | Seniority cohort: `0-2 Yrs (Entry)`, `3-5 Yrs (Mid)`, etc. |
| `normalized_role` | `string` | `title` | One of 15 standardized role families |
| `role_category` | `string` | Derived | Alias to `normalized_role` for exact ANSI SQL compatibility |
| `is_tech_role` | `bool` | `title`, `tagsAndSkills`| Deterministic technology domain indicator |
| `tags_and_skills` | `string` | `tagsAndSkills`| Comma-delimited skill list |
| `job_description` | `string` | `jobDescription`| Full textual job description |
| `job_uploaded` | `string` | `jobUploaded`| Freshness indicator (e.g. "6 Days Ago") |
| `reviews_count` | `float64`| `ReviewsCount` | Employer review count |
| `aggregate_rating`| `float64`| `AggregateRating`| Employer star rating (1.0 to 5.0) |
| `is_salary_valid` | `bool` | Derived | `currency == 'INR'` AND $\text{min} > 0$ AND $\text{max} \ge \text{min}$ |
| `is_inr` | `bool` | `currency` | Indicates domestic Indian rupee denomination |
| `is_exact_duplicate`| `bool` | All cols | Identifies complete row duplicate across all 17 columns |
| `is_jobid_duplicate`| `bool` | `jobId` | Identifies recurring job ID |
| `is_content_duplicate`| `bool`| 5 core cols | Identifies identical (title, company, location, salary, exp) |
| `is_analytical_eligible`| `bool`| Derived | `is_inr == True` AND `is_exact_duplicate == False` |

---

## 4. DETAILED TRANSFORMATION RULES

### A. Duplicate Handling
1. **Exact Duplicate Rows:** 247 rows (0.25%) share identical values across all 17 raw columns. Marked with `is_exact_duplicate = True`.
2. **Duplicate Job IDs:** 250 duplicate `jobId` instances exist in the raw dataset.
   - 247 are exact duplicates.
   - 3 instances represent identical job requirements posted across multiple locations.
3. **Analytical Resolution:**
   - In `cleaned_india_jobs.parquet`, all 97,929 rows are retained with provenance flags.
   - In `india_job_postings.parquet`, deduplication by `job_id` produces **97,679 unique job postings**, ensuring `job_id` serves as a clean primary key for relational joins without Cartesian fan-out.

### B. Currency & Salary Normalization
1. **Currency Segregation:**
   - `INR`: 97,800 rows (99.87%).
   - `USD`: 129 rows (0.13%).
   - All 129 USD rows are flagged (`is_inr = False`) and strictly excluded from domestic INR salary analysis. No artificial foreign exchange conversion is applied.
2. **Undisclosed Salary Encoding:**
   - 64,121 rows have `minimumSalary == 0.0` and `maximumSalary == 0.0` (matching the 64,076 `"Not disclosed"` text postings).
   - In accordance with the Salary Disclosure Rule, undisclosed salaries are set to `NULL` / `NaN`. They are **never** treated as ₹0 salary.
3. **Midpoint & LPA Computation:**
   $$\text{salary\_midpoint\_inr} = \frac{\text{minimumSalary} + \text{maximumSalary}}{2.0}$$
   $$\text{salary\_lpa} = \frac{\text{salary\_midpoint\_inr}}{100,000.0}$$
   - Fit strictly when `currency == 'INR'`, $\text{minimumSalary} > 0$, and $\text{maximumSalary} \ge \text{minimumSalary}$.
   - Result: Exactly **33,116 valid INR salary records** in the deduplicated analytical corpus (matching the Phase India-1 audit).

### C. Experience Normalization
1. **Coverage:** 99.42% of postings have valid numeric bounds. Zero instances of `min > max` exist.
2. **Midpoint Formula:**
   $$\text{experience\_midpoint} = \frac{\text{minimumExperience} + \text{maximumExperience}}{2.0}$$
3. **Standardized Seniority Bands:**
   - **`0-2 Yrs (Entry)`:** $\text{midpoint} \le 2.0$ ($N = 14,657$ total; $N = 7,511$ with salary)
   - **`3-5 Yrs (Mid)`:** $2.0 < \text{midpoint} \le 5.0$ ($N = 34,928$ total; $N = 14,243$ with salary)
   - **`6-10 Yrs (Senior)`:** $5.0 < \text{midpoint} \le 10.0$ ($N = 35,945$ total; $N = 8,483$ with salary)
   - **`11+ Yrs (Lead / Principal)`:** $\text{midpoint} > 10.0$ ($N = 11,828$ total; $N = 2,879$ with salary)

### D. Geographic Normalization & State Mapping
1. **Freeform Variation:** The raw dataset contains 10,066 distinct location strings.
2. **Primary-City Extraction Rule:**
   - Prefixes such as `"Hybrid - "` and `"Remote - "` are stripped.
   - For compound multi-city strings (e.g., `"Hyderabad, Chennai, Bengaluru"`), the string is tokenized by delimiter (`,` or `/`). The first recognized metropolitan entity is deterministically extracted as the primary job location.
   - Pure `"Remote"` postings are assigned to `city = "Remote"`.
3. **State Resolution:** A deterministic 45-city geographical mapping assigns `normalized_state` without hallucination. Coverage: 100.0% for cities, 89.01% for states.

### E. Deterministic Role Normalization & Tech Classification
1. **Ordered Rule Precedence:** Titles are matched hierarchically to avoid broad substring misclassification:
   1. `AI / ML Engineer`: LLM, GenAI, Machine Learning, Deep Learning, NLP, Computer Vision, MLOps.
   2. `Data Scientist`: Data Scientist, Lead/Principal/Applied Scientist.
   3. `Data Engineer`: Data Engineer, Big Data, ETL, PySpark, Snowflake, Databricks, DWH.
   4. `Data Analyst`: Data Analyst, Business Intelligence, Tableau/Power BI Analyst, Quant Analyst.
   5. `Business Analyst`: Business Analyst, Functional Analyst, IT Business Analyst, Systems Analyst.
   6. `Database Administrator`: DBA, SQL Developer, Database Administrator, PL/SQL, Oracle Developer.
   7. `Cloud / DevOps`: DevOps, Cloud Engineer, SRE, AWS/Azure Engineer, Infrastructure, Platform.
   8. `Cybersecurity`: Cybersecurity, Infosec, SOC Analyst, Security Engineer, Penetration Tester.
   9. `Full Stack Developer`: Full Stack, Fullstack, MERN/MEAN Stack.
   10. `Frontend Developer`: Frontend, UI Developer, Web Developer, React/Angular/Vue Developer.
   11. `QA / Testing`: QA, Quality Assurance, SDET, Test Engineer, Automation Tester.
   12. `Product / Program Manager`: Product Manager, Product Owner, Technical Program Manager, Scrum Master.
   13. `Software Engineer`: Software Engineer, Application Developer, Application Lead, SDE, Java/Python/.NET Developer.
   14. `Other Technology`: SAP, ERP, IT Support, Technical Support, Network Engineer, Hardware, Telecom.
   15. `Non-Tech`: Sales, BPO, HR, Accounting, Marketing, Nursing, Civil/Site Engineering.
2. **Tech Domain Indicator (`is_tech_role`):**
   - Classified as `True` for Roles 1 through 14 (excluding non-tech engineers such as civil/mechanical site engineers).
   - Classified as `False` for Role 15 (`Non-Tech`).

### F. Skill Extraction & Bridge Table (`job_skills`)
1. **Source:** `tagsAndSkills` (comma-delimited).
2. **Normalization Protocol:**
   - Lowercasing, leading/trailing whitespace stripping, punctuation stripping.
   - Technology alias consolidation:
     - Cloud: `amazon web services` $\rightarrow$ `aws`; `microsoft azure`, `ms azure` $\rightarrow$ `azure`; `google cloud platform` $\rightarrow$ `gcp`; `k8s` $\rightarrow$ `kubernetes`.
     - Frameworks: `react.js`, `reactjs`, `react js` $\rightarrow$ `react`; `nodejs`, `node js` $\rightarrow$ `node.js`; `vuejs`, `vue` $\rightarrow$ `vue.js`; `angularjs` $\rightarrow$ `angular`.
     - Data: `powerbi`, `ms power bi` $\rightarrow$ `power bi`; `ml` $\rightarrow$ `machine learning`; `nlp`, `natural language processing` $\rightarrow$ `nlp`; `mssql`, `ms sql` $\rightarrow$ `sql server`; `pyspark` $\rightarrow$ `spark`.
     - APIs: `restful api`, `restful apis`, `rest` $\rightarrow$ `rest api`; `micro services` $\rightarrow$ `microservices`.
3. **Bridge Table Creation:**
   - Extracted to `india_job_skills.parquet` with columns `(job_id, skill)`.
   - **Zero duplicate pairs** per job.
   - Total rows: **751,947 rows** across 97,108 jobs with skills.
   - Unique normalized skills: **43,947**.

---

## 5. REPRODUCIBILITY INSTRUCTIONS

The entire Phase India-2 pipeline is 100% automated and reproducible via terminal commands:

```bash
# 1. Run Data ETL and Generate Parquet Analytical Tables
python -m src.india.cleaning

# 2. Execute Adapted SQL Layer & Perform Independent Validations
python -m src.india.execute_and_validate_sql
```

Zero manual copy-pasting, zero GUI interaction, and zero hidden notebook state are required.
