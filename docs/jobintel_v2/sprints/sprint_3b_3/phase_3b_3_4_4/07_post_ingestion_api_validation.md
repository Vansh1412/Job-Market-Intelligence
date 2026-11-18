# SPRINT 3B.3.3.4.4 — POST-INGESTION API CONTRACT VALIDATION
**Sprint:** 3B.3.3.4.4 — Controlled Five-Employer Staging Ingestion, Provenance Validation & Live Registry Qualification  
**Date:** 2026-11-18  
**Role:** Principal Backend Architect, API Contract Specialist & QA Lead  
**Target Environment:** Staging  
**Contract Baseline:** OpenAPI 3.1 & Pydantic Schema Contracts

---

## 1. Executive Summary & Verification Matrix

Following controlled pilot ingestion of the five sovereign employer candidates, all primary Employer Intelligence REST endpoints were subjected to rigorous contract, pagination, and entity resolution validation.

| Endpoint | HTTP Method | Test Scenario | Expected Status | Actual Status | Contract Conformance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/v1/employers` | `GET` | Retrieve complete collection | `200 OK` | `200 OK` | **PASS (5 items)** |
| `/api/v1/employers?limit=2&offset=0` | `GET` | First page pagination | `200 OK` | `200 OK` | **PASS (2 items)** |
| `/api/v1/employers?limit=2&offset=2` | `GET` | Second page pagination | `200 OK` | `200 OK` | **PASS (2 items)** |
| `/api/v1/employers?limit=100` | `GET` | Out-of-bounds limit | `422 Unprocessable` | `422 Unprocessable` | **PASS (ge=1, le=50)** |
| `/api/v1/employers/{company_id}` | `GET` | Exact profile lookup (`comp_au_atlassian`) | `200 OK` | `200 OK` | **PASS** |
| `/api/v1/employers/{company_id}` | `GET` | Nonexistent company lookup | `404 Not Found` | `404 Not Found` | **PASS** |
| `/api/v1/employers/resolve` | `POST` | Exact statutory match (`CIK 0000789019`) | `200 OK` | `200 OK` | **PASS (AUTOMATICALLY_RESOLVED)** |
| `/api/v1/employers/resolve` | `POST` | Name-only query (`Microsoft Corporation`) | `200 OK` | `200 OK` | **PASS (MANUAL_REVIEW_REQUIRED)** |
| `/api/v1/employers/resolve` | `POST` | Unknown entity (`Acme Global`) | `200 OK` | `200 OK` | **PASS (CONFIRMED_DISTINCT)** |
| `/api/v1/employers/resolve` | `POST` | Empty payload | `422 Unprocessable` | `422 Unprocessable` | **PASS** |

---

## 2. Detailed Endpoint Validation Evidence

### 2.1 Complete Collection Retrieval (`GET /api/v1/employers`)

**Request:**
```http
GET /api/v1/employers HTTP/1.1
Host: jobintel-staging
Accept: application/json
```

**Response (HTTP 200 OK):**
```json
[
  {
    "company_id": "comp_au_atlassian",
    "company_name": "Atlassian Pty Ltd",
    "headquarters_country": "AU",
    "company_category": "OTHER_INTERNATIONAL",
    "industry": "Software & Cloud Collaboration Tools",
    "official_website": "https://www.atlassian.com/",
    "operating_markets": ["AU", "US", "IN"],
    "source_references": [
      {
        "source_name": "Australian Business Register",
        "source_organization": "Australian Taxation Office",
        "source_reference": "https://abr.business.gov.au/ABN/View?id=53102443916",
        "collected_at": "2026-11-18T00:00:00Z"
      }
    ],
    "verification_status": "VERIFIED",
    "verified_at": "2026-11-18T00:00:00Z",
    "locations": []
  },
  {
    "company_id": "comp_us_microsoft",
    "company_name": "Microsoft Corporation",
    "headquarters_country": "US",
    "company_category": "OTHER_INTERNATIONAL",
    "industry": "Cloud Computing, Enterprise Software & Hardware",
    "official_website": "https://www.microsoft.com/",
    "operating_markets": ["US", "UK", "IN", "AU", "SG"],
    "source_references": [
      {
        "source_name": "SEC EDGAR",
        "source_organization": "U.S. Securities and Exchange Commission",
        "source_reference": "https://www.sec.gov/edgar/browse/?CIK=0000789019",
        "collected_at": "2026-11-18T00:00:00Z"
      }
    ],
    "verification_status": "VERIFIED",
    "verified_at": "2026-11-18T00:00:00Z",
    "locations": []
  },
  {
    "company_id": "comp_uk_arm",
    "company_name": "Arm Limited",
    "headquarters_country": "UK",
    "company_category": "OTHER_INTERNATIONAL",
    "industry": "Semiconductor IP & Processor Architecture",
    "official_website": "https://www.arm.com/",
    "operating_markets": ["UK", "US", "IN"],
    "source_references": [
      {
        "source_name": "Companies House (UK)",
        "source_organization": "UK Department for Business and Trade",
        "source_reference": "https://find-and-update.company-information.service.gov.uk/company/02557590",
        "collected_at": "2026-11-18T00:00:00Z"
      }
    ],
    "verification_status": "VERIFIED",
    "verified_at": "2026-11-18T00:00:00Z",
    "locations": []
  },
  {
    "company_id": "comp_sg_dbs",
    "company_name": "DBS Bank Ltd.",
    "headquarters_country": "SG",
    "company_category": "OTHER_INTERNATIONAL",
    "industry": "Financial Services & Commercial Banking",
    "official_website": "https://www.dbs.com/",
    "operating_markets": ["SG", "IN", "AU", "UK"],
    "source_references": [
      {
        "source_name": "ACRA Bizfile",
        "source_organization": "Accounting and Corporate Regulatory Authority Singapore",
        "source_reference": "https://www.tis.bizfile.gov.sg/uen/196800306E",
        "collected_at": "2026-11-18T00:00:00Z"
      }
    ],
    "verification_status": "VERIFIED",
    "verified_at": "2026-11-18T00:00:00Z",
    "locations": []
  },
  {
    "company_id": "comp_in_infosys",
    "company_name": "Infosys Limited",
    "headquarters_country": "IN",
    "company_category": "INDIAN_HEADQUARTERED",
    "industry": "IT Services, Consulting & Business Solutions",
    "official_website": "https://www.infosys.com/",
    "operating_markets": ["IN", "US", "UK", "AU", "SG"],
    "source_references": [
      {
        "source_name": "Ministry of Corporate Affairs",
        "source_organization": "Ministry of Corporate Affairs India",
        "source_reference": "https://www.mca.gov.in/mcafoportal/companyLLPMasterData.do?cin=L85110KA1981PLC013115",
        "collected_at": "2026-11-18T00:00:00Z"
      }
    ],
    "verification_status": "VERIFIED",
    "verified_at": "2026-11-18T00:00:00Z",
    "locations": []
  }
]
```

---

### 2.2 Statutory Resolution Probing (`POST /api/v1/employers/resolve`)

#### Scenario A: Exact Statutory Match
```json
// Request
POST /api/v1/employers/resolve
{
  "candidate_name": "Atlassian Pty Ltd",
  "market_id": "AU",
  "statutory_identifier": "53102443916",
  "statutory_authority": "ASIC"
}

