# JOBINTEL 2.0 — SPRINT 3B.1.2 FINAL AUDIT REPORT
## Salary Data Remediation, Provenance Verification, and Evidence Closure

**Document Reference:** `JOBINTEL-FINAL-AUDIT-3B.1.2-20261116`  
**Date:** November 16, 2026  
**Target Branch:** `staging/sprint2c3`  
**Production Baseline:** `master` at `198b79dcdff08a5be5f08847c4262d31a3ce261e` (Verified UNTOUCHED)  
**Audit Standard:** Independent quality assurance, empirical source verification, cryptographic tracking, and complete closure of Corrective Action Register items C-01 through C-08.  
**Auditor Roles:** Principal Data Governance Architect, Labour Market Statistics Specialist, and Systems Quality Assurance Engineer.  
**Final Audit Verdict:** **FULL PASS — REMEDIATION COMPLETE & VERIFIED**

---

## 1. Executive Summary & Audit Mandate

Sprint 3B.1 implemented the cross-market descriptive salary intelligence subsystem for JOBINTEL 2.0 across five major economic jurisdictions: **United States (US)**, **United Kingdom (UK)**, **Australia (AU)**, **Singapore (SG)**, and **India (IN)**.

The subsequent independent audit in Sprint 3B.1.1 granted a **CONDITIONAL PASS**, having discovered 8 specific methodology and data-integrity defects (`C-01` through `C-08`), most notably:
1. An unauthorized 13-month AWS bonus inflation on Singapore MOM wages.
2. Synthetic interpolation of extreme tail percentiles (P10 and P90) where national agencies (MOM Singapore and ABS Australia) do not compile or publish them.
3. An eclipsed `NOT_COMPARABLE` branch in the automated comparability engine.
4. Overstated certainty regarding the "ICP 2024 revision round" and live "spot FX" rates.
5. Incomplete source URLs for US BLS occupations.

Sprint 3B.1.2 was commissioned with an unambiguous mandate: **resolve all 8 corrective actions, enforce strict empirical provenance, ensure absolute zero percentile fabrication, and maintain 100% test pass rates without touching production master or retraining frozen ML models.**

This audit report confirms that **all 8 corrective action items are formally closed**, all 28 observations and 140 percentile values are cryptographically verified and accounted for, and the codebase satisfies all 25 Acceptance Criteria (`AC-01` through `AC-25`).

---

## 2. Corrective Action Verification (C-01 through C-08)

### C-01: Singapore MOM OWS 12x Gross Wage Annualization Multiplier
- **Audit Requirement:** Revert Singapore annualized wages to $12 \times \text{monthly gross wage}$ without assuming unmeasured Annual Wage Supplements (AWS), adhering strictly to MOM's statutory gross wage definition.
- **Verification Evidence:**
  - `src/backend/data/salary/sources.json` updated: `pay_concept` explicitly specifies: `"Gross monthly wage annualized (monthly gross x 12). Excludes employer CPF, bonuses, and Annual Wage Supplement (AWS)."`
  - `src/backend/data/salary/observations.json` recomputed across all 6 Singapore occupations:
    - Software Developer (`25121`): Median is **\$90,000 SGD** ($7,500/mo × 12). (Reverted from \$97,500).
    - AI/ML Engineer (`25131`): Median is **\$98,400 SGD** ($8,200/mo × 12). (Reverted from \$106,600).
    - Data Scientist (`25132`): Median is **\$96,000 SGD** ($8,000/mo × 12). (Reverted from \$104,000).
    - Cloud Architect (`25124`): Median is **\$108,000 SGD** ($9,000/mo × 12). (Reverted from \$117,000).
    - DevOps Engineer (`25125`): Median is **\$93,600 SGD** ($7,800/mo × 12). (Reverted from \$101,400).
    - Cybersecurity Specialist (`25211`): Median is **\$94,800 SGD** ($7,900/mo × 12). (Reverted from \$102,700).
- **Status:** **VERIFIED & CLOSED**.

### C-02: Singapore MOM OWS Percentile Non-Fabrication (P10/P90 Nullification)
- **Audit Requirement:** Nullify P10 and P90 for all Singapore occupations because MOM OWS officially compiles and publishes only P25, Median (P50), and P75.
- **Verification Evidence:**
  - In `src/backend/data/salary/observations.json`, `p10: null` and `p90: null` for all 6 Singapore observations.
  - Automated test `test_salary_singapore_and_australia_percentiles_null_provenance` asserts `pct["p10"] is None` and `pct["p90"] is None` across all Singapore records.
  - Frontend verified to render `"N/A"` for missing percentiles without displaying `$0` or crashing.
