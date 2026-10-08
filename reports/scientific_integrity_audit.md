# JobIntel Phase 8 Remediation: Scientific Integrity Audit

**Date:** 2026-10-08  
**Auditor:** ML Systems Auditor & QA Lead  
**Scope:** Repository-wide audit of analytical calculations, constants, and data flows.  

---

## 1. Audit Framework & Classification Scheme

Every analytical number, percentage, currency figure, and statistical metric across the codebase has been audited and classified into one of five rigorous scientific categories:

- **Category A: Legitimate UI / Design Constants** (e.g. layout dimensions, CSS hex colors, Framer Motion transition durations, UI grid break-points).
- **Category B: Frozen Certified Research Metrics** (e.g. certified holdout test MAE, certified dataset sample sizes $N=34,036$ and $N=5,859$, certified $R^2$ scores, feature counts 123 and 290 in research documentation, metadata endpoints, and test assertions).
- **Category C: Empirical Analytical Computations** (e.g. live pandas/parquet groupings, dynamic median calculations, IQR intervals, percentile transforms, real-time feature matrix construction).
- **Category D: Architectural Configuration** (e.g. API base URLs, CORS allowed origins, route maps, HTTP timeouts, validation constraints).
- **Category E: Invalid Fabricated Analytical Values** (e.g. mock analytical percentages, fake hardcoded skill prevalences, invented role shares, static salary steps).

**Policy:** All Category E artifacts must be completely eradicated from active production paths.

---

## 2. Findings & Classification Matrix

| File / Component | Code Symbol / Value | Audit Classification | Remediation Status |
| :--- | :--- | :--- | :--- |
| `src/backend/services/market_service.py` | `shared_skills_tracking` (previously hardcoded Python=39.4%, etc.) | **Category E** | **REMEDIATED**: Replaced with dynamic aggregation from `modeling_dataset.parquet` and `india_modeling_cohort.parquet`. |
| `src/backend/services/market_service.py` | `role_demand_comparison` (previously hardcoded role shares) | **Category E** | **REMEDIATED**: Replaced with empirical role distribution calculation across certified parquets. |
| `src/backend/routers/skills.py` | `get_skill_detail` (schema mismatch producing 0% demand and +$0 delta) | **Category E** | **REMEDIATED**: Standardized canonical contract returning real empirical prevalence and salary delta. |
| `src/backend/services/market_service.py` | `EXCLUDED_CORPUS_SKILLS = {"skill_salesforce"}` | **Category D** | **VERIFIED & DOCUMENTED**: Documented as Taxonomy D artifact exclusion filter with zero data fabrication. |
| `src/backend/main.py` | `GET /api/meta` cohort metrics ($N=34,036$, $N=5,859$, MAE=$36,380.64$, etc.) | **Category B** | **VERIFIED**: Frozen certified empirical metrics from Phase 5 & 6 evaluation runs. Unchanged. |
| `src/backend/services/usa_service.py` | 123 feature vector assembly | **Category C** | **VERIFIED**: Strict mathematical feature pipeline adhering to frozen preprocessor. |
| `src/backend/services/india_service.py` | 290 feature matrix assembly | **Category C** | **VERIFIED**: Strict mathematical feature pipeline adhering to frozen preprocessor. |
| `frontend/src/utils/motionTokens.ts` | Animation spring / tween timing parameters (0.2s - 0.45s) | **Category A** | **VERIFIED**: Motion tokens standardized with hidden/visible contracts. |
| `frontend/src/context/MarketContext.tsx` | Currency symbols (`$`, `₹`), scales (`USD`, `LPA`) | **Category D** | **VERIFIED**: Architectural configuration for market isolation. |
| `tests/golden_predictions_manifest.json`| 6 certified golden profile prediction values | **Category B** | **VERIFIED**: Certified golden parity benchmarks. Bitwise verified. |

---

## 3. Strict Market Isolation Verification

Scientific integrity demands that the USA and Indian tech job markets are independently modeled and analyzed:
1. **Zero Currency Conversions:** No foreign exchange multiplier (e.g. USD/INR spot rate) is applied at any point in the pipeline. USA salaries are evaluated exclusively in USD ($) and Indian salaries in Lakhs Per Annum (₹ LPA).
2. **Model Isolation:**
   - USA predictions execute strictly against `models/phase5/best_model.pkl` (123 features, XGBoost architecture).
   - India predictions execute strictly against `models/india/final_model.pkl` (290 features, HistGradientBoosting architecture).
   - Cross-market API endpoints present side-by-side empirical distributions with explicit academic disclaimers.
3. **No Synthetic Step Functions:** In `test_skill_integrity.py::test_no_synthetic_step_function`, automated statistical tests assert that salary spreads across skills exhibit natural observational variance without synthetic discretization.

---

## 4. Frozen Artifact Hash Verification

Hashes re-verified after remediation:
- USA Model (`models/phase5/best_model.pkl`): `55c1b7fd87d2a04c...` (MATCH)
- India Model (`models/india/final_model.pkl`): `7a3490d7a36a128e...` (MATCH)
- USA Parquet (`data/processed/modeling_dataset.parquet`): `68895e3823cca91f...` (MATCH)
- India Parquet (`data/processed/india/india_modeling_cohort.parquet`): `d4e32be45d84b159...` (MATCH)

**Scientific Integrity Verdict: 100% PASS** (Zero fabricated analytical values in active product paths).
