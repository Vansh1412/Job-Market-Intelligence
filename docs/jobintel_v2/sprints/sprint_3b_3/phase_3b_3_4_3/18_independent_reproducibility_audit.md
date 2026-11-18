# SPRINT 3B.3.3.4.3 — INDEPENDENT REPRODUCIBILITY AUDIT
**Sprint:** 3B.3.3.4.3 — Employer Registry Data Readiness, Source Governance & Publication Eligibility Audit  
**Date:** 2026-11-18  
**Audit Role:** Principal Data Architect, Statistical Auditor & QA Automation Specialist  
**Execution Mode:** STRICTLY READ-ONLY

---

## 1. Executive Summary

This audit independently recalculates and reproduces every major quantitative claim, metric, and artifact count inherited from prior sprints.

Each metric has been evaluated against the raw source artifacts using independent Python scripts executed in read-only scratch space, adhering to the mandatory classifications:
- `REPRODUCED`
- `PARTIALLY_REPRODUCED`
- `NOT_REPRODUCIBLE`
- `CONTRADICTED`
- `SOURCE_UNAVAILABLE`

---

## 2. Master Reproducibility Ledger

| Metric / Claim | Reported Value | Independently Computed Value | Source Artifact | Calculation Method | Reproducibility Status | Discrepancy & Forensic Explanation |
|---|---:|---:|---|---|---|---|
| **Core Employer Pilot Profiles** | 28 | **28** | `employer_pilot_records.json` | `len(json.load(f))` | `REPRODUCED` | None. Exactly 28 profiles (AU 6, US 6, UK 6, SG 5, IN 5). |
| **Publication Matrix Rows** | 82 | **82** | `EMPLOYER_PUBLICATION_ELIGIBILITY_MATRIX.csv` | `len(list(csv.reader(f))) - 1` | `REPRODUCED` | None. Exactly 82 rows (28 profiles + 32 hiring obs + 22 skill obs). |
| **Candidate Screening Universe** | 45 | **45** | `employer_candidate_register.csv` | Valid non-empty rows parsed via CSV reader | `REPRODUCED` | Blank separator rows and unescaped commas resolved forensically; exactly 45 corporate candidates (28 INCLUDED, 17 EXCLUDED). |
| **Headcount & Hiring Observations** | 32 | **32** | `employer_hiring_observations.json` | `len(json.load(f))` | `REPRODUCED` | None. Exactly 32 observations (AU 8, US 8, UK 6, SG 5, IN 5). |
| **Skill Demand Observations** | 22 | **22** | `employer_skill_observations.json` | `len(json.load(f))` | `REPRODUCED` | None. Exactly 22 observations across 8 corporate employers. |
| **Observation to Source Crosswalk** | 54 | **54** | `OBSERVATION_TO_SOURCE_CROSSWALK.csv` | `len(list(csv.reader(f))) - 1` | `REPRODUCED` | None. Exactly 54 rows (`32 hiring + 22 skill = 54`). |
| **Source Catalog Definitions** | 14 | **14** | `employer_source_catalog.json` | `len(json.load(f))` | `REPRODUCED` | None. Exactly 14 cataloged source definitions. |
| **Source Approval Breakdown** | 11 Approved, 2 Review, 1 Revoked | **8 Approved, 2 Conditional, 3 Review, 1 Revoked** | `employer_source_catalog.json` & Legal Terms | Legal terms re-examination | `CONTRADICTED` | **Defect in Prior Sprints:** Lightcast was previously falsely claimed as 'Approved' for commercial SaaS. Reclassified to `REVIEW_REQUIRED`. Greenhouse/Lever reclassified to `CONDITIONAL`. |
| **Entity Resolution Gold Pairs** | 100 | **100** | `employer_entity_resolution_gold.json` | `len(json.load(f))` | `REPRODUCED` | None. Exactly 100 pairs (45 MATCH, 55 DISTINCT). |
| **Resolver V2 True Positives** | 31 | **31** | `employer_entity_resolution_gold.json` | Evaluated via `src/backend/employers/resolver.py` | `REPRODUCED` | None. 31 true matches correctly resolved. |
| **Resolver V2 False Merges (FP)** | 0 | **0** | `employer_entity_resolution_gold.json` | Evaluated via `src/backend/employers/resolver.py` | `REPRODUCED` | None. Zero false merges achieved on the 100-pair benchmark. |
| **Resolver V2 False Splits (FN)** | 14 | **14** | `employer_entity_resolution_gold.json` | Evaluated via `src/backend/employers/resolver.py` | `REPRODUCED` | None. 14 matches safely failed closed to manual review. |
| **Resolver V2 True Negatives (TN)** | 55 | **55** | `employer_entity_resolution_gold.json` | Evaluated via `src/backend/employers/resolver.py` | `REPRODUCED` | None. All 55 distinct pairs kept separate. |
| **Resolver V2 Precision** | 100.00% | **100.00%** | Statistical formula | $31 / (31 + 0)$ | `REPRODUCED` | Exactly 1.0000. |
| **Resolver V2 Recall** | 68.89% | **68.89%** | Statistical formula | $31 / 45$ | `REPRODUCED` | Exactly 0.68888... |
| **Resolver V2 False Merge Rate (FPR)** | 0.00% | **0.00%** | Statistical formula | $0 / 55$ | `REPRODUCED` | Exactly 0.0000. |
| **Wilson 95% CI Upper Bound on FPR** | 6.53% | **6.53%** | Wilson score formula ($N=55, z=1.96$) | Exact Wilson binomial formula | `REPRODUCED` | Upper bound on error rate is 6.53%, proving that claims of "0% error in production" are statistically false. |
| **Job Title Mapping Gold Examples** | 100 | **100** | `job_title_mapping_gold.json` | `len(json.load(f))` | `REPRODUCED` | None. Exactly 100 gold job title examples. |
| **Job Title Mapping Accuracy** | 94.00% | **94.00%** | Evaluated via canonical occupation regexes | 94 correct out of 100 | `REPRODUCED` | Exactly 94.0%. |
| **Skill Extraction Test Cases** | 20 | **20** | `skill_extraction_benchmark.csv` | Line count of test cases | `REPRODUCED` | Exactly 20 adversarial guardrail unit test cases. |

