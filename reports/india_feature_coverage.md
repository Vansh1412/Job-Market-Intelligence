# JOBINTEL — PHASE INDIA-3: FEATURE COVERAGE & SCHEMA INTEGRITY REPORT
## Comprehensive Pre-Modeling Dimension Audit & Sparsity Analysis

---

## 1. EXECUTIVE OVERVIEW

This report documents the statistical coverage, completeness, and dimensional properties of the **JobIntel India Primary Tech Modeling Cohort** (`data/processed/india/india_modeling_cohort.parquet`).

The isolated modeling dataset consists of **5,859 verified technology recruitment records** spanning 14 standardized tech role families across 297 Indian cities, bounded strictly within ₹1.20 LPA to ₹80.00 LPA.

```
================================================================================
MODELING COHORT SPECIFICATION AT A GLANCE
================================================================================
Population Scope:          Domestic Indian Technology / Data Roles
Sample Size (N):           5,859 observations
Target Variable:           salary_midpoint_inr (Display: salary_lpa)
Target Range:              ₹1,20,000 to ₹80,00,000 (1.20 to 80.00 LPA)
Target Median / Mean:      ₹10,00,000 (10.00 LPA) / ₹12,50,024 (12.50 LPA)
Predictor Dimensions:      290 features (3 numeric, 3 categorical, 284 binary skills)
Predictor Missingness:     0.00% (Zero missing values across all predictor columns)
Portfolio Skill Coverage:  90.85% (5,323 of 5,859 jobs carry >= 1 selected skill)
Skill Matrix Sparsity:     98.71% (Efficient sparse tabular representation)
Leakage Strategy:          GroupShuffleSplit on content_fingerprint (80/20 train/test)
================================================================================
```

---

## 2. TARGET VARIABLE PROFILE

The modeling target is the continuous annual salary midpoint in Indian Rupees (`salary_midpoint_inr`), with `salary_lpa` provided for human interpretation:

| Target Statistic | Value (INR) | Value (LPA) | Methodological Role |
| :--- | :---: | :---: | :--- |
| **Minimum Bound** | ₹1,20,000 | 1.20 LPA | Empirical floor (excludes non-target trainees) |
| **25th Percentile (Q1)** | ₹6,00,000 | 6.00 LPA | Lower quartile baseline |
| **50th Percentile (Median)** | **₹10,00,000** | **10.00 LPA** | **Primary central tendency metric** |
| **75th Percentile (Q3)** | ₹17,50,000 | 17.50 LPA | Upper quartile technical benchmark |
| **Mean** | ₹12,50,024 | 12.50 LPA | Parametric expectation |
| **Maximum Bound** | ₹80,00,000 | 80.00 LPA | Empirical ceiling (P99.9 boundary) |
| **Interquartile Range (IQR)**| ₹11,50,000 | 11.50 LPA | Spread measure |
| **Raw Target Skewness** | **+1.346** | +1.346 | Moderate positive skew |
| **Log1p Target Skewness** | **-0.173** | -0.173 | **Near-normal distribution ($\ln(1+y)$)** |

---

## 3. FEATURE DIMENSIONALITY & REPRESENTATION

The model-ready dataset comprises **299 total columns** structured into target, identifier, and predictor blocks:

| Column Block | Column Count | Storage Type | Memory Footprint | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Identifiers & Provenance** | 6 | `int64`, `string` | ~1.2 MB | `job_id`, `content_fingerprint`, title, company, raw city, state |
| **Targets** | 3 | `float64` | ~0.1 MB | `salary_midpoint_inr`, `salary_lpa`, `log_salary_midpoint_inr` |
| **Numerical Predictors** | 3 | `float64`, `int64` | ~0.1 MB | `experience_midpoint_years`, `experience_range_years`, `total_selected_skill_count` |
| **Categorical Predictors** | 3 | `string` / `category` | ~0.2 MB | `normalized_role`, `city_grouped`, `work_mode` |
| **Binary Skill Matrix** | 284 | `int64` (0/1) | ~13.2 MB | Sparse binary indicators for top technical skills ($\ge 25$ jobs) |
| **Total Dataset** | **299** | — | **~14.8 MB** | Complete self-contained parquet artifact |

---

## 4. DOMAIN COVERAGE AUDIT

### A. Experience Features (Coverage: 100.0%)
- **`experience_midpoint_years`:** Mean = 5.76 years, Median = 5.00 years, Range = 0.0 to 27.5 years.
- **`experience_range_years`:** Mean = 3.55 years, Median = 3.00 years, Range = 0.0 to 14.0 years.
- **Sanity:** Zero negative values, zero `min > max` errors, zero missing values.

