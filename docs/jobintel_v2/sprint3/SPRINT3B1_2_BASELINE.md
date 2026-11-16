# JOBINTEL 2.0 — SPRINT 3B.1.2 BASELINE RECONCILIATION
## Salary Data Remediation and Evidence Closure Baseline Report

**Document Reference:** `JOBINTEL-SPRINT3B1_2-BASELINE-20261116`  
**Date:** November 16, 2026  
**Target Branch:** `staging/sprint2c3`  
**Current HEAD Commit:** `3b0cb0c` (`docs(audit): publish sprint 3B.1.1 independent salary data integrity and methodology audit report`)  
**Previous Implementation Commit:** `0d0b2ed` (`feat(salary): implement cross-market salary intelligence, dual FX/PPP metrics, and 11-dimension comparability engine (Sprint 3B.1)`)  
**Production Baseline:** `master` at `198b79dcdff08a5be5f08847c4262d31a3ce261e` (Verified UNTOUCHED)  
**Execution Mode:** Controlled staging remediation, evidence-backed implementation, regression testing, and audit closure.

---

## 1. Executive Context and Mandate

Sprint 3B.1 implemented the cross-market descriptive salary intelligence engine across 5 jurisdictions:
- **United States (US):** 7 occupations (BLS OEWS May 2023)
- **United Kingdom (UK):** 8 occupations (ONS ASHE 2024 Revised — Fail-Closed Gate HTTP 503)
- **Australia (AU):** 4 occupations (ABS EEH Cat. 6306.0 May 2023)
- **Singapore (SG):** 6 occupations (MOM OWS 2023)
- **India (IN):** 3 occupations (JobIntel Statistical CTC Models 2024)

Sprint 3B.1.1 performed an independent empirical audit on this implementation and returned a **CONDITIONAL PASS — VERIFIED WITH LIMITATIONS**.
The audit cataloged 8 specific corrective action items (`C-01` through `C-08`), identifying:
1. **Singapore MOM Annualization Multiplier (`C-01`):** Monthly Gross Wage was annualized using a 13-month multiplier under an assumed Annual Wage Supplement (AWS), whereas MOM statutory definition explicitly excludes bonuses and AWS from gross monthly wage.
2. **Singapore Percentile Non-Availability (`C-02`):** MOM OWS officially publishes only P25, P50, and P75. P10 and P90 were synthetically interpolated and must be set to `null`.
3. **Australia Extreme Tail Percentile Provenance (`C-03`):** ABS EEH (Cat. 6306.0) publishes P25, P50, and P75 at the 4-digit unit group level. P10 and P90 are not officially published for 6-digit detailed OSCA roles and must be set to `null` to adhere to strict provenance rules.
4. **US BLS Source Reference Specificity (`C-04`):** In `sources.json`, `source_url` pointed to a single occupation URL (`oes151252.htm`) rather than the national OEWS index (`oes_nat.htm`), and per-occupation references were needed.
5. **Comparability Engine Branch Order Defect (`C-05`):** In `salary_service.py`, `NOT_COMPARABLE` was eclipsed by `COMPARABLE_WITH_MAJOR_CAVEATS` for low-confidence (< 0.50) or unmapped comparisons.
6. **Purchasing Power Parity (PPP) Limitation Specification (`C-06`):** Reference to "ICP 2024 Revision" implied a primary 2024 benchmark survey rather than a World Bank WDI private consumption model extrapolation (`PA.NUS.PRVT.PP`), and required explicit qualification as domestic consumption living-cost parity, not labor cost parity.
7. **Nominal Foreign Exchange (FX) Description (`C-07`):** FX rates are static 2024 annual reference averages, not dynamic live spot rates.
8. **UK ASHE Classification Consistency (`C-08`):** Legacy ingestion script uses SOC 2010 while current salary observations use SOC 2020. The HTTP 503 fail-closed gate must remain active until crosswalk reconciliation is formalized.

---

## 2. Repository and Environment Baseline

### 2.1 Git Verification
```
Branch:              staging/sprint2c3
Local HEAD Commit:   3b0cb0c4cb3aa7b0366ec96131375d04ef531db8
Remote Tracking:     origin/staging/sprint2c3 (synchronous)
Working Tree:        Clean (0 modified, 0 untracked files)
Production Master:   198b79dcdff08a5be5f08847c4262d31a3ce261e (Verified UNTOUCHED)
```

### 2.2 Execution Environment
- **Operating System:** Microsoft Windows 11 Enterprise / PowerShell 7+
- **Python Runtime:** Python 3.13.9 (64-bit)
- **Node.js Runtime:** v20+ / Vite 8.3.3 / Vitest 5.0.3
- **Test Runner:** Pytest 8.4.2

