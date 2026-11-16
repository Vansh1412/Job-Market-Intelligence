# JOBINTEL 2.0 — SPRINT 3A
## Data Dictionary: Global Occupation Intelligence & Taxonomy Entities

**Date:** November 16, 2026  
**Sprint:** 3A  
**Status:** Approved Schema Dictionary (`JOBINTEL-S3A-DICT-001`)  
**Author:** Principal Data Architect, Backend Engineer  

---

## 1. Domain Enums

### 1.1 `ClassificationId` (StrEnum)
Unique identifier for an official national or international classification version:
- `UK_SOC_2020`: UK Standard Occupational Classification 2020.
- `US_SOC_2018`: US 2018 Standard Occupational Classification.
- `AU_OSCA_2024`: Occupation Standard Classification for Australia 2024.
- `AU_ANZSCO_2022`: Australian and New Zealand Standard Classification of Occupations 2022.
- `SG_SSOC_2024`: Singapore Standard Occupational Classification 2024.
- `SG_SSOC_2020`: Singapore Standard Occupational Classification 2020.
- `IN_NCO_2015`: India National Classification of Occupations 2015.
- `INT_ISCO_08`: International Standard Classification of Occupations 2008.

### 1.2 `RelationshipType` (StrEnum)
Semantic category of concordance between occupations:
- `EXACT_MATCH`: Duties, skills, and scope are substantially identical.
- `CLOSE_MATCH`: High alignment with minor terminology or qualification nuances.
- `BROADER_THAN`: Source occupation is an aggregate encompassing multiple target roles.
- `NARROWER_THAN`: Source occupation is a specialization within a broader target group.
- `PARTIAL_OVERLAP`: Shared competencies, but key duties or certifications diverge.
- `RELATED_BUT_DISTINCT`: Adjacent profession; related discipline but non-interchangeable.
- `NO_SUPPORTED_MAPPING`: Country-specific role with no counterpart in target jurisdiction.

### 1.3 `MappingMethodology` (StrEnum)
Process by which the relationship was established:
- `OFFICIAL_CROSSWALK`: Direct government-published concordance table.
- `EXPERT_ASSESSMENT`: Systematic rubric evaluation by labor market researchers.
- `CALIBRATED_TASK_OVERLAP`: Mathematical/semantic evaluation of official task descriptions.

### 1.4 `ReviewStatus` (StrEnum)
Verification status of the mapping record:
- `VERIFIED_OFFICIAL`: Official government correspondence table.
- `VERIFIED_REVIEWED`: Human-reviewed by domain expert.
- `DERIVED_HIGH_CONFIDENCE`: Strong empirical concordance; pending formal signoff.
- `DERIVED_MEDIUM_CONFIDENCE`: Moderate alignment with documented task differences.
- `LOW_CONFIDENCE`: Speculative concordance.
- `REVIEW_REQUIRED`: Candidate mapping undergoing review.
- `UNMAPPED`: Formally designated as unmappable.
- `REJECTED`: Disproven and deprecated mapping.

---

## 2. Entity Schemas & Field Definitions

### 2.1 `ClassificationSystem`

| Field | Type | Constraint | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `classification_id` | `str` | Pattern `^[A-Z]{2,3}_[A-Z0-9]+_\d{4}$` | Unique identifier of classification system. | `"UK_SOC_2020"` |
| `market_id` | `MarketId` | Enum (`IN`, `US`, `UK`, `AU`, `SG`, `INT`) | Jurisdiction of origin. | `"UK"` |
| `official_title` | `str` | Min length 5, max 160 | Official published name of the standard. | `"UK Standard Occupational Classification 2020"` |
| `version_edition` | `str` | Min length 2, max 40 | Edition year or revision label. | `"2020 Volume 1"` |
| `issuing_authority` | `str` | Min length 3, max 120 | Government statistical agency. | `"Office for National Statistics (ONS)"` |
| `code_format` | `str` | Regex pattern | Structural format of occupation codes. | `r"^\d{4}$"` |
| `hierarchy_levels` | `tuple[str, ...]` | Length 1 to 6 | Names of tiers from top to bottom. | `("Major", "Sub-Major", "Minor", "Unit Group")` |
| `is_active` | `bool` | Default `True` | Whether active standard in jurisdiction. | `True` |
| `source_reference` | `AnyHttpUrl` | Valid URL | Official web documentation. | `"https://www.ons.gov.uk/methodology/..."` |
| `license_attribution` | `str` | Min length 5, max 200 | Licensing terms for reuse. | `"Open Government Licence v3.0"` |

