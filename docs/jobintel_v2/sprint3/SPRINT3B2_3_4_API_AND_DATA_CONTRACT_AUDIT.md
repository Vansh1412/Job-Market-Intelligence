# JOBINTEL 2.0 — SPRINT 3B.2.3.4
## FUNCTIONAL API AND DATA CONTRACT AUDIT REPORT

**Audit Date:** 2026-11-16  
**Audited Branch:** `staging/sprint2c3`  
**Committed Staging HEAD SHA:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  
**Execution Mode:** Strictly READ-ONLY Contract Verification

---

## 1. EXECUTIVE SUMMARY

This audit independently verified the functional behavior, API response contracts, serialization fidelity, and data governance guarantees of the Global Job Demand Intelligence module at committed HEAD `d1a8b027d10031b3568a3141f639e2f40a49be18`.

All verification checks passed with 100% compliance:
- **UK Publication Gate:** Withheld values serialize as explicit JSON `null` (not `0.0`), with `publication_gate_active=True` and reason code `UK_DEMAND_DATA_NOT_PUBLISHED`. Zero volume leakage across all UK routes.
- **Qualitative Shortage Independence:** The UK shortage indicators from `uk.gov.shortage` operate under Open Government Licence v3.0 (OGL v3.0 / Crown Copyright) and remain published and accessible independently from withheld volume metrics.
- **Data Provenance:** Exactly 25 observations are `OFFICIALLY_DERIVED` from national statistical agencies, and 3 are `JOBINTEL_CURATED` benchmark estimates.
- **Disclosure Hardening:** Regional and benchmark disclosures are present across all national profiles.
- **Skill Gap Formula:** Fully transparent mathematical explanation: `Skill Coverage (%) = (Matched Skill Weight / Total Required Skill Weight) * 100`, explicitly disclaiming employability probability.

**Verdict:** `PASS — ALL CONTRACTS FULLY VERIFIED`

---

## 2. UK PUBLICATION GATE & SERIALIZATION INTEGRITY

### A. List Endpoint Sanitization (`/v1/demand/occupations?market=UK`)
- **Status:** HTTP 200 OK
- **Occupations Returned:** 8 canonical profiles.
- **Sanitization Check:**
  - `value`: `None` (JSON `null`) for all 8 occupations.
  - `time_series`: Empty array `[]` (zero historical volume leakage).
  - `regional_breakdown`: Empty array `[]` (zero regional volume leakage).
  - `notes`: Contains mandatory warning flag `UK_DEMAND_DATA_NOT_PUBLISHED`.

### B. Occupation Detail Gate & JSON Raw Null Serialization (`/v1/demand/occupations/2134?market=UK`)
- **Status:** HTTP 200 OK
- **Payload Verification:**
  ```json
  {
    "market_id": "UK",
    "occupation_id": "2134",
    "publication_gate_active": true,
    "publication_gate_code": "UK_DEMAND_DATA_NOT_PUBLISHED",
    "primary_metric_value": null,
    "trend_time_series": [],
    "regional_distribution": []
  }
  ```
- **Raw Wire Check:** Evaluated raw response byte stream; verified `"primary_metric_value": null` is emitted on the wire. No numeric `0.0` or integer `0` is conflated with the withheld status.

### C. Cross-Market Comparison Sanitization (`/v1/demand/compare`)
- **Query:** `canonical_id=CAN_OCC_SOFTWARE_ENGINEER&market_a=US&market_b=UK`
- **Verdict:** `METHODOLOGICALLY_DISTINCT`
- **Metric A (US):** Fully populated with active BLS volume index.
- **Metric B (UK):** `value = null`, `publication_gate_active = true`.
- **Methodological Warnings:** Injected warnings explicitly alert user that UK demand volume metrics are withheld pending licensing clearance.

---

## 3. QUALITATIVE SHORTAGE INDEPENDENCE

The audit verified that qualitative shortage indicators for the United Kingdom remain functional and authoritative despite quantitative volume withholding:
- **Source ID:** `uk.gov.shortage`
- **Source Name:** `UK Immigration Salary List & Shortage Indicators`
- **Publisher:** `UK Home Office / Migration Advisory Committee / Skills England`
- **Legal License:** `Open Government Licence v3.0 (OGL v3.0)` (Crown Copyright)
- **Publication Status:** `PUBLISHED`
- **Independence:** The shortage status (`NATIONAL_SHORTAGE`) is derived from official governmental gazettes, completely decoupled from withheld quantitative posting metrics.

---

## 4. DATA PROVENANCE AND TAXONOMY HARMONIZATION

The demand intelligence system integrates 28 atomic observations across 5 global markets:

| Market | National Taxonomy | Total Observations | Provenance Category | Primary Source Agency |
| :--- | :--- | :--- | :--- | :--- |
| **United States** | SOC 2018 | 6 | `OFFICIALLY_DERIVED` | US Bureau of Labor Statistics (BLS) |
| **Australia** | ANZSCO 2022 | 6 | `OFFICIALLY_DERIVED` | Jobs and Skills Australia (JSA) |
| **Singapore** | SSOC 2020 | 5 | `OFFICIALLY_DERIVED` | Ministry of Manpower (MOM) |
| **United Kingdom** | SOC 2020 | 8 | `OFFICIALLY_DERIVED` (Withheld) | UK ONS / Shortage Gazettes |
| **India** | NCO-2015 | 3 | `JOBINTEL_CURATED` | JobIntel Research Benchmark |
| **Total** | | **28** | **25 Official / 3 Curated** | |

### Classification Integrity
- Zero taxonomy conflation: Each market queries strictly within its native classification system.
- Cross-market comparability maps through canonical role archetypes (`CAN_OCC_*`) with explicit comparability warnings regarding survey methodologies (vacancies vs. openings vs. online job ads).

---

## 5. STATISTICAL DISCLOSURE & REGIONAL MODELING

All national occupation profiles contain required contextual caveats:
1. **United States:** `derived allocations using employment weights ... not independently observed`
2. **Singapore:** `MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED`
3. **Australia:** `broader four-digit ANZSCO unit group inheritance`
4. **India:** `not an official MoSPI national vacancy census ... JobIntel research benchmark`

---

## 6. SKILL GAP ANALYTICS CONTRACT

The `/v1/demand/skills/gap-analysis` endpoint was evaluated with sample candidate skills `["Python", "SQL", "Git", "Docker"]` against Software Developers (`15-1252`):
- **Calculated Match Score:** `31.2%`
- **Mathematical Formula:** `Skill Coverage (%) = (Matched Skill Weight / Total Required Skill Weight) * 100`
- **Methodology Disclosure:** *"Skill coverage measures alignment between candidate skills and employer-requested competencies for the occupation. It is not an employability probability, hiring probability, or placement guarantee."*
- **Actionable Guidance:** Rule-based skill acquisition recommendations prioritized by occupational importance weight.

---

## 7. AUDIT CONCLUSION

The API contracts, data representations, serialization rules, and legal disclosures across the Global Job Demand module comply with academic research standards and regulatory publishing ethics.

**Audit Status:** `PASS`
