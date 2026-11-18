# 08. Security & Data Governance Review

## 1. Information Disclosure & Privacy Audit

A forensic scan of frontend network requests, error handlers, and component rendering logic was conducted:

| Inspection Item | Risk Evaluated | Audit Finding | Status |
|---|---|---|---|
| **Secret / Key Leakage** | Hardcoded tokens or API credentials in frontend bundle | Scanned `frontend/src/` for API keys, tokens, or private secrets. None found. | **SECURE** |
| **Filesystem Paths** | Internal server paths exposed in error messages | `fetchJson` and error boundary wrap all errors in clean user messages (`err?.message`). No server paths exposed. | **SECURE** |
| **Stack Traces** | Uncaught exceptions dumping Python / Node stack traces to UI | All API calls enclosed in try/catch blocks; UI displays clean failure notices. | **SECURE** |
| **Personally Identifiable Information (PII)** | Employee names or un-anonymized records | Only public, sovereign corporate registry identifiers (CIK, CIN, CRN) are retrieved. Zero PII present. | **SECURE** |

---

## 2. Injection & URL Parameter Sanitization

In `frontend/src/services/api.ts`:
```typescript
getEmployerDetail: (companyId: string) =>
  fetchJson<EmployerProfile>(`/v1/employers/${encodeURIComponent(companyId)}`),
```
- Path parameters are strictly sanitized via `encodeURIComponent()`.
- Prevents path traversal (`../`) and URL injection attacks when user-controlled `companyId` strings are supplied to the backend.

---

## 3. Statutory Identity & Governance Defenses

### Fail-Closed Ambiguity Defense
- In the event of duplicate statutory identifiers (e.g. data collusion, registration number collisions across jurisdictions, or synthetic fuzzing), the backend resolver and frontend UI **fail closed**:
  - `resolved_company_id` is guaranteed `null`.
  - Review status is forced to `MANUAL_REVIEW_REQUIRED`.
  - Amber collision alert notifies the user that resolution is suspended pending human governance review.
  - No corporate identity is arbitrarily selected or bound.

### Data Provenance Integrity
- Every profile rendered in the UI includes its statutory source provenance (`source_references`):
  - Ingestion timestamp (`retrieved_at`).
  - Source authority (`Securities and Exchange Commission`, `Ministry of Corporate Affairs`, `Companies House`).
  - Cryptographic verification hash (`source_hash`).
- Prevents unverified web scraping or speculative data from being presented as official corporate facts.

---

## 4. Production Master Isolation

- Verified that `origin/master` and local `master` remain pinned to `198b79dcdff08a5be5f08847c4262d31a3ce261e`.
- Local tests do not target or send mutation requests to production endpoints.
- No credentials or write tokens for production environments were accessed or used.
