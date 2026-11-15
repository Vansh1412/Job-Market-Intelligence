# SPRINT 2C.1 GOVERNANCE DECISION MATRIX
## Comprehensive Authorization Matrix, Reason Code Catalog & Evaluation Rules

- **Document Identifier:** `JOBINTEL-S2C1-DEC-003`
- **Execution Date:** November 13, 2026
- **Status:** Canonical Decision Matrix (Sprint 2C.1)
- **Applies to:** `GovernancePolicyEngine`, Data Catalog Registry, Fast API Router Middleware

---

## 1. Multi-Source, Multi-Operation Governance Decision Matrix

The following matrix documents the policy engine evaluation outcome across all 11 registered sources in `src/backend/data_catalog/registry.py` and all 8 governance operations:

```
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| COMPREHENSIVE GOVERNANCE DECISION MATRIX                                                                                                                          |
+----+-----------------------+-----------+------------+------------+------------+------------+------------+------------+------------+------------+--------------------+
| #  | Source Identifier     | Market    | Internal   | Public Agg | Commercial | Raw Data   | ML Model   | Internal   | Public     | Commercial | Governing Legal    |
|    |                       |           | Analytics  | Display    | Agg Display| Redistrib. | Training   | Inference  | Inference  | Inference  | Baseline / Reason  |
+----+-----------------------+-----------+------------+------------+------------+------------+------------+------------+------------+------------+--------------------+
| 1  | uk.ons.ashe           | UK        | CONDITIONAL| DENIED     | DENIED     | APPROVED   | DENIED     | N/A        | N/A        | N/A        | OGL v3.0 / Locked  |
| 2  | uk.ons.labour-demand  | UK        | CONDITIONAL| CONDITIONAL| CONDITIONAL| APPROVED   | DENIED     | N/A        | N/A        | N/A        | OGL v3.0 / Vacancy |
| 3  | uk.ons.soc2020        | UK        | APPROVED   | APPROVED   | APPROVED   | APPROVED   | APPROVED   | N/A        | N/A        | N/A        | OGL v3.0 / Taxonomy|
| 4  | us.jobintel.market-data| US       | APPROVED   | N/A        | N/A        | DENIED     | DENIED     | APPROVED   | APPROVED   | DENIED     | DataForge Tier 1   |
| 5  | in.jobintel.market-data| India    | CONDITIONAL| N/A        | N/A        | DENIED     | DENIED     | APPROVED   | APPROVED   | DENIED     | Zero-Retraining Rul|
| 6  | au.abs.eeh            | Australia | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | N/A        | N/A        | N/A        | CC-BY 4.0 / Not Col|
| 7  | au.abs.osca           | Australia | APPROVED   | APPROVED   | APPROVED   | APPROVED   | APPROVED   | N/A        | N/A        | N/A        | CC-BY 4.0 / Taxon  |
| 8  | au.jsa.ivi            | Australia | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | DENIED     | N/A        | N/A        | N/A        | CC-BY 4.0 / Vacancy|
| 9  | sg.mom.ows            | Singapore | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | N/A        | N/A        | N/A        | SG ODL / Not Col   |
| 10 | sg.mom.vacancies      | Singapore | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | REVIEW_REQ | DENIED     | N/A        | N/A        | N/A        | SG ODL / Vacancy   |
| 11 | sg.singstat.ssoc2024  | Singapore | APPROVED   | APPROVED   | APPROVED   | APPROVED   | APPROVED   | N/A        | N/A        | N/A        | SG ODL / Taxonomy  |
+----+-----------------------+-----------+------------+------------+------------+------------+------------+------------+------------+------------+--------------------+
```

---

## 2. Stable Governance Denial Reason Code Catalog

The `GovernancePolicyEngine` emits deterministic, sanitized reason codes. These codes are categorized by evaluation gate:

