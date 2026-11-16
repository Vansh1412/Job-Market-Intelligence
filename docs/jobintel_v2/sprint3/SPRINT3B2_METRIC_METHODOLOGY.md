# JOBINTEL 2.0 — SPRINT 3B.2
## SPRINT 3B.2 METRIC METHODOLOGY: GLOBAL DEMAND ANALYTICS & COMPARABILITY

**Document ID:** `SPRINT3B2_METRIC_METHODOLOGY`  
**Milestone:** Sprint 3B.2 — Phase 2 Methodology Specification  
**Date:** 2026-11-16  
**Auditor / Authors:** Principal Data Scientist, Labour Market Statistics Specialist, ML Engineer  
**Target Branch:** `staging/sprint2c3`  
**Baseline Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  

---

### 1. METHODOLOGICAL FOUNDATIONS

A persistent failure mode in multi-market labour intelligence platforms is the superficial unification of heterogeneous data. For example, naively charting Australia's monthly online job advertisement index next to the US Bureau of Labor Statistics' 10-year projected annual job openings misleads users into believing these numbers represent comparable units of volume.

In JOBINTEL 2.0, the Demand Intelligence layer enforces five core statistical distinctions:

1. **Online Job Postings $\neq$ Confirmed Hires:**
   Web-scraped postings measure employer recruitment effort, which is biased towards digital-first sectors and subject to ghost postings, staffing agency duplicates, and advertising budget fluctuations.
2. **Rising Job Postings $\neq$ Net Employment Growth:**
   An industry experiencing high turnover can produce an explosion of online job advertisements while its net headcount shrinks.
3. **Shortage Ratings $\neq$ High Demand Volume:**
   An occupation can have low overall headcount or few openings, yet experience acute shortage due to specialized skill prerequisites or geographic misalignment.
4. **Projected Job Openings $\neq$ Observed Vacancies:**
   Projected annual openings model long-term workforce replenishment and macroeconomic structural growth, not immediate spot vacancies.
5. **No Collapsed "Global Demand Score":**
   The platform refuses to generate a singular composite score that obscures the fundamental differences between national statistical instruments.

---

### 2. DEMAND METRIC TYPES & FORMULATIONS

#### 2.1 Metric Type Definitions

| Metric Type | Underlying Economic Phenomenon | Temporal Resolution | Aggregation Rule |
| :--- | :--- | :--- | :--- |
| `OBSERVED_JOB_ADVERTISEMENTS` | Newly lodged or active online job advertisements from scraped boards. | Monthly / Quarterly | Do not sum across different scrapers; normalize to index. |
| `OBSERVED_VACANCIES` | Unfilled jobs for which active recruitment action is being taken by employers. | Quarterly / Annual | Additive within the same statistical survey sample frame. |
| `ANNUAL_JOB_OPENINGS` | Average annual openings expected from structural growth plus replacement needs. | 10-Year Annualized | Cannot be combined with spot monthly observations. |
| `EMPLOYMENT_LEVEL` | Total headcount employed in the occupation at a given reference date. | Annual Survey / Census | Stock variable; non-additive across distinct time periods. |
| `EMPLOYMENT_CHANGE` | Historical net change in employed persons between two census dates. | Multi-Year Interval | Flow variable. |
| `PROJECTED_EMPLOYMENT_CHANGE`| Projected % growth or decline in total employment over a forecast horizon. | 10-Year Horizon | Rate variable. |
| `SHORTAGE_INDICATOR` | Triangulated rating of recruitment difficulty and supply bottleneck. | Annual Cycle | Categorical ordinal variable. |
| `SKILL_REQUIREMENT` | Importance score or empirical posting appearance percentage. | Continuous / Periodic | Normalized 0.0–100.0 scale. |

---

### 3. TREND CALCULATION ENGINE

#### 3.1 Mathematical Formulations

