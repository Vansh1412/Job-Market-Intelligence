# JOBINTEL 2.0 — SPRINT 3B.2.1
# AUDIT H: SKILL DEMAND & SKILL GAP ENGINE AUDIT

**Audit Date:** 2026-11-16  
**Auditor:** Principal Data Governance Auditor & Statistical Methodology Reviewer  
**Execution Mode:** STRICT READ-ONLY INDEPENDENT AUDIT  
**Baseline Git Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Repository Branch:** `staging/sprint2c3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`

---

## 1. Executive Summary

This audit evaluates the Skill Demand ontology and the Skill Gap Analysis engine implemented in `src/backend/services/demand_service.py` (`analyze_skill_gaps`), schema contracts in `src/backend/schemas/demand.py`, dataset integrity in `src/backend/data/demand/skill_demands.json`, and frontend presentation in `frontend/src/pages/DemandPage.tsx`.

The evaluation verifies:
1. Mathematical correctness of the skill coverage formula.
2. Weighting and normalization integrity.
3. Categorization of missing skills.
4. Prevention of misleading "employability probability" or "job-landing odds" claims.

---

## 2. Skill Demands Dataset Inspection (`skill_demands.json`)

- **Total Canonical Concepts:** 11 concepts covering core digital and technology roles.
- **Total Skill Records:** 75 individual skill items.
- **Unique Skill Names:** 54 distinct technical, framework, and process competencies.
- **Skill Provenance:** Mapped from O*NET 28.0 Knowledge/Technology Skill elements, validated against international ICT skill frameworks (SkillsFuture Singapore ICT SFw and Australian OSCA competencies).
- **Classification:** **`OFFICIALLY_DERIVED`** and **`EXPERT_CURATED`**.

### 2.1 Skill Attributes

Each skill record in `skill_demands.json` specifies:
- `skill_name`: Canonical standardized name (e.g., `Python`, `SQL`, `Kubernetes`, `Docker`).
- `category`: Competency category (`CORE_TECHNICAL`, `FRAMEWORK`, `CLOUD_INFRASTRUCTURE`, `PROCESS_DOMAIN`).
- `importance_score`: Continuous numerical weight in range $[70.0, 95.0]$.
- `frequency_percentage`: Empirical posting citation prevalence in range $[40.0, 95.0]$.
- `is_hot_skill`: Boolean flag indicating surging market demand.

---

## 3. Mathematical Verification of Skill Gap Engine

The skill gap engine evaluates candidate skills against target occupational requirements using a weighted coverage algorithm:

$$\text{Skill Match Percentage} = \left( \frac{\sum_{s \in \mathcal{S}_{\text{matched}}} w_s}{\sum_{s \in \mathcal{S}_{\text{target}}} w_s} \right) \times 100\%$$

Where:
- $\mathcal{S}_{\text{target}}$ is the set of required skills defined for the canonical occupation.
- $w_s$ is the `importance_score` ($70.0 \le w_s \le 95.0$) assigned to skill $s$.
- $\mathcal{S}_{\text{matched}}$ is the subset of target skills satisfied by the candidate's submitted skills.

### 3.1 Normalization and String Matching
The engine executes `_normalize_skill(s)`:
1. Strips leading/trailing whitespace.
2. Converts to lowercase.
3. Replaces hyphens and underscores with spaces.
4. Performs bidirectional containment checks (e.g., matching `"TypeScript"` to `"javascript/typescript"` or `"AWS"` to `"aws/azure/gcp"`).

### 3.2 Missing Skill Prioritization Matrix

Missing skills are partitioned into two priority tiers based on importance score and demand urgency:

| Priority Class | Inclusion Criteria | Actionable Guidance Generated |
|---|---|---|
| **`CRITICAL`** | $w_s \ge 85.0$ **OR** `is_hot_skill == True` | "Immediate Priority: Acquire core competencies in [Skills] to meet essential market threshold." |
| **`HIGH`** | $75.0 \le w_s < 85.0$ and not hot | "Secondary Advantage: Build practical projects utilizing [Skills]." |
| **`NICE_TO_HAVE`** | $w_s < 75.0$ | Supplementary enhancement. |

### 3.3 Readiness Level Thresholds

```
   Match Percentage:   0% ──────── 25% ──────── 50% ──────── 75% ──────── 100%
   Readiness Level:      FOUNDATIONAL │   EMERGING   │   MODERATE   │     HIGH
   Critical Constraint:               │              │ Max 1 Crit   │ 0 Missing Crit
```

- **`HIGH`**: $\text{Match} \ge 75.0\%$ **and** $0$ missing critical skills.
- **`MODERATE`**: $\text{Match} \ge 50.0\%$ **or** $\le 1$ missing critical skill.
- **`EMERGING`**: $\text{Match} \ge 25.0\%$.
- **`FOUNDATIONAL`**: $\text{Match} < 25.0\%$.

---

## 4. Linguistic and Statistical Framing Audit

A critical audit requirement is to verify that the system does **not** misrepresent skill match scores as hiring probabilities or predictive likelihoods of landing a job.

### 4.1 Backend Engine Language Check
Inspection of `demand_service.py` line 214:
```python
recommendations.append(
    f"Market Alignment: Your current profile aligns {match_pct}% with hiring prerequisites for {occ_title} in {m_val.value}."
)
```
- The backend refers strictly to **"Market Alignment"** and **"hiring prerequisites"**.
- Zero instances of words such as *"probability of hiring"*, *"chance of employment"*, or *"placement prediction"*.

### 4.2 Frontend Presentation Check (`DemandPage.tsx`)
Inspection of `DemandPage.tsx`:
- Metric is rendered with label **"Skill Match Indicator"**.
- Explanatory copy states: *"Your skill profile demonstrates X% alignment with employer-requested competencies for [Occupation]."*
- A prominent disclaimer informs the user:
  > **Note:** Skill alignment represents keyword and curriculum coverage against official occupational profiles. It is not an assessment of candidate competence, hiring guarantee, or automated screening decision.

---

## 5. Audit Verdict

- **Mathematical Correctness:** **PASS**. Weighted ratio is strictly bounded in $[0.0, 100.0]$.
- **Normalization Integrity:** **PASS**. Robust substring and case-insensitive matching.
- **Prioritization Logic:** **PASS**. Correct thresholding on $w_s \ge 85$ and `is_hot_skill`.
- **Governance & Consumer Protection:** **PASS**. Strictly presented as a descriptive skill match indicator; zero false claims of predictive employability.
