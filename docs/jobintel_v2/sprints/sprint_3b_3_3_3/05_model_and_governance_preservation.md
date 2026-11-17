# JOBINTEL 2.0 — SPRINT 3B.3.3.3
## DOCUMENT 05: MODEL AND GOVERNANCE PRESERVATION AUDIT

**Sprint:** 3B.3.3.3 — Critical Employer Resolver Remediation & Salary Contract Correction  
**Verification Scope:** Frozen Binary Models, Golden Predictions Parity & Sovereign Publication Gates  
**Status:** 100% BITWISE INTACT & GOVERNANCE COMPLIANT  

---

### 1. Bitwise Verification of Frozen Model Artifacts

All 20 model artifacts across USA Phase 4/5 and India pipelines were verified using SHA-256 digests. Zero model files have been modified, retrained, or altered:

| Model File | SHA-256 Digest | Status |
| :--- | :--- | :--- |
| `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | **UNMODIFIED** |
| `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | **UNMODIFIED** |
| `models/phase5/feature_metadata.json` | `c4b72be3d4f2bd6a64c132cf23a5b5f6133c7ad0ff9bbf3ea40a8260f011abdb` | **UNMODIFIED** |
| `models/phase5/model_metrics.json` | `9d777fa4bb663543d62776df48d547765e83ac4ca2f32d8b3ce38aec2945bc18` | **UNMODIFIED** |
| `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | **UNMODIFIED** |
| `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | **UNMODIFIED** |
| `models/india/final_feature_list.json` | `9085e3a0d95fc555e8b6bf4e31e4f86e1e97326ac51648164e723f9169b38d95` | **UNMODIFIED** |
| `models/india/final_evaluation.json` | `04552f31c8694223a7895a10ce195acf5629ec772fa7da68628a5b0afea7658b` | **UNMODIFIED** |
| `models/india/final_model_metadata.json` | `077a4c291d76d9332affe63d089e06023b31376ea24b39171d2e63934f76219f` | **UNMODIFIED** |
| `models/india/india_archetype_metadata.json` | `7d49f6a00c5018b1ab2d46dbbdb1648e09e1e4d785edfd599bc9b74b7d2abd99` | **UNMODIFIED** |
| `models/india/india_holdout_archetype_pipeline.pkl` | `efce615d239ca0198605bdee3468b1709c281242af0b49a38df311d3e272df6b` | **UNMODIFIED** |
| `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | **UNMODIFIED** |
| `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | **UNMODIFIED** |
| `models/india/experiment_registry.json` | `42d1d28344e930e0706f7e0cf0f9721f893330bec0529badb92d5ca8116224a4` | **UNMODIFIED** |
| `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | **UNMODIFIED** |
| `models/kmeans_phase4_k7.pkl` | `7716419c8b26eae903464d118137726294ad55084d90f83843b6264deab4b047` | **UNMODIFIED** |
| `models/pca_phase4.pkl` | `2995dfb11134ae9381f9e8c893ddfaea070ebfc1691287d6d883d12484f44a4a` | **UNMODIFIED** |
| `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | **UNMODIFIED** |
| `models/scaler_phase4.pkl` | `11067c5a83090ef2e96f2e75a279b2bf6dfee0c7b9a1f97cd7ef71005f9826ef` | **UNMODIFIED** |
| `models/scaler_phase4_1.pkl` | `2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c` | **UNMODIFIED** |

---

### 2. Golden Predictions Deterministic Parity

The automated test suite `tests/test_golden_predictions.py` executed with 100% pass rate:
- **USA Golden 01 (Senior ML Engineer in SF):**
  - Direct on-disk XGBoost model inference: `$256,960.28`
  - Live FastAPI endpoint (`POST /api/usa/predict`): `$256,960.28`
  - Delta: `$0.00` (Parity tolerance $< \$0.10$)
  - Archetype assigned: `SYS_ENG`
- **India Golden 01 (Lead Python / AI in Bangalore):**
  - Direct on-disk HistGradientBoosting model inference: `16.62 LPA` (`₹1,662,308`)
  - Live FastAPI endpoint (`POST /api/india/predict`): `16.62 LPA` (`₹1,662,308`)
  - Delta: `0.00 LPA` (Parity tolerance $< 0.05\text{ LPA}$)
  - Archetype assigned: `IND_ARC_03`

---

### 3. Sovereign Publication Gates

Both UK publication gates were verified active, defensive, and uncompromised:

1. **UK Salary Intelligence Gate:**
   - Endpoint: `GET /api/v1/markets/UK/salary/occupations`
   - Response Status: **`HTTP 503 Service Unavailable`**
   - Error Body:
     ```json
     {
       "detail": {
         "code": "UK_DATA_NOT_PUBLISHED",
         "message": "UK salary analytics are not currently published."
       }
     }
     ```
   - Logged Security Audit: `UK Salary Governance Gate denied request: code=GOV_DENIED_UNREVIEWED_SOURCE, status=REVIEW_REQUIRED`.

2. **UK Demand Intelligence Gate:**
   - Endpoint: `GET /v1/demand/occupations/2134?market=UK`
   - Response Status: **`HTTP 200 OK`**
   - Gate Payload:
     ```json
     {
       "primary_metric_value": null,
       "trend_percentage_change": null,
       "publication_gate_active": true,
       "publication_gate_code": "UK_DEMAND_DATA_NOT_PUBLISHED",
       "publication_gate_message": "UK demand data is currently withheld pending source-use and redistribution review."
     }
     ```
   - Redaction Guarantee: Absolute metric values are masked to `null` while public methodology disclaimers and source attributions are preserved.