// Response: HTTP 200 OK
{
  "query_name": "Atlassian Pty Ltd",
  "query_market_id": "AU",
  "resolution_match_type": "EXACT_IDENTIFIER_MATCH",
  "resolved_company_id": "comp_au_atlassian",
  "review_status": "AUTOMATICALLY_RESOLVED",
  "candidates": [
    {
      "target_company_id": "comp_au_atlassian",
      "target_company_name": "Atlassian Pty Ltd",
      "target_market_id": "AU",
      "match_type": "EXACT_IDENTIFIER_MATCH",
      "similarity_score": 1.0,
      "shared_brand_detected": false,
      "is_subsidiary_relationship": false,
      "evidence_summary": "Exact statutory identifier match via ASIC in jurisdiction AU.",
      "review_status": "AUTOMATICALLY_RESOLVED",
      "requires_human_approval": false
    }
  ],
  "governance_caveat": "JOBINTEL strict resolution policy: shared brand names and parent-subsidiary relationships do not constitute proof of identical legal identity. Ambiguous candidates require manual review."
}
```

#### Scenario B: Exact Name Match Without Statutory Identifier (Governance Safeguard)
```json
// Request
POST /api/v1/employers/resolve
{
  "candidate_name": "Microsoft Corporation",
  "market_id": "US"
}

// Response: HTTP 200 OK
{
  "query_name": "Microsoft Corporation",
  "query_market_id": "US",
  "resolution_match_type": "STRONG_CANDIDATE_MATCH",
  "resolved_company_id": null,
  "review_status": "MANUAL_REVIEW_REQUIRED",
  "candidates": [
    {
      "target_company_id": "comp_us_microsoft",
      "target_company_name": "Microsoft Corporation",
      "target_market_id": "US",
      "match_type": "STRONG_CANDIDATE_MATCH",
      "similarity_score": 1.0,
      "shared_brand_detected": false,
      "is_subsidiary_relationship": false,
      "evidence_summary": "High normalized lexical similarity (100.00%) in same jurisdiction (US).",
      "review_status": "MANUAL_REVIEW_REQUIRED",
      "requires_human_approval": true
    }
  ],
  "governance_caveat": "JOBINTEL strict resolution policy: shared brand names and parent-subsidiary relationships do not constitute proof of identical legal identity. Ambiguous candidates require manual review."
}
```

**Governance Validation:** In the absence of an authoritative statutory token, the resolver strictly prevents automatic identity collapsing, correctly returning `resolved_company_id = null` and `review_status = MANUAL_REVIEW_REQUIRED`.
