# JOBINTEL 2.0 — SPRINT 3B.3.3.3
## DOCUMENT 04: SKILL DENOMINATOR REGRESSION VERIFICATION

**Sprint:** 3B.3.3.3 — Critical Employer Resolver Remediation & Salary Contract Correction  
**Test Suite:** `tests/test_skill_denominator_integrity.py`  
**Focus:** Sample-Size Lineage & Prevalence Quotient Verification  
**Status:** 100% REGRESSION-VERIFIED (4/4 PASS)  

---

### 1. Lineage & Provenance of Skill Denominators

| Market | Verified Denominator ($N$) | Ground Truth Dataset Source | Primary Artifact |
| :--- | :--- | :--- | :--- |
| **USA** | **$335,995$** | Primary USA Job Postings Corpus | `data/processed/usa_postings_cleaned.parquet` |
| **India** | **$5,323$** | Curated India IT Job Postings Corpus | `data/india/processed/india_it_postings.parquet` |

---

### 2. Prevalence Quotient Verification

#### USA Skill Landscape ($N = 335,995$)
- **Python:** $31,583$ occurrences $\rightarrow \frac{31,583}{335,995} = 9.40\%$
- **SQL:** $41,327$ occurrences $\rightarrow \frac{41,327}{335,995} = 12.30\%$
- **AWS:** $28,895$ occurrences $\rightarrow \frac{28,895}{335,995} = 8.60\%$

#### India Skill Landscape ($N = 5,323$)
- **Development:** $724$ occurrences $\rightarrow \frac{724}{5,323} = 13.60\%$
- **Python:** $644$ occurrences $\rightarrow \frac{644}{5,323} = 12.10\%$
- **SQL:** $596$ occurrences $\rightarrow \frac{596}{5,323} = 11.20\%$
- **Machine Learning:** $346$ occurrences $\rightarrow \frac{346}{5,323} = 6.50\%$

---

### 3. Automated Regression Verification

The test suite `tests/test_skill_denominator_integrity.py` validates that neither backend services nor API routing can regress these denominators:

```
tests/test_skill_denominator_integrity.py::test_usa_skill_denominator_lineage_and_prevalence PASSED [ 25%]
tests/test_skill_denominator_integrity.py::test_india_skill_denominator_lineage_and_prevalence PASSED [ 50%]
tests/test_skill_denominator_integrity.py::test_skills_api_http_endpoints_return_verified_denominators PASSED [ 75%]
tests/test_skill_denominator_integrity.py::test_all_india_skills_prevalence_quotients PASSED [100%]

============================== 4 passed in 1.72s ==============================
```

- **HTTP Endpoint Testing:**
  - `GET /api/skills/frequency`: confirms USA total observations $N = 335,995$.
  - `GET /api/india/skills`: confirms India total sample size $N = 5,323$ and each individual skill's percentage calculation matches $count / 5323 * 100$.
- **Frontend Contract:**
  - `frontend/src/pages/SkillsPage.tsx` displays market-specific denominators with zero hardcoded cross-contamination.
