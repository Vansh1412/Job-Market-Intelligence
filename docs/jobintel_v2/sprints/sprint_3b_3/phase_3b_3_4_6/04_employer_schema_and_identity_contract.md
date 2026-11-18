# SPRINT 3B.3.3.4.6 — EMPLOYER SCHEMA & IDENTITY CONTRACT SPECIFICATION
**Sprint:** 3B.3.3.4.6  
**Document:** `04_employer_schema_and_identity_contract.md`  
**Date:** 2026-11-18  
**Author:** Principal Data Architect & Entity Resolution Specialist  
**Status:** COMPLETE & VERIFIED  

---

## 1. Schema Evolution & Backward Compatibility

Prior to Sprint 3B.3.3.4.6, employer statutory IDs and governance metadata were stored as loosely typed strings inside `sources: List[str]`. This impeded deterministic resolution and prevented high-fidelity display on the frontend.

In [src/backend/schemas/employer.py](file:///e:/Job%20Market/src/backend/schemas/employer.py), the `EmployerProfile` schema was enriched with first-class fields:

```python
class EmployerProfile(BaseModel):
    id: str = Field(..., description="Unique employer identifier, e.g. 'comp_au_atlassian'")
    name: str = Field(..., description="Canonical employer name")
    country: str = Field(..., description="Country code (ISO-3166-1 alpha-2 or platform market)")
    sector: str = Field(..., description="Primary industry sector")
    verified: bool = Field(False, description="Verification status")
    open_roles_count: int = Field(0, description="Observed open role count")
    website: Optional[str] = Field(None, description="Primary company URL")
    sources: List[str] = Field(default_factory=list, description="List of source attributions")
    
    # First-class statutory & governance fields (Sprint 3B.3.3.4.6)
    statutory_identifier: Optional[str] = Field(None, description="Official company registration number")
    statutory_authority: Optional[str] = Field(None, description="Issuing government corporate register")
    jurisdiction: Optional[str] = Field(None, description="Sovereign jurisdiction of legal incorporation")
    platform_market: Optional[str] = Field(None, description="JOBINTEL market mapping (e.g. 'US', 'UK', 'AU')")
    headquarters_country_code: Optional[str] = Field(None, description="ISO-3166-1 alpha-2 HQ country")
    headcount_value: Optional[int] = Field(None, description="Audited employee headcount figure")
    headcount_band: Optional[str] = Field(None, description="Standardized headcount band, e.g. '10000+'")
    headcount_basis: Optional[str] = Field(None, description="Basis of headcount disclosure (e.g. 'SEC Form 10-K')")
    headcount_scope: Optional[str] = Field(None, description="Headcount reporting scope (e.g. 'Global', 'Domestic')")
    observation_date: Optional[str] = Field(None, description="Date of regulatory filing or observation (YYYY-MM-DD)")
    source_license: Optional[str] = Field(None, description="Source data license or public disclosure regime")
    attribution_requirement: Optional[str] = Field(None, description="Mandatory attribution statement")
    publication_status: Optional[str] = Field("APPROVED", description="Governance publication state")
```

All new fields default to `None` or `"APPROVED"`, guaranteeing 100% backward compatibility with all existing tests, endpoints, and callers.

---

## 2. Jurisdiction Equivalence & Entity Resolution (`UK` vs `GB`)

The JOBINTEL platform models the United Kingdom market as `UK`, whereas statutory bodies and ISO-3166-1 alpha-2 designate it as `GB`. To eliminate resolution failures caused by this disparity, a symmetric compatibility helper was added to [src/backend/employers/resolver.py](file:///e:/Job%20Market/src/backend/employers/resolver.py):

```python
def markets_compatible(m1: Optional[str], m2: Optional[str]) -> bool:
    """Check if two market / country designations are compatible."""
    if not m1 or not m2:
        return True
    m1_clean = m1.strip().upper()
    m2_clean = m2.strip().upper()
    if m1_clean == m2_clean:
        return True
    # Handle UK vs GB ISO-3166-1 alpha-2 equivalence
    uk_synonyms = {"UK", "GB"}
    if m1_clean in uk_synonyms and m2_clean in uk_synonyms:
        return True
    return False
```

### Deterministic Multi-Tier Resolution Strategy
When an incoming query arrives at `resolve_employer`:
1. **Tier 1 (Statutory Authority & Number):** Direct exact lookup against `profile.statutory_identifier` and `profile.jurisdiction`. If matched, returns confidence `1.0` (EXACT).
2. **Tier 2 (Canonical Domain):** Normalized domain matching against `profile.website`. Returns confidence `0.95`.
3. **Tier 3 (Exact Canonical Name + Market):** Normalized name match under market compatibility. Returns confidence `0.90`.
4. **Tier 4 (Token-Set / Fuzzy Jaro-Winkler):** High-similarity threshold match. If score exceeds threshold, returns `HIGH` or `MEDIUM` match; otherwise triggers `MANUAL_REVIEW` or `NO_MATCH`.

---

## 3. Frontend Contract Alignment

The frontend TypeScript interface [frontend/src/types.ts](file:///e:/Job%20Market/frontend/src/types.ts) was updated with matching properties:
- `statutory_identifier?: string;`
- `statutory_authority?: string;`
- `jurisdiction?: string;`
- `headcount_value?: number;`
- `headcount_basis?: string;`
- `source_license?: string;`

The [frontend/src/pages/EmployersPage.tsx](file:///e:/Job%20Market/frontend/src/pages/EmployersPage.tsx) component surfaces these fields in both the card summary grid and the comprehensive Employer Detail Modal, providing transparent regulatory verification to the user.
