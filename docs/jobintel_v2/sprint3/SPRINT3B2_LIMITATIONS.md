# JOBINTEL 2.0 — SPRINT 3B.2
## SPRINT 3B.2 KNOWN LIMITATIONS & METHODOLOGICAL BOUNDARIES

**Document ID:** `SPRINT3B2_LIMITATIONS`  
**Milestone:** Sprint 3B.2 — Phase 9 Documentation  
**Date:** 2026-11-16  
**Auditor / Authors:** Principal Data Scientist, Labour Market Statistics Specialist, Governance Architect  
**Target Branch:** `staging/sprint2c3`  
**Baseline Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  

---

### 1. METHODOLOGICAL DIVERGENCE LIMITATIONS

#### 1.1 Non-Equivalence of Online Postings and Net Hires
- **Scope:** Australia (JSA IVI), UK (ONS Labour Demand), India (Tech Benchmark).
- **Caveat:** Online job advertisements measure recruitment effort and employer search intensity on digital platforms. They do **not** represent confirmed hires or net job creation. A sector undergoing rapid turnover or high attrition (such as software development) can exhibit substantial posting volumes without expanding net employment. Furthermore, web-scraped postings are susceptible to multi-posting across job boards, recruitment agency churn, and "ghost" postings.

#### 1.2 Survey Vacancies vs Web Scraped Postings
- **Scope:** Singapore (MOM Job Vacancy Statistics) vs Australia/UK/India.
- **Caveat:** Singapore MOM vacancy data is derived from a formal establishment survey of private enterprises employing 25+ workers and public sector agencies. This produces statistically rigorous counts of actual unfilled positions actively being recruited. In contrast, web-scraped series capture all digital postings, including unverified openings, but exclude informal or unadvertised vacancies.

#### 1.3 10-Year Projections vs Spot Market Indicators
- **Scope:** United States (US BLS Employment Projections) vs all other markets.
- **Caveat:** US BLS data provides 10-year projected annual job openings (2023–2033), combining macroeconomic model projections of net employment growth with occupational exits and replacement transfers. It is a structural macroeconomic planning instrument, **not** a real-time monitor of current monthly or quarterly vacancy fluctuations.

---

### 2. MARKET-SPECIFIC COVERAGE & SAMPLING LIMITATIONS

| Market | Source | Known Limitations & Gaps |
| :--- | :--- | :--- |
| **United States** | US BLS EP & O*NET | National projections assume full macroeconomic employment at the 10-year horizon. Unforeseen cyclical shocks or rapid generative AI disruptions may alter actual hiring velocity. |
| **Australia** | JSA IVI & SPL | IVI covers major internet recruitment portals (Seek, CareerOne, Workforce Australia). Excludes jobs advertised exclusively through personal networks, employer career portals, or social media. |
| **United Kingdom** | ONS Labour Demand | Experimental statistics derived from Textkernel data partnership. Granularity is restricted to sub-major and minor SOC 2020 groups; experimental deduplication algorithm may introduce variance. |
| **Singapore** | MOM Vacancies | Establishment survey excludes small firms with fewer than 25 employees in the private sector. Highly reliable for PMET tech occupations, but small startup recruitment may be underrepresented. |
| **India** | JobIntel Benchmark & PLFS | India lacks an official real-time nationwide administrative vacancy index for the informal economy. Tech demand data represents a calibrated benchmark of online tech postings across Tier-1 tech hubs, not an exhaustive national census. |

---

### 3. TECHNICAL & INFRASTRUCTURE BOUNDARIES

1. **In-Memory Registry Footprint:**
   The entire demand registry (`metrics.json`, `sources.json`, `observations.json`, `skill_demands.json`, `shortage_indicators.json`) is loaded into memory on container startup. While memory consumption is minimal ($< 2.5 \text{ MB}$), scaling beyond 10,000 national occupations in future sprints will require lazy indexing or embedded SQLite caching.
2. **Strict UK Salary Fail-Closed Preservation:**
   Under active governance protocols (`uk_salary_service.py`), UK descriptive salary data remains revoked and fails closed with HTTP 503. The demand intelligence layer operates strictly on official ONS online job advert volumes, leaving the salary gate completely intact and isolated.
3. **No Dynamic Model Retraining:**
   Sprint 3B.2 introduces zero mutations to production ML model artifacts (`Dataset A/B`, Ridge/XGBoost models). All demand metrics are descriptive, source-grounded statistical indicators.
