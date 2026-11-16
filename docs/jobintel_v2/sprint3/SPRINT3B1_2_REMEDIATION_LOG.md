# JOBINTEL 2.0 — SPRINT 3B.1.2 REMEDIATION LOG
## Corrective Action Execution & Provenance Closure Register

**Document Reference:** `JOBINTEL-REMEDIATION-LOG-3B.1.2-20261116`  
**Date:** November 16, 2026  
**Target Branch:** `staging/sprint2c3`  
**Audit Baseline Reference:** `JOBINTEL-AUDIT-3B.1.1-20261116` (`3b0cb0c`)  
**Status:** **ALL 8 CORRECTIVE ACTIONS CLOSED (C-01 THROUGH C-08)**

---

## 1. Remediation Register Overview

| Action ID | Severity | Component | Finding Description | Remediation Applied | Status |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **C-01** | **HIGH** | `observations.json`<br>`sources.json` | Singapore MOM OWS 13x AWS multiplier applied without empirical basis. | Reverted annualization multiplier to statutory $12 \times \text{monthly gross wage}$. Updated `sources.json` pay concept description. | **CLOSED** |
| **C-02** | **HIGH** | `observations.json` | Singapore MOM OWS P10 and P90 claimed figures were synthetically estimated. | Set P10 and P90 to `null` across all 6 Singapore occupations. Updated quality flag to `OFFICIALLY_DERIVED`. | **CLOSED** |
| **C-03** | **MEDIUM** | `observations.json` | Australia ABS EEH P10 and P90 were unit-group interpolations. | Set P10 and P90 to `null` across all 4 Australian occupations. Retained official P25, P50, and P75 ($52 \times \text{weekly}$). | **CLOSED** |
| **C-04** | **MEDIUM** | `sources.json`<br>`observations.json` | US BLS OEWS URL pointed to single occupation page (`oes151252.htm`) for all 7 roles. | Updated base `source_url` in `sources.json` to parent index (`oes_nat.htm`). Documented 2,080 annual hours convention. | **CLOSED** |
| **C-05** | **MEDIUM** | `salary_service.py` | Comparability engine never assigned `NOT_COMPARABLE` because confidence < 0.88 caught low-confidence matches. | Added explicit condition returning `NOT_COMPARABLE` when `confidence_score < 0.50` or `relationship_type == "NO_SUPPORTED_MAPPING"`. | **CLOSED** |
| **C-06** | **LOW** | `ppp_fx_rates.json`<br>`salary_service.py` | Reference to "ICP 2024 Revision" implied 2024 was an ICP benchmark survey. | Clarified metadata to cite World Bank WDI Series `PA.NUS.PRVT.PP` (2024 model extrapolation from ICP 2017/2021). | **CLOSED** |
| **C-07** | **LOW** | `ppp_fx_rates.json`<br>`salary_service.py` | Nominal FX described as "market spot conversion values". | Updated metadata to "Static 2024 Reference Annual Average Exchange Rates". Documented central bank / IMF sources. | **CLOSED** |
| **C-08** | **MEDIUM** | `docs/`<br>`salary_service.py` | Inconsistency between legacy ASHE pipeline (SOC 2010) and salary registry (SOC 2020). | Maintained fail-closed HTTP 503 gate. Formalized crosswalk and governance notes in methodology documentation. | **CLOSED** |

---

## 2. Granular Corrective Action Details