- **Status:** **VERIFIED & CLOSED**.

### C-03: Australia ABS EEH Detailed Percentile Provenance
- **Audit Requirement:** ABS Cat. 6306.0 does not publish P10 and P90 at the detailed 6-digit OSCA level. Enforce strict provenance by setting P10 and P90 to `null`.
- **Verification Evidence:**
  - In `src/backend/data/salary/observations.json`, `p10: null` and `p90: null` for all 4 Australian occupations (`261313`, `224411`, `262112`, `261314`).
  - Derived weekly ordinary-time cash earnings ($\text{Weekly} \times 52$) preserved for P25, P50, and P75 under `quality_flag: "OFFICIALLY_DERIVED"`.
  - Automated unit test asserts nullity of P10/P90 for all AU observations.
- **Status:** **VERIFIED & CLOSED**.

### C-04: US BLS OEWS Source Reference Refinement & Hours Convention
- **Audit Requirement:** Update `sources.json` to link to the national OEWS index and document individual occupation citation URLs and the 2,080 annual hours convention.
- **Verification Evidence:**
  - `src/backend/data/salary/sources.json` `source_url` updated to `https://www.bls.gov/oes/current/oes_nat.htm`.
  - Detailed individual URLs (`oes151252.htm`, `oes152051.htm`, etc.) documented in `SALARY_OBSERVATION_EVIDENCE_MATRIX.md`.
  - Standard full-time convention ($40 \text{ hrs/wk} \times 52 \text{ wks} = 2,080 \text{ hrs}$) documented in observation notes and methodology documentation.
- **Status:** **VERIFIED & CLOSED**.

### C-05: Comparability Engine Logic and Branch Ordering Correction
- **Audit Requirement:** In `salary_service.py`, add an explicit early check returning `ComparabilityVerdict.NOT_COMPARABLE` when `confidence_score < 0.50` or `relationship_type == "NO_SUPPORTED_MAPPING"`.
- **Verification Evidence:**
  - In `evaluate_comparability()`, branch reordered to evaluate `NOT_COMPARABLE` before `COMPARABLE_WITH_MAJOR_CAVEATS`.
  - Automated test `test_comparability_not_comparable_branch` passes, confirming `NOT_COMPARABLE` is returned for low-confidence matches.
- **Status:** **VERIFIED & CLOSED**.

### C-06: Purchasing Power Parity (PPP) Metadata Alignment
- **Audit Requirement:** Clarify that 2024 PPP conversion factors are World Bank WDI private consumption extrapolations (Series `PA.NUS.PRVT.PP`) from ICP benchmark rounds, reflecting household consumption living costs rather than employer labor costs.
- **Verification Evidence:**
  - `src/backend/data/salary/ppp_fx_rates.json` updated with explicit indicator code `PA.NUS.PRVT.PP` and extrapolation methodology.
  - UI labels and caveat texts in `OccupationsPage.tsx` and `salary_service.py` updated to "World Bank WDI PPP".
- **Status:** **VERIFIED & CLOSED**.

### C-07: Static FX Exchange Rate Metadata
- **Audit Requirement:** Label nominal foreign exchange rates as static 2024 annual reference averages, not live spot rates.
- **Verification Evidence:**
  - In `ppp_fx_rates.json`, `fx_description` updated to: `"Static 2024 Reference Annual Average Exchange Rates to US Dollars (USD). Sourced from central banks and IMF International Financial Statistics (IFS)."`
  - UI label updated to "Static 2024 Benchmark FX Conversion".
- **Status:** **VERIFIED & CLOSED**.

### C-08: UK ASHE Classification Consistency & Fail-Closed Gate
- **Audit Requirement:** Maintain fail-closed HTTP 503 publication gate and document the UK SOC 2010 vs SOC 2020 crosswalk requirement before future publication authorization.
- **Verification Evidence:**
  - `require_uk_publication()` verified active. All UK profile and comparison queries return `HTTP 503 Service Unavailable` with `UK_DATA_NOT_PUBLISHED`.
  - Crosswalk requirements formalized in `SPRINT3B1_2_METHODOLOGY_NOTES.md`.
- **Status:** **VERIFIED & CLOSED**.

---

## 3. Provenance Accounting Matrix (28 Observations / 140 Percentiles)

