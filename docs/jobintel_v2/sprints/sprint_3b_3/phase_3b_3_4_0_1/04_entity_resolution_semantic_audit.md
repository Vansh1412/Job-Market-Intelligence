# 04. Entity Resolution Semantic Audit Report

## 1. Resolution & Review Status Semantics

The JOBINTEL 2.0 entity resolution engine operates under strict statutory governance principles codified in `src/backend/employers/resolver.py`.

### Match Types (`ResolutionMatchType`)
1. **`EXACT_STATUTORY`**:
   - Condition: Candidate matches an official sovereign statutory identifier (e.g. UK Companies House CRN, US SEC CIK, India MCA CIN).
   - Review Status: Automatically set to `AUTO_VERIFIED` unless a collision is detected.
2. **`CANONICAL_NAME`**:
   - Condition: Exact normalized name match against a verified canonical corporate entity name.
   - Review Status: `AUTO_VERIFIED`.
3. **`ALIAS_MATCH`**:
   - Condition: Exact match against an approved registered corporate alias or DBA ("doing business as").
   - Review Status: `AUTO_VERIFIED`.
4. **`FUZZY_NAME`**:
   - Condition: String similarity exceeds `fuzzy_threshold` (default 0.85).
   - Review Status: `MANUAL_REVIEW_REQUIRED`. `resolved_company_id` is populated with the top candidate, but flagged for human verification.
5. **`NO_MATCH`**:
   - Condition: No candidate exceeds the similarity threshold and no statutory identifier matches.
   - Review Status: `CONFIRMED_DISTINCT`.

---

## 2. Critical Semantic Distinction: `CONFIRMED_DISTINCT`

### Forensic Finding
- In earlier sprint discussions, there was ambiguity regarding whether `CONFIRMED_DISTINCT` represented a pending state or an unverified match.
- **Audit Clarification**: `CONFIRMED_DISTINCT` is returned by the backend specifically when **no match is found** (`match_type: NO_MATCH`, `resolved_company_id: null`, `similarity_score: 0.0`). It designates that the submitted employer is recognized as an autonomous, distinct entity that is **not present** in the current sovereign registry.
- **Frontend Presentation**:
  - The UI renders this state with a distinct grey/blue badge: `CONFIRMED DISTINCT (NO MATCH)`.
  - It explicitly displays `Resolved Company ID: None (Distinct Entity)`.
  - It does not attempt to fabricate an ID or link to a profile.
  - This preserves mathematical and legal truthfulness.

---

## 3. Duplicate Statutory Identifier Collision Defense (Fail-Closed)

### Forensic Check of `src/backend/employers/resolver.py:165-178`
```python
if len(matching_candidates) > 1:
    return EmployerResolutionResponse(
        match_type=ResolutionMatchType.FUZZY_NAME,  # or AMBIGUOUS
        resolved_company_id=None,  # FAIL-CLOSED: Must be None!
        resolved_canonical_name=None,
        similarity_score=1.0,
        review_status=EntityReviewStatus.MANUAL_REVIEW_REQUIRED,
        candidates=matching_candidates,
        warnings=[
            f"STATUTORY_COLLISION: Identifier {statutory_id} is associated with {len(matching_candidates)} distinct entities."
        ],
        provenance_notes=[
            "Multiple entities claim or share this identifier. Resolution suspended pending manual human review."
        ]
    )
```

### UI Behavior on Collision
- When `review_status === 'MANUAL_REVIEW_REQUIRED'` and `warnings` contains a collision message, the frontend displays:
  - An amber alert banner: `Statutory Identifier Collision Detected`.
  - Notice stating: `Resolution suspended. Multiple entities claim this identifier. No corporate identity has been arbitrarily selected.`
  - A table of all conflicting candidate entities for auditor evaluation.
  - `Resolved Company ID: null`.

---

## 4. Corporate Boundary Preservation (Parent & Subsidiary Handling)

In corporate structures (e.g. *Alphabet Inc.* vs *Google LLC* vs *Google India Pvt Ltd*):
- Each entity possesses distinct legal incorporation, distinct statutory registration numbers (CIK / CIN / CRN), and distinct jurisdiction.
- The resolver strictly checks exact corporate names and statutory IDs independently.
- The UI never collapses subsidiaries into parent companies or vice versa.
- Subsidiary identifiers (`subsidiary_ids`) and parent identifiers (`parent_company_id`) are maintained as separate attributes in `EmployerProfile`.

---

## 5. Similarity Score Disclosure Standard

- The UI **never** refers to `similarity_score` as a "probability", "confidence interval", or "statistical likelihood".
- It is explicitly labeled: **`String Similarity Score (Levenshtein / Jaro-Winkler Token Match)`**.
- A tooltip explains that this score measures typographical string distance against canonical names, not empirical probability of business identity.
- This adheres to Section 7 of the Master Prompt governance criteria.
