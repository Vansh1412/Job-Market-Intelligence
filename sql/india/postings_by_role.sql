-- sql/india/postings_by_role.sql
-- Job posting demand volume across standardized role families.
-- Evaluated against full unique job postings corpus (N = 97,679).

SELECT
    role_category,
    COUNT(*) AS total_postings
FROM job_postings
GROUP BY role_category
ORDER BY total_postings DESC;
