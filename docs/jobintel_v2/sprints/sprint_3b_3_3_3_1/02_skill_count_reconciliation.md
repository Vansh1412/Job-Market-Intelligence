# JOBINTEL 2.0 — SPRINT 3B.3.3.3.1
## DOCUMENT 02: SKILL DENOMINATOR & NUMERATOR RECONCILIATION

**Sprint:** 3B.3.3.3.1 — Independent Remediation Verification & Release Gate Audit  
**Audit Target:** Audit B — Verification of Skill Frequencies, Denominators, and Count Lineage  
**Status:** FULLY RECONCILED — PRIMARY GROUND TRUTH CONFIRMED  

---

### 1. The Discrepancy Statement

In previous independent audits:
- **USA:** Total Postings $N = 335,995$; Python count = **$31,676$**
- **India:** Active Cohort $N = 5,323$; Development count = **$723$**; Python count = **$644$**

In Sprint 3B.3.3.3 Document 04 and final report text:
- **USA:** Total Postings $N = 335,995$; Python count = **$31,583$**
- **India:** Active Cohort $N = 5,323$; Development count = **$724$**; Python count = **$644$**

This audit independently inspected the source datasets, router code, and test assertions to determine which counts are genuine and why the documented numbers fluctuated.

---

### 2. Primary Source Dataset Audit

An independent examination of the underlying datasets and analytics tables on disk was performed:

#### 2.1 USA Skill Frequency Dataset (`reports/tables/phase3/skill_frequency.csv`)
- **File SHA-256:** `9be2e30f1466...` (verified immutable).
- **Row for Python:**
  - `Skill`: `"python"`
  - `Modeling_Count`: `11,593` (count in modeling cohort $N = 34,036$)
  - `Corpus_Count`: **`31,676`** (exact count in general corpus $N = 335,995$)
  - `Corpus_Prevalence`: `0.0942752124287563`
- **Calculation:**
  $$\frac{31,676}{335,995} = 0.0942752... \approx 9.4275\% \rightarrow \mathbf{9.4\%}$$

#### 2.2 India Skill Analytics Table (`reports/tables/india/india_skill_analytics.json`)
- **File SHA-256:** `2ba244f7158d...` (verified immutable).
- **Row for Development (`skill_development`):**
  - `display_name`: `"Development"`
  - `posting_count`: **`723`**
  - `demand_percentage`: `13.6`
- **Calculation:**
  $$\frac{723}{5,323} = 0.135825... \approx 13.582\% \rightarrow \mathbf{13.6\%}$$
- **Row for Python (`skill_python`):**
  - `display_name`: `"Python"`
  - `posting_count`: **`644`**
  - `demand_percentage`: `12.1`
- **Calculation:**
  $$\frac{644}{5,323} = 0.120984... \approx 12.098\% \rightarrow \mathbf{12.1\%}$$

---

### 3. Forensic Root Cause of Documented Count Differences

Why did Sprint 3B.3.3.3 report $31,583$ instead of $31,676$, and $724$ instead of $723$?

The investigation revealed that this was an **arithmetic back-calculation error in the documentation text**:
1. In the frontend and API responses, prevalence percentages are rounded to one decimal place for user presentation:
   - USA Python: $9.4\%$
   - India Development: $13.6\%$
2. The author of Sprint 3B.3.3.3 Document 04 attempted to reconstruct the raw counts by multiplying the verified denominators by the rounded display percentages:
   $$335,995 \times 9.4\% = 31,583.53 \rightarrow \mathbf{31,583}$$
   $$5,323 \times 13.6\% = 723.928 \rightarrow \mathbf{724}$$
3. This multiplication of a rounded percentage by the denominator discarded the true integer counts ($31,676$ and $723$).

---

### 4. Code & Test Assertion Verification

Crucially, **neither the backend code nor the automated test suite ever adopted the incorrect $31,583$ or $724$ counts**:
- In `src/backend/routers/skills.py` (`get_skill_detail`): Loads directly from `get_skill_frequency_df()`, returning `postings = 31676`.
- In `src/backend/services/india_service.py` (`get_skill_detail`): Loads directly from `india_skill_analytics.json`, returning `posting_count = 723`.
- In `tests/test_skill_denominator_integrity.py`:
  ```python
  # Line 15:
  assert detail["postings"] == 31676  # PASSES
  assert detail["population_size"] == 335995  # PASSES
  
  # Line 31:
  assert detail["posting_count"] == 723  # PASSES
  assert detail["population_size"] == 5323  # PASSES
  ```
All 4 tests in `tests/test_skill_denominator_integrity.py` pass cleanly because they assert the true, ground-truth integer counts.

---

### 5. Summary Reconciliation Table

| Metric | Source Ground Truth | Backend Runtime | Test Assertion | Sprint 3B.3.3.3 Text | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **USA Total Postings** | $335,995$ | $335,995$ | $335,995$ | $335,995$ | **VERIFIED** |
| **USA Python Count** | **$31,676$** | **$31,676$** | **$31,676$** | $31,583$ *(back-calc)* | **CORRECT (Data = 31,676)** |
| **India Active Cohort** | $5,323$ | $5,323$ | $5,323$ | $5,323$ | **VERIFIED** |
| **India Development Count** | **$723$** | **$723$** | **$723$** | $724$ *(back-calc)* | **CORRECT (Data = 723)** |
| **India Python Count** | **$644$** | **$644$** | **$644$** | $644$ | **VERIFIED** |

**Conclusion:** The underlying data, source hashes, router logic, and regression tests are 100% consistent with the historical baseline ($31,676$ and $723$). The figures $31,583$ and $724$ were documentation back-calculation artifacts with zero presence in runtime code or test suites.
