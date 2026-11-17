# SPRINT 3B.3.3: SCOPE & CONTRACT INVENTORY
## Affected Components, API Schemas, Thresholds & Change Matrix

**Sprint ID:** 3B.3.3  
**Target Branch:** `staging/sprint2c3`  
**Current Baseline:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  

---

## 1. Change Matrix

| Work Package | Current Behavior | Proposed Behavior | Affected Files | API Impact | Risk Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **WP-01** (Salary Presentation) | Prediction returns point estimate and mislabeled `confidence_interval` dictionary. Frontend displays point estimate without explicit evaluation sample size $N$ or base vs CTC distinction. | Preserve existing prediction return fields; add rich evaluation metadata (`evaluation_sample_size`, `pay_concept`, `disclaimer`). Frontend prominently displays point estimate, market-specific pay concept, holdout MAE/R², and non-guarantee caveat. | `src/backend/services/india_service.py`<br>`src/backend/services/usa_service.py`<br>`frontend/src/pages/PredictorPage.tsx` | Backward-compatible addition of optional metadata fields in response payload. | LOW |
| **WP-02** (Occupation Mapping) | Concordance score displayed as `{x}% EXPERT HEURISTIC`. Empty search results silently fall back to all occupations. | Concordance score displayed as `Match Index: {x}/100` with non-probability disclaimer. Zero-match search displays explicit unmapped title card explaining safe fallback. | `frontend/src/pages/OccupationsPage.tsx` | None (Frontend UI enhancement only). | LOW |
| **WP-03** (Employer Entity Resolution) | Entity registry provides basic list/get by ID; no explicit candidate matching or subsidiary-collapse protection. | Add structured candidate resolver distinguishing exact identifier match, strong match, ambiguous match, and no match. Explicitly block automatic subsidiary-into-parent collapsing. Expose `/api/v1/employers/resolve`. | `src/backend/schemas/employer.py`<br>`src/backend/employers/resolver.py`<br>`src/backend/routers/v1.py` | Add new endpoint `/api/v1/employers/resolve`. Existing `/api/v1/employers` preserved. | LOW |
| **WP-04** (Skill Extraction Disclosure) | Skill page displays prevalence percentage without explicit posting sample size badge. | Display explicit posting sample size badge ($N$), clarify that skills represent job ad requirements (not employee competence), and disclose benchmark evaluation bounds. | `frontend/src/pages/SkillsPage.tsx` | None (Frontend UI enhancement only). | LOW |
| **WP-05** (Demand Semantics) | Gated UK demand vacancy values returned as `null` with `UK_DEMAND_DATA_NOT_PUBLISHED` code. | Preserve existing behavior exactly. Ensure no conversion of null to zero or misleading global demand score. | `src/backend/routers/demand.py`<br>`frontend/src/pages/DemandPage.tsx` | None (Preservation verified). | LOW |
| **WP-06** (API Pagination) | `GET /v1/employers` returns full list without pagination parameters. | Add optional `limit` (1–50) and `offset` (ge=0) query parameters. Calling without params returns full list, maintaining 100% backward compatibility. | `src/backend/routers/v1.py` | Fully backward compatible. | LOW |

---

## 2. Threshold Semantics Documentation

In accordance with Sprint 3B.3.3 instructions, all numerical thresholds in the codebase are documented with their precise semantics:

1. **Threshold 0.60 (Occupation Fallback Threshold):**
   - *Current Implementation:* In `SYS_OCC_MAPPER`, when token Jaccard or Levenshtein similarity between a raw title and canonical titles falls below 0.60, the mapping is rejected and routed to `Other / Unmapped`.
   - *Semantics:* A conservative heuristic boundary preventing low-similarity matches from polluting canonical buckets. It is **not** a calibrated statistical probability.
2. **Threshold 0.85 (Entity Resolver Ambiguity Threshold):**
   - *Current Implementation:* In candidate entity name matching, normalized Levenshtein / Jaro-Winkler similarity between 0.85 and 0.98 without matching statutory IDs triggers `AMBIGUOUS_CANDIDATE`.
   - *Semantics:* Flags potential aliases, misspellings, or subsidiary entities for manual review. Never triggers automatic merging.
3. **Threshold 0.95 (Occupation High-Confidence Heuristic Tier):**
   - *Current Implementation:* Matches with similarity $\ge 0.95$ are assigned high expert concordance rating.
   - *Semantics:* Indicates strong lexical or classification concordance. Under `JOBINTEL-STD-PRED-001`, this must be rendered as `Match Index: 95/100` and must **not** be presented as a "95% probability of correctness."

---

## 3. Backward Compatibility Verification Plan

Every proposed change has been checked against existing automated tests:
- `test_golden_predictions.py`: Verifies `predicted_salary` (USA) and `predicted_salary_lpa` (India). These exact keys and numerical values remain unchanged.
- `test_prediction_parity.py`: Verifies parity between direct model execution and API execution down to $0.05. Model execution logic is untouched.
- `test_global_foundation.py`: Verifies `list_employers() == []` and schema routes. Optional pagination preserves empty list return when unparameterized.
- Frontend vitest suite (`calculator.test.ts`, `demand_contract.test.ts`, `routing.test.ts`, `skills_contract.test.ts`): All test payloads remain 100% valid.
