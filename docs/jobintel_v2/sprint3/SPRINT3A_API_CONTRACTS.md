# JOBINTEL 2.0 — SPRINT 3A
## API Contracts & OpenAPI Specification: Global Occupation Intelligence

**Date:** November 16, 2026  
**Sprint:** 3A  
**Status:** Approved API Contract (`JOBINTEL-S3A-API-001`)  
**Base URL:** `/api/v1/occupations` (and root alias `/v1/occupations`)  

---

## 1. Endpoints Overview

| Method | Endpoint Path | Query / Path Parameters | Response Model | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/v1/occupations/classifications` | `market` (optional `str`) | `list[ClassificationSystem]` | Lists official classification systems. |
| `GET` | `/v1/occupations/classifications/{classification_id}` | `classification_id` (`str`) | `ClassificationSystem` | Metadata for an official classification. |
| `GET` | `/v1/occupations/classifications/{classification_id}/occupations` | `q`, `page` (`int`), `page_size` (`int`) | `OccupationPage` | Paginated occupations within a system. |
| `GET` | `/v1/occupations/search` | `q` (`str`), `market`, `limit` (`int`) | `list[NationalOccupation]` | Multi-market search with relevance ranking. |
| `GET` | `/v1/occupations/canonical` | None | `list[CanonicalOccupation]` | Lists all harmonized canonical concepts. |
| `GET` | `/v1/occupations/canonical/{canonical_id}` | `canonical_id` (`str`) | `CanonicalOccupation` | Definition of a canonical archetype. |
| `GET` | `/v1/occupations/compare` | `source_occupation_id`, `target_market` | `CrossMarketComparisonResult` | Cross-market concordance comparison. |
| `GET` | `/v1/occupations/{occupation_id}/mappings` | `occupation_id` (`str`), `target_market` | `list[OccupationMapping]` | All mappings originating from occupation. |
| `GET` | `/v1/occupations/{occupation_id}` | `occupation_id` (`str`) | `NationalOccupation` | Full official definition, tasks, entry routes. |

---

## 2. Detailed Endpoint Contracts & Example Payloads

### 2.1 `GET /api/v1/occupations/classifications`
Retrieves all supported classification systems. Supports filtering by `?market=UK`.

**Example Response (`HTTP 200 OK`):**
```json
[
  {
    "classification_id": "UK_SOC_2020",
    "market_id": "UK",
    "official_title": "UK Standard Occupational Classification 2020",
    "version_edition": "2020 Volume 1 & 2",
    "issuing_authority": "Office for National Statistics (ONS)",
    "code_format": "^\\d{4}$",
    "hierarchy_levels": ["Major Group", "Sub-Major Group", "Minor Group", "Unit Group"],
    "is_active": true,
    "source_reference": "https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020",
    "license_attribution": "Open Government Licence v3.0 (OGL v3.0)"
  }
]
```

### 2.2 `GET /api/v1/occupations/search?q=Software+Developer`
Performs deterministic relevance-ranked search across national occupation codes, titles, and aliases.

**Example Response (`HTTP 200 OK`):**
```json
[
  {
    "occupation_id": "SG_SSOC_2024:25121",
    "classification_id": "SG_SSOC_2024",
    "market_id": "SG",
    "occupation_code": "25121",
    "occupation_title": "Software Developer",
    "official_definition": "Researches, designs, writes, and modifies computer software, applications, and operating systems according to technical requirements.",
    "tasks": [
      "analyzes software requirements and designs system architecture",
      "develops program code using structured programming languages"
    ],
    "entry_qualifications": "Bachelor's degree in computer science, information systems, or equivalent polytechnic diploma.",
    "hierarchy_level": "Detailed Occupation",
    "parent_code": "2512",
    "is_leaf": true,
    "alternate_titles": ["Software developer", "Software engineer", "Application developer"]
  }
]
```

### 2.3 `GET /api/v1/occupations/compare?source_occupation_id=UK_SOC_2020:2134`
Compares a source occupation to target counterparts in other markets, generating explicit relationship types, confidence scores, and approximation warnings.

**Example Response (`HTTP 200 OK`):**
```json
{
  "source_occupation": {
    "occupation_id": "UK_SOC_2020:2134",
    "classification_id": "UK_SOC_2020",
    "market_id": "UK",
    "occupation_code": "2134",
    "occupation_title": "Programmers and software development professionals"
  },
  "matches": [
    {
      "target_occupation": {
        "occupation_id": "US_SOC_2018:15-1252",
        "classification_id": "US_SOC_2018",
        "market_id": "US",
        "occupation_code": "15-1252",
        "occupation_title": "Software Developers"
      },
      "target_type": "NATIONAL",
      "target_market_id": "US",
      "relationship_type": "CLOSE_MATCH",
      "confidence_score": "0.92",
      "review_status": "VERIFIED_REVIEWED",
      "methodology": "EXPERT_ASSESSMENT",
      "evidence_sources": [
        "https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020",
        "https://www.bls.gov/soc/2018/major_groups.htm#15-0000"
      ],
      "notes_and_limitations": "UK SOC 2020 unit group 2134 includes full-stack, backend, and general web programmers, whereas US 2018 SOC separates dedicated Web Developers into 15-1254.",
      "approximation_warning": "This comparison relies on an approximate concordance between Programmers and software development professionals (2134) and target with evaluated confidence 92%. Roles differ in specific tasks, scope, or qualifications."
    },
    {
      "target_occupation": {
        "canonical_occupation_id": "CAN_OCC_SOFTWARE_ENGINEER",
        "preferred_title": "Software Engineer",
        "concept_family": "Software & Applications Development"
      },
      "target_type": "CANONICAL",
      "target_market_id": "INT",
      "relationship_type": "CLOSE_MATCH",
      "confidence_score": "0.95",
      "review_status": "VERIFIED_REVIEWED",
      "methodology": "EXPERT_ASSESSMENT",
      "evidence_sources": [
        "https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020"
      ],
      "notes_and_limitations": "UK unit group 2134 represents the national realization of the canonical Software Engineer concept.",
      "approximation_warning": null
    }
  ],
  "unmapped_markets": ["IN", "AU", "SG"],
  "total_matches": 2
}
```

### 2.4 Error Envelope
All endpoints return standard HTTP errors with descriptive JSON:
- `404 Not Found`:
  ```json
  {
    "detail": "Occupation 'UK_SOC_2020:9999' not found."
  }
  ```
- `422 Unprocessable Entity`: Standard FastAPI validation error envelope.
