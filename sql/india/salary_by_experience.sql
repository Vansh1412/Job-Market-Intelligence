-- sql/india/salary_by_experience.sql
-- Experience wage curve across standardized seniority bands.
-- Restricted strictly to valid disclosed INR compensation records (currency = 'INR' AND salary_lpa IS NOT NULL).

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
