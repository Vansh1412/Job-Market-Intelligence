# JOBINTEL 2.0 — SPRINT 3B.2.2
# PHASE 5: SKILL GAP METHODOLOGY & INTERPRETATION HARDENING

**Document ID:** `SPRINT3B2_2_SKILL_GAP_METHODOLOGY`  
**Milestone:** Sprint 3B.2.2 — Algorithmic Transparency & Consumer Protection  
**Date:** 2026-11-16  
**Auditor / Architect:** Principal Data Scientist & Software Architect  
**Target Branch:** `staging/sprint2c3`  
**HEAD Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  

---

## 1. Executive Summary

This document presents the mathematical verification and ethical interpretation hardening applied to the Skill Gap Analysis engine in JobIntel 2.0. Following Sprint 3B.2.1 Audit directives, this sprint makes the underlying calculation fully transparent by displaying raw weights and formulas in the UI, and enforces strict linguistic controls to prevent users from misinterpreting a descriptive skill match percentage as a predictive "probability of employment" or "hiring likelihood".

---

## 2. Mathematical Algorithm Specification

The Skill Gap Analyzer evaluates a candidate's submitted competencies against the canonical target occupation's skill profile using an importance-weighted coverage ratio:

$$\text{Skill Coverage (\%)} = \left( \frac{\sum_{s \in \mathcal{S}_{\text{matched}}} w_s}{\sum_{s \in \mathcal{S}_{\text{target}}} w_s} \right) \times 100$$

### 2.1 Variables and Boundaries
- $\mathcal{S}_{\text{target}}$: The set of validated occupational skills defined for the target canonical concept in `skill_demands.json`.
- $w_s \in [70.0, 95.0]$: The `importance_score` assigned to skill $s$ derived from O*NET Content Model and industry job descriptions.
- $\mathcal{S}_{\text{matched}} \subseteq \mathcal{S}_{\text{target}}$: The subset of target skills matched by user-submitted competencies (evaluated via normalized synonym mapping).
- **Mathematical Bounds:** $\text{Skill Coverage} \in [0.0, 100.0]\%$.
- **Zero-Denominator Guard:** If $\sum w_s = 0$, the denominator defaults to $1.0$, returning $0.0\%$.

---

## 3. Calculation Transparency in API & UI

The engine returns full mathematical calculation components in the API response:

```python
class SkillGapAnalysisResult(BaseModel):
    target_occupation_id: str
    target_occupation_title: str
    market_id: MarketId
    user_skills_submitted: list[str]
    matched_skills: list[str]
    missing_critical_skills: list[SkillGapItem]
    missing_secondary_skills: list[SkillGapItem]
    match_percentage: float
    matched_skill_weight: float
    total_required_weight: float
    formula_explanation: str
    methodology_notes: str
    readiness_level: str
    recommendations: list[str]
```

### 3.1 Frontend Formula Display Card
In `frontend/src/pages/DemandPage.tsx`, beneath the match percentage bar, a transparent mathematical breakdown card is displayed:

```text
📐 Mathematical Formula & Weight Breakdown:
Skill Coverage (%) = (Matched Skill Weight / Total Required Skill Weight) * 100
Matched Weight: 185.0 / Total Required Weight: 260.0
```

---

## 4. Linguistic Guardrails & Ethical Protection

To eliminate deceptive career outcome claims, JobIntel enforces strict terminology rules:

### 4.1 Prohibited Wording
- ❌ **"Probability of employment"**
- ❌ **"Hiring probability"**
- ❌ **"Job landing odds"**
- ❌ **"Guaranteed job readiness"**
- ❌ **"Predictive employability score"**

### 4.2 Approved Neutral Wording
- ✅ **"Skill coverage percentage"**
- ✅ **"Skill match indicator"**
- ✅ **"Market alignment with hiring prerequisites"**
- ✅ **"Missing technical competencies"**

### 4.3 Rule-Based Nature of Learning Recommendations
All generated recommendations explicitly carry the governance disclaimer:
> *"Learning Guidance: Recommendations are rule-based learning priority suggestions based on market demand weights, not a guarantee of employment or hiring probability."*

And the methodology notice:
> *"Skill coverage measures alignment between candidate skills and employer-requested competencies for the occupation. It is not an employability probability, hiring probability, or placement guarantee."*

---

## 5. Automated Verification

Tested in `tests/test_demand_intelligence.py`:
- `test_skill_gap_mathematical_formula_transparency`:
  - Verifies `matched_skill_weight` and `total_required_weight` are positive floats.
  - Verifies `formula_explanation` is populated.
  - Verifies `methodology_notes` explicitly disclaims employability probability.
  - Verifies recommendations identify rule-based guidance.
- Result: **PASS** (100% compliance).
