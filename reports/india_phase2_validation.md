# JOBINTEL — PHASE INDIA-2: SCHEMA NORMALIZATION & SQL INTEGRATION VALIDATION REPORT
## Comprehensive Pre-Modeling Verification & Empirical Audit

---

## EXECUTIVE SUMMARY & STATUS

| Metric / Dimension | Specification / Value | Validation Status |
| :--- | :--- | :---: |
| **Phase India-2 Status** | Schema Normalization + SQL Integration | **GREEN (100% COMPLETE)** |
| **Raw Source Observations** | `data/raw/india/indian-job-market-dataset-2025.xlsx` | **97,929 rows** |
| **Master Cleaned Dataset** | `data/processed/india/cleaned_india_jobs.parquet` | **97,929 rows** |
| **Analytical Postings Entity** | `data/processed/india/india_job_postings.parquet` | **97,679 rows** |
| **Relational Skill Pairs** | `data/processed/india/india_job_skills.parquet` | **751,947 rows** |
| **Valid INR Disclosed Salaries** | Positive INR compensation cohort | **33,116 rows** |
| **Unique Normalized Skills** | Vocabulary after cleaning and alias consolidation | **43,947 skills** |
| **Standardized Role Families** | Deterministic title classification | **15 families** |
| **SQL Analyses Executed** | Adapted from `data/raw/india_reference/` | **7 / 7 PASS** |
| **Independent Validations** | SQL results vs. Pure Pandas verification | **7 / 7 PASS** |
| **Mandatory Cross-Checks** | Section 22 integrity assertions | **10 / 10 PASS** |
| **USA Assets Modified** | USA pipelines, models, data, reports | **0 (STRICTLY FROZEN)** |
| **Models Trained** | Pre-modeling compliance | **0 (ZERO TRAINING)** |
| **Phase India-3 Readiness** | Feature engineering and modeling cohort definition | **APPROVED (YES)** |

---

## 1. INPUT DATASET

- **File Path:** `data/raw/india/indian-job-market-dataset-2025.xlsx`
- **File Size:** `31,709,363 bytes` (~31.7 MB)
- **Format:** Single-sheet OpenXML spreadsheet (`Sheet1`)
- **Origin:** Real 2025 Indian recruitment postings corpus
- **Reference SQL Directory:** `data/raw/india_reference/` (7 reference queries preserved untouched)

---

## 2. RAW ROW COUNT

- **Total Ingested Rows:** **97,929**
- **Total Columns:** **17**
- **Completeness:** Zero missing values in `jobId`, `title`, `currency`, `location`, `companyId`, `salary`, or `jobDescription`.

---

## 3. CLEAN ROW COUNT

- **`cleaned_india_jobs.parquet`:** **97,929 rows** × 31 columns. Preserves all raw observations with granular provenance and audit flags.
- **`india_job_postings.parquet`:** **97,679 rows** × 31 columns. Deduplicated by `job_id`, representing unique recruitment postings.
- **`india_job_skills.parquet`:** **751,947 rows** × 2 columns. Relational bridge table mapping each unique job to distinct normalized skills.

---

## 4. DUPLICATE HANDLING

- **Exact Duplicate Rows:** **247 rows** (0.25% of corpus). All 17 columns identical. Flagged via `is_exact_duplicate = True`.
- **Job ID Duplicates:** **250 rows** (97,679 unique IDs out of 97,929). 247 are exact duplicates; 3 represent identical openings multi-posted across regions. Flagged via `is_jobid_duplicate = True`.
- **Content Duplicates (`title`, `companyName`, `location`, `salary`, `experience`):** **9,758 rows** (9.96%). Represents recurring recruitment openings for high-volume enterprise roles. Flagged via `is_content_duplicate = True`.
- **Analytical Postings Resolution:** Primary key constraint enforced on `job_id` ($N = 97,679$), eliminating Cartesian product fan-out during relational joins while retaining full raw provenance in the master dataset.

---

## 5. CURRENCY HANDLING

- **Indian Rupee (`INR`):** **97,800 rows** (99.87% of corpus).
- **US Dollar (`USD`):** **129 rows** (0.13% of corpus).
- **Enforcement:** In accordance with Section 8, all 129 USD postings are retained in the master parquet with `currency = 'USD'` and `is_inr = False`. They are strictly excluded from domestic Indian salary analysis and modeling cohorts. No artificial currency conversion is applied.