| Gate | Reason Code | Description | Public Sanitized Message |
|---|---|---|---|
| **Gate 1: Revocation** | `GOV_DENIED_REVOKED_SOURCE` | Source-wide revocation registered. | `Dataset Temporarily Unavailable` |
| | `GOV_DENIED_REVOKED_RELEASE` | Specific release identifier revoked. | `Dataset Release Unavailable` |
| | `GOV_DENIED_REVOKED_APPROVAL` | Specific approval record canceled. | `Authorization Suspended` |
| | `GOV_DENIED_REVOKED_MODEL` | ML model artifact revoked. | `Model Inference Unavailable` |
| **Gate 2: Source** | `GOV_DENIED_UNKNOWN_SOURCE` | Source ID absent from data catalog. | `Internal Governance Error` |
| | `GOV_DENIED_UNREVIEWED_SOURCE` | Source in `REVIEW_REQUIRED` state. | `Dataset Under Compliance Review` |
| **Gate 3: Model** | `GOV_DENIED_MODEL_LINEAGE_MISSING` | Model lineage record not supplied. | `Model Lineage Incomplete` |
| | `GOV_DENIED_COMMERCIAL_RESTRICTION` | Model licensed for Tier 1 non-commercial. | `Commercial Monetization Restricted` |
| | `GOV_DENIED_ZERO_RETRAINING_VIOLATION` | Model violates zero-retraining policy. | `Model Certification Failed` |
| **Gate 4: Release** | `GOV_DENIED_RELEASE_REQUIRED` | Operation requires a release ID. | `Release Identifier Missing` |
| | `GOV_DENIED_RELEASE_NOT_FOUND` | Release ID absent from registry. | `Release Record Not Found` |
| | `GOV_DENIED_RELEASE_SUSPENDED` | Release lifecycle state is `SUSPENDED`. | `Dataset Quality Suspension` |
| | `GOV_DENIED_RELEASE_REVOKED` | Release lifecycle state is `REVOKED`. | `Dataset Permanently Revoked` |
| | `GOV_DENIED_CHECKSUM_MISMATCH` | Physical SHA-256 diverges from release. | `Dataset Integrity Check Failed` |
| **Gate 5: Approval** | `GOV_DENIED_APPROVAL_MISSING` | No active approval record for operation. | `Operation Not Approved` |
| | `GOV_DENIED_APPROVAL_EXPIRED` | Temporal approval window has elapsed. | `Dataset Release Expired` |
| | `GOV_DENIED_VERSION_MISMATCH` | Approval granted for different version. | `Version Authorization Mismatch` |
| | `GOV_DENIED_LICENSE_VERSION_MISMATCH`| License terms version diverges. | `License Version Mismatch` |
| | `GOV_DENIED_GEOGRAPHY_MISMATCH` | Requested geography outside approval. | `Jurisdiction Outside Approved Scope` |
| | `GOV_DENIED_AUDIENCE_MISMATCH` | Requested audience outside approval. | `Audience Tier Unauthorized` |
| **Gate 6: Caveats** | `GOV_DENIED_CONDITIONS_UNMET` | Statutory caveats or filters omitted. | `Mandatory Caveats Unmet` |
| **Success** | `GOV_ALLOWED` | All gates cleared; operation authorized. | `Operation Authorized` |

---

## 3. Critical Governance Decision Boundaries

### 3.1 USA DataForge Model Decision Boundary
- **Internal / Non-Commercial Inference:** `ALLOWED` under `GOV_ALLOWED`. Clause 3.1 permits sharing Derived Materials (models) for research and benchmarking.
- **Commercial Paid Inference:** `DENIED` under `GOV_DENIED_COMMERCIAL_RESTRICTION`. Schedule A purchased Tier 1; commercial deployment requires formal Tier 2 addendum or migration to US BLS OEWS.
- **Model Retraining:** `DENIED` under `GOV_DENIED_TIER2_LICENSE_REQUIRED`.

### 3.2 India Salary Model Decision Boundary
- **Inference:** `ALLOWED` under `GOV_ALLOWED`. Frozen scikit-learn weights are served with a mandatory research model disclaimer.
- **Retraining:** `PERMANENTLY DENIED` under `GOV_DENIED_ZERO_RETRAINING_RULE`. The raw file `indian-job-market-dataset-2025.xlsx` is permanently quarantined.

### 3.3 UK ASHE Decision Boundary
- **Public Aggregate Display:** `DENIED` under `GOV_DENIED_UNREVIEWED_SOURCE` and `GOV_DENIED_APPROVAL_MISSING`.
- **API Routes:** All 5 endpoints fail closed with `HTTP 503 UK_DATA_NOT_PUBLISHED`.
- **Publication Gate:** Unlocking requires formal dual-custody executive approval sign-off in Phase 2C.