Let a time-series of demand observations for occupation $i$ in market $m$ be represented as:
$$T = \{(t_1, v_1), (t_2, v_2), \dots, (t_n, v_n)\}$$
where $t_k$ represents the sequential time period and $v_k$ is the observed value.

##### 1. Percentage Change Formulation
The overall percentage change across the observation window is defined as:
$$\Delta\% = \begin{cases} 
\frac{v_n - v_1}{v_1} \times 100 & \text{if } v_1 > 0 \\
\text{undefined} & \text{if } v_1 = 0 \text{ and } v_n = 0 \\
+100\% & \text{if } v_1 = 0 \text{ and } v_n > 0 
\end{cases}$$

##### 2. Directional Classification Thresholds
Based on $\Delta\%$, the trend direction is assigned according to the following strict piecewise thresholds:
$$\text{Direction} = \begin{cases}
\text{STRONG\_GROWTH} & \text{if } \Delta\% > +10.0\% \\
\text{MODERATE\_GROWTH} & \text{if } +2.0\% \le \Delta\% \le +10.0\% \\
\text{STABLE} & \text{if } -2.0\% \le \Delta\% < +2.0\% \\
\text{MODERATE\_DECLINE} & \text{if } -10.0\% \le \Delta\% < -2.0\% \\
\text{STRONG\_DECLINE} & \text{if } \Delta\% < -10.0\% \\
\text{INSUFFICIENT\_DATA} & \text{if } n < 2 \text{ or data is suppressed}
\end{cases}$$

For projection metrics (e.g. US BLS 10-year projected employment change), the published 10-year percentage rate $\rho$ directly governs the trend direction using identical thresholds.

---

### 4. THE 11-DIMENSION DEMAND COMPARABILITY ENGINE

When comparing demand data between two national markets (Market $A$ and Market $B$) for a given canonical occupation concept, the system evaluates compatibility across **11 distinct methodological dimensions**.

#### 4.1 Evaluation Dimensions & Severity Matrix

| Dimension | Description | Match Condition | Severity on Mismatch |
| :--- | :--- | :--- | :---: |
| **1. Metric Instrument Type** | Identical underlying construct (e.g. both are `OBSERVED_JOB_ADVERTISEMENTS`) | $M_A = M_B$ | **CRITICAL** |
| **2. Target Population** | Scope of workers covered (e.g. all employees vs private sector only vs PMETs) | Same employee definition | **MODERATE** |
| **3. Survey vs Scraped Collection** | Establishment survey vs web-scraped job postings | Both survey or both scraped | **CRITICAL** |
| **4. Temporal Interval & Frequency** | Measurement interval (e.g. Monthly vs Quarterly vs 10-year projection) | Same frequency window | **CRITICAL** |
| **5. Seasonal Adjustment** | Whether series is raw unadjusted or seasonally smoothed | Same adjustment state | **LOW** |
| **6. Taxonomy Hierarchy Level** | Depth of classification (e.g. 4-digit unit group vs 6-digit detailed title) | Compatible granularity | **MODERATE** |
| **7. Geographic Coverage** | Nationwide census vs selected metropolitan hubs | Same national scope | **MODERATE** |
| **8. Deduplication Methodology** | Algorithm used to remove duplicate job postings across job boards | Similar deduplication | **LOW** |
| **9. Growth vs Replacement** | Net expansion only vs total openings including replacement exits | Same scope | **CRITICAL** |
| **10. Sampling Frame & Response** | Mandatory census vs voluntary sample vs platform posting capture | Similar statistical rigor | **MODERATE** |
| **11. Unit Normalization** | Raw counts vs index numbers (base 100) vs rates per 1,000 employees | Same unit class | **CRITICAL** |

#### 4.2 Overall Comparability Verdict Algorithm

Let $N_{\text{critical\_mismatch}}$ be the count of critical mismatches, and $N_{\text{moderate\_mismatch}}$ be the count of moderate mismatches:

