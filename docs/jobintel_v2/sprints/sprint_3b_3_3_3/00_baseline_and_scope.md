# JOBINTEL 2.0 — SPRINT 3B.3.3.3
## DOCUMENT 00: BASELINE AND EXECUTION SCOPE

**Sprint:** 3B.3.3.3 — Critical Employer Resolver Remediation & Salary Contract Correction  
**Role:** Principal Backend Engineer, Application Security Engineer, Data Governance Architect & Statistical API Contract Specialist  
**Execution Mode:** LOCAL CORRECTIVE IMPLEMENTATION & VERIFICATION ONLY (Zero Commits, Zero Pushes, Zero Deployments)  
**Date:** 2026-11-17  
**Status:** BASELINE VERIFIED & PHASE 0 COMPLETE  

---

### 1. Verified Repository Baseline

| Parameter | Expected Specification | Verified Runtime State | Status |
| :--- | :--- | :--- | :--- |
| **Working Repository** | `Job-Market-Intelligence` | `e:\Job Market` | **CONFIRMED** |
| **Working Branch** | `staging/sprint2c3` | `staging/sprint2c3` | **CONFIRMED** |
| **Baseline Staging HEAD** | `d1a8b027d10031b3568a3141f639e2f40a49be18` | `d1a8b027d10031b3568a3141f639e2f40a49be18` | **CONFIRMED** |
| **Production Baseline** | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | **CONFIRMED (ISOLATED)** |

---

### 2. Work Packages & Execution Scope

Sprint 3B.3.3.3 addresses the findings of the independent forensic audit `Sprint 3B.3.3.2.1` which issued a verdict of **FAIL — RELEASE BLOCKED**:

1. **Work Package A: Employer Resolver Security Remediation (`src/backend/employers/resolver.py`):**
   - Eliminate first-match early return.
   - Scan all registered employers and collect all matches.
   - Enforce fail-closed `MANUAL_REVIEW_REQUIRED` whenever multiple distinct entities share the same statutory identifier.
   - Prohibit arbitrary selection based on insertion order, list position, or similarity.
   - Eliminate artificial similarity score clamping (`max(similarity, 0.75)` in line 298).
   - Expand adversarial tests in `tests/test_employer_resolver.py` proving order-independence and multi-jurisdiction collision handling.
2. **Work Package B: Salary API Contract Correction:**
   - Align documentation with runtime reality: salary inference computes prediction $\pm$ empirical MAE dispersion under `confidence_interval`.
   - Purge unvalidated claims of conformal prediction intervals and calibrated 80%/95% coverage from documentation.
   - Retain backward compatibility for existing consumers.
3. **Work Package C: Skill Denominator Regression Protection:**
   - Preserve independently verified denominators ($N = 335,995$ for USA, $N = 5,323$ for India).
   - Ensure regression tests protect dynamic API metadata and UI consumption.
4. **Work Package D: Governance and Model Preservation:**
   - Verify all 10 model artifact hashes before and after remediation.
   - Verify golden predictions (USA = $244,423.42, India = 12.76 LPA / ₹1,275,646 INR).
   - Confirm UK demand and salary publication gates remain strictly intact.
5. **Work Package E: End-to-End Regression & Verification:**
   - Backend pytest suite, frontend vitest suite, production build (`tsc -b && vite build`).
