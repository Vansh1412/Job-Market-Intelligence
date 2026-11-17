# JOBINTEL 2.0 — SPRINT 3B.3 (PHASE 0)
## EMPLOYER INTELLIGENCE DATA DICTIONARY
### Entity Specifications, Relational Architecture, Data Types, Constraints & Quality Risk Controls

**Document ID:** `JOBINTEL-V2-SPRINT3B3-PH0-DATA-DICTIONARY`  
**Execution Phase:** Phase 0 (Data Architecture & Model Audit)  
**Date of Audit:** 2026-11-17  
**Design Standard:** Strict Pydantic v2 Schema Declarations, JSON Schema Compatibility, Entity Integrity Constraints.

---

## 1. DATA MODEL ARCHITECTURAL OVERVIEW

The proposed Global Employer Intelligence data architecture consists of **six interconnected core entities**:

```
+--------------------------------------------------------------------------+
|                                EMPLOYER                                  |
|  - employer_id (PK)                 - registration_id (CIN/CIK/CRN/...)  |
|  - legal_name                       - canonical_domain                   |
|  - country_code                     - parent_employer_id (Self-FK)       |
+------------------------------------+-------------------------------------+
                  | 1                | 1
                  |                  |
                  | 0..*             | 0..*
                  v                  v
+-----------------------------+    +---------------------------------------+
|      EMPLOYER_LOCATION      |    |       EMPLOYER_HIRING_OBSERVATION     |
|  - location_id (PK)         |    |  - observation_id (PK)                |
|  - employer_id (FK)         |    |  - employer_id (FK)                   |
|  - city, state, country     |    |  - canonical_occupation_id (FK)       |
|  - office_type              |    |  - advertised_openings (Nullable!)    |
|  - NO RESIDENTIAL DATA      |    |  - evidence_type                      |
+-----------------------------+    +-------------------+-------------------+
                                                       | 1
                                                       | 0..*
                                                       v
+-------------------------------+  +---------------------------------------+
|  EMPLOYER_SKILL_REQUIREMENT   |  |  EMPLOYER_QUALIFICATION_REQUIREMENT   |
|  - skill_requirement_id (PK)  |  |  - qualification_id (PK)              |
|  - employer_id (FK)           |  |  - employer_id (FK)                   |
|  - skill_token                |  |  - degree_level / certifications      |
|  - requirement_level          |  |  - min_experience_years               |
+-------------------------------+  +---------------------------------------+
                  ^                                    ^
                  |                                    |
                  +------------------+-----------------+
                                     |
                                     | 1..* references
                                     v
                  +------------------------------------+
                  |       EMPLOYER_EVIDENCE_RECORD     |
                  |  - evidence_id (PK)                |
                  |  - source_id                       |
                  |  - source_url                      |
                  |  - cryptographic_sha256            |
                  |  - provenance_tier                 |
                  +------------------------------------+
```

---

## 2. ENTITY SPECIFICATION: `Employer`

Represents an authoritative legal enterprise or operating commercial entity.

