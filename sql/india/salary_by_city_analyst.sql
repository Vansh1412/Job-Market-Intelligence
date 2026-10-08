-- sql/india/salary_by_city_analyst.sql
-- Geographic compensation benchmarking for Analyst cohort (Data Analyst & Business Analyst).
-- Restricted strictly to valid disclosed INR compensation records (currency = 'INR' AND salary_lpa IS NOT NULL).
-- Minimum sample threshold: at least 3 salary observations per city required.

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