### 2.3 Cryptographic Dataset Hashes (LF Normalized SHA-256)
Every critical data, schema, and service file hash was verified prior to remediation:

| Component | Path | LF Normalized SHA-256 Hash |
| :--- | :--- | :---: |
| **Salary Sources** | `src/backend/data/salary/sources.json` | `dbc8b0b6cf85e111d206c4380834d7e33fd321383b2df91ad14626d45855aa8a` |
| **PPP & FX Rates** | `src/backend/data/salary/ppp_fx_rates.json` | `aef330bb54cfcd4c78ac62c50de718165806dbf4d65e7cdf22c47f03b87c75a3` |
| **Salary Observations** | `src/backend/data/salary/observations.json` | `d078348b2ebec93d6037ad34c662c0d1139ae3329d63c864989bea511753e88e` |
| **Salary Schemas** | `src/backend/schemas/salary.py` | `148b58b5afc6384fc03437023280dff685e6d51b7507b992ad3a87844df2b52f` |
| **Salary Service** | `src/backend/services/salary_service.py` | `1dd59d1af58ed3f8fc9612e7b824ec7077e9ad4cd0341352e41ce170a8cc6c4e` |
| **Salary Routers** | `src/backend/routers/salary.py` | `687533418353dc5dd570450de8130a03832e710a3e3dc6488737f00c69f00a8c` |
| **Classifications** | `src/backend/data/occupations/classifications.json` | `b36b0683658005ed151deaccdcf134279fbdfe211ce46c5baba9a5d5c0231d53` |
| **National Occupations**| `src/backend/data/occupations/national_occupations.json` | `5fabc96a73002271a12e4443f6411d06139023f36d7f7b0c62f327cac856074d` |
| **Canonical Concepts** | `src/backend/data/occupations/canonical_occupations.json` | `a33cb726b8395e39e72818ddbbb12366fb7abb30b3b5eada2d05671bff78e040` |
| **Mappings** | `src/backend/data/occupations/mappings.json` | `79a2c1cd4adc8425c189fa658267877cf76e12b6bb68d41a8aab4fc6212da607` |

---

## 3. Pre-Remediation Test Verification

The entire repository test suites were executed to establish regression baselines:
- **Backend Test Suite:** `python -m pytest tests/`
  - **Result:** **330 passed** in 15.29s (100% pass rate).
  - Included golden prediction tests (`test_golden_predictions.py`), prediction parity (`test_prediction_parity.py`), UK governance gate (`test_uk_salary_api.py`), and salary intelligence (`test_salary_intelligence.py`).
- **Frontend Test Suite:** `npm --prefix frontend test -- --run`
  - **Result:** **3 test files, 9 passed** in 730ms.
- **Frontend Production Build:** `npm --prefix frontend run build`
  - **Result:** **Clean production bundle** (2,892 modules transformed in 262ms).
- **ML Artifact Integrity:**
  - India Random Forest model: Bitwise identical, checksum verified.
  - USA Ridge Regression model: Bitwise identical, checksum verified.

---

## 4. Remediation Scope & Action Plan

Sprint 3B.1.2 will execute the remediation in 13 structured phases:
1. **Phase 0:** Baseline reconciliation document (`SPRINT3B1_2_BASELINE.md`).
2. **Phase 1:** Detailed observation-level evidence matrix across all 28 national occupations (`SALARY_OBSERVATION_EVIDENCE_MATRIX.md`).
3. **Phase 2:** Singapore MOM annualization correction (12x multiplier) and nullification of unpublished P10/P90 (`C-01`, `C-02`).
4. **Phase 3:** Australia ABS EEH nullification of extreme tail P10/P90 to enforce strict official provenance (`C-03`).
5. **Phase 4:** US BLS OEWS national and per-occupation citation refinement (`C-04`).
6. **Phase 5:** India JobIntel model estimate transparency documentation.
7. **Phase 6:** Comparability engine branch reordering to properly return `NOT_COMPARABLE` (`C-05`).
8. **Phase 7:** PPP and Nominal FX metadata alignment (`C-06`, `C-07`).
9. **Phase 8:** UK ASHE classification consistency documentation and preservation of fail-closed HTTP 503 (`C-08`).
10. **Phase 9:** Frontend display robustness for null percentiles and updated benchmark labels.
11. **Phase 10:** Backend test suite expansions verifying all remediated behaviors.
12. **Phase 11:** End-to-end regression verification across Python, Vitest, and Vite build.
13. **Phase 12 & 13:** Documentation package finalization, staging commit, and push.