| Field Name | Type | Nullable | Uniqueness / Constraint | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `employer_id` | `string` | **No** | **Primary Key** | Canonical internal ID matching `^emp-[a-z]{2}-[a-z0-9._-]{2,80}$` (e.g. `emp-us-apple-inc`, `emp-in-infosys-ltd`). |
| `legal_name` | `string` | **No** | Mandatory | Officially registered corporate name (e.g. "APPLE INC.", "TATA CONSULTANCY SERVICES LIMITED"). |
| `trading_names` | `list[string]` | **No** | Default `[]` | Commercial DBAs and consumer brands (e.g. `["Apple", "Apple Store"]`). |
| `country_code` | `string` | **No** | ISO 3166-1 alpha-2 | Country of legal registration (`US`, `UK`, `AU`, `SG`, `IN`). |
| `registration_id` | `string` | Yes | Case-insensitive | Official national registration key: CIK (US), CRN (UK), ABN (AU), UEN (SG), CIN (IN). |
| `headquarters_city`| `string` | **No** | Min 2 chars | Principal corporate headquarters city. |
| `headquarters_state`| `string`| Yes | Max 80 chars | State, province, or administrative region. |
| `primary_industry_code` | `string` | **No** | Standard Code | Native statutory industry code: NAICS 2022 (US), UK SIC 2007, ANZSIC 2006 (AU), SSIC 2020 (SG), NIC-2008 (IN). |
| `canonical_domain` | `string` | Yes | FQDN format | Primary corporate web domain for entity resolution (e.g. `apple.com`, `tcs.com`). |
| `company_size_tier` | `string` | **No** | Enum | Enterprise size band: `MICRO` (1-9), `SMALL` (10-49), `MEDIUM` (50-249), `LARGE` (250-999), `ENTERPRISE` (1000+). |
| `ownership_type` | `string` | **No** | Enum | Corporate ownership structure: `PUBLIC_LISTED`, `PRIVATE_LIMITED`, `STATE_OWNED`, `SUBSIDIARY`, `NON_PROFIT`. |
| `parent_employer_id` | `string` | Yes | Self-Referential FK | Points to parent enterprise `employer_id` if this entity is a recognized subsidiary. |
| `subsidiary_ids` | `list[string]` | **No** | Default `[]` | List of child corporate entities. |
| `verification_status`| `string` | **No** | Enum | Identity validation status: `UNVERIFIED`, `REVIEW_REQUIRED`, `VERIFIED`, `REVOKED`. |
| `verified_at` | `datetime` | Yes | ISO 8601 UTC | Timestamp of verification. Mandatory if `verification_status == VERIFIED`. |
| `evidence_record_ids`| `list[string]`| **No** | Min 1 element | Foreign keys pointing to supporting `EmployerEvidenceRecord` objects. |

### Data Quality Risks & Validation Logic:
- **Corporate Dissolution Risk:** Companies dissolve or merge. Must validate against national status (`Active` vs `Struck Off` vs `Dissolved`).
- **Entity Inflation:** Failing to link local operating subsidiaries (e.g., "Google India Private Limited" vs "Google LLC") fragments hiring signals.

---

## 3. ENTITY SPECIFICATION: `EmployerLocation`

Represents a confirmed corporate physical operating facility or verified regional hub.

| Field Name | Type | Nullable | Uniqueness / Constraint | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `location_id` | `string` | **No** | **Primary Key** | Deterministic hash or ID `^loc-[a-z0-9._-]{8,64}$`. |
| `employer_id` | `string` | **No** | Foreign Key | References `Employer.employer_id`. |
| `country_code` | `string` | **No** | ISO 3166-1 alpha-2 | Country code where location physically exists. |
| `state_or_region` | `string` | Yes | Standard Region | State / Province / Territory (e.g. `California`, `Karnataka`, `New South Wales`). |
| `city` | `string` | **No** | Min 1 char | Urban agglomeration or municipality (e.g. `San Francisco`, `Bengaluru`, `Sydney`). |
| `office_type` | `string` | **No** | Enum | Classification: `GLOBAL_HQ`, `REGIONAL_HQ`, `R_AND_D_CENTER`, `BRANCH_OFFICE`, `REMOTE_HUB`. |
| `is_headquarters` | `boolean` | **No** | Boolean | True if primary registered or operating headquarters. |
| `address_redacted` | `boolean` | **No** | Default `True` | **PRIVACY ENFORCEMENT:** Strict flag confirming street-level PII or residential addresses are not published. |
| `evidence_id` | `string` | **No** | Foreign Key | References `EmployerEvidenceRecord`. |
| `observed_at` | `datetime` | **No** | ISO 8601 UTC | Date location evidence was verified. |

### Privacy & Governance Mandate:
> [!CAUTION]
> **Strict PII & Residential Address Elimination:**  
> Small businesses and remote startups frequently register using personal residential addresses. **JobIntel strictly restricts location resolution to City, State/Region, and Country.** Street names, building numbers, and apartment numbers are permanently scrubbed at ingestion.

---

## 4. ENTITY SPECIFICATION: `EmployerHiringObservation`

Represents an atomic, timestamped observation of recruitment activity.