---

## 6. SALARY NORMALIZATION

- **Undisclosed Salaries:** **64,121 rows** have `minimumSalary == 0.0` and `maximumSalary == 0.0` (matching the 64,076 text `"Not disclosed"` postings). In accordance with the Salary Disclosure Rule, undisclosed records are explicitly assigned `salary_midpoint_inr = NULL` and `salary_lpa = NULL`. They are never treated as ₹0 salary.
- **Valid Positive INR Ranges:** **33,116 rows** meet the criteria:
  $$\text{currency} = \text{'INR'} \quad \land \quad \text{minimumSalary} > 0 \quad \land \quad \text{maximumSalary} \ge \text{minimumSalary}$$
- **Midpoint and LPA Derivations:**
  $$\text{salary\_midpoint\_inr} = \frac{\text{minimumSalary} + \text{maximumSalary}}{2.0}$$
  $$\text{salary\_lpa} = \frac{\text{salary\_midpoint\_inr}}{100,000.0}$$
- **Data Integrity:** Negative values = 0; anomalies where $\text{min} > \text{max}$ = 0.

---

## 7. SALARY DISTRIBUTION (VALID INR COHORT, N = 33,116)

### Percentile Distribution

| Percentile | Salary (INR) | Salary (LPA) | Market Interpretation |
| :---: | :---: | :---: | :--- |
| **P0 (Min)** | ₹1,000 | 0.01 LPA | Nominal entry / apprenticeship stipend |
| **P1** | ₹80,000 | 0.80 LPA | Sub-minimum-wage / clerical entry |
| **P5** | ₹1,68,000 | 1.68 LPA | Entry-level vocational / diploma pay |
| **P10** | ₹2,00,000 | 2.00 LPA | Junior field operations / customer support |
| **P25 (Q1)** | ₹2,87,500 | 2.88 LPA | Early-career baseline |
| **P50 (Median)** | **₹4,25,000** | **4.25 LPA** | **Indian market median compensation** |
| **P75 (Q3)** | ₹8,25,000 | 8.25 LPA | Mid-level technical / professional compensation |
| **P90** | ₹18,00,000 | 18.00 LPA | Senior technical / team lead compensation |
| **P95** | ₹25,00,000 | 25.00 LPA | Lead engineer / architect level |
| **P99** | ₹45,00,000 | 45.00 LPA | Principal engineer / engineering manager |
| **P99.5** | ₹55,00,000 | 55.00 LPA | Director / specialized niche tech |
| **P99.9** | ₹80,00,000 | 80.00 LPA | Executive leadership / super-senior staff |
| **P100 (Max)** | ₹8,25,00,000 | 825.00 LPA | Recruiter data-entry error (Cr instead of Lacs) |

### Frequency Distribution by Salary Bands

| Salary Band | Observation Count ($N$) | Percentage Share | Cumulative Share |
| :--- | :---: | :---: | :---: |
| **< 1 LPA** | 433 | 1.31% | 1.31% |
| **1 – 2 LPA** | 2,281 | 6.89% | 8.19% |
| **2 – 3 LPA** | 5,787 | 17.47% | 25.67% |
| **3 – 5 LPA** | 10,686 | 32.27% | 57.94% |
| **5 – 10 LPA** | 6,803 | 20.54% | 78.48% |
| **10 – 20 LPA** | 4,194 | 12.66% | 91.14% |
| **20 – 30 LPA** | 1,892 | 5.71% | 96.86% |
| **30 – 50 LPA** | 792 | 2.39% | 99.25% |
| **50 – 80 LPA** | 205 | 0.62% | 99.87% |
| **80 – 100 LPA** | 25 | 0.08% | 99.95% |
| **> 100 LPA** | 18 | 0.05% | 100.00% |
| **Total Valid** | **33,116** | **100.00%** | — |

---

## 8. PROPOSED SALARY BOUNDARY INVESTIGATION & RECOMMENDATION

In accordance with Section 9 and Section 25, **no permanent salary filtering was applied in Phase India-2**. All 33,116 records remain in the analytical tables. Based on tail inspection, we submit the following evidence-based proposal for Phase India-3:

