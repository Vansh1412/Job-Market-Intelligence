# JOBINTEL 2.0 — SPRINT 3B.3.3.2
## DOCUMENT 02: SKILL DENOMINATOR LINEAGE & MATHEMATICAL RECONCILIATION

**Sprint:** 3B.3.3.2 — Critical Defect Remediation & Employer Resolver Hardening  
**Package:** WP-FIX-01  
**Author:** Principal Backend Engineer & Statistical Auditor  
**Date:** 2026-11-17  
**Status:** IMPLEMENTED & AUDIT VERIFIED  

---

### 1. Executive Summary

During Sprint 3B.3.3.1 Forensic Audit, a critical statistical presentation defect was identified:
On the frontend Skills Intelligence page (`SkillsPage.tsx`), skill penetration percentages were rendered alongside hardcoded sample size figures:
- USA Market: Displayed `N = 34,036`.
- India Market: Displayed `N = 5,859`.

However, the mathematical quotients for the displayed percentages did not match these sample sizes:
- USA Python count of 31,676 postings evaluated against $N = 34,036$ would yield $93.07\%$, but the UI displayed $9.4\%$.
- India Python count of 723 postings evaluated against $N = 5,859$ would yield $12.34\%$, but the UI displayed $13.6\%$.

This document provides the definitive data lineage tracing, mathematical proof, and architectural reconciliation of the true empirical denominators.

---

### 2. Empirical Data Lineage Tracing

#### 2.1 USA Market Lineage
Investigation of `src/backend/routers/skills.py` and the underlying Lightcast raw dataset revealed the exact lineage:
- **Raw General Postings Corpus:** $N = 335,995$ job postings collected across 2024.
- **Supervised Salary-Labeled Subset:** $N = 34,036$ postings containing validated, clean compensation data used to train the Phase 5 Ridge/XGBoost salary model.
- **Top Skill Frequency Analysis:**
  $$\text{Python Count} = 31,676$$
  $$\text{Observed Share} = \frac{31,676}{335,995} = 0.094275 \rightarrow 9.4\%$$
  $$\text{SQL Count} = 28,154 \rightarrow \frac{28,154}{335,995} = 0.08379 \rightarrow 8.4\%$$
  $$\text{Machine Learning Count} = 17,980 \rightarrow \frac{17,980}{335,995} = 0.05351 \rightarrow 5.4\%$$
  $$\text{AWS Count} = 16,140 \rightarrow \frac{16,140}{335,995} = 0.04804 \rightarrow 4.8\%$$

**Reconciliation Conclusion:** The true empirical denominator for the skill frequencies is the full observational corpus of **$N = 335,995$ postings**. The previously displayed $N = 34,036$ was conflated with the downstream supervised salary modeling subset.

#### 2.2 India Market Lineage
Investigation of `src/backend/services/india_service.py` and the India dataset revealed:
- **Raw Unfiltered Postings:** $N = 10,751$ job postings across all sectors and roles.
- **Salary Modeling Cohort:** $N = 5,859$ postings with valid annual CTC compensation.
- **Active Skill-Bearing Tech Cohort:** $N = 5,323$ tech postings containing structured skill annotations.
- **Top Skill Frequency Analysis:**
  $$\text{Python Count} = 723 \rightarrow \frac{723}{5,323} = 0.135825 \rightarrow 13.6\%$$
  $$\text{SQL Count} = 663 \rightarrow \frac{663}{5,323} = 0.124553 \rightarrow 12.5\%$$
  $$\text{Java Count} = 644 \rightarrow \frac{644}{5,323} = 0.120984 \rightarrow 12.1\%$$
  $$\text{AWS Count} = 538 \rightarrow \frac{538}{5,323} = 0.101070 \rightarrow 10.1\%$$

**Reconciliation Conclusion:** The true empirical denominator for the India tech skill frequencies is **$N = 5,323$ skill-bearing technology postings**. The previously displayed $N = 5,859$ was conflated with the salary model training cohort.

---

### 3. Mathematical Consistency Matrix

| Market | Skill | Raw Postings ($n$) | Supervised Modeling ($N_{\text{mod}}$) | True Empirical Population ($N$) | Quotient ($n / N$) | Displayed Percentage | Quotient with $N_{\text{mod}}$ (Flawed) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **USA** | Python | 31,676 | 34,036 | **335,995** | **9.43%** | **9.4%** | 93.07% (Mismatch) |
| **USA** | SQL | 28,154 | 34,036 | **335,995** | **8.38%** | **8.4%** | 82.72% (Mismatch) |
| **USA** | ML | 17,980 | 34,036 | **335,995** | **5.35%** | **5.4%** | 52.83% (Mismatch) |
| **USA** | AWS | 16,140 | 34,036 | **335,995** | **4.80%** | **4.8%** | 47.42% (Mismatch) |
| **India** | Python | 723 | 5,859 | **5,323** | **13.58%** | **13.6%** | 12.34% (Mismatch) |
| **India** | SQL | 663 | 5,859 | **5,323** | **12.46%** | **12.5%** | 11.32% (Mismatch) |
| **India** | Java | 644 | 5,859 | **5,323** | **12.10%** | **12.1%** | 10.99% (Mismatch) |
| **India** | AWS | 538 | 5,859 | **5,323** | **10.11%** | **10.1%** | 9.18% (Mismatch) |

---

### 4. Implementation Protocol

To remediate this across the entire stack:
1. **Backend Schemas & APIs:**
   - Expose dynamic metadata fields in `/api/v1/skills/{market_id}/{skill_name}`:
     - `population_size`: $335,995$ for USA, $5,323$ for India.
     - `population_type`: `"Total Observational Postings"` (USA) vs `"Skill-Bearing Tech Postings"` (India).
     - `observation_period`: `"2024 Full Year"` (USA) vs `"Q1-Q3 2024 Tech Cohort"` (India).
     - `denominator_source`: Clear data provenance citation.
2. **Frontend Type System & Presentation:**
   - Update `frontend/src/types.ts` with `SkillDetail` fields.
   - Update `frontend/src/pages/SkillsPage.tsx` to dynamically bind to `detail.population_size` and `detail.population_type`.
   - Eliminate all hardcoded `$N = 34,036$` and `$N = 5,859$` strings from the UI.
3. **Automated Verification:**
   - Unit tests in `tests/test_skill_denominator_integrity.py` asserting quotient integrity ($|n/N - p| < 0.15\%$).
   - Frontend tests in `frontend/src/__tests__/prediction_display.test.ts`.
