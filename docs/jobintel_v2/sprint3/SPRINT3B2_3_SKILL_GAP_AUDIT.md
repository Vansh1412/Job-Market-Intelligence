# JOBINTEL 2.0 — SPRINT 3B.2.3 SKILL GAP MATHEMATICAL & SEMANTIC AUDIT
## Formula Exactness, Edge Cases, Bounding Verification & Predictive Claim Prevention

**Audit Date:** November 16, 2026  
**Auditor:** Independent Software Architect & Technical Quality Assurance Auditor  
**Audit Scope:** Independent inspection of `src/backend/services/demand_service.py`, `src/backend/schemas/demand.py`, and `frontend/src/pages/DemandPage.tsx`.

---

### 1. MATHEMATICAL FORMULATION & NORMALIZATION AUDIT

The skill gap engine evaluates candidate competency coverage against occupation-specific skill importance profiles derived from official frameworks (O*NET 28.2, SkillsFuture Singapore ICT Framework, Jobs & Skills Australia SPL).

#### Canonical Formula:
$$\text{Skill Coverage (\%)} = \left( \frac{W_{\text{matched}}}{W_{\text{total}}} \right) \times 100$$
where:
- $W_{\text{matched}} = \sum_{s \in \text{MatchedSkills}} \text{ImportanceScore}(s)$
- $W_{\text{total}} = \sum_{s \in \text{TargetSkills}} \text{ImportanceScore}(s)$

#### Mathematical Invariants Verified:
1. **Division by Zero Protection:**
   In `src/backend/services/demand_service.py` (line 720):
   ```python
   total_weight = sum(s.importance_score for s in target_skills) or 1.0
   ```
   If an occupation has no registered competencies, `total_weight` defaults to `1.0`, producing `0.0%` rather than raising `ZeroDivisionError`, `NaN`, or `Infinity`.
2. **Range Bounding:**
   Because each target skill is evaluated once and matched at most once, $0 \le W_{\text{matched}} \le W_{\text{total}}$. Consequently, $\text{Skill Coverage} \in [0.0, 100.0]\%$.
3. **Weight Precision:**
   $W_{\text{matched}}$ and $W_{\text{total}}$ are exposed as floating-point values rounded to 1 decimal place, ensuring reproducible mathematical verification by end users.

---

### 2. NORMALIZATION & DEDUPLICATION AUDIT

The audit inspected `_normalize_skill(s)` and matching logic in `src/backend/services/demand_service.py`:
1. **Whitespace & Casing:** Strips leading/trailing whitespace and applies lowercasing (`s.strip().lower()`).
2. **Synonym Harmonization:** Mapped via `SYNONYM_MAP` (e.g., `k8s` $\rightarrow$ `kubernetes`, `py` $\rightarrow$ `python`, `js` $\rightarrow$ `javascript`, `postgres` $\rightarrow$ `postgresql`, `aws` $\rightarrow$ `amazon web services`).
3. **Deduplication:** Input list is converted to a set comprehension:
   ```python
   user_norm_set = {_normalize_skill(s) for s in request.user_skills}
   ```
   Submitting duplicate skills (e.g., `["Python", "python", "py"]`) does not inflate the matched weight. Python is counted exactly once with its single importance score (92.0).

---

### 3. EDGE CASE TESTING SUITE

All boundary conditions were tested directly using `scratch/test_skill_gap_edge_cases.py`:

| Test Scenario | Input Skills | Expected $W_{\text{matched}} / W_{\text{total}}$ | Expected Score | Readiness Tier | Audit Result |
|---|---|---|---|---|---|
| **Empty Inventory** | `[]` | $0.0 / 1113.0$ | $0.0\%$ | FOUNDATIONAL | **PASS** |
| **Duplicate Skills** | `["Python", "python", "  Python  ", "PY"]` | $92.0 / 1113.0$ | $8.3\%$ | FOUNDATIONAL | **PASS** |
| **Unrecognized Skills**| `["NonExistentTechXYZ", "RandomSkill123"]` | $0.0 / 1113.0$ | $0.0\%$ | FOUNDATIONAL | **PASS** |
| **All Target Skills** | All 13 canonical skills | $1113.0 / 1113.0$ | $100.0\%$ | HIGH | **PASS** |
| **Partial Inventory** | `["Python", "SQL", "Git", "Docker", "REST APIs"]` | $435.0 / 1113.0$ | $39.1\%$ | EMERGING | **PASS** |

---

### 4. ELIMINATION OF PREDICTIVE CLAIMS

The audit reviewed all user-facing strings in `src/backend/services/demand_service.py` and `frontend/src/pages/DemandPage.tsx` to verify compliance with academic and professional governance standards:

#### Strictly Disclaimed Concepts:
- **No Probabilistic Hiring:** The engine does NOT claim an $X\%$ chance of being hired.
- **No Employability Scores:** The engine does NOT claim an $X\%$ likelihood of receiving an interview or job offer.
- **No Placement Guarantee:** The engine explicitly states that skill fit does not guarantee job readiness.

#### Verified Neutral Disclaimers:
1. **Methodology Notes (`SkillGapAnalysisResult.methodology_notes`):**
   > *"Skill coverage measures alignment between candidate skills and employer-requested competencies for the occupation. It is not an employability probability, hiring probability, or placement guarantee."*
2. **Learning Guidance Disclaimer (`recommendations`):**
   > *"Learning Guidance: Recommendations are rule-based learning priority suggestions based on market demand weights, not a guarantee of employment or hiring probability."*
3. **Frontend UI Card:**
   Renders a dedicated **Mathematical Formula & Weight Breakdown** card displaying the exact formula and components ($W_{\text{matched}} = 435 / W_{\text{total}} = 1113$).

---

### 5. AUDIT VERDICT

```text
SKILL GAP AUDIT VERDICT: VERIFIED CLOSED
Status: PASS
Mathematical Formulation: Exact, bounded in [0, 100]%, zero-division protected.
Normalization: Case-insensitive, whitespace-trimmed, synonym-aware, deduplicated.
Governance Compliance: 100% free of predictive or probabilistic hiring claims.
```