| Field Name | Type | Nullable | Uniqueness / Constraint | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `observation_id` | `string` | **No** | **Primary Key** | Unique identifier matching `^eho-[a-z0-9._-]{8,64}$`. |
| `employer_id` | `string` | **No** | Foreign Key | References `Employer.employer_id`. |
| `job_title_raw` | `string` | **No** | Max 180 chars | Exact verbatim job title published by employer (e.g. "Senior Backend Staff Engineer"). |
| `canonical_occupation_id` | `string` | Yes | Foreign Key | Mapped JobIntel Canonical Role (e.g. `CAN_OCC_SOFTWARE_ENGINEER`). |
| `national_occupation_code` | `string` | Yes | Standard Code | Native taxonomy code (e.g. `US_SOC_2018:15-1252`, `AU_ANZSCO_2022:261313`). |
| `workplace_city` | `string` | Yes | Max 120 chars | Primary designated office city. |
| `workplace_country` | `string` | **No** | ISO 3166-1 alpha-2 | Country of posting. |
| `remote_policy` | `string` | **No** | Enum | Work mode: `ONSITE`, `HYBRID`, `FULLY_REMOTE`, `UNSPECIFIED`. |
| `advertised_openings` | `integer` | **YES (Explicitly Nullable)** | $\ge 1$ if present | **CARDINAL RULE:** Null when observation is an individual job advert. Populated ONLY when employer explicitly states count. |
| `employment_type` | `string` | **No** | Enum | `FULL_TIME`, `PART_TIME`, `CONTRACT_FIXED_TERM`, `INTERNSHIP`, `CASUAL`. |
| `seniority_level` | `string` | **No** | Enum | `ENTRY_LEVEL`, `MID_LEVEL`, `SENIOR`, `LEAD_PRINCIPAL`, `DIRECTOR_EXECUTIVE`, `UNSPECIFIED`. |
| `evidence_classification` | `string` | **No** | Enum | From 7-tier taxonomy: `JOB_ADVERTISEMENT`, `EXPLICIT_VACANCY_COUNT`, `OFFICIAL_EMPLOYMENT_STATISTIC`, etc. |
| `hiring_status` | `string` | **No** | Enum | Current observation state: `ACTIVE`, `EXPIRED`, `FILLED`, `WITHHELD_PENDING_REVIEW`. |
| `posted_at` | `datetime` | Yes | ISO 8601 UTC | Timestamp original advertisement was published. |
| `observed_at` | `datetime` | **No** | ISO 8601 UTC | Timestamp JobIntel ingested the observation. |
| `evidence_id` | `string` | **No** | Foreign Key | References `EmployerEvidenceRecord`. |

### Non-Conflation Rule:
- When `evidence_classification == JOB_ADVERTISEMENT`, `advertised_openings` defaults to `null`.
- One online job advert establishes only that an advert exists; it **must never be interpreted as 1 verified hire**.

---

## 5. ENTITY SPECIFICATION: `EmployerSkillRequirement`

Represents a specific skill or technical capability demanded by an employer for an occupation.

| Field Name | Type | Nullable | Uniqueness / Constraint | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `skill_requirement_id`| `string`| **No** | **Primary Key** | ID matching `^esr-[a-z0-9._-]{8,64}$`. |
| `employer_id` | `string` | **No** | Foreign Key | References `Employer.employer_id`. |
| `canonical_occupation_id`| `string`| **No** | Foreign Key | Mapped occupation concept. |
| `skill_token` | `string` | **No** | Standard Token | Canonical skill token matching JobIntel taxonomy (e.g. `skill_python`, `skill_kubernetes`). |
| `skill_name_display`| `string` | **No** | Max 100 chars | Clean display label (e.g. "Kubernetes", "PostgreSQL"). |
| `skill_category` | `string` | **No** | Enum | Taxonomy cluster: `PROGRAMMING_LANGUAGE`, `FRAMEWORK`, `CLOUD_INFRASTRUCTURE`, `DATA_ENGINEERING`, `TOOL`. |
| `requirement_level` | `string` | **No** | Enum | Rigor classification: `MANDATORY_REQUIRED`, `PREFERRED_BONUS`, `CONTEXTUAL_MENTION`. |
| `observation_count` | `integer` | **No** | $\ge 1$ | Number of independent job postings by this employer explicitly demanding this skill. |
| `observation_frequency_pct` | `float` | **No** | $0.0 \le x \le 100.0$ | Percentage of employer's postings in this occupation demanding the skill. |
| `observation_period_start` | `date` | **No** | ISO Date | Earliest observation included in window. |
| `observation_period_end` | `date` | **No** | ISO Date | Latest observation included in window. |
| `evidence_id` | `string` | **No** | Foreign Key | References `EmployerEvidenceRecord`. |

