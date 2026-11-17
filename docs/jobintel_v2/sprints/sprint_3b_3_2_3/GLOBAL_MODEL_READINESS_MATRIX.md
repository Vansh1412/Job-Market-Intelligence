# GLOBAL MODEL READINESS MATRIX
## Granular Component-by-Component Production Readiness Assessment

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- Model Inventory: `models/`
- Readiness Records: `docs/jobintel_v2/sprints/sprint_3b_3_2_2/model_readiness.csv`
- Reconciled Data: `docs/jobintel_v2/sprints/sprint_3b_3_2_3/model_readiness_matrix.csv`
- Governance Standard: `JOBINTEL-STD-PRED-001`

---

## 1. Governance Policy on Readiness

In compliance with `JOBINTEL-STD-PRED-001`, JOBINTEL strictly rejects binary "platform-wide blanket approvals." A platform containing supervised regression, unsupervised clustering, deterministic entity resolvers, and regulatory data pipelines must evaluate each component on its own empirical merits.

Every model and algorithmic system receives an independent readiness classification based on:
1. **Verification Status:** Reproducibility of offline metrics on persistent artifacts.
2. **Boundary Safety:** Enforcement of domain constraints and fallback behaviors.
3. **Display Integrity:** Implementation of required caveats, intervals, and disclaimers.

---

## 2. Granular Readiness Matrix

| Component ID | System Type | Readiness Tier | Verified Metric | Primary Intended Use | Strictly Prohibited Use | Required UI Disclosure |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`MOD_IN_SALARY_HGBR`** | Supervised Regression | **CONDITIONAL GO** | Holdout MAE ₹3.71 LPA, $R^2 = 0.5798$ ($N=1,173$) | Benchmark tech compensation estimation in India. | Guaranteed salary offers; non-tech role extrapolation. | *"Estimated compensation range based on verified Indian tech postings. Actual offers vary by employer scale and candidate skills."* |
| **`MOD_US_SALARY_XGB`** | Supervised Regression | **CONDITIONAL GO** | Test MAE $36,380, $R^2 = 0.4233$ ($N=6,808$) | Benchmark base salary estimation in US tech hubs. | Total comp (equity/bonus) estimation; contract quotes. | *"Base salary estimate derived from public job requisitions. Equity, bonuses, and benefits are not modeled."* |
| **`MOD_IN_ARCHETYPE_KM`** / **`MOD_US_ARCHETYPE_KM`** | Unsupervised Clustering | **GO** | Silhouette 0.38 / 0.41 ($k=7$) | Descriptive grouping into 7 skill-affinity archetypes. | Career match guarantees; predictive hiring scoring. | *"Archetypes reflect observed statistical clusters of skill co-occurrences in the labour market."* |
| **`SYS_OCC_MAPPER`** | Deterministic Mapping | **GO** | 97.0% pop. accuracy, 0.0% misclass ($N=100$) | Mapping titles to 12 canonical SOC categories. | Probabilistic certainty claims without calibration disclaimers. | *"Standardized canonical mapping. Non-standard titles route to 'Other / Unmapped' review."* |
| **`SYS_EMP_RESOLVER_V2`**| Hybrid Deterministic | **CONDITIONAL GO** | Precision 100%, 0 false merges ($N=55$ neg) | Pairwise deduplication against statutory registries. | Cross-market automated parent-subsidiary collapsing. | *"Matches verified against statutory corporate registries. Cross-border domain overlaps route to manual review."* |
| **`SYS_SKILL_EXTRACTOR`**| Context-Guarded NLP | **CONDITIONAL GO** | 100% on 20 adversarial edge cases | Extracting skills from active tech postings. | Staff competency audits; uncalibrated single-letter token extraction. | *"Skill frequencies reflect specifications in verified job postings (Sample size N displayed)."* |
| **`SYS_DEMAND_INTEL`** | Descriptive Aggregator | **CONDITIONAL GO** | 100% statutory lineage on IN/US/SG/AU | Aggregating statutory workforce size and vacancies. | Predictive headcount forecasting; unverified UK vacancy publication. | *"Statutory disclosures represent establishment workforce. Open requisitions reflect advertised vacancy flow, not confirmed hires."* |

---

## 3. Operational Prerequisites for Moving CONDITIONAL GO to FULL GO

To advance components from `CONDITIONAL GO` to unconditional `FULL GO` prior to production release:

1. **Frontend Display Gate:**
   - Verify that all salary widgets display proportional intervals $[\hat{y} \times 0.84, \hat{y} \times 1.16]$ rather than solitary point values.
   - Verify that the mandatory caveats specified in Section 2 are rendered adjacent to every metric.
2. **Sample Size Badges ($N$):**
   - Verify that skill demand frequency widgets render the exact count of analyzed postings ($N = \dots$) in the component footer.
3. **Pagination on Entity Endpoints:**
   - Verify that employer listing and search endpoints enforce strict pagination (`default=25`, `max=50`) to eliminate Render Free tier OOM vulnerabilities.
4. **Maintenance of UK Gating:**
   - Confirm that UK demand vacancy flow remains serialized as `null` / `withheld` until official ONS licensing approval is confirmed.

---

## 4. Audit Verdict

- **Platform Architectural Verdict:** **PARTIALLY RECONCILED — CONDITIONAL GO**
- **Readiness State:** Ready for controlled staging deployment upon confirmation of display and pagination guardrails.
