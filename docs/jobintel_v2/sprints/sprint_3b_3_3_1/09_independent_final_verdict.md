# SPRINT 3B.3.3.1: INDEPENDENT FINAL AUDIT VERDICT
## Comprehensive Audit Synthesis, Governance Evaluation & Release Authorization Decision

**Sprint ID:** 3B.3.3.1  
**Target Branch:** `staging/sprint2c3`  
**Current Baseline Commit:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  
**Production Baseline Commit:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  
**Audit Mode:** STRICTLY READ-ONLY  
**Auditor:** Independent Principal Engineer, Statistical Auditor, API Contract Reviewer & Data Governance Specialist  
**Evaluation Date:** 2026-11-17  

---

## 1. Final Audit Verdict

# **`CONDITIONAL PASS — RELEASE BLOCKED`**

### Summary of Verdict:
The implementation delivered in Sprint 3B.3.3 successfully achieved several critical objectives:
- Maintained 100% bitwise cryptographic integrity of all machine learning models.
- Preserved floating-point prediction parity across all golden benchmark profiles.
- Preserved the statutory UK demand publication gate (`UK_DEMAND_DATA_NOT_PUBLISHED` / `null`).
- Preserved 100% backward compatibility of existing API endpoints.
- Achieved a passing score across 376 backend pytest tests and 20 frontend vitest tests.

**HOWEVER**, in accordance with the governing mandate that:
> *"A claimed passing test suite does not override a semantic, statistical, API-contract, or governance defect,"*

this forensic audit identified **two critical blocking defects** and **two moderate contract limitations** that strictly prohibit proceeding directly to commit, push, and deployment in Sprint 3B.3.4:

1. **[BLOCKING DEFECT 1 — SKL-01] Skill Cohort Denominator Conflation:**  
   In `frontend/src/pages/SkillsPage.tsx`, the UI hardcodes `Cohort N = 34,036` (USA) and `Cohort N = 5,859` (India) directly under the skill postings count. In the USA, Python displays **"31,676 postings (Cohort N = 34,036)"** alongside a **9.4%** prevalence badge. In reality, $34,036$ is the salary modeling training dataset, while the $31,676$ count was derived from the $335,995$ general corpus. Displaying $31,676$ out of $34,036$ suggests a $93.1\%$ prevalence, creating an overt, mathematically absurd contradiction on the screen.
2. **[BLOCKING DEFECT 2 — RES-01] Resolver Substring & Contradictory Name Vulnerability:**  
   In `src/backend/employers/resolver.py`, statutory identifier matching uses insecure substring containment (`request.statutory_identifier.lower() in str(src.source_reference).lower()`) and **immediately returns `AUTOMATICALLY_RESOLVED` without verifying whether `candidate_name` contradicts the entity name**. This allows a query for a subsidiary (e.g. "Google India Private Limited") or an unrelated entity passing an SEC CIK to automatically resolve to the US parent, completely bypassing the parent-subsidiary anti-collapsing protections mandated by JOBINTEL data governance.
3. **[MODERATE LIMITATION — SAL-01] Salary API Contract Envelope Naming:**  
   The backend JSON payload retains the outer dictionary key `confidence_interval`. Although internal tags label it as `empirical_mae_dispersion`, retaining the outer key name invites automated API consumers to treat an empirical error band ($pred \pm MAE$) as a calibrated statistical confidence interval.
4. **[MODERATE LIMITATION — MAE-01] Recomputed USA Median AE Divergence:**  
   Stored report artifacts cite USA Median AE as `$26,384.22`. Independent recomputation of the frozen pipeline on the 6,808 test vectors yields `$26,775.59` (a \$391.37 / 1.48% divergence). The raw test prediction vector was not preserved on disk.

---

## 2. Findings Synthesis Matrix