### C-01: Singapore MOM OWS Annualization Factor Correction
- **Problem:** In Sprint 3B.1, Singapore annual wages were calculated as $\text{Monthly Gross} \times 13$, assuming an Annual Wage Supplement (AWS / 13th-month bonus). By MOM statutory definition: *"Monthly Gross Wage includes basic pay, overtime payments, commissions, allowances, and 1/12 of annual variable payment. It EXCLUDES employer CPF contributions, bonuses, and annual wage supplements (AWS)."*
- **Remediation:** 
  - Standardized annualization to $12 \times \text{Monthly Gross Wage}$.
  - Re-computed values across all 6 Singapore occupations:
    - `sal_obs_sg_25121_2023` (Software Developer): Median revised from \$97,500 to **\$90,000 SGD** ($7,500/mo × 12). P25: \$67,200 ($5,600 × 12). P75: \$122,400 ($10,200 × 12). Mean: \$97,200 ($8,100 × 12).
    - `sal_obs_sg_25131_2023` (AI/ML Engineer): Median revised from \$106,600 to **\$98,400 SGD** ($8,200/mo × 12). P25: \$74,400. P75: \$138,000. Mean: \$107,400.
    - `sal_obs_sg_25132_2023` (Data Scientist): Median revised from \$104,000 to **\$96,000 SGD** ($8,000/mo × 12). P25: \$72,000. P75: \$132,000. Mean: \$104,400.
    - `sal_obs_sg_25124_2023` (Cloud Architect): Median revised from \$117,000 to **\$108,000 SGD** ($9,000/mo × 12). P25: \$84,000. P75: \$150,000. Mean: \$117,600.
    - `sal_obs_sg_25125_2023` (DevOps Engineer): Median revised from \$101,400 to **\$93,600 SGD** ($7,800/mo × 12). P25: \$69,600. P75: \$129,600. Mean: \$100,800.
    - `sal_obs_sg_25211_2023` (Cybersecurity Specialist): Median revised from \$102,700 to **\$94,800 SGD** ($7,900/mo × 12). P25: \$70,800. P75: \$132,000. Mean: \$102,600.
  - In `src/backend/data/salary/sources.json`, updated `pay_concept`: `"Gross monthly wage annualized (monthly gross x 12). Excludes employer CPF, bonuses, and Annual Wage Supplement (AWS)."`

### C-02: Singapore MOM OWS Percentile Availability Enforcement
- **Problem:** MOM OWS officially compiles and publishes only P25, Median (P50), and P75. Claimed P10 and P90 figures were synthetic estimates, violating the strict non-fabrication invariant.
- **Remediation:**
  - For all 6 Singapore observations in `src/backend/data/salary/observations.json`, set `p10: null` and `p90: null`.
  - Updated `quality_flag` to `"OFFICIALLY_DERIVED"`.
  - Verified frontend renders `"N/A"` gracefully without displaying `$0` or crashing.

### C-03: Australia ABS EEH Detailed Percentile Provenance
- **Problem:** ABS Cat. 6306.0 publishes weekly ordinary-time earnings percentiles at the 4-digit unit group level. P10 and P90 are not officially published at the detailed 6-digit OSCA level.
- **Remediation:**
  - Set `p10: null` and `p90: null` for all 4 Australian occupations: `AU_OSCA_2024:261313`, `AU_OSCA_2024:224411`, `AU_OSCA_2024:262112`, and `AU_OSCA_2024:261314`.
  - Retained verified P25, P50, and P75 figures ($52 \times \text{weekly ordinary time earnings}$).
  - Updated `quality_flag` to `"OFFICIALLY_DERIVED"` with explicit provenance notes.

### C-04: US BLS OEWS Source Reference Specificity
- **Problem:** In `sources.json`, `source_url` was statically pointed to `oes151252.htm` (Software Developers) for all 7 US occupations.
- **Remediation:**
  - Updated `sources.json` to point to the national parent index: `https://www.bls.gov/oes/current/oes_nat.htm`.
  - Verified and documented detailed individual URLs in the Evidence Matrix (`oes151252.htm`, `oes152051.htm`, `oes151253.htm`, `oes151212.htm`, `oes151242.htm`, `oes151244.htm`, `oes151211.htm`).
  - Documented the 2,080 annual hours convention in methodology and observation notes.

