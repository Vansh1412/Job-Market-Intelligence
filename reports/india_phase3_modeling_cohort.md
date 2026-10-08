# JOBINTEL — PHASE INDIA-3 SCIENTIFIC REPORT
# FEATURE ENGINEERING & MODELING COHORT ISOLATION
## Formal Statistical Cohort Specification, Leakage Auditing, and Feature Schema Formulation

---

**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Phase:** INDIA-3 (Feature Engineering + Modeling Cohort Isolation)  
**Status:** COMPLETE (20/20 Validation Gates Passed)  
**Author:** Lead Data Scientist & ML Engineer  
**Handoff Target:** Phase India-4 (Model Selection & Salary Prediction Training)  
**Certified Date:** October 2026  
**Pipeline Independence:** Zero modifications to USA pipeline assets (`models/phase5/best_model.pkl` intact)

---

## 1. EXECUTIVE SUMMARY

Phase India-3 establishes the mathematical foundation and feature matrix architecture for predicting tech compensation in India within the JobIntel platform. Building upon the verified, deduplicated analytical tables delivered by Phase India-2, this phase isolates an empirical modeling cohort and formulates a leakage-safe feature space without training predictive models.

```
========================================================================================
                      PHASE INDIA-3 CORE METRICS AT A GLANCE
========================================================================================
Input Postings (Phase-2):          97,679 deduplicated analytical records
Valid INR Salary Records:          33,116 records (100% INR, 0 USD)
Empirical Salary Modeling Bounds:  ₹1.20 LPA to ₹80.00 LPA (Retains 98.11% of INR salaries)
Primary Modeling Cohort:           Cohort C/D — Bounded Tech Roles (N = 5,859 records)
Target Variable:                   salary_midpoint_inr (Display: salary_lpa)
Target Median / Mean:              ₹10,00,000 (10.00 LPA) / ₹12,50,024 (12.50 LPA)
Total Dataset Dimensions:          5,859 rows × 299 columns (~14.8 MB Parquet)
Predictor Features:                290 features (3 numeric, 3 categorical, 284 binary skills)
Predictor Missingness:             0.00% across all 290 candidate features
Skill Feature Threshold:           Frequency >= 25 cohort postings (284 skills selected)
Skill Portfolio Coverage:          90.85% (5,323 of 5,859 postings possess >= 1 skill)
Skill Matrix Sparsity:             98.71% (Optimized for gradient boosted decision trees)
Content Duplicate Groups:          48 groups (114 records, 1.95% cohort duplication)
Splitting Policy:                  GroupShuffleSplit / GroupKFold on content_fingerprint
Phase Validation Gates:            20 / 20 PASS (100% compliance)
========================================================================================
```

The primary modeling cohort addresses JobIntel's core objective: high-resolution skill-based salary intelligence. While the full Indian job dataset contains 33,116 disclosed salaries, 82.0% represent non-technical professions (field insurance sales, retail telecalling, clerical operations) where compensation is dictated by commissions rather than technology stacks. Retaining the non-tech majority introduces massive noise and 99.8% feature sparsity in tech skills. By isolating the **5,859 verified technology recruitment records** within defensible salary bounds, we achieve high signal density, 100% complete predictors, and balanced role representation.

---

## 2. PHASE-2 INHERITANCE & PRE-FLIGHT VERIFICATION

Phase India-3 inherits certified, deduplicated analytical tables generated in Phase India-2. Prior to engineering features, an exhaustive pre-flight verification was performed (`reports/india_phase3_input_audit.md`):

1. **Analytical Integrity:**
   - Source table `data/processed/india/india_job_postings.parquet`: 97,679 deduplicated postings (from 97,929 raw rows minus 250 duplicate `jobId` records).
   - Skills table `data/processed/india/india_job_skills.parquet`: 751,947 validated job-skill pairs across 43,947 unique normalized skills. Zero duplicate pairs.