### Lower Tail Inspection (< 1.2 LPA, $N = 727$, 2.19%)
- **Empirical Findings:** Postings below ₹1.2 LPA comprise ITI turner/fitters (e.g., JobId `31025003099`, ₹50k PA), entry-level field sales trainees (JobId `60825017347`, ₹50k–70k PA), and insurance bancassurance agents.
- **Assessment:** These represent sub-minimum-wage stipends, commission-only roles, or non-salaried trainees rather than professional career employment.
- **Recommended Lower Bound:** **₹1.20 LPA** (₹10,000/month).
- **Impact:** Eliminates 727 noisy records (2.19% of cohort), ensuring the model predicts legitimate professional wages.

### Upper Tail Inspection (> 80 LPA, $N = 43$, 0.13%)
- **Empirical Findings:**
  - **Recruiter Entry Errors:** JobId `250925921353` ("Deputy Manager", ₹7–9.5 Cr PA = ₹825 LPA). Clearly entered in Crores instead of Lacs.
  - **Non-Tech Executives & Medical Specialists:** JobId `64394` (Pharma CEO, ₹237.5 LPA), JobId `9719` (Medical Oncologist, ₹107.5 LPA).
  - **Legitimate Tech Upper Ceiling:** Staff Cloud Backend Engineers and Senior LLM Engineers top out at ₹52.5–₹65 LPA.
- **Assessment:** ₹80 LPA aligns exactly with the **99.9th percentile (P99.9)**. Filtering above ₹80 LPA strips recruiter entry errors and non-tech executive outliers while preserving 100% of high-end software, AI/ML, and cloud engineering roles.
- **Recommended Upper Bound:** **₹80.00 LPA**.
- **Impact:** Eliminates 43 extreme outliers (0.13% of cohort).

> [!IMPORTANT]
> **PROPOSED SALARY BOUNDARY FOR PHASE INDIA-3:**
> **₹1.20 LPA to ₹80.00 LPA**
> - Retained Modeling Cohort: **32,346 records** (97.68% of valid INR salaries).
> - Truncation Impact: Total 770 rows removed (2.32% of cohort).
> - Status in Phase India-2: **Zero rows removed.** All 33,116 rows preserved in analytical parquet tables.

---

## 9. EXPERIENCE NORMALIZATION

- **Coverage:** 99.42% of postings contain valid numeric bounds ($N = 97,358$).
- **Midpoint Formula:** $(\text{min} + \text{max}) / 2.0$. Mean: 5.85 years, Median: 5.0 years.
- **Empirical Wage Curve Across Standardized Bands:**

| Experience Band | Total Postings | Postings with Salary ($N$) | Mean Salary (LPA) | Median Salary (LPA) |
| :--- | :---: | :---: | :---: | :---: |
| **0-2 Yrs (Entry)** | 14,657 | 7,511 | ₹3.10 LPA | ₹2.62 LPA |
| **3-5 Yrs (Mid)** | 34,928 | 14,243 | ₹5.16 LPA | ₹3.75 LPA |
| **6-10 Yrs (Senior)** | 35,945 | 8,483 | ₹11.12 LPA | ₹8.75 LPA |
| **11+ Yrs (Lead / Principal)** | 11,828 | 2,879 | ₹20.81 LPA | ₹17.00 LPA |

The experience curve displays monotonic wage progression across both mean and median statistics.

---

## 10. LOCATION NORMALIZATION

- **Coverage:** 100.00% city coverage ($N = 97,679$), 89.01% state coverage ($N = 86,944$).
- **Deterministic Primary-City Rule:** Tokenized delimiters (`,` and `/`), stripped `"Hybrid - "` / `"Remote - "` prefixes, and prioritized first recognized metropolitan entity.
- **Top 15 Metropolitan Hubs (`postings_by_city.csv`):**

