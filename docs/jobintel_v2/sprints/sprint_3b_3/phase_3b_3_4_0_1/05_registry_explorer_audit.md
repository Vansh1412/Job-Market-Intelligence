# 05. Employer Registry Explorer Audit Report

## 1. Explorer Architecture & Scope

The Employer Registry Explorer tab in `frontend/src/pages/EmployersPage.tsx` provides an interactive directory of verified sovereign employer profiles retrieved from the backend API.

### Key Capabilities Evaluated
1. **Empty Registry Handling**: Graceful degradation when the database contains 0 employer profiles.
2. **Pagination Protocol**: Compliance with backend limits (`limit <= 50`, `offset >= 0`).
3. **Filtering Capabilities**: Client-side filtering by country and category on the loaded dataset.
4. **Detail Profile Inspection**: Drill-down modal/drawer view for individual employers.

---

## 2. Empty-State Behavior Verification

### Observation
- Live probe to `GET /api/v1/employers` on staging yields an empty array `[]` (HTTP 200 OK).
- In earlier system iterations, an empty list could lead to undefined access exceptions (e.g. `employers[0].locations`).

### Code Inspection (`EmployersPage.tsx:420-435`)
```tsx
{employers.length === 0 && !loading && !error && (
  <div className="bg-slate-800/40 border border-slate-700/60 rounded-xl p-8 text-center" data-testid="empty-registry-state">
    <BuildingOfficeIcon className="w-12 h-12 text-slate-500 mx-auto mb-3" />
    <h3 className="text-lg font-medium text-slate-200">No Verified Employers Registered</h3>
    <p className="text-sm text-slate-400 mt-1 max-w-md mx-auto">
      The sovereign employer registry currently has zero registered records. As employer statutory identities are verified and ingested, they will appear here.
    </p>
  </div>
)}
```
- **Auditor Evaluation**: The empty state renders an informative, clean UI with zero console errors or uncaught exceptions. Tested and verified in `employers_ui.test.tsx` (Test: *"switches to Registry tab and shows empty state when 0 employers exist"*).

---

## 3. Pagination Protocol & Boundary Enforcement

### FastAPI Query Validation
- `src/backend/api/v1.py` defines:
  ```python
  limit: int = Query(default=20, ge=1, le=50)
  offset: int = Query(default=0, ge=0)
  ```
- **Live Probe Finding**: Attempting `GET /api/v1/employers?limit=100` returns `HTTP 422 Unprocessable Entity` (`Input should be less than or equal to 50`).
- **Frontend Alignment**:
  - `frontend/src/services/api.ts` requests `limit = 20` by default.
  - Page navigation controls increment/decrement `offset` in increments of 20.
  - The UI cleanly handles pagination without triggering 422 boundary errors.

---

## 4. Filtering & Detail View

### Filtering
- The Explorer provides a country dropdown (`All Countries`, `USA`, `GBR`, `IND`) and category filters (`ENTERPRISE`, `MID_MARKET`, `SMB`, `STARTUP`).
- Filtering operates client-side over the fetched batch of verified employers, matching `profile.locations.some(loc => loc.country_code === filterCountry)`.
- No extraneous unindexed backend queries are generated.

### Detail View
- Clicking a profile row triggers `setSelectedEmployer(profile)`.
- The detail card renders:
  - Canonical Corporate Name & Category.
  - Verification Badge (`VERIFIED_STATUTORY`, `UNVERIFIED`).
  - Statutory Identifiers table (SEC CIK, MCA CIN, Companies House CRN).
  - Corporate Locations (Headquarters, Regional Offices, Remote Hubs).
  - Data Provenance References (Source register, ingestion date, source hash).
- If detail retrieval fails, the application smoothly falls back to the in-memory profile.
