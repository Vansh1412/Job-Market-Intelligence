# SPRINT 3B.3.3.3.3: SKILLS RUNTIME DEFECT VERIFICATION & DENOMINATOR INTEGRITY

**Audit Date:** 2026-11-17  
**Working Branch:** `staging/sprint2c3`  
**Target Staging Service:** `https://jobintel-backend-staging.onrender.com`  
**Defect Reference:** Sprint 3B.3.3.3.1 / Sprint 3B.3.3.3.2 Runtime Defect (`/api/skills/detail/python` HTTP 500)  
**Verification Verdict:** **PASS — DEFECT COMPLETELY RESOLVED & VERIFIED LIVE**

---

## 1. DEFECT ROOT CAUSE ANALYSIS

### 1.1 Root Cause in Commit `62f5525`
In the initial implementation of the skills router (`src/backend/routers/skills.py`), the endpoint `/api/skills/detail/{skill_name}` attempted to calculate cohort-level role associations by querying `MarketService.get_usa_cohort_df()`:
```python
# Problematic pattern in 62f5525:
cohort_df = MarketService.get_usa_cohort_df()
if target_skill_col not in cohort_df.columns:
    ...
```
In local environments with access to the raw research dataset `data/processed/modeling_dataset.parquet`, `cohort_df` loaded successfully. However, in zero-storage cloud container deployments (such as Render staging), large raw parquet files are deliberately unmounted to conserve disk and memory.

Consequently, `MarketService.get_usa_cohort_df()` safely returned `None`. The subsequent check `if target_skill_col not in cohort_df.columns` raised:
```python
AttributeError: 'NoneType' object has no attribute 'columns'
```
resulting in an unhandled HTTP 500 Internal Server Error when querying skill detail on the live staging deployment.

### 1.2 Remediated Pattern in Commit `f2a0777`
In commit `f2a0777`, the code was refactored to treat the raw cohort dataframe as strictly optional, falling back to precomputed certified artifacts (`skills_summary.json`):
```python
# Remediated code in src/backend/routers/skills.py:
target_skill_col = f"skill_{normalized_skill}"
cohort_df = MarketService.get_usa_cohort_df()

roles = []
if cohort_df is not None:
    if target_skill_col in cohort_df.columns and "Role_Family" in cohort_df.columns:
        # Compute dynamic role distribution if parquet is mounted
        role_counts = ...
        roles = ...

# Always return verified population denominators and prevalences
return {
    "skill": skill_entry["skill"],
    "display_name": skill_entry.get("display_name", skill_entry["skill"]),
    "category": skill_entry.get("category", "General"),
    "population_postings": USA_TOTAL_POSTINGS,       # 335,995
    "skill_postings": skill_entry["postings_count"], # 31,676 for Python
    "prevalence_pct": skill_entry["prevalence_pct"], # 9.43%
    "roles": roles
}
```

---

## 2. LIVE STAGING RUNTIME VERIFICATION MATRIX

Direct HTTP probes were conducted against `https://jobintel-backend-staging.onrender.com` to verify resolution on the live deployment.

### 2.1 Primary Defect Endpoint: `/api/skills/detail/python`
```http
GET /api/skills/detail/python HTTP/1.1
Host: jobintel-backend-staging.onrender.com

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 172
Date: Tue, 17 Nov 2026 17:38:00 GMT

{
  "skill": "python",
  "display_name": "python",
  "category": "Programming Languages",
  "population_postings": 335995,
  "skill_postings": 31676,
  "prevalence_pct": 9.43,
  "roles": []
}
```
- **HTTP Status:** 200 OK (Resolved from 500)
- **Latency:** 430.6 ms
- **Population Postings ($N$):** 335,995 (Verified general corpus denominator)
- **Skill Postings ($n$):** 31,676
- **Prevalence:** 9.43% ($31,676 / 335,995 \times 100$)
- **Fallback Roles List:** `[]` (Gracefully handled without crashing)

### 2.2 Supplementary USA Skills Probing
| Endpoint | HTTP Status | Latency | Population $N$ | Skill Postings $n$ | Prevalence |
| :--- | :-: | :-: | :-: | :-: | :-: |
| `/api/skills/detail/aws` | **200 OK** | 290.4 ms | 335,995 | 19,749 | 5.88% |
| `/api/skills/detail/sql` | **200 OK** | 312.1 ms | 335,995 | 23,756 | 7.07% |
| `/api/skills/frequency` | **200 OK** | 245.8 ms | *Returns 82 catalog skills with non-zero frequencies* |
| `/api/skills/salary-association` | **200 OK** | 260.5 ms | *Returns 81 salary associations ($N=34,036$ training cohort)* |

### 2.3 India Skills Probing & Denominator Verification
India skills endpoints were evaluated against the active requisitions cohort ($N = 5,323$):
| Endpoint | HTTP Status | Latency | Population $N$ | Skill Postings $n$ | Demand Share |
| :--- | :-: | :-: | :-: | :-: | :-: |
| `/api/india/skills/Python` | **200 OK** | 863.2 ms | 5,323 | 644 | 12.1% |
| `/api/india/skills/Development` | **200 OK** | 340.2 ms | 5,323 | 723 | 13.6% |
| `/api/india/skills/Java` | **200 OK** | 275.8 ms | 5,323 | 663 | 12.46% |
| `/api/india/skills` | **200 OK** | 315.0 ms | *Returns 284 catalog skills with non-zero frequencies* |

### 2.4 Error Handling & Path Sanitization
Probes with non-existent skill names were executed to verify that errors fail closed with clean JSON and zero server-side leaks:
- `GET /api/skills/detail/nonexistent_xyz`
  - **Status:** HTTP 404 Not Found
  - **Payload:** `{"detail": "Skill 'nonexistent_xyz' not found in USA skills catalog."}`
  - **Sanitization:** No stack trace, no file paths, no internal variables exposed.
- `GET /api/india/skills/nonexistent_xyz`
  - **Status:** HTTP 404 Not Found
  - **Payload:** `{"detail": "Skill 'nonexistent_xyz' not found in India skills catalog."}`
  - **Sanitization:** Clean, secure JSON error contract.

---

## 3. AUDIT CONCLUSION

The unmounted cohort dataframe exception in `src/backend/routers/skills.py` is **100% resolved**. The live staging backend handles unmounted storage gracefully, returns mathematically consistent population denominators ($335,995$ for USA, $5,323$ for India), and adheres to strict production API contracts.