| Rank | City | Total Postings ($N$) | Share of Total (%) | State / Territory |
| :---: | :--- | :---: | :---: | :--- |
| 1 | **Bengaluru** | 20,075 | 20.6% | Karnataka |
| 2 | **Hyderabad** | 12,491 | 12.8% | Telangana |
| 3 | **Mumbai** | 10,315 | 10.6% | Maharashtra |
| 4 | **Pune** | 9,570 | 9.8% | Maharashtra |
| 5 | **Chennai** | 6,769 | 6.9% | Tamil Nadu |
| 6 | **Gurugram** | 5,421 | 5.5% | Haryana |
| 7 | **Noida** | 5,228 | 5.4% | Uttar Pradesh |
| 8 | **Ahmedabad** | 2,701 | 2.8% | Gujarat |
| 9 | **Kolkata** | 2,000 | 2.0% | West Bengal |
| 10 | **Remote** | 1,953 | 2.0% | Remote |
| 11 | **Jaipur** | 1,069 | 1.1% | Rajasthan |
| 12 | **Kochi** | 999 | 1.0% | Kerala |
| 13 | **Coimbatore** | 937 | 1.0% | Tamil Nadu |
| 14 | **Chandigarh** | 695 | 0.7% | Chandigarh |
| 15 | **Vadodara** | 679 | 0.7% | Gujarat |

---

## 11. ROLE NORMALIZATION & DOMAIN BREAKDOWN

- **Classification Architecture:** 15 mutually exclusive role families mapped via hierarchical regular expressions.
- **Macro Corpus Composition ($N = 97,679$):**
  - **Tech Postings:** **32,066 rows** (32.83%)
  - **Non-Tech Postings:** **65,613 rows** (67.17%)
- **Salary Cohort Composition ($N = 33,116$):**
  - **Tech with Salary:** **5,945 rows** (17.95%)
  - **Non-Tech with Salary:** **27,171 rows** (82.05%)
- **Observed Salary Difference (Descriptive):**
  - Tech Median Salary: **₹10.00 LPA**
  - Non-Tech Median Salary: **₹3.88 LPA**
  - Observed Difference: **+₹6.12 LPA** (+158.1% higher descriptive median compensation).

---

## 12. SKILL NORMALIZATION & BRIDGE TABLE

- **Bridge Entity:** `india_job_skills.parquet` ($N = 751,947$ pairs).
- **Unique Normalized Skills:** **43,947**.
- **Average Skills Per Job:** **7.70** (Median: 8.0, Max: 8.0).
- **Missing Skills Postings:** **571 jobs** (0.58% missing rate).
- **Top 10 Normalized Skills Overall:** `sales` (9,178), `python` (5,846), `project management` (5,543), `customer service` (5,122), `sap` (5,043), `management` (4,849), `css` (4,187), `java` (4,088), `sql` (3,983), `business development` (3,738).

---

## 13. SQL SCHEMA MAPPINGS

The reference SQL files were adapted from `data/raw/india_reference/` to `sql/india/` with 100% preservation of analytical semantics:

| SQL Reference Field | Source Raw Field | Analytical Field in Parquet | Semantic Mapping Note |
| :--- | :--- | :--- | :--- |
| `job_postings.job_id` | `jobId` | `job_id` | Unique recruitment ID primary key |
| `job_postings.city` | `location` | `city` / `normalized_city` | Extracted primary metropolitan entity |
| `job_postings.role_category` | `title` | `role_category` / `normalized_role` | Standardized role family |
| `job_postings.salary_lpa` | `minimumSalary`, `maximumSalary` | `salary_lpa` | Midpoint annual compensation divided by 100,000 |
| `job_postings.experience_band` | `minimumExperience`, `maximumExperience` | `experience_band` | Standardized 4-band seniority cohort |
| `job_skills.skill` | `tagsAndSkills` | `skill` | Unnested, alias-normalized technology token |

---

## 14. SQL OUTPUT SUMMARY

All 7 analytical queries were executed against the analytical tables loaded into an in-memory SQLite database. Output CSV files were exported to `reports/tables/india/`:

1. `postings_by_city.csv` (15 rows): Bengaluru leads with 20.6% share, followed by Hyderabad (12.8%) and Mumbai (10.6%).
2. `postings_by_role.csv` (15 rows): Non-Tech represents 65,613 postings; Software Engineer leads tech volume with 8,757 postings.
3. `salary_by_experience.csv` (4 rows): Monotonic salary progression from Entry (₹3.10 LPA avg, ₹2.62 LPA median) to Lead (₹20.81 LPA avg, ₹17.00 LPA median).
4. `salary_by_role.csv` (15 rows): Product/Program Managers lead at ₹20.34 LPA avg (₹17.50 LPA median), closely followed by AI/ML Engineers at ₹19.88 LPA avg (₹20.00 LPA median) and Data Scientists at ₹19.01 LPA avg (₹16.50 LPA median).
5. `salary_by_city_analyst.csv` (12 rows): Bengaluru leads Analyst compensation at ₹16.38 LPA avg (₹17.00 LPA median), followed by Vadodara (₹12.67 LPA) and Chennai (₹12.61 LPA).
6. `top_skills_by_role.csv` (66,677 rows): Detailed relational demand matrix across all role families.
7. `job_market_analysis.sql`: Consolidated master script covering Views 1–5.

