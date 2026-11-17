# JOBINTEL 2.0 — SPRINT 3B.3.2
# DELIVERABLE 5: EMPLOYER PILOT DATA DICTIONARY
## Formal Schema Specifications, Data Constraints, Nullability Rules & Field Validations

**Document Version:** 1.0.0  
**Phase:** Sprint 3B.3.2 (Five-Market Data Acquisition Pilot)  
**Audit Date:** November 2026  
**Auditor:** Principal Data Architect & Pydantic v2 Specialist  
**Execution Type:** Controlled Empirical Pilot  
**Target Baseline:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)  
**Production Isolation:** `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)

---

## 1. DATA DICTIONARY ARCHITECTURE & DESIGN PRINCIPLES

The JOBINTEL 2.0 Employer Pilot data dictionary is built on four core principles:
1. **Relational Normalization:** Strictly separates the **Employer Legal Entity** from **Locations**, **Hiring Observations**, **Skill Requirements**, and **Statutory Evidence Records**.
2. **Dual Headcount Representation:** Enforces either an exact scalar float (`observed_count`) OR an official size band (`headcount_band`), explicitly forbidding the synthesis of midpoint numbers.
3. **Epistemological Stock-Flow Disentanglement:** Every observation must declare its `measurement_basis` (`EMPLOYMENT_STOCK` vs. `RECRUITMENT_FLOW` vs. `REDUNDANCY_ACTION`) and `geographic_scope` (`GLOBAL_WORLDWIDE`, `NATIONAL_DOMESTIC`, `ESTABLISHMENT_FACILITY`).
4. **Strict PII Elimination:** All street-level residential numbers are eliminated; only aggregated metropolitan hubs are persisted. Recruiter personal names, personal phone numbers, and direct email addresses are strictly excluded.

---

## 2. ENTITY 1: `EmployerPilotRecord`

Represents the core legal and operating profile of a corporate entity. Stored in [employer_pilot_records.json](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_pilot_records.json) and [employer_pilot_records.csv](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_pilot_records.csv).

| Field Name | Type | Nullable | Pattern / Constraint | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `company_id` | `string` | **No** | `^comp_[a-z]{2}_[a-z0-9_-]{2,60}$` | Unique system canonical identifier (e.g. `comp_us_microsoft`). |
| `company_name` | `string` | **No** | `min_length=2, max_length=180` | Common or preferred commercial trade name. |
| `legal_entity_name` | `string` | **No** | `min_length=2, max_length=200` | Full legal corporate name as registered with national authority. |
| `trading_name` | `string` | **No** | `min_length=1, max_length=180` | Operating brand name or common trading designation. |
| `market_id` | `enum` | **No** | `AU`, `US`, `UK`, `SG`, `IN` | Primary sovereign operating market. |
| `registration_identifier` | `string` | **No** | `min_length=2, max_length=60` | Official registration number (e.g. `0000789019`, `02557590`). |
| `registration_identifier_type` | `enum` | **No** | `ABN`, `CIK`, `CRN`, `UEN`, `CIN`, `AGENCY_CODE` | National authority identifier standard. |
| `registration_status` | `enum` | **No** | `ACTIVE`, `DISSOLVED`, `SUSPENDED` | Official legal standing with corporate registrar. |
| `primary_domain` | `string` | **No** | `^[a-z0-9.-]+\.[a-z]{2,}$` | Root corporate web domain (e.g. `microsoft.com`). |
| `headquarters_country` | `string` | **No** | `^[A-Z]{2}$` | ISO 3166-1 alpha-2 country code of corporate headquarters. |
| `industry_sector` | `string` | **No** | `min_length=2, max_length=160` | Descriptive industry sector name. |
| `industry_classification_system`| `enum` | **No** | `NAICS_2022`, `UK_SIC_2007`, `ANZSIC_2006`, `SSIC_2020`, `NIC_2008` | Sovereign standard industrial classification taxonomy. |
| `industry_classification_version`| `string` | **No** | `min_length=2, max_length=120` | Detailed division or code (e.g. `511210`, `6201`). |
| `parent_company_id` | `string` | **Yes** | `^comp_[a-z]{2}_[a-z0-9_-]{2,60}$` | Immediate or ultimate corporate parent ID if subsidiary. |
| `identity_verification_status` | `enum` | **No** | `VERIFIED_OFFICIAL`, `VERIFIED_REVIEWED`, `REVIEW_REQUIRED` | Verification certainty level. |
| `source_ids` | `array[string]` | **No** | `min_items=1` | Array of source identifiers substantiating this entity. |
| `last_verified_at` | `datetime` | **No** | ISO 8601 UTC string (`Z`) | Timezone-aware timestamp of latest manual/automated audit. |

---

## 3. ENTITY 2: `EmployerLocation`

Represents an operating office, tech hub, or headquarters location. Nested within `EmployerPilotRecord`.

| Field Name | Type | Nullable | Pattern / Constraint | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `city` | `string` | **No** | `min_length=1, max_length=100` | Municipal city name (e.g. `Sydney`, `Redmond`, `London`). |
| `state_or_region` | `string` | **Yes** | `max_length=100` | State, province, or county (e.g. `NSW`, `WA`, `Cambridgeshire`). |
| `country_code` | `string` | **No** | `^[A-Z]{2}$` | ISO 3166-1 alpha-2 country code. |
| `location_type` | `enum` | **No** | `HEADQUARTERS`, `OFFICE`, `RESEARCH_HUB`, `TECH_CENTER` | Functional operational designation. |

*PII Restriction:* Street names, door numbers, building levels, and postal box codes are strictly prohibited.

---

## 4. ENTITY 3: `EmployerHiringObservation`

Represents empirical headcount stock or recruitment flow observations. Stored in [employer_hiring_observations.json](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_hiring_observations.json).

| Field Name | Type | Nullable | Constraint / Enum | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `observation_id` | `string` | **No** | `^obs_[a-z]{2}_[a-z0-9_-]{4,40}$` | Unique observation identifier. |
| `company_id` | `string` | **No** | Foreign Key to `Employer` | Linking canonical company ID. |
| `market_id` | `enum` | **No** | `AU`, `US`, `UK`, `SG`, `IN` | Sovereign market where observation was recorded. |
| `evidence_category` | `enum` | **No** | `OFFICIAL_EMPLOYMENT_STATISTIC`, `COMPANY_DISCLOSED_HIRING`, `EXPLICIT_VACANCY_COUNT`, `JOB_ADVERTISEMENT`, `EMPLOYMENT_CHANGE` | Classification tier from evidence taxonomy. |
| `measurement_basis` | `enum` | **No** | `EMPLOYMENT_STOCK`, `RECRUITMENT_FLOW`, `REDUNDANCY_ACTION` | Fundamental economic phenomenon measured. |
| `geographic_scope` | `enum` | **No** | `GLOBAL_WORLDWIDE`, `NATIONAL_DOMESTIC`, `ESTABLISHMENT_FACILITY` | Geographic footprint of the observation. |
| `metric_name` | `string` | **No** | `min_length=4, max_length=160` | Descriptive title of the metric. |
| `observed_count` | `float` | **Yes** | `ge=0.0` | Discrete numeric count if officially published. |
| `headcount_band` | `string` | **Yes** | Categorical string | Official size band (e.g. `"1000 to 4999"`, `"5000+"`). |
| `reference_period_start`| `date` | **No** | `YYYY-MM-DD` | Start date of reference reporting interval. |
| `reference_period_end` | `date` | **No** | `YYYY-MM-DD` | End date of reference reporting interval. |
| `data_source_id` | `string` | **No** | Foreign Key to Catalog | Source ID from `employer_source_catalog.json`. |
| `statutory_citation` | `string` | **Yes** | Statutory law or filing | Primary legal authority or filing reference. |
| `publication_gate_active`| `boolean`| **No** | `True` / `False` | Gating flag (True for UK vacancy flow). |
| `gate_reason` | `string` | **Yes** | Descriptive explanation | Mandatory justification if publication gate is active. |

*Validation Invariant:* Exactly one of `observed_count` OR `headcount_band` must be populated unless `publication_gate_active` is `True`.

---

## 5. ENTITY 4: `EmployerSkillObservation`

Represents empirical skill requirements extracted from authorized first-party ATS job descriptions. Stored in [employer_skill_observations.json](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_skill_observations.json).

| Field Name | Type | Nullable | Constraint / Enum | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `skill_obs_id` | `string` | **No** | `^sk_[a-z]{3}_[0-9]{3}$` | Unique skill observation identifier. |
| `company_id` | `string` | **No** | Foreign Key to `Employer` | Canonical employer identifier. |
| `market_id` | `enum` | **No** | `AU`, `US`, `UK`, `SG`, `IN` | Operating market. |
| `job_posting_id` | `string` | **No** | Requisition identifier | Source job posting ID from Greenhouse/Lever/USAJOBS. |
| `canonical_occ_code` | `string` | **No** | Valid `CAN_OCC_*` | Canonical occupation anchor code. |
| `raw_skill_phrase` | `string` | **No** | Unstructured text | Verbatim phrase extracted from job advertisement. |
| `canonical_skill_id` | `string` | **No** | Valid skill token | Normalized skill concept (e.g. `skill_python`, `skill_aws`). |
| `skill_name` | `string` | **No** | Standard title | Standardized display name. |
| `skill_category` | `enum` | **No** | `TECHNICAL`, `SPECIALIZED`, `SOFT` | Skill taxonomy category. |
| `requirement_level` | `enum` | **No** | `REQUIRED`, `PREFERRED` | Job specification priority. |
| `mapping_provenance` | `enum` | **No** | `EXACT`, `DERIVED`, `CURATED`, `UNMAPPED` | Methodological derivation audit tag. |
| `is_short_token_validated`| `boolean`| **No** | `True` / `False` | Confirms contextual disambiguation for short tokens. |

---

## 6. ENTITY 5: `EmployerEvidenceRecord`

Maintains the cryptographic and statutory audit trail for every data point. Stored in [employer_evidence_ledger.csv](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_evidence_ledger.csv).

| Field Name | Type | Nullable | Constraint | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `evidence_id` | `string` | **No** | `^evi_[a-z0-9_-]{4,40}$` | Unique cryptographic audit record ID. |
| `company_id` | `string` | **No** | Foreign Key | Target company or `ALL_{MARKET}_QUALIFIED`. |
| `source_id` | `string` | **No** | Foreign Key to Catalog | Source identifier. |
| `source_url` | `url` | **No** | Valid HTTP/HTTPS URI | Live official retrieval URL. |
| `retrieval_date` | `date` | **No** | `YYYY-MM-DD` | Date when evidence was collected and verified. |
| `statutory_citation` | `string` | **No** | Statutory law or filing | Legal basis governing data publication. |
| `license_tier` | `enum` | **No** | `CC_BY_4_0`, `OGL_V3_0`, `US_PUBLIC_DOMAIN`, `SODL_V1_0`, `PUBLIC_REGULATORY_DISCLOSURE` | Intellectual property license tier. |
| `raw_data_summary` | `string` | **No** | Descriptive text | Summary of data extracted. |
| `sha256_checksum` | `string` | **No** | `^[a-f0-9]{64}$` | Cryptographic SHA-256 hash of the raw evidence payload. |
| `verification_status`| `enum` | **No** | `VERIFIED_OFFICIAL`, `VERIFIED_REVIEWED` | Verification audit determination. |
