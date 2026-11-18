# SPRINT 3B.3.3.4: BACKEND API CONTRACT INTEGRATION

**Date:** 2026-11-17  
**Working Branch:** `staging/sprint2c3`  
**Feature:** Typed API Client & Backend Schema Integration  
**Status:** **INTEGRATION COMPLETE**

---

## 1. ENDPOINTS & BACKEND ROUTER ALIGNMENT

The Employer Intelligence frontend connects directly to the endpoints exposed by `src/backend/routers/v1.py` and mounted in `src/backend/main.py`:

| Endpoint | HTTP Method | Request Payload | Response Model | Description |
| :--- | :-: | :--- | :--- | :--- |
| `/api/v1/employers` | GET | `limit?: number, offset?: number` | `EmployerProfile[]` | Paginated listing of registered corporate employers. |
| `/api/v1/employers/resolve` | POST | `EmployerResolutionRequest` | `EmployerResolutionResponse` | Corporate legal entity resolution with duplicate collision defense. |
| `/api/v1/employers/{company_id}` | GET | None (Path parameter) | `EmployerProfile` | Complete profile for a registered employer (or 404). |

---

## 2. TYPESCRIPT DATA SCHEMAS (`frontend/src/types.ts`)

To ensure type safety and eliminate runtime discrepancies, TypeScript interfaces were defined to match the Pydantic models in `src/backend/schemas/employer.py` exactly:

### 2.1 Resolution Request & Response
```typescript
export interface EmployerResolutionRequest {
  candidate_name: string;
  market_id?: string | null;
  statutory_identifier?: string | null;
  statutory_authority?: string | null;
}

export type ResolutionMatchType =
  | 'EXACT_IDENTIFIER_MATCH'
  | 'STRONG_CANDIDATE_MATCH'
  | 'AMBIGUOUS_CANDIDATE'
  | 'NO_MATCH';

export type EntityReviewStatus =
  | 'AUTOMATICALLY_RESOLVED'
  | 'MANUAL_REVIEW_REQUIRED'
  | 'CONFIRMED_DISTINCT'
  | 'HUMAN_VERIFIED_MERGE';

export interface EntityMatchCandidate {
  target_company_id: string;
  target_company_name: string;
  target_market_id: string;
  match_type: ResolutionMatchType;
  similarity_score: number;
  shared_brand_detected: boolean;
  is_subsidiary_relationship: boolean;
  evidence_summary: string;
  review_status: EntityReviewStatus;
  requires_human_approval: boolean;
}

export interface EmployerResolutionResponse {
  query_name: string;
  query_market_id?: string | null;
  resolution_match_type: ResolutionMatchType;
  resolved_company_id: string | null;
  review_status: EntityReviewStatus;
  candidates: EntityMatchCandidate[];
  governance_caveat: string;
}
```

### 2.2 Employer Profile & Registry Models
```typescript
export type EmployerCategory =
  | 'INDIAN_HEADQUARTERED'
  | 'MULTINATIONAL_OPERATING_IN_INDIA'
  | 'OTHER_INTERNATIONAL';

export type EmployerVerificationStatus =
  | 'UNVERIFIED'
  | 'REVIEW_REQUIRED'
  | 'VERIFIED';

export type EmployerLocationType =
  | 'HEADQUARTERS'
  | 'OFFICE'
  | 'RESEARCH'
  | 'OTHER';

export interface EmployerSourceReference {
  source_name: string;
  source_organization: string;
  source_reference: string;
  collected_at?: string | null;
}

export interface EmployerLocation {
  city: string;
  state_or_region?: string | null;
  country_code: string;
  location_type: EmployerLocationType;
  verification_status: EmployerVerificationStatus;
  verification_source: EmployerSourceReference;
  verified_at?: string | null;
}

export interface EmployerProfile {
  company_id: string;
  company_name: string;
  headquarters_country: string;
  company_category: EmployerCategory;
  industry?: string | null;
  official_website?: string | null;
  operating_markets: string[];
  source_references: EmployerSourceReference[];
  verification_status: EmployerVerificationStatus;
  verified_at?: string | null;
  locations: EmployerLocation[];
}
```

---

## 3. API SERVICE METHODS (`frontend/src/services/api.ts`)

In `frontend/src/services/api.ts`, three typed service functions were added to the centralized `api` object:

```typescript
  // Employer Intelligence & Entity Resolution Endpoints (Sprint 3B.3.4)
  getEmployers: (params?: { limit?: number; offset?: number }) => {
    const qp = new URLSearchParams();
    if (params?.limit !== undefined) qp.set('limit', String(params.limit));
    if (params?.offset !== undefined) qp.set('offset', String(params.offset));
    const qs = qp.toString();
    return fetchJson<EmployerProfile[]>(`/v1/employers${qs ? `?${qs}` : ''}`);
  },
  resolveEmployer: (payload: EmployerResolutionRequest) =>
    fetchJson<EmployerResolutionResponse>('/v1/employers/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  getEmployerDetail: (companyId: string) =>
    fetchJson<EmployerProfile>(`/v1/employers/${encodeURIComponent(companyId)}`),
```

### 3.1 Base URL & Path Resolution
Because `fetchJson` prepends `API_BASE` (`/api`), calls to `/v1/employers` resolve seamlessly to `/api/v1/employers`. This cleanly bridges:
- Local development proxying (`vite.config.ts` forwarding `/api` to `127.0.0.1:8000`).
- Remote staging environment (`https://jobintel-backend-staging.onrender.com/api/v1/employers`).

---

## 4. ERROR HANDLING & RESILIENCE

The frontend handles all HTTP error states gracefully without application crashes or memory leaks:
1. **HTTP 422 Unprocessable Entity:** Returned if request schema validation fails (e.g. empty string or missing required fields). Caught and surfaced as a clean banner: *"Company or employer candidate name is required."*
2. **HTTP 404 Not Found:** Returned when an individual employer detail cannot be retrieved. Caught and handled with a fallback to cached candidate data or an explicit notification.
3. **HTTP 5xx / Network Failures:** Trapped in a `try...catch` block, setting `resolutionError` and rendering a clean retry button. Zero stack traces or internal filesystem paths are exposed.
