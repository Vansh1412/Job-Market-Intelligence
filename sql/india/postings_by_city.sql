-- sql/india/postings_by_city.sql
-- Job posting volume across top 15 Indian metropolitan hubs.
-- Evaluated against full unique job postings corpus (N = 97,679).

SELECT
    city,
    COUNT(*) AS total_postings,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM job_postings WHERE city IS NOT NULL), 1) AS pct_of_total
FROM job_postings
WHERE city IS NOT NULL
GROUP BY city
ORDER BY total_postings DESC
LIMIT 15;