### C-05: Comparability Engine Logic and Branch Ordering Correction
- **Problem:** In `salary_service.py`, `evaluate_comparability()` evaluated `confidence_score < 0.88` before checking for unmapped or very low-confidence comparisons, so `ComparabilityVerdict.NOT_COMPARABLE` was unreachable.
- **Remediation:**
  - Reordered verdict determination logic. Added an explicit early branch:
    ```python
    if relationship_type == "NO_SUPPORTED_MAPPING" or confidence_score < 0.50:
        caveats.append(
            f"Statistical Non-Comparability: Concordance mapping relationship ({relationship_type}) "
            f"or confidence score ({confidence_score:.2f}) does not meet the minimum cross-market comparability threshold (0.50)."
        )
        verdict = ComparabilityVerdict.NOT_COMPARABLE
    ```
  - Added automated unit test in `tests/test_salary_intelligence.py` asserting `NOT_COMPARABLE` is returned when confidence is below 0.50 or unmapped.

### C-06: Purchasing Power Parity (PPP) Metadata Alignment
- **Problem:** References to "ICP 2024 Revision" implied a primary 2024 benchmark survey rather than a model extrapolation. Private consumption PPP factors were not explicitly distinguished from labor cost parities.
- **Remediation:**
  - In `ppp_fx_rates.json`, updated `ppp_description`:
    `"Purchasing Power Parity (PPP) conversion factor for private consumption from World Bank World Development Indicators (Series PA.NUS.PRVT.PP), 2024 observation extrapolated from the latest ICP 2017/2021 benchmark methodology (measured in domestic currency per international dollar). Reflects domestic household consumption cost parity, not occupational labor cost parity."`
  - Updated `ppp_source` strings to cite `World Bank WDI (PA.NUS.PRVT.PP) 2024 Extrapolation`.
  - Updated UI labels and caveat texts in `OccupationsPage.tsx` and `salary_service.py`.

### C-07: Static FX Exchange Rate Metadata
- **Problem:** Nominal foreign exchange rates were described as "market spot conversion values".
- **Remediation:**
  - Updated `fx_description` in `ppp_fx_rates.json` and API payloads to:
    `"Static 2024 Reference Annual Average Exchange Rates to US Dollars (USD). Sourced from central banks and IMF International Financial Statistics (IFS)."`
  - Updated frontend label to `Static 2024 Benchmark FX Conversion`.

### C-08: UK ASHE Classification Consistency & Fail-Closed Gate
- **Problem:** Legacy ingestion script used SOC 2010 while current salary observations use SOC 2020.
- **Remediation:**
  - Maintained absolute enforcement of `require_uk_publication()` (HTTP 503 fail-closed gate).
  - Documented the crosswalk requirements between SOC 2010 Table 15 and SOC 2020 Table 14 in `SPRINT3B1_2_METHODOLOGY_NOTES.md`.

---

## 3. Cryptographic Hashes (Post-Remediation)

| File Path | LF Normalized SHA-256 Hash | Status |
| :--- | :---: | :---: |
| `src/backend/data/salary/sources.json` | `979a8251bf966e300d6b8f59dbcff4216b2144a793dad697bce87a89179d9271` | REMEDIATED |
| `src/backend/data/salary/ppp_fx_rates.json` | `c2d351e280c16585f2302f273d210228224754b243ed6aed3e6d2abb88fdde93` | REMEDIATED |
| `src/backend/data/salary/observations.json` | `50a8c0dbc4c79b7e527f0bbf59ca4fdb19910f35be8fda7243661ba4503db9a4` | REMEDIATED |
| `src/backend/services/salary_service.py` | `9912bdcd517fba63509a3cc0eedf847dd85fc8c1ee91ddff9b7a96e641763931` | REMEDIATED |
| `frontend/src/pages/OccupationsPage.tsx` | `5c2ffb9ebeb963a1c230aece3532ed1c0fcae1dd0d912980706a0666412d3fab` | REMEDIATED |
| `tests/test_salary_intelligence.py` | `8bb3ff5b55905b2a86f0b360043a55fc60ef75660aac8923cb3049d48392355a` | REMEDIATED |
| `src/backend/schemas/salary.py` | `148b58b5afc6384fc03437023280dff685e6d51b7507b992ad3a87844df2b52f` | UNCHANGED |
| `src/backend/routers/salary.py` | `687533418353dc5dd570450de8130a03832e710a3e3dc6488737f00c69f00a8c` | UNCHANGED |