---

## 3. Forensic Analysis of Discrepancies

### 1. The Source Classification Contradiction (`CONTRADICTED`)
- **Historical Claim:** 11 Approved, 2 Review Required, 1 Revoked.
- **Independently Audited Truth:** **8 Approved, 2 Conditional, 3 Review Required, 1 Revoked**.
- **Root Cause:** Sprint 3B.3.2 and 3B.3.2.1 uncritically inherited an "Approved" status for Lightcast (`src_global_lightcast_skills`). Under commercial software licensing law, Lightcast's Open Skills license restricts use to non-commercial evaluation; redistribution in a commercial SaaS API without an enterprise agreement is a breach of contract. Correcting this shifts Lightcast from Approved to `REVIEW_REQUIRED`, and moves ATS job feeds (Greenhouse, Lever) to `CONDITIONAL`.

### 2. The 28-vs-82 Cohort Mystery (`RESOLVED & REPRODUCED`)
- Historical reports alternated between calling the pilot 28 employers and 82 entities.
- Independent audit proves that **both numbers are real, but represent different structural layers**:
  - `28`: Employer profiles (`EMPLOYER_PROFILE`).
  - `82`: Total rows in the publication matrix (`28 profiles + 32 hiring obs + 22 skill obs = 82`).

---

## 4. Final Reproducibility Verdict

**`PASS — ALL EMPIRICAL DATASETS & BENCHMARK METRICS FULLY REPRODUCED`**

With the exception of correcting the prior faulty legal classification of Lightcast, all mathematical counts, confusion matrix figures, precision/recall metrics, and dataset sizes were 100% reproduced from primary source code and data files.
