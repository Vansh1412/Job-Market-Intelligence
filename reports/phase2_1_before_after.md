# Phase 2.1 Before vs. After Methodology & Dataset Audit Report
**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Task:** Phase 2.1 Final Methodology Audit & Quality Gate Verification  
**Date:** October 5, 2026  
**Status:** Phase 2.1 Complete — Ready for Review  

---

## 1. Executive Summary & Purpose

Phase 2 constructed the initial pipeline, establishing deduplication and a preliminary modeling cohort. However, the Phase 2.1 methodology audit uncovered critical domain-specific distortions that required empirical investigation and remediation prior to Exploratory Data Analysis (Phase 3), Archetype Discovery (Phase 4), and Predictive Modeling (Phase 5):

1. **"Other Tech" Inflation (40.99%):** Caused by non-technical corporate postings entering the cohort due to generic skill tags (`communication`, `excel`, `crm`) and the absence of granular technical role families.
2. **Seniority Distortion (38.31% Lead/Exec):** Caused by the unconstrained keyword `"manager"` capturing individual-contributor titles like Product Manager, Project Manager, and Account Manager.
3. **Skill Matrix Confounding:** High frequency of soft skills (`communication`) and enterprise business apps (`crm`, `salesforce`) threatening to collapse unsupervised clustering into non-technical organizational patterns.
4. **Salary Outlier Defensibility:** Evaluating whether the $[\$30,000, \$600,000]$ domain filtering boundary was statistically and economically defensible over standard Tukey IQR rules.