| Finding ID | Area | Severity | Status | Summary |
| :--- | :--- | :--- | :--- | :--- |
| **BSL-01** | Git Baseline | None | **VERIFIED** | Staging baseline `d1a8b027d100...` and branch confirmed. |
| **BSL-02** | Production Isolation | None | **VERIFIED** | Production `master` (`198b79dcd...`) strictly isolated. |
| **SKL-01** | Skills UI Semantics | **CRITICAL (BLOCKER)** | **INCORRECT** | Conflates salary model size ($34,036$) with corpus denominator ($335,995$), creating a visible $93\%$ vs $9.4\%$ contradiction. |
| **SKL-02** | India Skill Denominator | Minor | **VERIFIED WITH LIMITATIONS** | Skill active denominator is $\sim 5,316$ rather than full $5,859$ cohort. |
| **SAL-01** | Prediction Interval Contract | Moderate | **VERIFIED WITH LIMITATIONS** | UI is clean (point estimate only), but backend API retains legacy `confidence_interval` dictionary key. |
| **SAL-02** | Prediction Route Schemas | Minor | **VERIFIED WITH LIMITATIONS** | Routes return unconstrained dicts without explicit Pydantic response models. |
| **MAE-01** | USA Median AE Lineage | Minor | **VERIFIED WITH LIMITATIONS** | Recomputed Median AE is $\$26,775.59$ vs stored $\$26,384.22$ ($1.48\%$ delta). |
| **MAE-02** | Test Residual Storage | Minor | **VERIFIED WITH LIMITATIONS** | Raw holdout prediction vector was not persisted as a dedicated parquet table. |
| **RES-01** | Entity Resolver Logic | **CRITICAL (BLOCKER)** | **INCORRECT / DEFECT** | Statutory ID substring match automatically resolves without checking if `candidate_name` is a subsidiary or contradictory. |
| **RES-02** | Substring Matching in ID | High | **INCORRECT** | Uses `in` operator on source reference string, allowing partial matches. |
| **RES-03** | Ignored Statutory Authority | Minor | **NOT VERIFIED** | `statutory_authority` is accepted in request schema but never evaluated. |
| **PAG-01** | Employer Pagination | Moderate | **VERIFIED WITH LIMITATIONS** | Unparameterized requests return full list; unbounded growth risk. |
| **PAG-02** | Pagination Metadata | Minor | **VERIFIED WITH LIMITATIONS** | Returns plain list; lacks total count envelope or pagination headers. |
| **MOD-01** | Model Pickles | None | **VERIFIED** | 10/10 model and pipeline hashes match bit-for-bit. |
| **MOD-02** | Feature Contracts | None | **VERIFIED** | 123-feature USA and 290-feature India feature contracts intact. |
| **GOV-01** | UK Demand Gating | None | **VERIFIED** | Value is strictly null; `UK_DEMAND_DATA_NOT_PUBLISHED` active. |
| **GOV-02** | Zero Null-to-Zero Substitution | None | **VERIFIED** | Nulls are preserved in API and rendered as gated badge in UI. |
| **TST-01** | Test Suite Execution | None | **VERIFIED** | 376 backend and 20 frontend tests pass cleanly; Vite build clean. |
| **TST-02** | Test Coverage Blindspots | High | **VERIFIED WITH LIMITATIONS** | Green test suite masked semantic denominator error and resolver vulnerability. |

---

## 3. Detailed Analysis of Blocking Defects

### 3.1 Defect 1: Skill Cohort Denominator Conflation (Finding SKL-01)
- **The Issue:** In `frontend/src/pages/SkillsPage.tsx`, the subtitle under Demand Prevalence renders:
  `{detailPostings.toLocaleString()} postings (Cohort N = {isUSA ? '34,036' : '5,859'})`
- **Why It Fails:**
  - In the USA market, `detailPostings` for Python is `31,676`.
  - The UI presents this as: `"31,676 postings (Cohort N = 34,036)"`.
  - Directly above this, the prevalence is displayed as **`9.4%`**.
  - Any user, statistician, or stakeholder performing basic arithmetic will calculate:
    $$\frac{31,676}{34,036} = 93.07\%$$
    This completely contradicts the 9.4% figure.
  - The true source of 31,676 postings is the full deduplicated corpus of **335,995 job postings** ($31,676 / 335,995 = 9.43\%$).
  - The figure 34,036 belongs exclusively to the supervised salary modeling cohort (postings with disclosed salaries), where Python only appeared 11,593 times ($11,593 / 34,036 = 34.06\%$).
