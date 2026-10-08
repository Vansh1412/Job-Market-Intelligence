-- sql/india/job_market_analysis.sql
-- Master consolidated SQL analysis on Indian Job Market dataset (2025).
--
-- Notes on Schema Adaptation:
-- 1. salary_lpa is disclosed for ~33.9% of postings. Salary queries filter to that subset
--    explicitly (currency = 'INR' AND salary_lpa IS NOT NULL) and sample sizes (N) are reported.
-- 2. Non-salary queries (posting volumes) evaluate against the complete analytical corpus.

-- 1. Average salary by role category, sorted highest first (disclosed-salary INR subset only)
SELECT
    role_category,
    COUNT(*)                  AS num_postings_with_salary,
    ROUND(AVG(salary_lpa), 2) AS avg_salary_lpa,
    ROUND(MIN(salary_lpa), 2) AS min_salary_lpa,
    ROUND(MAX(salary_lpa), 2) AS max_salary_lpa
FROM job_postings
WHERE salary_lpa IS NOT NULL
  AND currency = 'INR'
GROUP BY role_category
HAVING COUNT(*) >= 5
ORDER BY avg_salary_lpa DESC;

-- 2. Salary by city for Data Analyst / Business Analyst roles specifically
SELECT
    city,
    COUNT(*)                  AS num_postings_with_salary,
    ROUND(AVG(salary_lpa), 2) AS avg_salary_lpa
FROM job_postings
WHERE salary_lpa IS NOT NULL
  AND currency = 'INR'
  AND role_category IN ('Data Analyst', 'Business Analyst')
GROUP BY city
HAVING COUNT(*) >= 3
ORDER BY avg_salary_lpa DESC;

-- 3. Salary premium by experience band (disclosed-salary INR subset only)
SELECT
    experience_band,
    COUNT(*)                  AS num_postings_with_salary,
    ROUND(AVG(salary_lpa), 2) AS avg_salary_lpa
FROM job_postings
WHERE salary_lpa IS NOT NULL
  AND experience_band IS NOT NULL
  AND currency = 'INR'
GROUP BY experience_band
ORDER BY avg_salary_lpa;

-- 4. Posting volume by city (full dataset, top 15 metros)
SELECT
    city,
    COUNT(*)                  AS num_postings,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM job_postings WHERE city IS NOT NULL), 1) AS pct_of_total
FROM job_postings
WHERE city IS NOT NULL
GROUP BY city
ORDER BY num_postings DESC
LIMIT 15;

-- 5. Posting volume by role category (full dataset)
SELECT
    role_category,
    COUNT(*)                  AS num_postings
FROM job_postings
GROUP BY role_category
ORDER BY num_postings DESC;
