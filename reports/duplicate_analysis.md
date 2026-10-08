# Duplicate Analysis & Cross-Posting Audit Report
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction  
**Dataset:** Tech Job Postings with Parsed Salaries (ATS Direct), Package `jobs-tier1-L-2026-08-01`  
**Total Raw Rows:** 394,300  
**Date:** October 5, 2026  

---

## 1. Executive Summary

A core directive of Phase 2 is: **Do NOT automatically delete cross-postings blindly.** 
In labor market intelligence, postings sharing the same `(title, company, location)` can reflect several distinct real-world phenomena:
1. Technical crawler artifacts (case-insensitive board tokens scraped twice).
2. True multiple job openings (distinct requisition IDs for simultaneous headcount).
3. Legitimate geographic variation (the same role hired across multiple cities/offices).
4. Temporal renewals and recurring recruitment cycles across different quarters.

A naive deduplication on `title + company + location` would have blindly deleted **71,413 legitimate records**, discarding valuable geographic, temporal, and salary distribution variance. Through rigorous multi-column forensics across `job_id`, `ats`, `ats_token`, `url`, `location_raw`, and `posted_at`, every record group was classified into evidence-based categories.

---

## 2. Duplicate Categorization & Action Matrix

| Duplicate Type | Raw Count | Redundant Count | Action | Reason & Empirical Evidence |
|---|---:|---:|---|---|
| **A. Exact Row Duplicates** | 0 | 0 | None (Already clean) | Zero rows are 100% identical across all 21 raw columns. |
| **B. Crawler Token-Casing Artifacts (SmartRecruiters)** | 116,610 | **58,305** | **Remove redundant instances** | Exactly identical job requisitions scraped twice due to board token casing differences (e.g., `ALTEN/7440001...` vs `alten/7440001...`). 100% of these 116,610 rows originate from SmartRecruiters with identical `job_id`, `title`, `company_name`, `location_raw`, `posted_at`, `salary_min`, `salary_max`, and `skills`. Removing 58,305 redundant records eliminates pure technical crawler noise. |
| **C. Distinct Job Openings at Same Company & Location** | 26,387 | 0 | **Retain all** | Postings sharing `(title, company, location)` but carrying genuinely distinct `job_id` values (9,153 groups). Represents multiple headcount requisitions opened by the same company in the same city. Essential for accurate labor demand estimation. |
| **D. Same Role across Different Locations** | 21,480 groups | 0 | **Retain all** | Identical job titles at the same company posted in different cities/countries (e.g., "Software Engineer" at Google in Mountain View vs New York vs London). Crucial for studying geographic salary variation. |
| **E. Recurring / Reposted Jobs across Time** | 26,267 | 0 | **Retain all** | Roles re-advertised at different time intervals (`posted_at` dates differ by weeks or months) with distinct requisition lifecycles. Retaining them preserves legitimate temporal labor dynamics. |

---

## 3. Impact on the Modeling Dataset (Tech Roles with Annual Salary)

Within the target population of **Tech Roles with USD Annual Salary** (N = 25,008):
- **Exact Row Duplicates:** 0
- **Token-Casing Crawler Artifacts:** 1,300 rows (650 redundant pairs). These 650 duplicate instances are cleanly removed.
- **Genuine Requisitions & Location Variations:** Retained in full.
- **Resulting Clean Tech USD Annual Salary Population:** **24,358 high-quality, non-redundant postings**.

---

## 4. Deduplication Logic Implementation

The cleaning pipeline applies the following explicit, non-destructive deduplication filter:

```python
# 1. Standardize ATS token casing
df['ats_token_norm'] = df['ats_token'].str.lower()

# 2. Deduplicate only true crawler repeats (same ATS platform and normalized job requisition)
initial_count = len(df)
df = df.drop_duplicates(subset=['ats', 'ats_token_norm', 'job_id'], keep='first')
removed_count = initial_count - len(df)

# Rows before: 394,300
# Rows removed: 58,305
# Rows remaining: 335,995
```

This procedure eliminates all 58,305 redundant crawler artifacts while protecting 100% of legitimate multi-opening requisitions, temporal reposts, and geographic variations.
