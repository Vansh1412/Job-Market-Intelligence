# SPRINT 2C — PERMISSION & APPROVAL MODEL
## Purpose-Specific 7-State Permission Matrix, Source Audits & Contractual Analysis

- **Document Identifier:** `JOBINTEL-S2C-STD-003`
- **Status:** Approved Engineering Standard (Sprint 2C.0 Consolidation)
- **Authority:** Subordinate to `SPRINT2C_GOVERNANCE_MASTER_STANDARD.md`
- **Date:** November 2026
- **Applies to:** Data Catalog Registry (`src/backend/data_catalog/`), Ingestion Contracts, Policy Engine Engine

---

## 1. The 7-State Auditable Permission Architecture

In previous design iterations, permissions were represented as crude boolean flags (`can_publish: bool`, `can_train: bool`). This is inadequate for enterprise compliance because a boolean cannot distinguish between a permission that is actively rejected, under evaluation, conditionally permitted, expired, or simply unknown.

The JOBINTEL 2.0 standard mandates that all operational permissions must be evaluated against a **7-State Permission Enum**:

```python
class PermissionState(StrEnum):
    UNKNOWN = "UNKNOWN"                    # Unevaluated; fails closed immediately
    REVIEW_REQUIRED = "REVIEW_REQUIRED"    # Identified but pending legal/compliance review
    APPROVED = "APPROVED"                  # Fully authorized without extra operational conditions
    CONDITIONAL = "CONDITIONAL"            # Authorized strictly subject to mandatory caveats/filters
    DENIED = "DENIED"                      # Explicitly prohibited by legal counsel or source terms
    EXPIRED = "EXPIRED"                    # Temporally bounded grant has elapsed
    REVOKED = "REVOKED"                    # Previously approved grant actively canceled (kill-switch)
```

### 1.1 Non-Permissive Evaluation Invariant
Any state other than `APPROVED` and `CONDITIONAL` evaluates to **DENIED** at runtime. `UNKNOWN` and `REVIEW_REQUIRED` are strictly non-permissive.

---

## 2. Orthogonal Purpose-Specific Permission Matrix

Permission to perform one data operation never conveys permission to perform another. The governance architecture defines **seven distinct, orthogonal permission checks**:

```
+---------------------------------------------------------------------------------------------------+
| THE SEVEN ORTHOGONAL PERMISSION CHECKS                                                            |
+------------------------------------+--------------------------------------------------------------+
| Permission Dimension               | Technical & Operational Scope                                |
+------------------------------------+--------------------------------------------------------------+
| 1. public_aggregate_display        | Rendering aggregated statistics on open, unauthenticated web |
| 2. commercial_aggregate_display    | Displaying or querying aggregate statistics in paid tiers    |
| 3. redistribution_raw              | Allowing external users/clients to download raw records      |
| 4. ml_training                     | Using data records as input features to train or fit models  |
| 5. internal_model_inference        | Generating model predictions for internal QA or evaluation   |
| 6. public_model_inference          | Serving model predictions across unauthenticated public APIs |
| 7. commercial_model_inference      | Serving model predictions as a paid commercial API / SaaS    |
+------------------------------------+--------------------------------------------------------------+
```

---

## 3. Source-by-Source Governance Audit (All 11 Catalog Sources)

Audit of all eleven sources currently declared in `src/backend/data_catalog/registry.py`:

| Source ID | Market | Publisher | Legal License Basis | Public Display | Commercial Display | Raw Redist. | ML Train | Public Infer. | Commercial Infer. | Governance Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| `uk.ons.ashe` | UK | ONS | Open Government Licence v3.0 | `CONDITIONAL` | `CONDITIONAL` | `APPROVED` | `REVIEW_REQ` | `N/A` | `N/A` | **LOCKED (503):** Pending dual-custody sign-off & URL reconciliation. |
| `uk.ons.labour-demand` | UK | ONS / Textkernel | Open Government Licence v3.0 | `CONDITIONAL` | `CONDITIONAL` | `APPROVED` | `DENIED` | `N/A` | `N/A` | **NOT COLLECTED:** Vacancy advert counts only; not hires. |
| `uk.ons.soc2020` | UK | ONS | Open Government Licence v3.0 | `APPROVED` | `APPROVED` | `APPROVED` | `APPROVED` | `N/A` | `N/A` | **VERIFIED:** Classification reference only; no salary data. |
| `us.jobintel.market-data` | US | JobIntel (DataForge) | Proprietary Tier 1 License | `N/A` | `N/A` | `DENIED` | `DENIED` | `APPROVED` | `REVIEW_REQ` | **FROZEN:** Predictions served as research derived materials. |
| `in.jobintel.market-data` | India | JobIntel Research | Unknown / Unrecorded | `N/A` | `N/A` | `DENIED` | `DENIED` | `APPROVED` | `REVIEW_REQ` | **FROZEN:** Zero-retraining rule enforced; research serving only. |
| `au.abs.eeh` | Australia | ABS | CC-BY 4.0 | `CONDITIONAL` | `CONDITIONAL` | `APPROVED` | `REVIEW_REQ` | `N/A` | `N/A` | **NOT COLLECTED:** Candidate for Phase 3 ingestion. |
| `au.abs.osca` | Australia | ABS | CC-BY 4.0 | `APPROVED` | `APPROVED` | `APPROVED` | `APPROVED` | `N/A` | `N/A` | **NOT COLLECTED:** Official 2024 classification taxonomy. |
| `au.jsa.ivi` | Australia | JSA | CC-BY 4.0 | `CONDITIONAL` | `CONDITIONAL` | `APPROVED` | `DENIED` | `N/A` | `N/A` | **NOT COLLECTED:** Internet vacancy recruitment index. |
| `sg.mom.ows` | Singapore | MOM | Singapore Open Data Licence | `CONDITIONAL` | `CONDITIONAL` | `APPROVED` | `REVIEW_REQ` | `N/A` | `N/A` | **NOT COLLECTED:** Candidate for Phase 3 ingestion. |
| `sg.mom.vacancies` | Singapore | MOM | Singapore Open Data Licence | `CONDITIONAL` | `CONDITIONAL` | `APPROVED` | `DENIED` | `N/A` | `N/A` | **NOT COLLECTED:** Job vacancy recruitment index. |
| `sg.singstat.ssoc2024` | Singapore | SingStat | Singapore Open Data Licence | `APPROVED` | `APPROVED` | `APPROVED` | `APPROVED` | `N/A` | `N/A` | **NOT COLLECTED:** Official 2024 classification taxonomy. |

---

## 4. In-Depth Contractual Analysis: USA DataForge Dataset A

A critical objective of Sprint 2C.0 is to resolve ambiguity surrounding `data/raw/dataset_A/` by conducting a rigorous, evidence-based legal text analysis of the governing contract (`data/raw/dataset_A/LICENSE.md`).

### 4.1 Verified Contract Evidence:
1. **Definition of Derived Materials (Section 1.2):**
   > *"1.2 'Derived Materials' means analyses, models, reports, visualizations, aggregated statistics, or machine-learning model weights created by Licensee using the Dataset, provided that the Dataset records themselves cannot be extracted, reconstructed, or reverse-engineered from such materials in substantially their original form."*
2. **Tier 1 — Internal Analytics Grant (Section 3.1):**
   > *"3.1 Tier 1 — Internal Analytics. Licensee may use the Dataset for internal business analysis, research, benchmarking, and reporting within Licensee's organization. Licensee may share Derived Materials (but not Raw Data) with third parties, including in publications, provided no Dataset records are disclosed at record level."*
3. **Tier 2 — AI / Machine-Learning Training Grant (Section 3.2):**
   > *"3.2 Tier 2 — AI / Machine-Learning Training. All Tier 1 rights, plus the right to use the Dataset to train, fine-tune, evaluate, and validate machine-learning and artificial-intelligence models, and to deploy and commercially distribute the resulting models, provided the models do not memorize and emit Dataset records verbatim at scale."*