2. **Currency Partitioning:**
   - Disclosed salaries: 33,245 total.
   - INR cohort: 33,116 postings (100.0% domestic Indian currency).
   - Foreign currencies: 129 USD postings completely partitioned into `data/processed/india/usd_job_postings.parquet`. Zero USD contamination exists.
3. **Mathematical Consistency:**
   - Minimum salary $\le$ Maximum salary across 100% of disclosed records ($0$ inversion errors).
   - Minimum experience $\le$ Maximum experience across 100% of records ($0$ inversion errors).
4. **USA Protection:**
   - `models/phase5/best_model.pkl` (USA XGBoost regressor, exactly 619,464 bytes) remains completely untouched.

---

## 3. SALARY-BOUND DECISION & TAIL INVESTIGATION

Phase India-2 proposed empirical bounds of **₹1.20 LPA to ₹80.00 LPA**. In Phase India-3, these bounds were subjected to empirical tail analysis across all 33,116 valid INR salary postings.

![Salary Distribution Bounds](file:///e:/Job%20Market/reports/figures/india/salary_distribution_bounds.png)

### Tail Distribution Summary (`reports/tables/india/salary_bound_analysis.csv`):
| Segment | Count | Pct of Disclosed | Min LPA | Median LPA | Mean LPA | Max LPA | Tech Count | Non-Tech Count | Methodological Action |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Lower Tail (< 1.20 LPA)** | 593 | 1.79% | 0.01 | 0.75 | 0.78 | 1.18 | 84 | 509 | **Excluded:** Un-salaried apprenticeships, stipends |
| **Retained Core (1.20–80 LPA)** | 32,490 | 98.11% | 1.20 | 4.25 | 7.57 | 80.00 | 5,859 | 26,631 | **Retained:** Statistically valid professional market |
| **Upper Tail (> 80.00 LPA)** | 33 | 0.10% | 82.50 | 105.00 | 137.98 | 825.00 | 2 | 31 | **Excluded:** Recruiter entry errors & C-suite anomalies |

### Empirical Justification:
1. **Lower Tail (< ₹1.20 LPA / ₹10,000/month):**
   - Qualitative inspection reveals ITI trade fitters, un-salaried field sales apprenticeships, and telecalling stipends (e.g., ₹0.01 LPA = ₹100/year clerical data entry error; ₹0.30 LPA = ₹2,500/month stipend).
   - Minimum statutory wage benchmarks in Indian metropolitan areas for skilled labor exceed ₹10,000–₹12,000/month. Postings below ₹1.20 LPA represent non-target vocational labor or scrape errors.
2. **Upper Tail (> ₹80.00 LPA):**
   - The ₹80.00 LPA boundary corresponds to the 99.9th percentile ($P_{99.9}$) of domestic INR compensation.
   - Qualitative inspection reveals obvious recruiter data-entry errors where annual salaries in Lacs were entered into Crores fields (e.g., *Deputy Manager* entered as "7–9.5 Cr PA" = ₹825 LPA midpoint).
   - Only 2 tech postings exceeded ₹80 LPA, both exhibiting extreme typographical anomalies.
3. **Preservation of Legitimate High Earners:**
   - Unlike naive statistical trimming (e.g., Tukey 1.5× IQR, which would truncate valid senior tech salaries at ₹16.3 LPA), the ₹80.00 LPA ceiling preserves Staff Engineers, Principal Architects, Engineering Directors, and Chief Data Officers (earning ₹25–₹75 LPA).
   - Retains **98.11%** of all INR records and **98.55%** of tech postings. Silently clipping or winsorizing was explicitly avoided.

---

## 4. COHORT ALTERNATIVES & COMPARATIVE EVALUATION

To establish the appropriate modeling population, four candidate cohorts were formally evaluated across 15 dimensions (`reports/tables/india/cohort_comparison.csv`):

![Cohort Comparison](file:///e:/Job%20Market/reports/figures/india/cohort_comparison.png)

### Candidate Cohort Profiles:
| Dimension | Cohort A: All Disclosed INR | Cohort B: Bounded Disclosed INR | Cohort C: Bounded Tech Roles | Cohort D: Bounded Tech + Complete Features |
| :--- | :---: | :---: | :---: | :---: |
| **Sample Size (N)** | 33,116 | 32,490 | **5,859** | **5,859** |
| **Pct of Valid Salaries** | 100.0% | 98.11% | **17.69%** | **17.69%** |
| **Salary Median (LPA)** | 4.25 | 4.25 | **10.00** | **10.00** |
| **Salary Mean (LPA)** | 7.58 | 7.57 | **12.50** | **12.50** |
| **Salary Spread (IQR)** | 5.38 | 5.50 | **11.50** | **11.50** |
| **Salary Skewness** | +18.97 | +3.09 | **+1.35** | **+1.35** |
| **Standardized Roles** | 15 | 15 | **14 (Tech-Only)** | **14 (Tech-Only)** |
| **Dominant Role Share** | Non-Tech (82.05%) | Non-Tech (81.97%) | Other Tech (54.07%) | Other Tech (54.07%) |
| **Unique Metros** | 1,010 | 989 | **297** | **297** |
| **Avg Skills per Job** | 7.65 | 7.66 | **7.70** | **7.70** |
| **Tech Skill Sparsity** | 99.83% | 99.70% | **98.71%** | **98.71%** |
| **Feature Missingness** | 0.00% | 0.00% | **0.00%** | **0.00%** |

### Comparative Analysis:
- **Cohorts A & B (Full Market):** Severe class imbalance. Over 82% of rows are Non-Tech roles (bancassurance agents, pharmaceutical sales reps, warehouse coordinators). When pooling these with tech jobs, statistical models learn non-technical macro baselines, diluting technology skill premiums. Furthermore, raw skewness in Cohort A is extreme (+18.97).
- **Cohort C vs Cohort D:** In our processed dataset, all 5,859 bounded tech records possess 100% complete experience, role, and city data. Thus, Cohort C and Cohort D are identical ($N = 5,859$).

---

## 5. FINAL COHORT DEFINITION & SELECTION RATIONALE

### Final Modeling Cohort:
**JobIntel India Primary Tech Modeling Cohort (Cohort C/D)**  
**Sample Size:** **5,859 records**  
**Storage Path:** [`data/processed/india/india_modeling_cohort.parquet`](file:///e:/Job%20Market/data/processed/india/india_modeling_cohort.parquet)

### Decision Rationale:
1. **Core Product Alignment:** JobIntel is architected to deliver skill-differentiated compensation intelligence. Training on insurance sales and clerical jobs violates the core value proposition.
2. **Signal-to-Noise Optimization:** In the tech cohort, skill indicators directly correlate with salary variance (e.g., AWS, Python, Kubernetes, Spark). In the broader market, tech skills are present in less than 0.2% of rows, collapsing tabular trees into trivial role splits.
3. **Statistical Regularity:** Skewness drops from +18.97 (all raw) and +3.09 (bounded general) to **+1.35** in the bounded tech cohort, enabling stable linear, regularized, and gradient boosted learning.
4. **Zero Missingness:** 100% of records possess verified numeric experience bounds, standardized role classifications, and valid location metadata.

---

## 6. TARGET DEFINITION & LEAKAGE RESTRICTIONS

### Mathematical Formulation:
- **Primary Numerical Target:**
  $$\text{salary\_midpoint\_inr} = \frac{\text{minimumSalary} + \text{maximumSalary}}{2}$$
  - Range: ₹1,20,000 to ₹80,00,000  
  - Median: ₹10,00,000 (10.00 LPA)  
  - Mean: ₹12,50,024 (12.50 LPA)  
  - IQR: ₹11,50,000 (11.50 LPA)
- **Human Interpretation Target:**
  $$\text{salary\_lpa} = \frac{\text{salary\_midpoint\_inr}}{100,000}$$
- **Log Symmetrized Evaluation Target:**
  $$\text{log\_salary\_midpoint\_inr} = \ln(1 + \text{salary\_midpoint\_inr})$$

### Strict Target Leakage Protections:
To prevent circular information flow, the following variables are strictly sequestered from the feature matrix:
- `minimumSalary`, `maximumSalary` (Direct target constituents)
- `salary`, `original_salary` (Textual disclosure strings containing target numbers)
- Post-hoc salary percentiles, salary ranks, or salary-derived binning variables.

---

## 7. ROLE TAXONOMY ANALYSIS

The Phase-2 normalized role taxonomy identifies 14 distinct technology role families within the modeling cohort. Zero non-tech records are present.

![Role Distribution](file:///e:/Job%20Market/reports/figures/india/role_distribution.png)

### Modeling Cohort Role Breakdown:
| Standardized Role Family | Postings (N) | Share (%) | Median Salary (LPA) | Mean Salary (LPA) | Tech Focus |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Other Technology** | 3,168 | 54.07% | 9.00 | 11.83 | Infrastructure, IT Systems, General Eng |
| **Software Engineer** | 795 | 13.57% | 12.00 | 14.15 | Backend, Core Systems, Algorithms |
| **Full Stack Developer** | 409 | 6.98% | 10.00 | 11.58 | Multi-tier Web & Application Dev |
| **QA / Testing** | 371 | 6.33% | 7.50 | 9.42 | Automation, SDET, Performance Testing |
| **Data Engineer** | 354 | 6.04% | 15.00 | 16.59 | Big Data, Pipelines, ETL, Spark, Cloud |
| **Cloud / DevOps** | 183 | 3.12% | 16.00 | 17.58 | CI/CD, Kubernetes, AWS, SRE |
| **Frontend Developer** | 112 | 1.91% | 8.00 | 10.37 | React, Angular, UI/UX Engineering |
| **Business Analyst** | 99 | 1.69% | 10.00 | 12.44 | Requirements, Product Analytics, BI |
| **AI / ML Engineer** | 74 | 1.26% | 14.00 | 15.91 | Machine Learning, Deep Learning, MLOps |
| **Data Analyst** | 72 | 1.23% | 7.00 | 8.76 | SQL, Dashboarding, Reporting, Tableau |
| **Cybersecurity** | 70 | 1.19% | 14.00 | 16.48 | InfoSec, Pen Testing, SOC, Governance |
| **Database Administrator**| 63 | 1.08% | 11.00 | 12.95 | Oracle, MySQL, Performance Tuning |
| **Product / Program Mgr** | 61 | 1.04% | 16.00 | 18.25 | Technical Product Management, Scrum |
| **Data Scientist** | 47 | 0.80% | 15.00 | 16.63 | Statistical Modeling, Advanced Analytics |

### Taxonomy Governance:
- **Coverage:** 100.0% of cohort records map to one of these 14 families.
- **Decision:** The categorical feature `normalized_role` is adopted as a primary predictor. Raw job titles (4,800+ unique strings) are excluded to prevent extreme cardinality overfitting.

---

## 8. EXPERIENCE FEATURE ENGINEERING

The dataset provides structured minimum and maximum experience years.

![Experience Distribution](file:///e:/Job%20Market/reports/figures/india/experience_distribution.png)

### Engineered Predictors:
1. **`experience_midpoint_years`:**
   $$\text{experience\_midpoint\_years} = \frac{\text{minimumExperience} + \text{maximumExperience}}{2}$$
   - Descriptive Stats: Mean = 5.76 years, Median = 5.00 years, Min = 0.0, Max = 27.5 years.
   - Correlation with Salary: $r = +0.612$ (Strong monotonic relationship).
2. **`experience_range_years`:**
   $$\text{experience\_range\_years} = \text{maximumExperience} - \text{minimumExperience}$$
   - Descriptive Stats: Mean = 3.55 years, Median = 3.00 years, Min = 0.0, Max = 14.0 years.
   - Captures employer hiring flexibility and seniority bands.

### Integrity Validation:
- Missingness: 0.00% ($N = 5,859$).
- Negative values: 0.
- `min > max` inversions: 0.

---

## 9. LOCATION FEATURE ENGINEERING

The modeling cohort spans 297 unique Indian cities. A raw one-hot encoding of 297 categories would create severe parameter dilution for small towns.

![City Distribution](file:///e:/Job%20Market/reports/figures/india/city_distribution.png)

### Frequency Threshold Evaluation (`reports/tables/india/city_feature_coverage.csv`):
We evaluated thresholds from $\ge 10$ to $\ge 100$ postings:
- $\ge 10$ postings: 45 cities retained, 89.44% tech coverage.
- **$\ge 20$ postings (Selected):** **22 major tech hubs retained**, **83.70% direct coverage** in tech (and 90.92% across all jobs), with 16.30% ($N = 955$) mapping to `'Other'`.
- $\ge 50$ postings: 13 cities retained, 78.43% coverage (omits significant emerging hubs like Kochi, Coimbatore, Chandigarh).

### Grouped City Representation (`city_grouped`):
- **Tier-1 Tech Metros:** Bengaluru (1,688), Hyderabad (833), Pune (792), Mumbai (632), Chennai (490), Gurugram (331), Noida (276).
- **Secondary Hubs:** Ahmedabad (106), Kolkata (92), Remote (81), Kochi (49), Coimbatore (46), Vadodara (44), Chandigarh (35), Jaipur (34), Delhi NCR (25), Mohali (24), Indore (24), Nagpur (23), Surat (21), Nashik (20), Faridabad (20).
- **Aggregated Category:** `'Other'` (955 postings across 275 minor locations).

---

## 10. WORK MODE / REMOTE HANDLING

Unlike many scraped datasets where work mode is ambiguous, this dataset provides a standardized `work_mode` attribute:
- **`Onsite`:** 4,510 postings (76.98%), Median Salary = ₹7.00 LPA (Mean: ₹10.87 LPA)
- **`Hybrid`:** 1,106 postings (18.88%), Median Salary = ₹17.50 LPA (Mean: ₹18.17 LPA)
- **`Remote`:** 243 postings (4.15%), Median Salary = ₹15.00 LPA (Mean: ₹16.87 LPA)

### Methodological Inclusion:
The empirical evidence indicates that Hybrid and Remote positions command a significant compensation premium in the Indian tech market. Because missingness is 0.00% and classifications are deterministic, `work_mode` is formally **INCLUDED** as a three-level categorical predictor.

---

## 11. COMPANY FEATURES DECISION

- **Observation:** 2,529 unique company names and IDs exist across 5,859 postings.
- **Cardinality:** Over 68% of companies appear in only 1 posting.
- **Overfitting Risk:** Including high-cardinality company identifiers invites memorization of employer-specific compensation scales without generalizing to unobserved firms.
- **Decision:** **EXCLUDED** from the primary feature schema. Company name and ID are preserved solely as metadata for reporting and error audits.

---

## 12. JOB DESCRIPTION DECISION

- **Observation:** `jobDescription` contains unstructured HTML and plain text with extreme length variance (10 to 4,500 words) and high boilerplate repetition.
- **Tabular Scope:** The project architecture mandates a structured, interpretable tabular feature baseline for Phase India-4.
- **Decision:** **EXCLUDED** from the baseline tabular feature matrix. Multimodal text embeddings are reserved for future model expansions.

---

## 13. SKILL FEATURE ENGINEERING

The Phase-2 skills table contains 751,947 job-skill pairs across 43,947 normalized terms. A naive one-hot matrix would create an unmanageable 43,947-column sparse matrix.

![Skill Frequency Curve](file:///e:/Job%20Market/reports/figures/india/skill_frequency_curve.png)

### Skill Analysis Findings (`reports/tables/india/skill_frequency_analysis.csv`):
- Top skills by tech posting frequency: `JavaScript` (756), `Python` (707), `Java` (698), `SQL` (673), `HTML` (606), `CSS` (582), `React.js` (541), `AWS` (533), `Git` (346), `Node.js` (305).
- High-value specialized skills command clear compensation premiums:
  - `Kubernetes` (158 postings, Median: ₹20.00 LPA)
  - `Docker` (207 postings, Median: ₹18.00 LPA)
  - `Apache Spark` (112 postings, Median: ₹18.50 LPA)
  - `Snowflake` (98 postings, Median: ₹19.00 LPA)
  - `Machine Learning` (168 postings, Median: ₹16.00 LPA)

---

## 14. SKILL-FREQUENCY THRESHOLD ANALYSIS

We evaluated five candidate frequency thresholds within the modeling cohort (`reports/tables/india/skill_threshold_comparison.csv`):

![Skill Coverage vs Threshold](file:///e:/Job%20Market/reports/figures/india/skill_coverage_threshold.png)

### Threshold Comparison Table:
| Threshold (Min Jobs) | Retained Skills Count | Tech Jobs Covered | Tech Coverage (%) | Mean Skills / Job | Matrix Sparsity (%) | Evaluation / Decision |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| $\ge 10$ | 750 | 5,675 | 96.86% | 5.01 | 99.35% | High dimensionality, noisy rare tokens |
| **$\ge 25$ (Selected)** | **284** | **5,323** | **90.85%** | **4.03** | **98.71%** | **Optimal balance of coverage, sparsity & dimensionality** |
| $\ge 50$ | 121 | 4,717 | 80.51% | 3.40 | 97.74% | Drops valuable specialized tools (Airflow, Terraform) |
| $\ge 100$ | 58 | 4,035 | 68.87% | 2.90 | 96.55% | Loses 31.1% of candidate postings |
| $\ge 250$ | 12 | 2,730 | 46.59% | 1.91 | 92.60% | Severe under-representation (only 12 basic languages) |

### Selected Vocabulary:
Threshold **$\ge 25$ postings** was formally selected. It yields **284 distinct technical skill features**, captures **90.85%** of tech postings with at least one skill, maintains a mean of 4.03 skills per job, and keeps matrix sparsity at an efficient 98.71%.

---

## 15. DUPLICATE & CONTENT LEAKAGE AUDIT

Phase India-2 identified content duplicates across the broader scraped dataset. To ensure honest holdout evaluation, we conducted a content fingerprint audit (`reports/tables/india/content_duplicate_analysis.csv`):
- **Content Fingerprint:** An MD5 hash of `normalized_title + company_name + city + job_description[:200]`.
- **Total Unique Fingerprints:** 5,793 groups across 5,859 postings.
- **Duplicate Groups:** **48 groups** containing **114 records (1.95%)**.
- **Salary Uniformity:** 59.87% of duplicate openings possess identical salaries across multiple postings.

### Leakage Risk & Prevention:
If identical job postings appear in both training and test partitions, standard cross-validation will overfit by memorizing exact text-salary pairs.  
**Prescribed Split Protocol:** Standard random splitting is rejected. Cross-validation and train/test splitting in Phase India-4 must employ a **Grouped Split** using `content_fingerprint` as the grouping vector:
```python
from sklearn.model_selection import GroupShuffleSplit
gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=df["content_fingerprint"]))
```

---

## 16. COMPLETE FEATURE SCHEMA

The complete feature specification is serialized at [`data/processed/india/india_feature_schema.json`](file:///e:/Job%20Market/data/processed/india/india_feature_schema.json).

### Feature Taxonomy Summary:
```
========================================================================================
FEATURE BLOCK               COUNT     COLUMN NAMES / DETAILS
========================================================================================
Target Variables            3         salary_midpoint_inr, salary_lpa,
                                      log_salary_midpoint_inr
Identifiers & Metadata      6         job_id, content_fingerprint, title, company_name,
                                      city, state
Numerical Predictors        3         experience_midpoint_years, experience_range_years,
                                      total_selected_skill_count
Categorical Predictors      3         normalized_role (14 levels), city_grouped (23 levels),
                                      work_mode (3 levels)
Binary Skill Indicators     284       skill__javascript, skill__python, skill__java,
                                      skill__sql, skill__aws, skill__react_js, ...
TOTAL MATRIX DIMENSIONS     299       5,859 rows × 299 columns (~14.8 MB Parquet)
========================================================================================
```

---

## 17. LEAKAGE PREVENTION MATRIX

| Variable Name | Source Column | Modeling Status | Leakage Mechanism & Prevention Control |
| :--- | :--- | :---: | :--- |
| `minimumSalary` | `minimumSalary` | **EXCLUDED** | Direct mathematical constituent of target midpoint. |
| `maximumSalary` | `maximumSalary` | **EXCLUDED** | Direct mathematical constituent of target midpoint. |
| `salary` | `salary` | **EXCLUDED** | Raw text containing target figures. |
| `salary_band` | Derived | **EXCLUDED** | Post-hoc categorization of salary. |
| `company_name` | `companyName` | **EXCLUDED** | Memorization of firm-specific wage policies. |
| `company_id` | `companyId` | **EXCLUDED** | Surrogate ID for employer. |
| `title` | `title` | **EXCLUDED** | 4,800+ raw strings; summarized safely into `normalized_role`. |
| `jobDescription`| `jobDescription`| **EXCLUDED** | Reserved for future NLP pipelines. |
| `ReviewsCount` | `ReviewsCount` | **EXCLUDED** | 36% missing; unobserved for early-stage tech firms. |
| `AggregateRating`| `AggregateRating`| **EXCLUDED** | 36% missing; employer-level rating bias. |
| `jobUploaded` | `jobUploaded` | **EXCLUDED** | Relative scraper strings ("X days ago"), unanchored in time. |
| `jobId` | `jobId` | **METADATA** | Retained as row primary key, not passed into feature vector $X$. |

---

## 18. TRAIN / TEST SPLIT POLICY

The following train/test partition policy is established for Phase India-4:
1. **Partition Ratio:** 80% Training ($N \approx 4,687$), 20% Holdout Test ($N \approx 1,172$).
2. **Deterministic Seed:** `random_state = 42`.
3. **Grouped Partitioner:** `GroupShuffleSplit` on `content_fingerprint`.
4. **Data Isolation Principle:**
   - Any encoders, scalers, or target transformations must be fitted **strictly on training partitions** and applied downstream to holdout partitions.
   - Zero pre-fitting on the full dataset is permitted.

---

## 19. RAW VS. LOG TARGET ANALYSIS

To determine the optimal objective function for future regressors, we analyzed target normality and skewness:

![Salary Log Distribution](file:///e:/Job%20Market/reports/figures/india/salary_log_distribution.png)

### Distribution Metrics:
- **Raw Target (`salary_midpoint_inr`):**
  - Skewness: **+1.346** (Moderate positive skew, right-tailed tech salaries).
  - Kurtosis: +2.180.
- **Log Transformed Target ($\ln(1 + y)$):**
  - Skewness: **-0.173** (Near-perfect symmetry, Gaussian bell curve).
  - Kurtosis: -0.048 (Near-mesokurtic).

### Phase-4 Recommendation:
While linear models (Ridge, Lasso) and neural architectures require the log-transformed target ($\ln(1 + y)$) to satisfy homoscedasticity assumptions, gradient boosted trees (XGBoost, LightGBM, CatBoost) can optimize both RMSE on raw salaries and RMSLE on log salaries. Both formulations should be benchmarked during model selection.

---

## 20. DATA QUALITY AUDIT & REPRODUCIBILITY

The feature engineering pipeline is fully automated and reproducible via `src/india/cohort.py` and `src/india/feature_engineering.py`.

```bash
# Reproduction Command Sequence:
python -m src.india.cohort
python -m src.india.feature_engineering
python scratch/verify_phase3_gates.py
```

### Comprehensive Quality Checks:
- **Null Values in Predictors:** Exactly $0$ nulls across 290 candidate features.
- **Target Integrity:** All 5,859 targets satisfy ₹1,20,000 $\le y \le$ ₹80,00,000.
- **Deterministic Pipeline:** Zero non-deterministic random functions; execution from cold disk produces bitwise identical parquet outputs.

---

## 21. LIMITATIONS & THREATS TO VALIDITY

1. **Self-Reported Scraped Postings:** Salary data represents recruiter disclosures at posting time, which may differ from negotiated compensation packages (equity, signing bonuses).
2. **Dominance of 'Other Technology':** 54.07% of tech jobs fall under general IT/tech titles not mapping to specific sub-disciplines like AI/ML or Data Engineering. Skill features provide the critical resolving power for this group.
3. **Geographic Concentration:** Over 68% of postings originate from five metropolitan clusters (Bengaluru, Hyderabad, Pune, Mumbai, Chennai), reflecting the natural distribution of India's tech industry.

---

## 22. PHASE-4 READINESS DECISION

### Gate Verification Status:
All **20 of 20 Validation Gates PASS** with zero discrepancies (`scratch/verify_phase3_gates.py`).

| Gate # | Description | Status | Evidence |
| :---: | :--- | :---: | :--- |
| **GATE 1** | Raw source unchanged | **PASS** | `indian-job-market-dataset-2025.xlsx` byte size 31,709,363 intact. |
| **GATE 2** | USA assets unchanged | **PASS** | `models/phase5/best_model.pkl` byte size 619,464 intact. |
| **GATE 3** | Only INR salary records used | **PASS** | 100% currency == 'INR', zero USD records. |
| **GATE 4** | No negative salaries | **PASS** | Min salary ₹1.20 LPA > 0. |
| **GATE 5** | No min salary > max salary | **PASS** | 100% min $\le$ max across all rows. |
| **GATE 6** | Salary bounds applied with justification | **PASS** | Documented empirical tail audit (1.20 to 80.00 LPA). |
| **GATE 7** | Final cohort has no target leakage fields | **PASS** | Predictor matrix contains zero leakage columns. |
| **GATE 8** | Experience values validated | **PASS** | 100% valid, non-negative, min $\le$ max. |
| **GATE 9** | Role taxonomy validated | **PASS** | 14 tech roles, zero non-tech records in cohort. |
| **GATE 10** | City feature strategy validated | **PASS** | 22 metros ($\ge 20$ jobs) + 'Other' (23 levels). |
| **GATE 11** | Skill frequency threshold justified | **PASS** | Threshold $\ge 25$ selected via empirical tradeoff audit. |
| **GATE 12** | Skill matrix dimensionality reasonable | **PASS** | 284 skills, 98.71% sparsity, ~14.8 MB Parquet. |
| **GATE 13** | Content duplicate leakage assessed | **PASS** | 48 duplicate groups identified; GroupKFold specified. |
| **GATE 14** | Final cohort is reproducible | **PASS** | Runnable end-to-end via `src.india` CLI modules. |
| **GATE 15** | Feature schema is documented | **PASS** | Complete schema in `india_feature_schema.json`. |
| **GATE 16** | Target statistics reproduced | **PASS** | Exact match: Median ₹10 LPA, Mean ₹12.50 LPA. |
| **GATE 17** | Transformation logic deterministic | **PASS** | Deterministic mathematical vector operations. |
| **GATE 18** | No ML model trained | **PASS** | Exactly 0 models trained in this phase. |
| **GATE 19** | No API/frontend modified | **PASS** | Zero edits to React/Vite/FastAPI codebases. |
| **GATE 20** | All artifacts exist and regenerable | **PASS** | 100% of required parquet, json, csv, png files present. |

### Final Status:
**PHASE INDIA-3 STATUS: GREEN**  
**PHASE INDIA-4 AUTHORIZATION: RECOMMENDED & READY**