- **Impact:** Compromises data integrity and damages institutional credibility.

### 3.2 Defect 2: Resolver Statutory ID Overrides Contradictory Legal Identity (Finding RES-01)
- **The Issue:** In `src/backend/employers/resolver.py`:
  ```python
  if request.statutory_identifier:
      stat_match = any(
          request.statutory_identifier.lower() in str(src.source_reference).lower()
          for src in emp.source_references
      )
      if stat_match and (not cand_market or cand_market == emp_market):
          return EmployerResolutionResponse(
              resolution_match_type=ResolutionMatchType.EXACT_IDENTIFIER_MATCH,
              resolved_company_id=emp.company_id,
              review_status=EntityReviewStatus.AUTOMATICALLY_RESOLVED,
              candidates=(candidate,),
          )
  ```
- **Why It Fails:**
  - If a user queries for an Indian subsidiary:
    `candidate_name: "Google India Private Limited"`, `statutory_identifier: "0001652044"` (Alphabet's US CIK).
  - Because `request.market_id` is omitted, `not cand_market` evaluates to `True`.
  - Because `"0001652044"` is found in Google LLC's source reference, the resolver returns:
    `resolved_company_id: "google-llc"`, `review_status: AUTOMATICALLY_RESOLVED`!
  - It does this **without ever checking the candidate name**, completely ignoring that the candidate name contains the subsidiary marker "India Private Limited"!
  - Furthermore, using `in` allows partial string attacks (e.g. querying `"SEC"` or `"0001"` matches any company with those characters in its reference URL).
- **Impact:** Directly violates the core mandate of Sprint 3B.3.3: *"Never automatically collapse subsidiaries into parents or treat shared brands as identical legal identities."*

---

## 4. Release Authorization & Action Directive

### Can Sprint 3B.3.4 (Staging Commit & Deployment) Proceed?
# **`NO — SPRINT 3B.3.4 IS STRICTLY BLOCKED`**

Proceeding to commit and deploy these changes to staging would package a critical semantic error into the UI and deploy a vulnerable entity resolver.

### Mandatory Corrective Path: Sprint 3B.3.3.2
Before Sprint 3B.3.4 can be authorized, an immediate, tightly scoped corrective sprint (**Sprint 3B.3.3.2**) must be executed to resolve the two blocking defects:

1. **Fix Skills UI Denominator (Corrective Task 1):**
   - Update `frontend/src/pages/SkillsPage.tsx`:
     Change `(Cohort N = {isUSA ? '34,036' : '5,859'})` to accurately cite the true observation corpus:
     `(Corpus N = {isUSA ? '335,995' : '97,318'})`, or dynamically populate the denominator from the backend analytics endpoint.
2. **Harden Employer Entity Resolver (Corrective Task 2):**
   - In `src/backend/employers/resolver.py`:
     - Disallow substring containment: require exact token matching on statutory IDs.
     - Before returning `AUTOMATICALLY_RESOLVED`, check whether `candidate_name` contains subsidiary markers or has contradictory legal structure.
     - If a subsidiary marker is detected in `candidate_name` while matching a parent's statutory ID, force the review status to `MANUAL_REVIEW_REQUIRED` and set `is_subsidiary_relationship = True`.
     - Evaluate `statutory_authority` when provided.
   - Add negative and adversarial unit tests in `tests/test_employer_resolver.py` proving that contradictory subsidiary names with parent statutory IDs route to `MANUAL_REVIEW_REQUIRED`.
3. **Re-Verify Full Test Suite & Build:**
   - Run backend tests (376+ passing).
   - Run frontend tests (20+ passing).
   - Verify TypeScript compilation and Vite build.
4. **Authorize Sprint 3B.3.4:**
   - Once Sprint 3B.3.3.2 confirms these fixes, re-issue verdict and authorize staging commit and release packaging.
