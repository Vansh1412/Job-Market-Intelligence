-- sql/india/salary_by_role.sql
-- Disclosed compensation statistics across functional role categories.
-- Restricted strictly to valid disclosed INR compensation records (currency = 'INR' AND salary_lpa IS NOT NULL).
-- Minimum sample threshold: at least 5 salary observations required.

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