---

## 6. ENTITY SPECIFICATION: `EmployerQualificationRequirement`

Represents educational or professional credentials demanded by an employer.

| Field Name | Type | Nullable | Uniqueness / Constraint | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `qualification_id` | `string` | **No** | **Primary Key** | ID matching `^eqr-[a-z0-9._-]{8,64}$`. |
| `employer_id` | `string` | **No** | Foreign Key | References `Employer.employer_id`. |
| `canonical_occupation_id`| `string`| **No** | Foreign Key | Mapped occupation concept. |
| `qualification_type` | `string` | **No** | Enum | `ACADEMIC_DEGREE`, `PROFESSIONAL_CERTIFICATION`, `STATUTORY_LICENCE`, `MINIMUM_EXPERIENCE`. |
| `education_level` | `string` | Yes | Enum | `HIGH_SCHOOL`, `ASSOCIATE`, `BACHELORS`, `MASTERS`, `DOCTORATE`, `NO_DEGREE_REQUIRED`. |
| `certification_name`| `string` | Yes | Max 160 chars | Recognized professional credential (e.g. "AWS Certified Solutions Architect", "CISSP", "CPA"). |
| `min_experience_years`| `float` | Yes | $0.0 \le x \le 40.0$ | Explicit minimum years of professional experience requested in job descriptions. |
| `is_mandatory` | `boolean` | **No** | Boolean | True if stated as strict pre-condition for interview eligibility. |
| `evidence_id` | `string` | **No** | Foreign Key | References `EmployerEvidenceRecord`. |

---

## 7. ENTITY SPECIFICATION: `EmployerEvidenceRecord`

Maintains immutable cryptographic auditability for all employer facts.

| Field Name | Type | Nullable | Uniqueness / Constraint | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `evidence_id` | `string` | **No** | **Primary Key** | SHA-256 derived key matching `^ev-[a-f0-9]{32,64}$`. |
| `source_id` | `string` | **No** | Foreign Key | Unique source identifier (e.g. `uk.gov.companies_house`, `us.gov.sec.edgar`, `au.gov.wgea`). |
| `source_name` | `string` | **No** | Max 160 chars | Official publisher label. |
| `source_url` | `string` | **No** | Valid URL | Canonical source URL or public endpoint where record was retrieved. |
| `retrieval_timestamp`| `datetime`| **No** | ISO 8601 UTC | Exact timestamp of ingestion. |
| `source_native_id`| `string` | Yes | Max 120 chars | Primary identifier assigned by source (e.g. SEC CIK `0000320193`, UK CRN `00002065`). |
| `provenance_classification`| `string`| **No** | Enum | Integrity tier: `OFFICIAL_PUBLISHED`, `OFFICIALLY_DERIVED`, `EMPLOYER_DISCLOSED`, `CURATED_BENCHMARK`. |
| `publication_permission_status`| `string`| **No** | Enum | Licensing gate: `APPROVED_OPEN_ACCESS`, `APPROVED_FAIR_USE`, `WITHHELD_PENDING_REVIEW`, `REVOKED`. |
| `cryptographic_sha256`| `string` | **No** | 64 Hex Chars | SHA-256 hash of original raw JSON/text payload verifying non-tampering. |

---

## 8. UNIQUENESS & INTEGRITY CONSTRAINTS SUMMARY

1. **Employer Uniqueness:** `(country_code, registration_id)` must be unique across all non-null registration IDs.
2. **Domain Uniqueness:** `canonical_domain` must be unique across root enterprises (ignoring subdomains).
3. **Headquarters Validation:** Every `Employer` must have exactly one designated primary headquarters city.
4. **Hierarchical Consistency:** An `employer_id` cannot be its own `parent_employer_id` (preventing cyclic graphs).
5. **Evidence Immutability:** An `EmployerEvidenceRecord` is strictly append-only; updates require generating a new evidence record with updated timestamp.

**Audit Status:** `PASS — DATA DICTIONARY SPECIFIED ACCORDING TO REPOSITORY ARCHITECTURE`
