# JOBINTEL — PHASE INDIA-4 INPUT AUDIT REPORT
## Pre-Modeling Integrity Audit & Data Certification

---

**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Phase:** INDIA-4 (Leakage-Safe ML Modeling + Model Comparison)  
**Status:** PASSED (Verified & Certified)  
**Input Dataset:** `data/processed/india/india_modeling_cohort.parquet`  
**Input Schema:** `data/processed/india/india_feature_schema.json`  
**Audit Date:** October 2026  
**Auditor:** Lead Data Scientist & ML Engineer  

---

## 1. INPUT CERTIFICATION OVERVIEW

Before initiating machine learning model training or validation, an exhaustive audit of all input assets was performed to ensure strict adherence to Phase India-3 specifications, mathematical validity, and absolute leakage prevention.

```
========================================================================================
                      PHASE INDIA-4 INPUT AUDIT SUMMARY
========================================================================================
Modeling Cohort File:        data/processed/india/india_modeling_cohort.parquet
File Size / Hash (SHA256):   654,351 bytes / d4e32be45d84b159...
Sample Size (N):             5,859 records
Total Columns:               299 columns
Candidate Predictors (p):    290 features (3 numeric, 3 categorical, 284 binary skills)
Predictor Missingness:       0.00% across all 290 features (0 nulls)
Primary Target:              salary_midpoint_inr (Median: ₹10.00 LPA, Mean: ₹12.50 LPA)
Display Target:              salary_lpa (Range: 1.20 to 80.00 LPA)
Log Target:                  log_salary_midpoint_inr (Skewness: -0.173)
Grouping Key:                content_fingerprint (5,793 unique groups, 48 duplicate groups)
Target Leakage in Features:  0 detected (all raw salary strings/bounds quarantined)
High-Cardinality Identity:   0 in X (jobId, companyName, raw title quarantined)
USA Artifact Protection:     VERIFIED UNCHANGED (models/phase5/best_model.pkl: 619,464 bytes)
========================================================================================
```

---

## 2. TARGET INTEGRITY AUDIT

| Field Name | Type | Null Count | Min Value | Median Value | Mean Value | Max Value | Skewness | Audit Result |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `salary_midpoint_inr` | `float64` | 0 | ₹1,20,000 | ₹10,00,000 | ₹12,50,024 | ₹80,00,000 | +1.346 | **PASS** |
| `salary_lpa` | `float64` | 0 | 1.20 LPA | 10.00 LPA | 12.50 LPA | 80.00 LPA | +1.346 | **PASS** |
| `log_salary_midpoint_inr`| `float64` | 0 | 11.695 | 13.816 | 13.784 | 15.895 | -0.173 | **PASS** |

### Checks:
- [x] Target exists in modeling cohort.
- [x] Target contains exactly 0 NaN / null values.
- [x] Target is strictly positive ($> 0$).
- [x] Target values strictly adhere to the bounded domain [₹1.20 LPA, ₹80.00 LPA].

---

## 3. PREDICTOR MATRIX SPECIFICATION

The 290 candidate features are partitioned into explicit, disjoint groups:

### Group A: Role Family (1 Categorical)
- `normalized_role`: 14 distinct tech families (Software Engineer, Full Stack, Data Engineer, Cloud/DevOps, AI/ML Engineer, QA/Testing, Data Analyst, Data Scientist, Cybersecurity, Database Administrator, Frontend Developer, Business Analyst, Product/Program Manager, Other Technology). Zero non-tech records.

### Group B: Experience Features (2 Numerical)
- `experience_midpoint_years`: Mean = 5.76 years, Median = 5.00 years, Min = 0.0, Max = 22.5 years. Zero nulls.
- `experience_range_years`: Mean = 3.55 years, Median = 3.00 years, Min = 0.0, Max = 10.0 years. Zero nulls.

### Group C: Location Feature (1 Categorical)
- `city_grouped`: 23 levels (22 tech hubs with frequency $\ge 20$, plus `'Other'`). Top hubs: Bengaluru, Hyderabad, Pune, Mumbai, Chennai, Gurugram, Noida. Zero nulls.

### Group D: Work Mode (1 Categorical)
- `work_mode`: 3 levels (`Onsite` 76.98%, `Hybrid` 18.88%, `Remote` 4.15%). Zero nulls.

### Group E: Skill Count (1 Numerical)
- `total_selected_skill_count`: Count of selected skills present. Mean = 3.65, Median = 3.0, Max = 8. Zero nulls.

### Group F: Technical Skill Indicators (284 Binary)
- 284 columns prefixed with `skill_` (e.g., `skill_python`, `skill_sql`, `skill_aws`, `skill_react_js`, `skill_docker`, `skill_kubernetes`).
- Data type: integer indicators ($0$ or $1$).
- Portfolio coverage: 90.85% of records have $\ge 1$ skill. Sparsity: 98.71%.

---

## 4. METADATA & LEAKAGE QUARANTINE AUDIT

Six columns are verified as metadata / identifiers and **MUST NOT** enter predictor matrix $X$:
1. `job_id`: Relational primary key.
2. `content_fingerprint`: Grouping vector for `GroupShuffleSplit` and `GroupKFold`.
3. `original_title`: Raw scraped title (extreme cardinality).
4. `company_name`: Employer text (overfitting/memorization risk).
5. `city_raw`: Un-grouped granular city.
6. `state`: Scraped state metadata.

### Target Leakage Verification:
- `minimumSalary` / `minimum_salary_inr`: **ABSENT from X**
- `maximumSalary` / `maximum_salary_inr`: **ABSENT from X**
- `salary` / `original_salary`: **ABSENT from X**
- `salary_band`: **ABSENT from X**
- Post-hoc target statistics: **ABSENT from X**

---

## 5. GROUPING INTEGRITY AUDIT

- **Total records:** 5,859
- **Unique `content_fingerprint` values:** 5,793
- **Duplicate groups (size $\ge 2$):** 48 groups comprising 114 records (1.95% of cohort).
- **Audit Conclusion:** Grouped train/holdout partitioning (`GroupShuffleSplit`, `test_size=0.20`, `random_state=42`) and 5-fold grouped CV (`GroupKFold`) are strictly required and confirmed operational.

---

## 6. USA PIPELINE INTEGRITY AUDIT

- `models/phase5/best_model.pkl`: Size = 619,464 bytes, SHA256 = `55c1b7fd87d2a04c...` (VERIFIED UNCHANGED).
- USA raw, processed, notebook, report, and script files remain 100% frozen.
- USA assets modified: **0**.

---

## 7. INPUT AUDIT VERDICT

**STATUS: PASS — INPUT CERTIFICATION COMPLETE.**  
All input conditions for Phase India-4 machine learning experimentation are satisfied without exceptions.