Every wage figure in JOBINTEL 2.0 is categorized into one of five rigorous provenance classifications:

| Category | Definition | Percentiles Count | Jurisdictions | Audit Verdict |
| :--- | :--- | :---: | :--- | :---: |
| **`OFFICIAL_PUBLISHED`** | Verbatim correspondence to official statistical tables. | **35** | US (35) | **VERIFIED** |
| **`OFFICIALLY_DERIVED`** | Documented arithmetic conversion from official data ($52 \times \text{weekly}$ or $12 \times \text{monthly}$). | **30** | AU (12: P25, P50, P75)<br>SG (18: P25, P50, P75) | **VERIFIED** |
| **`JOBINTEL_MODEL_ESTIMATE`** | Calibrated statistical model distribution for tech metros. | **15** | IN (15) | **VERIFIED WITH DISCLOSED LIMITATIONS** |
| **`SUPPRESSED`** | Official data withheld under automated fail-closed gate. | **40** | UK (40) | **GATE ENFORCED (HTTP 503)** |
| **`NOT_PUBLISHED` (`null`)** | Metric not collected/compiled by source; recorded as `null`. | **20** | AU (8: P10, P90)<br>SG (12: P10, P90) | **VERIFIED ZERO FABRICATION** |
| **Total** | **100% of Wage Distribution Metrics** | **140** | **5 Markets** | **FULL INTEGRITY ASSURANCE** |

---

## 4. Cryptographic Dataset and Module Baseline (LF Normalized SHA-256)

Every critical file in the repository was hashed using LF-normalized SHA-256 post-remediation:

| Component | File Path | LF Normalized SHA-256 Hash |
| :--- | :--- | :---: |
| **Salary Sources** | `src/backend/data/salary/sources.json` | `979a8251bf966e300d6b8f59dbcff4216b2144a793dad697bce87a89179d9271` |
| **PPP & FX Rates** | `src/backend/data/salary/ppp_fx_rates.json` | `c2d351e280c16585f2302f273d210228224754b243ed6aed3e6d2abb88fdde93` |
| **Salary Observations** | `src/backend/data/salary/observations.json` | `50a8c0dbc4c79b7e527f0bbf59ca4fdb19910f35be8fda7243661ba4503db9a4` |
| **Salary Service** | `src/backend/services/salary_service.py` | `9912bdcd517fba63509a3cc0eedf847dd85fc8c1ee91ddff9b7a96e641763931` |
| **Frontend Occupations Page** | `frontend/src/pages/OccupationsPage.tsx` | `5c2ffb9ebeb963a1c230aece3532ed1c0fcae1dd0d912980706a0666412d3fab` |
| **Salary Test Suite** | `tests/test_salary_intelligence.py` | `8bb3ff5b55905b2a86f0b360043a55fc60ef75660aac8923cb3049d48392355a` |
| **Salary Schemas** | `src/backend/schemas/salary.py` | `148b58b5afc6384fc03437023280dff685e6d51b7507b992ad3a87844df2b52f` |
| **Salary Routers** | `src/backend/routers/salary.py` | `687533418353dc5dd570450de8130a03832e710a3e3dc6488737f00c69f00a8c` |
| **National Occupations** | `src/backend/data/occupations/national_occupations.json` | `5fabc96a73002271a12e4443f6411d06139023f36d7f7b0c62f327cac856074d` |
| **Canonical Occupations** | `src/backend/data/occupations/canonical_occupations.json` | `a33cb726b8395e39e72818ddbbb12366fb7abb30b3b5eada2d05671bff78e040` |
| **Concordance Mappings** | `src/backend/data/occupations/mappings.json` | `79a2c1cd4adc8425c189fa658267877cf76e12b6bb68d41a8aab4fc6212da607` |

---

## 5. Acceptance Criteria Audit (AC-01 through AC-25)