$$\text{Verdict} = \begin{cases}
\text{INSUFFICIENT\_DATA} & \text{if data missing for } A \text{ or } B \\
\text{DIRECTLY\_COMPARABLE} & \text{if } N_{\text{critical}} = 0 \text{ and } N_{\text{moderate}} = 0 \\
\text{DIRECTIONALLY\_COMPARABLE} & \text{if } N_{\text{critical}} \le 1 \text{ (e.g., both measure trends over similar periods)} \\
\text{METHODOLOGICALLY\_DISTINCT} & \text{if } N_{\text{critical}} \ge 2 \text{ but conceptually related} \\
\text{NOT\_COMPARABLE} & \text{if fundamentally divergent with zero valid concordance}
\end{cases}$$

Every comparison result produces:
1. The formal `DemandComparabilityVerdict`.
2. A synthesized `verdict_summary` explaining the primary drivers of mismatch.
3. Itemized evaluation results for all 11 dimensions.
4. Specific actionable warnings for downstream decision-makers.

---

### 5. SKILL GAP ANALYSIS ALGORITHM

The skill gap analyzer provides actionable career intelligence by comparing a user's self-reported skill inventory against the empirical skill requirements of a target occupation in a selected market.

#### 5.1 Algorithm Steps

1. **Input Normalization:**
   Given user skills $U = \{u_1, u_2, \dots, u_m\}$ and target occupation required skills $R = \{r_1, r_2, \dots, r_k\}$:
   - Normalize strings: lowercase, strip punctuation, map synonyms (e.g., "js" $\rightarrow$ "javascript", "reactjs" $\rightarrow$ "react", "k8s" $\rightarrow$ "kubernetes", "postgres" $\rightarrow$ "postgresql").
2. **Partition Target Skills by Importance:**
   - **Critical Skills ($R_{\text{critical}}$):** Skills with `importance_score` $\ge 75.0$ or `is_hot_skill == True`.
   - **Secondary Skills ($R_{\text{secondary}}$):** Skills with `importance_score` $< 75.0$.
3. **Intersection & Set Difference:**
   - $\text{Matched} = U_{\text{norm}} \cap R_{\text{norm}}$
   - $\text{Missing Critical} = R_{\text{critical}} \setminus U_{\text{norm}}$
   - $\text{Missing Secondary} = R_{\text{secondary}} \setminus U_{\text{norm}}$
4. **Weighted Match Percentage:**
   Let $w(r)$ be the `importance_score` of skill $r$:
   $$\text{Match } \% = \frac{\sum_{r \in \text{Matched}} w(r)}{\sum_{r \in R} w(r)} \times 100$$
5. **Readiness Level Classification:**
   - **HIGH:** Match $\% \ge 75.0\%$ and zero missing critical skills.
   - **MODERATE:** $50.0\% \le \text{Match } \% < 75.0\%$ or at most 1 missing critical skill.
   - **EMERGING:** $25.0\% \le \text{Match } \% < 50.0\%$.
   - **FOUNDATIONAL:** Match $\% < 25.0\%$.
6. **Prioritized Recommendations:**
   Generate targeted acquisition recommendations ordered by missing skill importance and market demand growth rate.

---

### 6. EDGE CASE DEFENSIVE SPECIFICATION

1. **Division by Zero:**
   In percentage calculations, if baseline $v_1 = 0$, the function returns `None` or `+100.0%` with an explicit flag rather than raising an unhandled exception.
2. **Missing Time Series:**
   If an occupation has a point-in-time observation without historical time-series points, `trend_direction` is set to `DemandTrendDirection.INSUFFICIENT_DATA`.
3. **Incomplete Regional Breakdowns:**
   If a market does not publish sub-national breakdowns for a specific occupation, the API returns an empty list `[]` and sets `geographic_scope = "National"` without failing.
4. **Singapore Hard-to-Fill Indicator:**
   The `% unfilled for > 6 months` metric is unique to Singapore MOM. It is displayed prominently on Singapore profiles and omitted gracefully on profiles from other markets.