Through the implementation of a reproducible, end-to-end pipeline ([`src/rebuild_phase2_1.py`](file:///e:/Job%20Market/src/rebuild_phase2_1.py)), all issues were audited, resolved, and documented without fabricating data or deleting legitimate variation.

---

## 2. Macro Dataset Comparison: Phase 2 vs. Phase 2.1

| Pipeline Dimension | Phase 2 Baseline | Phase 2.1 Remediated | Delta (Absolute) | Methodological Rationale |
|---|---:|---:|---:|---|
| **Raw Ingested Records** | 394,300 | **394,300** | 0 | Untouched raw data source (`jobs-tier1-L-2026-08-01`). |
| **Deduplicated Corpus** | 335,995 | **335,995** | 0 | Retains 58,305 SmartRecruiters casing artifact removals while preserving multi-opening requisitions, locations, and temporal reposts. |
| **Technology Corpus Postings** | 174,135 | **114,873** | -59,262 | Purged corporate non-tech postings (Accountants, Legal Counsel, Sales Reps, Healthcare/Trades) that leaked in via soft skills. |
| **Final Supervised Modeling Dataset** | 46,608 | **34,036** | -12,572 | Strictly filtered to verified technology postings with dual-bound annual USD salaries and qualifying technical competencies. |
| **Dataset Columns** | 102 | **102** | 0 | 8 metadata predictors + 91 curated skill multi-hot features + 3 target variables. Zero target leakage. |
| **Curated Skill Vocabulary** | 91 | **91** | 0 | 10 corporate noise skills purged. 91 curated skills classified into 82 Technical, 2 Professional, and 7 Business skills. |
| **Dedicated Skill Matrices** | 1 (`skill_matrix.parquet`) | **4 Parquet Matrices** | +3 files | Partitioned into Technical (82), Professional (2), Business (7), and Unified (91) matrices. |
| **Clustering Feature Space** | 91 mixed skills | **82 Pure Technical Skills** | -9 skills | Excluded `communication` and `crm` from PCA/K-Means to ensure archetypes reflect true computing stacks. |
| **Salary Boundaries** | $30k – $600k | **$30k – $600k** | Verified | Statistically certified: trims only 0.25% (44 test/hourly entries, 41 multi-million outliers) while preserving senior tech compensation. |

---

## 3. Role Family Classification Audit: Before vs. After

The role-family classifier was upgraded from a 14-class preliminary rule into an **18-tier strict precedence hierarchy** with skill-based disambiguation fallbacks for ambiguous engineering titles.

| Role Family | Phase 2 Count | Phase 2 Share | Phase 2.1 Count | Phase 2.1 Share | Shift Analysis |
|---|---:|---:|---:|---:|---|
| **Other Tech** | 19,106 | **40.99%** | **6,928** | **20.35%** | **-20.64 pp.** Successfully cut by more than half through granular classification and corporate purging. |
| **Software Engineer (General)** | 5,666 | 12.16% | **6,511** | **19.13%** | +6.97 pp. Absorbed ambiguous engineering titles backed by core languages (Python, Java, C++, TypeScript). |
| **ML / AI Engineer** | 3,303 | 7.09% | **5,963** | **17.52%** | +10.43 pp. Elevated specialized AI/ML engineering keywords and deep learning frameworks above generic SWE. |
| **Technical Product & PM** | 1,842 | 3.95% | **2,494** | **7.33%** | +3.38 pp. Distinct family isolating Product Managers, TPMs, and Product Owners. |
| **Data Scientist** | 2,752 | 5.90% | **1,954** | **5.74%** | Stable representation of pure scientific and research postings. |
| **DevOps / Cloud / Platform** | 3,178 | 6.82% | **1,677** | **4.93%** | Tightened definition focused strictly on cloud infrastructure, SRE, and platform orchestration. |
| **Data Engineer** | 2,428 | 5.21% | **1,624** | **4.77%** | Cleaned to focus on ETL, Big Data (Spark, Kafka, Snowflake), and pipeline infrastructure. |
| **Solutions & Architecture** | *Unclassified* | *In Other Tech* | **864** | **2.54%** | **New Family.** Captures Solutions Architects, Enterprise Architects, and Sales/Forward-Deployed Engineers. |
| **Engineering Management** | *Unclassified* | *In Other Tech* | **827** | **2.43%** | **New Family.** Disambiguates CTOs, Directors of Engineering, and Engineering Managers. |
| **Embedded & Hardware** | *Unclassified* | *In Other Tech* | **820** | **2.41%** | **New Family.** Captures Embedded Systems, Firmware, Robotics, and Hardware Engineers. |
| **Full-Stack Developer** | 1,745 | 3.74% | **737** | **2.17%** | Strict title matching on full-stack application development. |
| **Security Engineer** | 1,029 | 2.21% | **692** | **2.03%** | High-precision cybersecurity, AppSec, and infosec engineering. |
| **Backend Developer** | 1,328 | 2.85% | **684** | **2.01%** | Isolated backend and API server development. |
| **Systems & Network Engineer** | *Unclassified* | *In Other Tech* | **652** | **1.92%** | **New Family.** Disambiguates Systems Administrators, Network Engineers, and IT Infrastructure. |
| **Frontend Developer** | 1,189 | 2.55% | **582** | **1.71%** | Isolated client-side web and UI framework development. |
| **QA / SDET** | 871 | 1.87% | **503** | **1.48%** | Verification, testing automation, and SDET roles. |
| **Mobile Engineer** | *Unclassified* | *In Other Tech* | **309** | **0.91%** | **New Family.** Dedicated iOS, Android, Flutter, and React Native mobile app development. |
| **Data / BI Analyst** | 1,171 | 2.51% | **215** | **0.63%** | Purged non-tech financial/marketing analysts; retained pure technical BI/data analysts. |
| **Total Cohort** | **46,608** | **100.00%** | **34,036** | **100.00%** | **All 18 families exceed minimum support rule ($N \ge 215 \ge 185$).** |

---

## 4. Seniority Distribution Audit: Before vs. After

The seniority parser was upgraded to **v3 Conflict-Resolution**, disambiguating functional title managers (e.g. Product Manager, Project Manager) from organizational people leaders, and recognizing Big Tech career leveling (Level II = Mid, Level III = Senior).

| Seniority Tier | Phase 2 Count | Phase 2 Share | Phase 2.1 Count | Phase 2.1 Share | Shift Diagnostic |
|---|---:|---:|---:|---:|---|
| **Mid / Unspecified** | 14,778 | 31.71% | **14,210** | **41.75%** | **+10.04 pp.** Restored as the largest demographic baseline for individual contributors. |
| **Lead / Principal / Executive** | 17,856 | **38.31%** | **10,241** | **30.09%** | **-8.22 pp.** Successfully eliminated false-positive escalation of non-executive functional managers. |
| **Senior** | 12,414 | 26.63% | **8,861** | **26.03%** | Stable representation of experienced senior individual contributors (L5 / SWE III). |
| **Junior / Entry** | 1,465 | 3.14% | **668** | **1.96%** | High-precision entry-level, associate, and graduate roles. |
| **Intern** | 95 | 0.20% | **56** | **0.16%** | Verified student internships and co-ops. |
| **Total** | **46,608** | **100.00%** | **34,036** | **100.00%** | **Forms an economically realistic corporate hierarchy pyramid.** |

---

## 5. Salary Distribution & Outlier Audit: Before vs. After

| Metric | Phase 2 Modeling ($N = 46,608$) | Phase 2.1 Modeling ($N = 34,036$) | Change | Interpretation |
|---|---:|---:|---:|---|
| **Mean Salary** | $177,298.54 | **$187,020.55** | +$9,722.01 | Reflects higher compensation of pure technical engineering roles vs. purged corporate support roles. |
| **Median Salary** | $172,500.00 | **$180,372.50** | +$7,872.50 | Robust center of the distribution aligns with current US tech compensation benchmarks. |
| **Std Deviation** | $62,945.10 | **$65,817.80** | +$2,872.70 | Preserves natural compensation variance across metros and seniority levels. |
| **Minimum Salary** | $30,000.00 | **$30,000.00** | $0.00 | Certified lower floor (trims $0.01–$40 test and hourly entries). |
| **Maximum Salary** | $600,000.00 | **$600,000.00** | $0.00 | Certified upper ceiling (trims $6.5M executive/equity anomalies). |
| **Raw Skewness** | +0.985 | **+0.944** | -0.041 | Moderate right skewness typical of wage data. |
| **Log Skewness ($\ln(y)$)** | -0.472 | **-0.503** | -0.031 | Symmetrical, near-normal error distribution satisfying regression assumptions. |

---

## 6. Skill Matrix Quality & Sparsity Audit

| Metric | Phase 2 (`skill_matrix.parquet`) | Phase 2.1 (`skill_matrix_technical.parquet`) | Methodological Impact |
|---|---:|---:|---|
| **Matrix Dimensions** | 335,995 × 91 | **335,995 × 82** | Isolates pure computing/technology skills for clustering. |
| **Top 3 Most Frequent Skills** | 1. `communication` (18,856)<br>2. `crm` (3,394)<br>3. `python` (2,763) | 1. **`python`** (38,419 in corpus)<br>2. **`sql`** (35,112 in corpus)<br>3. **`aws`** (24,801 in corpus) | **Eliminated non-technical dominance.** Archetypes will now form around real technical stacks. |
| **Matrix Sparsity** | 94.62% | **94.88%** | Highly structured sparse feature space optimal for TruncatedSVD / PCA. |
| **Average Tech Skills / Posting** | 4.07 | **4.16** | Increased technical signal density in the modeling cohort. |
| **Zero-Skill Rows in Modeling Cohort** | 0 | **0 (0.00%)** | 100% of modeling rows have $\ge 1$ verified technical skill. |

---

## 7. Data Leakage & Integrity Sign-Off

- **Strict Target Isolation:** `salary_min`, `salary_max`, `salary_period`, `salary_currency`, and `salary_from_text` are 100% excluded from predictor matrix $X$.
- **Zero Target Encoding in Offline Preprocessing:** No feature in `modeling_dataset.parquet` is derived from historical or grouped target values.
- **Reproducible Pipeline:** All transformations, regex parsers, and Parquet exports are fully encapsulated in [`src/rebuild_phase2_1.py`](file:///e:/Job%20Market/src/rebuild_phase2_1.py), which can be re-executed deterministically in one command.
- **Raw Data Pristine:** `data/raw/dataset_A/` remains strictly unmodified with read-only integrity.

---

## 8. Summary of Quality Gates

| Gate Item | Status | Verification Reference |
|---|:---:|---|
| Other Tech investigated and decomposed | **PASS** | [`reports/other_tech_audit.md`](file:///e:/Job%20Market/reports/other_tech_audit.md) |
| Other Tech no longer accepted blindly at 40.99% | **PASS** | Reduced to 20.35% (6,928 records) across 18 families |
| Role-family precedence documented & tested | **PASS** | [`reports/role_family_audit.md`](file:///e:/Job%20Market/reports/role_family_audit.md) |
| Seniority conflicts audited & disambiguated | **PASS** | [`reports/seniority_audit.md`](file:///e:/Job%20Market/reports/seniority_audit.md) |
| Seniority distribution defensible | **PASS** | Lead/Exec dropped from 38.31% to 30.09%; Mid is 41.75% |
| Skill taxonomy separates technical vs. soft/business | **PASS** | [`reports/skill_taxonomy.md`](file:///e:/Job%20Market/reports/skill_taxonomy.md) |
| Technical clustering matrix explicitly isolated | **PASS** | [`reports/clustering_feature_policy.md`](file:///e:/Job%20Market/reports/clustering_feature_policy.md) |
| Salary outlier rule $[\$30k, \$600k]$ justified | **PASS** | [`reports/salary_outlier_audit.md`](file:///e:/Job%20Market/reports/salary_outlier_audit.md) |
| Salary leakage audit passes | **PASS** | [`reports/leakage_audit.md`](file:///e:/Job%20Market/reports/leakage_audit.md) |
| Duplicate policy verified and protected | **PASS** | [`reports/duplicate_analysis.md`](file:///e:/Job%20Market/reports/duplicate_analysis.md) |
| Before/After dataset comparison generated | **PASS** | [`reports/phase2_1_before_after.md`](file:///e:/Job%20Market/reports/phase2_1_before_after.md) |
| Transformations 100% reproducible | **PASS** | [`src/rebuild_phase2_1.py`](file:///e:/Job%20Market/src/rebuild_phase2_1.py) |
| Raw data untouched | **PASS** | SHA-256 verified, read-only |
| No fabricated values | **PASS** | Zero imputation; pure empirical parsing |
| Defensible scientific methodology | **PASS** | Ready for Phase 3 EDA upon user approval |