4. **Schedule A (Purchased License Tier, Lines 124–131):**
   ```
   | Tier | Included rights | Purchased (check one) |
   | Tier 1 — Internal Analytics | Internal analysis, benchmarking, reporting; share Derived Materials only | ☑ |
   | Tier 2 — AI / ML Training | Tier 1 + model training, fine-tuning, evaluation; commercial model deployment | ☐ |
   | Tier 3 — Redistribution / Embedded | Tier 2 + embed portions in Licensee products (no standalone dataset resale) | ☐ |
   ```

### 4.2 Legal & Operational Findings:
- **Trained Model Artifacts are "Derived Materials":** Section 1.2 explicitly includes "machine-learning model weights" in the definition of Derived Materials. Under Section 3.1, Licensee is permitted to share Derived Materials with third parties.
- **The Contractual Tension:** Schedule A explicitly shows **Tier 1 is checked (`☑`)** while **Tier 2 is unchecked (`☐`)**. Section 3.2 states that Tier 2 grants the right *"to deploy and commercially distribute the resulting models"*.
- **The Operational Boundary:**
  - *Internal & Research Serving:* Serving predictions from the existing frozen weights (`salary_usa_xgb_model.joblib`) for internal benchmarking, academic evaluation, or free exploratory research is legally defensible under Section 3.1 as sharing Derived Materials.
  - *Commercial SaaS / Paid API:* Monetizing access to the model, offering paid commercial API access, or retraining the model on Dataset A without upgrading to Tier 2 constitutes a **material contractual breach** of Sections 2.1 and 3.2.
- **Sprint 2C Decision:** Keep USA model serving active for non-commercial research; mark `commercial_model_inference` as `REVIEW_REQUIRED`; require formal commercial Tier 2 upgrade or migration to US BLS OEWS prior to paid launch.

---

## 5. In-Depth Analysis: India Job Market Dataset

- **Physical Inventory:** `data/raw/india/indian-job-market-dataset-2025.xlsx` (31,709,363 bytes, dated 14-Oct-2025).
- **Missing Documentation:** No `LICENSE.md`, `README.md`, or `DATASHEET.md` exists in `data/raw/india/`.
- **Catalog Status:** `src/backend/data_catalog/registry.py:21-25` marks it `reuse_review_status = ReuseReviewStatus.UNKNOWN` and `validation_status = ValidationStatus.NOT_COLLECTED`.
- **Operational Boundary:**
  - The existing frozen weights (`salary_india_hgb_model.joblib`) are parametric derived representations verified bitwise identical in `artifact_manifest.json`.
  - The platform continues to serve non-commercial predictions under the disclaimer that results represent historical research models.
  - **Zero-Retraining Governance Rule:** Re-fitting or training on the raw Excel file is **permanently prohibited**. In Phase 3, this source will be replaced by microdata from India's official Periodic Labour Force Survey (PLFS) published by MOSPI.

---

## 6. In-Depth Analysis: UK ASHE 2025 Revised

- **Legal License:** Open Government Licence v3.0 (OGL v3.0).
- **Commercial Rights:** OGL v3.0 unconditionally authorizes commercial exploitation, adaptation, and public display of aggregate statistics.
- **Statutory Obligation:** Mandatory attribution text must be displayed on all screens and payloads:
  > *"Source: Office for National Statistics licensed under the Open Government Licence v.3.0"*
- **Current Blocker:** Dataset publication remains blocked (`HTTP 503 UK_DATA_NOT_PUBLISHED`) because:
  1. The catalog record (`registry.py:81`) is set to `REVIEW_REQUIRED`.
  2. The manifest records `source_reference_matches_catalog: false` (URL slug contains `soc2010ashetable15` vs catalog `socashetable15`).
  3. Formal dual-custody executive sign-off has not been completed.

