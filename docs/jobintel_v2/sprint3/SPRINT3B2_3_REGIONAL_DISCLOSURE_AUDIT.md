# JOBINTEL 2.0 — SPRINT 3B.2.3 REGIONAL & OCCUPATIONAL DISCLOSURE AUDIT
## Derived Geographic Breakdown Audit, Inheritance Lineage & Multi-Market Consistency

**Audit Date:** November 16, 2026  
**Auditor:** Independent Labour Market Statistics Specialist & Frontend QA Auditor  
**Audit Scope:** Independent inspection of `src/backend/data/demand/observations.json`, `src/backend/schemas/demand.py`, `src/backend/services/demand_service.py`, and `frontend/src/pages/DemandPage.tsx`.

---

### 1. AUDIT OBJECTIVE

National statistical agencies frequently collect occupational data at national or high-level occupational group levels. Sub-national distributions or granular occupational specializations often require computational allocation, proxy modeling, or taxonomic inheritance.

This audit evaluated whether:
1. Derived state/regional distributions are clearly differentiated from directly observed local census counts.
2. 6-digit detailed occupations inheriting 4-digit unit group numbers disclose this inheritance.
3. Modelled proxies (such as Singapore planning areas) carry mandatory user warnings.
4. Cross-market semantic consistency is maintained without false equivalence.

---

### 2. UNITED STATES: OEWS EMPLOYMENT WEIGHT ALLOCATION

#### Underlying Methodology & Lineage:
- **National Metric:** US Bureau of Labor Statistics (BLS) Table 1.7 Occupational Projections (2023–2033), measuring 10-year annualized projected openings ($\text{Growth} + \text{Replacement Needs}$).
- **State Allocation Method:** BLS does not publish monthly state-level job vacancy counts by 6-digit SOC in the EP series. Sub-national distributions are computed using state employment proportions from the Occupational Employment and Wage Statistics (OEWS):
  $$\text{State Openings} = \text{National Openings} \times \left( \frac{\text{OEWS State Employment}}{\text{OEWS National Employment}} \right)$$
- **Backend Schema Verification:**
  - In `src/backend/schemas/demand.py`, every US `RegionalDemandPoint` has `is_derived = True`, `derivation_method = "OEWS_STATE_EMPLOYMENT_WEIGHTS"`, and `disclosure_label = "Derived state allocation"`.
  - In `src/backend/services/demand_service.py`, the profile attaches `regional_disclosure`:
    > *"State-level values are derived allocations using employment weights. They are not independently observed state-level job-opening counts."*
- **Frontend Presentation:**
  - Verified live in `DemandPage.tsx` (lines 903–918) displaying a blue informational badge directly above the geographic breakdown chart.

---

### 3. AUSTRALIA: 4-DIGIT ANZSCO GROUP INHERITANCE

#### Underlying Methodology & Lineage:
- **Source Metric:** Jobs and Skills Australia (JSA) Internet Vacancy Index (IVI), measuring monthly online job advertisements.
- **Classification Inheritance:** JSA publishes the IVI series primarily at the 4-digit ANZSCO unit group level (e.g., ANZSCO 2613 *Software and Applications Programmers*). When mapped to 6-digit OSCA 2024 / ANZSCO detailed titles (e.g., 261313 *Software Engineer* or 261314 *Software Tester*), values represent the broader unit group scaled to the occupation.
- **Backend Schema Verification:**
  - `src/backend/schemas/demand.py` defines `occupation_inheritance_disclosure: str | None`.
  - `src/backend/services/demand_service.py` attaches:
    > *"Detailed occupation values are derived from broader four-digit ANZSCO group data. They should not be interpreted as directly observed six-digit occupation counts."*
- **Frontend Presentation:**
  - Verified in `DemandPage.tsx` (lines 919–934) displaying an amber warning alert above the regional breakdown.

---

### 4. SINGAPORE: PLANNING-AREA PROXIES

#### Underlying Methodology & Lineage:
- **Source Metric:** Ministry of Manpower (MOM) Job Vacancy Report, measuring establishment-level unfilled job openings across private firms (25+ employees) and the public sector.
- **Regional Modeling:** MOM collects vacancy data at national establishment level; official sub-national geographic vacancy stats do not exist. JobIntel calculates sub-national shares using enterprise cluster proxies across Singapore planning areas (Central/CBD, West/Jurong Innovation, East/Changi, North).
- **Backend Schema Verification:**
  - Every Singapore regional point has `is_derived = True`, `derivation_method = "PLANNING_AREA_PROXIES"`, and `disclosure_label = "Modelled regional distribution"`.
  - `src/backend/services/demand_service.py` attaches:
    > *"MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED. Sub-national shares are planning area proxies derived from enterprise cluster estimates."*
- **Frontend Presentation:**
  - Verified in `DemandPage.tsx` displaying the uppercase warning banner, preventing any user from citing planning-area shares as official MOM figures.

---

### 5. CROSS-MARKET CONSISTENCY MATRIX

| Evaluation Criterion | United States (BLS) | Australia (JSA) | Singapore (MOM) | India (JobIntel) | Audit Assessment |
|---|---|---|---|---|---|
| **Derived Flag (`is_derived`)** | `True` for all states | `True` for all states | `True` for all regions | `True` for all hubs | **Consistent** |
| **Derivation Method Field** | `OEWS_STATE_EMPLOYMENT_WEIGHTS` | `JSA_IVI_STATE_SHARES` | `PLANNING_AREA_PROXIES` | `TECH_HUB_POSTINGS_SHARE` | **Explicit & Traceable** |
| **Visible UI Derivation Alert** | Present (Blue notice) | Present (Amber warning) | Present (Amber warning) | Present (Amber warning) | **Verified Live** |
| **National Construct Distinctness** | Annual Projected Openings | Monthly Advert Volume | Establishment Vacancies | Empirical Postings Sample | **Preserved (Non-collapsed)** |

---

### 6. AUDIT VERDICT

```text
REGIONAL DISCLOSURE AUDIT VERDICT: VERIFIED CLOSED
Status: PASS
US OEWS Allocation Notice: Verified across API and UI.
AU ANZSCO Inheritance Warning: Verified across API and UI.
SG Modelled Proxy Warning: Verified across API and UI.
Cross-Market Integrity: 100% compliant with statistical non-collapsibility rules.
```
