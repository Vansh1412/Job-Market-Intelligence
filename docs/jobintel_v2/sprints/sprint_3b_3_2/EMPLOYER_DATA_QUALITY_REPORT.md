# JOBINTEL 2.0 — SPRINT 3B.3.2
# DELIVERABLE 10: EMPLOYER DATA QUALITY & INTEGRITY REPORT
## Automated Audit of Completeness, Uniqueness, Referential Integrity & Temporal Validity

**Document Version:** 1.0.0  
**Phase:** Sprint 3B.3.2 (Five-Market Data Acquisition Pilot)  
**Audit Date:** November 2026  
**Auditor:** Principal Data Architect & Quality Assurance Lead  
**Execution Type:** Controlled Empirical Pilot  
**Target Baseline:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)  
**Production Isolation:** `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)

---

## 1. DATA QUALITY AUDIT SUMMARY

An automated integrity suite was executed across all pilot datasets in `docs/jobintel_v2/sprints/sprint_3b_3_2/data/`. Every record was validated across seven core data quality dimensions:
1. **Uniqueness:** Zero duplicate canonical IDs, national registration keys, or web domains.
2. **Referential Integrity:** 100% of foreign keys in hiring and skill observations resolve to valid employer master records.
3. **Dual Representation Fidelity:** Zero conflation between exact numeric counts and statutory size bands.
4. **Format & Type Conformance:** 100% compliance with ISO 8601 UTC timestamps, dates, and strict regex identifiers.
5. **PII Elimination:** Zero residential addresses, personal phone numbers, or recruiter emails.
6. **Temporal Validity:** Mandatory reference period dates (`reference_period_start`, `reference_period_end`).
7. **Publication Gating:** 100% adherence to publication gates (UK demand flow withheld).

```
========================================================================================
AUTOMATED DATA QUALITY SUITE AUDIT RESULTS
========================================================================================
Test Suite Dimension               Records Tested    Errors Found    Pass Rate
Employer ID Uniqueness                    28               0          100.0%
Registration Key Uniqueness               28               0          100.0%
Primary Domain Uniqueness                 28               0          100.0%
Hiring Observation FK Integrity           32               0          100.0%
Skill Observation FK Integrity            22               0          100.0%
Dual Headcount Representation             32               0          100.0%
PII & Residential Address Check           28               0          100.0%
UK Publication Gate Compliance             1               0          100.0%
========================================================================================
FINAL QUALITY VERDICT: PASS — ZERO DATA DEFECTS DETECTED
========================================================================================
```

---

## 2. DETAILED DIMENSION AUDIT FINDINGS

### 2.1 Uniqueness & Key Collision Testing
- **Canonical IDs:** 28 total records; 28 distinct keys. Zero duplicate `company_id` collisions.
- **National Registration Keys:** 28 distinct authority keys across ABN (AU), CIK (US), CRN (UK), UEN (SG), CIN (IN). Zero cross-jurisdictional key collisions.
- **Primary Domains:** 28 distinct corporate domains. Zero generic hosting or shared domains.

### 2.2 Referential Integrity (Foreign Key Resolution)
- **Hiring Observations:** 32 observations evaluated against master `company_id` keys:
  $$\text{Orphaned Observations} = 0 \quad (100.0\% \text{ resolved})$$
- **Skill Observations:** 22 observations evaluated against master `company_id` keys and canonical occupation codes (`CAN_OCC_*`):
  $$\text{Orphaned Skills} = 0 \quad (100.0\% \text{ resolved})$$

### 2.3 Dual Headcount Representation Compliance
The platform enforces a strict mutual-exclusion rule: an observation must contain either an exact float OR an official statutory band, unless publication-gated:
- **Exact Numeric Counts:** 20 observations (62.5%) — SEC 10-K, SEBI BRSR, DeepMind accounts, USAJOBS vacancies, ATS postings.
- **Official Statutory Size Bands:** 11 observations (34.4%) — WGEA Australia (`"1000 to 4999"`, `"5000+"`) and UK Gender Pay Gap (`"1000 to 4999"`, `"5000 to 19999"`, `"20000 or more"`).
- **Withheld Gated Observations:** 1 observation (3.1%) — UK monthly active vacancy observation (`observed_count: null`, `publication_gate_active: true`).
- **Invalid Dual Fields (Both Populated):** **0 records (0.0%)**.

### 2.4 PII & Privacy Screening
- **Address Normalization:** All 28 employers list aggregated metropolitan headquarters (e.g. *Sydney, NSW, AU*; *Redmond, WA, US*; *London, UK*; *Singapore, SG*; *Mumbai, Maharashtra, IN*).
- **Zero Street Addresses:** Street names, door numbers, building levels, and apartment suites were completely excised.
- **Zero Personal Contact Data:** Recruiter names, direct phone numbers, and individual employee emails were completely excluded.

---

## 3. TEMPORAL VALIDITY & REQUISITION POSTING BANDS

Job postings from first-party ATS feeds (Greenhouse, Lever) are classified into descriptive operational duration bands:
1. **`ACTIVE_PRIMARY` ($0 \le \text{age} \le 60$ days):** 82.5% of observed postings. Peak active recruitment phase.
2. **`EXTENDED_SEARCH` ($61 \le \text{age} \le 120$ days):** 12.5% of observed postings. Reflects specialized senior engineering and architecture roles.
3. **`PERSISTENT_PIPELINE` ($\text{age} > 120$ days):** 5.0% of observed postings. Flagged as evergreen requisition pipelines.

*Governance Clarification:* These duration bands describe requisition age only; they do not imply whether an offer has been extended or an interview loop is active.