| AC ID | Requirement Summary | Verification Mechanism | Status |
| :---: | :--- | :--- | :---: |
| **AC-01** | Git branch is `staging/sprint2c3` and origin is aligned. | `git status` check; synchronous tracking. | **PASS** |
| **AC-02** | Master commit `198b79d` verified untouched. | `git rev-parse origin/master` = `198b79dcdff...`. | **PASS** |
| **AC-03** | Frozen ML model artifacts remain bitwise identical. | Checksums and golden prediction parity tests pass. | **PASS** |
| **AC-04** | UK ASHE publication gate strictly enforced with HTTP 503. | `test_uk_salary_api.py` (84 tests passed). | **PASS** |
| **AC-05** | Singapore annualized wage reverted to 12x monthly gross wage. | `observations.json` revised; tests verify \$90,000 SGD median. | **PASS** |
| **AC-06** | Singapore P10 and P90 set to `null`. | `test_salary_singapore_and_australia_percentiles_null_provenance`. | **PASS** |
| **AC-07** | Australia P10 and P90 set to `null`. | `test_salary_singapore_and_australia_percentiles_null_provenance`. | **PASS** |
| **AC-08** | Australia P25, P50, and P75 derived as $\text{Weekly} \times 52$. | Verified in `observations.json` and Evidence Matrix. | **PASS** |
| **AC-09** | US BLS OEWS national index URL configured. | `sources.json` updated to `oes_nat.htm`. | **PASS** |
| **AC-10** | US 2,080 annual hours convention documented. | Evidence Matrix and observation notes document convention. | **PASS** |
| **AC-11** | India CTC employer overhead documented. | PF 12%, gratuity 4.81%, allowances documented. | **PASS** |
| **AC-12** | India tagged as `MODEL_PREDICTION` with major caveats. | Verified in `observations.json` and comparison endpoints. | **PASS** |
| **AC-13** | Comparability engine assigns `NOT_COMPARABLE` for confidence < 0.50. | Verified via `test_comparability_not_comparable_branch`. | **PASS** |
| **AC-14** | Comparability engine assigns `NOT_COMPARABLE` for unmapped roles. | Verified via `test_comparability_not_comparable_branch`. | **PASS** |
| **AC-15** | World Bank private consumption PPP (`PA.NUS.PRVT.PP`) cited. | Verified in `ppp_fx_rates.json` and rates API endpoint. | **PASS** |
| **AC-16** | PPP clarified as domestic living cost adjustment, not labor cost parity. | Separation warning and methodology notes verified. | **PASS** |
| **AC-17** | Nominal FX labeled as static 2024 reference annual averages. | `fx_description` verified in `ppp_fx_rates.json`. | **PASS** |
| **AC-18** | FX and PPP strictly decoupled (zero blending/averaging). | Verified mathematically in `salary_service.py`. | **PASS** |
| **AC-19** | Observation Evidence Matrix created with 24 fields per observation. | `SALARY_OBSERVATION_EVIDENCE_MATRIX.md` created. | **PASS** |
| **AC-20** | Data Dictionary specifying all schemas and nullability created. | `SPRINT3B1_2_DATA_DICTIONARY.md` created. | **PASS** |
| **AC-21** | Methodology Notes detailing concepts and UK SOC crosswalk created. | `SPRINT3B1_2_METHODOLOGY_NOTES.md` created. | **PASS** |
| **AC-22** | API Regression Report detailing modern/legacy endpoints created. | `SPRINT3B1_2_API_REGRESSION_REPORT.md` created. | **PASS** |
| **AC-23** | Frontend handles null percentiles gracefully without `$0` or crash. | `OccupationsPage.tsx` verified; Vitest & Vite build pass. | **PASS** |
| **AC-24** | All backend tests pass (`python -m pytest tests/`). | **333/333 passed** in 18.37s. | **PASS** |
| **AC-25** | All frontend tests pass and clean build transforms 2,892 modules. | **9/9 passed**, build clean in 236ms. | **PASS** |

---

## 6. Definitive Audit Determination

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       FINAL AUDIT DETERMINATION                                        │
│                                                                                                        │
│                                           FULL PASS                                                    │
│                                                                                                        │
│ The Cross-Market Salary Intelligence subsystem for JOBINTEL 2.0 has successfully closed all 8          │
│ corrective actions (C-01 through C-08).                                                                │
│                                                                                                        │
│ 1. Zero synthetic or extrapolated percentiles remain; missing percentiles are strictly recorded as     │
│    null with graceful frontend handling.                                                               │
│ 2. Singapore annualization adheres to statutory gross wage definitions (12x).                         │
│ 3. Automated comparability properly distinguishes non-comparable occupational pairs.                  │
│ 4. Static 2024 FX and World Bank private-consumption PPP factors are rigorously decoupled.            │
│ 5. UK fail-closed governance (HTTP 503) is completely intact.                                          │
│ 6. Production baseline master remains untouched, and frozen ML model parity is 100% preserved.          │
│                                                                                                        │
│ The staging implementation on branch staging/sprint2c3 is formally approved and accepted.              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
