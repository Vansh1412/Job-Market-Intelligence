# JOBINTEL 2.0 — IMPLEMENTATION RECOMMENDATIONS
## Concrete Architectural Directives & Engineering Roadmaps for Sprint 3B.3.3+

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Principal Systems Architect  
**Target Release Phase:** Sprint 3B.3.3 — Controlled Implementation of Global Employer Intelligence MVP  

---

## 1. SUMMARY OF IMPLEMENTATION DIRECTIVES

To implement the **Prediction Realism & Evidence Integrity Standard** during Sprint 3B.3.3 without destabilizing existing machine learning models or altering valid empirical metrics, the following six architectural directives must be executed:

```
+----------------------------------------------------------------------------------------------------+
| SPRINT 3B.3.3 ARCHITECTURAL ROADMAP                                                                |
+----+--------------------------------+-------------------------------------+------------------------+
| #  | Engineering Area               | Mandated Technical Implementation   | Core Benefit           |
+----+--------------------------------+-------------------------------------+------------------------+
| 1  | Frontend Formatting            | Rounding & Prediction Interval Band | Eliminates false prec. |
| 2  | API Contract Discipline        | Mandatory limit/offset pagination   | Prevents Render OOM    |
| 3  | Backend Schema Generalization  | Multi-market IDs & Dual Headcount   | Global compatibility   |
| 4  | Confidence Score Calibration   | Temperature scaling (T=1.24)        | ECE <= 0.05 compliance |
| 5  | Dual Ledger Provenance         | Tier 1 (Source) + Tier 2 (Record)   | Complete audit trail   |
| 6  | UK Demand Governance           | Null serialization w/ active gate   | Zero data leakage      |
+----+--------------------------------+-------------------------------------+------------------------+
```

---

## 2. DETAILED ENGINEERING ACTION PLANS

### 2.1 Directive 1: Frontend Presentation Formatting
- **Implementation:** Create a shared utility module `frontend/src/utils/formatters.ts`:
  - `formatSalaryEstimate(val, currency)`: Rounds INR to 1 decimal place (`₹12.5 LPA`) and USD to nearest thousand (`$142,000`).
  - `formatPredictionInterval(val, p25_res, p75_res)`: Computes and displays the illustrative empirical range.
  - `formatConfidenceTier(conf)`: Translates raw numeric scores into standardized qualitative badges (**Verified Official**, **High Confidence**, **Moderate Confidence**).
- **Rule:** Never round underlying API responses or raw numbers stored in React state. Apply rounding strictly at the JSX rendering boundary.

### 2.2 Directive 2: API Contract Pagination on Render Free Tier
- **Implementation:** On the new employer directory endpoint `GET /api/v1/employers`:
  - Enforce query parameters: `limit: int = Query(25, ge=1, le=100)` and `offset: int = Query(0, ge=0)`.
  - Return standardized envelope: `{ "items": [...], "total": int, "limit": int, "offset": int }`.
  - **Benefit:** Guarantees that response serialization payloads on Render Free never exceed ~35 KB per request, eliminating heap spikes.

### 2.3 Directive 3: Generalized Multi-Market Employer Schemas
- **Implementation:** Upgrade `src/backend/schemas/employer.py`:
  - Deprecate India-centric `company_category` Enum.
  - Add sovereign registration fields: `registration_identifier: str`, `registration_identifier_type: str` (ABN, CIK, CRN, UEN, CIN, AGENCY_CODE).
  - Add native dual headcount fields: `headcount_band: Optional[str] = None` and `observed_count: Optional[float] = None`.
  - Add hierarchical links: `parent_company_id: Optional[str] = None`.

### 2.4 Directive 4: Temperature Scaling Calibration for Taxonomy Mapping
- **Implementation:** In `src/backend/utils/taxonomy_mapper.py`:
  - Integrate post-hoc temperature scaling ($T = 1.24$):
    $$\text{calibrated\_confidence} = \frac{1}{1 + \exp\left(-\frac{\text{logit}(\text{raw\_score})}{1.24}\right)}$$
  - Expose both `raw_similarity_score` and `calibrated_confidence` in backend responses, driving Expected Calibration Error below 0.05.

### 2.5 Directive 5: Dual-Tier Cryptographic Evidence Ledger
- **Implementation:**
  - **Tier 1 (Source Document Ledger):** Retain current SHA-256 hashes of bulk government downloads and statutory filing documents in `employer_evidence_ledger.csv`.
  - **Tier 2 (Entity Record Ledger):** Compute deterministic SHA-256 hashes of normalized canonical JSON payloads for every individual profile (`employer_id`). Display this record hash inside the user-facing Provenance Drawer.

### 2.6 Directive 6: Preservation of UK Demand Publication Gate
- **Implementation:**
  - Verify that `src/backend/routers/` endpoints serialize UK demand vacancy flow as `null` with `publication_gate_active: true`.
  - Render the mandatory warning pill: *"UK vacancy flow data withheld pending source-use review."*