---

## 15. INDEPENDENT VALIDATION RESULTS

Each SQL query result was independently computed in pure Pandas and cross-checked cell-by-cell:

| Query ID | Analytical View | SQL File Path | Output CSV Path | Validation Check | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **Q1** | Postings by City | `sql/india/postings_by_city.sql` | `postings_by_city.csv` | Exact counts, ranks, percentages | **PASS** |
| **Q2** | Postings by Role | `sql/india/postings_by_role.sql` | `postings_by_role.csv` | Exact role counts, sums | **PASS** |
| **Q3** | Salary by Experience | `sql/india/salary_by_experience.sql` | `salary_by_experience.csv` | Sample counts, averages, medians | **PASS** |
| **Q4** | Salary by Role | `sql/india/salary_by_role.sql` | `salary_by_role.csv` | Means, mins, maxs, threshold $\ge 5$ | **PASS** |
| **Q5** | Salary by City (Analyst) | `sql/india/salary_by_city_analyst.sql` | `salary_by_city_analyst.csv` | City means, threshold $\ge 3$ | **PASS** |
| **Q6** | Top Skills by Role | `sql/india/top_skills_by_role.sql` | `top_skills_by_role.csv` | 66,677 demand counts exact match | **PASS** |
| **Q7** | Master Consolidated | `sql/india/job_market_analysis.sql` | Master script | Execution and consistency | **PASS** |

---

## 16. DATA-QUALITY CROSS-CHECKS (SECTION 22)

All 10 mandatory data integrity assertions passed with 100% compliance:

| Check ID | Integrity Assertion | Measured Value | Expected Target | Status |
| :---: | :--- | :---: | :---: | :---: |
| **CHECK 1** | Sum of role posting counts == total postings | 97,679 | 97,679 | **PASS** |
| **CHECK 2** | Sum of city posting counts == total known city | 97,679 | 97,679 | **PASS** |
| **CHECK 3** | Valid INR salary rows matches audited cohort | 33,116 | 33,116 | **PASS** |
| **CHECK 4** | Zero USD rows appear in domestic salary analyses | 0 | 0 | **PASS** |
| **CHECK 5** | Zero negative salary values | 0 | 0 | **PASS** |
| **CHECK 6** | Zero salary midpoints where min > max | 0 | 0 | **PASS** |
| **CHECK 7** | Zero duplicate `(job_id, skill)` pairs | 0 | 0 | **PASS** |
| **CHECK 8** | All `job_skills` foreign keys exist in `job_postings` | 751,947 (0 orphans) | 0 orphans | **PASS** |
| **CHECK 9** | All salary analyses retain sample size $N$ | 100% retained | $N$ reported | **PASS** |
| **CHECK 10** | Raw Excel row count preserved in master cleaned parquet | 97,929 | 97,929 | **PASS** |

---

## 17. KNOWN LIMITATIONS

1. **Salary Disclosure Selectivity:** Disclosed salaries represent 33.93% of the raw corpus ($N = 33,116$). Tech postings disclose salaries at a lower rate (17.95%) compared to Non-Tech (82.05%). Future modeling in Phase India-3 must evaluate potential disclosure selectivity bias.
2. **Multi-City Aggregation:** When a posting lists multiple locations (e.g. `"Hyderabad, Chennai, Bengaluru"`), the deterministic rule selects the primary (first recognized) metro.
3. **Upper Tail Noise:** Approximately 43 postings exceed ₹80 LPA, containing a blend of legitimate C-suite positions and recruiter entry errors ("Cr instead of Lacs").

---

## 18. DECISION FOR NEXT PHASE

**PHASE INDIA-2 COMPLETE. VERDICT: GREEN — APPROVED FOR PHASE INDIA-3.**

The analytical schema normalization and SQL integration layer is fully reproducible, validated, and frozen.

The next recommended stage is:
> **PHASE INDIA-3: Feature Engineering, Skill Matrix Construction & Modeling Cohort Isolation.**