### 2.2 `NationalOccupation`

| Field | Type | Constraint | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `occupation_id` | `str` | Format `{classification_id}:{code}` | Unique composite identifier. | `"UK_SOC_2020:2134"` |
| `classification_id` | `str` | Foreign key to `ClassificationSystem` | Parent classification. | `"UK_SOC_2020"` |
| `market_id` | `MarketId` | Enum | Jurisdiction of origin. | `"UK"` |
| `occupation_code` | `str` | Matches `code_format` | Official code string. | `"2134"` |
| `occupation_title` | `str` | Min length 2, max 200 | Official verbatim occupation title. | `"Programmers and software development professionals"` |
| `official_definition` | `str` | Min length 10, max 2000 | Official scope note or description. | `"Programmers and software development professionals design, develop, test..."` |
| `tasks` | `tuple[str, ...]` | Min 0 items | Official duties from taxonomy volume. | `("writes code in multiple languages", "debugs software systems")` |
| `entry_qualifications` | `str \| None` | Max 500 chars | Typical education, degrees, training. | `"Degree or equivalent qualification in computer science or related field"` |
| `hierarchy_level` | `str` | In `hierarchy_levels` | Hierarchy tier. | `"Unit Group"` |
| `parent_code` | `str \| None` | Valid parent code | Immediate parent category code. | `"213"` |
| `is_leaf` | `bool` | Default `True` | Whether most granular codable level. | `True` |
| `alternate_titles` | `tuple[str, ...]` | Min 0 items | Official coding index aliases. | `("Backend developer", "Software engineer", "Java programmer")` |

### 2.3 `CanonicalOccupation`

| Field | Type | Constraint | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `canonical_occupation_id` | `str` | Pattern `^CAN_OCC_[A-Z0-9_]+$` | Unique canonical identifier. | `"CAN_OCC_SOFTWARE_ENGINEER"` |
| `preferred_title` | `str` | Min length 3, max 120 | Globally understood preferred title. | `"Software Engineer"` |
| `concept_family` | `str` | Min length 3, max 80 | High-level occupational domain. | `"Software & Applications"` |
| `description` | `str` | Min length 20, max 2000 | Comprehensive harmonized description. | `"Designs, develops, tests, and maintains software applications and systems..."` |
| `core_competencies` | `tuple[str, ...]` | Min 1 item | Cross-market technical competencies. | `("Software Architecture", "Algorithms", "Version Control", "System Design")` |
| `status` | `str` | Literal `ACTIVE`, `DEPRECATED` | Concept lifecycle state. | `"ACTIVE"` |

### 2.4 `OccupationMapping` & `MappingProvenance`

| Field | Type | Constraint | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `mapping_id` | `str` | Unique string | Identifier for mapping pair. | `"map_uk2134_us151252_v1"` |
| `source_occupation_id` | `str` | Valid `occupation_id` | Source national occupation. | `"UK_SOC_2020:2134"` |
| `target_occupation_id` | `str` | Valid `occupation_id` or canonical | Target national or canonical concept. | `"US_SOC_2018:15-1252"` |
| `target_type` | `str` | Literal `NATIONAL`, `CANONICAL` | Whether target is national or canonical. | `"NATIONAL"` |
| `relationship_type` | `RelationshipType` | Enum | Exact, Close, Broader, Narrower, etc. | `"CLOSE_MATCH"` |
| `confidence_score` | `Decimal` | Range `0.00` to `1.00` | Calibrated concordance score. | `Decimal("0.92")` |
| `review_status` | `ReviewStatus` | Enum | Official, Reviewed, Derived, etc. | `"VERIFIED_REVIEWED"` |
| `methodology` | `MappingMethodology` | Enum | Official crosswalk, expert, etc. | `"EXPERT_ASSESSMENT"` |
| `evidence_sources` | `tuple[str, ...]` | Min 1 item | Citations or reference URLs. | `("https://www.ons.gov.uk/...", "https://www.bls.gov/...")` |
| `notes_and_limitations` | `str` | Max 1000 chars | Caveats, differences, or exclusions. | `"UK 2134 includes web developers while US splits 15-1254."` |
| `reviewer` | `str` | Min length 2, max 80 | Identity of reviewer or pipeline. | `"JobIntel Taxonomy Review Committee"` |
| `effective_date` | `str` | ISO date string | Date mapping took effect. | `"2026-11-16"` |
| `created_at` | `datetime` | Valid timestamp | Creation timestamp. | `"2026-11-16T10:00:00Z"` |