### B. Role Taxonomy (Coverage: 100.0%)
All 5,859 postings map into 14 distinct technology role families:
1. `Other Technology`: 3,168 (54.07%)
2. `Software Engineer`: 795 (13.57%)
3. `Full Stack Developer`: 409 (6.98%)
4. `QA / Testing`: 371 (6.33%)
5. `Data Engineer`: 354 (6.04%)
6. `Cloud / DevOps`: 183 (3.12%)
7. `Frontend Developer`: 112 (1.91%)
8. `Business Analyst`: 99 (1.69%)
9. `AI / ML Engineer`: 74 (1.26%)
10. `Data Analyst`: 72 (1.23%)
11. `Cybersecurity`: 70 (1.19%)
12. `Database Administrator`: 63 (1.08%)
13. `Product / Program Manager`: 61 (1.04%)
14. `Data Scientist`: 47 (0.80%)

### C. Geographic Metro Coverage (`city_grouped`, Coverage: 100.0%)
Grouping cities with frequency $\ge 20$ into individual categories and mapping rare cities to `'Other'` yields **23 categorical levels**:
- **Top Metros Retained:** Bengaluru (1,688), Hyderabad (833), Pune (792), Mumbai (632), Chennai (490), Gurugram (331), Noida (276), Ahmedabad (106), Kolkata (92), Remote (81), Kochi (49), Coimbatore (46), Vadodara (44), Chandigarh (35), Jaipur (34), Delhi NCR (25), Mohali (24), Indore (24), Nagpur (23), Surat (21), Nashik (20), Faridabad (20).
- **Metro Share:** 90.92% ($N = 5,327$) map to explicit top tech hubs.
- **`'Other'` Share:** 9.08% ($N = 532$) across 275 minor towns.

### D. Work Mode Distribution (Coverage: 100.0%)
- **`Onsite`:** 4,510 postings (76.98%), Median Salary = ₹7.00 LPA (Mean: ₹10.87 LPA)
- **`Hybrid`:** 1,106 postings (18.88%), Median Salary = ₹17.50 LPA (Mean: ₹18.17 LPA)
- **`Remote`:** 243 postings (4.15%), Median Salary = ₹15.00 LPA (Mean: ₹16.87 LPA)
- **Signal:** Hybrid and Remote tech roles command an empirical premium over strictly onsite roles in the Indian tech market.

### E. Skill Matrix Coverage & Sparsity
- **Total Selected Skills:** **284 skills** meeting the empirical cutoff ($\ge 25$ postings).
- **Postings with $\ge 1$ Skill:** **5,323 jobs (90.85% coverage)**.
- **Postings with 0 Skills:** 536 jobs (9.15%). Handled gracefully by all-zero rows and `total_selected_skill_count = 0`.
- **Median Skills per Job:** 3.0 (Mean: 3.65, Max: 8.0).
- **Sparsity:** **98.71%**, ideal for sparse gradient boosting matrix representations.

---

## 5. FEATURE EXCLUSIONS & METHODOLOGICAL RATIONALE

| Excluded Variable | Raw Column | Methodological Rationale for Exclusion |
| :--- | :--- | :--- |
| `minimumSalary` | `minimumSalary` | **Direct Target Leakage:** Mathematically defines the lower bound of the target. |
| `maximumSalary` | `maximumSalary` | **Direct Target Leakage:** Mathematically defines the upper bound of the target. |
| `salary` | `salary` | **Direct Target Leakage:** Textual disclosure string containing target figures. |
| `company_name` | `companyName` | **Overfitting / Memorization:** Extreme cardinality (2,529 companies), high risk of memorizing company-specific wage bands. |
| `company_id` | `companyId` | **Overfitting / Leakage Risk:** Employer portal proxy for company name. |
| `original_title` | `title` | **Extreme Cardinality:** 4,800+ raw strings; summarized into `normalized_role`. |
| `job_description`| `jobDescription` | **Computational / Leakage Control:** Reserved for future multimodal text evaluation. |
| `reviews_count` | `ReviewsCount` | **High Missingness (36%):** Missing for majority of boutique startups; employer-specific bias. |
| `aggregate_rating`| `AggregateRating`| **High Missingness (36%):** Unreliable Glassdoor ratings introduce employer-level bias. |
| `job_uploaded` | `jobUploaded` | **Unreliable Temporal Quality:** Relative string ("6 Days Ago") lacking true calendar timestamp. |
| `job_id` | `jobId` | **Arbitrary Identifier:** Primary key used only for relational tracking, not prediction. |

---

## 6. CONTENT LEAKAGE AUDIT & SPLIT SPECIFICATION

- **Unique Content Fingerprints:** **5,793 groups** across 5,859 records.
- **Duplicate Content Groups:** **48 groups** containing **114 records (1.95%)**.
- **Identical Salaries in Duplicate Groups:** 59.9% share identical salary figures.
- **Prescribed Split Protocol for Phase India-4:**
  ```python
  from sklearn.model_selection import GroupShuffleSplit
  gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
  train_idx, test_idx = next(gss.split(X, y, groups=df["content_fingerprint"]))
  ```
  This ensures that identical recruitment openings never cross the train/holdout boundary.
